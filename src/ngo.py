from pathlib import Path
import json
import uuid
import smtplib
import os
from email.message import EmailMessage
from datetime import datetime, timedelta

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / 'ngo' / 'requests.json'
NGOFILE = ROOT / 'ngo' / 'ngos.csv'


def ngos():
    return pd.read_csv(NGOFILE)


def load():
    return json.loads(STORE.read_text()) if STORE.exists() else []


def save(x):
    STORE.write_text(json.dumps(x, indent=2))


def smtp_configured():
    return bool(
        os.getenv('SMTP_HOST')
        and os.getenv('SMTP_USER')
        and os.getenv('SMTP_PASSWORD')
    )


def test_smtp_connection():
    """Verify SMTP login without sending a message."""
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASSWORD')

    if not host or not user or not pwd:
        return False, 'SMTP_HOST, SMTP_USER and SMTP_PASSWORD are required.'

    try:
        with smtplib.SMTP(host, port, timeout=20) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(user, pwd)

        return True, 'SMTP connection and login successful.'

    except Exception as e:
        return False, f'SMTP connection failed: {e}'


def process_timeouts():
    """
    Mark pending requests as timed out after 30 minutes.

    The timeout is checked when the application processes the NGO page.
    """
    x = load()
    now = datetime.now()
    changed = False

    for r in x:
        if (
            r['status'] == 'pending'
            and now >= datetime.fromisoformat(r['sent_at']) + timedelta(minutes=30)
        ):
            r['status'] = 'timeout'
            r['responded_at'] = now.isoformat()
            changed = True

    if changed:
        save(x)

    return x


def create_request(
    restaurant,
    item,
    qty,
    kg,
    ngo,
    chain_id=None,
    quantity_unit='kg',
    demo_mode=False
):
    x = load()
    rid = uuid.uuid4().hex[:10]

    x.append({
        'request_id': rid,
        'chain_id': chain_id or rid,
        'restaurant': restaurant,
        'item': item,
        'quantity_servings': float(qty),
        'quantity_kg': float(kg),
        'quantity_unit': str(quantity_unit),
        'ngo_id': str(ngo.ngo_id),
        'ngo_name': str(ngo.name),
        'ngo_email': str(ngo.email),
        'location': str(ngo.location),
        'demo_mode': bool(demo_mode),
        'status': 'pending',
        'sent_at': datetime.now().isoformat(),
        'responded_at': None
    })

    save(x)
    return rid


def respond(request_id, status):
    x = load()

    for r in x:
        if (
            r['request_id'] == request_id
            and r['status'] == 'pending'
        ):
            r['status'] = status
            r['responded_at'] = datetime.now().isoformat()
            save(x)
            return r

    return None


def send_smtp(request_id, base_url=None):
    x = load()

    r = next(
        z for z in x
        if z['request_id'] == request_id
    )

    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASSWORD')
    sender = os.getenv('SMTP_FROM', user or '')

    if not host or not user or not pwd:
        return (
            False,
            'SMTP credentials are not configured. '
            'Configure Gmail/App Password to send real email.'
        )

    base = (
        base_url
        or os.getenv('RESPONSE_BASE_URL', 'http://localhost:8501')
    ).rstrip('/')

    accept = (
        f'{base}/?ngo_request={r["request_id"]}&response=accept'
    )

    decline = (
        f'{base}/?ngo_request={r["request_id"]}&response=decline'
    )

    msg = EmailMessage()

    msg['Subject'] = (
        f'Food donation request: '
        f'{r["item"]} ({r["quantity_servings"]:.0f} servings)'
    )

    msg['From'] = sender

    # Demo Mode:
    # First request in a chain -> DEMO_EMAIL_1
    # Second request in the same chain -> DEMO_EMAIL_2
    #
    # Normal Mode:
    # Send to the actual NGO email stored in ngos.csv.
    if r.get('demo_mode'):
        chain_requests = [
            z for z in x
            if z.get('chain_id') == r.get('chain_id')
        ]

        demo_index = len(chain_requests)

        demo_email = os.getenv(
            f'DEMO_EMAIL_{demo_index}',
            r['ngo_email']
        )

        msg['To'] = demo_email

    else:
        msg['To'] = r['ngo_email']

    msg.set_content(
        f'''Food Donation Request

Restaurant: {r['restaurant']}
Location: {r['location']}
Food item: {r['item']}
Quantity: {r['quantity_kg']:.2f} {r.get('quantity_unit', 'kg')} ({r['quantity_servings']:.0f} servings)

Please verify food safety, shelf life, storage and pickup requirements before acceptance.

ACCEPT: {accept}
DECLINE: {decline}

Please respond within 30 minutes.

If no response is received within 30 minutes, this request will be treated as declined and the system will automatically send the donation request to the next matched NGO for this location.
'''
    )

    with smtplib.SMTP(host, port, timeout=20) as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(user, pwd)
        s.send_message(msg)

    return True, 'Email sent successfully.'


def next_ngo_for_chain(chain_id, location):
    x = load()

    tried = {
        r['ngo_id']
        for r in x
        if r.get('chain_id') == chain_id
    }

    n = ngos()

    n = n[
        n.location.astype(str).str.lower()
        == str(location).lower()
    ]

    n = n[
        ~n.ngo_id.astype(str).isin(tried)
    ].sort_values('ngo_id')

    return None if n.empty else n.iloc[0]


def advance_after_response(request_id):
    x = load()

    current = next(
        (
            r for r in x
            if r['request_id'] == request_id
        ),
        None
    )

    if (
        not current
        or current['status'] not in ('declined', 'timeout')
    ):
        return None

    # Do not create another request if another request
    # from the same chain is already pending.
    if any(
        r.get('chain_id') == current['chain_id']
        and r['request_id'] != request_id
        and r['status'] == 'pending'
        for r in x
    ):
        return None

    ngo = next_ngo_for_chain(
        current['chain_id'],
        current['location']
    )

    if ngo is None:
        return None

    # IMPORTANT:
    # Preserve demo_mode when moving to the next NGO.
    rid = create_request(
        current['restaurant'],
        current['item'],
        current['quantity_servings'],
        current['quantity_kg'],
        ngo,
        current['chain_id'],
        current.get('quantity_unit', 'kg'),
        current.get('demo_mode', False)
    )

    try:
        sent, msg = send_smtp(rid)

    except Exception as e:
        sent, msg = False, f'SMTP error: {e}'

    return {
        'request_id': rid,
        'message': msg,
        'ngo': ngo.name,
        'sent': sent
    }
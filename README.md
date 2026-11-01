# Food Waste Reduction and Climate Impact Analyzer

## What this project does
1. Provides 12 sample Chennai restaurants/cafes/canteens with unique IDs, locations, contact details and **different 7–10 item menus**.
2. Generates two years of synthetic historical demand containing day-of-week, weekend, holiday, promotion, temperature, rainfall, rainy/hot indicators and historical demand lags.
3. Trains and compares **Linear Regression, Decision Tree, Random Forest and XGBoost**. Selection is based on chronological validation MAE; the later test set is not used to select the winner.
4. Predicts demand/preparation for a selected restaurant and item, and converts kg to approximate servings using item-specific portion assumptions.
5. Allows a genuinely new restaurant to be registered and its menu saved. Because it has no sales history, its first estimate is a labelled cold-start transfer estimate from matching existing restaurants/items/categories. It should enter the training data after history accumulates.
6. Estimates expected waste and an illustrative climate/disposal burden.
7. Gives category-based waste-management guidance.
8. Matches restaurants to sample NGOs by location and supports SMTP notification, accept/decline recording and 30-minute timeout logic.

## Setup
Use Python 3.11 if available.

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_models.py
python -m pytest -q
python -m streamlit run dashboard/app.py
```

If PowerShell activation is blocked, use `.venv\Scripts\python.exe` directly.

## SMTP
For real email sending, configure environment variables before launching:
- `SMTP_HOST`
- `SMTP_PORT` (usually 587)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `RESPONSE_BASE_URL` (a publicly reachable URL to the dashboard/response endpoint)

Without SMTP credentials, the dashboard provides simulated accept/decline buttons so the complete workflow can be demonstrated without sending real emails.

## Portion-size assumptions
The included serving masses are **reference assumptions, not official restaurant serving standards**. Published sources show substantial variation: for example, USDA-derived records commonly represent a medium dosa around 80 g, while an MTR product lists one dosa at 45 g; common roti references range around 35–50 g, and cooked rice references are around 140–158 g. The dashboard therefore uses explicit item-specific assumptions and labels servings as approximate. Restaurants should replace them with measured portions. citeturn1search0turn1search3turn1search1turn1search4

## Research honesty
The dataset is controlled synthetic data. Metrics are valid for the generated benchmark only and must not be described as real-world restaurant performance. The climate disposal factor in `src/climate.py` is intentionally an illustrative placeholder and must be replaced with a documented, locally applicable factor before publication.

FSSAI's surplus-food regulations require safe handling and prohibit donation of unsafe food; donated food must be handed over before spoilage/expiry and appropriate handling, storage, transport and records are required. citeturn0search33

EPA materials explain that food waste in landfills can generate methane and that composting/anaerobic digestion can divert suitable organics; AD can recover biogas and digestate. These are environmental-management principles, not a claim that this prototype measures actual atmospheric reductions. citeturn0search31turn0search34

## Corrected item-level demand behaviour
The synthetic generator now uses explicit item-popularity profiles so items such as Idli, Dosa, Rice, Biryani, Coffee and Salad do not share the same demand distribution. Restaurant-level multipliers and day/context effects further change demand. Menu item IDs are standardized between the catalog, history and prediction pipeline.

The dashboard also displays an approximate prediction interval and constrains the preparation recommendation to be at least the point forecast. This is a prototype decision rule; publication experiments should evaluate service level, shortage, waste and climate trade-offs explicitly.

## Gmail SMTP — quick setup
1. Copy `.env.example` to `.env`.
2. Create a dedicated Gmail account for the demo.
3. Enable 2-Step Verification and create a Google App Password.
4. Put the App Password in `.env` as `SMTP_PASSWORD`.
5. Keep `SMTP_FROM` equal to the Gmail account unless you have a verified sender setup.
6. Start Streamlit and open **NGO Matching**. The page includes an SMTP connection/login test.

For a real NGO to click Accept/Decline, `RESPONSE_BASE_URL` must be a publicly reachable HTTPS address. `http://localhost:8501` is only for local testing.

## NGO queue behaviour
For each restaurant location, NGOs are ordered by `ngo_id`. The first NGO receives the request. A decline or a 30-minute timeout advances the same donation request chain to the next location-matched NGO. The sample NGO emails in `ngo/ngos.csv` are placeholders and must be replaced with verified recipient addresses before real use.

import sys, json, os
from pathlib import Path
from datetime import date
import numpy as np, pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
try:
 from dotenv import load_dotenv
 load_dotenv(ROOT / '.env')
except Exception:
 pass
from src.catalog import restaurants, menus, menu_for, add_restaurant, add_menu_item
from src.predict import trained_ready, predict_existing, predict_new
from src.synthetic_data import portions_per_person
from src.optimizer import optimize
from src.waste_rules import get_rule
from src.climate import climate_result, climate_scenario, LANDFILL_FACTOR_KG_CO2E_PER_KG
from src.ngo import ngos,load,process_timeouts,create_request,respond,send_smtp,advance_after_response, smtp_configured, test_smtp_connection

st.set_page_config(page_title='Food Waste & Climate Impact Analyzer',page_icon='♻️',layout='wide')

# ---------------------------------------------------------------- UI LAYER (presentation only)
st.markdown("""
<style>
:root {
  --ink:#20352e; --ink2:#526a60; --line:#d8e6db;
  --green:#176b4b; --green-dark:#104b39; --green-soft:#e9f5e9;
  --cream:#fff9e9; --paper:#f6f8ef; --card:#ffffff;
}
html, body, .stApp, [class*="css"] {
  font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,sans-serif;
  color:var(--ink);
}
.stApp {
  background:
    radial-gradient(ellipse at 86% 7%, rgba(220,239,202,.78) 0, rgba(220,239,202,0) 30%),
    radial-gradient(ellipse at 4% 80%, rgba(196,232,218,.72) 0, rgba(196,232,218,0) 28%),
    radial-gradient(ellipse at 76% 94%, rgba(255,238,190,.52) 0, rgba(255,238,190,0) 32%),
    linear-gradient(125deg,#f8f8ef 0%,#eef6eb 38%,#fff9ed 68%,#e7f3e9 100%);
  background-attachment:fixed;
}
[data-testid="stAppViewContainer"] {
  background:linear-gradient(130deg,rgba(246,250,241,.30),rgba(255,250,237,.22) 55%,rgba(226,244,230,.26));
}
header[data-testid="stHeader"] {background:rgba(248,250,244,.58);}
#MainMenu, footer {visibility:hidden;}
.block-container {max-width:1180px;padding:2rem 2rem 4rem;}
h1,h2,h3,h4 {letter-spacing:-.025em;color:var(--ink)!important;font-weight:650;}
h3 {font-size:1.25rem;margin-top:1.6rem;}
p,li,.stMarkdown {line-height:1.6;color:var(--ink);}
label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label, [data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p, [data-testid="stDateInput"] label,
[data-testid="stNumberInput"] label, [data-testid="stSelectbox"] label {
  color:#30483e!important;
  -webkit-text-fill-color:#30483e!important;
  opacity:1!important;
}
[data-testid="stCaptionContainer"],.stCaption {color:var(--ink2)!important;}
/* Sage-to-cream sidebar */
[data-testid="stSidebar"] {
  background:linear-gradient(160deg,#eaf4e8 0%,#fbf6e8 50%,#e4f2e7 100%)!important;
  border-right:1px solid #dbe8dc;
}
[data-testid="stSidebar"] * {color:var(--ink);}
[data-testid="stSidebar"] div[role="radiogroup"] {gap:5px;}
[data-testid="stSidebar"] div[role="radiogroup"] label {
  padding:.62rem .78rem;border-radius:12px;transition:all .18s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  background:rgba(202,229,207,.72);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background:linear-gradient(110deg,#2b815a,#104e3b);
  box-shadow:0 5px 14px rgba(22,92,62,.14);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) *,
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
  color:#fff!important;-webkit-text-fill-color:#fff!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label>div:first-child {display:none;}
/* Brand and hero */
.brand {display:flex;align-items:center;gap:.6rem;font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);margin-bottom:2rem;}
.brand b {color:var(--green);}
.brand .dot {width:8px;height:8px;border-radius:50%;background:#23835a;box-shadow:0 0 0 4px rgba(35,131,90,.10);}
.hero {margin:0 0 1.8rem;padding:0 0 1.5rem;border-bottom:1px solid rgba(188,211,192,.72);}
.hero .eyebrow {font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:#218257;font-weight:750;margin-bottom:.7rem;}
.hero h1 {font-size:2.8rem;line-height:1.08;margin:0 0 .8rem;font-weight:750;}
.hero p {font-size:1.12rem;color:#61766b!important;max-width:46rem;margin:0;}
/* Workflow chips */
.flow {display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:0 0 1.8rem;}
.flow span.s {background:rgba(255,255,255,.88);border:1px solid #dce8dd;border-radius:999px;padding:.43rem .9rem;font-size:.86rem;color:#30483e;}
.flow span.a {color:#9aafa2;}
.flow span.s.g {background:linear-gradient(120deg,#edf8e9,#e3f2e8);border-color:#c7dfce;color:#176b4b;font-weight:650;}
/* Journey cards */
.journey {display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:0 0 2.2rem;}
.journey div {background:rgba(255,255,255,.91);border:1px solid var(--line);border-radius:16px;padding:1.1rem 1.2rem;box-shadow:0 7px 20px rgba(40,80,55,.045);}
.journey em {font-style:normal;font-size:.78rem;letter-spacing:.14em;color:var(--green);font-weight:700;display:block;margin-bottom:.35rem;}
.journey strong {font-size:1.02rem;font-weight:650;}
/* Status pills */
.pill {display:inline-block;border-radius:999px;padding:.2rem .7rem;font-size:.78rem;font-weight:650;margin-right:.4rem;border:1px solid var(--line);background:#fff;}
.pill.pending {background:#fff7e6;color:#805500;border-color:#f1deb0;}
.pill.accepted {background:#e8f5e9;color:#176b4b;border-color:#cfe0d6;}
.pill.declined {background:#fdeeee;color:#9b2c2c;border-color:#f1c9c9;}
.pill.timeout {background:#f1f1f3;color:#555;}
/* Metrics */
[data-testid="stMetric"] {
  background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(241,249,239,.96))!important;
  border:1px solid #dce8dd;border-radius:16px;padding:1.1rem 1.2rem;
  box-shadow:0 7px 20px rgba(40,80,55,.05);
}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] * {color:#5b7166!important;}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] * {color:var(--ink)!important;font-size:1.9rem;font-weight:700;letter-spacing:-.02em;}
/* Buttons */
.stButton>button,.stFormSubmitButton>button {
  border-radius:999px;border:1px solid #d6e4d8;background:rgba(255,255,255,.96);
  color:#20352e!important;padding:.58rem 1.35rem;font-weight:650;transition:all .18s ease;
}
.stButton>button:hover,.stFormSubmitButton>button:hover {
  border-color:#5a9a75;transform:translateY(-1px);box-shadow:0 5px 15px rgba(24,91,60,.12);
}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {
  background:linear-gradient(110deg,#2b815a,#104e3b)!important;color:#fff!important;border-color:#176b4b!important;
}
.stButton>button[kind="primary"] *, .stFormSubmitButton>button[kind="primary"] * {color:#fff!important;}
.stButton>button[kind="primary"]:hover {background:linear-gradient(110deg,#23734f,#0b3f30)!important;}
/* Force light, readable Streamlit/BaseWeb controls */
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"],
[data-testid="stDateInput"] [data-baseweb="input"] {
  border-radius:11px!important;border:1px solid #d7e3d9!important;
  background:#fff!important;box-shadow:none!important;
}
[data-baseweb="input"]>div,[data-baseweb="input"]>div>div,
[data-baseweb="textarea"]>div,[data-baseweb="select"]>div,
[data-testid="stNumberInput"] [data-baseweb="input"]>div {
  background:#fff!important;color:#20352e!important;
}
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea,
[data-baseweb="select"] input,[data-baseweb="select"] [role="combobox"],
[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input {
  color:#20352e!important;-webkit-text-fill-color:#20352e!important;
  background:#fff!important;opacity:1!important;
}
[data-baseweb="select"] svg {fill:#526a60!important;color:#526a60!important;}
[data-baseweb="select"] [role="option"] {color:#20352e!important;background:#fff!important;}
[data-baseweb="select"] [role="option"]:hover {background:#eaf5e9!important;}
[data-testid="stCheckbox"] label,[data-testid="stCheckbox"] label *,
[data-testid="stRadio"] label,[data-testid="stRadio"] label * {
  color:#30483e!important;-webkit-text-fill-color:#30483e!important;
}
[data-testid="stCheckbox"] input {accent-color:#176b4b;}
/* Cards / alerts */
[data-testid="stForm"] {
  background:linear-gradient(135deg,rgba(255,255,255,.97),rgba(248,252,245,.96))!important;
  border:1px solid #dce8dd;border-radius:18px;padding:1.6rem;
  box-shadow:0 9px 25px rgba(37,79,53,.06);
}
[data-testid="stExpander"] {background:rgba(255,255,255,.86);border:1px solid #dce8dd!important;border-radius:14px;}
[data-testid="stAlert"] {border-radius:14px;border:1px solid #d7e8d9;background:linear-gradient(115deg,rgba(237,248,235,.97),rgba(255,250,237,.97));}
[data-testid="stDataFrame"] {border:1px solid #dce8dd;border-radius:14px;overflow:hidden;}
.stProgress>div>div>div>div {background:#238257;}
hr {border-color:#dce8dd;}

/* Botanical artwork layer: decorative only, never blocks controls */
.eco-art {
  position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden;
}
.eco-art svg {position:absolute; overflow:visible;}
.eco-art .globe {width:min(22vw,340px); min-width:220px; height:auto; right:-22px; top:76px; opacity:.48;}
.eco-art .lower-leaves {width:245px;height:auto;left:-52px;bottom:-25px;opacity:.55;}
.eco-art .right-leaves {width:210px;height:auto;right:-60px;bottom:-32px;opacity:.35;}
.eco-art .floating-leaf {width:48px;height:auto;right:8%;top:7%;opacity:.5;transform:rotate(20deg);}
.eco-art .small-cloud {position:absolute;right:14%;top:23%;width:90px;height:22px;border-radius:30px;background:rgba(255,255,255,.62);filter:blur(.2px);}
.eco-art .small-cloud:before,.eco-art .small-cloud:after {content:"";position:absolute;bottom:5px;border-radius:50%;background:inherit;}
.eco-art .small-cloud:before {width:32px;height:32px;left:17px;}
.eco-art .small-cloud:after {width:25px;height:25px;left:42px;}
.main .block-container {position:relative;z-index:1;}
[data-testid="stSidebar"] > div:first-child {position:relative;z-index:1;}
/* Small brand lockup and sustainability note in the sidebar */
.sidebar-brand {display:flex;align-items:center;gap:10px;padding:10px 4px 24px;margin-bottom:10px;border-bottom:1px solid rgba(91,133,99,.15);}
.sidebar-brand .leaf-mark {font-size:30px;line-height:1;filter:saturate(.9);}
.sidebar-brand .brand-title {font-size:.82rem;font-weight:800;letter-spacing:.045em;line-height:1.25;color:#15543e;}
.sidebar-brand .brand-subtitle {font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;color:#708478;margin-top:3px;}
.sidebar-note {position:relative;margin-top:2rem;padding:13px 12px;border:1px solid rgba(176,207,177,.55);border-radius:16px;background:linear-gradient(135deg,rgba(255,255,255,.60),rgba(224,242,224,.65));box-shadow:0 8px 24px rgba(48,91,57,.045);display:flex;align-items:center;gap:10px;}
.sidebar-note .note-icon {font-size:25px;}
.sidebar-note .note-text {font-size:.75rem;line-height:1.45;color:#375747;}
@media (max-width:900px) {
 .eco-art .globe {right:-100px;top:100px;opacity:.24;}
 .eco-art .lower-leaves {width:155px;left:-65px;opacity:.25;}
 .eco-art .right-leaves {width:120px;opacity:.2;}
 .eco-art .floating-leaf,.eco-art .small-cloud {display:none;}
}

</style>
""", unsafe_allow_html=True)

# Decorative botanical artwork inspired by the chosen sage/cream reference.
# This layer is visual only; all prediction and workflow logic stays unchanged.
st.markdown("""
<div class="eco-art" aria-hidden="true">
  <svg class="globe" viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <radialGradient id="earthFill" cx="32%" cy="25%" r="78%">
        <stop offset="0%" stop-color="#f4f8d9"/>
        <stop offset="58%" stop-color="#b9dfc8"/>
        <stop offset="100%" stop-color="#82c6b0"/>
      </radialGradient>
      <clipPath id="earthClip"><circle cx="160" cy="160" r="142"/></clipPath>
    </defs>
    <circle cx="160" cy="160" r="145" fill="#d6ead0" opacity=".55"/>
    <circle cx="160" cy="160" r="136" fill="url(#earthFill)" stroke="#a7d5bd" stroke-width="2"/>
    <g clip-path="url(#earthClip)" fill="#eaf3c9" opacity=".9">
      <path d="M48 83l25-18 24 8 11 24-19 17-5 28-25-5-9-25-18-7z"/>
      <path d="M130 43l33 5 15 20-11 19-28 2-14-19z"/>
      <path d="M171 104l31-17 32 13 14 28-15 25-7 30-25 14-17-23-23-10 4-27-18-16z"/>
      <path d="M91 176l28-10 24 20 4 30-19 19-12 35-21-15-9-34-16-17z"/>
      <path d="M214 221l28-11 23 19-5 28-26 15-20-20z"/>
      <path d="M43 146l22-9 15 13-8 22-20 4z"/>
    </g>
    <g fill="none" stroke="#ffffff" stroke-width="2" opacity=".62">
      <ellipse cx="160" cy="160" rx="61" ry="136"/>
      <ellipse cx="160" cy="160" rx="112" ry="136"/>
      <ellipse cx="160" cy="160" rx="136" ry="47"/>
      <ellipse cx="160" cy="160" rx="136" ry="91"/>
      <path d="M24 160h272M160 24v272"/>
    </g>
  </svg>
  <svg class="floating-leaf" viewBox="0 0 80 110" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 98C9 50 28 13 70 7C70 49 48 84 9 98Z" fill="#9bc87e"/>
    <path d="M10 98L61 22" fill="none" stroke="#eaf4d9" stroke-width="2.5"/>
  </svg>
  <svg class="lower-leaves" viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg">
    <path d="M66 248C16 191 13 111 65 38C103 105 102 183 66 248Z" fill="#55a98b"/>
    <path d="M68 248C65 174 65 106 65 44" fill="none" stroke="#d8f0dc" stroke-width="3"/>
    <path d="M68 247C84 166 139 117 211 119C183 183 132 224 68 247Z" fill="#8dc99b"/>
    <path d="M68 247L196 132" fill="none" stroke="#e4f4df" stroke-width="3"/>
    <path d="M61 248C21 222 2 183 8 143C47 163 67 199 61 248Z" fill="#2f8b73"/>
  </svg>
  <svg class="right-leaves" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 218C12 148 52 80 125 35C125 111 84 178 12 218Z" fill="#72b998"/>
    <path d="M13 218L112 54" fill="none" stroke="#e6f5dd" stroke-width="3"/>
    <path d="M20 219C84 154 142 137 210 153C164 203 99 225 20 219Z" fill="#a6d49a"/>
    <path d="M21 219L194 162" fill="none" stroke="#f0f8e7" stroke-width="3"/>
  </svg>
  <div class="small-cloud"></div>
</div>
""", unsafe_allow_html=True)

def ui_brand():
    st.markdown('<div class="brand"><span class="dot"></span><b>Rescue</b>&nbsp;Food Waste &amp; Climate Impact Analyzer</div>', unsafe_allow_html=True)

def ui_hero(title, sub='', eyebrow=''):
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)

def ui_flow(steps, green_last=True):
    out=''
    for i,t in enumerate(steps):
        g=' g' if (green_last and i==len(steps)-1) else ''
        out+=f'<span class="s{g}">{t}</span>'+('<span class="a">→</span>' if i<len(steps)-1 else '')
    st.markdown(f'<div class="flow">{out}</div>', unsafe_allow_html=True)

def ui_journey(items):
    cards=''.join(f'<div><em>{n}</em><strong>{t}</strong></div>' for n,t in items)
    st.markdown(f'<div class="journey">{cards}</div>', unsafe_allow_html=True)
# ---------------------------------------------------------------- END UI LAYER

ui_brand()
ui_flow(['Demand forecasting','Preparation recommendation','Waste reduction','Climate impact','Food rescue'])

DATA=ROOT/'data'/'food_service_research_dataset.csv'; hist=pd.read_csv(DATA,parse_dates=['Date'])

def qty_display(value_kg, item_row):
 unit=str(item_row.get('Quantity_Unit','kg'))
 # Beverage/liquid portions are stored as ml-equivalent grams for forecasting;
 # for display we report litres using the configured 1 kg/L density-equivalent.
 if unit=='L': return float(value_kg), 'L'
 return float(value_kg), 'kg'

if not trained_ready(): st.error('Models have not been trained yet. Run: python train_models.py'); st.stop()
summary=json.loads((ROOT/'results/models/model_selection.json').read_text())
# Handle email response links first
q=st.query_params
if 'ngo_request' in q and 'response' in q:
 rid=q['ngo_request']; status=q['response']
 if status in ('accept','decline'):
  ok=respond(rid,'accepted' if status=='accept' else 'declined')
  st.success('Response recorded. Thank you.') if ok else st.warning('This request is no longer pending.')
  if ok and status=='decline':
   from src.ngo import advance_after_response
   nxt=advance_after_response(rid)
   if nxt: st.info('The first NGO declined. The request has moved to the next NGO for this location.')

# top navigation
st.sidebar.markdown("""
<div class="sidebar-brand">
  <span class="leaf-mark">🌿</span>
  <div><div class="brand-title">FOOD WASTE</div><div class="brand-subtitle">&amp; Climate Impact Analyzer</div></div>
</div>
""", unsafe_allow_html=True)
page=st.sidebar.radio('Go to',['🍱 Food Waste Prediction','🏪 Add New Restaurant','🌍 Climate Impact','♻️ Waste Management','🤝 NGO Matching','📊 Model Comparison','ℹ️ How It Works'])
st.sidebar.markdown("""
<div class="sidebar-note">
  <span class="note-icon">🌱</span>
  <div class="note-text">Smarter Food Choices<br><strong>for a Greener Tomorrow</strong></div>
</div>
""", unsafe_allow_html=True)

if page=='🍱 Food Waste Prediction':
 ui_hero('Food Waste Prediction','Forecast demand for any menu item and prepare exactly what you need.','Forecasting')
 st.write('Choose an existing restaurant and one of its menu items. The trained XGBoost/baseline model uses calendar, holiday, promotion, temperature, rainfall and historical-demand features.')
 rs=restaurants(); rlabel={f"{r.Restaurant_Name} — {r.Location} ({r.Restaurant_ID})":r.Restaurant_ID for _,r in rs.iterrows()}
 rchoice=st.selectbox('Restaurant',list(rlabel)); rid=rlabel[rchoice]; r=rs[rs.Restaurant_ID==rid].iloc[0]
 mm=menu_for(rid); ilabel={f"{x.Item_Name} ({x.Item_ID})":x.Item_ID for _,x in mm.iterrows()}; ichoice=st.selectbox('Menu item',list(ilabel)); iid=ilabel[ichoice]; item=mm[mm.Item_ID==iid].iloc[0]
 c1,c2,c3=st.columns(3); fdate=c1.date_input('Prediction date',date.today()); temp=c2.number_input('Expected temperature (°C)',15.0,45.0,29.0); rain=c3.number_input('Expected rainfall (mm)',0.0,200.0,5.0)
 c1,c2=st.columns(2); holiday=c1.checkbox('Holiday'); promotion=c2.checkbox('Promotion')
 if st.button('Predict preparation quantity',type='primary'):
  try:
   kg,serv=predict_existing(rid,iid,str(fdate),temp,rain,holiday,promotion,hist)
   mode='ML forecast'
  except Exception:
   kg,serv,npeer=predict_new(item.Item_Name,item.Food_Category,item.Meal_Type,r.Location,str(fdate),temp,rain,holiday,promotion,hist)
   mode=f'Cold-start transfer estimate from {npeer} historical rows'
  # All decision calculations use SERVINGS. The model target remains kg-equivalent internally;
  # display units are item-specific (kg for foods, L for configured liquids).
  piece_kg=float(item.Serving_Mass_g)/1000
  person_portions=portions_per_person(str(item.Item_Name))
  serving_kg=piece_kg*person_portions
  forecast_servings=kg/serving_kg if serving_kg>0 else serv
  rng=np.random.default_rng(42)
  spread=max(1.0,0.12*forecast_servings)
  samples=np.maximum(0,rng.normal(forecast_servings,spread,size=2000))
  p10,p90=np.percentile(samples,[10,90])
  dec=optimize(samples,shortage_cost=50,overage_cost=20,emission_factor=float(item.Emission_Factor_kgCO2e_per_kg),portion_kg=serving_kg,prep_cost=1,min_preparation_servings=forecast_servings)
  prep=float(dec['preparation_servings']); prepkg=prep*serving_kg; waste=float(dec['expected_waste_kg'])

  # Transparent benchmark: assume a conventional policy prepares 15% above forecast
  # and that this excess becomes avoidable waste. This is a scenario benchmark,
  # not measured historical waste.
  benchmark_excess_kg=max(0.0, kg*0.15)
  estimated_waste_reduction=max(0.0,benchmark_excess_kg-waste)
  benchmark_prep_kg=kg*1.15

  unit=str(item.get('Quantity_Unit','kg'))
  demand_disp,demand_unit=qty_display(kg,item)
  prep_disp,_=qty_display(prepkg,item)
  waste_disp,_=qty_display(waste,item)
  benchmark_disp,_=qty_display(benchmark_excess_kg,item)
  p10_disp=p10; p90_disp=p90
  st.session_state['last_prediction']={'restaurant':r,'item':item,'forecast_kg':kg,'forecast_servings':forecast_servings,'display_unit':unit,'decision':dec,'benchmark_waste_kg':benchmark_excess_kg,'estimated_waste_reduction':estimated_waste_reduction,'prepkg':prepkg,'wastekg':waste,'date':fdate,'p10_servings':p10,'p90_servings':p90,'recommended_servings':prep}
  a,b,c,d=st.columns(4)
  a.metric('Predicted demand',f'{demand_disp:.2f} {demand_unit}')
  b.metric('Approx. people served',f'{forecast_servings:.0f}')
  c.metric('Recommended preparation',f'{prep_disp:.2f} {demand_unit}')
  d.metric('Expected waste',f'{waste_disp:.2f} {demand_unit}')
  st.info(f'Forecast uncertainty: approximately {p10:.0f}–{p90:.0f} servings (10th–90th percentile). Recommendation is at least the point forecast and may be slightly higher when service-risk warrants it.')
  st.metric('Estimated waste avoided vs 15% over-preparation benchmark',f"{estimated_waste_reduction:.2f} {demand_unit}")
  if str(item.Item_Name) in {'Idli','Dosa','Roti','Burger'}:
   portion_text=f"{person_portions:g} × {item.Item_Name} per person (~{serving_kg*1000:.0f} g/person)"
  else:
   portion_text=f"{float(item.Serving_Mass_g):.0f} {'mL' if demand_unit=='L' else 'g'} per person"
  st.success(f"For {item.Item_Name} at {r.Restaurant_Name} on {fdate}: prepare about {prep_disp:.2f} {demand_unit}. This corresponds to approximately {prep:.0f} people served. Planning portion: {portion_text}.")
  st.caption('Forecast mode: '+mode)
  st.caption('Quantity units are item-specific: solid foods are shown in kg; configured liquid items (for example coffee, tea, soup, sambar and juice) are shown in litres. For Idli, Dosa, Roti and Burger, the system converts piece-level food mass into a person-equivalent portion before showing people served and optimizing preparation. Other menu items are unchanged. Liquid display uses a 1 kg/L density-equivalent for the synthetic planning dataset.')
  st.caption(f'Illustrative benchmark: {benchmark_prep_kg:.2f} kg-equivalent preparation (15% above forecast), with {benchmark_excess_kg:.2f} {demand_unit} treated as potentially avoidable over-preparation waste. This is a scenario assumption, not measured waste.')
  st.subheader('Why demand changes on this day')
  st.write(f"Holiday: **{'Yes' if holiday else 'No'}** · Weekend: **{'Yes' if fdate.weekday()>=5 else 'No'}** · Temperature: **{temp:.1f}°C** · Rainfall: **{rain:.1f} mm** · Promotion: **{'Yes' if promotion else 'No'}**")
  st.info('The model uses these as prediction features. Weather values should be forecast weather when used operationally, not observed future weather.')

elif page=='🏪 Add New Restaurant':
 ui_hero('Add a Restaurant','Set up a new kitchen and its menu. Predictions start from a transparent cold-start estimate.','Onboarding')
 st.write('Existing restaurants and menus remain unchanged. This section is only for adding a genuinely new restaurant.')
 with st.form('newrest'):
  name=st.text_input('Restaurant name'); rid=st.text_input('Unique restaurant ID',placeholder='R013'); loc=st.selectbox('Sample Chennai location',sorted(restaurants().Location.unique().tolist()+['Madhya Kailash','Koyambedu','Alandur','Chromepet'])); phone=st.text_input('Phone'); email=st.text_input('Contact email')
  st.subheader('Menu for this new restaurant')
  names=st.text_area('Enter 7–10 menu items, one per line',value='Idli\nDosa\nRice Bowl\nVeg Meals\nRoti\nBiryani\nSoup')
  submitted=st.form_submit_button('Save new restaurant and menu')
  if submitted:
   try:
    add_restaurant(name,rid,loc,phone,email); items=[x.strip() for x in names.splitlines() if x.strip()]
    for j,n in enumerate(items[:10],1):
     row=hist[hist.Item_Name.str.lower()==n.lower()].head(1)
     if len(row): cat=row.Food_Category.iloc[0]; meal=row.Meal_Type.iloc[0]; mass=float(row.Serving_Mass_g.iloc[0]); ef=float(row.Emission_Factor_kgCO2e_per_kg.iloc[0])
     else: cat='Other'; meal='Lunch'; mass=200; ef=.0
     # Match the quantity unit to the nearest known item; unknown items default to kg.
     unit='L' if (len(row) and str(row.Quantity_Unit.iloc[0])=='L') else 'kg'
     add_menu_item(rid,f'{rid}_{j:02d}',n,meal,cat,mass,ef,unit)
    st.success('Restaurant and menu saved. It will now appear in the existing-restaurant list.')
    st.warning('Cold-start note: this new restaurant has no own sales history. The next prediction uses transfer estimates from existing restaurants and matching food categories/locations; it is explicitly labelled as a cold-start estimate.')
   except Exception as e: st.error(str(e))
 st.subheader('Current restaurants')
 st.dataframe(restaurants(),use_container_width=True,hide_index=True)

elif page=='🌍 Climate Impact':
 ui_hero('Climate Impact','See how smarter preparation turns into avoided waste and a lower disposal burden.','Impact'); ui_flow(['Demand prediction','Reduced over-preparation','Reduced food waste','Reduced disposal burden','Climate benefit'])
 st.caption('A clear view of how demand forecasting can reduce food waste and the associated disposal burden.')
 p=st.session_state.get('last_prediction')
 if not p: st.info('First make a prediction in Food Waste Prediction.')
 else:
  item=p['item']
  waste=float(max(0.0,p['wastekg']))
  base_waste=float(max(0.0,p.get('benchmark_waste_kg',waste)))
  scenario=climate_scenario(
   benchmark_excess_waste_kg=base_waste,
   expected_waste_kg=waste,
   diversion='organic_processing',
   factor=LANDFILL_FACTOR_KG_CO2E_PER_KG,
  )
  avoided_waste=scenario['avoided_waste_kg']
  benchmark_burden=scenario['benchmark_landfill_burden_co2e_kg']
  model_route_burden=scenario['model_route_burden_co2e_kg']
  avoided_burden=scenario['total_avoided_burden_co2e_kg']

  # Visual-only presentation layer: all underlying climate calculations remain unchanged.
  st.markdown('### 🌱 Environmental outcome')
  a,b,c,d=st.columns(4)
  a.metric('Expected waste',f"{waste:.2f} kg")
  b.metric('Benchmark excess',f"{base_waste:.2f} kg")
  c.metric('Food waste avoided',f"{avoided_waste:.2f} kg")
  d.metric('Estimated CO₂e burden avoided',f"{avoided_burden:.2f} kg CO₂e")

  st.progress(min(1.0, avoided_waste/base_waste) if base_waste>0 else 0.0, text='Share of benchmark excess waste avoided')

  left,right=st.columns([1.15,0.85])
  with left:
   st.markdown('#### 📊 Waste-to-impact pathway')
   st.info(
    f"**{item.Item_Name}** → expected waste **{waste:.2f} kg** → **{avoided_waste:.2f} kg** below the illustrative benchmark → **{avoided_burden:.2f} kg CO₂e** estimated disposal burden avoided."
   )
  with right:
   st.markdown('#### 🔎 Scenario assumptions')
   st.metric('Landfill factor',f"{scenario['landfill_factor_kgco2e_per_kg']:.2f} kg CO₂e/kg")
   st.metric('Organic-processing route factor',f"{scenario['route_factor']:.2f}×")

  with st.expander('📐 View detailed calculation', expanded=False):
   st.markdown('### 1. Food-waste comparison')
   st.write(f"**Illustrative benchmark excess:** {base_waste:.2f} kg")
   st.write(f"**Expected waste with the model:** {waste:.2f} kg")
   st.latex(r"\text{Food Waste Avoided}=\text{Benchmark Excess}-\text{Model Expected Waste}")
   st.write(f"**Calculation:** {base_waste:.2f} − {waste:.2f} = **{avoided_waste:.2f} kg food waste avoided**")

   st.divider()
   st.markdown('### 2. Benchmark disposal burden')
   st.write(f"**Illustrative landfill factor:** {scenario['landfill_factor_kgco2e_per_kg']:.2f} kg CO₂e/kg food waste")
   st.latex(r"\text{Benchmark CO₂e}=\text{Benchmark Excess Waste}\times\text{Landfill Factor}")
   st.write(f"**Calculation:** {base_waste:.2f} × {scenario['landfill_factor_kgco2e_per_kg']:.2f} = **{benchmark_burden:.2f} kg CO₂e**")

   st.divider()
   st.markdown('### 3. Model waste under the same landfill baseline')
   model_landfill=scenario['model_landfill_equivalent_burden_co2e_kg']
   waste_reduction_benefit=scenario['avoided_burden_from_waste_reduction_co2e_kg']
   st.latex(r"\text{Model Landfill-Equivalent CO₂e}=\text{Model Waste}\times\text{Landfill Factor}")
   st.write(f"**Calculation:** {waste:.2f} × {scenario['landfill_factor_kgco2e_per_kg']:.2f} = **{model_landfill:.2f} kg CO₂e**")
   st.write(f"**Burden avoided from producing less waste:** {benchmark_burden:.2f} − {model_landfill:.2f} = **{waste_reduction_benefit:.2f} kg CO₂e**")

   st.divider()
   st.markdown('### 4. Selected organic-processing route')
   st.write(f"**Illustrative route factor:** {scenario['route_factor']:.2f} × landfill-equivalent burden")
   st.latex(r"\text{Route CO₂e}=\text{Model Waste}\times\text{Landfill Factor}\times\text{Route Factor}")
   st.write(f"**Calculation:** {waste:.2f} × {scenario['landfill_factor_kgco2e_per_kg']:.2f} × {scenario['route_factor']:.2f} = **{model_route_burden:.2f} kg CO₂e**")
   st.write(f"**Additional illustrative diversion benefit:** {model_landfill:.2f} − {model_route_burden:.2f} = **{scenario['diversion_benefit_co2e_kg']:.2f} kg CO₂e**")

   st.divider()
   st.markdown('### 5. Total scenario comparison')
   st.latex(r"\text{Total Avoided CO₂e}=\text{Benchmark Landfill Burden}-\text{Model Route Burden}")
   st.write(f"**Calculation:** {benchmark_burden:.2f} − {model_route_burden:.2f} = **{avoided_burden:.2f} kg CO₂e estimated disposal burden avoided**")

  st.success(
   f"**Model contribution:** compared with the project's illustrative 15% over-preparation benchmark, this run estimates **{avoided_waste:.2f} kg of food waste avoided** and **{avoided_burden:.2f} kg CO₂e of estimated disposal burden avoided**."
  )
  st.caption('The 15% benchmark represents assumed excess preparation above predicted demand; it is not measured historical waste. The climate comparison combines lower waste with the selected organic-processing scenario.')
  st.write('**Why diversion matters:** food waste sent to landfill can contribute to methane generation under anaerobic conditions. Suitable organic waste can instead be diverted through routes such as composting or anaerobic digestion; anaerobic digestion can also recover biogas.')
  st.warning(scenario['factor_note'])

elif page=='♻️ Waste Management':
 ui_hero('Waste Management','The right route for every kind of surplus, from prevention to authorised treatment.','Operations'); ui_flow(['Prevent overproduction','Redistribute safe edible surplus','Segregate inedible organics','Authorised treatment route'])
 p=st.session_state.get('last_prediction')
 if not p: st.info('First make a prediction.')
 else:
  item=p['item']; cat=item.Food_Category; rule,kind=get_rule(cat); st.subheader(f"{item.Item_Name} — {cat}"); st.write(rule)
  st.write('**Priority:** 1) prevent overproduction, 2) if safe, redistribute edible surplus, 3) segregate inedible organics and use an authorised treatment route accepted locally, 4) avoid drains/soil for unsuitable wastes.')
  st.write('For donation, FSSAI surplus-food regulations require surplus food to be safe, appropriately handled, and handed over in time for consumption within shelf life; records and hygienic storage/transport are also required. citeturn0search33')
  if kind in ('organic','animal-derived'):
   st.info('Climate pathway: suitable segregated organic waste may be sent to authorised composting or anaerobic digestion where accepted. These pathways can avoid some landfill methane and may recover nutrients/energy. citeturn0search31turn0search1')

elif page=='🤝 NGO Matching':
 ui_hero('NGO Matching','Coordinate food rescue with local NGOs, with a 30-minute response window and automatic fallback.','Food rescue'); st.markdown('<span class="pill pending">Pending</span><span class="pill accepted">Accepted</span><span class="pill declined">Declined</span><span class="pill timeout">Timeout</span>', unsafe_allow_html=True)
 st.caption('The system matches NGOs by restaurant location. In Guide Demo Mode, the selected real NGO remains the NGO for the request, while the actual email is delivered to your configured demo test recipient.')
 process_timeouts()
 requests=load()
 # Advance timed-out requests once the page is opened.
 for rr in list(requests):
  if rr.get('status')=='timeout':
   nxt=advance_after_response(rr['request_id'])
   if nxt: st.info(f"30-minute timeout: request moved to {nxt['ngo']}.")
 requests=load()

 with st.expander('SMTP configuration / connection test', expanded=not smtp_configured()):
  st.write('For Gmail, use an App Password rather than your normal Gmail password.')
  if smtp_configured():
   ok,msg=test_smtp_connection()
   (st.success if ok else st.error)(msg)
  else:
   st.warning('SMTP is not configured yet. You can still use the simulated Accept/Decline buttons for local testing.')
   st.code('SMTP_HOST=smtp.gmail.com\nSMTP_PORT=587\nSMTP_USER=yourproject@gmail.com\nSMTP_PASSWORD=your_16_character_app_password\nSMTP_FROM=yourproject@gmail.com\nRESPONSE_BASE_URL=http://localhost:8501',language='text')

 p=st.session_state.get('last_prediction')
 demo_mode=st.checkbox(
  '🎓 Guide demo mode — send to my test email(s)',
  value=False,
  help='Keeps the real location-matched NGO selected in the request, but routes the actual email to your configured demo test recipients.'
 )
 if demo_mode:
  st.info('**Demo recipients:** first request → itzsush7@gmail.com · fallback request → sreejakumar2107@gmail.com. These are used only for your presentation/test flow.')

 if p:
  r=p['restaurant']; item=p['item']; wastekg=float(p['wastekg'])
  if wastekg<=0:
   st.info('No predicted surplus is available for NGO redistribution in this scenario.')
  else:
   n=ngos()

   # IMPORTANT: Demo Mode changes only the delivery recipient.
   # NGO matching remains based on the restaurant's actual location.
   local=n[
    n.location.astype(str).str.lower()==str(r.Location).lower()
   ].sort_values('ngo_id')

   if local.empty:
    st.info(f'No sample NGOs configured for the restaurant location: {r.Location}.')
   else:
    st.subheader(f'NGOs matched to {r.Restaurant_Name} — {r.Location}')
    st.dataframe(
     local[['ngo_id','name','email','capacity_servings']],
     use_container_width=True,
     hide_index=True
    )

    st.write(f'Potential surplus: **{wastekg:.2f} kg**')

    ngo_options=[
     f"{row.ngo_id} — {row.name}"
     for _,row in local.iterrows()
    ]
    selected_label=st.selectbox(
     'Select NGO for this donation request',
     ngo_options,
     key='selected_ngo_for_donation'
    )
    selected_index=ngo_options.index(selected_label)
    selected_ngo=local.iloc[selected_index]

    c1,c2=st.columns(2)
    with c1:
     st.markdown('**Selected NGO**')
     st.write(f"**{selected_ngo['name']}**")
     st.write(f"Location: {selected_ngo['location']}")
     st.write(f"Contact: {selected_ngo['email']}")

    # Convert the existing predicted waste mass to the same person-equivalent
    # serving unit already used by the prediction page. No model output changes.
    piece_kg=float(item.Serving_Mass_g)/1000
    person_portions=portions_per_person(str(item.Item_Name))
    serving_kg=piece_kg*person_portions
    waste_servings=wastekg/serving_kg if serving_kg>0 else 0.0

    with c2:
     st.markdown('**Donation request**')
     st.write(f"Food item: **{item.Item_Name}**")
     st.write(f"Quantity: **{wastekg:.2f} {p.get('display_unit','kg')}**")
     st.write(f"Approx. servings: **{waste_servings:.0f}**")

    if demo_mode:
     st.warning(
      '🎓 Demo Mode is ON. The selected NGO name/location will appear in the request, '
      'but the actual email will be delivered to your demo test recipient. '
      'First request → itzsush7@gmail.com; next request after decline/timeout → sreejakumar2107@gmail.com.'
     )
    else:
     st.info('Normal Mode is ON. The email will be sent to the selected NGO contact email shown above.')

    existing_chain=any(
     x.get('restaurant')==r.Restaurant_Name
     and x.get('item')==item.Item_Name
     and x.get('status')=='pending'
     for x in load()
    )

    if not existing_chain:
     if st.button('📨 Send Donation Request',type='primary',use_container_width=True):
      req=create_request(
       r.Restaurant_Name,
       item.Item_Name,
       waste_servings,
       wastekg,
       selected_ngo,
       quantity_unit=p.get('display_unit','kg'),
       demo_mode=demo_mode
      )
      try:
       sent,msg=send_smtp(req)
       if sent:
        if demo_mode:
         st.success(
          f"Donation request sent for {selected_ngo['name']}. "
          f"Demo delivery: first request goes to itzsush7@gmail.com."
         )
        else:
         st.success(
          f"Donation request sent to {selected_ngo['name']} ({selected_ngo['email']})."
         )
       else:
        st.warning(msg)
      except Exception as e:
       st.error(f'SMTP error: {e}')
    else:
     st.info('A pending request for this restaurant/item already exists. Respond to it before starting another chain.')

    st.divider()
    st.subheader('30-minute response window')
    st.info(
     'The NGO receives Accept and Decline links by email. If no response is recorded within 30 minutes, '
     'the pending request is marked as timed out when the NGO workflow is processed, and the system '
     'automatically moves the request to the next matched NGO for the same restaurant location. '
     'In Demo Mode, the next request is delivered to the second configured demo email.'
    )

 st.subheader('Request history')
 requests=load()
 if requests:
  st.dataframe(pd.DataFrame(requests),use_container_width=True,hide_index=True)
  for req in requests:
   if req['status']=='pending':
    a,b=st.columns(2)
    if a.button(f"Simulate ACCEPT — {req['ngo_name']}",key='a'+req['request_id']):
     respond(req['request_id'],'accepted')
     st.rerun()
    if b.button(f"Simulate DECLINE — {req['ngo_name']}",key='d'+req['request_id']):
     respond(req['request_id'],'declined')
     nxt=advance_after_response(req['request_id'])
     if nxt:
      st.success(f"Declined. Request moved to {nxt['ngo']}.")
     st.rerun()
  st.caption('If no response is recorded for 30 minutes, the next time the NGO page is opened the system marks it timeout and sends the request to the next matched NGO.')
 else:
  st.info('No NGO requests yet. Make a prediction first, then start a donation request.')

elif page=='📊 Model Comparison':
 ui_hero('Model Comparison','Candidate models trained on the same chronological window, selected on validation MAE.','Evaluation')
 st.write('We do not assume XGBoost is best. All candidate baselines are trained and compared on the same chronological validation window; the model with the lowest validation MAE is selected, then evaluated once on the later test window.')
 comp=pd.read_csv(ROOT/'results/metrics/model_comparison.csv').sort_values('MAE_kg'); st.dataframe(comp,use_container_width=True,hide_index=True)
 st.success(f"Selected model: {summary['selected_model']} — validation MAE {summary['validation_metrics'][0]['MAE_kg']:.2f} kg")
 st.json(summary['final_test_metrics']); st.caption('These are controlled synthetic-data results, not evidence of real-world restaurant performance.')

else:
 ui_hero('How It Works','From demand forecast to food rescue, in one connected workflow.','Overview'); ui_journey([('01','Demand prediction'),('02','Preparation recommendation'),('03','Waste reduction'),('04','Climate impact'),('05','Waste management'),('06','NGO food rescue'),('07','Model comparison')])
 st.markdown('''**Module 1 — Food waste prediction**\n\nExisting Chennai restaurants have different menus and historical sales. XGBoost, Random Forest, Decision Tree and Linear Regression are compared. For a selected restaurant + menu item + future day, the model uses historical demand, day/weekend, holiday, promotion, temperature and rainfall to estimate demand and preparation quantity.\n\n**New restaurant — cold start**\n\nA new restaurant is registered once with its own menu. Because it has no history, the system does not pretend it has trained history. It transfers an approximate estimate from matching existing restaurants/items/categories in the dataset. After real sales are collected, it can be added to future training.\n\n**Module 2 — Climate impact**\n\nExpected waste is converted to waste mass and an estimated disposal burden. The dashboard explains that forecasting can reduce over-preparation, while diversion can reduce landfill-related impacts.\n\n**Module 3 — Waste management**\n\nEdible surplus is separated from inedible waste. Food-category rules recommend donation or suitable authorised organic/animal-derived treatment routes.\n\n**Module 4 — NGO matching**\n\nThe system filters sample NGOs by the restaurant location, sends a request through SMTP when configured, records accept/decline, and supports a 30-minute timeout before moving to the next NGO.\n\n**Module 5 — Model comparison**\n\nThe dashboard shows why the selected model won instead of simply claiming XGBoost is superior.''')
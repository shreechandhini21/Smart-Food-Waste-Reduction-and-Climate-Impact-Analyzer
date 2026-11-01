from pathlib import Path
import joblib, pandas as pd, numpy as np
from datetime import date
from .models import FEATURES
from .cold_start import estimate_new_restaurant
from .synthetic_data import portions_per_person
ROOT=Path(__file__).resolve().parents[1]

def _codes(): return joblib.load(ROOT/'results'/'models'/'mappings.joblib')
def _model(): return joblib.load(ROOT/'results'/'models'/'selected_model.joblib')
def trained_ready(): return (ROOT/'results'/'models'/'selected_model.joblib').exists() and (ROOT/'results'/'models'/'mappings.joblib').exists()

def feature_row(rid,item_id,forecast_date,temp,rain,holiday,promotion,history):
 c=_codes(); ridcode=c['restaurant_codes'].get(rid,0); itemcode=c['item_codes'].get(item_id,0)
 h=history[(history.Restaurant_ID==rid)&(history.Item_ID==item_id)].sort_values('Date')
 vals=h.Observed_Sales.tail(28).to_numpy(dtype=float) if len(h) else np.array([20.])
 def lag(n): return float(vals[-n]) if len(vals)>=n else float(vals[-1])
 return pd.DataFrame([{ 'Day_of_Week':pd.Timestamp(forecast_date).dayofweek,'Is_Weekend':int(pd.Timestamp(forecast_date).dayofweek>=5),'Holiday':int(holiday),'Promotion':int(promotion),'Temperature_C':float(temp),'Rainfall_mm':float(rain),'Rainy':int(rain>10),'Hot':int(temp>32),'Lag_1_Demand':lag(1),'Lag_7_Demand':lag(7),'Lag_14_Demand':lag(14),'Lag_28_Demand':lag(28),'Rolling_7_Mean_Demand':float(vals[-7:].mean()),'Rolling_28_Mean_Demand':float(vals.mean()),'Restaurant_Code':ridcode,'Item_Code':itemcode,'Serving_Mass_g':float(h.Serving_Mass_g.iloc[-1]) if len(h) else 200.0 }],columns=FEATURES)

def predict_existing(rid,item_id,forecast_date,temp,rain,holiday,promotion,history):
 if not trained_ready(): raise RuntimeError('Models are not trained yet. Run train_models.py first.')
 row=feature_row(rid,item_id,forecast_date,temp,rain,holiday,promotion,history); kg=max(0,float(_model().predict(row)[0])); grams=float(row.Serving_Mass_g.iloc[0]); item_name=str(history[(history.Restaurant_ID==rid)&(history.Item_ID==item_id)].Item_Name.iloc[-1]) if len(history[(history.Restaurant_ID==rid)&(history.Item_ID==item_id)]) else ''; portions=portions_per_person(item_name); person_kg=grams*portions/1000.0; people=kg/person_kg if person_kg>0 else 0.0; return kg,people

def predict_new(item_name,category,meal_type,location,forecast_date,temp,rain,holiday,promotion,history):
 # Cold-start transfer: aggregate peer models/observed history rather than inventing a new restaurant code.
 h=history.copy(); h['score']=0
 peers=h[h.Location.astype(str).str.lower()==str(location).lower()]
 same=peers[peers.Item_Name.astype(str).str.lower()==str(item_name).lower()]
 if len(same)<20: same=peers[peers.Food_Category.astype(str).str.lower()==str(category).lower()]
 if len(same)<20: same=h[h.Food_Category.astype(str).str.lower()==str(category).lower()]
 if same.empty: return 0.0,0.0,0
 # Use peer restaurant/item historical demand adjusted by context ratio.
 same=same.copy(); same['context']=1+0.16*same.Holiday+0.10*same.Promotion+np.where(same.Hot==1,0.08,0)+np.where(same.Rainy==1,-0.05,0)
 base=float((same.True_Demand_Servings/same.context).tail(120).mean()); target_context=1+0.16*int(holiday)+0.10*int(promotion)+(0.08 if temp>32 else 0)-(.05 if rain>10 else 0)
 demand=max(0,base*target_context); grams=float(same.Serving_Mass_g.iloc[-1]); return demand,demand*grams/1000,len(same)

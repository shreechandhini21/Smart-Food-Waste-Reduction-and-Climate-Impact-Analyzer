from pathlib import Path
import json, joblib, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURES=['Day_of_Week','Is_Weekend','Holiday','Promotion','Temperature_C','Rainfall_mm','Rainy','Hot','Lag_1_Demand','Lag_7_Demand','Lag_14_Demand','Lag_28_Demand','Rolling_7_Mean_Demand','Rolling_28_Mean_Demand','Restaurant_Code','Item_Code','Serving_Mass_g']

def add_codes(df):
 df=df.copy(); df['Restaurant_Code']=df['Restaurant_ID'].astype('category').cat.codes; df['Item_Code']=df['Item_ID'].astype('category').cat.codes; return df

def metrics(y,p): return {'MAE_kg':float(mean_absolute_error(y,p)),'RMSE_kg':float(mean_squared_error(y,p)**.5),'R2':float(r2_score(y,p))}
def train_compare(data_path='data/food_service_research_dataset.csv',out='results'):
 df=pd.read_csv(data_path,parse_dates=['Date']); df=add_codes(df); df=df.dropna(subset=FEATURES+['Demand_Target_kg']).sort_values('Date')
 d0=df.Date.min(); vstart=df.Date.quantile(.70); tstart=df.Date.quantile(.85); train=df[df.Date<vstart]; val=df[(df.Date>=vstart)&(df.Date<tstart)]; test=df[df.Date>=tstart]
 models={'Linear Regression':LinearRegression(),'Decision Tree':DecisionTreeRegressor(max_depth=14,min_samples_leaf=8,random_state=42),'Random Forest':RandomForestRegressor(n_estimators=150,max_depth=18,min_samples_leaf=3,n_jobs=-1,random_state=42)}
 try:
  from xgboost import XGBRegressor
  models['XGBoost']=XGBRegressor(n_estimators=500,max_depth=8,learning_rate=.06,subsample=.85,colsample_bytree=.85,objective='reg:squarederror',random_state=42,n_jobs=4)
 except Exception as e: print('XGBoost unavailable:',e)
 results=[]; fitted={}
 for name,m in models.items():
  m.fit(train[FEATURES],train.Demand_Target_kg); p=m.predict(val[FEATURES]); mm=metrics(val.Demand_Target_kg,p); mm['Model']=name; results.append(mm); fitted[name]=m
 comp=pd.DataFrame(results).sort_values('MAE_kg'); winner=comp.iloc[0]['Model']; final=fitted[winner]; final.fit(pd.concat([train,val])[FEATURES],pd.concat([train,val]).Demand_Target_kg); tp=final.predict(test[FEATURES]); testm=metrics(test.Demand_Target_kg,tp)
 Path(out+'/models').mkdir(parents=True,exist_ok=True); Path(out+'/metrics').mkdir(parents=True,exist_ok=True); comp.to_csv(out+'/metrics/model_comparison.csv',index=False); joblib.dump(final,out+'/models/selected_model.joblib'); joblib.dump({'features':FEATURES,'restaurant_codes':dict(zip(df.Restaurant_ID.astype('category').cat.categories,range(df.Restaurant_ID.nunique()))),'item_codes':dict(zip(df.Item_ID.astype('category').cat.categories,range(df.Item_ID.nunique())))},out+'/models/mappings.joblib')
 summary={'selected_model':winner,'validation_metrics':comp.to_dict('records'),'final_test_metrics':testm,'split_dates':{'validation_start':str(vstart.date()),'test_start':str(tstart.date())},'note':'Synthetic controlled benchmark; not real-world evidence.'}; json.dump(summary,open(out+'/models/model_selection.json','w'),indent=2); print(json.dumps(summary,indent=2)); return summary

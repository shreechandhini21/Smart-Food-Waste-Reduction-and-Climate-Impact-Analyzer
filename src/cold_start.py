import pandas as pd, numpy as np

def estimate_new_restaurant(history,location,item_name,temperature,rainfall,holiday,promotion):
 """Transfer estimate from existing restaurants in same location; falls back to same food category."""
 h=history.copy(); h['Location']=h.Location.astype(str); exact=h[h.Location.str.lower()==str(location).lower()]
 if exact.empty: exact=h[h.Item_Name.str.lower()==str(item_name).lower()]
 if exact.empty: exact=h
 same=exact[exact.Item_Name.str.lower()==str(item_name).lower()]
 pool=same if len(same)>=20 else exact
 dow=0
 weather=(pool.Temperature_C-pool.Temperature_C.mean()).abs()<8
 p=pool.copy(); p=p[weather]
 if holiday is not None: p=p[p.Holiday==int(holiday)] if (p.Holiday==int(holiday)).any() else p
 if promotion is not None: p=p[p.Promotion==int(promotion)] if (p.Promotion==int(promotion)).any() else p
 if p.empty: p=pool
 return float(max(0,p.True_Demand_Servings.mean())),int(len(p))

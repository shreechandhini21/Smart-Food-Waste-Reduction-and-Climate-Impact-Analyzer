from pathlib import Path
import numpy as np, pandas as pd

RESTAURANTS = [
('R001','Chennai Tiffin House','T Nagar','044-40010001','contact@tch.example'),
('R002','Velachery Bowl Cafe','Velachery','044-40010002','contact@vbc.example'),
('R003','Adyar Green Kitchen','Adyar','044-40010003','contact@agk.example'),
('R004','Anna Nagar Meals','Anna Nagar','044-40010004','contact@anm.example'),
('R005','Guindy Quick Bites','Guindy','044-40010005','contact@gqb.example'),
('R006','Besant Nagar Cafe','Besant Nagar','044-40010006','contact@bnc.example'),
('R007','Porur Family Kitchen','Porur','044-40010007','contact@pfk.example'),
('R008','Mylapore Traditional Foods','Mylapore','044-40010008','contact@mtf.example'),
('R009','Sholinganallur Cloud Kitchen','Sholinganallur','044-40010009','contact@sck.example'),
('R010','Tambaram Campus Canteen','Tambaram','044-40010010','contact@tcc.example'),
('R011','Nungambakkam Food Corner','Nungambakkam','044-40010011','contact@nfc.example'),
('R012','OMR Healthy Cafe','OMR','044-40010012','contact@ohc.example'),
]
MENUS={
'R001':['Idli','Dosa','Vada','Sambar','Curd Rice','Lemon Rice','Poori','Filter Coffee'],
'R002':['Rice Bowl','Paneer Bowl','Veg Wrap','Noodles','Pasta','Salad','Soup','Cold Coffee'],
'R003':['Idli','Pongal','Dosa','Veg Meals','Sambar','Rasam','Curd Rice','Lemon Juice'],
'R004':['Biryani','Chicken Curry','Veg Meals','Roti','Paneer Bowl','Fried Rice','Noodles','Lassi'],
'R005':['Burger','Chicken Rice','Egg Rice','Sandwich','French Fries','Noodles','Tea','Coffee'],
'R006':['Dosa','Pasta','Sandwich','Salad','Soup','Veg Wrap','Muffin','Cold Coffee'],
'R007':['Veg Meals','Chicken Curry','Fish Meal','Roti','Rice Bowl','Dal Rice','Curd Rice','Payasam'],
'R008':['Idli','Vada','Pongal','Dosa','Sambar','Rasam Rice','Poori','Filter Coffee'],
'R009':['Biryani','Chicken Rice','Paneer Rice','Noodles','Pasta','Burger','Veg Wrap','Juice'],
'R010':['Idli','Dosa','Meals','Curd Rice','Lemon Rice','Roti','Tea','Coffee'],
'R011':['Biryani','Paneer Bowl','Roti','Dal Rice','Noodles','Sandwich','Tea','Juice'],
'R012':['Oats Bowl','Salad','Veg Wrap','Soup','Pasta','Fruit Cup','Muffin','Smoothie'],
}
SPECS={
'Idli':('Breakfast','Grain',40,1.5),'Dosa':('Breakfast','Grain',80,1.5),'Vada':('Breakfast','Grain',45,1.5),'Sambar':('Side','Vegetarian',150,1.0),'Curd Rice':('Lunch','Dairy',180,2.0),'Lemon Rice':('Lunch','Rice',180,1.8),'Poori':('Breakfast','Bread',50,1.6),'Filter Coffee':('Beverage','Beverage',180,0.4),'Rice Bowl':('Lunch','Rice',300,1.8),'Paneer Bowl':('Lunch','Dairy',300,2.2),'Veg Wrap':('Lunch','Vegetarian',180,1.2),'Noodles':('Lunch','Grain',250,1.7),'Pasta':('Lunch','Grain',250,1.7),'Salad':('Lunch','Vegetarian',180,0.8),'Soup':('Lunch','Vegetarian',250,0.8),'Cold Coffee':('Beverage','Dairy',250,1.0),'Pongal':('Breakfast','Grain',200,1.5),'Veg Meals':('Lunch','Vegetarian',450,1.7),'Rasam':('Side','Vegetarian',150,0.8),'Lemon Juice':('Beverage','Beverage',250,0.4),'Biryani':('Lunch','Rice',350,1.8),'Chicken Curry':('Lunch','Meat',220,5.5),'Roti':('Lunch','Bread',45,1.6),'Fried Rice':('Lunch','Rice',300,1.8),'Lassi':('Beverage','Dairy',250,1.2),'Burger':('Lunch','Meat',220,5.5),'Chicken Rice':('Lunch','Meat',300,5.0),'Egg Rice':('Lunch','Egg',280,3.0),'Sandwich':('Snack','Bread',180,1.6),'French Fries':('Snack','Vegetarian',150,1.2),'Tea':('Beverage','Beverage',180,0.4),'Coffee':('Beverage','Beverage',180,0.4),'Fish Meal':('Lunch','Fish',350,6.0),'Dal Rice':('Lunch','Grain',300,1.6),'Payasam':('Dessert','Dairy',150,1.5),'Rasam Rice':('Lunch','Rice',250,1.6),'Juice':('Beverage','Beverage',250,0.5),'Paneer Rice':('Lunch','Dairy',300,2.2),'Meals':('Lunch','Vegetarian',450,1.7),'Oats Bowl':('Breakfast','Grain',250,1.3),'Fruit Cup':('Snack','Fruit',180,0.6),'Smoothie':('Beverage','Fruit',300,0.7),'Muffin':('Snack','Bakery',90,1.5)}
# Food-specific portions per person. These apply only to piece-based menu items.
# Serving_Mass_g remains the mass of ONE piece. Portions_Per_Person converts
# piece demand into a realistic person-equivalent planning portion.
PORTIONS_PER_PERSON={
 'Idli':2.5,    # 2–3 medium idlis per person; planning midpoint = 2.5
 'Dosa':2.5,    # 2–3 medium dosas per person; planning midpoint = 2.5
 'Roti':2.5,    # 2–3 rotis per person; planning midpoint = 2.5
 'Poori':3.0,   # about 3 medium pooris per person
 'Burger':1.0,  # 1 burger per person
}

def portions_per_person(item):
    return float(PORTIONS_PER_PERSON.get(str(item), 1.0))

LIQUID_ITEMS={
 'Sambar','Rasam','Soup','Lemon Juice','Lassi','Tea','Coffee','Filter Coffee','Cold Coffee','Juice','Smoothie'
}

def quantity_unit(item):
    # Display unit: liquids are planned/served by volume; foods by mass.
    return 'L' if item in LIQUID_ITEMS else 'kg'

HOLIDAYS={(1,1),(1,26),(4,14),(5,1),(8,15),(10,2),(11,1),(12,25)}

# Item-level baseline popularity in servings/day. These are controlled synthetic
# assumptions designed to make demand meaningfully different across menu items.
ITEM_POPULARITY={
 'Idli':150,'Dosa':125,'Vada':75,'Sambar':115,'Curd Rice':55,'Lemon Rice':45,'Poori':80,'Filter Coffee':190,
 'Rice Bowl':105,'Paneer Bowl':70,'Veg Wrap':85,'Noodles':95,'Pasta':70,'Salad':45,'Soup':50,'Cold Coffee':120,
 'Pongal':105,'Veg Meals':110,'Rasam':75,'Lemon Juice':90,'Biryani':120,'Chicken Curry':65,'Roti':100,'Fried Rice':100,
 'Lassi':85,'Burger':95,'Chicken Rice':115,'Egg Rice':100,'Sandwich':85,'French Fries':105,'Tea':180,'Coffee':160,
 'Fish Meal':75,'Dal Rice':90,'Payasam':45,'Rasam Rice':80,'Juice':95,'Paneer Rice':80,'Meals':120,'Oats Bowl':80,
 'Fruit Cup':45,'Smoothie':75,'Muffin':55
}

def generate(days=730,start='2024-01-01',seed=42):
    rng=np.random.default_rng(seed); dates=pd.date_range(start,periods=days,freq='D'); rows=[]
    for rid,name,loc,phone,email in RESTAURANTS:
      rmult=float(rng.uniform(.8,1.25)); menu=MENUS[rid]
      for iid,item in enumerate(menu,1):
        meal,cat,serv_g,ef=SPECS[item]; base=float(ITEM_POPULARITY.get(item,80))*rmult
        restaurant_item_effect=float(rng.uniform(.92,1.08))
        for d in dates:
          dow=d.dayofweek; holiday=int((d.month,d.day) in HOLIDAYS); weekend=int(dow>=5)
          temp=float(rng.normal(29 if d.month in [3,4,5] else 27,3.5)); rain=float(max(0,rng.gamma(1.4,4)-2))
          rainy=int(rain>10); hot=int(temp>32); promo=int(rng.random()<0.10)
          weather_effect=.10 if hot and meal in ['Beverage','Snack'] else (-.07 if rainy and meal=='Lunch' else 0)
          holiday_effect=.16 if holiday else 0; weekend_effect=.10 if weekend else 0
          season=1+.10*np.sin(2*np.pi*d.dayofyear/365.25)
          expected=base*restaurant_item_effect*season*(1+holiday_effect+weekend_effect+.10*promo+weather_effect)
          demand=max(0,int(round(rng.normal(expected,max(2,expected*.16)))))
          rows.append((rid,name,loc,phone,email,f'{rid}_{iid:02d}',item,meal,cat,serv_g,ef,quantity_unit(item),d, dow,weekend,holiday,promo,round(temp,2),round(rain,2),rainy,hot,demand))
    cols=['Restaurant_ID','Restaurant_Name','Location','Phone','Email','Item_ID','Item_Name','Meal_Type','Food_Category','Serving_Mass_g','Emission_Factor_kgCO2e_per_kg','Quantity_Unit','Date','Day_of_Week','Is_Weekend','Holiday','Promotion','Temperature_C','Rainfall_mm','Rainy','Hot','True_Demand_Servings']
    df=pd.DataFrame(rows,columns=cols).sort_values(['Restaurant_ID','Item_ID','Date'])
    g=df.groupby(['Restaurant_ID','Item_ID'])['True_Demand_Servings']
    for lag in [1,7,14,28]: df[f'Lag_{lag}_Demand']=g.shift(lag)
    for w in [7,28]: df[f'Rolling_{w}_Mean_Demand']=g.transform(lambda s:s.shift(1).rolling(w,min_periods=3).mean())
    # Simulated prior preparation is based only on past observed demand, never today's true demand.
    prev=df['Lag_7_Demand'].fillna(df['Rolling_7_Mean_Demand'])
    prev=prev.fillna(df.groupby(['Restaurant_ID','Item_ID'])['True_Demand_Servings'].shift(1))
    prev=prev.fillna(df['True_Demand_Servings'].median())
    df['Historical_Preparation']=np.maximum(0,prev*1.04).round(0)
    df['Observed_Sales']=np.minimum(df['True_Demand_Servings'],df['Historical_Preparation']).astype(int)
    df['Censored_Demand']=(df['Observed_Sales']<df['True_Demand_Servings']).astype(int)
    df['Historical_Waste_Servings']=np.maximum(0,df['Historical_Preparation']-df['True_Demand_Servings'])
    df['Portions_Per_Person']=df['Item_Name'].map(portions_per_person)
    # True_Demand_Servings is the historical piece/unit count. Convert that count
    # to food mass using the mass of one piece only. Portions_Per_Person is used
    # later to convert food mass into people served; multiplying by it here would
    # double-count the pieces and inflate the kg target.
    df['Demand_Target_kg']=df['True_Demand_Servings']*df['Serving_Mass_g']/1000
    return df

if __name__=='__main__':
    out=Path('data'); out.mkdir(exist_ok=True)
    df=generate(); df.to_csv(out/'food_service_research_dataset.csv',index=False)
    pd.DataFrame(RESTAURANTS,columns=['Restaurant_ID','Restaurant_Name','Location','Phone','Email']).to_csv(out/'restaurants.csv',index=False)
    menu=[]
    for rid,items in MENUS.items():
      for j,item in enumerate(items,1):
       meal,cat,g,ef=SPECS[item]; menu.append([rid,f'{rid}_{j:02d}',item,meal,cat,g,ef,quantity_unit(item),portions_per_person(item)])
    pd.DataFrame(menu,columns=['Restaurant_ID','Item_ID','Item_Name','Meal_Type','Food_Category','Serving_Mass_g','Emission_Factor_kgCO2e_per_kg','Quantity_Unit','Portions_Per_Person']).to_csv(out/'menus.csv',index=False)
    print(df.shape, 'rows'); print('restaurants',df.Restaurant_ID.nunique(),'items',df.Item_ID.nunique())

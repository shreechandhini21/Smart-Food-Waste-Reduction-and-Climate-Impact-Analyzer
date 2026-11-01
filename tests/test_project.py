import sys, pathlib, tempfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from src.synthetic_data import generate,RESTAURANTS,MENUS
from src.waste_rules import get_rule
from src.climate import climate_result
from src.optimizer import optimize

def test_unique_restaurant_menus():
 assert len(RESTAURANTS)==12
 assert all(7<=len(MENUS[r[0]])<=10 for r in RESTAURANTS)
 assert len(set(tuple(v) for v in MENUS.values()))>1

def test_synthetic_has_context():
 d=generate(days=100); assert {'Holiday','Temperature_C','Rainfall_mm','Promotion','Observed_Sales'}.issubset(d.columns); assert d.Restaurant_ID.nunique()==12

def test_waste_rules():
 assert 'donat' in get_rule('Vegetarian')[0].lower(); assert 'animal' in get_rule('Meat')[1]

def test_climate_math():
 x=climate_result(10,'organic_processing'); assert x['estimated_avoided_co2e_kg']>0

def test_optimizer():
 x=optimize([10,12,15,20,25],50,20,portion_kg=.2); assert x['preparation_servings']>0

def test_menu_ids_match_history_and_item_demand_varies():
 import pandas as pd
 from src.catalog import menu_for
 from src.predict import predict_existing
 h=pd.read_csv('data/food_service_research_dataset.csv',parse_dates=['Date'])
 mm=menu_for('R001')
 assert set(mm.Item_ID).issubset(set(h.Item_ID))
 vals=[]
 for _,it in mm.iterrows():
  kg,_=predict_existing('R001',it.Item_ID,'2026-10-11',29,5,True,False,h)
  vals.append(round(kg,4))
 assert len(set(vals)) >= 5


def test_quantity_units_and_liquid_portions():
    import pandas as pd
    m=pd.read_csv('data/menus.csv')
    assert set(m.Quantity_Unit.unique()) == {'kg','L'}
    assert (m[m.Item_Name.isin(['Filter Coffee','Coffee','Tea','Sambar','Soup','Lemon Juice','Lassi','Juice','Smoothie'])].Quantity_Unit == 'L').all()
    assert (m[m.Item_Name.isin(['Idli','Dosa','Lemon Rice','Biryani','Veg Meals'])].Quantity_Unit == 'kg').all()
    coffee=m[m.Item_Name=='Filter Coffee'].iloc[0]
    assert float(coffee.Serving_Mass_g)==180

def test_item_serving_mass_is_not_shared_across_all_foods():
    import pandas as pd
    m=pd.read_csv('data/menus.csv')
    assert m.Serving_Mass_g.nunique() >= 8
    assert float(m[m.Item_Name=='Idli'].iloc[0].Serving_Mass_g) != float(m[m.Item_Name=='Biryani'].iloc[0].Serving_Mass_g)


def test_climate_scenario_reconciles_all_numbers():
    from src.climate import climate_scenario
    x = climate_scenario(1.96, 1.09, 'organic_processing', factor=1.0)
    assert round(x['avoided_waste_kg'], 2) == 0.87
    assert round(x['benchmark_landfill_burden_co2e_kg'], 2) == 1.96
    assert round(x['model_landfill_equivalent_burden_co2e_kg'], 2) == 1.09
    assert round(x['model_route_burden_co2e_kg'], 3) == 0.327
    assert round(x['total_avoided_burden_co2e_kg'], 3) == round(1.96 - 0.327, 3)
    assert x['total_avoided_burden_co2e_kg'] >= x['avoided_burden_from_waste_reduction_co2e_kg']


def test_climate_scenario_never_treats_waste_difference_as_new_stream():
    from src.climate import climate_scenario
    x = climate_scenario(1.96, 1.09, 'organic_processing', factor=1.0)
    # The total comparison is benchmark burden minus model-route burden,
    # not climate_result(benchmark - model).
    assert round(x['total_avoided_burden_co2e_kg'], 3) == 1.633


def test_requested_piece_based_portions():
    from src.synthetic_data import portions_per_person
    assert portions_per_person('Idli') == 2.5
    assert portions_per_person('Dosa') == 2.5
    assert portions_per_person('Roti') == 2.5
    assert portions_per_person('Poori') == 3.0
    assert portions_per_person('Burger') == 1.0


def test_piece_mass_is_not_multiplied_by_people_portion_in_target():
    from src.synthetic_data import generate
    df = generate(days=2, start='2024-01-01', seed=42)
    for item, expected_mass in [('Idli', 40), ('Dosa', 80), ('Roti', 45), ('Poori', 50), ('Burger', 220)]:
        x = df[df.Item_Name == item].iloc[0]
        assert round(float(x.Demand_Target_kg), 6) == round(float(x.True_Demand_Servings) * expected_mass / 1000, 6)

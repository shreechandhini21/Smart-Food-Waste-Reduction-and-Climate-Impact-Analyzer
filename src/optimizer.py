import numpy as np


def evaluate_preparation(demand_samples, preparation_servings, shortage_cost=50, overage_cost=20,
                         carbon_price=0, emission_factor=0, portion_kg=0.2, prep_cost=1):
    d = np.asarray(demand_samples, dtype=float)
    q = max(0.0, float(preparation_servings))
    co = overage_cost + carbon_price * emission_factor * portion_kg
    cu = shortage_cost
    waste = np.maximum(q - d, 0)
    shortage = np.maximum(d - q, 0)
    co2 = waste * portion_kg * emission_factor
    cost = overage_cost * waste + shortage_cost * shortage + prep_cost * q + carbon_price * co2
    return {
        'preparation_servings': q,
        'expected_waste_servings': float(waste.mean()),
        'expected_shortage_servings': float(shortage.mean()),
        'expected_waste_kg': float(waste.mean() * portion_kg),
        'expected_shortage_kg': float(shortage.mean() * portion_kg),
        'expected_co2e_kg': float(co2.mean()),
        'expected_cost': float(cost.mean()),
        'critical_fractile': float(np.clip((cu - prep_cost) / (cu + co), .001, .999)),
    }


def optimize(demand_samples, shortage_cost=50, overage_cost=20, carbon_price=0,
             emission_factor=0, portion_kg=0.2, prep_cost=1, min_preparation_servings=None):
    d = np.asarray(demand_samples, dtype=float)
    co = overage_cost + carbon_price * emission_factor * portion_kg
    cu = shortage_cost
    alpha = float(np.clip((cu - prep_cost) / (cu + co), .001, .999))
    q = float(np.quantile(d, alpha, method='higher'))
    if min_preparation_servings is not None:
        q = max(q, float(min_preparation_servings))
    result = evaluate_preparation(
        d, q, shortage_cost=shortage_cost, overage_cost=overage_cost,
        carbon_price=carbon_price, emission_factor=emission_factor,
        portion_kg=portion_kg, prep_cost=prep_cost
    )
    result['critical_fractile'] = alpha
    return result

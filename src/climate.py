"""Climate-impact calculations for the Food Waste Reduction & Climate Impact Analyzer.

All values are scenario estimates.  The project intentionally uses configurable,
illustrative factors until documented locally applicable factors are supplied.
"""

LANDFILL_FACTOR_KG_CO2E_PER_KG = 1.0
ROUTE_FACTORS_KG_CO2E_PER_KG_LANDFILL_BURDEN = {
    'donation': 0.0,
    'composting': 0.25,
    'anaerobic_digestion': 0.20,
    'organic_processing': 0.30,
    'authorised_collection': 0.70,
    'landfill': 1.0,
}

FACTOR_NOTE = (
    'Illustrative disposal/treatment factors used for the synthetic planning scenario. '
    'Replace them with documented, locally applicable factors before publication or '
    'real-world environmental reporting.'
)


def climate_result(
    waste_kg,
    diversion='organic_processing',
    factor=LANDFILL_FACTOR_KG_CO2E_PER_KG,
):
    """Calculate the burden of one waste quantity under a disposal route.

    This function is retained for the Waste Management module.  It does NOT compare
    a benchmark against the model scenario; use ``climate_scenario`` for that.
    """
    waste = float(max(0.0, waste_kg))
    landfill_burden = waste * float(factor)
    route_factor = ROUTE_FACTORS_KG_CO2E_PER_KG_LANDFILL_BURDEN.get(
        diversion, ROUTE_FACTORS_KG_CO2E_PER_KG_LANDFILL_BURDEN['organic_processing']
    )
    route_burden = landfill_burden * route_factor
    avoided_by_diversion = max(0.0, landfill_burden - route_burden)

    # Backward-compatible keys are retained because the existing Waste Management
    # page and tests use them.
    return {
        'waste_kg': waste,
        'baseline_disposal_co2e_kg': landfill_burden,
        'estimated_route_co2e_kg': route_burden,
        'estimated_avoided_co2e_kg': avoided_by_diversion,
        'landfill_burden_co2e_kg': landfill_burden,
        'route_burden_co2e_kg': route_burden,
        'avoided_by_diversion_co2e_kg': avoided_by_diversion,
        'route_factor': route_factor,
        'factor_note': FACTOR_NOTE,
    }


def climate_scenario(
    benchmark_excess_waste_kg,
    expected_waste_kg,
    diversion='organic_processing',
    factor=LANDFILL_FACTOR_KG_CO2E_PER_KG,
):
    """Compare the illustrative benchmark with the model scenario.

    The dashboard's benchmark is explicitly an *excess-preparation scenario*:
    benchmark_excess_waste_kg is the assumed avoidable excess above predicted demand.
    We do not call ``climate_result`` on the difference because that would incorrectly
    treat the difference as a new waste stream.

    Outputs distinguish:
      - food-waste reduction from the benchmark;
      - landfill-equivalent burden avoided from reducing waste;
      - additional route burden/benefit from diversion; and
      - total scenario burden avoided versus the benchmark.
    """
    benchmark_waste = float(max(0.0, benchmark_excess_waste_kg))
    model_waste = float(max(0.0, expected_waste_kg))
    factor = float(factor)

    avoided_waste = max(0.0, benchmark_waste - model_waste)

    # Both scenarios expressed against the same landfill baseline isolates the
    # benefit attributable to producing less waste.
    benchmark_landfill_burden = benchmark_waste * factor
    model_landfill_equivalent_burden = model_waste * factor
    avoided_burden_from_waste_reduction = max(
        0.0,
        benchmark_landfill_burden - model_landfill_equivalent_burden,
    )

    route_factor = ROUTE_FACTORS_KG_CO2E_PER_KG_LANDFILL_BURDEN.get(
        diversion, ROUTE_FACTORS_KG_CO2E_PER_KG_LANDFILL_BURDEN['organic_processing']
    )
    model_route_burden = model_landfill_equivalent_burden * route_factor
    diversion_benefit = max(
        0.0,
        model_landfill_equivalent_burden - model_route_burden,
    )

    # Total difference between the benchmark landfill scenario and the model's
    # selected treatment route.  This combines waste reduction + diversion.
    total_avoided_burden = max(
        0.0,
        benchmark_landfill_burden - model_route_burden,
    )

    return {
        'benchmark_waste_kg': benchmark_waste,
        'expected_waste_kg': model_waste,
        'avoided_waste_kg': avoided_waste,
        'landfill_factor_kgco2e_per_kg': factor,
        'benchmark_landfill_burden_co2e_kg': benchmark_landfill_burden,
        'model_landfill_equivalent_burden_co2e_kg': model_landfill_equivalent_burden,
        'avoided_burden_from_waste_reduction_co2e_kg': avoided_burden_from_waste_reduction,
        'route': diversion,
        'route_factor': route_factor,
        'model_route_burden_co2e_kg': model_route_burden,
        'diversion_benefit_co2e_kg': diversion_benefit,
        'total_avoided_burden_co2e_kg': total_avoided_burden,
        'factor_note': FACTOR_NOTE,
    }

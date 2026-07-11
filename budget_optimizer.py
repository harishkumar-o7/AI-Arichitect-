# --------------------------------------------------------
# Budget Optimizer
# --------------------------------------------------------
# Helps a user figure out what they can build within a given
# budget — by area, by BHK configuration, and by cost tier —
# and suggests ways to fit a desired plan into a tighter budget.
# --------------------------------------------------------

from cost import estimate_cost

COST_RATES = {
    "basic": 2200,
    "standard": 2800,
    "premium": 3500
}

# Typical minimum comfortable built-up area (sqft) for a given BHK
MIN_AREA_FOR_BHK = {
    1: 600,
    2: 900,
    3: 1400,
    4: 1800,
    5: 2200
}

TIPS = {
    "reduce_tier": "Switch from Premium to Standard or Basic finishes to reduce cost per sqft without changing the layout.",
    "reduce_area": "Reduce the built-up area slightly, or move a room (e.g. a study) to a later construction phase.",
    "reduce_bathroom": "Reducing one bathroom typically frees up ~10% of the budget for the remaining rooms.",
    "phase_construction": "Consider phased construction — complete the ground floor first and add upper floors later as budget allows.",
    "negotiate_materials": "Bulk-purchase materials like cement and steel directly to reduce the ~5-10% markup typically added by contractors."
}


def _max_area_for_budget(budget, rate):
    return int(budget // rate)


def _best_bhk_for_area(area):
    best = 0
    for bhk, min_area in sorted(MIN_AREA_FOR_BHK.items()):
        if area >= min_area:
            best = bhk
    return best


def optimize_budget(budget, area=None, bedrooms=None, bathrooms=None):
    budget = max(budget, 1)

    # --------------------------------
    # What can you build, per tier?
    # --------------------------------
    tier_breakdown = {}
    for tier, rate in COST_RATES.items():
        max_area = _max_area_for_budget(budget, rate)
        tier_breakdown[tier] = {
            "rate_per_sqft": rate,
            "max_affordable_area": max_area,
            "max_affordable_bhk": _best_bhk_for_area(max_area)
        }

    suggestions = []
    fits_requested_plan = None
    shortfall = None

    # --------------------------------
    # If user gave a specific area, check feasibility per tier
    # --------------------------------
    if area:
        feasibility = {}
        for tier, rate in COST_RATES.items():
            required_cost = area * rate
            feasibility[tier] = {
                "required_cost": required_cost,
                "fits_budget": required_cost <= budget,
                "difference": budget - required_cost
            }
        fits_requested_plan = feasibility

        # Does the cheapest tier even fit?
        if not feasibility["basic"]["fits_budget"]:
            shortfall = abs(feasibility["basic"]["difference"])
            suggestions.append(
                f"Your budget falls short by approximately Rs. {shortfall:,.0f} "
                f"even at Basic finish for {area} sqft."
            )
            suggestions.append(TIPS["reduce_area"])
            suggestions.append(TIPS["phase_construction"])
        else:
            affordable_tiers = [t for t, f in feasibility.items() if f["fits_budget"]]
            best_tier = affordable_tiers[-1] if affordable_tiers else "basic"
            suggestions.append(
                f"For {area} sqft, your budget comfortably covers the "
                f"'{best_tier}' finish tier."
            )
            if best_tier != "premium" and "premium" not in affordable_tiers:
                suggestions.append(TIPS["reduce_tier"])

    # --------------------------------
    # If user gave bedrooms/bathrooms, check against min recommended area
    # --------------------------------
    if bedrooms:
        min_area = MIN_AREA_FOR_BHK.get(bedrooms, bedrooms * 450)
        for tier, rate in COST_RATES.items():
            cost_for_min_area = min_area * rate
            if cost_for_min_area <= budget:
                suggestions.append(
                    f"A {bedrooms}BHK ({min_area} sqft minimum) is affordable "
                    f"at '{tier}' finish within your budget."
                )
                break
        else:
            suggestions.append(
                f"A {bedrooms}BHK typically needs at least {min_area} sqft, which "
                f"exceeds your budget even at Basic finish. Consider a "
                f"{max(bedrooms - 1, 1)}BHK instead, or increase the budget."
            )
            suggestions.append(TIPS["reduce_bathroom"] if bathrooms else TIPS["reduce_tier"])

    if not suggestions:
        suggestions.append(
            "Provide an area or a BHK preference along with your budget for "
            "more specific recommendations."
        )

    suggestions.append(TIPS["negotiate_materials"])

    return {
        "budget": budget,
        "tier_breakdown": tier_breakdown,
        "requested_plan_feasibility": fits_requested_plan,
        "recommendations": suggestions
    }

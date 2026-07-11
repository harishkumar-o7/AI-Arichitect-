# --------------------------------------------------------
# Material Estimation
# --------------------------------------------------------
# Quantities below are based on common construction thumb-rules
# (per sqft of built-up area). These are approximate planning
# figures, not a substitute for a structural engineer's BOQ.
# --------------------------------------------------------

THUMB_RULES = {
    "cement_bags_per_sqft": 0.4,      # bags
    "steel_kg_per_sqft": 4.0,         # kg
    "bricks_per_sqft": 8,             # units
    "sand_cuft_per_sqft": 1.5,        # cubic feet
    "aggregate_cuft_per_sqft": 1.2,   # cubic feet
    "paint_liters_per_sqft": 0.15,    # liters (interior + exterior combined)
    "tiles_sqft_per_sqft": 0.9,       # sqft of flooring/wall tiles
}

# Approximate unit costs (INR) — used only for a rough material cost split
UNIT_COSTS = {
    "cement": 400,      # per bag
    "steel": 65,         # per kg
    "bricks": 8,          # per brick
    "sand": 60,           # per cu.ft
    "aggregate": 55,      # per cu.ft
    "paint": 250,         # per liter
    "tiles": 80,          # per sqft
}


def estimate_materials(area):
    area = max(area, 1)

    cement_bags = round(area * THUMB_RULES["cement_bags_per_sqft"])
    steel_kg = round(area * THUMB_RULES["steel_kg_per_sqft"])
    bricks = round(area * THUMB_RULES["bricks_per_sqft"])
    sand_cuft = round(area * THUMB_RULES["sand_cuft_per_sqft"])
    aggregate_cuft = round(area * THUMB_RULES["aggregate_cuft_per_sqft"])
    paint_liters = round(area * THUMB_RULES["paint_liters_per_sqft"], 1)
    tiles_sqft = round(area * THUMB_RULES["tiles_sqft_per_sqft"])

    materials = {
        "cement": {"quantity": cement_bags, "unit": "bags"},
        "steel": {"quantity": steel_kg, "unit": "kg"},
        "bricks": {"quantity": bricks, "unit": "units"},
        "sand": {"quantity": sand_cuft, "unit": "cu.ft"},
        "aggregate": {"quantity": aggregate_cuft, "unit": "cu.ft"},
        "paint": {"quantity": paint_liters, "unit": "liters"},
        "tiles": {"quantity": tiles_sqft, "unit": "sqft"},
    }

    estimated_cost = {}
    total_cost = 0

    for material, info in materials.items():
        cost = round(info["quantity"] * UNIT_COSTS[material])
        estimated_cost[material] = cost
        total_cost += cost

    return {
        "area": area,
        "materials": materials,
        "estimated_material_cost": estimated_cost,
        "total_material_cost": total_cost,
        "note": "Quantities are approximate, based on standard thumb-rule "
                 "construction ratios per sqft of built-up area. Actual "
                 "requirements may vary based on design, soil type, and "
                 "structural specifications."
    }

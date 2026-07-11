def allocate_space(area, bedrooms, bathrooms):

    bedrooms = max(bedrooms, 1)
    bathrooms = max(bathrooms, 1)

    living = round(area * 0.30)

    total_bedroom_area = round(area * 0.40)
    bedroom_size = round(total_bedroom_area / bedrooms)

    kitchen = round(area * 0.15)

    total_bathroom_area = round(area * 0.10)
    bathroom_size = round(total_bathroom_area / bathrooms)

    return {
        "living_room": living,
        "bedroom_size": bedroom_size,
        "kitchen": kitchen,
        "bathroom_size": bathroom_size
    }
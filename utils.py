import math

def room_dimensions(area_sqft):

    area_sqft = max(area_sqft, 1)

    width = math.sqrt(area_sqft)
    length = area_sqft / width

    return round(length, 1), round(width, 1)
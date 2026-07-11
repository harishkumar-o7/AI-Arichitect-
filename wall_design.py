def recommend_wall_design(room_type):

    designs = {

        "living room": [
            "Wooden TV Panel",
            "Modern Marble Wall",
            "LED Accent Wall"
        ],

        "bedroom": [
            "Textured Wallpaper",
            "Wooden Headboard Wall",
            "Minimalist Paint Design"
        ],

        "office": [
            "Acoustic Panels",
            "Modern Wooden Finish",
            "Industrial Design"
        ]
    }

    return designs.get(
        room_type.lower(),
        ["Modern Paint Design"]
    )
from PIL import Image, ImageDraw
from utils import room_dimensions
import os


def generate_floorplan(area, bedrooms, bathrooms, rooms):

    os.makedirs("static", exist_ok=True)

    img = Image.new("RGB", (1000, 700), "white")
    draw = ImageDraw.Draw(img)

    # --------------------------------
    # House Category
    # --------------------------------
    if area <= 1000:
        scale = 0.8
        house_type = "SMALL HOUSE"

    elif area <= 2000:
        scale = 1.2
        house_type = "MEDIUM HOUSE"

    else:
        scale = 1.8
        house_type = "LARGE HOUSE"

    # --------------------------------
    # Title
    # --------------------------------
    draw.text(
        (380, 10),
        "AI ARCHITECT - FLOOR PLAN",
        fill="black"
    )

    draw.text(
        (430, 30),
        house_type,
        fill="red"
    )

    # --------------------------------
    # Room Dimensions
    # --------------------------------
    living_l, living_w = room_dimensions(
        rooms["living_room"]
    )

    bed_l, bed_w = room_dimensions(
        rooms["bedroom_size"]
    )

    kitchen_l, kitchen_w = room_dimensions(
        rooms["kitchen"]
    )

    bath_l, bath_w = room_dimensions(
        rooms["bathroom_size"]
    )

    # --------------------------------
    # Outer Boundary
    # --------------------------------
    draw.rectangle(
        (20, 40, 980, 680),
        outline="black",
        width=4
    )

    # --------------------------------
    # Dynamic Sizes
    # --------------------------------
    living_width = int(350 * scale)
    living_height = int(200 * scale)

    bed_width = int(180 * scale)
    bed_height = int(180 * scale)

    kitchen_width = int(220 * scale)
    kitchen_height = int(180 * scale)

    bath_width = int(160 * scale)
    bath_height = int(130 * scale)

    # =================================
    # 2 BHK
    # =================================
    if bedrooms == 2:

        # Living Room
        draw.rectangle(
            (
                50,
                70,
                50 + living_width,
                70 + living_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (70, 90),
            f"Living Room\n{rooms['living_room']} sqft\n{living_l}ft x {living_w}ft",
            fill="black"
        )

        # Bedroom 1
        draw.rectangle(
            (
                50,
                100 + living_height,
                50 + bed_width,
                100 + living_height + bed_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (
                60,
                120 + living_height
            ),
            f"Bedroom 1\n{rooms['bedroom_size']} sqft\n{bed_l}ft x {bed_w}ft",
            fill="black"
        )

        # Bedroom 2
        draw.rectangle(
            (
                70 + bed_width,
                100 + living_height,
                70 + (bed_width * 2),
                100 + living_height + bed_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (
                80 + bed_width,
                120 + living_height
            ),
            f"Bedroom 2\n{rooms['bedroom_size']} sqft\n{bed_l}ft x {bed_w}ft",
            fill="black"
        )

        # Kitchen
        draw.rectangle(
            (
                100 + (bed_width * 2),
                70,
                100 + (bed_width * 2) + kitchen_width,
                70 + kitchen_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (
                120 + (bed_width * 2),
                90
            ),
            f"Kitchen\n{rooms['kitchen']} sqft\n{kitchen_l}ft x {kitchen_w}ft",
            fill="black"
        )

        # Bathroom
        draw.rectangle(
            (
                100 + (bed_width * 2),
                100 + kitchen_height,
                100 + (bed_width * 2) + bath_width,
                100 + kitchen_height + bath_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (
                110 + (bed_width * 2),
                120 + kitchen_height
            ),
            f"Bathroom\n{rooms['bathroom_size']} sqft\n{bath_l}ft x {bath_w}ft",
            fill="black"
        )

        # Large House Extras
        if area > 2000:

            draw.rectangle(
                (650, 250, 900, 450),
                outline="green",
                width=4
            )

            draw.text(
                (720, 330),
                "Dining Room",
                fill="green"
            )

            draw.rectangle(
                (650, 500, 900, 620),
                outline="orange",
                width=4
            )

            draw.text(
                (740, 550),
                "Balcony",
                fill="orange"
            )

    # =================================
    # 3 BHK
    # =================================
    elif bedrooms == 3:

        draw.rectangle(
            (
                50,
                70,
                50 + living_width,
                70 + living_height
            ),
            outline="navy",
            width=4
        )

        draw.text(
            (
                70,
                90
            ),
            f"Living Room\n{rooms['living_room']} sqft"
        )

        bedroom_positions = [
            (50, 300),
            (300, 300),
            (550, 300)
        ]

        for i, (x, y) in enumerate(
            bedroom_positions
        ):

            draw.rectangle(
                (
                    x,
                    y,
                    x + bed_width,
                    y + bed_height
                ),
                outline="navy",
                width=4
            )

            draw.text(
                (
                    x + 10,
                    y + 30
                ),
                f"Bedroom {i+1}"
            )

    else:

        draw.text(
            (
                350,
                350
            ),
            f"{bedrooms} BHK Layout Coming Soon"
        )

    # --------------------------------
    # Window
    # --------------------------------
    draw.line(
        (120, 70, 220, 70),
        fill="blue",
        width=5
    )

    draw.text(
        (120, 45),
        "WINDOW"
    )

    # --------------------------------
    # Main Door
    # --------------------------------
    draw.line(
        (450, 680, 550, 680),
        fill="brown",
        width=6
    )

    draw.text(
        (430, 650),
        "MAIN DOOR"
    )

    # --------------------------------
    # North Direction
    # --------------------------------
    draw.text(
        (900, 60),
        "N"
    )

    draw.line(
        (910, 120, 910, 80),
        fill="black",
        width=3
    )

    # --------------------------------
    # Plot Info
    # --------------------------------
    draw.text(
        (50, 620),
        f"Plot Area : {area} sqft"
    )

    draw.text(
        (250, 620),
        f"{bedrooms} BHK"
    )

    image_path = "static/floor_plan.png"

    img.save(image_path)

    return image_path
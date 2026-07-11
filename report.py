import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="SubTitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=16,
        spaceAfter=8
    ))
    return styles


def _info_table(rows, col_widths=(6 * cm, 6 * cm)):
    table = Table(rows, colWidths=list(col_widths))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f3f6")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#222222")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.white]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def generate_report(plan_data, image_path=None, output_dir="static", filename=None):
    """
    plan_data: dict with keys -
        area, bedrooms, bathrooms, style, layout_type,
        rooms (dict), cost_estimation (dict), vastu (bool), vastu_rules (dict)
    image_path: path to the floor plan PNG (e.g. "static/floor_plan.png")
    Returns the path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)

    if not filename:
        filename = "floor_plan_report.pdf"

    pdf_path = os.path.join(output_dir, filename)
    styles = _styles()
    story = []

    # --------------------------------
    # Header
    # --------------------------------
    story.append(Paragraph("AI Architect", styles["ReportTitle"]))
    story.append(Paragraph(
        f"Floor Plan & Cost Report &nbsp;|&nbsp; Generated on "
        f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        styles["SubTitle"]
    ))

    # --------------------------------
    # Project Summary
    # --------------------------------
    story.append(Paragraph("Project Summary", styles["SectionHeading"]))
    summary_rows = [
        ["Plot Area", f"{plan_data.get('area')} sqft"],
        ["Configuration", f"{plan_data.get('bedrooms')} BHK"],
        ["Bathrooms", f"{plan_data.get('bathrooms')}"],
        ["Style", f"{plan_data.get('style', 'N/A')}"],
        ["Layout Type", f"{plan_data.get('layout_type', 'A')}"],
    ]
    story.append(_info_table(summary_rows))

    # --------------------------------
    # Floor Plan Image
    # --------------------------------
    if image_path and os.path.exists(image_path):
        story.append(Paragraph("Floor Plan", styles["SectionHeading"]))
        story.append(Image(image_path, width=16 * cm, height=11.2 * cm))

    # --------------------------------
    # Room Allocation
    # --------------------------------
    rooms = plan_data.get("rooms", {})
    if rooms:
        story.append(Paragraph("Room Allocation", styles["SectionHeading"]))
        room_rows = [["Room", "Area (sqft)"]]
        labels = {
            "living_room": "Living Room",
            "bedroom_size": "Each Bedroom",
            "kitchen": "Kitchen",
            "bathroom_size": "Each Bathroom"
        }
        for key, value in rooms.items():
            room_rows.append([labels.get(key, key), f"{value} sqft"])
        room_table = Table(room_rows, colWidths=[8 * cm, 8 * cm])
        room_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(room_table)

    # --------------------------------
    # Cost Estimation
    # --------------------------------
    cost = plan_data.get("cost_estimation", {})
    if cost:
        story.append(Paragraph("Cost Estimation", styles["SectionHeading"]))
        cost_rows = [["Package", "Estimated Cost (Rs.)"]]
        for tier, amount in cost.items():
            cost_rows.append([tier.capitalize(), f"Rs. {amount:,.0f}"])
        cost_table = Table(cost_rows, colWidths=[8 * cm, 8 * cm])
        cost_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(cost_table)

    # --------------------------------
    # Material Estimation
    # --------------------------------
    material_data = plan_data.get("material_estimation")
    if material_data:
        story.append(Paragraph("Material Estimation", styles["SectionHeading"]))
        mat_rows = [["Material", "Quantity", "Est. Cost (Rs.)"]]
        materials = material_data.get("materials", {})
        costs = material_data.get("estimated_material_cost", {})
        for mat, info in materials.items():
            mat_rows.append([
                mat.capitalize(),
                f"{info['quantity']} {info['unit']}",
                f"Rs. {costs.get(mat, 0):,.0f}"
            ])
        mat_rows.append([
            "Total", "", f"Rs. {material_data.get('total_material_cost', 0):,.0f}"
        ])
        mat_table = Table(mat_rows, colWidths=[6 * cm, 5 * cm, 5 * cm])
        mat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5f2c82")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f3f6")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f8f9fb")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(mat_table)
        story.append(Paragraph(material_data.get("note", ""), styles["SubTitle"]))

    # --------------------------------
    # Vastu Recommendations
    # --------------------------------
    if plan_data.get("vastu") and plan_data.get("vastu_rules"):
        story.append(Paragraph("Vastu Recommendations", styles["SectionHeading"]))
        vastu_rows = [["Element", "Recommended Direction"]]
        for element, direction in plan_data["vastu_rules"].items():
            vastu_rows.append([element.replace("_", " ").title(), direction])
        vastu_table = _info_table(vastu_rows, col_widths=(8 * cm, 8 * cm))
        story.append(vastu_table)

    # --------------------------------
    # Footer note
    # --------------------------------
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "This report is auto-generated by AI Architect and is intended for "
        "preliminary planning purposes only. Please consult a certified architect "
        "or structural engineer before construction.",
        styles["SubTitle"]
    ))

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )
    doc.build(story)

    return pdf_path

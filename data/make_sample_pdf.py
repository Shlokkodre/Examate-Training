"""
Day 11 — Generate a realistic sample FSSAI labelling regulation PDF.

The PDF mimics the structure of the real FSSAI Labelling and Display
Compendium so that app/pdf_parser.py has a real file to parse.

Run from repo root:
    python data/make_sample_pdf.py
Output: data/raw/FSSAI_Sample_Labelling.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_PATH = "data/raw/FSSAI_Sample_Labelling.pdf"

REGULATIONS = [
    ("5.1", "Name of Food",
     "All packaged foods",
     "The name of the food shall be the name prescribed in the relevant "
     "food safety regulations or standard. If no name is prescribed, a common "
     "or generic name shall be used that is not misleading to the consumer.",
     "None"),
    ("5.2", "List of Ingredients",
     "All packaged foods",
     "A complete list of ingredients shall be declared in descending order of "
     "their composition by weight or volume at the time of manufacture. "
     "Ingredients constituting less than 5 percent may be listed in any order "
     "after the other ingredients.",
     "Single ingredient foods, fresh fruits and vegetables"),
    ("5.3", "Nutritional Information",
     "All packaged foods with principal display panel > 100 cm²",
     "Mandatory nutritional information per 100 g or 100 ml and per serving: "
     "Energy (kcal), Protein (g), Carbohydrate (g) of which Total Sugars (g), "
     "Fat (g) of which Saturated Fat (g) and Trans Fat (g), and Sodium (mg).",
     "Small packages with principal display panel area less than 100 cm², "
     "spices, salt, tea, coffee"),
    ("5.4", "Declaration of Allergens",
     "Foods containing common allergens",
     "If the product contains any of the following, they must be declared: "
     "Cereals containing gluten (wheat, rye, barley, oats), Crustaceans, Eggs, "
     "Fish, Peanuts, Soybeans, Milk, Tree nuts, Sulphite at or above 10 mg/kg. "
     "Declaration format: 'Contains: [allergen name]'.",
     "None for products containing listed allergens"),
    ("5.5", "Name and Complete Address of Manufacturer",
     "All packaged foods",
     "Complete name and address of the manufacturer, packer, or bottler "
     "including street name or number, city, state, pin code, and country. "
     "For imported products, the name and address of the importer shall also "
     "be declared.",
     "None"),
    ("5.6", "Net Quantity",
     "All packaged foods",
     "Net quantity shall be declared in terms of weight, volume, or number "
     "as appropriate. Metric system units (g, kg, ml, l) shall be used. "
     "The declaration shall be distinct and in a conspicuous location.",
     "None"),
    ("5.7", "Date of Manufacture and Best Before / Use By Date",
     "All packaged foods",
     "Both manufacturing or packing date and Best Before date or Use By date "
     "must be declared. Acceptable formats include DD/MM/YYYY, MM/YYYY, or "
     "Month YYYY. The words 'Best Before' or 'Use By' must precede the date.",
     "None"),
    ("5.8", "FSSAI License or Registration Number",
     "All packaged foods",
     "The FSSAI license number or registration number issued by the Food Safety "
     "and Standards Authority of India must be prominently displayed along with "
     "the FSSAI logo. Format: 'FSSAI Lic. No.: XXXXXXXXXXXXXXXXXXX'.",
     "None"),
    ("5.9", "Country of Origin",
     "Imported packaged foods",
     "For every imported packaged food, the country of origin of the food must "
     "be declared. Where the food undergoes processing in a second country which "
     "changes its nature, the country where the processing is performed shall be "
     "considered to be the country of origin.",
     "Domestically manufactured products"),
    ("5.10", "Veg / Non-Veg Symbol",
     "All packaged foods",
     "A green coloured filled circle inside a square border indicates the food "
     "is vegetarian. A brown coloured filled circle inside a square border "
     "indicates the food is non-vegetarian. The symbol shall have a minimum "
     "diameter of 3 mm and shall be displayed prominently on the principal "
     "display panel.",
     "None"),
    ("5.11", "Instructions for Use",
     "Foods requiring preparation or special storage conditions",
     "Adequate instructions for use, including reconstitution, thawing, or "
     "other pre-treatment as necessary, shall be included as required. Storage "
     "conditions and temperature requirements must be stated if shelf life "
     "depends on them.",
     "Ready-to-eat products that do not require preparation instructions"),
    ("5.12", "Food Additive Declaration",
     "Foods containing permitted food additives",
     "All food additives used in the product shall be declared by their "
     "functional class name followed by the specific name or the INS number. "
     "Example: Preservative (INS 211), Antioxidant (INS 300), "
     "Colour (INS 110 — Sunset Yellow FCF).",
     "Foods containing no additives"),
    ("6.1", "Minimum Font Size on Principal Display Panel",
     "All packaged foods",
     "The minimum letter height for mandatory declarations on the principal "
     "display panel is specified in Table I based on panel area: "
     "less than 40 cm² requires 1.0 mm; "
     "40 to 170 cm² requires 1.5 mm; "
     "170 to 650 cm² requires 2.0 mm; "
     "greater than 650 cm² requires 3.0 mm minimum letter height.",
     "None"),
    ("6.2", "Legibility and Contrast",
     "All packaged foods",
     "All mandatory information shall be displayed in a colour that provides "
     "sharp contrast to the background colour of the label. All mandatory "
     "declarations shall be clearly legible, prominent, and indelible so that "
     "they can be read easily under customary conditions of purchase and use.",
     "None"),
]


def build_pdf(output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=16, alignment=TA_CENTER, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, alignment=TA_CENTER, spaceAfter=20, textColor=colors.grey
    )
    reg_heading = ParagraphStyle(
        "RegHeading", parent=styles["Heading2"],
        fontSize=12, spaceBefore=14, spaceAfter=4,
        textColor=colors.HexColor("#1a5276")
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=9, textColor=colors.grey, spaceAfter=1
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, spaceAfter=4, leading=14
    )

    story = []

    # Cover
    story.append(Paragraph("Food Safety and Standards Authority of India", title_style))
    story.append(Paragraph(
        "Labelling and Display Regulations — Sample Compendium", subtitle_style
    ))
    story.append(Paragraph(
        "FSSAI Regulations 5.1 – 6.2 &nbsp;|&nbsp; For Training Use", subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.5 * cm))

    # Regulation entries
    for reg_no, requirement, applies_to, details, exemption in REGULATIONS:
        story.append(Paragraph(f"Regulation {reg_no} — {requirement}", reg_heading))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 0.15 * cm))

        story.append(Paragraph("Applies to:", label_style))
        story.append(Paragraph(applies_to, body_style))

        story.append(Paragraph("Requirements:", label_style))
        story.append(Paragraph(details, body_style))

        if exemption and exemption.lower() != "none":
            story.append(Paragraph("Exemption:", label_style))
            story.append(Paragraph(exemption, body_style))

        story.append(Spacer(1, 0.3 * cm))

    # Font size table (Regulation 6.1 Table I)
    story.append(Paragraph("Table I — Minimum Font Size (Regulation 6.1)", reg_heading))
    table_data = [
        ["Principal Display Panel Area", "Minimum Letter Height"],
        ["Less than 40 cm²", "1.0 mm"],
        ["40 cm² to 170 cm²", "1.5 mm"],
        ["170 cm² to 650 cm²", "2.0 mm"],
        ["Greater than 650 cm²", "3.0 mm"],
    ]
    t = Table(table_data, colWidths=[10 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eaf4fb")]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN",      (1, 0), (1, -1), "CENTER"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "This document is a sample generated for training purposes. "
        "Always refer to the official FSSAI Gazette notification for authoritative text.",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"PDF created: {output_path}  ({size_kb:.1f} KB,  {len(REGULATIONS)} regulations)")


if __name__ == "__main__":
    build_pdf(OUTPUT_PATH)

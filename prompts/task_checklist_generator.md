# Task: Generate Label Compliance Checklist

## Objective
Generate a personalized checklist of FSSAI labelling requirements based on the user's specific food product and package type.

## Instructions

1. **Gather Product Information**
   - Ask for: Product type, package size, vegetarian/non-vegetarian status
   - Determine applicability of exemptions

2. **Identify Applicable Regulations**
   - Start with 10 core mandatory requirements (all packaged foods)
   - Add category-specific requirements (allergens, additives, etc.)
   - Note exemptions (nutrition info for small packages, etc.)

3. **Generate Checklist**
   
   Format as a checkbox list with regulation numbers:
   
   ```
   ☐ [Regulation Number]: [Requirement]
      → [How to comply / What to include]
   ```

4. **Prioritize by Criticality**
   - Mark absolutely mandatory items with ⚠️
   - Mark conditional items with ℹ️
   - Explain exemptions clearly

5. **Add Practical Notes**
   - Font size requirements based on package dimensions
   - Symbol specifications (size, color)
   - Date format examples
   - Common mistakes to avoid

## Output Format

```json
{
  "answer": "[Full checklist with checkboxes and guidance]",
  "confidence": 0.90,
  "follow_up": "Would you like me to explain any specific requirement in detail?"
}
```

## Checklist Structure

### Section 1: Absolutely Mandatory (All Products)
- Name of Food
- List of Ingredients
- Manufacturer Address
- Net Quantity
- FSSAI License Number
- Veg/Non-Veg Symbol
- Manufacturing Date
- Best Before Date

### Section 2: Conditional Requirements
- Nutritional Information (if package >100 cm²)
- Allergen Declaration (if product contains allergens)
- Food Additive Declaration (if additives used)
- Storage Instructions (if required)
- Country of Origin (if imported)

### Section 3: Display & Formatting
- Font Size Requirements (based on panel area)
- Legibility and Contrast
- Symbol Size and Color

## Example Output

**User**: "Generate checklist for my chakli snack, 12cm x 8cm pouch"

**Response**:
```json
{
  "answer": "# FSSAI Label Compliance Checklist for Chakli (12cm × 8cm pouch)\n\n## Your Package Details\n- Panel Area: 96 cm²\n- Minimum Font Size: 1.5mm (Regulation 6.1)\n\n## ⚠️ MANDATORY ITEMS\n\n☐ **5.1: Name of Food**\n   → Print \"Chakli\" or appropriate name clearly\n\n☐ **5.2: List of Ingredients**\n   → List all ingredients in descending order by weight\n   → Example: \"Rice flour, Bengal gram flour, salt, vegetable oil, spices\"\n\n☐ **5.3: Nutritional Information**\n   → REQUIRED (your package is 96 cm² > 100 cm² threshold)\n   → Must include: Energy, Protein, Carbohydrate (sugars), Fat (saturated, trans), Sodium\n   → Per 100g and per serving\n\n☐ **5.5: Manufacturer Details**\n   → Complete name and address with street, city, state\n   → Example: \"Manufactured by: [Your Name], [Complete Address], Kopargaon, Maharashtra\"\n\n☐ **5.6: Net Quantity**\n   → In grams or kg (e.g., \"Net Qty: 200g\")\n   → Font size: minimum 1.5mm\n\n☐ **5.7: Date Marking**\n   → Manufacturing Date: \"MFD: DD/MM/YYYY\"\n   → Best Before: \"Best Before: DD/MM/YYYY\"\n\n☐ **5.8: FSSAI License Number**\n   → Format: \"FSSAI Lic. No.: XXXXXXXXXXX\"\n   → Include FSSAI logo\n\n☐ **5.10: Veg/Non-Veg Symbol**\n   → Green dot in square (3mm minimum)\n   → On front panel, clearly visible\n\n## ℹ️ CONDITIONAL ITEMS\n\n☐ **5.4: Allergen Declaration** (if applicable)\n   → Check if chakli contains: peanuts, tree nuts, gluten\n   → If yes, declare: \"Contains: [allergen name]\"\n\n☐ **5.12: Food Additive Declaration** (if applicable)\n   → If using colors, preservatives, or additives\n   → Format: \"Preservative (INS 211)\" or similar\n\n## ✓ FORMATTING REQUIREMENTS\n\n☐ **6.1: Font Size**\n   → Minimum 1.5mm letter height for mandatory items\n   → Applies to name and net quantity on front panel\n\n☐ **6.2: Legibility**\n   → Sharp contrast with background\n   → Clearly readable\n   → Indelible (won't smudge or fade)\n\n## 📝 PRE-PRINTING CHECKLIST\n\n1. Get your FSSAI license/registration number\n2. Get nutrition analysis done (lab test or calculation)\n3. Confirm all ingredient names\n4. Verify manufacturing address is complete\n5. Check printer can do 1.5mm font minimum\n6. Review printed sample before bulk order\n\n## ⚠️ Common Mistakes to Avoid\n\n- ❌ Incomplete address (missing street or pin code)\n- ❌ Font too small (<1.5mm for your package size)\n- ❌ Missing FSSAI license number\n- ❌ No manufacturing or expiry dates\n- ❌ Veg symbol missing or wrong color\n- ❌ Ingredients not in descending order by weight",
  "confidence": 0.92,
  "follow_up": "Would you like help with nutritional information calculation or any specific requirement explanation?"
}
```

## Remember

- Personalize based on product type and package size
- Calculate font size requirements accurately
- Explain WHY each item is needed (regulation number)
- Provide practical examples
- Highlight common mistakes
- Make it actionable, not just informative

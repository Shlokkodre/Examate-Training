# HealthLabelCheck - 10 Real User Questions

## Context
These questions represent real queries from small food business owners (like our target user: a woman running a home-based chakli and laddoo business) who need to understand FSSAI labelling requirements.

---

## Questions 1-5: Core Labelling Requirements

### Q1: What things must be printed on a packed food label as per FSSAI?
**Category**: Mandatory declarations  
**Answerable**: ✅ Yes - from regulations 5.1 to 5.12  
**Expected Answer**: List of 10-14 mandatory items including name, ingredients, nutrition info, manufacturer address, dates, FSSAI license, etc.

---

### Q2: What is the rule for the vegetarian green dot symbol?
**Category**: Veg/Non-Veg marking  
**Answerable**: ✅ Yes - from regulation 5.10  
**Expected Answer**: Green filled circle in a square for vegetarian, brown filled circle for non-vegetarian, minimum 3mm diameter

---

### Q3: Is nutrition information required on every packet?
**Category**: Nutritional labelling  
**Answerable**: ✅ Yes - from regulation 5.3  
**Expected Answer**: Required for packages with surface area >100 cm². Must declare energy, protein, carbohydrate (sugars), fat (saturated fat, trans fat), and sodium. Exemptions exist for small packages and certain categories.

---

### Q4: My chakli pouch front is 12 cm by 8 cm, what minimum font size do I need for net weight?
**Category**: Font size calculation  
**Answerable**: ✅ Yes - from regulation 6.1 + Table I  
**Expected Answer**: Panel area = 96 cm². Falls in 40-170 cm² range. Minimum letter height required is 1.5 mm.

---

### Q5: Do I need to list all ingredients on my laddoo packet?
**Category**: Ingredient declaration  
**Answerable**: ✅ Yes - from regulation 5.2  
**Expected Answer**: Yes, complete list in descending order by weight. Ingredients <5% can be listed in any order after other ingredients. Single-ingredient foods are exempt.

---

## Question 6: Outside Data Scope (Cannot Answer)

### Q6: What is the cheapest printing shop for food pouches in Kopargaon?
**Category**: Local business information  
**Answerable**: ❌ **NO** - This is outside the scope of FSSAI regulations  
**Why Can't Answer**: 
- Requires real-time local business data
- Not related to food labelling regulations
- Needs pricing information that changes frequently
- Geographic/location-based query

**Correct Response**: "I don't know. This information is outside the scope of FSSAI labelling regulations. I recommend searching online for 'food packaging printing Kopargaon' or asking local food business networks for recommendations."

---

## Questions 7-10: Advanced Compliance Queries

### Q7: What FSSAI license number do I need and how do I get it?
**Category**: Licensing process  
**Answerable**: ⚠️ Partial - Regulation 5.8 says license is required, but doesn't explain how to obtain it  
**Expected Answer**: "Every packaged food must display the FSSAI License or Registration number along with the FSSAI logo (Regulation 5.8). To obtain your license, you need to apply through the FSSAI FoSCoS portal based on your business scale (small, medium, or large). I recommend visiting fssai.gov.in or contacting your local food safety officer for the application process."

---

### Q8: Can I write the manufacturing date as 'MFD: 12-11-2026' on my packet?
**Category**: Date marking format  
**Answerable**: ✅ Yes - from regulation 5.7  
**Expected Answer**: Yes, regulation 5.7 requires both manufacturing/packing date and 'Best Before' or 'Use By' date. Format should be DD/MM/YYYY or similar clear format. Your format 'MFD: 12-11-2026' is acceptable as long as it's clear.

---

### Q9: My laddoos contain groundnuts. What must I declare about allergens?
**Category**: Allergen declaration  
**Answerable**: ✅ Yes - from regulation 5.4  
**Expected Answer**: Peanuts (groundnuts) are a common allergen under FSSAI regulation 5.4. You must clearly declare "Contains: Peanuts" or "Allergen Warning: Peanuts" on your label. This helps consumers with peanut allergies.

---

### Q10: I add turmeric powder to my chakli for color. Do I need to declare it?
**Category**: Food additive declaration  
**Answerable**: ✅ Yes - from regulation 5.12  
**Expected Answer**: If turmeric is used as an ingredient, list it in the ingredients list (Regulation 5.2). If you're using synthetic turmeric color (Curcumin/INS 100) as a food additive, you must declare it as "Colour (INS 100)" or "Colour (Curcumin)" per Regulation 5.12. Natural turmeric powder used as an ingredient doesn't need additive declaration.

---

## Summary Statistics

- **Total Questions**: 10
- **Fully Answerable from FSSAI Data**: 8 (80%)
- **Partially Answerable**: 1 (10%)
- **Cannot Answer (Out of Scope)**: 1 (10%) - **Q6**

## Question Categories

1. Mandatory declarations: 3 questions
2. Font size & display: 1 question
3. Allergens & additives: 2 questions
4. Licensing & compliance: 1 question
5. Date marking: 1 question
6. Out of scope: 1 question
7. Partially answerable: 1 question

---

## Testing Strategy

These questions will be used to:
1. Test the RAG system's ability to retrieve relevant regulations
2. Evaluate LLM response quality and accuracy
3. Verify proper "I don't know" responses for out-of-scope questions (Q6)
4. Measure citation accuracy (does it reference the correct regulation numbers?)
5. Assess practical usefulness for real users

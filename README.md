# LabelCheck

## Project Card

- **Product:** LabelCheck — a beginner-friendly food-label checking assistant that helps people understand packaged food labels before buying.
- **Target user:** Indian consumers, students, and families who want to make more informed packaged-food choices.
- **Problem:** Food packaging can be difficult to interpret. Nutrition values, ingredients, allergens, and marketing claims may be confusing, making it hard to compare products quickly.
- **Proposed data source:** [Open Food Facts](https://world.openfoodfacts.org/) product database/API. FSSAI resources can be used as a reference for Indian food-safety and labelling guidance.

## Day 01 scope

This first version is a command-line learning prototype. It does not fetch live product data or provide medical advice.

- `day01_intro.py` prints this project card using variables and f-strings, then asks for the user's name and question.
- `day01_menu.py` displays a repeatable menu using a `while` loop, shows sample questions, and demonstrates one simple label rule.

## Run the scripts

```bash
python day01_intro.py
python day01_menu.py
```

## Example rule

The menu includes a simple sugar-value demonstration:
- Below 5 g per 100 g: lower-sugar example
- From 5 g through 22.5 g per 100 g: moderate-sugar example
- Above 22.5 g per 100 g: high-sugar example

These are illustrative learning thresholds, not an official FSSAI classification or a health recommendation. Always check the full label and applicable official guidance.

## Future improvements

1. Fetch product details from Open Food Facts.
2. Add ingredient and allergen highlighting.
3. Compare two products side by side.
4. Add clearer explanations of nutrition information and label terminology.

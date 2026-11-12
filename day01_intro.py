
product = "HealthLabelCheck"
target_user = "Small food business owners (home-based chakli and laddoo makers)"
problem = "Don't know what mandatory declarations must be printed on food packet labels per FSSAI regulations"
data_source = "FSSAI Labelling and Display Regulations (PDF)"
purpose = "Check packet labels against FSSAI regulations and list what is missing"

print("=" * 70)
print(f"{product:^70}")
print("=" * 70)
print(f"Product     : {product}")
print(f"User        : {target_user}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print(f"Purpose     : {purpose}")
print("=" * 70)

user_name = input("\nWhat is your name? ").strip()
if not user_name:
    user_name = "Guest"

user_question = input(f"Hi {user_name}! What is your question about food label regulations? ").strip()
if not user_question:
    user_question = "No question entered."

print(f"\nThanks, {user_name}!")
print(f"Your question: {user_question}")
print("HealthLabelCheck Day 01 introduction completed.")



product = "LabelCheck"
target_user = "Indian consumers, students, and families"
problem = "Packaged-food labels can be confusing and difficult to compare."
data_source = "Open Food Facts (proposed database/API)"
purpose = "Help users understand ingredients and nutrition information."

print("=" * 55)
print(f"{product:^55}")
print("=" * 55)
print(f"Product     : {product}")
print(f"User        : {target_user}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print(f"Purpose     : {purpose}")
print("=" * 55)

user_name = input("\nWhat is your name? ").strip()
if not user_name:
    user_name = "Guest"

user_question = input(f"Hi {user_name}! What is your question about food labels? ").strip()
if not user_question:
    user_question = "No question entered."

print(f"\nThanks, {user_name}!")
print(f"Your question: {user_question}")
print("LabelCheck Day 01 introduction completed.")


product = "LabelCheck"
target_users = "Indian consumers, students, and families"
data_source = "Open Food Facts"
menu_title = "LABELCHECK MENU"
separator = "=" * 55

print(f"Welcome to {product}!")

while True:
    print(f"\n{separator}")
    print(f"{menu_title:^55}")
    print(separator)
    print("1. About LabelCheck")
    print("2. Sample questions")
    print("3. Check a sample sugar value")
    print("0. Exit")
    print(separator)

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        print(f"\n{product} helps people understand packaged-food labels.")
        print(f"Target users: {target_users}.")
        print(f"Proposed data source: {data_source}.")

    elif choice == "2":
        print("\nSample questions:")
        print("- How much sugar does this product contain?")
        print("- Does this product list common allergens?")
        print("- What do the ingredients mean?")
        print("- How can I compare two packaged products?")

    elif choice == "3":
        try:
            sugar = float(input("Enter sugar in grams per 100 g: "))

            if sugar < 0:
                print("Sugar value cannot be negative.")
            elif sugar < 5:
                print("Demo result: lower-sugar example.")
            elif sugar <= 22.5:
                print("Demo result: moderate-sugar example.")
            else:
                print("Demo result: high-sugar example.")

            print("Note: These are illustrative coding thresholds,")
            print("not an official FSSAI classification or health advice.")

        except ValueError:
            print("Please enter a valid number, such as 4.5.")

    elif choice == "0":
        print(f"Thank you for trying {product}. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, 3, or 0.")

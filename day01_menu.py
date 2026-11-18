 
product = "HealthLabelCheck"
target_users = "Small food business owners, home-based snack makers"
data_source = "FSSAI Labelling and Display Regulations"
menu_title = "HEALTHLABELCHECK MENU"
separator = "=" * 70

print(f"Welcome to {product}!")

while True:
    print(f"\n{separator}")
    print(f"{menu_title:^70}")
    print(separator)
    print("1. About HealthLabelCheck")
    print("2. Sample questions")
    print("3. Check if nutrition information is required (simple rule)")
    print("0. Exit")
    print(separator)

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        print(f"\n{product} helps small food makers check their packet labels")
        print(f"against FSSAI regulations before printing.")
        print(f"Target users: {target_users}.")
        print(f"Data source: {data_source}.")

    elif choice == "2":
        print("\nSample questions:")
        print("- What things must be printed on a packed food label as per FSSAI?")
        print("- What is the rule for the vegetarian green dot symbol?")
        print("- Is nutrition information required on every packet?")
        print("- My chakli pouch front is 12 cm by 8 cm, what minimum font size")
        print("  do I need for net weight?")
        print("- Which labelling rules changed in the 2021 amendment?")

    elif choice == "3":
        print("\nSimple check: Is nutrition information required?")
        print("According to FSSAI Regulation 2.2:")
        
        try:
            package_size = float(input("Enter package size in cm² (length × width): "))
            
            if package_size < 0:
                print("Package size cannot be negative.")
            elif package_size < 100:
                print("✓ Small package (<100 cm²): Nutrition info may be exempted")
                print("  (check specific product category exemptions)")
            else:
                print("✗ Package ≥100 cm²: Nutrition information IS REQUIRED")
                print("  Must include: Energy, Protein, Carbohydrate, Total Sugars,")
                print("  Total Fat, Saturated Fat, Trans Fat, and Sodium")
            
            print("\nNote: This is a simplified rule for learning.")
            print("Always verify with complete FSSAI regulations.")
            
        except ValueError:
            print("Please enter a valid number, such as 96 or 120.")

    elif choice == "0":
        print(f"Thank you for using {product}. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, 3, or 0.")


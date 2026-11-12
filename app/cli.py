"""
CLI interface for HealthLabelCheck
Command-line menu for interacting with FSSAI regulation records
"""

from app.records import (
    load_records, search, count_by, get_by_id, 
    get_mandatory_checklist, filter_by_category
)


def print_separator():
    """Print a visual separator line"""
    print("=" * 70)


def display_record(record):
    """Display a single record in a formatted way"""
    print(f"\nRegulation: {record['regulation_no']}")
    print(f"Requirement: {record['requirement']}")
    print(f"Applies to: {record['applies_to']}")
    print(f"Details: {record['details']}")
    print(f"Exemption: {record['exemption']}")


def display_menu():
    """Display the main menu"""
    print_separator()
    print("HEALTHLABELCHECK - FSSAI Regulation Checker".center(70))
    print_separator()
    print("1. View all regulations")
    print("2. Search by keyword")
    print("3. Get regulation by number")
    print("4. View mandatory checklist")
    print("5. Count regulations by category")
    print("6. Calculate minimum font size")
    print("0. Exit")
    print_separator()


def calculate_font_size():
    """Calculate minimum font size based on principal display panel area"""
    print("\n=== Minimum Font Size Calculator (Regulation 6.1) ===")
    try:
        length = float(input("Enter panel length in cm: "))
        width = float(input("Enter panel width in cm: "))
        area = length * width
        
        print(f"\nPrincipal Display Panel Area: {area:.2f} cm²")
        
        # Font size table from FSSAI Regulation 6.1
        if area < 40:
            min_height = 1.0
        elif area < 170:
            min_height = 1.5
        elif area < 650:
            min_height = 2.0
        else:
            min_height = 3.0
        
        print(f"Minimum letter height required: {min_height} mm")
        print(f"\nThis applies to:")
        print("- Name of food")
        print("- Net quantity")
        print("- Other mandatory declarations on principal display panel")
        
    except ValueError:
        print("Invalid input. Please enter numeric values.")


def run_cli():
    """Main CLI loop"""
    print("\nWelcome to HealthLabelCheck!")
    print("FSSAI Food Labelling Regulation Checker")
    
    # Load records at startup
    records = load_records()
    
    if not records:
        print("\nError: Could not load regulation records.")
        print("Make sure data/sample_records.py exists.")
        return
    
    print(f"Loaded {len(records)} FSSAI regulations.\n")
    
    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            print("\n=== All FSSAI Labelling Regulations ===")
            for i, record in enumerate(records, 1):
                print(f"\n--- {i}. {record['regulation_no']} ---")
                print(f"Requirement: {record['requirement']}")
                print(f"Applies to: {record['applies_to']}")
                print(f"Details: {record['details'][:100]}...")
        
        elif choice == "2":
            keyword = input("\nEnter search keyword: ").strip()
            results = search(records, keyword)
            print(f"\nFound {len(results)} matching regulations:")
            for r in results:
                display_record(r)
        
        elif choice == "3":
            reg_no = input("\nEnter regulation number (e.g., 5.3): ").strip()
            record = get_by_id(records, reg_no)
            if record:
                display_record(record)
            else:
                print(f"Regulation {reg_no} not found.")
        
        elif choice == "4":
            checklist = get_mandatory_checklist(records)
            print("\n=== Mandatory Label Requirements Checklist ===")
            print(f"Total mandatory items: {len(checklist)}\n")
            for item in checklist:
                print(f"☐ {item['regulation_no']}: {item['requirement']}")
                if item['exemption'] != "None":
                    print(f"   Exemption: {item['exemption']}")
        
        elif choice == "5":
            print("\nCommon categories:")
            print("- All packaged foods")
            print("- Foods containing allergens")
            print("- Imported foods")
            category = input("Enter category: ").strip()
            count = count_by(records, 'applies_to', category)
            print(f"\nFound {count} regulations for '{category}'")
            
            # Show the records
            filtered = filter_by_category(records, category)
            for r in filtered:
                print(f"- {r['regulation_no']}: {r['requirement']}")
        
        elif choice == "6":
            calculate_font_size()
        
        elif choice == "0":
            print("\nThank you for using HealthLabelCheck!")
            print("Remember: Always verify with FSSAI before printing labels.")
            break
        
        else:
            print("\nInvalid choice. Please enter a valid option (0-6).")


if __name__ == "__main__":
    run_cli()

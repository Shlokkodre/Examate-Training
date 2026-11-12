"""
Records module for HealthLabelCheck
Handles loading, searching, and managing FSSAI regulation records
"""

import json
import os


def load_records(file_path='data/sample_records.py'):
    """
    Load records from sample_records.py or records.json
    Returns list of regulation dictionaries
    """
    # Try to import from sample_records.py first
    if file_path.endswith('.py'):
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from data.sample_records import SAMPLE_RECORDS
            return SAMPLE_RECORDS
        except ImportError:
            print(f"Could not import from {file_path}")
            return []
    
    # Try to load from JSON
    elif file_path.endswith('.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Invalid JSON in {file_path}")
            return []
    
    return []


def search(records, keyword):
    """
    Search records by keyword in requirement, details, or regulation_no
    Returns list of matching records
    """
    keyword_lower = keyword.lower()
    results = []
    
    for record in records:
        # Search in multiple fields
        if (keyword_lower in record.get('requirement', '').lower() or
            keyword_lower in record.get('details', '').lower() or
            keyword_lower in record.get('regulation_no', '').lower() or
            keyword_lower in record.get('applies_to', '').lower()):
            results.append(record)
    
    return results


def count_by(records, field, value):
    """
    Count records where field contains value
    Example: count_by(records, 'applies_to', 'All packaged foods')
    """
    count = 0
    value_lower = value.lower()
    
    for record in records:
        field_value = record.get(field, '')
        if value_lower in field_value.lower():
            count += 1
    
    return count


def get_by_id(records, regulation_no):
    """
    Get a specific record by regulation number
    Returns record dict or None if not found
    """
    for record in records:
        if record.get('regulation_no') == regulation_no:
            return record
    return None


def get_mandatory_checklist(records):
    """
    Get all mandatory requirements as a checklist
    Returns list of (regulation_no, requirement) tuples
    """
    checklist = []
    for record in records:
        applies_to = record.get('applies_to', '').lower()
        exemption = record.get('exemption', '').lower()
        
        # Include if it applies to all packaged foods and has no general exemption
        if 'all packaged foods' in applies_to:
            checklist.append({
                'regulation_no': record.get('regulation_no'),
                'requirement': record.get('requirement'),
                'exemption': record.get('exemption')
            })
    
    return checklist


def filter_by_category(records, category):
    """
    Filter records by applies_to category
    Returns list of matching records
    """
    category_lower = category.lower()
    results = []
    
    for record in records:
        if category_lower in record.get('applies_to', '').lower():
            results.append(record)
    
    return results


if __name__ == "__main__":
    # Test the module
    print("=== Testing records.py module ===\n")
    
    records = load_records()
    print(f"Loaded {len(records)} records")
    
    print("\n=== Search for 'FSSAI License' ===")
    results = search(records, "FSSAI License")
    for r in results:
        print(f"- {r['regulation_no']}: {r['requirement']}")
    
    print("\n=== Count by 'All packaged foods' ===")
    count = count_by(records, 'applies_to', 'All packaged foods')
    print(f"Found: {count} regulations")
    
    print("\n=== Get by ID '5.3' ===")
    record = get_by_id(records, '5.3')
    if record:
        print(f"Found: {record['requirement']}")
        print(f"Details: {record['details'][:80]}...")
    
    print("\n=== Mandatory Checklist ===")
    checklist = get_mandatory_checklist(records)
    print(f"Mandatory items: {len(checklist)}")
    for item in checklist[:5]:
        print(f"- {item['regulation_no']}: {item['requirement']}")

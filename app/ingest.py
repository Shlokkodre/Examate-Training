"""
Data ingestion module for HealthLabelCheck
Cleans and processes FSSAI regulation data into structured records
"""

import json
import os
from app.models import RegulationRecord


def clean_text(text):
    """Clean and normalize text data"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters that might cause issues
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    
    return text.strip()


def validate_record(data):
    """
    Validate that a record has all required fields
    Returns (is_valid, error_message)
    """
    required_fields = ['regulation_no', 'requirement', 'applies_to', 
                      'details', 'exemption', 'source_doc']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not data[field]:
            return False, f"Empty field: {field}"
    
    return True, None


def ingest_from_list(raw_data):
    """
    Ingest data from a list of dictionaries
    Returns (records, errors)
    """
    records = []
    errors = []
    
    for i, item in enumerate(raw_data, 1):
        try:
            # Validate
            is_valid, error_msg = validate_record(item)
            if not is_valid:
                errors.append(f"Row {i}: {error_msg}")
                continue
            
            # Clean data
            cleaned_data = {
                'regulation_no': clean_text(item['regulation_no']),
                'requirement': clean_text(item['requirement']),
                'applies_to': clean_text(item['applies_to']),
                'details': clean_text(item['details']),
                'exemption': clean_text(item['exemption']),
                'source_doc': clean_text(item['source_doc'])
            }
            
            # Create record
            record = RegulationRecord.from_dict(cleaned_data)
            records.append(record.to_dict())
            
        except KeyError as e:
            errors.append(f"Row {i}: Missing key {e}")
        except Exception as e:
            errors.append(f"Row {i}: Unexpected error - {e}")
    
    return records, errors


def save_records(records, output_path='data/records.json'):
    """
    Save cleaned records to JSON file
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        return True, f"Saved {len(records)} records to {output_path}"
    
    except Exception as e:
        return False, f"Error saving records: {e}"


def ingest_sample_data():
    """
    Ingest data from sample_records.py
    """
    try:
        from data.sample_records import SAMPLE_RECORDS
        
        print(f"Ingesting {len(SAMPLE_RECORDS)} sample records...")
        records, errors = ingest_from_list(SAMPLE_RECORDS)
        
        if errors:
            print(f"\nWarning: {len(errors)} errors found:")
            for error in errors:
                print(f"  - {error}")
        
        print(f"\nSuccessfully processed {len(records)} records")
        
        # Save to JSON
        success, message = save_records(records)
        print(message)
        
        return records, errors
    
    except ImportError as e:
        print(f"Error: Could not import sample data - {e}")
        return [], [str(e)]


def add_custom_record(regulation_no, requirement, applies_to, 
                     details, exemption, source_doc):
    """
    Add a custom regulation record
    Returns (success, record_or_error)
    """
    try:
        record_data = {
            'regulation_no': regulation_no,
            'requirement': requirement,
            'applies_to': applies_to,
            'details': details,
            'exemption': exemption,
            'source_doc': source_doc
        }
        
        # Validate
        is_valid, error_msg = validate_record(record_data)
        if not is_valid:
            return False, error_msg
        
        # Create record
        record = RegulationRecord.from_dict(record_data)
        return True, record.to_dict()
    
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    print("=== HealthLabelCheck Data Ingestion ===\n")
    
    # Ingest sample data
    records, errors = ingest_sample_data()
    
    print(f"\n=== Summary ===")
    print(f"Total records ingested: {len(records)}")
    print(f"Total errors: {len(errors)}")
    
    if records:
        print(f"\nFirst record:")
        print(json.dumps(records[0], indent=2))
    
    # Test adding a custom record
    print("\n=== Testing Custom Record Addition ===")
    success, result = add_custom_record(
        regulation_no="7.1",
        requirement="Storage Instructions",
        applies_to="Perishable foods",
        details="Storage conditions must be clearly stated",
        exemption="Shelf-stable products",
        source_doc="FSSAI 2020"
    )
    
    if success:
        print("Custom record added successfully:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {result}")

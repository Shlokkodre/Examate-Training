"""
Document fetching module for HealthLabelCheck
Downloads FSSAI regulation documents with error handling
"""

import os
import time


def create_mock_document(filename, content):
    """
    Create a mock document for testing (since we can't download real PDFs yet)
    """
    os.makedirs('data/raw', exist_ok=True)
    filepath = os.path.join('data/raw', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


def simulate_fetch(url, output_filename, timeout=30):
    """
    Simulate fetching a document with error handling
    In Day 3 S2, this will use requests library
    
    Args:
        url: URL to fetch from
        output_filename: Filename to save as
        timeout: Timeout in seconds
    
    Returns:
        (success, filepath_or_error)
    """
    try:
        print(f"Simulating fetch from: {url}")
        print(f"Timeout: {timeout} seconds")
        
        # Simulate network delay
        time.sleep(0.5)
        
        # Create mock content
        mock_content = f"""Mock FSSAI Document
Downloaded from: {url}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

This is a placeholder for the actual document.
In production, this would contain the full PDF content.

Key sections to extract:
- Regulation 5: Mandatory Declarations
- Regulation 6: Font Size Requirements
- Table I: Principal Display Panel Font Sizes
- Schedules and Amendments
"""
        
        filepath = create_mock_document(output_filename, mock_content)
        print(f"✓ Successfully saved to: {filepath}")
        
        return True, filepath
    
    except Exception as e:
        error_msg = f"Error fetching {url}: {e}"
        print(f"✗ {error_msg}")
        return False, error_msg


def fetch_fssai_documents():
    """
    Fetch the main FSSAI labelling documents
    Returns list of (success, filepath_or_error) tuples
    """
    documents = [
        {
            'url': 'https://fssai.gov.in/upload/uploadfiles/files/Compendium_Labelling_Display_04_01_2022.pdf',
            'filename': 'FSSAI_Labelling_Compendium_2022.txt',
            'description': 'FSSAI Labelling and Display Compendium 2022'
        },
        {
            'url': 'https://fssai.gov.in/upload/media/FSSAI_News_Packaged_FNB_04_01_2020.pdf',
            'filename': 'FSSAI_Packaged_Foods_2020.txt',
            'description': 'FSSAI Packaged Food Regulations 2020'
        },
        {
            'url': 'https://fssai.gov.in/upload/advisories/2021_Labelling_Amendment.pdf',
            'filename': 'FSSAI_2021_Amendment.txt',
            'description': 'FSSAI 2021 Labelling Amendment (mock)'
        }
    ]
    
    results = []
    
    print("=== Fetching FSSAI Documents ===\n")
    
    for doc in documents:
        print(f"Fetching: {doc['description']}")
        success, result = simulate_fetch(doc['url'], doc['filename'], timeout=30)
        results.append({
            'description': doc['description'],
            'url': doc['url'],
            'success': success,
            'result': result
        })
        print()
    
    return results


def fetch_with_retry(url, output_filename, max_retries=3, timeout=30):
    """
    Fetch with automatic retry on failure
    
    Args:
        url: URL to fetch
        output_filename: Output filename
        max_retries: Maximum number of retry attempts
        timeout: Timeout per attempt
    
    Returns:
        (success, filepath_or_error)
    """
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}/{max_retries}")
        
        success, result = simulate_fetch(url, output_filename, timeout)
        
        if success:
            return True, result
        
        if attempt < max_retries:
            wait_time = attempt * 2  # Exponential backoff
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    return False, f"Failed after {max_retries} attempts"


if __name__ == "__main__":
    print("=== HealthLabelCheck Document Fetcher ===\n")
    
    # Fetch all documents
    results = fetch_fssai_documents()
    
    # Summary
    print("\n=== Fetch Summary ===")
    success_count = sum(1 for r in results if r['success'])
    print(f"Total documents: {len(results)}")
    print(f"Successfully fetched: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    print("\n=== Details ===")
    for r in results:
        status = "✓" if r['success'] else "✗"
        print(f"{status} {r['description']}")
        if r['success']:
            print(f"   Saved to: {r['result']}")
        else:
            print(f"   Error: {r['result']}")
    
    # Test retry mechanism
    print("\n\n=== Testing Retry Mechanism ===")
    success, result = fetch_with_retry(
        'https://example.com/test.pdf',
        'test_retry.txt',
        max_retries=2,
        timeout=10
    )
    print(f"\nRetry test result: {'Success' if success else 'Failed'}")

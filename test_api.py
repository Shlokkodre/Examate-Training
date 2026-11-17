"""
Quick API test script for Day 4
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("Testing HealthLabelCheck API")
print("=" * 70)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Get records with limit
print("\n2. Testing /records?limit=3...")
response = requests.get(f"{BASE_URL}/records?limit=3")
print(f"Status: {response.status_code}")
print(f"Returned {len(response.json())} records")
print(f"First record: {response.json()[0]['regulation_no']} - {response.json()[0]['requirement']}")

# Test 3: Get specific record by ID
print("\n3. Testing /records/5.3 (Nutritional Information)...")
response = requests.get(f"{BASE_URL}/records/5.3")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Found: {data['regulation_no']} - {data['requirement']}")

# Test 4: Get non-existent record (should return 404)
print("\n4. Testing /records/99.9 (should be 404)...")
response = requests.get(f"{BASE_URL}/records/99.9")
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print(f"Correctly returned 404: {response.json()['detail']}")

# Test 5: Search with smart ranking
print("\n5. Testing /search?q=nutrition...")
response = requests.get(f"{BASE_URL}/search?q=nutrition")
print(f"Status: {response.status_code}")
results = response.json()
print(f"Found {len(results)} results")
for i, r in enumerate(results[:3], 1):
    print(f"  {i}. {r['regulation_no']}: {r['requirement']}")

# Test 6: Ask a question
print("\n6. Testing POST /questions...")
response = requests.post(
    f"{BASE_URL}/questions",
    json={"question": "What is required for the vegetarian symbol?"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Question: {data['question']}")
    print(f"Answer: {data['answer'][:150]}...")
    print(f"Relevant regulations: {data['relevant_regulations']}")

# Test 7: Calculate font size
print("\n7. Testing POST /font-size (12cm x 8cm panel)...")
response = requests.post(
    f"{BASE_URL}/font-size",
    json={"panel_length_cm": 12, "panel_width_cm": 8}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Panel area: {data['panel_area_cm2']} cm²")
    print(f"Minimum font height: {data['min_letter_height_mm']} mm")
    print(f"Regulation: {data['regulation']}")

# Test 8: Get mandatory checklist
print("\n8. Testing /mandatory-checklist...")
response = requests.get(f"{BASE_URL}/mandatory-checklist")
print(f"Status: {response.status_code}")
checklist = response.json()
print(f"Found {len(checklist)} mandatory requirements")
print("First 5 mandatory items:")
for item in checklist[:5]:
    print(f"  ☐ {item['regulation_no']}: {item['requirement']}")

print("\n" + "=" * 70)
print("All API tests completed!")
print("API Documentation available at: http://127.0.0.1:8000/docs")
print("=" * 70)

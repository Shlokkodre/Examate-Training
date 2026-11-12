"""
Smart search module using TF-IDF and cosine similarity
Ranks regulation records by relevance to search query
"""

import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SmartSearch:
    """
    Smart search engine using TF-IDF vectorization and cosine similarity
    """
    
    def __init__(self, records):
        """
        Initialize with regulation records
        
        Args:
            records: List of regulation dictionaries
        """
        self.records = records
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100,
            ngram_range=(1, 2)
        )
        
        # Create searchable text from each record
        self.documents = [
            self._create_searchable_text(record)
            for record in records
        ]
        
        # Fit the vectorizer on all documents
        if self.documents:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        else:
            self.tfidf_matrix = None
    
    def _create_searchable_text(self, record):
        """
        Create searchable text from a record
        Combines relevant fields with weights
        """
        text_parts = [
            record.get('requirement', '') * 3,  # Weight requirement higher
            record.get('regulation_no', '') * 2,
            record.get('details', ''),
            record.get('applies_to', '') * 2,
            record.get('exemption', '')
        ]
        return ' '.join(str(part) for part in text_parts)
    
    def search(self, query, top_k=5):
        """
        Search for relevant regulations
        
        Args:
            query: Search query string
            top_k: Number of top results to return
        
        Returns:
            List of (record, score) tuples, sorted by relevance
        """
        if not self.documents or self.tfidf_matrix is None:
            return []
        
        # Transform the query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filter out zero-similarity results
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0:  # Only include results with some relevance
                results.append({
                    'record': self.records[idx],
                    'score': float(score),
                    'regulation_no': self.records[idx]['regulation_no'],
                    'requirement': self.records[idx]['requirement']
                })
        
        return results
    
    def search_by_category(self, category, query=None):
        """
        Search within a specific category
        
        Args:
            category: Category to filter by (e.g., "All packaged foods")
            query: Optional search query within that category
        
        Returns:
            List of matching records
        """
        filtered_records = [
            r for r in self.records
            if category.lower() in r.get('applies_to', '').lower()
        ]
        
        if not query:
            return filtered_records
        
        # Perform smart search on filtered records
        filtered_search = SmartSearch(filtered_records)
        return filtered_search.search(query)


def load_records():
    """Load records from JSON file"""
    try:
        with open('data/records.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data/records.json not found")
        return []


if __name__ == "__main__":
    print("=== Smart Search with TF-IDF Demo ===\n")
    
    # Load records
    records = load_records()
    print(f"Loaded {len(records)} records")
    
    # Initialize search engine
    search_engine = SmartSearch(records)
    
    # Test queries
    test_queries = [
        "nutrition information requirements",
        "FSSAI license number",
        "vegetarian symbol",
        "font size minimum",
        "list of ingredients"
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: '{query}'")
        print('='*70)
        
        results = search_engine.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['regulation_no']}: {result['requirement']}")
                print(f"   Relevance score: {result['score']:.4f}")
                print(f"   Details: {result['record']['details'][:100]}...")
        else:
            print("No relevant results found")
    
    # Test category search
    print(f"\n{'='*70}")
    print("Category Search: 'All packaged foods' with query 'symbol'")
    print('='*70)
    
    category_results = search_engine.search_by_category("All packaged foods", "symbol")
    for i, result in enumerate(category_results[:3], 1):
        if 'score' in result:
            print(f"\n{i}. {result['regulation_no']}: {result['requirement']}")
            print(f"   Score: {result['score']:.4f}")
        else:
            print(f"\n{i}. {result['regulation_no']}: {result['requirement']}")

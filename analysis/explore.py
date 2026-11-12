"""
Data exploration and analysis for HealthLabelCheck
Uses pandas to analyze FSSAI regulation records
"""

import json
import pandas as pd


def load_records_as_dataframe():
    """Load regulation records as pandas DataFrame"""
    try:
        with open('data/records.json', 'r', encoding='utf-8') as f:
            records = json.load(f)
        return pd.DataFrame(records)
    except FileNotFoundError:
        print("Error: data/records.json not found")
        return pd.DataFrame()


def analyze_records():
    """Perform exploratory analysis on regulation records"""
    df = load_records_as_dataframe()
    
    if df.empty:
        print("No data to analyze")
        return
    
    print("=" * 70)
    print("HEALTHLABELCHECK DATA ANALYSIS")
    print("=" * 70)
    
    # Fact 1: Total number of regulations
    print("\n📊 FACT 1: Dataset Overview")
    print(f"Total number of FSSAI labelling regulations: {len(df)}")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    
    # Fact 2: Category distribution
    print("\n📊 FACT 2: Regulation Categories")
    category_counts = df['applies_to'].value_counts()
    print("\nDistribution by 'applies_to' category:")
    for category, count in category_counts.items():
        print(f"  • {category}: {count} regulations ({count/len(df)*100:.1f}%)")
    
    mandatory_for_all = df[df['applies_to'].str.contains('All packaged foods', case=False, na=False)]
    print(f"\n✓ {len(mandatory_for_all)} regulations apply to ALL packaged foods")
    print(f"✓ {len(df) - len(mandatory_for_all)} regulations have specific applicability")
    
    # Fact 3: Exemptions analysis
    print("\n📊 FACT 3: Exemptions Analysis")
    has_exemptions = df[df['exemption'] != 'None']
    no_exemptions = df[df['exemption'] == 'None']
    
    print(f"Regulations with exemptions: {len(has_exemptions)} ({len(has_exemptions)/len(df)*100:.1f}%)")
    print(f"Regulations with NO exemptions: {len(no_exemptions)} ({len(no_exemptions)/len(df)*100:.1f}%)")
    
    if len(has_exemptions) > 0:
        print("\nRegulations with exemptions:")
        for idx, row in has_exemptions.iterrows():
            print(f"  • {row['regulation_no']}: {row['requirement']}")
            print(f"    Exemption: {row['exemption']}")
    
    # Additional insights
    print("\n📊 ADDITIONAL INSIGHTS")
    
    # Regulation numbering sections
    df['section'] = df['regulation_no'].str.split('.').str[0]
    section_counts = df['section'].value_counts().sort_index()
    print("\nRegulations by section:")
    for section, count in section_counts.items():
        print(f"  Section {section}: {count} regulations")
    
    # Text length analysis
    df['details_length'] = df['details'].str.len()
    avg_length = df['details_length'].mean()
    max_length = df['details_length'].max()
    min_length = df['details_length'].min()
    
    print(f"\nRegulation details text length:")
    print(f"  Average: {avg_length:.0f} characters")
    print(f"  Maximum: {max_length} characters")
    print(f"  Minimum: {min_length} characters")
    
    # Most detailed regulation
    most_detailed = df.loc[df['details_length'].idxmax()]
    print(f"\nMost detailed regulation: {most_detailed['regulation_no']} - {most_detailed['requirement']}")
    
    # Key requirement keywords
    print("\n📊 FACT 4: Common Requirement Keywords")
    all_requirements = ' '.join(df['requirement'].values).lower()
    keywords = ['food', 'name', 'ingredient', 'nutrition', 'label', 'information', 'declaration']
    
    for keyword in keywords:
        count = all_requirements.count(keyword)
        print(f"  '{keyword}': appears {count} times")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    analyze_records()

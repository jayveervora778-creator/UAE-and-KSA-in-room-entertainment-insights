#!/usr/bin/env python3
"""Test the fixed multi-response processor"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend' / 'app'
sys.path.insert(0, str(backend_path))

from fixed_multiresponse_processor import FixedMultiResponseProcessor

def test_processor():
    print("=== TESTING FIXED MULTI-RESPONSE PROCESSOR ===\n")
    
    # Load processor
    data_file = Path('data/survey_data.xlsx')
    processor = FixedMultiResponseProcessor(data_file)
    
    # Test multi-response data
    print("1. Multi-response questions detected:")
    multi_data = processor.get_combined_multiresponse_data()
    
    for question_code, info in multi_data.items():
        print(f"\n{question_code}: {info['question']}")
        print(f"  Total responses: {info['total_responses']}")
        print(f"  Response distribution:")
        
        for choice, count in sorted(info['response_counts'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / info['total_responses']) * 100
            print(f"    {choice}: {count} ({percentage:.1f}%)")
    
    # Test regular data
    print(f"\n2. Regular processed data:")
    combined_df = processor._get_combined_data()
    print(f"  Total respondents: {len(combined_df)}")
    print(f"  Columns: {len(combined_df.columns)}")
    
    # Show some key columns
    key_columns = ['A1', 'A2', 'A3', 'Country']
    for col in key_columns:
        if col in combined_df.columns:
            unique_values = combined_df[col].dropna().unique()
            print(f"  {col}: {len(unique_values)} unique values - {list(unique_values)[:5]}")
    
    print(f"\n3. Filter options:")
    filters = processor.get_filter_options()
    for filter_name, options in filters.items():
        print(f"  {filter_name}: {len(options)} options - {options[:5]}")

if __name__ == "__main__":
    test_processor()

#!/usr/bin/env python3
"""
Quick validation of OSN Dashboard functionality
"""

import pandas as pd
from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor
import sys
from pathlib import Path

def validate_dashboard_components():
    """Validate all key dashboard components"""
    
    print("🔍 OSN Dashboard Validation Report")
    print("=" * 50)
    
    # 1. Check data loading
    try:
        data_path = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        if data_path.exists():
            processor = FixedMultiResponseProcessor(str(data_path))
            
            # Load data using the processor
            survey_data = processor._get_combined_data()
            
            print(f"✅ Data Loading: {len(survey_data)} responses loaded")
            
            print(f"✅ Combined Data: {len(survey_data)} rows, {len(survey_data.columns)} columns")
            
            # Check filter columns
            sample_df = survey_data
            
            # Check key filter columns
            filter_columns = {
                    'A1': 'Country/Market',
                    'A2': 'Nationality', 
                    'A3': 'Purpose of Visit',
                    'A4': 'Visit Frequency'
            }
            
            print(f"\n✅ Filter Columns Check:")
            for col_code, col_name in filter_columns.items():
                if col_code in sample_df.columns:
                    unique_values = sample_df[col_code].nunique()
                    print(f"   - {col_code} ({col_name}): {unique_values} unique values")
                else:
                    print(f"   - ❌ {col_code} ({col_name}): Column not found")
            
            # Check multi-response processing
            print(f"\n✅ Multi-Response Processing:")
            multi_questions = processor.multi_response_questions
            for sheet, questions in multi_questions.items():
                if questions:
                    print(f"   - {sheet}: {len(questions)} multi-response questions")
                    for q_code, q_info in questions.items():
                        print(f"     * {q_code}: {len(q_info['columns'])} options")
            
        else:
            print(f"❌ Data file not found at: {data_path}")
            
    except Exception as e:
        print(f"❌ Data Loading Error: {e}")
    
    # 2. Check analytics components
    try:
        from optimized_analytics import OptimizedOSNAnalytics
        from config import Config
        print(f"\n✅ Advanced Analytics: Available")
    except ImportError as e:
        print(f"\n⚠️ Advanced Analytics: Not available ({e})")
    
    # 3. Check Streamlit configuration
    try:
        config_path = Path(__file__).parent / '.streamlit' / 'config.toml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_content = f.read()
                if 'base = "light"' in config_content:
                    print(f"\n✅ Streamlit Theme: Light theme configured")
                else:
                    print(f"\n⚠️ Streamlit Theme: Light theme not found in config")
        else:
            print(f"\n❌ Streamlit Config: Not found at {config_path}")
    except Exception as e:
        print(f"\n❌ Streamlit Config Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Validation Complete!")

if __name__ == "__main__":
    validate_dashboard_components()
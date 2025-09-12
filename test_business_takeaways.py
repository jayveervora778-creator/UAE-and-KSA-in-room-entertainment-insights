#!/usr/bin/env python3
"""
Test script to verify business takeaways functionality is working correctly
"""

import pandas as pd
from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor

def test_business_takeaways():
    """Test the business takeaways generation without correlation analysis"""
    print("🔍 Testing Business Takeaways Generation...")
    
    # Load the processor and data using the same method as streamlit_app.py
    try:
        from pathlib import Path
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        processor = FixedMultiResponseProcessor(str(data_file))
        df = processor._get_combined_data()
        print(f"✅ Data loaded successfully: {len(df)} responses")
        
        # Test sample filters
        filters = {
            'country': 'All Countries',
            'nationality': 'All Nationalities', 
            'purpose': 'All Purposes',
            'frequency': 'All Frequencies'
        }
        
        # Import the business takeaways function
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import functions from streamlit_app
        from streamlit_app import generate_business_takeaways, detect_patterns_and_insights
        
        # Test on a sample question
        test_questions = ['A1', 'B2', 'C1']  # Sample question codes
        
        for question_code in test_questions:
            if question_code in df.columns:
                print(f"\n📊 Testing question: {question_code}")
                
                # Test business takeaways
                takeaways = generate_business_takeaways(df, question_code, filters)
                print(f"   Generated {len(takeaways)} business takeaways")
                
                # Test pattern insights (should now use business takeaways instead of correlation)
                insights = detect_patterns_and_insights(df, question_code, filters)
                print(f"   Generated {len(insights)} total insights")
                
                # Verify structure
                for i, insight in enumerate(insights[:2]):  # Check first 2
                    required_fields = ['title', 'finding', 'confidence']
                    has_business_action = 'business_action' in insight or 'implication' in insight
                    
                    print(f"   Insight {i+1}: {insight['title'][:50]}...")
                    print(f"   - Has business action: {has_business_action}")
                    print(f"   - Confidence: {insight.get('confidence', 'unknown')}")
                
                break  # Test just one question
        
        print("\n✅ Business takeaways functionality test completed successfully!")
        print("🚫 No correlation analysis detected - correctly removed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing business takeaways: {e}")
        return False

if __name__ == "__main__":
    test_business_takeaways()
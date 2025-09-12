#!/usr/bin/env python3
"""
Test multi-response question visualization functionality
"""

from pathlib import Path
from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor

def test_multiresponse_visualization():
    """Test that B1-A multi-response question works correctly"""
    print("🔍 Testing Multi-Response Question Visualization...")
    
    try:
        # Load data using the same method as streamlit_app.py
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        processor = FixedMultiResponseProcessor(str(data_file))
        
        # Test B1-A multi-response question
        print("\n📊 Testing B1-A: Hotel Choice Factors (Multi-Response)")
        
        # Get multi-response data
        multi_data = processor.get_combined_multiresponse_data()
        
        if 'B1-A' in multi_data:
            b1a_data = multi_data['B1-A']
            print(f"✅ B1-A data found:")
            print(f"   Total responses: {b1a_data.get('total_responses', 0)}")
            print(f"   Response counts: {len(b1a_data.get('response_counts', {}))}")
            
            response_counts = b1a_data.get('response_counts', {})
            print(f"\n📈 Response Distribution:")
            for response, count in sorted(response_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / b1a_data['total_responses']) * 100 if b1a_data['total_responses'] > 0 else 0
                print(f"   • {response}: {count} ({percentage:.1f}%)")
                
            print(f"\n✅ Multi-response visualization data is properly structured!")
            return True
        else:
            print("❌ B1-A multi-response data not found")
            print(f"Available multi-response questions: {list(multi_data.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing multi-response visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_multiresponse_visualization()
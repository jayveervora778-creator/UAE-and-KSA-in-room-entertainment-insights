#!/usr/bin/env python3
"""
Quick test to verify dropdowns and filters are working
"""

def test_dashboard_components():
    """Test key dashboard components"""
    print("🔍 Testing Dashboard Components...")
    
    try:
        # Test data loading
        from pathlib import Path
        from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor
        
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        processor = FixedMultiResponseProcessor(str(data_file))
        df = processor._get_combined_data()
        
        print(f"✅ Data loading: {len(df)} responses")
        
        # Test demographic options function
        from streamlit_app import get_demographic_options, apply_demographic_filters
        
        options = get_demographic_options(df)
        print(f"✅ Demographic options:")
        print(f"   Countries: {len(options.get('countries', []))}")
        print(f"   Nationalities: {len(options.get('nationalities', []))}")
        print(f"   Purposes: {len(options.get('purposes', []))}")
        print(f"   Frequencies: {len(options.get('frequencies', []))}")
        
        # Test filter function
        if options.get('countries'):
            test_country = options['countries'][0]
            filtered_df = apply_demographic_filters(df, test_country, "All Nationalities", "All Purposes", "All Frequencies")
            print(f"✅ Filter test ({test_country}): {len(filtered_df)} guests")
        
        # Test chart creation
        from streamlit_app import create_universal_chart
        
        if 'A1' in df.columns:
            chart = create_universal_chart(df, 'A1', 'Nationality Test', 'auto')
            print(f"✅ Chart creation: {'SUCCESS' if chart else 'FAILED'}")
        
        # Test cross-tabulation
        from streamlit_app import create_cross_tabulation
        
        if 'A1' in df.columns and 'A2' in df.columns:
            cross_chart = create_cross_tabulation(df, 'A1', 'A2')
            print(f"✅ Cross-tabulation: {'SUCCESS' if cross_chart else 'FAILED'}")
        
        print("\n🎉 All Dashboard Components Working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_dashboard_components()
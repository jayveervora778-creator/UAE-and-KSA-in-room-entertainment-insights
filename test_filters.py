#!/usr/bin/env python3
"""
Test if the filters are actually working
"""

import pandas as pd
from pathlib import Path
from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor

def test_filters():
    """Test that demographic filters actually reduce the dataset"""
    print("🔍 Testing Filter Functionality...")
    
    try:
        # Load data
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        processor = FixedMultiResponseProcessor(str(data_file))
        df = processor._get_combined_data()
        
        # Import functions from streamlit_app
        from streamlit_app import apply_demographic_filters, get_demographic_options
        
        print(f"✅ Original dataset: {len(df)} responses")
        
        # Get available options
        options = get_demographic_options(df)
        print(f"✅ Available filter options:")
        print(f"   Countries: {len(options.get('countries', []))} options")
        print(f"   Nationalities: {len(options.get('nationalities', []))} options") 
        print(f"   Purposes: {len(options.get('purposes', []))} options")
        print(f"   Frequencies: {len(options.get('frequencies', []))} options")
        
        # Test 1: No filters (should return full dataset)
        filtered_df = apply_demographic_filters(df, "All Countries", "All Nationalities", "All Purposes", "All Frequencies")
        print(f"\n📊 Test 1 - No Filters: {len(filtered_df)} responses (should be {len(df)})")
        no_filter_working = len(filtered_df) == len(df)
        
        # Test 2: Apply country filter if available
        if options.get('countries'):
            first_country = options['countries'][0]
            filtered_df_country = apply_demographic_filters(df, first_country, "All Nationalities", "All Purposes", "All Frequencies")
            print(f"📊 Test 2 - Country '{first_country}': {len(filtered_df_country)} responses")
            country_filter_working = len(filtered_df_country) < len(df)
            
            # Show what countries are in the filtered data
            if 'Country' in filtered_df_country.columns:
                unique_countries = filtered_df_country['Country'].unique()
                print(f"   Countries in filtered data: {unique_countries}")
        else:
            country_filter_working = True
            print("📊 Test 2 - No countries available to filter")
        
        # Test 3: Apply nationality filter if available  
        if options.get('nationalities'):
            first_nationality = options['nationalities'][0]
            filtered_df_nat = apply_demographic_filters(df, "All Countries", first_nationality, "All Purposes", "All Frequencies")
            print(f"📊 Test 3 - Nationality '{first_nationality}': {len(filtered_df_nat)} responses")
            nationality_filter_working = len(filtered_df_nat) < len(df)
            
            # Show what nationalities are in the filtered data
            if 'A1' in filtered_df_nat.columns:
                unique_nationalities = filtered_df_nat['A1'].dropna().unique()
                print(f"   Nationalities in filtered data: {unique_nationalities[:3]}...")  # Show first 3
        else:
            nationality_filter_working = True
            print("📊 Test 3 - No nationalities available to filter")
            
        # Test 4: Multiple filters
        if options.get('countries') and options.get('nationalities'):
            first_country = options['countries'][0]
            first_nationality = options['nationalities'][0]
            filtered_df_multi = apply_demographic_filters(df, first_country, first_nationality, "All Purposes", "All Frequencies")
            print(f"📊 Test 4 - Multi-filter ({first_country} + {first_nationality}): {len(filtered_df_multi)} responses")
            multi_filter_working = len(filtered_df_multi) <= len(filtered_df_country)
        else:
            multi_filter_working = True
            print("📊 Test 4 - Insufficient options for multi-filter test")
        
        # Summary
        print(f"\n✅ Filter Test Results:")
        print(f"   No filters working: {'✅' if no_filter_working else '❌'}")
        print(f"   Country filter working: {'✅' if country_filter_working else '❌'}")
        print(f"   Nationality filter working: {'✅' if nationality_filter_working else '❌'}")
        print(f"   Multi-filter working: {'✅' if multi_filter_working else '❌'}")
        
        all_working = no_filter_working and country_filter_working and nationality_filter_working and multi_filter_working
        
        if all_working:
            print("\n🎉 ALL FILTERS ARE WORKING CORRECTLY!")
            print("The issue might be elsewhere - filters are not redundant.")
        else:
            print("\n⚠️ SOME FILTERS ARE NOT WORKING PROPERLY!")
            print("This could explain why filters seem redundant.")
            
        return all_working
        
    except Exception as e:
        print(f"❌ Error testing filters: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_filters()
#!/usr/bin/env python3
"""
Debug the dashboard filter issue by simulating the exact same flow
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor

def debug_dashboard_filters():
    """Debug the exact filter flow used in the dashboard"""
    
    st.title("🔍 Filter Debug Dashboard")
    
    # Load data exactly like the main dashboard
    try:
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        processor = FixedMultiResponseProcessor(str(data_file))
        df = processor._get_combined_data()
        
        st.success(f"✅ Data loaded: {len(df)} responses")
        
        # Import functions from main dashboard
        from streamlit_app import get_demographic_options, apply_demographic_filters
        
        # Get options exactly like main dashboard
        demographic_options = get_demographic_options(df)
        
        st.sidebar.title("Debug Filters")
        
        # Create filters exactly like main dashboard
        countries = ['All Countries'] + demographic_options.get('countries', [])
        selected_country = st.sidebar.selectbox("📍 Market", countries, key='country_filter')
        
        nationalities = ['All Nationalities'] + demographic_options.get('nationalities', [])
        selected_nationality = st.sidebar.selectbox("🌍 Nationality", nationalities, key='nationality_filter')
        
        purposes = ['All Purposes'] + demographic_options.get('purposes', [])
        selected_purpose = st.sidebar.selectbox("🎯 Visit Purpose", purposes, key='purpose_filter')
        
        frequencies = ['All Frequencies'] + demographic_options.get('frequencies', [])
        selected_frequency = st.sidebar.selectbox("📅 Visit Frequency", frequencies, key='frequency_filter')
        
        # Apply filters exactly like main dashboard
        filtered_df = apply_demographic_filters(df, selected_country, selected_nationality, selected_purpose, selected_frequency)
        
        # Calculate active filters exactly like main dashboard
        active_filters = 0
        filter_details = []
        
        if selected_country != "All Countries":
            active_filters += 1
            filter_details.append(f"Country: {selected_country}")
        if selected_nationality != "All Nationalities":
            active_filters += 1
            filter_details.append(f"Nationality: {selected_nationality}")
        if selected_purpose != "All Purposes":
            active_filters += 1
            filter_details.append(f"Purpose: {selected_purpose}")
        if selected_frequency != "All Frequencies":
            active_filters += 1
            filter_details.append(f"Frequency: {selected_frequency}")
        
        # Display debug information
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Debug Info:**
            - Original dataset: {len(df)} guests
            - Filtered dataset: {len(filtered_df)} guests
            - Active filters count: {active_filters}
            - Filter reduction: {len(df) - len(filtered_df)} guests
            """)
        
        with col2:
            if active_filters > 0:
                st.success(f"""
                **Active Filters ({active_filters}):**
                {chr(10).join([f"• {detail}" for detail in filter_details])}
                """)
            else:
                st.warning("**No filters active**")
        
        # Test if filtering actually works
        if active_filters > 0:
            if len(filtered_df) < len(df):
                st.success("✅ **FILTERS ARE WORKING** - Dataset size reduced")
            else:
                st.error("❌ **FILTERS NOT WORKING** - Dataset size unchanged")
        else:
            st.info("ℹ️ No filters to test")
        
        # Show sample of filtered data
        if not filtered_df.empty:
            st.subheader("📊 Filtered Data Sample")
            sample_size = min(5, len(filtered_df))
            st.dataframe(filtered_df[['Country', 'A1', 'A2', 'A3']].head(sample_size))
        
    except Exception as e:
        st.error(f"Error in debug: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    debug_dashboard_filters()
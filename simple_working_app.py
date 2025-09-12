#!/usr/bin/env python3
"""
OSN Survey Analytics - Simple Working Version
Clean, functional dashboard without complex features that break
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Configure Plotly to use light theme globally
import plotly.io as pio
pio.templates.default = "plotly_white"

# Import the working data processor
try:
    from comprehensive_data_processor import ComprehensiveOSNProcessor
    print("✅ Imported ComprehensiveOSNProcessor")
except ImportError as e:
    st.error(f"Could not import data processor: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="OSN Survey Analytics - Working Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple light theme CSS that works
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    
    .stMultiSelect > div > div {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    
    .stPlotlyChart {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    .js-plotly-plot {
        background-color: #FFFFFF !important;
    }
    
    /* Hide Streamlit branding */
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load and process the survey data"""
    try:
        processor = ComprehensiveOSNProcessor("data/survey_data.xlsx")
        success = processor.load_and_process_data()
        if success:
            return processor
        else:
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    """Main dashboard application"""
    
    # Header
    st.title("📊 OSN Survey Analytics Dashboard")
    st.markdown("### Enterprise Survey Intelligence Platform")
    st.markdown("**UAE & KSA Markets • 400 Total Responses • Real-Time Analytics**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading survey data..."):
        processor = load_data()
    
    if not processor:
        st.error("❌ Could not load survey data. Please check the data file.")
        st.stop()
    
    # Sidebar filters
    st.sidebar.markdown("## 🎯 Filters")
    
    # Get filter options
    try:
        stats = processor.get_summary_statistics()
        filter_options = stats.get('filter_options', {})
    except Exception as e:
        st.sidebar.error(f"Error loading filters: {e}")
        filter_options = {}
    
    # Country filter
    countries = filter_options.get('countries', ['UAE', 'KSA'])
    selected_countries = st.sidebar.multiselect(
        "📍 Countries",
        options=countries,
        default=countries
    )
    
    # Nationality filter
    nationalities = filter_options.get('nationalities', [])
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Nationalities",
        options=nationalities[:10] if len(nationalities) > 10 else nationalities
    )
    
    # Visit purpose filter
    visit_purposes = filter_options.get('visit_purposes', [])
    selected_purposes = st.sidebar.multiselect(
        "✈️ Visit Purposes",
        options=visit_purposes[:10] if len(visit_purposes) > 10 else visit_purposes
    )
    
    # Create filter dictionary
    filters = {
        'countries': selected_countries,
        'nationalities': selected_nationalities,
        'visit_purposes': selected_purposes
    }
    
    # Get filtered data
    try:
        filtered_data = processor.get_filtered_data(filters)
    except Exception as e:
        st.error(f"Error filtering data: {e}")
        filtered_data = pd.DataFrame()
    
    if len(filtered_data) == 0:
        st.warning("No data available for selected filters.")
        return
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Responses", len(filtered_data))
    
    with col2:
        if 'Country' in filtered_data.columns:
            countries_count = filtered_data['Country'].nunique()
            st.metric("Countries", countries_count)
        else:
            st.metric("Countries", 0)
    
    with col3:
        st.metric("Survey Questions", len(filtered_data.columns) - 1)
    
    with col4:
        if len(filtered_data) > 0:
            completeness = (filtered_data.notna().sum().sum() / (len(filtered_data) * len(filtered_data.columns))) * 100
            st.metric("Data Completeness", f"{completeness:.1f}%")
        else:
            st.metric("Data Completeness", "0%")
    
    st.markdown("---")
    
    # Country distribution
    if 'Country' in filtered_data.columns and len(filtered_data) > 0:
        st.markdown("### 📊 Response Distribution by Country")
        
        col1, col2 = st.columns(2)
        
        with col1:
            country_counts = filtered_data['Country'].value_counts()
            fig_pie = px.pie(
                values=country_counts.values,
                names=country_counts.index,
                title="Country Distribution"
            )
            fig_pie.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1f2937'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title="Response Count by Country",
                labels={'x': 'Country', 'y': 'Number of Responses'}
            )
            fig_bar.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='#1f2937'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Question Explorer
    st.markdown("### 🔍 Question Explorer")
    
    # Get available questions (columns)
    available_questions = [col for col in filtered_data.columns if col != 'Country']
    
    if available_questions:
        selected_question = st.selectbox(
            "📋 Select a Survey Question",
            options=available_questions
        )
        
        if selected_question:
            try:
                question_data = filtered_data[selected_question].dropna()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Responses", len(question_data))
                with col2:
                    st.metric("Unique Answers", question_data.nunique())
                with col3:
                    response_rate = (len(question_data) / len(filtered_data)) * 100
                    st.metric("Response Rate", f"{response_rate:.1f}%")
                
                # Question response distribution
                if len(question_data) > 0:
                    value_counts = question_data.value_counts().head(10)  # Top 10 responses
                    
                    fig = px.bar(
                        x=value_counts.values,
                        y=value_counts.index,
                        orientation='h',
                        title=f"Response Distribution: {selected_question}",
                        labels={'x': 'Count', 'y': 'Response'}
                    )
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font_color='#1f2937'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Sample responses
                    if st.checkbox("Show Sample Responses"):
                        sample_responses = question_data.head(10).tolist()
                        for i, response in enumerate(sample_responses, 1):
                            st.write(f"**{i}.** {response}")
                
            except Exception as e:
                st.error(f"Error analyzing question: {e}")
    
    # Data Summary
    st.markdown("### 📈 Data Summary")
    
    if len(filtered_data) > 0:
        st.write(f"**Showing {len(filtered_data)} responses from {len(filtered_data.columns)} survey questions**")
        
        # Show column info without displaying the actual dataframe to avoid PyArrow errors
        col_info = []
        for col in filtered_data.columns:
            col_info.append({
                'Column': col,
                'Data Type': str(filtered_data[col].dtype),
                'Non-Null Count': filtered_data[col].notna().sum(),
                'Unique Values': filtered_data[col].nunique()
            })
        
        col_df = pd.DataFrame(col_info)
        st.write("**Dataset Information:**")
        
        # Display as simple table without PyArrow conversion
        for _, row in col_df.head(10).iterrows():
            st.write(f"• **{row['Column']}**: {row['Data Type']} ({row['Non-Null Count']} values, {row['Unique Values']} unique)")

if __name__ == "__main__":
    main()
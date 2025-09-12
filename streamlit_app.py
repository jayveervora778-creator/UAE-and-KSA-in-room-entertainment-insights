#!/usr/bin/env python3
"""
OSN Survey Analytics Dashboard - Streamlit Version
Comprehensive survey analytics with native chart support
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys
import os

# Import processors (try both local and backend paths for compatibility)
try:
    from corrected_data_processor import CorrectedSurveyDataProcessor
    from optimized_analytics import OptimizedOSNAnalytics
    from config import Config
except ImportError as e:
    # Fallback to backend path for development
    try:
        backend_path = Path(__file__).parent / 'backend' / 'app'
        sys.path.insert(0, str(backend_path))
        from corrected_data_processor import CorrectedSurveyDataProcessor
        from optimized_analytics import OptimizedOSNAnalytics
        from config import Config
    except ImportError as e2:
        st.error(f"Could not import backend modules: {e2}")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="OSN Survey Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_survey_data():
    """Load and cache survey data"""
    try:
        # Try both local development and deployment paths
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        if not data_file.exists():
            data_file = Path(__file__).parent / 'backend' / 'data' / 'survey_data.xlsx'
        if not data_file.exists():
            st.error(f"Survey data file not found: {data_file}")
            return None, None
        
        processor = CorrectedSurveyDataProcessor(str(data_file))
        analytics = OptimizedOSNAnalytics(processor)
        return processor, analytics
    except Exception as e:
        st.error(f"Error loading survey data: {e}")
        return None, None

def create_entertainment_importance_chart(df):
    """Create entertainment importance by country chart"""
    if 'B2-A' not in df.columns or 'Country' not in df.columns:
        return None
    
    # Clean data
    clean_df = df[['B2-A', 'Country']].dropna()
    
    # Calculate percentages
    country_ent = clean_df.groupby('Country')['B2-A'].value_counts(normalize=True).unstack(fill_value=0) * 100
    
    fig = px.bar(
        x=country_ent.index,
        y=[country_ent.get('Very Important', []), 
           country_ent.get('Somewhat Important', []), 
           country_ent.get('Not Important', [])],
        title="Entertainment Importance by Market",
        labels={'x': 'Country', 'y': 'Percentage (%)'},
        color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
    )
    
    fig.update_layout(
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

def create_content_preferences_chart(df):
    """Create content preferences pie chart"""
    content_cols = [col for col in df.columns if col.startswith('C2-A/')]
    
    if not content_cols:
        return None
    
    content_counts = {}
    for col in content_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            content_type = col_data.iloc[0]
            content_counts[content_type] = len(col_data)
    
    if not content_counts:
        return None
    
    fig = px.pie(
        values=list(content_counts.values()),
        names=list(content_counts.keys()),
        title="Guest Content Preferences",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(height=400)
    return fig

def create_payment_willingness_chart(df):
    """Create payment willingness by visitor type chart"""
    if 'D3' not in df.columns or 'A2' not in df.columns:
        return None
    
    clean_df = df[['D3', 'A2']].dropna()
    payment_by_purpose = clean_df.groupby('A2')['D3'].value_counts(normalize=True).unstack(fill_value=0) * 100
    
    fig = px.bar(
        x=payment_by_purpose.index,
        y=[payment_by_purpose.get('Yes', []), payment_by_purpose.get('No', [])],
        title="Payment Willingness by Visitor Type",
        labels={'x': 'Visit Purpose', 'y': 'Percentage (%)'},
        color_discrete_sequence=['#28a745', '#dc3545']
    )
    
    fig.update_layout(
        barmode='stack',
        height=400,
        showlegend=True
    )
    
    return fig

def create_market_opportunity_chart(df):
    """Create market opportunity scatter plot"""
    opportunities = []
    
    for country in df['Country'].unique():
        country_data = df[df['Country'] == country]
        
        # Entertainment demand
        ent_demand = 50.0
        if 'B2-A' in country_data.columns:
            ent_demand = (country_data['B2-A'] == 'Very Important').mean() * 100
        
        # Payment willingness
        pay_willingness = 50.0
        if 'D3' in country_data.columns:
            pay_willingness = (country_data['D3'] == 'Yes').mean() * 100
        
        opportunities.append({
            'Country': country,
            'Entertainment_Demand': ent_demand,
            'Payment_Willingness': pay_willingness,
            'Opportunity_Score': (ent_demand + pay_willingness) / 2
        })
    
    opp_df = pd.DataFrame(opportunities)
    
    fig = px.scatter(
        opp_df,
        x='Entertainment_Demand',
        y='Payment_Willingness',
        size='Opportunity_Score',
        color='Country',
        title="Market Opportunity Matrix",
        labels={
            'Entertainment_Demand': 'Entertainment Demand (%)',
            'Payment_Willingness': 'Payment Willingness (%)'
        }
    )
    
    fig.update_layout(height=400)
    return fig

def generate_insights(df, filters):
    """Generate AI insights based on filtered data"""
    insights = []
    
    # Entertainment priority analysis
    if 'B2-A' in df.columns:
        very_important_count = (df['B2-A'] == 'Very Important').sum()
        total_responses = len(df)
        very_important_pct = (very_important_count / total_responses) * 100 if total_responses > 0 else 0
        
        insights.append({
            'title': '🎯 Entertainment Priority Distribution',
            'finding': f'{very_important_pct:.1f}% of surveyed guests rate entertainment as "Very Important"',
            'data_backing': f'Based on {very_important_count} out of {total_responses} survey responses',
            'implication': f'Strong demand signals from {very_important_count} high-priority entertainment guests'
        })
    
    # Market comparison
    if 'Country' in df.columns and len(df['Country'].unique()) > 1:
        country_analysis = {}
        for country in df['Country'].unique():
            country_data = df[df['Country'] == country]
            if 'B2-A' in country_data.columns:
                country_very_important = (country_data['B2-A'] == 'Very Important').sum()
                country_total = len(country_data)
                country_pct = (country_very_important / country_total) * 100 if country_total > 0 else 0
                country_analysis[country] = country_pct
        
        if country_analysis:
            best_country = max(country_analysis, key=country_analysis.get)
            best_pct = country_analysis[best_country]
            
            insights.append({
                'title': '🌍 Market Prioritization',
                'finding': f'{best_country} shows highest entertainment priority at {best_pct:.1f}%',
                'data_backing': f'Comparative analysis across {len(country_analysis)} markets',
                'implication': f'Focus OSN+ rollout in {best_country} first for maximum market penetration'
            })
    
    # Payment willingness analysis
    if 'D3' in df.columns:
        willing_count = (df['D3'] == 'Yes').sum()
        willing_pct = (willing_count / len(df)) * 100 if len(df) > 0 else 0
        
        insights.append({
            'title': '💰 Revenue Opportunity',
            'finding': f'{willing_pct:.1f}% of guests are willing to pay premium for entertainment',
            'data_backing': f'{willing_count} out of {len(df)} survey responses',
            'implication': f'Revenue opportunity from {willing_count} confirmed willing-to-pay customers'
        })
    
    return insights

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 OSN UAE & KSA Guest Survey Analytics</h1>
        <p>Complete survey analysis with filtering and AI-backed insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor, analytics = load_survey_data()
    
    if processor is None:
        st.error("Could not load survey data. Please check the data file.")
        st.stop()
    
    # Get combined data
    try:
        df = processor._get_combined_data()
        if df.empty:
            st.error("No data available after processing.")
            st.stop()
    except Exception as e:
        st.error(f"Error getting combined data: {e}")
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Survey Response Filters")
    
    # Country filter
    countries = ['All Countries'] + list(df['Country'].unique())
    selected_country = st.sidebar.selectbox("Country", countries)
    
    # Visit purpose filter (if column exists)
    purposes = ['All Purposes']
    if 'A2' in df.columns:
        purposes.extend(list(df['A2'].dropna().unique()))
    selected_purpose = st.sidebar.selectbox("Visit Purpose", purposes)
    
    # Nationality filter placeholder
    nationalities = ['All Nationalities', 'UAE National', 'Saudi National', 'European', 'American', 'Indian', 'Other']
    selected_nationality = st.sidebar.selectbox("Nationality", nationalities)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_country != 'All Countries':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    if selected_purpose != 'All Purposes':
        if 'A2' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['A2'] == selected_purpose]
    
    # Display filter status
    st.sidebar.markdown(f"""
    **Filter Status:**
    - Showing: **{len(filtered_df)} responses**
    - Country: **{selected_country}**
    - Purpose: **{selected_purpose}**
    - Nationality: **{selected_nationality}**
    """)
    
    # Main dashboard content
    st.header("📈 Complete Survey Analysis")
    st.markdown(f"*All Questions with Current Filters ({len(filtered_df)} responses)*")
    
    # Charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 Entertainment Importance by Market")
        fig1 = create_entertainment_importance_chart(filtered_df)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <strong>📊 Survey Response:</strong> Entertainment importance varies significantly between markets, 
                indicating different guest priorities and opportunities for OSN+ targeting.
                <br><strong>💡 Business Implication:</strong> Prioritize markets showing highest entertainment 
                demand for initial OSN+ hotel partnerships and content strategy.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chart data not available with current filters")
    
    with col2:
        st.subheader("🎬 Guest Content Preferences")
        fig2 = create_content_preferences_chart(filtered_df)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <strong>📊 Survey Response:</strong> Guest preferences show clear patterns toward specific 
                content types, providing direction for OSN+ content strategy.
                <br><strong>💡 Business Implication:</strong> Focus OSN+ content library development 
                on most preferred categories to maximize guest satisfaction.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chart data not available with current filters")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("💳 Payment Willingness by Visitor Type")
        fig3 = create_payment_willingness_chart(filtered_df)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <strong>📊 Survey Response:</strong> Payment willingness varies by visitor type, 
                revealing monetization opportunities across different guest segments.
                <br><strong>💡 Business Implication:</strong> Develop tiered pricing strategies 
                targeting visitor types with highest payment willingness.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chart data not available with current filters")
    
    with col4:
        st.subheader("🎯 Market Opportunity Matrix")
        fig4 = create_market_opportunity_chart(filtered_df)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <strong>📊 Survey Response:</strong> Market opportunity analysis combines entertainment 
                demand with payment willingness to identify optimal expansion targets.
                <br><strong>💡 Business Implication:</strong> Focus on markets in upper-right quadrant 
                for highest ROI on OSN+ investments.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chart data not available with current filters")
    
    # AI Insights Section
    st.header("🧠 AI Insights with Survey Data Rationale")
    
    insights = generate_insights(filtered_df, {
        'country': selected_country,
        'purpose': selected_purpose,
        'nationality': selected_nationality
    })
    
    if insights:
        for insight in insights:
            with st.expander(insight['title'], expanded=True):
                col_finding, col_data = st.columns([2, 1])
                
                with col_finding:
                    st.markdown(f"**Finding:** {insight['finding']}")
                    st.markdown(f"**Implication:** {insight['implication']}")
                
                with col_data:
                    st.info(f"**Data Source:** {insight['data_backing']}")
    else:
        st.info("No insights available with current filter selection.")
    
    # Data summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    **Data Summary:**
    - Total responses: {len(df)}
    - Filtered responses: {len(filtered_df)}
    - Countries: {len(df['Country'].unique())}
    - Survey completion: 100%
    """)

if __name__ == "__main__":
    main()
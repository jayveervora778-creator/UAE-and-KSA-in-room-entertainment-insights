#!/usr/bin/env python3
"""
OSN Survey Analytics Dashboard - Corrected Architecture
Proper slice-and-dice: Hotel Facts (filters) → Guest Opinions (visualizations)
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
from typing import Dict, List, Any, Optional

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

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Filter panel styling */
    .filter-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Insight boxes */
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .implication-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Filter status */
    .filter-status {
        background: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    /* Section headers */
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Hide default streamlit styling */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

def get_hotel_facts_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Extract options for hotel demographic filters"""
    options = {}
    
    # Country (Market)
    if 'Country' in df.columns:
        options['countries'] = sorted(df['Country'].dropna().unique().tolist())
    
    # Nationality (A1)
    if 'A1' in df.columns:
        nationalities = df['A1'].dropna().unique().tolist()
        # Clean up nationalities and sort
        clean_nationalities = []
        for nat in nationalities:
            cleaned = str(nat).strip().replace('\xa0', ' ')  # Remove non-breaking spaces
            if cleaned and cleaned != 'nan':
                clean_nationalities.append(cleaned)
        options['nationalities'] = sorted(list(set(clean_nationalities)))
    
    # Visit Purpose (A2)
    if 'A2' in df.columns:
        purposes = df['A2'].dropna().unique().tolist()
        options['purposes'] = sorted([str(p) for p in purposes if str(p) != 'nan'])
    
    # Visit Frequency (A3)
    if 'A3' in df.columns:
        frequencies = df['A3'].dropna().unique().tolist()
        options['frequencies'] = sorted([str(f) for f in frequencies if str(f) != 'nan'])
    
    return options

def apply_hotel_facts_filter(df: pd.DataFrame, country: str, nationality: str, purpose: str, frequency: str) -> pd.DataFrame:
    """Apply hotel demographic filters to isolate guest segments"""
    filtered_df = df.copy()
    
    # Country filter
    if country and country != "All Countries":
        filtered_df = filtered_df[filtered_df['Country'] == country]
    
    # Nationality filter (A1)
    if nationality and nationality != "All Nationalities" and 'A1' in df.columns:
        # Handle the non-breaking space issue
        mask = filtered_df['A1'].str.replace('\xa0', ' ').str.strip() == nationality
        filtered_df = filtered_df[mask]
    
    # Visit Purpose filter (A2) 
    if purpose and purpose != "All Purposes" and 'A2' in df.columns:
        filtered_df = filtered_df[filtered_df['A2'] == purpose]
    
    # Visit Frequency filter (A3)
    if frequency and frequency != "All Frequencies" and 'A3' in df.columns:
        filtered_df = filtered_df[filtered_df['A3'] == frequency]
    
    return filtered_df

def create_entertainment_importance_chart(df: pd.DataFrame):
    """B2-A: How important is entertainment to you during hotel stays?"""
    if 'B2-A' not in df.columns:
        return None
    
    clean_df = df[['B2-A']].dropna()
    if clean_df.empty:
        return None
    
    # Count responses
    importance_counts = clean_df['B2-A'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=importance_counts.index,
        y=importance_counts.values,
        text=[f"{count}<br>({count/len(clean_df)*100:.1f}%)" for count in importance_counts.values],
        textposition='auto',
        marker_color=['#28a745', '#ffc107', '#dc3545', '#6c757d'][:len(importance_counts)]
    )])
    
    fig.update_layout(
        title="Entertainment Importance During Hotel Stays",
        xaxis_title="Importance Level",
        yaxis_title="Number of Responses",
        height=400,
        showlegend=False
    )
    
    return fig

def create_booking_factors_chart(df: pd.DataFrame):
    """B1-A series: What factors influence your hotel booking decisions?"""
    booking_cols = [col for col in df.columns if col.startswith('B1-A/')]
    
    if not booking_cols:
        return None
    
    # Count mentions across all booking factor columns
    factor_counts = {}
    for col in booking_cols:
        factors = df[col].dropna()
        for factor in factors:
            if factor and str(factor) != 'nan':
                factor_counts[factor] = factor_counts.get(factor, 0) + 1
    
    if not factor_counts:
        return None
    
    # Sort by count
    sorted_factors = dict(sorted(factor_counts.items(), key=lambda x: x[1], reverse=True))
    
    fig = go.Figure(data=[go.Bar(
        x=list(sorted_factors.values()),
        y=list(sorted_factors.keys()),
        orientation='h',
        text=[f"{count} mentions" for count in sorted_factors.values()],
        textposition='auto',
        marker_color='#667eea'
    )])
    
    fig.update_layout(
        title="Hotel Booking Decision Factors",
        xaxis_title="Number of Mentions",
        yaxis_title="Booking Factors",
        height=400,
        showlegend=False
    )
    
    return fig

def create_content_preferences_chart(df: pd.DataFrame):
    """C2-A series: Content/service preferences"""
    content_cols = [col for col in df.columns if col.startswith('C2-A/')]
    
    if not content_cols:
        return None
    
    # Count preferences
    pref_counts = {}
    for col in content_cols:
        prefs = df[col].dropna()
        for pref in prefs:
            if pref and str(pref) != 'nan':
                pref_counts[pref] = pref_counts.get(pref, 0) + 1
    
    if not pref_counts:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=list(pref_counts.keys()),
        values=list(pref_counts.values()),
        hole=0.4,
        marker_colors=px.colors.qualitative.Set3
    )])
    
    fig.update_layout(
        title="Guest Content/Service Preferences",
        height=400,
        showlegend=True
    )
    
    return fig

def create_satisfaction_ratings_chart(df: pd.DataFrame):
    """D1 series: Satisfaction ratings across different aspects"""
    satisfaction_cols = [col for col in df.columns if col.startswith('D1/')]
    
    if not satisfaction_cols:
        return None
    
    # Create satisfaction heatmap
    satisfaction_data = []
    for col in satisfaction_cols:
        ratings = df[col].dropna()
        if not ratings.empty:
            # Assuming numeric ratings or convert text to numeric
            try:
                numeric_ratings = pd.to_numeric(ratings, errors='coerce').dropna()
                if not numeric_ratings.empty:
                    avg_rating = numeric_ratings.mean()
                    satisfaction_data.append({
                        'Aspect': col.replace('D1/', 'Aspect '),
                        'Average_Rating': avg_rating,
                        'Response_Count': len(numeric_ratings)
                    })
            except:
                # Handle text ratings
                rating_counts = ratings.value_counts()
                if not rating_counts.empty:
                    satisfaction_data.append({
                        'Aspect': col.replace('D1/', 'Aspect '),
                        'Top_Rating': rating_counts.index[0],
                        'Response_Count': len(ratings)
                    })
    
    if not satisfaction_data:
        return None
    
    sat_df = pd.DataFrame(satisfaction_data)
    
    if 'Average_Rating' in sat_df.columns:
        fig = go.Figure(data=[go.Bar(
            x=sat_df['Aspect'],
            y=sat_df['Average_Rating'],
            text=[f"{rating:.1f}<br>({count} responses)" for rating, count in zip(sat_df['Average_Rating'], sat_df['Response_Count'])],
            textposition='auto',
            marker_color='#28a745'
        )])
        
        fig.update_layout(
            title="Average Satisfaction Ratings by Aspect",
            xaxis_title="Service Aspects", 
            yaxis_title="Average Rating",
            height=400,
            showlegend=False
        )
    else:
        fig = go.Figure(data=[go.Bar(
            x=sat_df['Aspect'],
            y=sat_df['Response_Count'],
            text=[f"{count} responses" for count in sat_df['Response_Count']],
            textposition='auto',
            marker_color='#17a2b8'
        )])
        
        fig.update_layout(
            title="Satisfaction Response Counts by Aspect",
            xaxis_title="Service Aspects",
            yaxis_title="Number of Responses", 
            height=400,
            showlegend=False
        )
    
    return fig

def create_willingness_to_pay_chart(df: pd.DataFrame):
    """C2-B: Willingness to pay for enhanced services"""
    if 'C2-B' not in df.columns:
        return None
    
    clean_df = df[['C2-B']].dropna()
    if clean_df.empty:
        return None
    
    willingness_counts = clean_df['C2-B'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=willingness_counts.index,
        y=willingness_counts.values,
        text=[f"{count}<br>({count/len(clean_df)*100:.1f}%)" for count in willingness_counts.values],
        textposition='auto',
        marker_color=['#28a745', '#ffc107', '#dc3545'][:len(willingness_counts)]
    )])
    
    fig.update_layout(
        title="Willingness to Pay for Enhanced Entertainment Services",
        xaxis_title="Response",
        yaxis_title="Number of Guests",
        height=400,
        showlegend=False
    )
    
    return fig

def generate_segment_insights(df: pd.DataFrame, filters: Dict[str, str]) -> List[Dict[str, str]]:
    """Generate insights for the filtered guest segment"""
    
    insights = []
    
    # Create segment description
    segment_parts = []
    if filters.get('country') and filters['country'] != 'All Countries':
        segment_parts.append(f"{filters['country']} market")
    if filters.get('nationality') and filters['nationality'] != 'All Nationalities':
        segment_parts.append(f"{filters['nationality']} guests")
    if filters.get('purpose') and filters['purpose'] != 'All Purposes':
        segment_parts.append(f"{filters['purpose'].lower()} travelers")
    if filters.get('frequency') and filters['frequency'] != 'All Frequencies':
        segment_parts.append(f"visiting {filters['frequency'].lower()}")
    
    segment_desc = " | ".join(segment_parts) if segment_parts else "All guests"
    
    # Entertainment importance insight
    if 'B2-A' in df.columns:
        ent_data = df['B2-A'].dropna()
        if not ent_data.empty:
            very_important = (ent_data == 'Very Important').sum()
            percentage = (very_important / len(ent_data)) * 100
            
            insights.append({
                'title': '🎬 Entertainment Priority Analysis',
                'finding': f'{percentage:.1f}% of this guest segment ({very_important}/{len(ent_data)}) rate entertainment as "Very Important"',
                'implication': f'{"High" if percentage > 50 else "Moderate" if percentage > 30 else "Low"} entertainment demand in this segment - {"prioritize" if percentage > 50 else "consider" if percentage > 30 else "lower priority for"} OSN+ integration',
                'data_backing': f'Based on {len(ent_data)} responses from: {segment_desc}'
            })
    
    # Payment willingness insight
    if 'C2-B' in df.columns:
        pay_data = df['C2-B'].dropna()
        if not pay_data.empty:
            positive_responses = pay_data[pay_data.isin(['Yes', 'Definitely', 'Very Likely', 'Likely'])].count()
            percentage = (positive_responses / len(pay_data)) * 100
            
            insights.append({
                'title': '💰 Monetization Potential',
                'finding': f'{percentage:.1f}% of this segment ({positive_responses}/{len(pay_data)}) show willingness to pay for enhanced services',
                'implication': f'{"Strong" if percentage > 60 else "Moderate" if percentage > 40 else "Limited"} revenue opportunity - {"develop premium packages" if percentage > 60 else "test pricing models" if percentage > 40 else "focus on basic offerings"}',
                'data_backing': f'Based on {len(pay_data)} payment preference responses from: {segment_desc}'
            })
    
    # Booking factors insight
    booking_cols = [col for col in df.columns if col.startswith('B1-A/')]
    if booking_cols:
        factor_mentions = 0
        entertainment_mentions = 0
        
        for col in booking_cols:
            factors = df[col].dropna()
            factor_mentions += len(factors)
            entertainment_mentions += factors.str.contains('Entertainment', case=False, na=False).sum()
        
        if factor_mentions > 0:
            ent_factor_percentage = (entertainment_mentions / factor_mentions) * 100
            
            insights.append({
                'title': '🏨 Booking Decision Influence',
                'finding': f'Entertainment appears in {ent_factor_percentage:.1f}% of booking decision factors ({entertainment_mentions}/{factor_mentions} mentions)',
                'implication': f'Entertainment is {"highly influential" if ent_factor_percentage > 20 else "moderately influential" if ent_factor_percentage > 10 else "less influential"} in booking decisions for this segment',
                'data_backing': f'Based on {factor_mentions} booking factor mentions from: {segment_desc}'
            })
    
    return insights

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>📊 OSN UAE & KSA Guest Survey Analytics</h1>
        <p>Slice & Dice: Hotel Guest Facts → Survey Opinion Analysis</p>
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
    
    # Get filter options
    hotel_facts_options = get_hotel_facts_options(df)
    
    # Sidebar - Hotel Facts Filters
    st.sidebar.markdown("""
    <div class="filter-panel">
        <h4>🏨 Hotel Guest Facts</h4>
        <p>Filter by what the hotel knows about guests</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Country (Market) filter
    countries = ['All Countries'] + hotel_facts_options.get('countries', [])
    selected_country = st.sidebar.selectbox("📍 Market", countries, key='country_filter')
    
    # Nationality filter (A1) - CORRECTED
    nationalities = ['All Nationalities'] + hotel_facts_options.get('nationalities', [])
    selected_nationality = st.sidebar.selectbox("🌍 Guest Nationality", nationalities, key='nationality_filter')
    
    # Visit Purpose filter (A2)
    purposes = ['All Purposes'] + hotel_facts_options.get('purposes', [])
    selected_purpose = st.sidebar.selectbox("🎯 Visit Purpose", purposes, key='purpose_filter')
    
    # Visit Frequency filter (A3)
    frequencies = ['All Frequencies'] + hotel_facts_options.get('frequencies', [])
    selected_frequency = st.sidebar.selectbox("📅 Visit Frequency", frequencies, key='frequency_filter')
    
    # Apply hotel facts filters
    filtered_df = apply_hotel_facts_filter(df, selected_country, selected_nationality, selected_purpose, selected_frequency)
    
    # Filter status display
    filter_parts = []
    if selected_country != "All Countries":
        filter_parts.append(f"Market: {selected_country}")
    if selected_nationality != "All Nationalities":
        filter_parts.append(f"Nationality: {selected_nationality}")
    if selected_purpose != "All Purposes":
        filter_parts.append(f"Purpose: {selected_purpose}")
    if selected_frequency != "All Frequencies":
        filter_parts.append(f"Frequency: {selected_frequency}")
    
    filter_text = " | ".join(filter_parts) if filter_parts else "All guests"
    
    st.markdown(f"""
    <div class="filter-status">
        👥 Guest Segment: {len(filtered_df)} responses | {filter_text}
    </div>
    """, unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.warning("No guests match the selected demographic criteria. Please adjust your filters.")
        return
    
    # Main dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(filtered_df)}</h3>
            <p>Guest Responses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        nationalities_count = len(filtered_df['A1'].dropna().unique()) if 'A1' in filtered_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{nationalities_count}</h3>
            <p>Nationalities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Entertainment importance percentage
        ent_importance = 0
        if 'B2-A' in filtered_df.columns:
            ent_data = filtered_df['B2-A'].dropna()
            if not ent_data.empty:
                ent_importance = (ent_data == 'Very Important').sum() / len(ent_data) * 100
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ent_importance:.1f}%</h3>
            <p>High Entertainment Priority</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Willingness to pay percentage
        pay_willing = 0
        if 'C2-B' in filtered_df.columns:
            pay_data = filtered_df['C2-B'].dropna()
            if not pay_data.empty:
                positive = pay_data[pay_data.isin(['Yes', 'Definitely', 'Very Likely', 'Likely'])].count()
                pay_willing = (positive / len(pay_data)) * 100
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{pay_willing:.1f}%</h3>
            <p>Willing to Pay Premium</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Guest Opinion Analysis Section
    st.markdown("""
    <div class="section-header">
        <h2>📊 Guest Opinion Analysis</h2>
        <p>Survey responses from the selected guest segment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chart sections - Guest Opinions
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Entertainment Importance
        st.markdown("### 🎬 Entertainment Importance")
        ent_chart = create_entertainment_importance_chart(filtered_df)
        if ent_chart:
            st.plotly_chart(ent_chart, use_container_width=True)
        else:
            st.info("No entertainment importance data for this segment")
        
        # Content Preferences
        st.markdown("### 🎵 Content Preferences")
        content_chart = create_content_preferences_chart(filtered_df)
        if content_chart:
            st.plotly_chart(content_chart, use_container_width=True)
        else:
            st.info("No content preference data for this segment")
    
    with col_right:
        # Booking Factors
        st.markdown("### 🏨 Hotel Booking Factors")
        booking_chart = create_booking_factors_chart(filtered_df)
        if booking_chart:
            st.plotly_chart(booking_chart, use_container_width=True)
        else:
            st.info("No booking factor data for this segment")
        
        # Willingness to Pay
        st.markdown("### 💰 Payment Willingness")
        payment_chart = create_willingness_to_pay_chart(filtered_df)
        if payment_chart:
            st.plotly_chart(payment_chart, use_container_width=True)
        else:
            st.info("No payment willingness data for this segment")
    
    # Satisfaction Ratings (full width)
    st.markdown("### ⭐ Satisfaction Ratings")
    satisfaction_chart = create_satisfaction_ratings_chart(filtered_df)
    if satisfaction_chart:
        st.plotly_chart(satisfaction_chart, use_container_width=True)
    else:
        st.info("No satisfaction rating data for this segment")
    
    # AI Insights Section
    st.markdown("""
    <div class="section-header">
        <h2>🧠 Guest Segment Insights</h2>
        <p>AI analysis of the selected guest demographic and their survey responses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate insights
    segment_insights = generate_segment_insights(filtered_df, {
        'country': selected_country,
        'nationality': selected_nationality,
        'purpose': selected_purpose,
        'frequency': selected_frequency
    })
    
    # Display insights
    for insight in segment_insights:
        with st.expander(insight['title'], expanded=True):
            col_finding, col_data = st.columns([2, 1])
            
            with col_finding:
                st.markdown(f"**Finding:** {insight['finding']}")
                st.markdown(f"**Business Implication:** {insight['implication']}")
            
            with col_data:
                st.info(f"**Data Source:** {insight['data_backing']}")
    
    # Data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    **Data Summary:**
    - Total guests: {len(df)}
    - Filtered segment: {len(filtered_df)}
    - Available nationalities: {len(hotel_facts_options.get('nationalities', []))}
    - Survey questions: {len([col for col in df.columns if col.startswith(('B', 'C', 'D'))])}
    """)

if __name__ == "__main__":
    main()
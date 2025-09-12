#!/usr/bin/env python3
"""
OSN Survey Analytics Dashboard - Enhanced Streamlit Version
Comprehensive survey analytics with rich filtering and AI insights
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

# Custom CSS for professional styling matching original design
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

def get_filter_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Extract unique values for filter dropdowns"""
    filter_options = {}
    
    # Country options
    if 'Country' in df.columns:
        filter_options['countries'] = sorted(df['Country'].unique().tolist())
    
    # Visit purpose options (A2 column)
    if 'A2' in df.columns:
        purposes = df['A2'].dropna().unique().tolist()
        filter_options['purposes'] = sorted([p for p in purposes if str(p) != 'nan'])
    
    # Nationality options (A3 column if exists)
    if 'A3' in df.columns:
        nationalities = df['A3'].dropna().unique().tolist()
        filter_options['nationalities'] = sorted([n for n in nationalities if str(n) != 'nan'])
    
    return filter_options

def filter_data(df: pd.DataFrame, country: str, purpose: str, nationality: str) -> pd.DataFrame:
    """Apply filters to the dataframe"""
    filtered_df = df.copy()
    
    if country and country != "All Countries":
        filtered_df = filtered_df[filtered_df['Country'] == country]
    
    if purpose and purpose != "All Purposes" and 'A2' in df.columns:
        filtered_df = filtered_df[filtered_df['A2'] == purpose]
    
    if nationality and nationality != "All Nationalities" and 'A3' in df.columns:
        filtered_df = filtered_df[filtered_df['A3'] == nationality]
    
    return filtered_df

def create_entertainment_importance_chart(df: pd.DataFrame):
    """Create entertainment importance by country chart"""
    if 'B2-A' not in df.columns or 'Country' not in df.columns:
        return None
    
    clean_df = df[['B2-A', 'Country']].dropna()
    if clean_df.empty:
        return None
    
    # Calculate percentages by country
    country_ent = clean_df.groupby('Country')['B2-A'].value_counts(normalize=True).unstack(fill_value=0) * 100
    
    fig = go.Figure()
    
    colors = {'Very Important': '#28a745', 'Somewhat Important': '#ffc107', 'Not Important': '#dc3545'}
    
    for importance in ['Very Important', 'Somewhat Important', 'Not Important']:
        if importance in country_ent.columns:
            fig.add_trace(go.Bar(
                name=importance,
                x=country_ent.index,
                y=country_ent[importance],
                marker_color=colors.get(importance, '#007bff'),
                text=[f"{val:.1f}%" for val in country_ent[importance]],
                textposition='inside'
            ))
    
    fig.update_layout(
        title="Entertainment Importance by Market",
        xaxis_title="Country",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

def create_payment_willingness_chart(df: pd.DataFrame):
    """Create payment willingness analysis chart"""
    payment_cols = [col for col in df.columns if 'payment' in col.lower() or 'willing' in col.lower()]
    
    if not payment_cols and 'C2-A' in df.columns:
        payment_cols = ['C2-A']
    
    if not payment_cols:
        return None
    
    col = payment_cols[0]
    clean_df = df[[col, 'Country']].dropna()
    
    if clean_df.empty:
        return None
    
    # Calculate payment willingness by country
    payment_analysis = clean_df.groupby('Country')[col].value_counts(normalize=True).unstack(fill_value=0) * 100
    
    fig = go.Figure()
    
    colors = ['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1']
    
    for i, response in enumerate(payment_analysis.columns):
        fig.add_trace(go.Bar(
            name=str(response),
            x=payment_analysis.index,
            y=payment_analysis[response],
            marker_color=colors[i % len(colors)],
            text=[f"{val:.1f}%" for val in payment_analysis[response]],
            textposition='inside'
        ))
    
    fig.update_layout(
        title="Payment Willingness by Market",
        xaxis_title="Country",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

def create_satisfaction_analysis_chart(df: pd.DataFrame):
    """Create satisfaction analysis chart"""
    satisfaction_cols = [col for col in df.columns if 'satisfaction' in col.lower() or 'satisfied' in col.lower()]
    
    if not satisfaction_cols and 'D1' in df.columns:
        satisfaction_cols = ['D1']
    
    if not satisfaction_cols:
        return None
    
    col = satisfaction_cols[0]
    clean_df = df[[col, 'Country']].dropna()
    
    if clean_df.empty:
        return None
    
    # Calculate satisfaction by country
    satisfaction_analysis = clean_df.groupby('Country')[col].value_counts(normalize=True).unstack(fill_value=0) * 100
    
    fig = go.Figure()
    
    colors = {'Very Satisfied': '#28a745', 'Satisfied': '#17a2b8', 'Neutral': '#ffc107', 'Dissatisfied': '#fd7e14', 'Very Dissatisfied': '#dc3545'}
    
    for response in satisfaction_analysis.columns:
        color = colors.get(str(response), '#007bff')
        fig.add_trace(go.Bar(
            name=str(response),
            x=satisfaction_analysis.index,
            y=satisfaction_analysis[response],
            marker_color=color,
            text=[f"{val:.1f}%" for val in satisfaction_analysis[response]],
            textposition='inside'
        ))
    
    fig.update_layout(
        title="Current Satisfaction Levels by Market",
        xaxis_title="Country",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

def create_content_preferences_chart(df: pd.DataFrame):
    """Create content preferences distribution chart"""
    content_cols = [col for col in df.columns if 'content' in col.lower() or 'prefer' in col.lower()]
    
    if not content_cols and 'B1-A/1' in df.columns:
        # Use entertainment preferences columns
        content_cols = [col for col in df.columns if col.startswith('B1-A/')]
    
    if not content_cols:
        return None
    
    # Aggregate content preferences
    preferences = {}
    for col in content_cols:
        col_name = col.replace('B1-A/', '').replace('/', ' ')
        if col_name.isdigit():
            col_name = f"Content Type {col_name}"
        
        clean_data = df[col].dropna()
        if not clean_data.empty:
            preferences[col_name] = len(clean_data)
    
    if not preferences:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=list(preferences.keys()),
        values=list(preferences.values()),
        hole=0.4,
        marker_colors=px.colors.qualitative.Set3
    )])
    
    fig.update_layout(
        title="Content Preferences Distribution",
        height=400,
        showlegend=True
    )
    
    return fig

def create_market_opportunity_heatmap(df: pd.DataFrame):
    """Create market opportunity analysis heatmap"""
    if 'Country' not in df.columns:
        return None
    
    countries = df['Country'].unique()
    
    # Calculate entertainment importance and payment willingness for each country
    opportunity_data = []
    
    for country in countries:
        country_df = df[df['Country'] == country]
        
        # Entertainment importance (B2-A)
        ent_score = 0
        if 'B2-A' in df.columns:
            ent_data = country_df['B2-A'].dropna()
            if not ent_data.empty:
                ent_score = (ent_data == 'Very Important').sum() / len(ent_data) * 100
        
        # Payment willingness (C2-A)
        pay_score = 0
        if 'C2-A' in df.columns:
            pay_data = country_df['C2-A'].dropna()
            if not pay_data.empty:
                # Assuming positive responses indicate willingness
                positive_responses = ['Yes', 'Definitely', 'Very Likely', 'Likely']
                pay_score = sum(pay_data.isin(positive_responses)) / len(pay_data) * 100
        
        opportunity_data.append({
            'Country': country,
            'Entertainment_Demand': ent_score,
            'Payment_Willingness': pay_score,
            'Opportunity_Score': (ent_score + pay_score) / 2
        })
    
    if not opportunity_data:
        return None
    
    opp_df = pd.DataFrame(opportunity_data)
    
    fig = go.Figure(data=go.Scatter(
        x=opp_df['Entertainment_Demand'],
        y=opp_df['Payment_Willingness'], 
        mode='markers+text',
        text=opp_df['Country'],
        textposition='top center',
        marker=dict(
            size=opp_df['Opportunity_Score'],
            sizemode='diameter',
            sizeref=2.*max(opp_df['Opportunity_Score'])/(40.**2),
            color=opp_df['Opportunity_Score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Opportunity Score")
        )
    ))
    
    fig.update_layout(
        title="Market Opportunity Analysis",
        xaxis_title="Entertainment Demand (%)",
        yaxis_title="Payment Willingness (%)",
        height=400
    )
    
    return fig

def generate_chart_insights(chart_type: str, df: pd.DataFrame, filters: Dict[str, str]) -> Dict[str, str]:
    """Generate AI insights for each chart with survey-backed rationale"""
    
    insights = {
        'finding': '',
        'implication': '',
        'data_backing': ''
    }
    
    filter_desc = []
    if filters.get('country') and filters['country'] != 'All Countries':
        filter_desc.append(f"Country: {filters['country']}")
    if filters.get('purpose') and filters['purpose'] != 'All Purposes':
        filter_desc.append(f"Purpose: {filters['purpose']}")
    if filters.get('nationality') and filters['nationality'] != 'All Nationalities':
        filter_desc.append(f"Nationality: {filters['nationality']}")
    
    filter_text = " | ".join(filter_desc) if filter_desc else "All responses"
    
    if chart_type == 'entertainment_importance':
        if 'B2-A' in df.columns and 'Country' in df.columns:
            clean_df = df[['B2-A', 'Country']].dropna()
            if not clean_df.empty:
                very_important = clean_df[clean_df['B2-A'] == 'Very Important']
                country_stats = very_important.groupby('Country').size()
                
                if not country_stats.empty:
                    top_country = country_stats.idxmax()
                    top_percentage = (country_stats.max() / clean_df.groupby('Country').size()[top_country]) * 100
                    
                    insights['finding'] = f"{top_percentage:.1f}% of {top_country} guests rate entertainment as 'Very Important' (highest among surveyed markets)"
                    insights['implication'] = f"Prioritize OSN+ integration in {top_country} hotels - strong entertainment demand indicates high adoption potential"
                    insights['data_backing'] = f"Based on {len(clean_df)} responses | Filters: {filter_text}"
    
    elif chart_type == 'payment_willingness':
        if 'C2-A' in df.columns:
            payment_data = df['C2-A'].dropna()
            if not payment_data.empty:
                positive_responses = ['Yes', 'Definitely', 'Very Likely', 'Likely']
                willing_count = sum(payment_data.isin(positive_responses))
                percentage = (willing_count / len(payment_data)) * 100
                
                insights['finding'] = f"{percentage:.1f}% of guests express willingness to pay premium for enhanced entertainment services"
                insights['implication'] = "Strong monetization opportunity - develop tiered entertainment packages for willing-to-pay segments"
                insights['data_backing'] = f"Based on {len(payment_data)} payment preference responses | Filters: {filter_text}"
    
    elif chart_type == 'market_opportunity':
        countries = df['Country'].unique() if 'Country' in df.columns else []
        if len(countries) > 0:
            insights['finding'] = f"Market analysis across {len(countries)} markets reveals varying entertainment demand and payment willingness levels"
            insights['implication'] = "Focus expansion on upper-right quadrant markets for optimal ROI on OSN+ investments"
            insights['data_backing'] = f"Combined analysis of entertainment importance + payment willingness | Filters: {filter_text}"
    
    else:
        insights['finding'] = "Survey data analysis provides valuable insights into guest preferences and market opportunities"
        insights['implication'] = "Use data-driven insights to optimize OSN entertainment strategy and partnership development"
        insights['data_backing'] = f"Survey analysis | Filters: {filter_text}"
    
    return insights

def main():
    # Main header
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
    
    # Get filter options
    filter_options = get_filter_options(df)
    
    # Sidebar filters
    st.sidebar.markdown("""
    <div class="filter-panel">
        <h4>🔍 Survey Response Filters</h4>
        <p>Select filters to analyze specific segments</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Country filter
    countries = ['All Countries'] + filter_options.get('countries', [])
    selected_country = st.sidebar.selectbox("Country", countries, key='country_filter')
    
    # Visit purpose filter
    purposes = ['All Purposes'] + filter_options.get('purposes', [])
    selected_purpose = st.sidebar.selectbox("Visit Purpose", purposes, key='purpose_filter')
    
    # Nationality filter
    nationalities = ['All Nationalities'] + filter_options.get('nationalities', [])
    selected_nationality = st.sidebar.selectbox("Nationality", nationalities, key='nationality_filter')
    
    # Apply filters
    filtered_df = filter_data(df, selected_country, selected_purpose, selected_nationality)
    
    # Filter status
    filter_parts = []
    if selected_country != "All Countries":
        filter_parts.append(f"Country: {selected_country}")
    if selected_purpose != "All Purposes":
        filter_parts.append(f"Purpose: {selected_purpose}")
    if selected_nationality != "All Nationalities":
        filter_parts.append(f"Nationality: {selected_nationality}")
    
    filter_text = " | ".join(filter_parts) if filter_parts else "All responses"
    
    st.markdown(f"""
    <div class="filter-status">
        📊 Showing: {len(filtered_df)} responses | Filters: {filter_text}
    </div>
    """, unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selection.")
        return
    
    # Main dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(filtered_df)}</h3>
            <p>Total Responses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        countries_count = len(filtered_df['Country'].unique()) if 'Country' in filtered_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{countries_count}</h3>
            <p>Markets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate entertainment demand
        ent_demand = 0
        if 'B2-A' in filtered_df.columns:
            ent_data = filtered_df['B2-A'].dropna()
            if not ent_data.empty:
                ent_demand = (ent_data == 'Very Important').sum() / len(ent_data) * 100
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ent_demand:.1f}%</h3>
            <p>High Entertainment Demand</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calculate payment willingness
        pay_willing = 0
        if 'C2-A' in filtered_df.columns:
            pay_data = filtered_df['C2-A'].dropna()
            if not pay_data.empty:
                positive_responses = ['Yes', 'Definitely', 'Very Likely', 'Likely']
                pay_willing = sum(pay_data.isin(positive_responses)) / len(pay_data) * 100
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{pay_willing:.1f}%</h3>
            <p>Willing to Pay Premium</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chart sections
    st.markdown("## 📈 Complete Survey Analysis")
    st.markdown("*All survey questions visualized with current filters applied*")
    
    # Entertainment Importance Chart
    st.markdown("### Entertainment Importance by Market")
    ent_chart = create_entertainment_importance_chart(filtered_df)
    if ent_chart:
        st.plotly_chart(ent_chart, use_container_width=True)
        
        # Chart insights
        insights = generate_chart_insights('entertainment_importance', filtered_df, {
            'country': selected_country,
            'purpose': selected_purpose, 
            'nationality': selected_nationality
        })
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>📊 Survey Response:</strong> {insights['finding']}
        </div>
        <div class="implication-box">
            <strong>💡 Business Implication:</strong> {insights['implication']}
            <br><small><strong>Data Source:</strong> {insights['data_backing']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Entertainment importance data not available with current filters")
    
    # Payment Willingness Chart
    st.markdown("### Payment Willingness Analysis")
    payment_chart = create_payment_willingness_chart(filtered_df)
    if payment_chart:
        st.plotly_chart(payment_chart, use_container_width=True)
        
        insights = generate_chart_insights('payment_willingness', filtered_df, {
            'country': selected_country,
            'purpose': selected_purpose,
            'nationality': selected_nationality
        })
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>📊 Survey Response:</strong> {insights['finding']}
        </div>
        <div class="implication-box">
            <strong>💡 Business Implication:</strong> {insights['implication']}
            <br><small><strong>Data Source:</strong> {insights['data_backing']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Payment willingness data not available with current filters")
    
    # Content Preferences Chart
    st.markdown("### Content Preferences Distribution")
    content_chart = create_content_preferences_chart(filtered_df)
    if content_chart:
        st.plotly_chart(content_chart, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
            <strong>📊 Survey Response:</strong> Content preference analysis reveals guest entertainment priorities
        </div>
        <div class="implication-box">
            <strong>💡 Business Implication:</strong> Focus OSN+ content strategy on highest-demand categories for maximum engagement
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Content preferences data not available with current filters")
    
    # Market Opportunity Heatmap
    st.markdown("### Market Opportunity Analysis")
    opportunity_chart = create_market_opportunity_heatmap(filtered_df)
    if opportunity_chart:
        st.plotly_chart(opportunity_chart, use_container_width=True)
        
        insights = generate_chart_insights('market_opportunity', filtered_df, {
            'country': selected_country,
            'purpose': selected_purpose,
            'nationality': selected_nationality
        })
        
        st.markdown(f"""
        <div class="insight-box">
            <strong>📊 Survey Response:</strong> {insights['finding']}
        </div>
        <div class="implication-box">
            <strong>💡 Business Implication:</strong> {insights['implication']}
            <br><small><strong>Data Source:</strong> {insights['data_backing']}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Market opportunity data not available with current filters")
    
    # AI Insights Section
    st.markdown("## 🧠 AI Insights with Survey Data Rationale")
    
    # Generate comprehensive insights
    all_insights = []
    
    if 'B2-A' in filtered_df.columns:
        ent_insights = generate_chart_insights('entertainment_importance', filtered_df, {
            'country': selected_country, 'purpose': selected_purpose, 'nationality': selected_nationality
        })
        all_insights.append({
            'title': '🎬 Entertainment Demand Analysis',
            'finding': ent_insights['finding'],
            'implication': ent_insights['implication'],
            'data_backing': ent_insights['data_backing']
        })
    
    if 'C2-A' in filtered_df.columns:
        pay_insights = generate_chart_insights('payment_willingness', filtered_df, {
            'country': selected_country, 'purpose': selected_purpose, 'nationality': selected_nationality
        })
        all_insights.append({
            'title': '💰 Monetization Opportunity',
            'finding': pay_insights['finding'], 
            'implication': pay_insights['implication'],
            'data_backing': pay_insights['data_backing']
        })
    
    mkt_insights = generate_chart_insights('market_opportunity', filtered_df, {
        'country': selected_country, 'purpose': selected_purpose, 'nationality': selected_nationality
    })
    all_insights.append({
        'title': '📊 Market Prioritization Strategy',
        'finding': mkt_insights['finding'],
        'implication': mkt_insights['implication'], 
        'data_backing': mkt_insights['data_backing']
    })
    
    # Display insights
    for insight in all_insights:
        with st.expander(insight['title'], expanded=True):
            col_finding, col_data = st.columns([2, 1])
            
            with col_finding:
                st.markdown(f"**Finding:** {insight['finding']}")
                st.markdown(f"**Implication:** {insight['implication']}")
            
            with col_data:
                st.info(f"**Data Source:** {insight['data_backing']}")
    
    # Data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    **Data Summary:**
    - Total responses: {len(df)}
    - Filtered responses: {len(filtered_df)}
    - Countries: {len(df['Country'].unique()) if 'Country' in df.columns else 0}
    - Survey questions: {len(df.columns)}
    """)

if __name__ == "__main__":
    main()
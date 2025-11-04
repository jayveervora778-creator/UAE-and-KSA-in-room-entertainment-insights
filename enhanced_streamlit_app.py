#!/usr/bin/env python3
"""
OSN Survey Analytics Dashboard - Enhanced Edition
Comprehensive survey analysis with AI/ML insights and elegant light theme
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
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re
import warnings

warnings.filterwarnings('ignore')

# Configure Plotly to use light theme globally
import plotly.io as pio
pio.templates.default = "plotly_white"

# Import enhanced data processor
try:
    from comprehensive_data_processor import ComprehensiveOSNProcessor
    print("✅ Imported ComprehensiveOSNProcessor")
except ImportError as e:
    st.error(f"Could not import ComprehensiveOSNProcessor: {e}")
    st.stop()

# Import refined themes
try:
    from refined_light_theme import apply_refined_light_theme
    from refined_black_killer import apply_refined_black_killer
    print("✅ Imported refined theme modules")
except ImportError as e:
    print(f"Warning: Could not import theme modules: {e}")
    apply_refined_light_theme = None
    apply_refined_black_killer = None

# Page configuration
st.set_page_config(
    page_title="OSN Survey Analytics - Enterprise Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply refined themes immediately
if apply_refined_light_theme:
    apply_refined_light_theme()
    print("✅ Applied refined light theme")

if apply_refined_black_killer:
    apply_refined_black_killer()
    print("✅ Applied refined black killer")

@st.cache_resource
def initialize_processor():
    """Initialize the data processor with caching"""
    try:
        processor = ComprehensiveOSNProcessor("data/survey_data.xlsx")
        success = processor.load_and_process_data()
        if success:
            return processor
        else:
            st.error("Failed to initialize data processor")
            return None
    except Exception as e:
        st.error(f"Error initializing processor: {e}")
        return None

@st.cache_data  
def get_cached_summary_stats(_processor):
    """Get cached summary statistics"""
    try:
        return _processor.get_summary_statistics()
    except Exception as e:
        st.error(f"Error getting summary stats: {e}")
        return {}

@st.cache_data
def get_cached_filtered_data(_processor, countries, nationalities, purposes):
    """Get cached filtered data"""
    try:
        filters = {
            'countries': countries,
            'nationalities': nationalities, 
            'visit_purposes': purposes
        }
        return _processor.get_filtered_data(filters)
    except Exception as e:
        st.error(f"Error getting filtered data: {e}")
        return pd.DataFrame()

@st.cache_data
def get_cached_question_responses(_processor, question_col, countries, nationalities, purposes):
    """Get cached question responses"""
    try:
        filters = {
            'countries': countries,
            'nationalities': nationalities,
            'visit_purposes': purposes  
        }
        return _processor.get_question_responses(question_col, filters)
    except Exception as e:
        st.error(f"Error getting question responses: {e}")
        return {"error": str(e)}

@st.cache_data
def get_cached_text_analysis(_processor, column_name, countries, nationalities, purposes):
    """Get cached text analysis"""
    try:
        filters = {
            'countries': countries,
            'nationalities': nationalities,
            'visit_purposes': purposes
        }
        return _processor.perform_text_analysis(column_name, filters)
    except Exception as e:
        st.error(f"Error in text analysis: {e}")
        return {"error": str(e)}

@st.cache_data  
def get_cached_business_insights(_processor, countries, nationalities, purposes):
    """Get cached business insights"""
    try:
        filters = {
            'countries': countries,
            'nationalities': nationalities,
            'visit_purposes': purposes
        }
        return _processor.generate_business_insights(filters)
    except Exception as e:
        st.error(f"Error generating business insights: {e}")
        return {}

def create_metric_card(title: str, value: str, delta: str = None):
    """Create elegant metric card"""
    delta_html = f"<p style='color: #10b981; font-size: 0.875rem; margin: 0;'>{delta}</p>" if delta else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        text-align: center;
        margin: 0.5rem 0;
    ">
        <h3 style="color: #1f2937; font-size: 2rem; font-weight: 700; margin: 0;">{value}</h3>
        <p style="color: #6b7280; font-size: 0.875rem; margin: 0.5rem 0 0 0; font-weight: 500;">{title}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_enhanced_chart(fig, title: str = None):
    """Apply consistent styling to charts"""
    if title:
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1f2937', 'family': 'Arial, sans-serif'}
            }
        )
    
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font={'color': '#1f2937'},
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#e5e7eb',
            borderwidth=1
        )
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='#f3f4f6',
        linecolor='#e5e7eb',
        tickcolor='#e5e7eb'
    )
    fig.update_yaxes(
        gridcolor='#f3f4f6',
        linecolor='#e5e7eb',
        tickcolor='#e5e7eb'
    )
    
    return fig

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 3rem; margin: 0; font-weight: 700;">📊 OSN Survey Analytics</h1>
        <p style="font-size: 1.25rem; margin: 0.5rem 0 0 0; opacity: 0.9;">Enterprise-Grade Guest Survey Intelligence Platform</p>
        <p style="font-size: 1rem; margin: 0.5rem 0 0 0; opacity: 0.8;">UAE & KSA Markets • AI-Powered Insights • Real-Time Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize processor
    processor = initialize_processor()
    if not processor:
        st.error("❌ Could not initialize data processor. Please check your data file.")
        st.stop()
    
    # Sidebar filters
    st.sidebar.markdown("## 🎯 Filter Controls")
    
    # Get filter options
    try:
        summary_stats = get_cached_summary_stats(processor)
        filter_options = summary_stats.get('filter_options', {})
    except Exception as e:
        st.sidebar.error(f"Error loading filter options: {e}")
        filter_options = {}
    
    # Country filter
    countries = filter_options.get('countries', ['UAE', 'KSA'])
    selected_countries = st.sidebar.multiselect(
        "📍 Select Countries",
        options=countries,
        default=countries,
        help="Filter responses by country"
    )
    
    # Nationality filter
    nationalities = filter_options.get('nationalities', [])
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Select Nationalities",
        options=nationalities[:10],  # Show top 10
        help="Filter by guest nationality"
    )
    
    # Visit purpose filter
    visit_purposes = filter_options.get('visit_purposes', [])
    selected_purposes = st.sidebar.multiselect(
        "✈️ Select Visit Purposes",
        options=visit_purposes[:10],  # Show top 10
        help="Filter by purpose of visit"
    )
    
    # Create filter dictionary
    filters = {
        'countries': selected_countries,
        'nationalities': selected_nationalities,
        'visit_purposes': selected_purposes
    }
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview Dashboard", 
        "🔍 Question Explorer", 
        "🧠 AI Text Analysis", 
        "💼 Business Insights", 
        "📊 Raw Data Browser"
    ])
    
    with tab1:
        overview_dashboard(processor, filters)
    
    with tab2:
        question_explorer(processor, filters)
    
    with tab3:
        ai_text_analysis(processor, filters)
    
    with tab4:
        business_insights(processor, filters)
    
    with tab5:
        raw_data_browser(processor, filters)

def overview_dashboard(processor, filters):
    """Main overview dashboard with key metrics and charts"""
    st.markdown("### 📊 Survey Overview & Key Metrics")
    
    try:
        # Get summary statistics using cached function
        stats = get_cached_summary_stats(processor)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card("Total Responses", f"{stats['total_responses']:,}")
        
        with col2:
            create_metric_card("Countries", str(stats['countries_represented']))
        
        with col3:
            create_metric_card("Survey Questions", str(stats['total_questions']))
        
        with col4:
            completion_rate = f"{stats['data_completeness']:.1f}%"
            create_metric_card("Data Completeness", completion_rate)
        
        st.markdown("---")
        
        # Country distribution chart  
        filtered_data = get_cached_filtered_data(
            processor, 
            selected_countries, 
            selected_nationalities, 
            selected_purposes
        )
        
        if len(filtered_data) > 0 and 'Country' in filtered_data.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Country distribution pie chart
                country_counts = filtered_data['Country'].value_counts()
                fig_pie = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Response Distribution by Country"
                )
                fig_pie = create_enhanced_chart(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Country comparison bar chart
                fig_bar = px.bar(
                    x=country_counts.index,
                    y=country_counts.values,
                    title="Response Count by Country",
                    labels={'x': 'Country', 'y': 'Number of Responses'}
                )
                fig_bar = create_enhanced_chart(fig_bar)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Sample data quality metrics
            st.markdown("### 📈 Data Quality Overview")
            
            quality_col1, quality_col2, quality_col3 = st.columns(3)
            
            with quality_col1:
                non_empty_cols = (filtered_data.notna().sum() > 0).sum()
                create_metric_card("Active Columns", str(non_empty_cols))
            
            with quality_col2:
                avg_response_rate = (filtered_data.notna().sum().sum() / (len(filtered_data) * len(filtered_data.columns))) * 100
                create_metric_card("Avg Response Rate", f"{avg_response_rate:.1f}%")
            
            with quality_col3:
                text_cols = len(processor.text_columns)
                create_metric_card("Text Response Fields", str(text_cols))
        
        else:
            st.warning("No data available for the selected filters.")
            
    except Exception as e:
        st.error(f"Error in overview dashboard: {e}")

def question_explorer(processor, filters):
    """Dynamic question explorer with visualization"""
    st.markdown("### 🔍 Survey Question Explorer")
    st.markdown("Explore individual survey questions and their response patterns.")
    
    try:
        # Get filtered data using cached function
        filtered_data = get_cached_filtered_data(
            processor,
            filters['countries'],
            filters['nationalities'], 
            filters['visit_purposes']
        )
        
        if len(filtered_data) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # Question selection
        available_questions = [col for col in filtered_data.columns if col != 'Country']
        
        selected_question = st.selectbox(
            "📋 Select a Survey Question",
            options=available_questions,
            help="Choose a question to explore its response patterns"
        )
        
        if selected_question:
            # Get question responses using cached function
            question_data = get_cached_question_responses(
                processor, 
                selected_question,
                filters['countries'],
                filters['nationalities'],
                filters['visit_purposes']
            )
            
            if 'error' in question_data:
                st.error(question_data['error'])
                return
            
            # Display question metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                create_metric_card("Total Responses", str(question_data['total_responses']))
            
            with col2:
                create_metric_card("Unique Answers", str(question_data['unique_responses']))
            
            with col3:
                response_rate = (question_data['total_responses'] / len(filtered_data)) * 100
                create_metric_card("Response Rate", f"{response_rate:.1f}%")
            
            # Response distribution visualization
            distribution = question_data['response_distribution']
            
            if len(distribution) > 0:
                st.markdown("#### 📊 Response Distribution")
                
                # Determine chart type based on data
                if len(distribution) <= 10:  # Use bar chart for few categories
                    fig = px.bar(
                        x=list(distribution.keys()),
                        y=list(distribution.values()),
                        title=f"Response Distribution: {selected_question}",
                        labels={'x': 'Response', 'y': 'Count'}
                    )
                else:  # Use histogram for many categories
                    fig = px.histogram(
                        x=list(distribution.keys()),
                        title=f"Response Distribution: {selected_question}"
                    )
                
                fig = create_enhanced_chart(fig)
                st.plotly_chart(fig, use_container_width=True)
                
                # Response details table
                if st.checkbox("Show Detailed Response Breakdown"):
                    response_df = pd.DataFrame([
                        {'Response': k, 'Count': v, 'Percentage': f"{(v/sum(distribution.values()))*100:.1f}%"}
                        for k, v in distribution.items()
                    ])
                    st.dataframe(response_df, use_container_width=True)
            
            # Sample responses
            if question_data.get('sample_responses'):
                with st.expander("📝 Sample Responses", expanded=False):
                    for i, response in enumerate(question_data['sample_responses'][:5], 1):
                        st.write(f"**Response {i}:** {response}")
        
    except Exception as e:
        st.error(f"Error in question explorer: {e}")

def ai_text_analysis(processor, filters):
    """AI-powered text analysis with NLP insights"""
    st.markdown("### 🧠 AI Text Analysis & Sentiment Intelligence")
    st.markdown("Advanced NLP analysis of open-ended survey responses using machine learning.")
    
    try:
        # Get available text columns
        text_columns = processor.text_columns
        
        if not text_columns:
            st.warning("No text response columns found for analysis.")
            return
        
        # Column selection
        selected_column = st.selectbox(
            "📝 Select Text Response Column",
            options=list(text_columns.keys()),
            help="Choose a text column for AI analysis"
        )
        
        if selected_column:
            with st.spinner("🔄 Performing AI analysis..."):
                # Perform text analysis using cached function
                analysis_results = get_cached_text_analysis(
                    processor,
                    selected_column,
                    filters['countries'],
                    filters['nationalities'],
                    filters['visit_purposes']
                )
                
                if 'error' in analysis_results:
                    st.error(analysis_results['error'])
                    return
                
                # Analysis metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    create_metric_card("Analyzed Responses", str(analysis_results['total_responses']))
                
                with col2:
                    sentiment = analysis_results['sentiment_analysis']
                    avg_polarity = sentiment['average_polarity']
                    sentiment_label = "Positive" if avg_polarity > 0.1 else "Negative" if avg_polarity < -0.1 else "Neutral"
                    create_metric_card("Overall Sentiment", sentiment_label)
                
                with col3:
                    keywords_count = len(analysis_results['top_keywords'])
                    create_metric_card("Key Topics", str(keywords_count))
                
                # Sentiment analysis visualization
                st.markdown("#### 🎯 Sentiment Analysis")
                
                sentiment_dist = sentiment['sentiment_distribution']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sentiment distribution pie chart
                    fig_sentiment = px.pie(
                        values=list(sentiment_dist.values()),
                        names=list(sentiment_dist.keys()),
                        title="Sentiment Distribution",
                        color_discrete_map={
                            'positive': '#10b981',
                            'neutral': '#6b7280',
                            'negative': '#ef4444'
                        }
                    )
                    fig_sentiment = create_enhanced_chart(fig_sentiment)
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                
                with col2:
                    # Sentiment metrics
                    st.markdown("**Sentiment Metrics:**")
                    st.metric("Average Polarity", f"{avg_polarity:.3f}", help="Range: -1 (negative) to +1 (positive)")
                    st.metric("Average Subjectivity", f"{sentiment['average_subjectivity']:.3f}", help="Range: 0 (objective) to 1 (subjective)")
                
                # Keyword analysis
                st.markdown("#### 🔑 Top Keywords & Topics")
                
                keywords = analysis_results['top_keywords']
                
                if keywords:
                    # Keywords chart
                    kw_data = keywords[:15]  # Top 15 keywords
                    fig_keywords = px.bar(
                        x=[kw['score'] for kw in kw_data],
                        y=[kw['keyword'] for kw in kw_data],
                        orientation='h',
                        title="Top Keywords by TF-IDF Score",
                        labels={'x': 'TF-IDF Score', 'y': 'Keyword'}
                    )
                    fig_keywords = create_enhanced_chart(fig_keywords)
                    st.plotly_chart(fig_keywords, use_container_width=True)
                
                # Theme clustering
                themes = analysis_results['themes_clusters']
                
                if themes:
                    st.markdown("#### 🎭 Response Themes")
                    
                    for theme_name, theme_data in themes.items():
                        with st.expander(f"📂 {theme_name} ({theme_data['sample_count']} responses)"):
                            st.markdown("**Sample responses in this theme:**")
                            for i, text in enumerate(theme_data['sample_texts'], 1):
                                st.write(f"{i}. {text}")
                
                # Sample responses
                if analysis_results.get('sample_responses'):
                    with st.expander("📄 Sample Text Responses", expanded=False):
                        for i, response in enumerate(analysis_results['sample_responses'][:10], 1):
                            st.write(f"**{i}.** {response}")
        
    except Exception as e:
        st.error(f"Error in AI text analysis: {e}")

def business_insights(processor, filters):
    """Generate strategic business insights for OSN"""
    st.markdown("### 💼 Strategic Business Intelligence")
    st.markdown("AI-generated insights and strategic recommendations for OSN market positioning.")
    
    try:
        with st.spinner("🔄 Generating business insights..."):
            insights = get_cached_business_insights(
                processor,
                filters['countries'],
                filters['nationalities'], 
                filters['visit_purposes']
            )
        
        # Market Overview
        st.markdown("#### 🌍 Market Overview")
        market = insights['market_overview']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_metric_card("Market Sample Size", f"{market['total_responses']:,}")
        
        with col2:
            adequacy = market['sample_size_adequacy']
            create_metric_card("Sample Quality", adequacy)
        
        with col3:
            countries = len(market['country_distribution'])
            create_metric_card("Markets Analyzed", str(countries))
        
        # Guest Preferences Analysis
        st.markdown("#### 🎯 Guest Preference Patterns")
        preferences = insights['guest_preferences']
        
        if preferences.get('preference_patterns'):
            pref_data = preferences['preference_patterns']
            
            # Create preference visualization
            if pref_data:
                # Show top preference categories
                pref_items = list(pref_data.items())[:3]  # Top 3 preference categories
                
                for pref_name, pref_values in pref_items:
                    if isinstance(pref_values, dict) and 'average_score' in pref_values:
                        st.metric(
                            f"📊 {pref_name}", 
                            f"{pref_values['average_score']:.2f}/5.0",
                            help="Average satisfaction score"
                        )
        
        # Entertainment Insights
        st.markdown("#### 🎬 Entertainment & Content Insights")
        entertainment = insights['entertainment_insights']
        
        if entertainment.get('entertainment_usage_patterns'):
            st.write("**Top Entertainment Preferences:**")
            for pattern_name, pattern_data in list(entertainment['entertainment_usage_patterns'].items())[:3]:
                if pattern_data:
                    top_choice = max(pattern_data.items(), key=lambda x: x[1])
                    st.write(f"• **{pattern_name}**: {top_choice[0]} ({top_choice[1]} responses)")
        
        # Technology Adoption
        st.markdown("#### 💻 Technology Adoption Patterns")
        tech = insights['technology_adoption']
        
        if tech.get('technology_adoption_patterns'):
            st.write("**Digital Engagement Insights:**")
            readiness = tech.get('digital_readiness', 'Assessment in progress')
            st.info(f"📱 {readiness}")
        
        # Strategic Recommendations
        st.markdown("#### 🚀 Strategic Recommendations for OSN")
        recommendations = insights['strategic_recommendations']
        
        for i, recommendation in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {recommendation}")
        
        # Competitive Analysis
        st.markdown("#### 🏆 Competitive Positioning")
        competitive = insights['competitive_positioning']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Key Selection Factors:**")
            factors = competitive.get('key_selection_factors', {})
            for factor_name, factor_data in list(factors.items())[:3]:
                if factor_data:
                    top_factor = max(factor_data.items(), key=lambda x: x[1])
                    st.write(f"• {top_factor[0]}: {top_factor[1]} mentions")
        
        with col2:
            st.markdown("**🔍 Competitive Advantages:**")
            advantages = competitive.get('competitive_advantages', [])
            for advantage in advantages[:3]:
                st.write(f"• {advantage}")
        
        # Export insights
        if st.button("📊 Generate Detailed Report"):
            st.success("🎯 Detailed business intelligence report would be generated here for OSN leadership team.")
    
    except Exception as e:
        st.error(f"Error generating business insights: {e}")

def raw_data_browser(processor, filters):
    """Browse and export raw survey data"""
    st.markdown("### 📊 Raw Data Browser & Export")
    st.markdown("Explore the complete survey dataset with filtering and export capabilities.")
    
    try:
        # Get filtered data using cached function
        filtered_data = get_cached_filtered_data(
            processor,
            filters['countries'],
            filters['nationalities'],
            filters['visit_purposes']
        )
        
        if len(filtered_data) == 0:
            st.warning("No data available for the selected filters.")
            return
        
        # Data overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_metric_card("Filtered Rows", f"{len(filtered_data):,}")
        
        with col2:
            create_metric_card("Total Columns", str(len(filtered_data.columns)))
        
        with col3:
            memory_usage = filtered_data.memory_usage(deep=True).sum() / 1024 / 1024
            create_metric_card("Data Size", f"{memory_usage:.1f} MB")
        
        # Column information
        st.markdown("#### 📋 Column Information")
        
        col_info = []
        for col in filtered_data.columns:
            col_info.append({
                'Column': col,
                'Data Type': str(filtered_data[col].dtype),
                'Non-Null Count': filtered_data[col].notna().sum(),
                'Unique Values': filtered_data[col].nunique(),
                'Sample Value': str(filtered_data[col].dropna().iloc[0]) if len(filtered_data[col].dropna()) > 0 else 'N/A'
            })
        
        col_df = pd.DataFrame(col_info)
        st.dataframe(col_df, use_container_width=True)
        
        # Data preview
        st.markdown("#### 👁️ Data Preview")
        
        # Show sample options
        sample_size = st.slider("Preview Rows", 5, min(100, len(filtered_data)), 20)
        show_columns = st.multiselect(
            "Select Columns to Display",
            options=filtered_data.columns.tolist(),
            default=filtered_data.columns.tolist()[:10]  # Show first 10 by default
        )
        
        if show_columns:
            preview_data = filtered_data[show_columns].head(sample_size)
            st.dataframe(preview_data, use_container_width=True)
        
        # Export options
        st.markdown("#### 📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download CSV"):
                csv = filtered_data.to_csv(index=False)
                st.download_button(
                    label="💾 Download Filtered Data (CSV)",
                    data=csv,
                    file_name=f"osn_survey_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Download Excel"):
                # For Excel export, we'd need to use BytesIO
                st.info("Excel export functionality would be implemented here")
        
        with col3:
            if st.button("🔍 Generate Summary"):
                st.info("Detailed data summary report would be generated here")
        
    except Exception as e:
        st.error(f"Error in raw data browser: {e}")

if __name__ == "__main__":
    main()
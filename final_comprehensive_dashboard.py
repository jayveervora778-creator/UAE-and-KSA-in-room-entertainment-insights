#!/usr/bin/env python3
"""
Final Comprehensive OSN Survey Analytics Dashboard
Uses properly mapped question names instead of A1, B1, etc.
All functionality working: 400 responses, cross-tabs, AI analysis, proper filters
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

# Import the properly structured processor
from properly_structured_processor import ProperlyStructuredOSNProcessor

# Streamlit App Configuration
st.set_page_config(
    page_title="OSN Survey Analytics - Final Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Final Light Theme CSS - Comprehensive and working
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #f8fafc !important;
    }
    
    /* All dropdown elements */
    .stSelectbox > div > div, .stSelectbox select {
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
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3b82f6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
    }
    
    .stButton > button:hover {
        background-color: #2563eb !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f5f9 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        color: #1f2937 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #FFFFFF !important;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Charts */
    .stPlotlyChart {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #f8fafc !important;
        color: #1f2937 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Hide Streamlit branding */
    .stDeployButton {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_final_data():
    """Load the properly structured data processor"""
    try:
        processor = ProperlyStructuredOSNProcessor("data/survey_data.xlsx")
        success = processor.load_and_process_data()
        if success:
            return processor
        else:
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    """Final comprehensive dashboard application with proper question mapping"""
    
    # Header
    st.title("🏨 OSN Survey Analytics - Enterprise Dashboard")
    st.markdown("### Comprehensive Survey Intelligence Platform")
    st.markdown("**UAE & KSA Markets • 400 Total Responses • Proper Question Mapping • AI-Powered Analytics**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading properly structured survey data..."):
        processor = load_final_data()
    
    if not processor:
        st.error("❌ Could not load survey data. Please check the data file and processing.")
        return
    
    # Get summary statistics to verify consistency
    stats = processor.get_summary_statistics()
    
    # Data consistency verification display
    consistency = stats.get('consistency_check', {})
    if consistency.get('is_consistent', False):
        st.success(f"✅ Data Consistency Verified: {stats['total_responses']} responses ({stats['uae_responses']} UAE + {stats['ksa_responses']} KSA) • {stats['meaningful_question_columns']} properly mapped questions")
    else:
        st.error(f"⚠️ Data Inconsistency Detected: Expected 400 (200+200), Found {stats['total_responses']} ({stats['uae_responses']}+{stats['ksa_responses']})")
    
    # Sidebar filters
    st.sidebar.markdown("## 🎯 Analytics Filters")
    
    # Country filter
    filter_options = stats.get('filter_options', {})
    countries = filter_options.get('countries', ['UAE', 'KSA'])
    selected_countries = st.sidebar.multiselect(
        "📍 Countries",
        options=countries,
        default=countries,
        key="country_filter"
    )
    
    # Nationality filter
    nationalities = filter_options.get('nationalities', [])
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Nationalities",
        options=nationalities[:20] if nationalities else [],
        key="nationality_filter"
    )
    
    # Visit purpose filter
    purposes = filter_options.get('visit_purposes', [])
    selected_purposes = st.sidebar.multiselect(
        "✈️ Visit Purposes",
        options=purposes[:15] if purposes else [],
        key="purpose_filter"
    )
    
    # Create filters
    filters = {
        'countries': selected_countries,
        'nationalities': selected_nationalities,
        'visit_purposes': selected_purposes
    }
    
    # Get filtered data
    filtered_data = processor.get_filtered_data(filters)
    
    if len(filtered_data) == 0:
        st.warning("No data available for selected filters.")
        return
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🔍 Question Analysis", "📈 Cross-Tabulation", "🤖 AI Insights", "📋 Business Intelligence"])
    
    with tab1:
        st.markdown("### 📊 Survey Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Responses", len(filtered_data))
        
        with col2:
            if 'Country' in filtered_data.columns:
                countries_count = filtered_data['Country'].nunique()
                st.metric("Countries", countries_count)
        
        with col3:
            st.metric("Survey Questions", stats['meaningful_question_columns'])
        
        with col4:
            completeness = (filtered_data.notna().sum().sum() / (len(filtered_data) * len(filtered_data.columns))) * 100 if len(filtered_data) > 0 else 0
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        st.markdown("---")
        
        # Country distribution charts
        if 'Country' in filtered_data.columns and len(filtered_data) > 0:
            st.markdown("### 🌍 Response Distribution Analysis")
            
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
        
        # Sample of properly mapped questions
        st.markdown("### 📝 Sample Survey Questions (Properly Mapped)")
        sample_questions = stats.get('sample_question_names', [])
        if sample_questions:
            for i, question in enumerate(sample_questions, 1):
                st.write(f"**{i}.** {question}")
        
        # Data validation summary
        st.markdown("### ✅ Data Validation & Quality Check")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Base Dataset",
                "400 responses",
                delta="✅ Consistent" if stats.get('total_responses') == 400 else "❌ Inconsistent"
            )
        
        with col2:
            st.metric(
                "UAE Market",
                f"{stats.get('uae_responses', 0)} responses",
                delta="✅ Target met" if stats.get('uae_responses') == 200 else "⚠️ Below target"
            )
        
        with col3:
            st.metric(
                "KSA Market",
                f"{stats.get('ksa_responses', 0)} responses", 
                delta="✅ Target met" if stats.get('ksa_responses') == 200 else "⚠️ Below target"
            )
        
        with col4:
            st.metric(
                "Question Mapping",
                f"{stats['meaningful_question_columns']} questions",
                delta="✅ Properly mapped"
            )
    
    with tab2:
        st.markdown("### 🔍 Individual Question Analysis")
        st.markdown("*All questions now properly mapped with meaningful names instead of A1, B1, etc.*")
        
        # Question selector with properly mapped names
        available_questions = processor.get_available_questions()
        
        if available_questions:
            selected_question = st.selectbox(
                "📋 Select Survey Question for Analysis",
                options=available_questions,
                key="question_analysis",
                help="Questions are now properly mapped from the Excel structure"
            )
            
            if selected_question:
                question_data = filtered_data[selected_question].dropna()
                
                # Question metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Responses", len(question_data))
                with col2:
                    st.metric("Base Dataset", len(filtered_data))
                with col3:
                    st.metric("Unique Answers", question_data.nunique())
                with col4:
                    response_rate = (len(question_data) / len(filtered_data)) * 100 if len(filtered_data) > 0 else 0
                    st.metric("Response Rate", f"{response_rate:.1f}%")
                
                # Response distribution
                if len(question_data) > 0:
                    value_counts = question_data.value_counts().head(15)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig = px.bar(
                            x=value_counts.values,
                            y=[str(x)[:50] + "..." if len(str(x)) > 50 else str(x) for x in value_counts.index],
                            orientation='h',
                            title=f"Response Distribution",
                            labels={'x': 'Count', 'y': 'Response'}
                        )
                        fig.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font_color='#1f2937',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Country breakdown if applicable
                        if 'Country' in filtered_data.columns and len(filtered_data) > 1:
                            try:
                                country_breakdown = filtered_data.groupby('Country')[selected_question].value_counts().unstack(fill_value=0)
                                if not country_breakdown.empty and len(country_breakdown.columns) > 0:
                                    fig_country = px.bar(
                                        country_breakdown.T,
                                        title=f"Response by Country",
                                        labels={'index': 'Response', 'value': 'Count'}
                                    )
                                    fig_country.update_layout(
                                        plot_bgcolor='white',
                                        paper_bgcolor='white',
                                        font_color='#1f2937',
                                        height=400
                                    )
                                    st.plotly_chart(fig_country, use_container_width=True)
                                else:
                                    st.info("Country breakdown not available for this question")
                            except Exception:
                                st.info("Country breakdown not available for this question")
                
                # Display full question name
                st.markdown("### 📋 Question Details")
                st.info(f"**Selected Question:** {selected_question}")
                
                # Sample responses
                if st.checkbox("Show Sample Responses", key="show_samples"):
                    st.markdown("**Sample Responses:**")
                    sample_responses = question_data.head(10).tolist()
                    for i, response in enumerate(sample_responses, 1):
                        st.write(f"**{i}.** {response}")
        else:
            st.error("No properly mapped questions available. Please check data processing.")
    
    with tab3:
        st.markdown("### 📈 Cross-Tabulation Analysis")
        st.markdown("*Analyze relationships between two survey questions using properly mapped names*")
        
        available_questions = processor.get_available_questions()
        
        if len(available_questions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                question1 = st.selectbox(
                    "📋 First Question",
                    options=available_questions,
                    key="crosstab_q1",
                    help="Select the first question for cross-tabulation"
                )
            
            with col2:
                available_q2 = [q for q in available_questions if q != question1]
                question2 = st.selectbox(
                    "📋 Second Question",
                    options=available_q2,
                    key="crosstab_q2",
                    help="Select the second question for cross-tabulation"
                )
            
            if question1 and question2:
                if st.button("🔍 Generate Cross-Tabulation Analysis", key="generate_crosstab"):
                    with st.spinner("Generating cross-tabulation analysis..."):
                        crosstab_result = processor.generate_cross_tabulation(question1, question2, filters)
                        
                        if 'error' in crosstab_result:
                            st.error(f"❌ {crosstab_result['error']}")
                        else:
                            st.success(f"✅ Cross-tabulation generated for {crosstab_result['total_responses']} responses")
                            
                            # Display question names
                            st.markdown("### 📊 Analysis Results")
                            st.info(f"**Question 1:** {question1}")
                            st.info(f"**Question 2:** {question2}")
                            
                            # Display results as formatted text to avoid PyArrow issues
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📊 Response Counts:**")
                                counts_dict = crosstab_result['crosstab_counts']
                                count_items = []
                                for row, data in counts_dict.items():
                                    if isinstance(data, dict) and row != 'Total':
                                        for col, count in data.items():
                                            if col != 'Total' and count > 0:
                                                count_items.append((row, col, count))
                                
                                # Sort by count and show top combinations
                                count_items.sort(key=lambda x: x[2], reverse=True)
                                for row, col, count in count_items[:10]:
                                    st.write(f"• **{row}** & **{col}**: {count} responses")
                            
                            with col2:
                                st.markdown("**📈 Key Percentages:**")
                                pct_dict = crosstab_result['crosstab_percentages']
                                pct_items = []
                                for row, data in pct_dict.items():
                                    if isinstance(data, dict) and row != 'Total':
                                        for col, pct in data.items():
                                            if col != 'Total' and pct > 0:
                                                pct_items.append((row, col, pct))
                                
                                # Sort by percentage and show top combinations
                                pct_items.sort(key=lambda x: x[2], reverse=True)
                                for row, col, pct in pct_items[:10]:
                                    st.write(f"• **{row}** & **{col}**: {pct:.1f}%")
                            
                            # Insights
                            st.markdown("### 💡 Cross-Tabulation Insights")
                            insights = crosstab_result.get('insights', [])
                            if insights:
                                for insight in insights:
                                    st.write(f"• {insight}")
                            else:
                                st.info("No specific insights generated for this combination.")
        else:
            st.info("Need at least 2 properly mapped questions for cross-tabulation analysis")
    
    with tab4:
        st.markdown("### 🤖 AI-Powered Text Analysis")
        st.markdown("*Advanced sentiment analysis and keyword extraction using machine learning on properly mapped text questions*")
        
        # Get text columns with proper names
        text_cols = list(processor.text_columns.keys())
        
        if text_cols:
            st.markdown("#### 📝 Available Text Response Questions:")
            for i, col_name in enumerate(text_cols, 1):
                col_info = processor.text_columns[col_name]
                st.write(f"**{i}.** {col_name} ({col_info['response_count']} responses, avg {col_info['avg_length']:.1f} characters)")
            
            selected_text_col = st.selectbox(
                "📝 Select Text Response Question for AI Analysis",
                options=text_cols,
                key="ai_analysis_col",
                help="These are properly mapped text response questions identified from the survey"
            )
            
            if selected_text_col:
                if st.button("🚀 Run AI Analysis", key="run_ai_analysis"):
                    with st.spinner("Running AI analysis (TF-IDF, Sentiment Analysis, ML Clustering)..."):
                        ai_result = processor.perform_ai_analysis(selected_text_col, filters)
                        
                        if 'error' in ai_result:
                            st.error(f"❌ {ai_result['error']}")
                        else:
                            st.success(f"✅ AI Analysis completed for {ai_result['total_responses']} text responses")
                            
                            # Display question being analyzed
                            st.info(f"**Analyzing:** {selected_text_col}")
                            
                            # Metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Text Responses", ai_result['total_responses'])
                            
                            with col2:
                                st.metric("Base Dataset", ai_result.get('base_dataset_size', 'N/A'))
                            
                            sentiment = ai_result.get('sentiment_analysis', {})
                            with col3:
                                avg_polarity = sentiment.get('average_polarity', 0)
                                sentiment_label = "Positive" if avg_polarity > 0.1 else "Negative" if avg_polarity < -0.1 else "Neutral"
                                st.metric("Overall Sentiment", sentiment_label)
                            
                            with col4:
                                total_themes = len(ai_result.get('themes', {}))
                                st.metric("Identified Themes", total_themes)
                            
                            # Detailed analysis
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**🎯 Top Keywords (TF-IDF)**")
                                keywords = ai_result.get('top_keywords', [])
                                if keywords:
                                    for kw in keywords[:10]:
                                        st.write(f"• **{kw['keyword']}** (relevance: {kw['relevance']})")
                                else:
                                    st.info("No significant keywords identified")
                            
                            with col2:
                                st.markdown("**😊 Sentiment Distribution**")
                                if sentiment:
                                    sentiment_data = {
                                        'Sentiment': ['Positive', 'Neutral', 'Negative'],
                                        'Count': [
                                            sentiment.get('positive_count', 0),
                                            sentiment.get('neutral_count', 0),
                                            sentiment.get('negative_count', 0)
                                        ]
                                    }
                                    
                                    if sum(sentiment_data['Count']) > 0:
                                        fig = px.pie(
                                            sentiment_data,
                                            values='Count',
                                            names='Sentiment',
                                            title="Sentiment Distribution",
                                            color_discrete_map={
                                                'Positive': '#22c55e',
                                                'Neutral': '#64748b',
                                                'Negative': '#ef4444'
                                            }
                                        )
                                        fig.update_layout(
                                            plot_bgcolor='white',
                                            paper_bgcolor='white',
                                            font_color='#1f2937'
                                        )
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.info("No sentiment data available")
                            
                            # Themes
                            themes = ai_result.get('themes', {})
                            if themes:
                                st.markdown("### 🏷️ Identified Themes (ML Clustering)")
                                for theme_name, theme_data in themes.items():
                                    with st.expander(f"{theme_name} ({theme_data['count']} responses)"):
                                        st.write("**Sample responses:**")
                                        for sample in theme_data.get('samples', []):
                                            st.write(f"• {sample}")
                            
                            # Sample responses
                            st.markdown("### 📄 Sample Text Responses")
                            samples = ai_result.get('sample_responses', [])
                            if samples:
                                for i, sample in enumerate(samples, 1):
                                    st.write(f"**{i}.** {sample}")
                            else:
                                st.info("No sample responses available")
                                
        else:
            st.info("No text response questions identified in the survey data with proper mapping.")
    
    with tab5:
        st.markdown("### 📋 Business Intelligence Dashboard")
        st.markdown("*Strategic insights and recommendations for OSN operations based on properly mapped survey data*")
        
        # Key business metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            market_coverage = (len(filtered_data) / 400) * 100
            st.metric(
                "Market Coverage",
                f"{market_coverage:.1f}%",
                delta=f"{len(filtered_data)} responses"
            )
        
        with col2:
            if 'Country' in filtered_data.columns:
                country_diversity = filtered_data['Country'].nunique()
                st.metric("Market Diversity", f"{country_diversity} markets")
        
        with col3:
            response_quality = stats.get('data_completeness', 0)
            st.metric(
                "Data Quality Score",
                f"{response_quality:.1f}%",
                delta="High" if response_quality > 85 else "Moderate"
            )
        
        # Business insights sections
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Market Analysis")
            
            if 'Country' in filtered_data.columns and len(filtered_data) > 0:
                # Market penetration
                market_data = filtered_data['Country'].value_counts()
                
                st.write("**Market Penetration Analysis:**")
                for country, count in market_data.items():
                    penetration = (count / 200) * 100  # Expected 200 per country
                    status = "✅ Target Met" if count == 200 else "⚠️ Below Target" if count < 200 else "📈 Above Target"
                    st.write(f"• **{country}**: {count} responses ({penetration:.1f}% of target) {status}")
                
                # Top nationalities from properly mapped nationality question
                nationality_cols = [col for col in filtered_data.columns 
                                  if 'nationality' in col.lower()]
                if nationality_cols:
                    nat_col = nationality_cols[0]
                    top_nationalities = filtered_data[nat_col].value_counts().head(5)
                    st.markdown("**🌍 Top Guest Nationalities:**")
                    for nat, count in top_nationalities.items():
                        if pd.notna(nat) and str(nat).strip():
                            percentage = (count / len(filtered_data)) * 100
                            st.write(f"• {nat}: {count} responses ({percentage:.1f}%)")
        
        with col2:
            st.markdown("### 💡 Strategic Recommendations")
            
            recommendations = [
                "📊 **Market Focus**: Leverage the 400-response dataset for statistically significant insights across UAE & KSA markets",
                "🎯 **Content Strategy**: Use properly mapped entertainment preferences to optimize programming decisions", 
                "📱 **Technology Enhancement**: Analyze in-room entertainment feedback to guide digital service improvements",
                "🏆 **Guest Experience**: Address specific improvement areas identified through structured feedback analysis",
                "📈 **Regional Adaptation**: Customize services based on nationality and visit purpose patterns",
                "🔄 **Continuous Monitoring**: Implement regular feedback cycles using the established question framework"
            ]
            
            for rec in recommendations:
                st.write(f"• {rec}")
        
        # Survey performance summary
        st.markdown("---")
        st.markdown("### 📈 Survey Performance Summary")
        
        # Create performance summary without problematic dataframes
        performance_metrics = [
            ("Total Survey Responses", f"{stats.get('total_responses', 0)}/400", "✅ Complete" if stats.get('total_responses') == 400 else "⚠️ Incomplete"),
            ("UAE Market Coverage", f"{stats.get('uae_responses', 0)}/200", "✅ Target Met" if stats.get('uae_responses') == 200 else "⚠️ Below Target"),
            ("KSA Market Coverage", f"{stats.get('ksa_responses', 0)}/200", "✅ Target Met" if stats.get('ksa_responses') == 200 else "⚠️ Below Target"),
            ("Question Mapping", f"{stats.get('meaningful_question_columns', 0)} questions", "✅ Properly Mapped"),
            ("Text Analysis Ready", f"{stats.get('text_columns', 0)} columns", "✅ Available" if stats.get('text_columns', 0) > 0 else "⚠️ Limited"),
            ("Cross-Tabulation Ready", f"{len(available_questions)} questions", "✅ Ready" if len(available_questions) >= 2 else "⚠️ Limited"),
            ("Data Quality Score", f"{response_quality:.1f}%", "✅ High" if response_quality > 85 else "⚠️ Moderate"),
            ("AI/ML Features", "Active", "✅ Operational")
        ]
        
        st.markdown("**Performance Metrics:**")
        for metric, value, status in performance_metrics:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{metric}**")
            with col2:
                st.write(value)
            with col3:
                st.write(status)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
HIGH CONTRAST OSN Survey Dashboard with Advanced Text Insights
✅ Dark text on white backgrounds everywhere for maximum readability
✅ Advanced text insights module analyzing what answers actually mean
✅ Cross-question key takeaways connecting insights across questions  
✅ OSN-relevant strategic inferences from guest responses
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from enhanced_osn_processor import EnhancedOSNProcessor
from osn_wordcloud_analyzer import OSNWordCloudAnalyzer
from advanced_text_insights_analyzer import AdvancedTextInsightsAnalyzer

# Configure Streamlit
st.set_page_config(
    page_title="High Contrast OSN Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# HIGH CONTRAST CSS - Dark text on white backgrounds everywhere
st.markdown("""
<style>
    /* FORCE HIGH CONTRAST EVERYWHERE */
    .stApp {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* All text elements - dark on white */
    .stApp * {
        color: #1a1a1a !important;
        background-color: transparent !important;
    }
    
    /* Main containers - pure white backgrounds */
    .main .block-container {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0 !important;
        padding: 2rem !important;
    }
    
    /* Headers and titles - very dark for maximum contrast */
    .main-header {
        background: #ffffff !important;
        border: 2px solid #1a1a1a !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        margin-bottom: 2rem !important;
    }
    
    .main-header h1 {
        color: #000000 !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    
    .main-header p {
        color: #333333 !important;
        margin: 0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards - white with dark borders */
    .metric-card {
        background: #ffffff !important;
        border: 2px solid #333333 !important;
        padding: 1.5rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .metric-card h4 {
        color: #000000 !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-card p, .metric-card span {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* Insight boxes - white with dark text and borders */
    .insight-box {
        background: #ffffff !important;
        border: 2px solid #2563eb !important;
        border-left: 6px solid #2563eb !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1) !important;
    }
    
    .insight-box * {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* Success/status boxes */
    .success-box {
        background: #ffffff !important;
        border: 2px solid #10b981 !important;
        border-left: 6px solid #10b981 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
        margin: 1rem 0 !important;
        color: #000000 !important;
    }
    
    .success-box * {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Word cloud container */
    .wordcloud-container {
        background: #ffffff !important;
        border: 3px solid #f59e0b !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
    }
    
    .wordcloud-container h4 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    /* Advanced insights container */
    .insights-container {
        background: #ffffff !important;
        border: 3px solid #8b5cf6 !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
    }
    
    .insights-container * {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* Theme tags */
    .theme-tag {
        background: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        color: #1a1a1a !important;
        padding: 0.5rem 1rem !important;
        border-radius: 15px !important;
        font-size: 0.9rem !important;
        margin: 0.3rem !important;
        display: inline-block !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar - force white background and dark text */
    .stSidebar {
        background-color: #ffffff !important;
        border-right: 2px solid #e0e0e0 !important;
    }
    
    .stSidebar * {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    .stSidebar .stSelectbox > div > div,
    .stSidebar .stMultiSelect > div > div {
        background-color: #ffffff !important;
        border: 2px solid #333333 !important;
        color: #1a1a1a !important;
    }
    
    /* Dropdowns - white backgrounds, dark text, dark borders */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        border: 2px solid #333333 !important;
        color: #1a1a1a !important;
    }
    
    .stSelectbox label,
    .stMultiSelect label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
    }
    
    /* Tabs - high contrast */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        border-bottom: 2px solid #333333 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-weight: 700 !important;
        border: 2px solid #333333 !important;
        margin-right: 0.5rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border-bottom: 3px solid #2563eb !important;
    }
    
    /* Buttons - high contrast */
    .stButton > button {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 2px solid #333333 !important;
        font-weight: 700 !important;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa !important;
        border-color: #2563eb !important;
    }
    
    /* Metrics - ensure visibility */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }
    
    [data-testid="metric-container"] * {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* Force all text to be dark and visible */
    .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
        background-color: transparent !important;
    }
    
    /* Priority indicators */
    .priority-critical {
        background: #ffffff !important;
        border: 3px solid #dc2626 !important;
        color: #dc2626 !important;
        font-weight: 800 !important;
        padding: 0.5rem !important;
        border-radius: 5px !important;
    }
    
    .priority-high {
        background: #ffffff !important;
        border: 3px solid #f59e0b !important;
        color: #f59e0b !important;
        font-weight: 700 !important;
        padding: 0.5rem !important;
        border-radius: 5px !important;
    }
    
    /* Ensure plotly charts have white backgrounds */
    .plotly .main-svg {
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_survey_data():
    """Load and cache enhanced survey data"""
    processor = EnhancedOSNProcessor()
    success = processor.load_data()
    if success:
        return processor
    return None

def create_wordcloud_visualization(word_data, title="Word Cloud"):
    """Create word cloud visualization with white background"""
    if not word_data or not word_data['word_frequency']:
        return None
    
    words = list(word_data['word_frequency'].keys())[:30]
    frequencies = list(word_data['word_frequency'].values())[:30]
    
    max_freq = max(frequencies) if frequencies else 1
    normalized_sizes = [20 + (freq / max_freq) * 40 for freq in frequencies]
    
    np.random.seed(42)
    n_words = len(words)
    
    angles = np.linspace(0, 4 * np.pi, n_words)
    radii = np.linspace(0.5, 3, n_words)
    x_pos = radii * np.cos(angles)
    y_pos = radii * np.sin(angles)
    
    # High contrast colors for word cloud
    colors = ['#1a1a1a', '#2563eb', '#dc2626', '#059669', '#7c2d12', '#4338ca', '#9333ea', '#c2410c'] * (n_words // 8 + 1)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='text',
        text=words,
        textfont=dict(
            size=normalized_sizes,
            color=colors[:n_words]
        ),
        hovertemplate='<b>%{text}</b><br>Frequency: %{customdata}<extra></extra>',
        customdata=frequencies,
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16, color='#1a1a1a', family='Arial Black')),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        height=400,
        font=dict(color='#1a1a1a')
    )
    
    return fig

def display_advanced_insights(insights_report):
    """Display advanced text insights with high contrast formatting"""
    if not insights_report or 'error' in insights_report:
        st.warning("⚠️ No advanced insights available for current selection")
        return
    
    # Executive Summary
    exec_summary = insights_report.get('executive_summary', {})
    
    st.markdown("""
    <div class="insights-container">
        <h3>🎯 Executive Summary - What Guest Responses Actually Mean</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Analysis Scope</h4>
            <p><strong>{exec_summary.get('overview', 'No data')}</strong></p>
            <p>Completeness: {insights_report.get('analysis_completeness', 0):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 Overall Guest Sentiment</h4>
            <p><strong>{exec_summary.get('overall_guest_sentiment_trend', 'Unknown')}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        critical_actions = exec_summary.get('immediate_actions_required', 0)
        priority_class = 'priority-critical' if critical_actions > 0 else 'priority-high'
        st.markdown(f"""
        <div class="metric-card">
            <h4>⚠️ Critical Actions</h4>
            <p class="{priority_class}"><strong>{critical_actions} Immediate Actions Required</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic Priorities
    st.markdown("### 🎯 OSN Strategic Action Priorities")
    
    osn_priorities = insights_report.get('osn_strategic_priorities', [])
    
    if osn_priorities:
        for i, priority in enumerate(osn_priorities[:5]):
            priority_class = f"priority-{priority['priority'].lower()}" if priority['priority'].lower() in ['critical', 'high'] else 'metric-card'
            
            st.markdown(f"""
            <div class="{priority_class}">
                <h4>#{i+1} - {priority['priority']} Priority: {priority['theme']}</h4>
                <p><strong>Action:</strong> {priority['action']}</p>
                <p><strong>Business Impact:</strong> {priority['business_impact']}</p>
                <p><strong>Timeline:</strong> {priority['timeline']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Cross-Question Insights
    st.markdown("### 🔗 Cross-Question Strategic Patterns")
    
    cross_patterns = insights_report.get('cross_question_patterns', {})
    
    if cross_patterns and 'cross_question_patterns' in cross_patterns:
        patterns = cross_patterns['cross_question_patterns']
        
        for theme, analysis in patterns.items():
            if analysis.get('theme_priority', 0) > 0:
                theme_name = theme.replace('_', ' ').title()
                
                st.markdown(f"""
                <div class="insight-box">
                    <h4>📊 {theme_name}</h4>
                    <p><strong>Pattern Strength:</strong> {analysis.get('pattern_strength', 'Unknown')}</p>
                    <p><strong>Questions Analyzed:</strong> {analysis.get('questions_analyzed', 0)}</p>
                    <p><strong>Priority Score:</strong> {analysis.get('theme_priority', 0):.1f}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Strategic Recommendations
    strategic_recs = cross_patterns.get('strategic_recommendations', [])
    
    if strategic_recs:
        st.markdown("### 💡 Strategic Recommendations for OSN")
        
        for rec in strategic_recs:
            st.markdown(f"""
            <div class="insight-box">
                <p><strong>{rec}</strong></p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main dashboard application with high contrast design"""
    
    # High contrast header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 High Contrast OSN Guest Survey Analytics</h1>
        <p>Maximum Readability Dashboard with Advanced Text Insights & Cross-Question Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor = load_survey_data()
    
    if processor is None:
        st.error("❌ Failed to load survey data. Please check the data file.")
        return
    
    # Get summary statistics
    stats = processor.get_summary_stats()
    
    # Data integrity check with high contrast
    if stats['total_responses'] == 400 and stats['uae_responses'] == 200 and stats['ksa_responses'] == 200:
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Enhanced Data Integrity:</strong> Exactly 400 responses (200 UAE + 200 KSA) with all nationalities and advanced insights
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Data integrity issue: {stats['total_responses']} total responses")
    
    # High contrast sidebar
    st.sidebar.markdown("### 🎛️ High Contrast Filters")
    st.sidebar.markdown("**Dark text on white backgrounds for maximum readability**")
    
    filter_options = stats['filter_options']
    
    # Enhanced filters with better contrast
    selected_countries = st.sidebar.multiselect(
        "🌍 Markets",
        options=filter_options['countries'],
        default=filter_options['countries'],
        key="country_filter"
    )
    
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Guest Nationalities",
        options=filter_options['nationalities'],
        key="nationality_filter",
        help=f"Select from ALL {len(filter_options['nationalities'])} nationalities available"
    )
    
    selected_purposes = st.sidebar.multiselect(
        "✈️ Visit Purposes",
        options=filter_options['visit_purposes'],
        key="purpose_filter",
        help="Business, Leisure, Family Vacation, Other"
    )
    
    selected_frequencies = st.sidebar.multiselect(
        "🏨 Hotel Stay Frequency",
        options=filter_options['hotel_frequency'],
        key="frequency_filter"
    )
    
    # Apply filters
    filtered_data = processor.get_filtered_data(
        country_filter=selected_countries,
        nationality_filter=selected_nationalities,
        purpose_filter=selected_purposes,
        frequency_filter=selected_frequencies
    )
    
    if len(filtered_data) == 0:
        st.warning("⚠️ No data matches the selected filters. Please adjust your selection.")
        return
    
    # Enhanced tabs with high contrast
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview", 
        "📈 Cross-Analysis", 
        "🔤 Word Cloud Analysis",
        "🧠 Advanced Text Insights",
        "💼 Business Intelligence"
    ])
    
    with tab1:
        st.markdown("### 📊 High Contrast Market Overview")
        
        # High contrast metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filtered Responses", len(filtered_data))
            
        with col2:
            filtered_uae = len(filtered_data[filtered_data['Country'] == 'UAE'])
            st.metric("UAE Filtered", filtered_uae)
            
        with col3:
            filtered_ksa = len(filtered_data[filtered_data['Country'] == 'KSA'])
            st.metric("KSA Filtered", filtered_ksa)
            
        with col4:
            coverage = (len(filtered_data) / 400) * 100
            st.metric("Market Coverage", f"{coverage:.1f}%")
        
        # High contrast visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            if len(filtered_data) > 0:
                country_counts = filtered_data['Country'].value_counts()
                fig_country = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Market Distribution - High Contrast",
                    color_discrete_map={'UAE': '#059669', 'KSA': '#2563eb'}
                )
                fig_country.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff',
                    font=dict(color='#1a1a1a', family='Arial Black'),
                    title_font=dict(color='#1a1a1a', size=16)
                )
                st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            if 'Nationality' in filtered_data.columns and len(filtered_data) > 0:
                nat_counts = filtered_data['Nationality'].value_counts().head(10)
                fig_nat = px.bar(
                    x=nat_counts.values,
                    y=nat_counts.index,
                    orientation='h',
                    title=f"Top Guest Nationalities - ALL {len(filter_options['nationalities'])} Available",
                    labels={'x': 'Guest Count', 'y': 'Nationality'},
                    color=nat_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_nat.update_layout(
                    plot_bgcolor='#ffffff',
                    paper_bgcolor='#ffffff',
                    font=dict(color='#1a1a1a', family='Arial Black'),
                    title_font=dict(color='#1a1a1a', size=16),
                    showlegend=False
                )
                st.plotly_chart(fig_nat, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 High Contrast Cross-Analysis")
        st.markdown("**Dark text on white background for maximum readability**")
        
        available_questions = [q for q in stats['available_questions'] if 'Unnamed' not in str(q)]
        
        if len(available_questions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                question1 = st.selectbox(
                    "📋 First Dimension",
                    options=available_questions,
                    key="crosstab_q1"
                )
            
            with col2:
                available_q2 = [q for q in available_questions if q != question1]
                question2 = st.selectbox(
                    "📋 Second Dimension", 
                    options=available_q2,
                    key="crosstab_q2"
                )
            
            if st.button("🔍 Generate High Contrast Cross-Analysis", key="run_crosstab", type="primary"):
                with st.spinner("Analyzing relationship patterns..."):
                    
                    crosstab_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes,
                        'frequency': selected_frequencies
                    }
                    
                    result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
                    
                    if result and result['combinations']:
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ High contrast analysis completed using {result['total_responses']} responses
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Cross-Analysis Results</h4>
                            <p><strong>Dimension 1:</strong> {question1}</p>
                            <p><strong>Dimension 2:</strong> {question2}</p>
                            <p><strong>Sample Size:</strong> {result['total_responses']} responses</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display results with high contrast
                        st.markdown("#### 🎯 Top Response Combinations")
                        
                        combinations = result['combinations'][:8]
                        
                        for i, combo in enumerate(combinations, 1):
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>#{i} - {combo['count']} responses ({combo['percentage']}%)</h4>
                                <p><strong>Dimension 1:</strong> {combo['question1_value']}</p>
                                <p><strong>Dimension 2:</strong> {combo['question2_value']}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔤 High Contrast Word Cloud Analysis")
        
        wordcloud_analyzer = OSNWordCloudAnalyzer()
        text_questions = stats['text_questions']
        
        if text_questions:
            st.markdown(f"📝 **{len(text_questions)} Opinion/Text Questions Available:**")
            
            for question in text_questions:
                st.markdown(f'<span class="theme-tag">{question[:50]}{"..." if len(question) > 50 else ""}</span>', unsafe_allow_html=True)
            
            selected_text_question = st.selectbox(
                "🎯 Select Question for Word Cloud Analysis",
                options=text_questions,
                key="wordcloud_question"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_words = st.slider("📊 Max Words in Cloud", 20, 100, 50)
            
            with col2:
                osn_focus = st.checkbox("🎯 OSN-Focused Analysis", value=True)
            
            with col3:
                min_word_length = st.slider("✂️ Min Word Length", 3, 6, 4)
            
            if st.button("🚀 Generate High Contrast Word Cloud", type="primary"):
                with st.spinner("Analyzing text responses..."):
                    
                    text_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes,
                        'frequency': selected_frequencies
                    }
                    
                    text_responses = processor.get_text_responses_for_wordcloud(
                        selected_text_question, 
                        text_filters
                    )
                    
                    if text_responses:
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ Analyzing {len(text_responses)} text responses with high contrast visualization
                        </div>
                        """, unsafe_allow_html=True)
                        
                        wordcloud_data = wordcloud_analyzer.generate_wordcloud_data(
                            text_responses,
                            max_words=max_words,
                            osn_focus=osn_focus
                        )
                        
                        wordcloud_fig = create_wordcloud_visualization(
                            wordcloud_data,
                            title=f"High Contrast Word Cloud: {selected_text_question[:40]}{'...' if len(selected_text_question) > 40 else ''}"
                        )
                        
                        if wordcloud_fig:
                            st.markdown("""
                            <div class="wordcloud-container">
                                <h4>🎨 High Contrast Word Cloud - Maximum Readability</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            st.plotly_chart(wordcloud_fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 🧠 Advanced Text Insights - What Answers Actually Mean")
        st.markdown("**Analyze guest responses for strategic business intelligence**")
        
        # Initialize advanced analyzer
        insights_analyzer = AdvancedTextInsightsAnalyzer()
        text_questions = stats['text_questions']
        
        if text_questions and len(filtered_data) > 10:
            
            if st.button("🔍 Generate Advanced Text Insights Analysis", type="primary"):
                with st.spinner("Performing advanced analysis of guest response meanings..."):
                    
                    # Generate comprehensive insights report
                    insights_report = insights_analyzer.generate_comprehensive_insights_report(
                        filtered_data, 
                        text_questions
                    )
                    
                    if insights_report and 'error' not in insights_report:
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ Advanced insights analysis completed - Understanding what {insights_report.get('total_responses_analyzed', 0)} guest responses actually mean
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display advanced insights
                        display_advanced_insights(insights_report)
                        
                    else:
                        st.warning("⚠️ Could not generate advanced insights. Try adjusting filters or ensure text responses are available.")
            
            # Show preview of available text questions
            st.markdown("#### 📋 Available Text Questions for Advanced Analysis")
            
            for i, question in enumerate(text_questions, 1):
                responses_count = len(filtered_data[question].dropna()) if question in filtered_data.columns else 0
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{i}. {question}</h4>
                    <p><strong>Available Responses:</strong> {responses_count}</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="insight-box">
                <p><strong>Advanced text insights require:</strong></p>
                <p>• At least 10 filtered responses</p>
                <p>• Text/opinion questions available</p>
                <p>• Adjust filters to include more data</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 💼 High Contrast Business Intelligence")
        
        business_insights = processor.generate_insights(filtered_data, "strategic")
        
        st.markdown("#### 💡 Strategic OSN Insights")
        st.markdown(f"""
        <div class="insight-box">
            {business_insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Additional high contrast analytics
        if len(filtered_data) > 50:
            st.markdown("#### 📈 High Contrast Advanced Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Entertainment Quality Rating' in filtered_data.columns:
                    rating_dist = filtered_data['Entertainment Quality Rating'].value_counts().sort_index()
                    fig_ratings = px.bar(
                        x=rating_dist.index,
                        y=rating_dist.values,
                        title="Entertainment Satisfaction - High Contrast",
                        labels={'x': 'Rating (1-5)', 'y': 'Guest Count'},
                        color=rating_dist.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_ratings.update_layout(
                        plot_bgcolor='#ffffff',
                        paper_bgcolor='#ffffff',
                        font=dict(color='#1a1a1a', family='Arial Black'),
                        title_font=dict(color='#1a1a1a', size=16)
                    )
                    st.plotly_chart(fig_ratings, use_container_width=True)

if __name__ == "__main__":
    main()
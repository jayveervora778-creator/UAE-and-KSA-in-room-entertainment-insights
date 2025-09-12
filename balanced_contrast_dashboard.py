#!/usr/bin/env python3
"""
BALANCED HIGH CONTRAST OSN Dashboard - FIXED VERSION
✅ Dark text on white backgrounds for readability
✅ Graphs and dropdowns work properly
✅ No aggressive CSS that breaks functionality
✅ Simple, clean, readable design
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
    page_title="Readable OSN Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# DARK TEXT ON WHITE BACKGROUNDS EVERYWHERE
st.markdown("""
<style>
    /* FORCE WHITE BACKGROUNDS AND DARK TEXT EVERYWHERE */
    .stApp {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    /* All containers - white backgrounds */
    .main .block-container {
        background-color: #ffffff !important;
    }
    
    /* Sidebar - white background, dark text */
    .stSidebar {
        background-color: #ffffff !important;
    }
    
    .stSidebar * {
        color: #2c3e50 !important;
        background-color: #ffffff !important;
    }
    
    /* Headers - dark text, white backgrounds */
    .main-header {
        background: #ffffff !important;
        border: 2px solid #34495e;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        color: #2c3e50 !important;
        font-weight: 800;
        margin: 0;
    }
    
    .main-header p {
        color: #34495e !important;
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* MAIN TEXT - DARK ON WHITE (BUT NOT CHART DATA) */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        background-color: #ffffff !important;
    }
    
    /* Main text elements - but NOT chart data labels */
    .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: #34495e !important;
        background-color: #ffffff !important;
    }
    
    /* Sidebar text */
    .stSidebar p, .stSidebar span, .stSidebar label {
        color: #2c3e50 !important;
        background-color: #ffffff !important;
    }
    
    /* Content boxes - white backgrounds, dark text */
    .metric-card {
        background: #ffffff !important;
        border: 1px solid #bdc3c7;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .metric-card h4 {
        color: #2c3e50 !important;
        font-weight: 700;
        background-color: #ffffff !important;
    }
    
    .metric-card p {
        color: #34495e !important;
        font-weight: 500;
        background-color: #ffffff !important;
    }
    
    /* Insight boxes - white backgrounds */
    .insight-box {
        background: #ffffff !important;
        border: 2px solid #3498db;
        border-left: 5px solid #3498db;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .insight-box h4, .insight-box p {
        color: #2c3e50 !important;
        font-weight: 500;
        background-color: #ffffff !important;
    }
    
    /* Success boxes - white backgrounds */
    .success-box {
        background: #ffffff !important;
        border: 2px solid #27ae60;
        border-left: 5px solid #27ae60;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box * {
        color: #27ae60 !important;
        font-weight: 600;
        background-color: #ffffff !important;
    }
    
    /* Word cloud container - white background */
    .wordcloud-container {
        background: #ffffff !important;
        border: 2px solid #f39c12;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .wordcloud-container h4 {
        color: #2c3e50 !important;
        font-weight: 700;
        background-color: #ffffff !important;
    }
    
    /* Advanced insights - white background */
    .insights-container {
        background: #ffffff !important;
        border: 2px solid #9b59b6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .insights-container * {
        color: #2c3e50 !important;
        font-weight: 500;
        background-color: #ffffff !important;
    }
    
    /* Theme tags - white background, dark text */
    .theme-tag {
        background: #ffffff !important;
        border: 1px solid #3498db;
        color: #2c3e50 !important;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 600;
    }
    
    /* Priority indicators - white backgrounds */
    .priority-critical {
        background: #ffffff !important;
        border: 2px solid #e74c3c;
        color: #e74c3c !important;
        font-weight: 700;
        padding: 0.5rem;
        border-radius: 5px;
    }
    
    .priority-high {
        background: #ffffff !important;
        border: 2px solid #f39c12;
        color: #f39c12 !important;
        font-weight: 600;
        padding: 0.5rem;
        border-radius: 5px;
    }
    
    /* DROPDOWNS - WHITE BACKGROUNDS, DARK TEXT */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 1px solid #bdc3c7 !important;
        color: #2c3e50 !important;
    }
    
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        border: 1px solid #bdc3c7 !important;
        color: #2c3e50 !important;
    }
    
    /* Dropdown containers */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    /* Dropdown menu backgrounds */
    .stSelectbox div[data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    
    .stMultiSelect div[data-baseweb="menu"] {
        background-color: #ffffff !important;
    }
    
    /* Individual dropdown options - white backgrounds */
    .stSelectbox div[data-baseweb="menu"] > ul > li {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    .stMultiSelect div[data-baseweb="menu"] > ul > li {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
    }
    
    /* Dropdown hover states - light gray on white */
    .stSelectbox div[data-baseweb="menu"] > ul > li:hover {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    .stMultiSelect div[data-baseweb="menu"] > ul > li:hover {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    /* Selected items - blue background with white text (only exception) */
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #3498db !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    /* Ensure all dropdown containers have white backgrounds */
    .stSelectbox div, .stMultiSelect div {
        background-color: #ffffff !important;
    }
    
    /* Dropdown arrows and icons - dark */
    .stSelectbox svg, .stMultiSelect svg {
        color: #2c3e50 !important;
    }
    
    /* Tabs - white backgrounds, dark text */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
    }
    
    /* Buttons - functional styling */
    .stButton > button {
        background-color: #3498db !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
    }
    
    .stButton > button:hover {
        background-color: #2980b9 !important;
        color: #ffffff !important;
    }
    
    .stButton > button:active {
        background-color: #21618c !important;
        color: #ffffff !important;
    }
    
    /* Metrics - white backgrounds */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }
    
    [data-testid="metric-container"] * {
        color: #2c3e50 !important;
        background-color: #ffffff !important;
        font-weight: 600;
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
    """Create word cloud visualization - SIMPLE VERSION"""
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
    
    # Simple, readable colors
    colors = ['#2c3e50', '#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#34495e', '#16a085'] * (n_words // 8 + 1)
    
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
    
    # Simple chart layout
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16, color='#2c3e50')),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400
    )
    
    return fig

def display_advanced_insights(insights_report):
    """Display advanced insights - SIMPLE VERSION"""
    if not insights_report or 'error' in insights_report:
        st.warning("⚠️ No advanced insights available for current selection")
        return
    
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

def main():
    """Main dashboard - SIMPLE AND FUNCTIONAL"""
    
    # Simple header
    st.markdown("""
    <div class="main-header">
        <h1>📊 OSN Guest Survey Analytics - Readable & Functional</h1>
        <p>Dark text on white background for maximum readability - graphs and dropdowns work properly</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor = load_survey_data()
    
    if processor is None:
        st.error("❌ Failed to load survey data. Please check the data file.")
        return
    
    # Get summary statistics
    stats = processor.get_summary_stats()
    
    # Simple success message
    if stats['total_responses'] == 400 and stats['uae_responses'] == 200 and stats['ksa_responses'] == 200:
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Data Loaded Successfully:</strong> Exactly 400 responses (200 UAE + 200 KSA) with readable interface
        </div>
        """, unsafe_allow_html=True)
    
    # NORMAL SIDEBAR - NO AGGRESSIVE STYLING
    st.sidebar.markdown("### 🎛️ Filters")
    
    filter_options = stats['filter_options']
    
    # Normal dropdowns
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
        key="purpose_filter"
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
    
    # NORMAL TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview", 
        "📈 Cross-Analysis", 
        "🔤 Word Cloud",
        "🧠 Advanced Insights",
        "💼 Business Intelligence"
    ])
    
    with tab1:
        st.markdown("### 📊 Market Overview")
        
        # Simple metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filtered Responses", len(filtered_data))
            
        with col2:
            filtered_uae = len(filtered_data[filtered_data['Country'] == 'UAE'])
            st.metric("UAE Responses", filtered_uae)
            
        with col3:
            filtered_ksa = len(filtered_data[filtered_data['Country'] == 'KSA'])
            st.metric("KSA Responses", filtered_ksa)
            
        with col4:
            coverage = (len(filtered_data) / 400) * 100
            st.metric("Coverage", f"{coverage:.1f}%")
        
        # NORMAL CHARTS - LET PLOTLY HANDLE STYLING
        col1, col2 = st.columns(2)
        
        with col1:
            if len(filtered_data) > 0:
                country_counts = filtered_data['Country'].value_counts()
                fig_country = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Market Distribution",
                    color_discrete_map={'UAE': '#27ae60', 'KSA': '#3498db'}
                )
                # Ensure labels are dark and visible
                fig_country.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50', size=12),
                    title_font=dict(color='#2c3e50', size=16)
                )
                fig_country.update_traces(
                    textfont=dict(color='#2c3e50', size=12),
                    textinfo='label+percent'
                )
                st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            if 'Nationality' in filtered_data.columns and len(filtered_data) > 0:
                nat_counts = filtered_data['Nationality'].value_counts().head(10)
                fig_nat = px.bar(
                    x=nat_counts.values,
                    y=nat_counts.index,
                    orientation='h',
                    title=f"Top Nationalities (from {len(filter_options['nationalities'])} total)",
                    labels={'x': 'Count', 'y': 'Nationality'}
                )
                fig_nat.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50', size=12),
                    title_font=dict(color='#2c3e50', size=16)
                )
                fig_nat.update_traces(
                    textfont=dict(color='#2c3e50', size=12)
                )
                st.plotly_chart(fig_nat, use_container_width=True)
        
        # Visit purpose analysis
        if 'Visit Purpose' in filtered_data.columns and len(filtered_data) > 0:
            st.markdown("### ✈️ Visit Purpose Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                purpose_counts = filtered_data['Visit Purpose'].value_counts()
                fig_purpose = px.bar(
                    x=purpose_counts.index,
                    y=purpose_counts.values,
                    title="Visit Purpose Distribution",
                    labels={'x': 'Purpose', 'y': 'Count'},
                    color_discrete_sequence=['#3498db', '#27ae60', '#f39c12', '#e74c3c']
                )
                fig_purpose.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50', size=12),
                    title_font=dict(color='#2c3e50', size=16)
                )
                fig_purpose.update_traces(
                    textfont=dict(color='#2c3e50', size=12)
                )
                st.plotly_chart(fig_purpose, use_container_width=True)
            
            with col2:
                if len(filtered_data) > 1:
                    try:
                        purpose_country = pd.crosstab(filtered_data['Visit Purpose'], filtered_data['Country'])
                        fig_cross = px.bar(
                            purpose_country,
                            title="Purpose by Country",
                            color_discrete_map={'UAE': '#27ae60', 'KSA': '#3498db'}
                        )
                        fig_cross.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(color='#2c3e50', size=12),
                            title_font=dict(color='#2c3e50', size=16)
                        )
                        fig_cross.update_traces(
                            textfont=dict(color='#2c3e50', size=12)
                        )
                        st.plotly_chart(fig_cross, use_container_width=True)
                    except:
                        st.info("Cross-tabulation not available for current selection")
    
    with tab2:
        st.markdown("### 📈 Cross-Analysis")
        
        available_questions = [q for q in stats['available_questions'] if 'Unnamed' not in str(q)]
        
        if len(available_questions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                question1 = st.selectbox(
                    "📋 First Question",
                    options=available_questions,
                    key="crosstab_q1"
                )
            
            with col2:
                available_q2 = [q for q in available_questions if q != question1]
                question2 = st.selectbox(
                    "📋 Second Question", 
                    options=available_q2,
                    key="crosstab_q2"
                )
            
            if st.button("🔍 Generate Analysis", type="primary"):
                with st.spinner("Analyzing..."):
                    
                    crosstab_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes,
                        'frequency': selected_frequencies
                    }
                    
                    result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
                    
                    if result and result['combinations']:
                        st.success(f"✅ Analysis completed: {result['total_responses']} responses")
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Results</h4>
                            <p><strong>Q1:</strong> {question1}</p>
                            <p><strong>Q2:</strong> {question2}</p>
                            <p><strong>Sample:</strong> {result['total_responses']} responses</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Simple results display
                        st.markdown("#### 🎯 Top Combinations")
                        
                        for i, combo in enumerate(result['combinations'][:5], 1):
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>#{i} - {combo['count']} responses ({combo['percentage']}%)</h4>
                                <p><strong>Answer 1:</strong> {combo['question1_value']}</p>
                                <p><strong>Answer 2:</strong> {combo['question2_value']}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔤 Word Cloud Analysis")
        
        wordcloud_analyzer = OSNWordCloudAnalyzer()
        text_questions = stats['text_questions']
        
        if text_questions:
            st.markdown(f"📝 **{len(text_questions)} Text Questions Available:**")
            
            for question in text_questions:
                st.markdown(f'<span class="theme-tag">{question[:50]}{"..." if len(question) > 50 else ""}</span>', unsafe_allow_html=True)
            
            selected_text_question = st.selectbox(
                "🎯 Select Question",
                options=text_questions,
                key="wordcloud_question"
            )
            
            if st.button("🚀 Generate Word Cloud", type="primary"):
                with st.spinner("Analyzing text..."):
                    
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
                        st.success(f"✅ Analyzing {len(text_responses)} responses")
                        
                        wordcloud_data = wordcloud_analyzer.generate_wordcloud_data(
                            text_responses,
                            max_words=50,
                            osn_focus=True
                        )
                        
                        wordcloud_fig = create_wordcloud_visualization(
                            wordcloud_data,
                            title=f"Word Cloud: {selected_text_question[:30]}..."
                        )
                        
                        if wordcloud_fig:
                            st.markdown("""
                            <div class="wordcloud-container">
                                <h4>🎨 Word Cloud Visualization</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            st.plotly_chart(wordcloud_fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 🧠 Advanced Text Insights")
        
        insights_analyzer = AdvancedTextInsightsAnalyzer()
        text_questions = stats['text_questions']
        
        if text_questions and len(filtered_data) > 10:
            
            if st.button("🔍 Generate Advanced Insights", type="primary"):
                with st.spinner("Analyzing guest response meanings..."):
                    
                    insights_report = insights_analyzer.generate_comprehensive_insights_report(
                        filtered_data, 
                        text_questions
                    )
                    
                    if insights_report and 'error' not in insights_report:
                        st.success(f"✅ Analysis complete: {insights_report.get('total_responses_analyzed', 0)} responses")
                        
                        display_advanced_insights(insights_report)
                        
                    else:
                        st.warning("⚠️ Could not generate insights. Adjust filters or check data.")
        
        else:
            st.info("💡 Need at least 10 responses for advanced insights analysis.")
    
    with tab5:
        st.markdown("### 💼 Business Intelligence")
        
        business_insights = processor.generate_insights(filtered_data, "strategic")
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>💡 Strategic OSN Insights</h4>
            {business_insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Additional charts if enough data
        if len(filtered_data) > 50:
            st.markdown("#### 📈 Satisfaction Analysis")
            
            if 'Entertainment Quality Rating' in filtered_data.columns:
                rating_dist = filtered_data['Entertainment Quality Rating'].value_counts().sort_index()
                fig_ratings = px.bar(
                    x=rating_dist.index,
                    y=rating_dist.values,
                    title="Entertainment Satisfaction",
                    labels={'x': 'Rating', 'y': 'Count'},
                    color_discrete_sequence=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
                )
                fig_ratings.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50', size=12),
                    title_font=dict(color='#2c3e50', size=16)
                )
                fig_ratings.update_traces(
                    textfont=dict(color='#2c3e50', size=12)
                )
                st.plotly_chart(fig_ratings, use_container_width=True)

if __name__ == "__main__":
    main()
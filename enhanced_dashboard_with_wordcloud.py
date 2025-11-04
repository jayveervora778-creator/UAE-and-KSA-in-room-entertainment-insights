#!/usr/bin/env python3
"""
ENHANCED OSN Survey Dashboard with Word Cloud Analysis
✅ ALL nationalities included in dropdown
✅ NO 'Unnamed' questions in dropdowns 
✅ Word Cloud text analysis module
✅ Opinion/text response filtering
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from enhanced_osn_processor import EnhancedOSNProcessor
from osn_wordcloud_analyzer import OSNWordCloudAnalyzer

# Configure Streamlit
st.set_page_config(
    page_title="Enhanced OSN Survey Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for word cloud and better UI
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
    }
    .main-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #10b981;
        margin: 1rem 0;
        color: #065f46;
    }
    .wordcloud-container {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #f59e0b;
        margin: 1rem 0;
    }
    .theme-tag {
        background: #3b82f6;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    /* Fix any remaining dark theme issues */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    .stMultiSelect > div > div {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes only
def load_survey_data():
    """Load and cache enhanced survey data"""
    processor = EnhancedOSNProcessor()
    success = processor.load_data()
    if success:
        return processor
    return None

def create_wordcloud_visualization(word_data, title="Word Cloud"):
    """Create word cloud visualization using Plotly"""
    if not word_data or not word_data['word_frequency']:
        return None
    
    words = list(word_data['word_frequency'].keys())[:30]  # Top 30 words
    frequencies = list(word_data['word_frequency'].values())[:30]
    
    # Normalize frequencies for better visualization
    max_freq = max(frequencies) if frequencies else 1
    normalized_sizes = [20 + (freq / max_freq) * 40 for freq in frequencies]
    
    # Create scatter plot as word cloud
    fig = go.Figure()
    
    # Generate random positions for words
    np.random.seed(42)  # For consistent positioning
    n_words = len(words)
    
    # Create spiral positioning for better word cloud look
    angles = np.linspace(0, 4 * np.pi, n_words)
    radii = np.linspace(0.5, 3, n_words)
    x_pos = radii * np.cos(angles)
    y_pos = radii * np.sin(angles)
    
    colors = px.colors.qualitative.Set3[:n_words]
    
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='text',
        text=words,
        textfont=dict(
            size=normalized_sizes,
            color=colors
        ),
        hovertemplate='<b>%{text}</b><br>Frequency: %{customdata}<extra></extra>',
        customdata=frequencies,
        showlegend=False
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16, color='#1f2937')),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🎯 Enhanced OSN Guest Survey Analytics</h1>
        <p style="color: #e0f2fe; margin: 0; font-size: 1.1rem;">Advanced Analytics with Word Cloud Text Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor = load_survey_data()
    
    if processor is None:
        st.error("❌ Failed to load survey data. Please check the data file.")
        return
    
    # Get summary statistics
    stats = processor.get_summary_stats()
    
    # Data integrity check
    if stats['total_responses'] == 400 and stats['uae_responses'] == 200 and stats['ksa_responses'] == 200:
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Enhanced Data Integrity:</strong> Exactly 400 responses (200 UAE + 200 KSA) with improved question naming
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Data integrity issue: {stats['total_responses']} total responses")
    
    # Sidebar filters
    st.sidebar.markdown("### 🎛️ Enhanced Filters")
    
    filter_options = stats['filter_options']
    
    # Country filter
    selected_countries = st.sidebar.multiselect(
        "🌍 Markets",
        options=filter_options['countries'],
        default=filter_options['countries'],
        key="country_filter"
    )
    
    # Enhanced nationality filter - ALL NATIONALITIES
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Guest Nationalities",
        options=filter_options['nationalities'],
        key="nationality_filter",
        help=f"Select from ALL {len(filter_options['nationalities'])} nationalities available"
    )
    
    # Visit purpose filter  
    selected_purposes = st.sidebar.multiselect(
        "✈️ Visit Purposes",
        options=filter_options['visit_purposes'],
        key="purpose_filter",
        help="Business, Leisure, Family Vacation, Other"
    )
    
    # Hotel frequency filter
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
    
    # Main content tabs - INCLUDING NEW WORD CLOUD TAB
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Market Overview", 
        "📈 Cross-Analysis", 
        "🔤 Text Analysis & Word Cloud",
        "💼 Business Intelligence"
    ])
    
    with tab1:
        st.markdown("### 📊 Enhanced Market Overview")
        
        # Enhanced metrics
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
        
        # Enhanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Country distribution
            if len(filtered_data) > 0:
                country_counts = filtered_data['Country'].value_counts()
                fig_country = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Market Distribution",
                    color_discrete_map={'UAE': '#10b981', 'KSA': '#3b82f6'}
                )
                fig_country.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#1f2937')
                )
                st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            # Top nationalities with ALL nationalities available
            if 'Nationality' in filtered_data.columns and len(filtered_data) > 0:
                nat_counts = filtered_data['Nationality'].value_counts().head(10)
                fig_nat = px.bar(
                    x=nat_counts.values,
                    y=nat_counts.index,
                    orientation='h',
                    title=f"Top Guest Nationalities (from {len(filter_options['nationalities'])} total)",
                    labels={'x': 'Guest Count', 'y': 'Nationality'},
                    color=nat_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_nat.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#1f2937'),
                    showlegend=False
                )
                st.plotly_chart(fig_nat, use_container_width=True)
        
        # Visit purpose analysis (enhanced)
        if 'Visit Purpose' in filtered_data.columns and len(filtered_data) > 0:
            st.markdown("### ✈️ Enhanced Visit Purpose Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                purpose_counts = filtered_data['Visit Purpose'].value_counts()
                fig_purpose = px.bar(
                    x=purpose_counts.index,
                    y=purpose_counts.values,
                    title="Visit Purpose Distribution",
                    labels={'x': 'Visit Purpose', 'y': 'Guest Count'},
                    color=purpose_counts.values,
                    color_continuous_scale='Greens'
                )
                fig_purpose.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#1f2937'),
                    showlegend=False
                )
                st.plotly_chart(fig_purpose, use_container_width=True)
            
            with col2:
                # Purpose by country cross-tabulation
                if len(filtered_data) > 1:
                    try:
                        purpose_country = pd.crosstab(filtered_data['Visit Purpose'], filtered_data['Country'])
                        fig_cross = px.bar(
                            purpose_country,
                            title="Visit Purpose by Market",
                            labels={'index': 'Visit Purpose', 'value': 'Count'},
                            color_discrete_map={'UAE': '#10b981', 'KSA': '#3b82f6'}
                        )
                        fig_cross.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(color='#1f2937')
                        )
                        st.plotly_chart(fig_cross, use_container_width=True)
                    except:
                        st.info("Cross-tabulation chart not available for current filter selection")
    
    with tab2:
        st.markdown("### 📈 Enhanced Cross-Analysis (No More 'Unnamed')")
        st.markdown("Explore relationships between survey dimensions using meaningful question names.")
        
        # Get CLEAN question names (no more 'Unnamed')
        available_questions = [q for q in stats['available_questions'] if 'Unnamed' not in str(q)]
        
        if len(available_questions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                question1 = st.selectbox(
                    "📋 First Dimension (Enhanced Names)",
                    options=available_questions,
                    key="crosstab_q1",
                    help="All questions now have meaningful names - no more codes!"
                )
            
            with col2:
                available_q2 = [q for q in available_questions if q != question1]
                question2 = st.selectbox(
                    "📋 Second Dimension", 
                    options=available_q2,
                    key="crosstab_q2",
                    help="Select second dimension for comparison"
                )
            
            if st.button("🔍 Generate Enhanced Cross-Analysis", key="run_crosstab", type="primary"):
                with st.spinner("Analyzing relationship patterns..."):
                    
                    crosstab_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes,
                        'frequency': selected_frequencies
                    }
                    
                    result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
                    
                    if result and result['combinations']:
                        st.success(f"✅ Enhanced analysis completed using {result['total_responses']} responses")
                        
                        # Analysis header
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Enhanced Cross-Analysis Results</h4>
                            <p><strong>Dimension 1:</strong> {question1}</p>
                            <p><strong>Dimension 2:</strong> {question2}</p>
                            <p><strong>Sample Size:</strong> {result['total_responses']} responses</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Top combinations
                        st.markdown("#### 🎯 Top Response Combinations")
                        
                        combinations = result['combinations'][:8]
                        
                        for i, combo in enumerate(combinations, 1):
                            col1, col2, col3, col4 = st.columns([1, 3, 3, 2])
                            
                            with col1:
                                st.markdown(f"**#{i}**")
                            
                            with col2:
                                st.markdown(f"**{combo['question1_value'][:40]}{'...' if len(combo['question1_value']) > 40 else ''}**")
                            
                            with col3:
                                st.markdown(f"**{combo['question2_value'][:40]}{'...' if len(combo['question2_value']) > 40 else ''}**")
                            
                            with col4:
                                st.metric("", f"{combo['count']}", f"{combo['percentage']}%")
                    
                    else:
                        st.warning("⚠️ Could not generate meaningful cross-analysis. Try different dimensions.")
        
        else:
            st.info("ℹ️ Cross-analysis requires at least 2 survey dimensions with meaningful names.")
    
    with tab3:
        st.markdown("### 🔤 Text Analysis & Word Cloud Module")
        st.markdown("Analyze guest opinions and text responses with OSN-focused insights.")
        
        # Initialize word cloud analyzer
        wordcloud_analyzer = OSNWordCloudAnalyzer()
        
        # Text question selection
        text_questions = stats['text_questions']
        
        if text_questions:
            st.markdown(f"📝 **{len(text_questions)} Opinion/Text Questions Available:**")
            
            # Display available text questions as tags
            for question in text_questions:
                st.markdown(f'<span class="theme-tag">{question[:50]}{"..." if len(question) > 50 else ""}</span>', unsafe_allow_html=True)
            
            # Question selector for word cloud
            selected_text_question = st.selectbox(
                "🎯 Select Question for Word Cloud Analysis",
                options=text_questions,
                key="wordcloud_question",
                help="Choose a text/opinion question to analyze guest responses"
            )
            
            # Word cloud settings
            col1, col2, col3 = st.columns(3)
            
            with col1:
                max_words = st.slider("📊 Max Words in Cloud", 20, 100, 50)
            
            with col2:
                osn_focus = st.checkbox("🎯 OSN-Focused Analysis", value=True, help="Boost hospitality and entertainment terms")
            
            with col3:
                min_word_length = st.slider("✂️ Min Word Length", 3, 6, 4)
            
            if st.button("🚀 Generate Word Cloud Analysis", type="primary"):
                with st.spinner("Analyzing text responses and generating insights..."):
                    
                    # Get filtered text responses
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
                        st.success(f"✅ Analyzing {len(text_responses)} text responses")
                        
                        # Generate word cloud data
                        wordcloud_data = wordcloud_analyzer.generate_wordcloud_data(
                            text_responses,
                            max_words=max_words,
                            osn_focus=osn_focus
                        )
                        
                        # Create and display word cloud
                        wordcloud_fig = create_wordcloud_visualization(
                            wordcloud_data,
                            title=f"Word Cloud: {selected_text_question[:40]}{'...' if len(selected_text_question) > 40 else ''}"
                        )
                        
                        if wordcloud_fig:
                            st.markdown("""
                            <div class="wordcloud-container">
                                <h4>🎨 Interactive Word Cloud Visualization</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            st.plotly_chart(wordcloud_fig, use_container_width=True)
                        
                        # Display categorized words
                        st.markdown("#### 🏷️ Words by OSN Theme Categories")
                        
                        categorized = wordcloud_data['categorized']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if categorized['entertainment']:
                                st.markdown("**🎬 Entertainment**")
                                for word, freq in list(categorized['entertainment'].items())[:5]:
                                    st.markdown(f"• {word} ({freq}x)")
                        
                        with col2:
                            if categorized['experience']:
                                st.markdown("**⭐ Experience**") 
                                for word, freq in list(categorized['experience'].items())[:5]:
                                    st.markdown(f"• {word} ({freq}x)")
                        
                        with col3:
                            if categorized['technology']:
                                st.markdown("**💻 Technology**")
                                for word, freq in list(categorized['technology'].items())[:5]:
                                    st.markdown(f"• {word} ({freq}x)")
                        
                        # OSN-focused insights
                        st.markdown("#### 💡 OSN Strategic Text Insights")
                        st.markdown(f"""
                        <div class="insight-box">
                            {wordcloud_data['osn_insights'].replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.warning("⚠️ No meaningful text responses found for the selected question and filters.")
        
        else:
            st.info("ℹ️ No text/opinion questions identified in the dataset for word cloud analysis.")
    
    with tab4:
        st.markdown("### 💼 Enhanced Business Intelligence")
        
        # Generate enhanced business insights
        business_insights = processor.generate_insights(filtered_data, "strategic")
        
        st.markdown("#### 💡 Strategic OSN Insights")
        st.markdown(f"""
        <div class="insight-box">
            {business_insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Additional analytics
        if len(filtered_data) > 50:  # Only show for meaningful sample sizes
            st.markdown("#### 📈 Advanced Analytics Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Satisfaction distribution
                if 'Entertainment Quality Rating' in filtered_data.columns:
                    rating_dist = filtered_data['Entertainment Quality Rating'].value_counts().sort_index()
                    fig_ratings = px.bar(
                        x=rating_dist.index,
                        y=rating_dist.values,
                        title="Entertainment Satisfaction Distribution",
                        labels={'x': 'Rating (1-5)', 'y': 'Guest Count'},
                        color=rating_dist.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_ratings.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1f2937')
                    )
                    st.plotly_chart(fig_ratings, use_container_width=True)
            
            with col2:
                # Nationality vs Visit Purpose heatmap
                if 'Nationality' in filtered_data.columns and 'Visit Purpose' in filtered_data.columns:
                    try:
                        nat_purpose_crosstab = pd.crosstab(
                            filtered_data['Nationality'], 
                            filtered_data['Visit Purpose']
                        )
                        
                        # Get top 8 nationalities for readability
                        top_nats = filtered_data['Nationality'].value_counts().head(8).index
                        heatmap_data = nat_purpose_crosstab.loc[
                            nat_purpose_crosstab.index.intersection(top_nats)
                        ]
                        
                        fig_heatmap = px.imshow(
                            heatmap_data.values,
                            x=heatmap_data.columns,
                            y=heatmap_data.index,
                            title="Nationality vs Visit Purpose Heatmap",
                            color_continuous_scale='Blues'
                        )
                        fig_heatmap.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(color='#1f2937')
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                    except Exception as e:
                        st.info("Heatmap not available for current data selection")

if __name__ == "__main__":
    main()
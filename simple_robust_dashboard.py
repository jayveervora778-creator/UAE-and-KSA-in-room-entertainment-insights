#!/usr/bin/env python3
"""
Simple, Robust OSN Survey Dashboard
Clean approach: 400 responses, working filters, cross-tabs, business insights
No over-engineering - focus on reliability and usability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from simple_robust_processor import SimpleRobustProcessor

# Configure Streamlit
st.set_page_config(
    page_title="OSN Survey Dashboard - Simple & Robust",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean CSS - no complex theming that breaks functionality
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    .main-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }
    .insight-box {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
    .stMultiSelect > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_processor():
    """Load data processor once and cache it"""
    processor = SimpleRobustProcessor()
    success = processor.load_data()
    return processor if success else None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">📊 OSN Survey Analytics Dashboard</h1>
        <p style="color: #bfdbfe; margin: 0;">Simple, Reliable Survey Analysis • UAE & KSA Markets • 400 Responses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor = load_processor()
    
    if processor is None:
        st.error("❌ Could not load survey data. Please check the data file.")
        return
    
    # Get basic stats
    stats = processor.get_summary_stats()
    
    # Data validation display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Responses", stats['total_responses'])
        
    with col2:
        st.metric("UAE Responses", stats['uae_responses'])
        
    with col3:
        st.metric("KSA Responses", stats['ksa_responses'])
        
    with col4:
        st.metric("Survey Questions", stats['total_questions'])
    
    # Show data consistency status
    is_consistent = (stats['total_responses'] == 400 and 
                    stats['uae_responses'] == 200 and 
                    stats['ksa_responses'] == 200)
    
    if is_consistent:
        st.success("✅ Data consistency verified: Exactly 400 responses (200 UAE + 200 KSA)")
    else:
        st.warning(f"⚠️ Data inconsistency: Found {stats['total_responses']} total responses")
    
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.markdown("## 🎯 Filter Options")
    
    filter_options = stats['filter_options']
    
    # Country filter
    selected_countries = st.sidebar.multiselect(
        "📍 Countries",
        options=filter_options['countries'],
        default=filter_options['countries'],
        key="country_filter"
    )
    
    # Nationality filter
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Guest Nationalities",
        options=filter_options['nationalities'],
        key="nationality_filter",
        help=f"{len(filter_options['nationalities'])} nationalities available"
    )
    
    # Visit purpose filter  
    selected_purposes = st.sidebar.multiselect(
        "✈️ Visit Purposes",
        options=filter_options['visit_purposes'],
        key="purpose_filter",
        help="Business, Leisure, Family, etc."
    )
    
    # Get filtered data
    filtered_data = processor.get_filtered_data(
        country_filter=selected_countries,
        nationality_filter=selected_nationalities,
        purpose_filter=selected_purposes
    )
    
    if len(filtered_data) == 0:
        st.warning("No data matches the selected filters. Please adjust your selection.")
        return
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview & Charts", "📈 Cross-Tabulation", "💼 Business Insights"])
    
    with tab1:
        st.markdown("### 📊 Filtered Data Overview")
        
        # Filtered metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filtered Responses", len(filtered_data))
            
        with col2:
            filtered_uae = len(filtered_data[filtered_data['Country'] == 'UAE'])
            st.metric("UAE (Filtered)", filtered_uae)
            
        with col3:
            filtered_ksa = len(filtered_data[filtered_data['Country'] == 'KSA'])
            st.metric("KSA (Filtered)", filtered_ksa)
            
        with col4:
            filter_percentage = (len(filtered_data) / stats['total_responses']) * 100
            st.metric("Data Coverage", f"{filter_percentage:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Country distribution
            if len(filtered_data) > 0:
                country_counts = filtered_data['Country'].value_counts()
                fig_country = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Country Distribution (Filtered Data)",
                    color_discrete_map={'UAE': '#3b82f6', 'KSA': '#10b981'}
                )
                fig_country.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            # Nationality distribution (top 8)
            if 'Nationality' in filtered_data.columns and len(filtered_data) > 0:
                nat_counts = filtered_data['Nationality'].value_counts().head(8)
                fig_nat = px.bar(
                    x=nat_counts.values,
                    y=nat_counts.index,
                    orientation='h',
                    title="Top Guest Nationalities (Filtered)",
                    labels={'x': 'Count', 'y': 'Nationality'}
                )
                fig_nat.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_nat, use_container_width=True)
        
        # Visit purpose analysis
        if 'Visit Purpose' in filtered_data.columns and len(filtered_data) > 0:
            st.markdown("### ✈️ Visit Purpose Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                purpose_counts = filtered_data['Visit Purpose'].value_counts().head(6)
                fig_purpose = px.bar(
                    x=purpose_counts.index.astype(str),
                    y=purpose_counts.values,
                    title="Visit Purpose Distribution",
                    labels={'x': 'Purpose', 'y': 'Count'}
                )
                fig_purpose.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_purpose, use_container_width=True)
            
            with col2:
                # Purpose by country
                if len(filtered_data) > 1:
                    purpose_country = pd.crosstab(filtered_data['Visit Purpose'], filtered_data['Country'])
                    fig_purpose_country = px.bar(
                        purpose_country,
                        title="Visit Purpose by Country",
                        labels={'index': 'Purpose', 'value': 'Count'}
                    )
                    fig_purpose_country.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig_purpose_country, use_container_width=True)
        
        # Entertainment satisfaction
        if 'Entertainment Quality Rating' in filtered_data.columns:
            st.markdown("### ⭐ Entertainment Satisfaction")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rating_counts = filtered_data['Entertainment Quality Rating'].value_counts().sort_index()
                fig_rating = px.bar(
                    x=rating_counts.index.astype(str),
                    y=rating_counts.values,
                    title="Entertainment Quality Ratings",
                    labels={'x': 'Rating', 'y': 'Count'}
                )
                fig_rating.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_rating, use_container_width=True)
            
            with col2:
                avg_rating = filtered_data['Entertainment Quality Rating'].mean()
                if pd.notna(avg_rating):
                    # Rating by country
                    country_ratings = filtered_data.groupby('Country')['Entertainment Quality Rating'].mean()
                    fig_country_rating = px.bar(
                        x=country_ratings.index,
                        y=country_ratings.values,
                        title="Average Rating by Country",
                        labels={'x': 'Country', 'y': 'Average Rating'}
                    )
                    fig_country_rating.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig_country_rating, use_container_width=True)
        
        # Business Insights Box
        st.markdown("### 💡 Key Insights from Filtered Data")
        insights = processor.generate_insights(filtered_data, "overview")
        st.markdown(f"""
        <div class="insight-box">
            {insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📈 Cross-Tabulation Analysis")
        st.markdown("Analyze relationships between two survey questions using your filtered data.")
        
        available_questions = stats['available_questions']
        
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
            
            if st.button("🔍 Generate Cross-Tabulation", key="run_crosstab"):
                with st.spinner("Analyzing relationship..."):
                    
                    # Create filter dict for crosstab
                    crosstab_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes
                    }
                    
                    result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
                    
                    if result:
                        st.success(f"✅ Cross-tabulation completed using {result['total_responses']} responses")
                        
                        # Show question info
                        st.info(f"**Analyzing:** {question1} ↔ {question2}")
                        
                        # Display top combinations
                        st.markdown("### 📊 Top Response Combinations")
                        
                        combinations = result['combinations']
                        if combinations:
                            for i, combo in enumerate(combinations[:8], 1):
                                col1, col2, col3 = st.columns([3, 3, 1])
                                
                                with col1:
                                    st.write(f"**{combo['question1_value']}**")
                                
                                with col2:
                                    st.write(f"**{combo['question2_value']}**")
                                
                                with col3:
                                    st.metric("", f"{combo['count']} ({combo['percentage']}%)")
                        
                        # Business insights for this combination
                        st.markdown("### 💡 Cross-Tabulation Insights")
                        
                        crosstab_insights = []
                        if combinations:
                            top_combo = combinations[0]
                            crosstab_insights.append(f"🎯 **Strongest Pattern**: {top_combo['question1_value']} + {top_combo['question2_value']} ({top_combo['count']} responses, {top_combo['percentage']}%)")
                            
                            if len(combinations) > 1:
                                crosstab_insights.append(f"📈 **Secondary Pattern**: {combinations[1]['question1_value']} + {combinations[1]['question2_value']} ({combinations[1]['count']} responses)")
                            
                            crosstab_insights.append(f"💼 **Business Action**: Focus service offerings on the {top_combo['question1_value']} and {top_combo['question2_value']} combination")
                            crosstab_insights.append(f"📊 **Market Opportunity**: {result['total_responses']} total responses analyzed for strategic insights")
                        
                        insights_text = "\n\n".join(crosstab_insights)
                        st.markdown(f"""
                        <div class="insight-box">
                            {insights_text.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.error("❌ Could not generate cross-tabulation. Please try different questions.")
        
        else:
            st.info("Need at least 2 questions for cross-tabulation analysis.")
    
    with tab3:
        st.markdown("### 💼 Business Intelligence & Strategic Insights")
        
        # Generate comprehensive business insights
        business_insights = processor.generate_insights(filtered_data, "business")
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>📊 Strategic Analysis Based on {len(filtered_data)} Filtered Responses</h4>
            {business_insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Additional business metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Market Segmentation")
            
            # Market coverage analysis
            market_metrics = []
            
            if 'Nationality' in filtered_data.columns:
                top_nat = filtered_data['Nationality'].value_counts().iloc[0]
                nat_name = filtered_data['Nationality'].value_counts().index[0]
                market_metrics.append(f"**Primary Market**: {nat_name} ({top_nat} guests, {(top_nat/len(filtered_data)*100):.1f}%)")
            
            if 'Visit Purpose' in filtered_data.columns:
                top_purpose = filtered_data['Visit Purpose'].value_counts().iloc[0]
                purpose_name = filtered_data['Visit Purpose'].value_counts().index[0]
                market_metrics.append(f"**Main Visit Type**: {purpose_name} ({top_purpose} guests)")
            
            if 'Entertainment Quality Rating' in filtered_data.columns:
                avg_rating = filtered_data['Entertainment Quality Rating'].mean()
                if pd.notna(avg_rating):
                    satisfaction_level = "High" if avg_rating >= 4 else "Moderate" if avg_rating >= 3 else "Low"
                    market_metrics.append(f"**Satisfaction Level**: {satisfaction_level} (Avg: {avg_rating:.1f}/5)")
            
            for metric in market_metrics:
                st.write(f"• {metric}")
        
        with col2:
            st.markdown("#### 💡 Strategic Recommendations")
            
            recommendations = [
                "🎯 **Target Audience**: Focus marketing on identified top nationality segments",
                "📈 **Service Enhancement**: Improve entertainment offerings based on satisfaction ratings",
                "🏨 **Guest Experience**: Customize services for primary visit purposes",
                "📊 **Data-Driven Decisions**: Use 400-response dataset for strategic planning",
                "🌍 **Market Expansion**: Leverage UAE/KSA insights for regional growth"
            ]
            
            for rec in recommendations:
                st.write(f"• {rec}")
        
        # Filter summary
        st.markdown("---")
        st.markdown("#### 🔍 Current Filter Summary")
        
        filter_summary = []
        if selected_countries != filter_options['countries']:
            filter_summary.append(f"Countries: {', '.join(selected_countries)}")
        if selected_nationalities:
            filter_summary.append(f"Nationalities: {', '.join(selected_nationalities[:3])}{'...' if len(selected_nationalities) > 3 else ''}")
        if selected_purposes:
            filter_summary.append(f"Purposes: {', '.join(selected_purposes[:3])}{'...' if len(selected_purposes) > 3 else ''}")
        
        if filter_summary:
            st.info(f"**Active Filters**: {' | '.join(filter_summary)}")
        else:
            st.info("**Showing all data** (no filters applied)")

if __name__ == "__main__":
    main()
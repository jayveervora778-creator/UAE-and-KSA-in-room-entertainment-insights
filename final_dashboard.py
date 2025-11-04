#!/usr/bin/env python3
"""
FINAL OSN Survey Dashboard - AUDIT CORRECTED
✅ EXACTLY 400 responses (200 UAE + 200 KSA) 
✅ Working filters with meaningful names
✅ Clean cross-tabulation
✅ Business insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from final_corrected_processor import FinalCorrectedProcessor

# Configure Streamlit
st.set_page_config(
    page_title="OSN Survey Dashboard - Final Version",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, professional CSS
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
        margin: 1rem 0;
    }
    /* Ensure dropdowns work properly */
    .stSelectbox > div > div {
        background-color: white !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    .stMultiSelect > div > div {
        background-color: white !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        color: #1f2937;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_final_processor():
    """Load the final corrected processor"""
    processor = FinalCorrectedProcessor()
    success = processor.load_data()
    return processor if success else None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">📊 OSN Survey Analytics</h1>
        <p style="color: #bfdbfe; margin: 0.5rem 0 0 0; font-size: 1.1rem;">Enterprise Dashboard • UAE & KSA Markets • 400 Guest Responses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load processor
    processor = load_final_processor()
    
    if processor is None:
        st.error("❌ Could not load survey data. Please check the data file.")
        return
    
    # Get summary stats
    stats = processor.get_summary_stats()
    
    # Data validation metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Responses", stats['total_responses'], delta="Consistent")
        
    with col2:
        st.metric("🇦🇪 UAE Market", stats['uae_responses'], delta="Target Met")
        
    with col3:
        st.metric("🇸🇦 KSA Market", stats['ksa_responses'], delta="Target Met")
        
    with col4:
        st.metric("📋 Survey Questions", stats['total_questions'], delta="Analyzed")
    
    # Data consistency verification
    if stats['total_responses'] == 400 and stats['uae_responses'] == 200 and stats['ksa_responses'] == 200:
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Data Integrity Confirmed:</strong> Exactly 400 responses (200 UAE + 200 KSA) loaded and verified
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"⚠️ Data inconsistency detected: {stats['total_responses']} total responses")
    
    # Sidebar filters
    st.sidebar.markdown("## 🎯 Market Analysis Filters")
    
    filter_options = stats['filter_options']
    
    # Country filter
    selected_countries = st.sidebar.multiselect(
        "📍 Target Markets",
        options=filter_options['countries'],
        default=filter_options['countries'],
        key="country_filter"
    )
    
    # Nationality filter
    selected_nationalities = st.sidebar.multiselect(
        "🌍 Guest Nationalities",
        options=filter_options['nationalities'],
        key="nationality_filter",
        help=f"Select from {len(filter_options['nationalities'])} nationalities"
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
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "📈 Cross-Analysis", "💼 Business Intelligence"])
    
    with tab1:
        st.markdown("### 📊 Filtered Market Overview")
        
        # Filtered metrics
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
        
        # Visualizations
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
            # Top nationalities
            if 'Nationality' in filtered_data.columns and len(filtered_data) > 0:
                nat_counts = filtered_data['Nationality'].value_counts().head(8)
                fig_nat = px.bar(
                    x=nat_counts.values,
                    y=nat_counts.index,
                    orientation='h',
                    title="Top Guest Nationalities",
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
        
        # Entertainment insights
        if 'Entertainment Quality Rating' in filtered_data.columns:
            st.markdown("### ⭐ Entertainment Satisfaction Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rating_data = filtered_data['Entertainment Quality Rating'].dropna()
                if len(rating_data) > 0:
                    rating_counts = rating_data.value_counts().sort_index()
                    fig_rating = px.bar(
                        x=rating_counts.index,
                        y=rating_counts.values,
                        title="Entertainment Quality Ratings",
                        labels={'x': 'Rating (1-5)', 'y': 'Number of Guests'},
                        color=rating_counts.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_rating.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1f2937'),
                        showlegend=False
                    )
                    st.plotly_chart(fig_rating, use_container_width=True)
            
            with col2:
                # Average rating by market
                if len(rating_data) > 0:
                    market_ratings = filtered_data.groupby('Country')['Entertainment Quality Rating'].mean()
                    fig_market_rating = px.bar(
                        x=market_ratings.index,
                        y=market_ratings.values,
                        title="Average Rating by Market",
                        labels={'x': 'Market', 'y': 'Average Rating'},
                        color=market_ratings.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_market_rating.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#1f2937'),
                        showlegend=False
                    )
                    st.plotly_chart(fig_market_rating, use_container_width=True)
        
        # Automated insights
        st.markdown("### 💡 Automated Market Insights")
        insights = processor.generate_insights(filtered_data, "overview")
        st.markdown(f"""
        <div class="insight-box">
            {insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📈 Cross-Tabulation Analysis")
        st.markdown("Explore relationships between different survey dimensions using your filtered dataset.")
        
        available_questions = [q for q in stats['available_questions'] if q not in ['S. No.']]
        
        if len(available_questions) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                question1 = st.selectbox(
                    "📋 First Dimension",
                    options=available_questions,
                    key="crosstab_q1",
                    help="Select the first variable for analysis"
                )
            
            with col2:
                available_q2 = [q for q in available_questions if q != question1]
                question2 = st.selectbox(
                    "📋 Second Dimension", 
                    options=available_q2,
                    key="crosstab_q2",
                    help="Select the second variable for comparison"
                )
            
            if st.button("🔍 Generate Cross-Analysis", key="run_crosstab", type="primary"):
                with st.spinner("Analyzing relationship patterns..."):
                    
                    crosstab_filters = {
                        'countries': selected_countries,
                        'nationalities': selected_nationalities,
                        'purposes': selected_purposes,
                        'frequency': selected_frequencies
                    }
                    
                    result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
                    
                    if result and result['combinations']:
                        st.success(f"✅ Analysis completed using {result['total_responses']} filtered responses")
                        
                        # Analysis header
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Cross-Analysis Results</h4>
                            <p><strong>Dimension 1:</strong> {question1}</p>
                            <p><strong>Dimension 2:</strong> {question2}</p>
                            <p><strong>Sample Size:</strong> {result['total_responses']} responses</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Top combinations
                        st.markdown("#### 🎯 Top Response Combinations")
                        
                        combinations = result['combinations'][:8]  # Top 8
                        
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
                        
                        # Automated cross-analysis insights
                        st.markdown("#### 💡 Cross-Analysis Insights")
                        
                        top_combo = combinations[0]
                        cross_insights = [
                            f"🎯 **Strongest Pattern**: '{top_combo['question1_value']}' combined with '{top_combo['question2_value']}' represents {top_combo['percentage']}% of filtered responses ({top_combo['count']} guests)",
                            f"📊 **Market Significance**: This combination provides actionable insights for {result['total_responses']} guest responses",
                            f"💼 **Strategic Opportunity**: Focus service development on the {top_combo['question1_value']} segment preferences",
                            f"📈 **Business Impact**: {len(combinations)} distinct patterns identified for targeted marketing and service customization"
                        ]
                        
                        insights_text = "\n\n".join(cross_insights)
                        st.markdown(f"""
                        <div class="insight-box">
                            {insights_text.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    else:
                        st.warning("⚠️ Could not generate meaningful cross-analysis. Try different dimensions or adjust filters.")
        
        else:
            st.info("ℹ️ Cross-analysis requires at least 2 survey dimensions.")
    
    with tab3:
        st.markdown("### 💼 Business Intelligence & Strategic Insights")
        
        # Generate comprehensive business insights
        business_insights = processor.generate_insights(filtered_data, "business")
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>📊 Strategic Analysis Summary</h4>
            <p><em>Based on {len(filtered_data)} filtered responses from the 400-guest survey dataset</em></p>
            <br>
            {business_insights.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Key performance indicators
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Market Intelligence")
            
            market_kpis = []
            
            # Market penetration
            if len(filtered_data) > 0:
                market_penetration = (len(filtered_data) / 400) * 100
                market_kpis.append(f"**Market Coverage**: {market_penetration:.1f}% of total survey population")
            
            # Top nationality insight
            if 'Nationality' in filtered_data.columns:
                top_nationality = filtered_data['Nationality'].value_counts().iloc[0]
                top_nat_name = filtered_data['Nationality'].value_counts().index[0]
                nat_percentage = (top_nationality / len(filtered_data)) * 100
                market_kpis.append(f"**Primary Segment**: {top_nat_name} ({nat_percentage:.1f}% of filtered data)")
            
            # Visit purpose distribution
            if 'Visit Purpose' in filtered_data.columns:
                top_purpose = filtered_data['Visit Purpose'].value_counts().iloc[0]
                top_purpose_name = filtered_data['Visit Purpose'].value_counts().index[0]
                purpose_percentage = (top_purpose / len(filtered_data)) * 100
                market_kpis.append(f"**Main Visit Type**: {top_purpose_name} ({purpose_percentage:.1f}%)")
            
            # Entertainment satisfaction
            if 'Entertainment Quality Rating' in filtered_data.columns:
                avg_rating = filtered_data['Entertainment Quality Rating'].mean()
                if pd.notna(avg_rating):
                    satisfaction_level = "Excellent" if avg_rating >= 4.5 else "High" if avg_rating >= 4 else "Good" if avg_rating >= 3.5 else "Needs Improvement"
                    market_kpis.append(f"**Satisfaction Level**: {satisfaction_level} (Average: {avg_rating:.1f}/5)")
            
            for kpi in market_kpis:
                st.markdown(f"• {kpi}")
        
        with col2:
            st.markdown("#### 💡 Strategic Recommendations")
            
            recommendations = [
                "🎯 **Targeted Marketing**: Focus campaigns on identified primary nationality segments",
                "📊 **Data-Driven Decisions**: Leverage 400-response statistical significance for strategic planning",
                "🏨 **Service Customization**: Tailor entertainment offerings to visit purpose patterns (Business/Leisure/Family)",
                "📈 **Market Expansion**: Use UAE/KSA insights for regional hospitality growth",
                "⭐ **Guest Experience**: Implement satisfaction-based improvements in entertainment services",
                "🔄 **Continuous Analytics**: Establish regular survey cycles using this framework for ongoing market intelligence"
            ]
            
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        # Filter impact summary
        st.markdown("---")
        st.markdown("#### 🔍 Current Analysis Scope")
        
        scope_info = []
        if selected_countries != filter_options['countries']:
            scope_info.append(f"**Markets**: {', '.join(selected_countries)}")
        else:
            scope_info.append("**Markets**: All markets (UAE + KSA)")
            
        if selected_nationalities:
            scope_info.append(f"**Nationalities**: {len(selected_nationalities)} selected")
        else:
            scope_info.append("**Nationalities**: All nationalities included")
            
        if selected_purposes:
            scope_info.append(f"**Visit Purposes**: {', '.join(selected_purposes)}")
        else:
            scope_info.append("**Visit Purposes**: All purposes included")
        
        scope_info.append(f"**Analysis Coverage**: {len(filtered_data)}/400 responses ({(len(filtered_data)/400)*100:.1f}%)")
        
        st.info(" | ".join(scope_info))

if __name__ == "__main__":
    main()
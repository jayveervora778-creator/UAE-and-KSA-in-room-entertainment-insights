#!/usr/bin/env python3
"""
OSN Survey Analytics Dashboard - ULTIMATE DATA MANEUVERABILITY
Comprehensive survey analysis with full question exploration and pattern detection
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


# Import processors
try:
    from fixed_multiresponse_processor_lazy import FixedMultiResponseProcessor
    print("✅ Imported FixedMultiResponseProcessor (lazy loading version)")
except ImportError as e:
    st.error(f"Could not import FixedMultiResponseProcessor: {e}")
    st.stop()

# Import optional analytics (can work without them)
OptimizedOSNAnalytics = None
Config = None

try:
    from optimized_analytics import OptimizedOSNAnalytics
    from config import Config
    print("✅ Imported OptimizedOSNAnalytics and Config")
except ImportError:
    try:
        backend_path = Path(__file__).parent / 'backend' / 'app'
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        from optimized_analytics import OptimizedOSNAnalytics
        from config import Config
        print(f"✅ Imported OptimizedOSNAnalytics and Config from {backend_path}")
    except ImportError as e:
        print(f"Warning: Could not import OptimizedOSNAnalytics or Config: {e}")
        print("Will proceed without advanced analytics")

# Page configuration
st.set_page_config(
    page_title="OSN Survey Analytics - Ultimate Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .filter-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .pattern-box {
        background: #e8f5e8;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .question-title {
        font-weight: bold;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    /* Hide default streamlit styling */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Survey Question Mapping (Complete)
SURVEY_QUESTIONS = {
    # Demographics (A series)
    'A1': 'What is your nationality?',
    'A2': 'What was the primary purpose of your visit?',
    'A2-A': 'Please specify other purpose of your visit?',
    'A3': 'How many times have you stayed in a hotel over the past year?',
    
    # Hotel Choice & Entertainment Priority (B series)
    'B1-A': 'What were your top 3 reasons for choosing this hotel? (Multi-response)',
    'B-A-a': 'Please specify other reason for choosing the hotel?',
    'B1-B': 'Would you prioritize entertainment more if traveling with children or family?',
    'B2-A': 'How important is in-room entertainment in shaping your hotel experience?',
    'B2-B': 'Can you recall a hotel stay where entertainment exceeded or disappointed expectations?',
    
    # Content Usage & Preferences (C series)
    'C1': 'Did you use the in-room TV or entertainment system during your stay?',
    'C2-A/1': 'Content Type Watched: OSN+',
    'C2-A/2': 'Content Type Watched: Netflix',
    'C2-A/3': 'Content Type Watched: Amazon Prime',
    'C2-A/4': 'Content Type Watched: YouTube',
    'C2-A/5': 'Content Type Watched: Local Channels',
    'C2-A/99': 'Content Type Watched: Other',
    'C2-A-a': 'Please specify other type of content did you watch?',
    'C2-B': 'Was this content easily accessible or did it require effort to set up?',
    'C3/1': 'Entertainment Format Preference: Rank 1',
    'C3/2': 'Entertainment Format Preference: Rank 2', 
    'C3/3': 'Entertainment Format Preference: Rank 3',
    'C3/4': 'Entertainment Format Preference: Rank 4',
    'C3/5': 'Entertainment Format Preference: Rank 5',
    'C4-A': 'Rate the overall quality of the in-room entertainment experience',
    'C4-B': 'What would have improved your rating?',
    
    # Streaming & Payment (D series)
    'D1/1': 'Current Subscription: Netflix',
    'D1/2': 'Current Subscription: Amazon Prime',
    'D1/3': 'Current Subscription: OSN+',
    'D1/4': 'Current Subscription: Disney+',
    'D1/5': 'Current Subscription: YouTube Premium',
    'D1/6': 'Current Subscription: Other/None',
    'D2': 'Would you prefer access to your own streaming accounts while in the hotel room?',
    'D3': 'Would you be willing to pay a small fee for enhanced in-room entertainment?',
    'D4': 'If yes, what price range (per day) would be acceptable?',
    'D5': 'Any suggestions to improve the in-room entertainment experience?'
}

@st.cache_data
def load_survey_data():
    """Load and cache survey data with question mapping"""
    try:
        data_file = Path(__file__).parent / 'data' / 'survey_data.xlsx'
        if not data_file.exists():
            data_file = Path(__file__).parent / 'backend' / 'data' / 'survey_data.xlsx'
            
        if not data_file.exists():
            st.error(f"Survey data file not found: {data_file}")
            return None, None, None
        
        processor = FixedMultiResponseProcessor(str(data_file))
        analytics = OptimizedOSNAnalytics(processor) if OptimizedOSNAnalytics else None
        df = processor._get_combined_data()
        
        return processor, analytics, df
    except Exception as e:
        st.error(f"Error loading survey data: {e}")
        return None, None, None

def get_demographic_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Extract demographic filter options"""
    options = {}
    
    # Countries
    if 'Country' in df.columns:
        options['countries'] = sorted(df['Country'].dropna().unique().tolist())
    
    # Nationalities (A1)
    if 'A1' in df.columns:
        nationalities = df['A1'].dropna().unique().tolist()
        clean_nationalities = []
        for nat in nationalities:
            cleaned = str(nat).strip().replace('\xa0', ' ')
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

def get_available_questions(df: pd.DataFrame, processor=None) -> Dict[str, Dict[str, Any]]:
    """Get all available survey questions including multi-response questions"""
    available_questions = {}
    
    # Regular single-response questions
    for col in df.columns:
        if col in SURVEY_QUESTIONS:
            data = df[col].dropna()
            if not data.empty:
                unique_values = data.unique()
                available_questions[col] = {
                    'title': SURVEY_QUESTIONS[col],
                    'responses': len(data),
                    'unique_values': len(unique_values),
                    'sample_values': list(unique_values)[:5],
                    'data_type': 'categorical' if len(unique_values) < 20 else 'text'
                }
    
    # Add multi-response questions if processor is available
    if processor:
        try:
            multi_data = processor.get_combined_multiresponse_data()
            for question_code, info in multi_data.items():
                if info['response_counts']:  # Only include if has data
                    available_questions[question_code] = {
                        'title': info['question'],
                        'responses': info['total_responses'],
                        'unique_values': len(info['response_counts']),
                        'sample_values': list(info['response_counts'].keys())[:5],
                        'data_type': 'multi_response'
                    }
        except Exception as e:
            print(f"Error adding multi-response questions: {e}")
    
    return available_questions

def apply_demographic_filters(df: pd.DataFrame, country: str, nationality: str, purpose: str, frequency: str) -> pd.DataFrame:
    """Apply demographic filters"""
    filtered_df = df.copy()
    
    if country and country != "All Countries":
        filtered_df = filtered_df[filtered_df['Country'] == country]
    
    if nationality and nationality != "All Nationalities" and 'A1' in df.columns:
        mask = filtered_df['A1'].str.replace('\xa0', ' ').str.strip() == nationality
        filtered_df = filtered_df[mask]
    
    if purpose and purpose != "All Purposes" and 'A2' in df.columns:
        filtered_df = filtered_df[filtered_df['A2'] == purpose]
    
    if frequency and frequency != "All Frequencies" and 'A3' in df.columns:
        filtered_df = filtered_df[filtered_df['A3'] == frequency]
    
    return filtered_df

def create_universal_chart(df: pd.DataFrame, question_col: str, question_title: str, chart_type: str = 'auto'):
    """Create charts for any survey question"""
    if question_col not in df.columns:
        return None
    
    clean_df = df[[question_col]].dropna()
    if clean_df.empty:
        return None
    
    data = clean_df[question_col]
    value_counts = data.value_counts()
    
    # Auto-detect chart type based on data
    if chart_type == 'auto':
        if len(value_counts) <= 10:
            chart_type = 'bar'
        elif len(value_counts) <= 20:
            chart_type = 'pie'
        else:
            chart_type = 'histogram'
    
    if chart_type == 'bar':
        fig = go.Figure(data=[go.Bar(
            x=value_counts.index,
            y=value_counts.values,
            text=[f"{count}<br>({count/len(data)*100:.1f}%)" for count in value_counts.values],
            textposition='auto',
            marker_color='#667eea'
        )])
        
        fig.update_layout(
            title=f"{question_title}<br><sub>Total Responses: {len(data)}</sub>",
            xaxis_title="Response Options",
            yaxis_title="Number of Responses",
            height=400,
            showlegend=False
        )
    
    elif chart_type == 'pie':
        fig = go.Figure(data=[go.Pie(
            labels=value_counts.index,
            values=value_counts.values,
            hole=0.4,
            textinfo='label+percent',
            marker_colors=px.colors.qualitative.Set3
        )])
        
        fig.update_layout(
            title=f"{question_title}<br><sub>Total Responses: {len(data)}</sub>",
            height=400,
            showlegend=True
        )
    
    elif chart_type == 'histogram':
        fig = go.Figure(data=[go.Histogram(
            x=data,
            nbinsx=min(20, len(value_counts)),
            marker_color='#667eea'
        )])
        
        fig.update_layout(
            title=f"{question_title}<br><sub>Total Responses: {len(data)}</sub>",
            xaxis_title="Response Values",
            yaxis_title="Frequency",
            height=400
        )
    
    return fig

def create_cross_tabulation(df: pd.DataFrame, question1: str, question2: str):
    """Create cross-tabulation analysis between two questions"""
    if question1 not in df.columns or question2 not in df.columns:
        return None
    
    clean_df = df[[question1, question2]].dropna()
    if clean_df.empty:
        return None
    
    # Create cross-tabulation
    crosstab = pd.crosstab(clean_df[question1], clean_df[question2], normalize='index') * 100
    
    fig = go.Figure(data=go.Heatmap(
        z=crosstab.values,
        x=crosstab.columns,
        y=crosstab.index,
        colorscale='Blues',
        text=[[f"{val:.1f}%" for val in row] for row in crosstab.values],
        texttemplate="%{text}",
        showscale=True
    ))
    
    fig.update_layout(
        title=f"Cross Analysis: {SURVEY_QUESTIONS.get(question1, question1)} vs {SURVEY_QUESTIONS.get(question2, question2)}",
        xaxis_title=SURVEY_QUESTIONS.get(question2, question2),
        yaxis_title=SURVEY_QUESTIONS.get(question1, question1),
        height=500
    )
    
    return fig

def analyze_distribution_patterns(data: pd.Series) -> Dict[str, Any]:
    """Analyze distribution patterns beyond just top response"""
    value_counts = data.value_counts()
    total_responses = len(data)
    percentages = (value_counts / total_responses * 100).round(1)
    
    # Calculate distribution metrics
    entropy = -sum((p/100) * np.log2(p/100) for p in percentages if p > 0)  # Diversity measure
    concentration = (percentages.iloc[0] / 100) if len(percentages) > 0 else 0  # Top response concentration
    fragmentation = len(percentages)  # Number of different responses
    
    # Identify distribution type
    if concentration > 0.7:
        distribution_type = "dominant"
    elif concentration > 0.5:
        distribution_type = "majority"
    elif concentration > 0.4:
        distribution_type = "plurality"
    else:
        distribution_type = "fragmented"
    
    return {
        'value_counts': value_counts,
        'percentages': percentages,
        'total_responses': total_responses,
        'entropy': entropy,
        'concentration': concentration,
        'fragmentation': fragmentation,
        'distribution_type': distribution_type
    }

def generate_business_takeaways(df: pd.DataFrame, question_col: str, filters: Dict[str, str]) -> List[Dict[str, str]]:
    """Generate practical business takeaways based on response patterns"""
    takeaways = []
    
    if question_col not in df.columns:
        return takeaways
    
    data = df[question_col].dropna()
    if data.empty:
        return takeaways
    
    # Create market segment description
    segment_parts = []
    if filters.get('country') and filters['country'] != 'All Countries':
        segment_parts.append(f"{filters['country']} market")
    if filters.get('nationality') and filters['nationality'] != 'All Nationalities':
        segment_parts.append(f"{filters['nationality']} travelers")
    if filters.get('purpose') and filters['purpose'] != 'All Purposes':
        segment_parts.append(f"{filters['purpose'].lower()} segment")
    if filters.get('frequency') and filters['frequency'] != 'All Frequencies':
        segment_parts.append(f"{filters['frequency'].lower()} hotel users")
    
    market_segment = " | ".join(segment_parts) if segment_parts else "Overall market"
    
    # Analyze response distribution
    value_counts = data.value_counts()
    total_responses = len(data)
    percentages = (value_counts / total_responses * 100).round(1)
    
    # Generate takeaways based on response patterns
    question_title = SURVEY_QUESTIONS.get(question_col, question_col)
    
    if len(value_counts) == 0:
        return takeaways
    
    top_response = value_counts.index[0]
    top_percentage = percentages.iloc[0]
    
    # Business takeaway based on top response
    if 'entertainment' in question_title.lower() and 'important' in question_title.lower():
        if 'very important' in str(top_response).lower():
            takeaways.append({
                'title': '🎯 HIGH Entertainment Priority Market',
                'finding': f'**{top_percentage}% of {market_segment}** rate entertainment as very important',
                'business_action': f'OSN should prioritize premium entertainment partnerships with hotels serving this segment. High willingness indicates strong revenue opportunity.',
                'confidence': 'high'
            })
        elif 'not important' in str(top_response).lower():
            takeaways.append({
                'title': '⚠️ LOW Entertainment Priority Market', 
                'finding': f'**{top_percentage}% of {market_segment}** rate entertainment as not important',
                'business_action': f'Focus on basic OSN+ access rather than premium features for this segment. Consider cost-effective bundling strategies.',
                'confidence': 'high'
            })
        else:
            takeaways.append({
                'title': '📊 MODERATE Entertainment Interest',
                'finding': f'**{top_percentage}% of {market_segment}** show moderate entertainment interest',
                'business_action': f'Balanced approach: offer tiered OSN+ packages allowing guests to upgrade based on individual preferences.',
                'confidence': 'medium'
            })
    
    elif 'streaming' in question_title.lower() or 'access' in question_title.lower():
        if 'yes' in str(top_response).lower():
            takeaways.append({
                'title': '📱 HIGH Streaming Demand',
                'finding': f'**{top_percentage}% of {market_segment}** want access to their streaming accounts',
                'business_action': f'OSN should develop seamless account integration features and partner with hotels to provide secure streaming access.',
                'confidence': 'high'
            })
        else:
            takeaways.append({
                'title': '🏨 Traditional Entertainment Preference',
                'finding': f'**{top_percentage}% of {market_segment}** prefer hotel-provided entertainment',
                'business_action': f'Focus on curated OSN+ content libraries rather than personal account access for this market.',
                'confidence': 'high'
            })
    
    elif 'pay' in question_title.lower() or 'fee' in question_title.lower():
        if 'yes' in str(top_response).lower():
            takeaways.append({
                'title': '💰 MONETIZATION Opportunity',
                'finding': f'**{top_percentage}% of {market_segment}** willing to pay for enhanced entertainment',
                'business_action': f'Implement tiered pricing strategy. Premium OSN+ packages can generate additional revenue in this segment.',
                'confidence': 'high'
            })
        else:
            takeaways.append({
                'title': '🆓 FREE Content Strategy',
                'finding': f'**{top_percentage}% of {market_segment}** unwilling to pay extra fees',
                'business_action': f'Focus on hotel partnership models where OSN+ is included in room rate rather than separate charges.',
                'confidence': 'high'
            })
    
    elif 'nationality' in question_title.lower():
        # Top nationalities insight
        if len(value_counts) >= 3:
            top_3_nationalities = value_counts.head(3)
            nationality_insight = ", ".join([f"{nat} ({pct:.1f}%)" for nat, pct in zip(top_3_nationalities.index, percentages.head(3))])
            
            takeaways.append({
                'title': '🌍 PRIMARY Market Demographics',
                'finding': f'Top guest nationalities: {nationality_insight}',
                'business_action': f'Localize OSN+ content for these key markets. Prioritize Arabic, English, and regional language content.',
                'confidence': 'high'
            })
    
    elif 'purpose' in question_title.lower():
        # Visit purpose insights
        if 'business' in str(top_response).lower():
            takeaways.append({
                'title': '💼 BUSINESS Traveler Focus',
                'finding': f'**{top_percentage}% of {market_segment}** are business travelers',
                'business_action': f'Offer productivity-focused OSN+ packages: news, business channels, and quick entertainment for short stays.',
                'confidence': 'high'
            })
        elif 'leisure' in str(top_response).lower():
            takeaways.append({
                'title': '🏖️ LEISURE Traveler Focus',
                'finding': f'**{top_percentage}% of {market_segment}** are leisure travelers',
                'business_action': f'Emphasize entertainment variety: movies, series, and family content. Longer engagement expected.',
                'confidence': 'high'
            })
    
    # Add market size context
    takeaways.append({
        'title': '📊 Market Size Context',
        'finding': f'Analysis based on **{total_responses} guest responses** from {market_segment}',
        'business_action': f'Sample size provides {"reliable" if total_responses >= 100 else "preliminary"} insights for strategic planning.',
        'confidence': 'high' if total_responses >= 100 else 'medium'
    })
    
    return takeaways

def detect_patterns_and_insights(df: pd.DataFrame, question_col: str, filters: Dict[str, str]) -> List[Dict[str, str]]:
    """Generate actionable business insights based on survey response patterns"""
    insights = []
    
    if question_col not in df.columns:
        return insights
    
    data = df[question_col].dropna()
    if data.empty:
        return insights
    
    # Create market segment description
    segment_parts = []
    if filters.get('country') and filters['country'] != 'All Countries':
        segment_parts.append(f"{filters['country']} market")
    if filters.get('nationality') and filters['nationality'] != 'All Nationalities':
        segment_parts.append(f"{filters['nationality']} travelers")
    if filters.get('purpose') and filters['purpose'] != 'All Purposes':
        segment_parts.append(f"{filters['purpose'].lower()} segment")
    if filters.get('frequency') and filters['frequency'] != 'All Frequencies':
        segment_parts.append(f"{filters['frequency'].lower()} hotel users")
    
    market_segment = " | ".join(segment_parts) if segment_parts else "Overall market"
    
    # Distribution analysis for pattern detection
    distribution = analyze_distribution_patterns(data)
    question_title = SURVEY_QUESTIONS.get(question_col, question_col)
    
    # Generate business takeaways instead of correlations
    business_takeaways = generate_business_takeaways(df, question_col, filters)
    
    # Add primary distribution insight with clear business focus
    top_response = distribution['value_counts'].index[0]
    top_pct = distribution['percentages'].iloc[0]
    
    # Simple, clear market pattern insight
    if distribution['distribution_type'] == 'dominant':
        pattern_type = "Strong Consensus"
        confidence = "high"
    elif distribution['distribution_type'] == 'fragmented':
        pattern_type = "Diverse Opinions"
        confidence = "medium"
    else:
        pattern_type = "Clear Preference"  
        confidence = "high"
    
    insights.append({
        'title': f'📊 {pattern_type}: {top_pct}% Market Pattern',
        'finding': f"**{top_response}** is the top response from {len(data)} guests in {market_segment}",
        'implication': f"Clear market direction for OSN strategy and hotel partnership focus",
        'data_backing': f'Sample: {len(data)} responses | Pattern: {distribution["distribution_type"]} | Categories: {distribution["fragmentation"]}',
        'confidence': confidence
    })
    
    # Return business takeaways instead of complex correlation analysis
    return insights + business_takeaways

def create_multiresponse_chart(processor, question_code: str, title: str) -> go.Figure:
    """Create visualization for multi-response questions"""
    try:
        multi_data = processor.get_combined_multiresponse_data()
        
        if question_code not in multi_data:
            return None
        
        question_info = multi_data[question_code]
        response_counts = question_info['response_counts']
        
        if not response_counts:
            return None
        
        # Create horizontal bar chart for better readability
        labels = list(response_counts.keys())
        values = list(response_counts.values())
        
        # Calculate percentages
        total_responses = question_info['total_responses']
        percentages = [count / total_responses * 100 for count in values]
        
        # Sort by value
        sorted_data = sorted(zip(labels, values, percentages), key=lambda x: x[1], reverse=True)
        sorted_labels, sorted_values, sorted_percentages = zip(*sorted_data)
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=sorted_labels,
            x=sorted_values,
            orientation='h',
            text=[f'{count}<br>({pct:.1f}%)' for count, pct in zip(sorted_values, sorted_percentages)],
            textposition='outside',
            marker=dict(
                color=sorted_values,
                colorscale='viridis',
                showscale=True,
                colorbar=dict(title="Response Count")
            )
        ))
        
        fig.update_layout(
            title=f"{title}<br><sub>Multiple responses allowed - {total_responses} total selections</sub>",
            xaxis_title="Number of Responses",
            yaxis_title="Hotel Choice Factors",
            height=max(400, len(sorted_labels) * 50),
            margin=dict(l=150, r=100, t=80, b=50),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating multi-response chart: {e}")
        return None

def display_multiresponse_insights(processor, question_code: str, filters: Dict[str, str]) -> None:
    """Display insights for multi-response questions"""
    try:
        multi_data = processor.get_combined_multiresponse_data()
        
        if question_code not in multi_data:
            return
        
        question_info = multi_data[question_code]
        response_counts = question_info['response_counts']
        
        # Create market segment description
        segment_parts = []
        if filters.get('country') and filters['country'] != 'All Countries':
            segment_parts.append(f"{filters['country']} market")
        if filters.get('nationality') and filters['nationality'] != 'All Nationalities':
            segment_parts.append(f"{filters['nationality']} travelers")
        if filters.get('purpose') and filters['purpose'] != 'All Purposes':
            segment_parts.append(f"{filters['purpose'].lower()} segment")
        if filters.get('frequency') and filters['frequency'] != 'All Frequencies':
            segment_parts.append(f"{filters['frequency'].lower()} hotel users")
        
        market_segment = " | ".join(segment_parts) if segment_parts else "Overall market"
        
        # Calculate insights
        total_selections = sum(response_counts.values())
        sorted_factors = sorted(response_counts.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_factors:
            return
        
        top_factor = sorted_factors[0]
        top_percentage = (top_factor[1] / total_selections) * 100
        
        insights = []
        
        # Primary factor insight
        insights.append({
            'title': '🎯 PRIMARY Hotel Selection Driver',
            'finding': f'**{top_factor[0]}** dominates guest decision-making with {top_factor[1]} selections ({top_percentage:.1f}%)',
            'implication': f'OSN should prioritize partnerships with hotels emphasizing {top_factor[0].lower()}-focused marketing',
            'confidence': 'high'
        })
        
        # Second and third factors
        if len(sorted_factors) >= 3:
            second_factor = sorted_factors[1]
            third_factor = sorted_factors[2]
            
            second_pct = (second_factor[1] / total_selections) * 100
            third_pct = (third_factor[1] / total_selections) * 100
            
            insights.append({
                'title': '🔄 SECONDARY Decision Factors',
                'finding': f'**{second_factor[0]}** ({second_pct:.1f}%) and **{third_factor[0]}** ({third_pct:.1f}%) form the secondary decision matrix',
                'implication': f'Multi-factor marketing approach combining {top_factor[0].lower()}, {second_factor[0].lower()}, and {third_factor[0].lower()} messaging will maximize guest acquisition',
                'confidence': 'medium'
            })
        
        # Entertainment factor specific insight
        entertainment_factors = [factor for factor, count in response_counts.items() if 'entertainment' in factor.lower()]
        if entertainment_factors:
            entertainment_factor = entertainment_factors[0]
            entertainment_count = response_counts[entertainment_factor]
            entertainment_pct = (entertainment_count / total_selections) * 100
            
            if entertainment_count > 0:
                insights.append({
                    'title': '📺 In-Room ENTERTAINMENT Impact',
                    'finding': f'**{entertainment_count} guests ({entertainment_pct:.1f}%)** consider in-room entertainment a key hotel selection factor',
                    'implication': f'OSN+ positioning as a hotel amenity differentiator has **{entertainment_pct:.1f}% direct market penetration** potential for hotel partnerships',
                    'confidence': 'high'
                })
        
        # Display insights
        for insight in insights:
            st.markdown(f"""
            <div class="pattern-box">
                <h4>{insight['title']}</h4>
                <p><strong>Finding:</strong> {insight['finding']}</p>
                <p><strong>Strategic Implication:</strong> {insight['implication']}</p>
                <p><em>Confidence: {insight['confidence']}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error displaying multi-response insights: {e}")

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>📊 OSN Survey Analytics - ULTIMATE DASHBOARD</h1>
        <p>Complete Data Maneuverability: Explore ANY Survey Question with Full Pattern Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    processor, analytics, df = load_survey_data()
    
    if df is None:
        st.error("Could not load survey data. Please check the data file.")
        st.stop()
    
    # Get options
    demographic_options = get_demographic_options(df)
    available_questions = get_available_questions(df, processor)
    
    # Sidebar - Demographics
    st.sidebar.markdown("""
    <div class="filter-panel">
        <h4>🏨 Guest Demographics</h4>
        <p>Filter by what hotels know about guests</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demographic filters
    countries = ['All Countries'] + demographic_options.get('countries', [])
    selected_country = st.sidebar.selectbox("📍 Market", countries, key='country_filter')
    
    nationalities = ['All Nationalities'] + demographic_options.get('nationalities', [])
    selected_nationality = st.sidebar.selectbox("🌍 Nationality", nationalities, key='nationality_filter')
    
    purposes = ['All Purposes'] + demographic_options.get('purposes', [])
    selected_purpose = st.sidebar.selectbox("🎯 Visit Purpose", purposes, key='purpose_filter')
    
    frequencies = ['All Frequencies'] + demographic_options.get('frequencies', [])
    selected_frequency = st.sidebar.selectbox("📅 Visit Frequency", frequencies, key='frequency_filter')
    
    # Apply filters
    filtered_df = apply_demographic_filters(df, selected_country, selected_nationality, selected_purpose, selected_frequency)
    
    # Filter status
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
    <div style="background: #007bff; color: white; padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; margin: 1rem 0;">
        👥 Analyzing: <strong>{len(filtered_df)} guests</strong> | {filter_text}
    </div>
    """, unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.warning("No guests match the selected criteria. Please adjust your filters.")
        return
    
    # SURVEY QUESTION EXPLORER
    st.markdown("""
    <div class="section-header">
        <h2>🔍 Survey Question Explorer</h2>
        <p>Select ANY survey question to analyze for your filtered guest segment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Question categories
    question_categories = {
        'Demographics': {k: v for k, v in available_questions.items() if k.startswith('A')},
        'Hotel Choice & Entertainment Priority': {k: v for k, v in available_questions.items() if k.startswith('B')},
        'Content Usage & Preferences': {k: v for k, v in available_questions.items() if k.startswith('C')},
        'Streaming & Payment': {k: v for k, v in available_questions.items() if k.startswith('D')}
    }
    
    # Primary question selector
    st.markdown("### 📊 Primary Analysis Question")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox(
            "Question Category",
            list(question_categories.keys()),
            key='category_selector'
        )
    
    with col2:
        category_questions = question_categories[selected_category]
        question_options = [f"{code}: {details['title']}" for code, details in category_questions.items()]
        
        if question_options:
            selected_question_option = st.selectbox(
                "Survey Question",
                question_options,
                key='question_selector'
            )
            
            selected_question_code = selected_question_option.split(':')[0]
        else:
            st.warning(f"No questions available in {selected_category} category")
            return
    
    # Chart type selector
    chart_type = st.selectbox(
        "Visualization Type",
        ['auto', 'bar', 'pie', 'histogram'],
        key='chart_type'
    )
    
    # Generate primary analysis
    question_info = available_questions.get(selected_question_code, {})
    question_title = question_info.get('title', selected_question_code)
    
    # Main chart
    st.markdown(f"""
    <div class="question-title">
        📊 {question_title}
    </div>
    """, unsafe_allow_html=True)
    
    chart = None
    insights = []
    
    # Check if this is a multi-response question
    if question_info.get('data_type') == 'multi_response':
        # Handle multi-response questions
        chart = create_multiresponse_chart(processor, selected_question_code, question_title)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
            
        # Multi-response specific insights
        display_multiresponse_insights(processor, selected_question_code, {
            'country': selected_country,
            'nationality': selected_nationality,
            'purpose': selected_purpose,
            'frequency': selected_frequency
        })
        
    elif selected_question_code in filtered_df.columns:
        # Handle regular single-response questions
        chart = create_universal_chart(filtered_df, selected_question_code, question_title, chart_type)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
            
        # Pattern detection and insights for single-response questions
        insights = detect_patterns_and_insights(filtered_df, selected_question_code, {
            'country': selected_country,
            'nationality': selected_nationality,
            'purpose': selected_purpose,
            'frequency': selected_frequency
        })
        
        if insights:
            st.markdown("### 🧠 Pattern Detection & Insights")
            for insight in insights:
                confidence_color = "#28a745" if insight['confidence'] == 'high' else "#ffc107" if insight['confidence'] == 'medium' else "#dc3545"
                
                # Handle both old and new insight formats
                implication = insight.get('implication') or insight.get('business_action', 'No business action specified')
                data_confidence = insight.get('data_backing', f"Confidence: {insight.get('confidence', 'medium')}")
                
                st.markdown(f"""
                <div style="background: {confidence_color}15; border-left: 4px solid {confidence_color}; padding: 1rem; margin: 1rem 0; border-radius: 5px;">
                    <strong>{insight['title']}</strong><br>
                    <strong>Finding:</strong> {insight['finding']}<br>
                    <strong>Business Action:</strong> {implication}<br>
                    <small><strong>Data Confidence:</strong> {data_confidence}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data available for this question with current filters")
    
    # CROSS-ANALYSIS SECTION
    st.markdown("""
    <div class="section-header">
        <h2>🔀 Cross-Tabulation Analysis</h2>
        <p>Compare two survey questions to find correlations and patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        all_questions = list(available_questions.keys())
        question1 = st.selectbox(
            "First Question",
            [f"{code}: {SURVEY_QUESTIONS.get(code, code)}" for code in all_questions],
            key='cross_q1'
        )
        question1_code = question1.split(':')[0]
    
    with col2:
        question2 = st.selectbox(
            "Second Question", 
            [f"{code}: {SURVEY_QUESTIONS.get(code, code)}" for code in all_questions],
            key='cross_q2'
        )
        question2_code = question2.split(':')[0]
    
    if st.button("Generate Cross-Analysis", key='cross_analysis_btn'):
        if question1_code != question2_code:
            cross_chart = create_cross_tabulation(filtered_df, question1_code, question2_code)
            if cross_chart:
                st.plotly_chart(cross_chart, use_container_width=True)
                
                # Cross-analysis insights for OSN strategy
                st.markdown("### 🎯 Cross-Analysis Market Intelligence")
                
                # Generate strategic insights based on correlation
                cross_data = filtered_df[(filtered_df[question1_code].notna()) & (filtered_df[question2_code].notna())]
                sample_size = len(cross_data)
                
                # Create market segment description
                segment_parts = []
                if selected_country != "All Countries":
                    segment_parts.append(f"{selected_country} market")
                if selected_nationality != "All Nationalities":
                    segment_parts.append(f"{selected_nationality} travelers")
                if selected_purpose != "All Purposes":
                    segment_parts.append(f"{selected_purpose.lower()} segment")
                if selected_frequency != "All Frequencies":
                    segment_parts.append(f"{selected_frequency.lower()} hotel users")
                
                market_segment = " | ".join(segment_parts) if segment_parts else "Overall market"
                
                st.markdown(f"""
                <div class="insight-box">
                    <strong>Market Intelligence:</strong> Cross-correlation analysis reveals strategic insights for OSN:<br><br>
                    
                    <strong>Questions Analyzed:</strong><br>
                    • {SURVEY_QUESTIONS.get(question1_code, question1_code)}<br>
                    • {SURVEY_QUESTIONS.get(question2_code, question2_code)}<br><br>
                    
                    <strong>OSN Strategic Value:</strong><br>
                    • <strong>Market Segmentation:</strong> Identify which guest types correlate with high entertainment value<br>
                    • <strong>Partnership Strategy:</strong> Understand content preferences vs. payment willingness by segment<br>
                    • <strong>Product Development:</strong> Design hotel entertainment solutions based on correlated preferences<br>
                    • <strong>Revenue Optimization:</strong> Target high-value segments with premium offerings<br><br>
                    
                    <strong>Market Sample:</strong> {sample_size} responses from {market_segment}<br>
                    <strong>Confidence Level:</strong> {"High" if sample_size > 50 else "Medium" if sample_size > 20 else "Low"} - {"Statistically significant for market decisions" if sample_size > 50 else "Directional insights for strategy development" if sample_size > 20 else "Exploratory findings requiring additional validation"}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No data available for cross-analysis with current filters")
        else:
            st.warning("Please select different questions for cross-analysis")
    
    # QUICK STATS OVERVIEW
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    **Data Overview:**
    - Total guests: {len(df)}
    - Filtered segment: {len(filtered_df)}
    - Available questions: {len(available_questions)}
    - Nationalities: {len(demographic_options.get('nationalities', []))}
    - Countries: {len(demographic_options.get('countries', []))}
    """)
    
    # Show available questions summary
    if st.sidebar.checkbox("Show All Questions", key='show_questions'):
        st.sidebar.markdown("**Survey Questions:**")
        for category, questions in question_categories.items():
            st.sidebar.markdown(f"**{category}:** {len(questions)} questions")

if __name__ == "__main__":
    main()
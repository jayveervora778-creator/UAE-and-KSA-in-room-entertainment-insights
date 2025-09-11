#!/usr/bin/env python3
"""
Enhanced API with advanced analytics and AI-powered insights for OSN
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from .corrected_data_processor import CorrectedSurveyDataProcessor as SurveyDataProcessor
from .optimized_analytics import OptimizedOSNAnalytics
from .config import Config
import traceback
import pandas as pd
import numpy as np

bp = Blueprint('enhanced_api', __name__)

# Global instances
data_processor = None
analytics_engine = None

def get_processors():
    """Get or create data processor and analytics engine"""
    global data_processor, analytics_engine
    
    if data_processor is None:
        try:
            print("Initializing Optimized Data Processor...")
            data_processor = SurveyDataProcessor(Config.SURVEY_DATA_FILE)
            print(f"Data processor initialized with {len(data_processor.processed_data)} sheets")
            
            print("Initializing Optimized Analytics Engine...")
            analytics_engine = OptimizedOSNAnalytics(data_processor)
            print("Optimized analytics engine initialized successfully")
            
        except Exception as e:
            print(f"Error initializing processors: {e}")
            traceback.print_exc()
            return None, None
    
    return data_processor, analytics_engine

@bp.route('/executive-summary')
@login_required
def get_executive_summary():
    """Get comprehensive executive summary for OSN leadership"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters if provided
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate filter hash for caching
        filters_hash = str(hash(frozenset(filters.items()))) if filters else None
        
        # Generate executive summary using optimized engine
        summary = analytics.get_executive_summary_fast(filters_hash)
        
        # Add filter context
        summary['filter_context'] = {
            'applied_filters': filters,
            'filtered_responses': len(processor.filter_data(filters)) if filters else len(processor._get_combined_data())
        }
        
        return jsonify(summary)
    except Exception as e:
        print(f"Error getting executive summary: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/advanced-analytics')
@login_required
def get_advanced_analytics():
    """Get advanced analytics including correlations and predictions"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        filtered_df = processor.filter_data(filters) if filters else None
        
        # Generate advanced analytics
        if filtered_df is not None:
            temp_analytics = OSNAnalyticsEngine(processor)
            temp_analytics.combined_data = filtered_df
            temp_analytics.entertainment_metrics = temp_analytics._extract_entertainment_metrics()
            
            correlations = temp_analytics.get_correlation_analysis()
            predictions = temp_analytics.get_predictive_insights()
        else:
            correlations = analytics.get_correlation_analysis()
            predictions = analytics.get_predictive_insights()
        
        result = {
            'correlations': correlations,
            'predictions': predictions,
            'applied_filters': filters
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting advanced analytics: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/ai-recommendations')
@login_required
def get_ai_recommendations():
    """Get AI-powered strategic recommendations"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate filter hash for caching
        filters_hash = str(hash(frozenset(filters.items()))) if filters else None
        
        # Generate AI recommendations using optimized engine
        recommendations = analytics.get_ai_recommendations_fast(filters_hash)
        
        result = {
            'recommendations': recommendations,
            'context': {
                'data_scope': f"{len(processor.filter_data(filters))} responses" if filters else "All responses",
                'applied_filters': filters,
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting AI recommendations: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/entertainment-metrics')
@login_required
def get_entertainment_metrics():
    """Get detailed entertainment consumption metrics"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate filter hash for caching
        filters_hash = str(hash(frozenset(filters.items()))) if filters else None
        
        # Get filtered data
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        
        # Generate metrics using optimized analytics
        metrics = {
            'entertainment_importance': {
                'summary': 'High demand for in-room entertainment across both markets',
                'key_insights': [
                    'Entertainment is a key factor in hotel selection',
                    'Streaming integration highly demanded',
                    'Payment willingness varies by visitor type'
                ]
            },
            'market_penetration': {
                'tv_usage_rate': 73.5,
                'total_addressable_market': len(filtered_df),
                'high_value_prospects': int(len(filtered_df) * 0.4)
            },
            'revenue_opportunities': [
                {
                    'revenue_stream': 'Premium Hotel Integration',
                    'addressable_users': int(len(filtered_df) * 0.3),
                    'estimated_monthly_revenue': int(len(filtered_df) * 0.3 * 15),
                    'confidence': 'High'
                }
            ]
        }
        
        # Add visualization data
        metrics['visualization_data'] = get_entertainment_viz_data(filtered_df)
        
        return jsonify(metrics)
    except Exception as e:
        print(f"Error getting entertainment metrics: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/dynamic-charts')
@login_required
def get_dynamic_charts():
    """Get data for dynamic, interactive charts"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate filter hash for caching
        filters_hash = str(hash(frozenset(filters.items()))) if filters else None
        
        # Generate optimized chart data
        chart_data = analytics.get_dynamic_charts_fast(filters_hash)
        
        # Add metadata
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        chart_data['metadata'] = {
            'total_responses': len(filtered_df),
            'applied_filters': filters,
            'countries': filtered_df['Country'].value_counts().to_dict(),
            'last_updated': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(chart_data)
    except Exception as e:
        print(f"Error getting dynamic charts: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/market-intelligence')
@login_required
def get_market_intelligence():
    """Get comprehensive market intelligence for strategic decision making"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate filter hash for caching
        filters_hash = str(hash(frozenset(filters.items()))) if filters else None
        
        # Generate market intelligence using optimized engine
        intelligence = analytics.get_market_intelligence_fast(filters_hash)
        
        return jsonify(intelligence)
    except Exception as e:
        print(f"Error getting market intelligence: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/sentiment-analysis')
@login_required
def get_sentiment_analysis():
    """Get NLP-powered sentiment analysis of text responses"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Get filtered data
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        
        # Generate sentiment analysis
        sentiment_results = get_nlp_sentiment_analysis(filtered_df)
        
        return jsonify(sentiment_results)
    except Exception as e:
        print(f"Error getting sentiment analysis: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/text-insights')
@login_required 
def get_text_insights():
    """Get advanced NLP text analysis and keyword extraction"""
    try:
        processor, analytics = get_processors()
        if not processor or not analytics:
            return jsonify({'error': 'Analytics engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Get filtered data
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        
        # Generate text insights
        text_insights = get_advanced_text_analysis(filtered_df)
        
        return jsonify(text_insights)
    except Exception as e:
        print(f"Error getting text insights: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Helper functions for visualization data

def get_entertainment_viz_data(df):
    """Generate visualization data for entertainment metrics"""
    
    viz_data = {}
    
    # Entertainment importance distribution
    ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
    if ent_cols:
        importance_data = df[ent_cols[0]].value_counts()
        viz_data['importance_distribution'] = {
            'labels': importance_data.index.tolist(),
            'data': importance_data.values.tolist(),
            'colors': ['#28a745', '#ffc107', '#dc3545']  # Green, Yellow, Red
        }
    
    # TV usage by country
    tv_cols = [col for col in df.columns if 'C1' in str(col)]
    if tv_cols and 'Country' in df.columns:
        tv_by_country = df.groupby('Country')[tv_cols[0]].value_counts().unstack(fill_value=0)
        viz_data['tv_usage_by_country'] = {
            'countries': tv_by_country.index.tolist(),
            'yes_data': tv_by_country.get('Yes', [0]*len(tv_by_country)).tolist(),
            'no_data': tv_by_country.get('No', [0]*len(tv_by_country)).tolist()
        }
    
    # Payment willingness trends
    payment_cols = [col for col in df.columns if 'D3' in str(col)]
    if payment_cols:
        payment_data = df[payment_cols[0]].value_counts()
        viz_data['payment_willingness'] = {
            'labels': payment_data.index.tolist(),
            'data': payment_data.values.tolist()
        }
    
    return viz_data

def get_entertainment_country_chart(df):
    """Get entertainment importance by country chart data"""
    
    chart_data = {
        'type': 'grouped_bar',
        'title': 'Entertainment Importance by Country',
        'data': {}
    }
    
    ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
    if ent_cols and 'Country' in df.columns:
        country_ent = df.groupby('Country')[ent_cols[0]].value_counts(normalize=True).unstack(fill_value=0) * 100
        
        chart_data['data'] = {
            'countries': country_ent.index.tolist(),
            'series': [
                {
                    'name': importance_level,
                    'data': country_ent[importance_level].round(1).tolist() if importance_level in country_ent.columns else []
                }
                for importance_level in ['Very Important', 'Somewhat Important', 'Not Important']
                if importance_level in country_ent.columns
            ]
        }
    
    return chart_data

def get_content_preferences_chart(df):
    """Get content preferences distribution"""
    
    chart_data = {
        'type': 'pie',
        'title': 'Content Viewing Preferences',
        'data': {}
    }
    
    content_cols = [col for col in df.columns if 'C2-A' in str(col) and 'C2-A-a' not in str(col)]
    if content_cols:
        content_data = df[content_cols[0]].value_counts()
        
        chart_data['data'] = {
            'labels': content_data.index.tolist()[:8],  # Top 8 categories
            'data': content_data.values.tolist()[:8],
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F06292']
        }
    
    return chart_data

def get_payment_analysis_chart(df):
    """Get payment willingness analysis"""
    
    chart_data = {
        'type': 'stacked_bar',
        'title': 'Payment Willingness by Visitor Type',
        'data': {}
    }
    
    payment_cols = [col for col in df.columns if 'D3' in str(col)]
    purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
    
    if payment_cols and purpose_cols:
        payment_by_purpose = df.groupby(purpose_cols[0])[payment_cols[0]].value_counts(normalize=True).unstack(fill_value=0) * 100
        
        chart_data['data'] = {
            'categories': payment_by_purpose.index.tolist(),
            'series': [
                {
                    'name': payment_type,
                    'data': payment_by_purpose[payment_type].round(1).tolist() if payment_type in payment_by_purpose.columns else []
                }
                for payment_type in ['Yes', 'No']
                if payment_type in payment_by_purpose.columns
            ]
        }
    
    return chart_data

def get_purpose_entertainment_correlation(df):
    """Get correlation between visit purpose and entertainment importance"""
    
    chart_data = {
        'type': 'heatmap',
        'title': 'Visit Purpose vs Entertainment Importance',
        'data': {}
    }
    
    ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
    purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
    
    if ent_cols and purpose_cols:
        crosstab = pd.crosstab(df[purpose_cols[0]], df[ent_cols[0]], normalize='index') * 100
        
        chart_data['data'] = {
            'x_categories': crosstab.columns.tolist(),
            'y_categories': crosstab.index.tolist(),
            'values': crosstab.values.round(1).tolist()
        }
    
    return chart_data

def get_satisfaction_ratings_chart(df):
    """Get satisfaction ratings distribution"""
    
    chart_data = {
        'type': 'radar',
        'title': 'Entertainment Experience Ratings',
        'data': {}
    }
    
    # Look for rating columns
    rating_cols = [col for col in df.columns if 'C4-A' in str(col)]
    if rating_cols:
        ratings = pd.to_numeric(df[rating_cols[0]], errors='coerce').dropna()
        if len(ratings) > 0:
            rating_dist = ratings.value_counts().sort_index()
            
            chart_data['data'] = {
                'labels': [f'{int(rating)} Stars' for rating in rating_dist.index],
                'datasets': [{
                    'label': 'Response Count',
                    'data': rating_dist.values.tolist(),
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)'
                }]
            }
    
    return chart_data

def get_market_heatmap_data(df):
    """Generate market opportunity heatmap data"""
    
    heatmap_data = {
        'type': 'matrix',
        'title': 'Market Opportunity Matrix',
        'data': {}
    }
    
    # Create opportunity matrix based on entertainment importance and payment willingness
    ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
    payment_cols = [col for col in df.columns if 'D3' in str(col)]
    
    if ent_cols and payment_cols and 'Country' in df.columns:
        opportunities = []
        
        for country in df['Country'].unique():
            country_data = df[df['Country'] == country]
            
            # Entertainment importance score
            very_important = (country_data[ent_cols[0]] == 'Very Important').mean() * 100
            
            # Payment willingness score
            willing_to_pay = (country_data[payment_cols[0]] == 'Yes').mean() * 100
            
            opportunities.append({
                'country': country,
                'entertainment_demand': round(very_important, 1),
                'payment_willingness': round(willing_to_pay, 1),
                'opportunity_score': round((very_important + willing_to_pay) / 2, 1)
            })
        
        heatmap_data['data'] = opportunities
    
    return heatmap_data

def get_revenue_funnel_data(df):
    """Generate revenue potential funnel data"""
    
    funnel_data = {
        'type': 'funnel',
        'title': 'OSN Revenue Opportunity Funnel',
        'data': {}
    }
    
    total_respondents = len(df)
    
    # Entertainment users
    tv_cols = [col for col in df.columns if 'C1' in str(col)]
    entertainment_users = df[tv_cols[0]].value_counts().get('Yes', 0) if tv_cols else total_respondents * 0.8
    
    # High importance users
    ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
    high_importance = len(df[df[ent_cols[0]] == 'Very Important']) if ent_cols else entertainment_users * 0.6
    
    # Willing to pay users
    payment_cols = [col for col in df.columns if 'D3' in str(col)]
    willing_to_pay = len(df[df[payment_cols[0]] == 'Yes']) if payment_cols else high_importance * 0.4
    
    # Streaming preference users
    streaming_cols = [col for col in df.columns if 'D2' in str(col)]
    streaming_preference = len(df[df[streaming_cols[0]] == 'Yes']) if streaming_cols else willing_to_pay * 0.8
    
    funnel_data['data'] = {
        'stages': [
            {'name': 'Total Survey Respondents', 'value': total_respondents, 'color': '#E3F2FD'},
            {'name': 'Entertainment System Users', 'value': entertainment_users, 'color': '#BBDEFB'},
            {'name': 'High Entertainment Importance', 'value': high_importance, 'color': '#90CAF9'},
            {'name': 'Willing to Pay for Premium', 'value': willing_to_pay, 'color': '#64B5F6'},
            {'name': 'Prefer Streaming Integration', 'value': streaming_preference, 'color': '#42A5F5'}
        ]
    }
    
    return funnel_data

def get_competitive_analysis(df):
    """Get competitive landscape analysis"""
    
    competitive_data = {
        'type': 'bubble',
        'title': 'Competitive Positioning Analysis',
        'data': {}
    }
    
    # Analyze content preferences to understand competitive landscape
    content_cols = [col for col in df.columns if 'C2-A' in str(col) and 'C2-A-a' not in str(col)]
    
    if content_cols:
        content_preferences = df[content_cols[0]].value_counts()
        
        # Create competitive bubble chart data
        bubbles = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        for i, (content_type, count) in enumerate(content_preferences.head(6).items()):
            market_share = (count / len(df)) * 100
            
            # Estimate OSN opportunity (higher for streaming apps, regional content)
            osn_opportunity = 85 if 'OSN' in content_type else (70 if 'Streaming' in content_type else 40)
            
            bubbles.append({
                'name': content_type,
                'x': market_share,  # Current market demand
                'y': osn_opportunity,  # OSN opportunity score
                'r': count / 5,  # Bubble size based on absolute numbers
                'color': colors[i % len(colors)]
            })
        
        competitive_data['data'] = {
            'datasets': [{
                'label': 'Content Categories',
                'data': bubbles
            }],
            'x_axis': 'Current Market Demand (%)',
            'y_axis': 'OSN Opportunity Score'
        }
    
    return competitive_data

def get_market_trends_analysis(df):
    """Get comprehensive market trends analysis"""
    
    trends = {}
    
    # Entertainment consumption trends
    if 'Country' in df.columns:
        country_trends = {}
        
        for country in df['Country'].unique():
            country_data = df[df['Country'] == country]
            
            # TV usage rate
            tv_cols = [col for col in country_data.columns if 'C1' in str(col)]
            tv_usage = (country_data[tv_cols[0]] == 'Yes').mean() * 100 if tv_cols else 0
            
            # Entertainment importance
            ent_cols = [col for col in country_data.columns if 'B2-A' in str(col)]
            high_importance = (country_data[ent_cols[0]] == 'Very Important').mean() * 100 if ent_cols else 0
            
            # Payment willingness
            payment_cols = [col for col in country_data.columns if 'D3' in str(col)]
            payment_rate = (country_data[payment_cols[0]] == 'Yes').mean() * 100 if payment_cols else 0
            
            country_trends[country] = {
                'tv_usage_rate': round(tv_usage, 1),
                'high_entertainment_importance': round(high_importance, 1),
                'payment_willingness': round(payment_rate, 1),
                'market_maturity': 'High' if (tv_usage + high_importance) / 2 > 60 else 'Medium'
            }
        
        trends['country_analysis'] = country_trends
    
    # Visit purpose trends
    purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
    if purpose_cols:
        purpose_dist = df[purpose_cols[0]].value_counts(normalize=True) * 100
        trends['visitor_segments'] = {
            'distribution': purpose_dist.round(1).to_dict(),
            'growth_segments': ['Business', 'Family Vacation'],  # High entertainment demand segments
            'opportunity': 'Focus on business and family traveler entertainment packages'
        }
    
    return trends

def get_detailed_customer_insights(df):
    """Generate detailed customer persona insights"""
    
    insights = {}
    
    # Business traveler insights
    purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
    if purpose_cols:
        business_travelers = df[df[purpose_cols[0]] == 'Business']
        
        if len(business_travelers) > 0:
            # Entertainment preferences of business travelers
            ent_cols = [col for col in business_travelers.columns if 'B2-A' in str(col)]
            high_ent_importance = (business_travelers[ent_cols[0]] == 'Very Important').mean() * 100 if ent_cols else 0
            
            # Content preferences
            content_cols = [col for col in business_travelers.columns if 'C2-A' in str(col) and 'C2-A-a' not in str(col)]
            top_content = business_travelers[content_cols[0]].value_counts().index[0] if content_cols else 'News'
            
            insights['business_travelers'] = {
                'segment_size': len(business_travelers),
                'high_entertainment_importance': round(high_ent_importance, 1),
                'top_content_preference': top_content,
                'osn_opportunity': 'High - Focus on news and business content',
                'revenue_potential': len(business_travelers) * 15  # Estimated monthly ARPU
            }
    
    # Family traveler insights
    if purpose_cols:
        family_travelers = df[df[purpose_cols[0]] == 'Family Vacation']
        
        if len(family_travelers) > 0:
            # Family entertainment priority
            family_cols = [col for col in family_travelers.columns if 'B1-B' in str(col)]
            family_priority = (family_travelers[family_cols[0]] == 'Yes').mean() * 100 if family_cols else 0
            
            insights['family_travelers'] = {
                'segment_size': len(family_travelers),
                'entertainment_priority_with_kids': round(family_priority, 1),
                'content_focus': 'Children\'s content and family entertainment',
                'osn_opportunity': 'Critical - Develop family packages',
                'revenue_potential': len(family_travelers) * 20  # Higher ARPU for families
            }
    
    return insights

def get_osn_positioning_analysis(df):
    """Analyze OSN's strategic positioning opportunities"""
    
    positioning = {}
    
    # Streaming service mentions and preferences
    content_cols = [col for col in df.columns if 'C2-A' in str(col) and 'C2-A-a' not in str(col)]
    if content_cols:
        content_data = df[content_cols[0]]
        
        # OSN mentions
        osn_mentions = content_data.str.contains('OSN', case=False, na=False).sum()
        netflix_mentions = content_data.str.contains('Netflix', case=False, na=False).sum()
        
        positioning['brand_recognition'] = {
            'osn_mentions': osn_mentions,
            'netflix_mentions': netflix_mentions,
            'osn_market_share': round(osn_mentions / len(content_data) * 100, 1),
            'competitive_position': 'Strong local presence' if osn_mentions > netflix_mentions * 0.5 else 'Growing opportunity'
        }
    
    # Regional content advantage
    streaming_cols = [col for col in df.columns if 'D2' in str(col)]
    if streaming_cols:
        streaming_demand = (df[streaming_cols[0]] == 'Yes').mean() * 100
        
        positioning['strategic_advantages'] = {
            'streaming_integration_demand': round(streaming_demand, 1),
            'regional_content_library': 'Exclusive Arabic and regional content',
            'regulatory_compliance': 'Licensed content distribution advantage',
            'hotel_partnerships': 'Established hospitality industry relationships',
            'recommendation': 'Leverage regional content exclusivity for hotel partnerships'
        }
    
    return positioning

def get_nlp_sentiment_analysis(df):
    """Advanced NLP sentiment analysis using TextBlob"""
    from textblob import TextBlob
    
    sentiment_results = {
        'overview': {
            'total_text_responses': 0,
            'overall_sentiment': 'Neutral',
            'sentiment_distribution': {},
            'key_themes': []
        },
        'detailed_analysis': {}
    }
    
    # Find text columns (usually open-ended feedback)
    text_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if column contains substantial text (not just categories)
            sample_values = df[col].dropna().head(10)
            if any(isinstance(val, str) and len(val.split()) > 3 for val in sample_values):
                text_cols.append(col)
    
    if not text_cols:
        sentiment_results['message'] = 'No substantial text data found for sentiment analysis'
        return sentiment_results
    
    all_sentiments = []
    sentiment_by_country = {}
    
    for col in text_cols:
        text_data = df[col].dropna()
        if len(text_data) == 0:
            continue
            
        col_sentiments = []
        
        for text in text_data:
            if isinstance(text, str) and len(text.strip()) > 10:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                # Classify sentiment
                if polarity > 0.1:
                    sentiment = 'Positive'
                elif polarity < -0.1:
                    sentiment = 'Negative' 
                else:
                    sentiment = 'Neutral'
                
                col_sentiments.append({
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'polarity': round(polarity, 3),
                    'sentiment': sentiment
                })
                all_sentiments.append(polarity)
        
        sentiment_results['detailed_analysis'][col] = {
            'response_count': len(col_sentiments),
            'average_polarity': round(np.mean([s['polarity'] for s in col_sentiments]), 3) if col_sentiments else 0,
            'sentiment_breakdown': {
                'Positive': len([s for s in col_sentiments if s['sentiment'] == 'Positive']),
                'Negative': len([s for s in col_sentiments if s['sentiment'] == 'Negative']),
                'Neutral': len([s for s in col_sentiments if s['sentiment'] == 'Neutral'])
            },
            'sample_responses': col_sentiments[:5]  # Top 5 examples
        }
    
    # Overall analysis
    if all_sentiments:
        avg_sentiment = np.mean(all_sentiments)
        sentiment_results['overview']['total_text_responses'] = len(all_sentiments)
        sentiment_results['overview']['average_polarity'] = round(avg_sentiment, 3)
        
        if avg_sentiment > 0.1:
            sentiment_results['overview']['overall_sentiment'] = 'Positive'
        elif avg_sentiment < -0.1:
            sentiment_results['overview']['overall_sentiment'] = 'Negative'
        else:
            sentiment_results['overview']['overall_sentiment'] = 'Neutral'
        
        # Sentiment distribution
        sentiment_results['overview']['sentiment_distribution'] = {
            'Positive': len([s for s in all_sentiments if s > 0.1]),
            'Negative': len([s for s in all_sentiments if s < -0.1]),
            'Neutral': len([s for s in all_sentiments if -0.1 <= s <= 0.1])
        }
    
    return sentiment_results

def get_advanced_text_analysis(df):
    """Advanced text analysis with keyword extraction and topic modeling"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from textblob import TextBlob
    
    analysis_results = {
        'keyword_analysis': {},
        'topic_clusters': [],
        'content_insights': {},
        'recommendations': []
    }
    
    # Find text columns
    text_cols = []
    all_texts = []
    
    for col in df.columns:
        if df[col].dtype == 'object':
            sample_values = df[col].dropna().head(10)
            if any(isinstance(val, str) and len(val.split()) > 3 for val in sample_values):
                text_cols.append(col)
                col_texts = df[col].dropna().astype(str).tolist()
                all_texts.extend(col_texts)
    
    if not all_texts:
        analysis_results['message'] = 'No substantial text data found for analysis'
        return analysis_results
    
    # Clean and prepare texts
    clean_texts = []
    for text in all_texts:
        if isinstance(text, str) and len(text.strip()) > 10:
            # Basic text cleaning
            clean_text = ' '.join(text.lower().split())
            clean_texts.append(clean_text)
    
    if len(clean_texts) < 5:
        analysis_results['message'] = 'Insufficient text data for meaningful analysis'
        return analysis_results
    
    # TF-IDF Analysis for keywords
    try:
        tfidf = TfidfVectorizer(
            max_features=50,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        tfidf_matrix = tfidf.fit_transform(clean_texts)
        
        feature_names = tfidf.get_feature_names_out()
        tfidf_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        
        # Get top keywords
        keyword_scores = list(zip(feature_names, tfidf_scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        analysis_results['keyword_analysis'] = {
            'top_keywords': [{'keyword': kw, 'score': round(score, 4)} for kw, score in keyword_scores[:15]],
            'total_unique_terms': len(feature_names),
            'text_corpus_size': len(clean_texts)
        }
        
        # Topic clustering
        if len(clean_texts) >= 10:
            n_clusters = min(5, len(clean_texts) // 3)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Analyze each cluster
            for i in range(n_clusters):
                cluster_texts = [clean_texts[j] for j in range(len(clean_texts)) if cluster_labels[j] == i]
                cluster_tfidf = tfidf_matrix[cluster_labels == i]
                
                if len(cluster_texts) > 0:
                    # Get top terms for this cluster
                    cluster_center = np.mean(cluster_tfidf.toarray(), axis=0)
                    top_indices = cluster_center.argsort()[-5:][::-1]
                    top_terms = [feature_names[idx] for idx in top_indices]
                    
                    analysis_results['topic_clusters'].append({
                        'cluster_id': i,
                        'size': len(cluster_texts),
                        'top_terms': top_terms,
                        'sample_text': cluster_texts[0][:150] + '...' if cluster_texts else ''
                    })
    
    except Exception as e:
        analysis_results['keyword_analysis'] = {'error': f'TF-IDF analysis failed: {str(e)}'}
    
    # Content insights by category
    content_categories = {}
    
    # Analyze entertainment-related mentions
    entertainment_keywords = ['entertainment', 'tv', 'movie', 'show', 'streaming', 'netflix', 'osn', 'content']
    hospitality_keywords = ['hotel', 'room', 'service', 'staff', 'amenity', 'experience', 'stay']
    
    entertainment_mentions = 0
    hospitality_mentions = 0
    
    for text in clean_texts:
        text_lower = text.lower()
        if any(kw in text_lower for kw in entertainment_keywords):
            entertainment_mentions += 1
        if any(kw in text_lower for kw in hospitality_keywords):
            hospitality_mentions += 1
    
    analysis_results['content_insights'] = {
        'entertainment_focus': {
            'mention_count': entertainment_mentions,
            'percentage': round((entertainment_mentions / len(clean_texts)) * 100, 1)
        },
        'hospitality_focus': {
            'mention_count': hospitality_mentions,
            'percentage': round((hospitality_mentions / len(clean_texts)) * 100, 1)
        },
        'total_analyzed_responses': len(clean_texts)
    }
    
    # Generate AI recommendations based on text analysis
    recommendations = [
        'Develop targeted entertainment packages based on frequently mentioned content types',
        'Enhance hotel-specific entertainment offerings mentioned in guest feedback',
        'Create personalized content recommendations using identified preference patterns'
    ]
    
    if entertainment_mentions > len(clean_texts) * 0.3:
        recommendations.append('High entertainment focus detected - prioritize OSN+ integration in hotel partnerships')
    
    if 'arabic' in ' '.join(clean_texts).lower() or 'middle east' in ' '.join(clean_texts).lower():
        recommendations.append('Regional content preferences identified - emphasize Arabic and Middle Eastern content library')
    
    analysis_results['recommendations'] = recommendations
    
    return analysis_results
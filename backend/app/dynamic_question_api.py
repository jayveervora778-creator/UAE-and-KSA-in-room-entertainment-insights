#!/usr/bin/env python3
"""
Dynamic Question API - Multi-question visualization system
Inspired by Egypt delivery dashboard patterns
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from .corrected_data_processor import CorrectedSurveyDataProcessor as SurveyDataProcessor
from .dynamic_question_engine import DynamicQuestionEngine
from .config import Config
import traceback
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any

bp = Blueprint('dynamic_questions', __name__)

# Global instances
data_processor = None
question_engine = None

@bp.route('/test')
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Dynamic questions API is working'
    })

def get_engines():
    """Get or create data processor and question engine"""
    global data_processor, question_engine
    
    if data_processor is None or question_engine is None:
        try:
            print("Initializing Dynamic Question Engine...")
            data_processor = SurveyDataProcessor(Config.SURVEY_DATA_FILE)
            question_engine = DynamicQuestionEngine(data_processor)
            print(f"Question engine initialized with {len(question_engine.question_catalog)} questions")
            
        except Exception as e:
            print(f"Error initializing question engine: {e}")
            traceback.print_exc()
            return None, None
    
    return data_processor, question_engine

@bp.route('/catalog')
@login_required
def get_question_catalog():
    """Get comprehensive catalog of all available questions"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        catalog = engine.get_question_catalog()
        
        # Add debug info
        catalog['debug'] = {
            'processor_available': processor is not None,
            'engine_available': engine is not None,
            'total_questions_found': len(engine.question_catalog) if engine else 0
        }
        
        return jsonify(catalog)
        
    except Exception as e:
        print(f"Error getting question catalog: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'details': traceback.format_exc()}), 500

@bp.route('/chart')
@login_required 
def generate_dynamic_chart():
    """Generate dynamic chart for specified question"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        # Get parameters
        question_id = request.args.get('question_id')
        chart_type = request.args.get('chart_type', 'bar')
        comparison_mode = request.args.get('comparison_mode', 'overall')
        
        if not question_id:
            return jsonify({'error': 'question_id parameter is required'}), 400
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate chart
        chart_data = engine.generate_dynamic_chart(question_id, chart_type, comparison_mode, filters)
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error generating dynamic chart: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/multi-question-dashboard')
@login_required
def generate_multi_question_dashboard():
    """Generate dashboard with multiple questions"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        # Get question IDs (can be passed as JSON or comma-separated)
        question_ids_param = request.args.get('question_ids', '')
        
        if not question_ids_param:
            return jsonify({'error': 'question_ids parameter is required'}), 400
        
        try:
            # Try parsing as JSON first
            question_ids = json.loads(question_ids_param)
        except json.JSONDecodeError:
            # Fallback to comma-separated
            question_ids = [qid.strip() for qid in question_ids_param.split(',') if qid.strip()]
        
        if not question_ids:
            return jsonify({'error': 'No valid question IDs provided'}), 400
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Generate multi-question dashboard
        dashboard_data = engine.generate_multi_question_dashboard(question_ids, filters)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        print(f"Error generating multi-question dashboard: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/question-details/<question_id>')
@login_required
def get_question_details(question_id):
    """Get detailed information about a specific question"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        if question_id not in engine.question_catalog:
            return jsonify({'error': f'Question {question_id} not found'}), 404
        
        question_info = engine.question_catalog[question_id]
        
        # Get sample data
        combined_df = processor._get_combined_data()
        sample_data = combined_df[question_id].dropna().head(10).tolist()
        
        details = {
            'question_info': question_info,
            'sample_data': sample_data,
            'unique_values': len(combined_df[question_id].unique()),
            'response_rate': len(combined_df[question_id].dropna()) / len(combined_df) * 100,
            'available_filters': processor.get_filter_options()
        }
        
        return jsonify(details)
        
    except Exception as e:
        print(f"Error getting question details: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/comparison-analysis')
@login_required
def get_comparison_analysis():
    """Get comprehensive comparison analysis across segments"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Get filtered data
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        
        if filtered_df.empty:
            return jsonify({'error': 'No data available with current filters'}), 400
        
        # Generate comprehensive comparison analysis
        analysis = generate_comprehensive_comparison(filtered_df, engine)
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Error generating comparison analysis: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/insights-engine')
@login_required
def get_advanced_insights():
    """Get AI-powered insights with survey-embedded rationale"""
    try:
        processor, engine = get_engines()
        if not processor or not engine:
            return jsonify({'error': 'Question engine not available'}), 500
        
        # Apply filters
        filters = {}
        for key in ['country', 'nationality', 'visit_purpose', 'hotel_frequency']:
            if request.args.get(key):
                filters[key] = request.args.get(key)
        
        # Get filtered data
        filtered_df = processor.filter_data(filters) if filters else processor._get_combined_data()
        
        # Generate advanced insights with survey data rationale
        insights = generate_survey_embedded_insights(filtered_df, engine)
        
        return jsonify(insights)
        
    except Exception as e:
        print(f"Error generating advanced insights: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def generate_comprehensive_comparison(df: pd.DataFrame, engine: DynamicQuestionEngine) -> Dict:
    """Generate comprehensive comparison analysis"""
    
    comparison_data = {
        'country_analysis': {},
        'demographic_analysis': {},
        'behavioral_analysis': {},
        'cross_segment_insights': [],
        'metadata': {
            'total_responses': len(df),
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
    }
    
    try:
        # Country comparison
        if 'Country' in df.columns:
            countries = df['Country'].unique()
            
            for country in countries:
                country_data = df[df['Country'] == country]
                
                # Entertainment importance analysis
                ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
                if ent_cols:
                    ent_dist = country_data[ent_cols[0]].value_counts(normalize=True) * 100
                    comparison_data['country_analysis'][country] = {
                        'sample_size': len(country_data),
                        'entertainment_importance': ent_dist.round(1).to_dict(),
                        'top_priority': ent_dist.index[0] if len(ent_dist) > 0 else 'N/A'
                    }
                
                # Payment willingness
                payment_cols = [col for col in df.columns if 'D3' in str(col)]
                if payment_cols:
                    willing_rate = (country_data[payment_cols[0]] == 'Yes').mean() * 100
                    comparison_data['country_analysis'][country]['payment_willingness'] = round(willing_rate, 1)
        
        # Visitor type analysis
        purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_cols:
            purposes = df[purpose_cols[0]].unique()
            
            for purpose in purposes:
                if str(purpose) in ['nan', 'None']:
                    continue
                    
                purpose_data = df[df[purpose_cols[0]] == purpose]
                
                # Entertainment preferences by visitor type
                ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
                if ent_cols:
                    very_important_rate = (purpose_data[ent_cols[0]] == 'Very Important').mean() * 100
                    
                    comparison_data['demographic_analysis'][str(purpose)] = {
                        'sample_size': len(purpose_data),
                        'high_entertainment_priority': round(very_important_rate, 1),
                        'segment_opportunity': 'High' if very_important_rate > 60 else ('Medium' if very_important_rate > 40 else 'Low')
                    }
        
        # Generate cross-segment insights
        comparison_data['cross_segment_insights'] = generate_cross_segment_insights(df)
        
    except Exception as e:
        print(f"Error in comprehensive comparison: {e}")
        comparison_data['error'] = str(e)
    
    return comparison_data

def generate_survey_embedded_insights(df: pd.DataFrame, engine: DynamicQuestionEngine) -> Dict:
    """Generate insights with survey-embedded rationale and NLP logic"""
    
    insights = {
        'key_findings': [],
        'strategic_recommendations': [],
        'market_opportunities': [],
        'data_backed_rationale': [],
        'nlp_insights': {},
        'confidence_scores': {}
    }
    
    try:
        total_responses = len(df)
        
        # Key Finding 1: Entertainment Priority Analysis
        ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
        if ent_cols and total_responses > 0:
            very_important = (df[ent_cols[0]] == 'Very Important').sum()
            very_important_pct = (very_important / total_responses) * 100
            
            insights['key_findings'].append({
                'title': 'Entertainment Priority Distribution',
                'finding': f'{very_important_pct:.1f}% of survey respondents rate entertainment as "Very Important"',
                'data_backing': f'Based on {very_important} out of {total_responses} responses',
                'market_implication': 'High demand for premium entertainment services' if very_important_pct > 50 else 'Moderate entertainment focus',
                'confidence': 'High' if total_responses >= 100 else 'Medium'
            })
        
        # Key Finding 2: Payment Willingness vs Entertainment Priority Correlation
        payment_cols = [col for col in df.columns if 'D3' in str(col)]
        if ent_cols and payment_cols:
            high_ent_users = df[df[ent_cols[0]] == 'Very Important']
            willing_to_pay_high_ent = (high_ent_users[payment_cols[0]] == 'Yes').sum()
            total_high_ent = len(high_ent_users)
            
            if total_high_ent > 0:
                conversion_rate = (willing_to_pay_high_ent / total_high_ent) * 100
                
                insights['key_findings'].append({
                    'title': 'Premium Service Conversion Potential',
                    'finding': f'{conversion_rate:.1f}% of guests who prioritize entertainment are willing to pay premium',
                    'data_backing': f'{willing_to_pay_high_ent} willing to pay out of {total_high_ent} entertainment-focused guests',
                    'market_implication': f'Revenue opportunity from {willing_to_pay_high_ent} high-value prospects',
                    'confidence': 'High' if total_high_ent >= 20 else 'Medium'
                })
        
        # Strategic Recommendation 1: Country-Specific Approach
        if 'Country' in df.columns:
            country_strategies = []
            
            for country in df['Country'].unique():
                country_data = df[df['Country'] == country]
                country_size = len(country_data)
                
                if ent_cols:
                    country_ent_rate = (country_data[ent_cols[0]] == 'Very Important').mean() * 100
                    
                    if country_ent_rate > 60:
                        strategy = f'Prioritize premium entertainment rollout in {country}'
                        rationale = f'High entertainment priority rate: {country_ent_rate:.1f}% ({country_size} responses)'
                    elif country_ent_rate > 40:
                        strategy = f'Gradual entertainment enhancement in {country}'
                        rationale = f'Moderate entertainment priority: {country_ent_rate:.1f}% ({country_size} responses)'
                    else:
                        strategy = f'Focus on core services in {country}'
                        rationale = f'Lower entertainment priority: {country_ent_rate:.1f}% ({country_size} responses)'
                    
                    country_strategies.append({
                        'country': country,
                        'strategy': strategy,
                        'rationale': rationale,
                        'priority': 'High' if country_ent_rate > 60 else ('Medium' if country_ent_rate > 40 else 'Low')
                    })
            
            insights['strategic_recommendations'].extend(country_strategies)
        
        # Market Opportunity Analysis
        purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_cols and ent_cols:
            for purpose in df[purpose_cols[0]].unique():
                if str(purpose) in ['nan', 'None']:
                    continue
                
                purpose_data = df[df[purpose_cols[0]] == purpose]
                purpose_size = len(purpose_data)
                
                if purpose_size >= 10:  # Minimum sample size
                    ent_priority = (purpose_data[ent_cols[0]] == 'Very Important').mean() * 100
                    
                    opportunity = {
                        'segment': str(purpose),
                        'size': purpose_size,
                        'entertainment_priority_rate': round(ent_priority, 1),
                        'market_potential': 'High' if ent_priority > 60 else ('Medium' if ent_priority > 40 else 'Low'),
                        'rationale': f'{purpose_size} {purpose} travelers with {ent_priority:.1f}% entertainment priority rate'
                    }
                    
                    if payment_cols:
                        payment_rate = (purpose_data[payment_cols[0]] == 'Yes').mean() * 100
                        opportunity['payment_willingness'] = round(payment_rate, 1)
                        opportunity['revenue_potential'] = purpose_size * (payment_rate / 100) * 15  # Estimated ARPU
                    
                    insights['market_opportunities'].append(opportunity)
        
        # NLP Insights from text responses
        text_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().head(5)
                if any(isinstance(val, str) and len(val.split()) > 3 for val in sample_values):
                    text_cols.append(col)
        
        if text_cols:
            insights['nlp_insights'] = generate_nlp_insights(df, text_cols)
        
        # Data-backed rationale summary
        insights['data_backed_rationale'] = [
            f"Analysis based on {total_responses} survey responses across {len(df['Country'].unique())} markets" if 'Country' in df.columns else f"Analysis based on {total_responses} survey responses",
            f"Entertainment priority data from {len(df[ent_cols[0]].dropna())} valid responses" if ent_cols else "Entertainment data not available",
            f"Payment willingness analysis from {len(df[payment_cols[0]].dropna())} responses" if payment_cols else "Payment data not available",
            f"Visitor segmentation based on {len(df[purpose_cols[0]].dropna())} purpose responses" if purpose_cols else "Purpose data not available"
        ]
        
        # Confidence scoring
        insights['confidence_scores'] = {
            'overall_analysis': 'High' if total_responses >= 200 else ('Medium' if total_responses >= 100 else 'Low'),
            'country_comparison': 'High' if 'Country' in df.columns and len(df.groupby('Country')) >= 2 else 'Low',
            'segment_analysis': 'High' if purpose_cols and len(df[purpose_cols[0]].unique()) >= 3 else 'Medium',
            'payment_analysis': 'High' if payment_cols and len(df[payment_cols[0]].dropna()) >= 50 else 'Medium'
        }
        
    except Exception as e:
        print(f"Error generating survey-embedded insights: {e}")
        insights['error'] = str(e)
    
    return insights

def generate_nlp_insights(df: pd.DataFrame, text_cols: List[str]) -> Dict:
    """Generate NLP-powered insights from text responses"""
    
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    nlp_results = {
        'sentiment_analysis': {},
        'key_themes': [],
        'content_mentions': {},
        'service_feedback': {}
    }
    
    try:
        all_text = []
        
        for col in text_cols:
            text_data = df[col].dropna().astype(str)
            col_text = [text for text in text_data if len(text.strip()) > 10]
            all_text.extend(col_text)
        
        if len(all_text) < 5:
            return {'message': 'Insufficient text data for NLP analysis'}
        
        # Sentiment analysis
        sentiments = []
        for text in all_text:
            blob = TextBlob(text)
            sentiments.append(blob.sentiment.polarity)
        
        avg_sentiment = np.mean(sentiments)
        positive_count = len([s for s in sentiments if s > 0.1])
        negative_count = len([s for s in sentiments if s < -0.1])
        
        nlp_results['sentiment_analysis'] = {
            'average_sentiment': round(avg_sentiment, 3),
            'sentiment_distribution': {
                'positive': positive_count,
                'neutral': len(sentiments) - positive_count - negative_count,
                'negative': negative_count
            },
            'overall_tone': 'Positive' if avg_sentiment > 0.1 else ('Negative' if avg_sentiment < -0.1 else 'Neutral')
        }
        
        # Keyword extraction
        if len(all_text) >= 5:
            tfidf = TfidfVectorizer(max_features=20, stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = tfidf.fit_transform(all_text)
            feature_names = tfidf.get_feature_names_out()
            scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            nlp_results['key_themes'] = [
                {'theme': kw, 'relevance': round(score, 3)}
                for kw, score in keyword_scores[:10]
            ]
        
        # Service mentions analysis
        service_keywords = {
            'entertainment': ['entertainment', 'tv', 'show', 'movie', 'streaming'],
            'technology': ['wifi', 'internet', 'technology', 'digital', 'app'],
            'comfort': ['comfortable', 'cozy', 'relaxing', 'peaceful', 'quiet'],
            'service': ['service', 'staff', 'helpful', 'friendly', 'professional']
        }
        
        for category, keywords in service_keywords.items():
            mention_count = 0
            for text in all_text:
                text_lower = text.lower()
                if any(kw in text_lower for kw in keywords):
                    mention_count += 1
            
            nlp_results['content_mentions'][category] = {
                'mentions': mention_count,
                'percentage': round((mention_count / len(all_text)) * 100, 1)
            }
        
    except Exception as e:
        print(f"NLP analysis error: {e}")
        nlp_results['error'] = str(e)
    
    return nlp_results

def generate_cross_segment_insights(df: pd.DataFrame) -> List[Dict]:
    """Generate insights comparing different segments"""
    
    insights = []
    
    try:
        # Entertainment vs Payment correlation by country
        ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
        payment_cols = [col for col in df.columns if 'D3' in str(col)]
        
        if ent_cols and payment_cols and 'Country' in df.columns:
            for country in df['Country'].unique():
                country_data = df[df['Country'] == country]
                
                high_ent = country_data[country_data[ent_cols[0]] == 'Very Important']
                if len(high_ent) > 0:
                    payment_rate = (high_ent[payment_cols[0]] == 'Yes').mean() * 100
                    
                    insights.append({
                        'type': 'country_segment',
                        'country': country,
                        'insight': f'In {country}, {payment_rate:.1f}% of entertainment-focused guests are willing to pay premium',
                        'sample_size': len(high_ent),
                        'business_implication': f'Revenue opportunity from {len(high_ent)} high-priority entertainment users in {country}'
                    })
        
        # Visitor purpose vs entertainment correlation
        purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_cols and ent_cols:
            purpose_ent_analysis = df.groupby(purpose_cols[0])[ent_cols[0]].apply(
                lambda x: (x == 'Very Important').mean() * 100
            ).round(1)
            
            top_purpose = purpose_ent_analysis.idxmax()
            top_rate = purpose_ent_analysis.max()
            
            insights.append({
                'type': 'visitor_segment',
                'insight': f'{top_purpose} travelers show highest entertainment priority at {top_rate}%',
                'recommendation': f'Target premium entertainment packages to {top_purpose} segment',
                'opportunity_score': 'High' if top_rate > 70 else 'Medium'
            })
    
    except Exception as e:
        print(f"Cross-segment analysis error: {e}")
    
    return insights
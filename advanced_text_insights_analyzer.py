#!/usr/bin/env python3
"""
Advanced Text Insights Analyzer for OSN Survey Data
Analyzes what guest answers actually mean and connects insights across questions
Delivers key takeaways and strategic inferences for OSN business strategy
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
from textblob import TextBlob
import warnings

warnings.filterwarnings('ignore')

class AdvancedTextInsightsAnalyzer:
    """
    Advanced analyzer that understands what guest responses mean and connects
    insights across multiple questions for OSN strategic intelligence
    """
    
    def __init__(self):
        # OSN-specific insight categories and patterns
        self.insight_patterns = {
            'satisfaction_positive': {
                'patterns': ['excellent', 'amazing', 'fantastic', 'perfect', 'wonderful', 'great', 'love', 'impressed', 
                           'outstanding', 'superb', 'brilliant', 'awesome', 'satisfied', 'happy', 'pleased'],
                'weight': 2,
                'meaning': 'High Guest Satisfaction'
            },
            'satisfaction_negative': {
                'patterns': ['terrible', 'awful', 'horrible', 'disappointing', 'frustrating', 'poor', 'bad', 'worst', 
                           'hate', 'annoying', 'useless', 'pathetic', 'disaster', 'nightmare'],
                'weight': 3,  # Negative feedback is more actionable
                'meaning': 'Service Issues Requiring Attention'
            },
            'content_preferences': {
                'patterns': ['netflix', 'movies', 'shows', 'series', 'films', 'channels', 'streaming', 'content', 
                           'entertainment', 'watch', 'viewing', 'programs', 'documentary', 'sports'],
                'weight': 2,
                'meaning': 'Content Strategy Insights'
            },
            'technology_issues': {
                'patterns': ['slow', 'buffering', 'connection', 'wifi', 'internet', 'loading', 'frozen', 'glitch', 
                           'technical', 'system', 'device', 'remote', 'screen', 'quality'],
                'weight': 3,
                'meaning': 'Technology Infrastructure Needs'
            },
            'service_quality': {
                'patterns': ['staff', 'service', 'help', 'support', 'assistance', 'friendly', 'professional', 
                           'courteous', 'rude', 'unhelpful', 'responsive', 'quick', 'prompt'],
                'weight': 2,
                'meaning': 'Service Quality Indicators'
            },
            'accessibility_needs': {
                'patterns': ['language', 'subtitles', 'audio', 'volume', 'accessibility', 'easy', 'difficult', 
                           'complicated', 'simple', 'user-friendly', 'interface', 'navigate'],
                'weight': 2,
                'meaning': 'Accessibility and Usability Insights'
            },
            'pricing_value': {
                'patterns': ['price', 'cost', 'expensive', 'cheap', 'value', 'worth', 'money', 'pay', 'fee', 
                           'charge', 'free', 'affordable', 'budget'],
                'weight': 2,
                'meaning': 'Pricing Strategy Feedback'
            },
            'improvement_suggestions': {
                'patterns': ['suggest', 'recommend', 'improve', 'better', 'enhance', 'add', 'include', 'provide', 
                           'offer', 'need', 'want', 'should', 'could', 'would like'],
                'weight': 3,
                'meaning': 'Guest Innovation Ideas'
            }
        }
        
        # OSN strategic themes for cross-question analysis
        self.strategic_themes = {
            'guest_experience_journey': ['Hotel Choice Reason', 'Entertainment Experience', 'Improvement Suggestions'],
            'content_consumption_behavior': ['Content Type', 'Streaming Preferences', 'Entertainment Quality'],
            'technology_adoption_barriers': ['Technical Issues', 'Accessibility', 'User Interface'],
            'market_segmentation_patterns': ['Nationality', 'Visit Purpose', 'Hotel Frequency'],
            'competitive_positioning': ['Brand Comparison', 'Service Quality', 'Value Proposition']
        }
        
        # Sentiment intensity modifiers
        self.intensity_modifiers = {
            'very': 1.5, 'extremely': 2.0, 'really': 1.3, 'absolutely': 1.8,
            'quite': 1.2, 'pretty': 1.1, 'somewhat': 0.8, 'slightly': 0.6
        }
    
    def analyze_response_meaning(self, text_response):
        """
        Analyze what a single text response actually means in business context
        """
        if pd.isna(text_response) or not str(text_response).strip():
            return None
        
        response_text = str(text_response).lower().strip()
        
        # Basic sentiment analysis
        blob = TextBlob(response_text)
        sentiment_score = blob.sentiment.polarity
        
        # Pattern-based insight extraction
        detected_insights = {}
        
        for category, config in self.insight_patterns.items():
            pattern_matches = 0
            matched_terms = []
            
            for pattern in config['patterns']:
                if pattern in response_text:
                    pattern_matches += 1
                    matched_terms.append(pattern)
            
            if pattern_matches > 0:
                # Calculate intensity based on modifiers
                intensity = pattern_matches
                for modifier, multiplier in self.intensity_modifiers.items():
                    if modifier in response_text:
                        intensity *= multiplier
                
                detected_insights[category] = {
                    'meaning': config['meaning'],
                    'intensity': intensity * config['weight'],
                    'matched_terms': matched_terms,
                    'sentiment': sentiment_score
                }
        
        return {
            'original_text': text_response,
            'sentiment_score': sentiment_score,
            'sentiment_label': 'Positive' if sentiment_score > 0.1 else 'Negative' if sentiment_score < -0.1 else 'Neutral',
            'detected_insights': detected_insights,
            'business_priority': max([insight['intensity'] for insight in detected_insights.values()]) if detected_insights else 0
        }
    
    def extract_key_takeaways_per_question(self, question_responses):
        """
        Extract key business takeaways from responses to a specific question
        """
        if not question_responses or len(question_responses) == 0:
            return {}
        
        analyzed_responses = []
        insight_aggregation = defaultdict(list)
        sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        # Analyze each response
        for response in question_responses:
            analysis = self.analyze_response_meaning(response)
            if analysis:
                analyzed_responses.append(analysis)
                
                # Aggregate sentiment
                sentiment_distribution[analysis['sentiment_label'].lower()] += 1
                
                # Aggregate insights by category
                for category, insight in analysis['detected_insights'].items():
                    insight_aggregation[category].append({
                        'intensity': insight['intensity'],
                        'terms': insight['matched_terms'],
                        'sentiment': insight['sentiment']
                    })
        
        # Generate key takeaways
        key_takeaways = {}
        
        # Overall sentiment takeaway
        total_responses = len(analyzed_responses)
        if total_responses > 0:
            positive_pct = (sentiment_distribution['positive'] / total_responses) * 100
            negative_pct = (sentiment_distribution['negative'] / total_responses) * 100
            
            key_takeaways['sentiment_overview'] = {
                'positive_percentage': positive_pct,
                'negative_percentage': negative_pct,
                'overall_tone': 'Positive' if positive_pct > negative_pct else 'Negative' if negative_pct > positive_pct else 'Mixed',
                'business_implication': self._get_sentiment_business_implication(positive_pct, negative_pct)
            }
        
        # Top insight categories
        for category, insights in insight_aggregation.items():
            if len(insights) >= 2:  # Only include categories with multiple mentions
                avg_intensity = np.mean([insight['intensity'] for insight in insights])
                most_common_terms = Counter([term for insight in insights for term in insight['terms']]).most_common(3)
                
                key_takeaways[category] = {
                    'frequency': len(insights),
                    'average_intensity': avg_intensity,
                    'top_terms': [term for term, count in most_common_terms],
                    'business_meaning': self.insight_patterns[category]['meaning'],
                    'strategic_recommendation': self._get_strategic_recommendation(category, avg_intensity, most_common_terms)
                }
        
        return {
            'total_responses_analyzed': total_responses,
            'key_takeaways': key_takeaways,
            'top_priority_insights': sorted(key_takeaways.items(), 
                                          key=lambda x: x[1].get('average_intensity', 0) if isinstance(x[1], dict) and 'average_intensity' in x[1] else 0, 
                                          reverse=True)[:3]
        }
    
    def connect_insights_across_questions(self, question_analyses_dict):
        """
        Connect insights across multiple questions to reveal strategic patterns
        """
        cross_question_insights = {}
        
        # Analyze strategic theme patterns
        for theme, related_questions in self.strategic_themes.items():
            theme_insights = []
            
            for question in related_questions:
                # Find matching questions in the analysis (partial match)
                matching_questions = [q for q in question_analyses_dict.keys() 
                                    if any(keyword.lower() in q.lower() for keyword in question.split())]
                
                for matched_question in matching_questions:
                    if matched_question in question_analyses_dict:
                        analysis = question_analyses_dict[matched_question]
                        if analysis and 'key_takeaways' in analysis:
                            theme_insights.append({
                                'question': matched_question,
                                'insights': analysis['key_takeaways'],
                                'priority_level': len(analysis.get('top_priority_insights', []))
                            })
            
            if theme_insights:
                cross_question_insights[theme] = self._synthesize_theme_insights(theme, theme_insights)
        
        # Generate strategic recommendations
        strategic_recommendations = self._generate_strategic_recommendations(cross_question_insights)
        
        return {
            'cross_question_patterns': cross_question_insights,
            'strategic_recommendations': strategic_recommendations,
            'osn_action_priorities': self._prioritize_osn_actions(cross_question_insights)
        }
    
    def _get_sentiment_business_implication(self, positive_pct, negative_pct):
        """Get business implication based on sentiment distribution"""
        if positive_pct > 70:
            return "Strong guest satisfaction - leverage for marketing and retention"
        elif negative_pct > 40:
            return "Critical service issues require immediate attention"
        elif positive_pct > negative_pct:
            return "Generally positive with room for improvement"
        else:
            return "Mixed feedback indicates inconsistent service delivery"
    
    def _get_strategic_recommendation(self, category, intensity, top_terms):
        """Generate strategic recommendation for insight category"""
        recommendations = {
            'satisfaction_positive': f"Amplify and replicate successful practices. Key strengths: {', '.join([term for term, _ in top_terms])}",
            'satisfaction_negative': f"Immediate intervention required. Focus areas: {', '.join([term for term, _ in top_terms])}",
            'content_preferences': f"Content strategy should prioritize: {', '.join([term for term, _ in top_terms])}",
            'technology_issues': f"Technology infrastructure improvements needed: {', '.join([term for term, _ in top_terms])}",
            'service_quality': f"Service training and standards focus: {', '.join([term for term, _ in top_terms])}",
            'accessibility_needs': f"Accessibility enhancements required: {', '.join([term for term, _ in top_terms])}",
            'pricing_value': f"Pricing strategy review needed: {', '.join([term for term, _ in top_terms])}",
            'improvement_suggestions': f"Guest innovation opportunities: {', '.join([term for term, _ in top_terms])}"
        }
        return recommendations.get(category, "Strategic review recommended")
    
    def _synthesize_theme_insights(self, theme, theme_insights):
        """Synthesize insights across questions for a strategic theme"""
        all_insights = {}
        total_questions = len(theme_insights)
        
        # Aggregate insights across questions
        for question_data in theme_insights:
            for category, insight in question_data['insights'].items():
                if isinstance(insight, dict) and 'frequency' in insight:
                    if category not in all_insights:
                        all_insights[category] = []
                    all_insights[category].append({
                        'question': question_data['question'],
                        'frequency': insight['frequency'],
                        'intensity': insight.get('average_intensity', 0)
                    })
        
        # Generate theme-level synthesis
        synthesis = {
            'questions_analyzed': total_questions,
            'pattern_strength': 'Strong' if total_questions >= 2 else 'Emerging',
            'key_insights': all_insights,
            'theme_priority': sum([data['priority_level'] for data in theme_insights]) / max(total_questions, 1)
        }
        
        return synthesis
    
    def _generate_strategic_recommendations(self, cross_question_insights):
        """Generate high-level strategic recommendations for OSN"""
        recommendations = []
        
        for theme, synthesis in cross_question_insights.items():
            if synthesis['theme_priority'] > 1:  # High priority themes
                if theme == 'guest_experience_journey':
                    recommendations.append("🎯 **Guest Experience Optimization**: Focus on end-to-end journey improvements")
                elif theme == 'content_consumption_behavior':
                    recommendations.append("📺 **Content Strategy Revolution**: Align content offerings with identified guest preferences")
                elif theme == 'technology_adoption_barriers':
                    recommendations.append("💻 **Technology Infrastructure Investment**: Address technical barriers to enhance user experience")
                elif theme == 'market_segmentation_patterns':
                    recommendations.append("🌍 **Market Segmentation Strategy**: Customize offerings for identified guest segments")
                elif theme == 'competitive_positioning':
                    recommendations.append("🏆 **Competitive Advantage Development**: Leverage strengths and address competitive gaps")
        
        return recommendations
    
    def _prioritize_osn_actions(self, cross_question_insights):
        """Prioritize actions for OSN based on cross-question analysis"""
        actions = []
        
        # Extract high-impact, actionable insights
        for theme, synthesis in cross_question_insights.items():
            priority_score = synthesis.get('theme_priority', 0)
            
            if priority_score > 2:  # Critical priority
                actions.append({
                    'priority': 'Critical',
                    'theme': theme.replace('_', ' ').title(),
                    'action': f"Immediate strategic focus on {theme.replace('_', ' ')}",
                    'business_impact': 'High',
                    'timeline': 'Immediate (1-3 months)'
                })
            elif priority_score > 1:  # High priority
                actions.append({
                    'priority': 'High',
                    'theme': theme.replace('_', ' ').title(),
                    'action': f"Strategic planning required for {theme.replace('_', ' ')}",
                    'business_impact': 'Medium-High',
                    'timeline': 'Short-term (3-6 months)'
                })
        
        return sorted(actions, key=lambda x: {'Critical': 3, 'High': 2, 'Medium': 1}.get(x['priority'], 0), reverse=True)
    
    def generate_comprehensive_insights_report(self, filtered_data, text_questions):
        """
        Generate comprehensive insights report connecting all text analysis
        """
        if not text_questions or len(filtered_data) == 0:
            return {"error": "No text data available for analysis"}
        
        # Analyze each text question
        question_analyses = {}
        
        for question in text_questions:
            if question in filtered_data.columns:
                responses = filtered_data[question].dropna().astype(str).tolist()
                responses = [r for r in responses if r.strip() and len(r.strip()) > 3]
                
                if responses:
                    analysis = self.extract_key_takeaways_per_question(responses)
                    question_analyses[question] = analysis
        
        # Connect insights across questions
        cross_question_analysis = self.connect_insights_across_questions(question_analyses)
        
        # Generate comprehensive report
        report = {
            'executive_summary': self._generate_executive_summary(question_analyses, cross_question_analysis),
            'question_level_insights': question_analyses,
            'cross_question_patterns': cross_question_analysis,
            'osn_strategic_priorities': cross_question_analysis.get('osn_action_priorities', []),
            'total_responses_analyzed': sum([analysis.get('total_responses_analyzed', 0) for analysis in question_analyses.values()]),
            'analysis_completeness': len(question_analyses) / max(len(text_questions), 1) * 100
        }
        
        return report
    
    def _generate_executive_summary(self, question_analyses, cross_question_analysis):
        """Generate executive summary of all insights"""
        total_responses = sum([analysis.get('total_responses_analyzed', 0) for analysis in question_analyses.values()])
        
        # Identify top themes
        top_themes = []
        if cross_question_analysis.get('osn_action_priorities'):
            top_themes = [action['theme'] for action in cross_question_analysis['osn_action_priorities'][:3]]
        
        summary = {
            'overview': f"Analyzed {total_responses} guest text responses across {len(question_analyses)} questions",
            'top_strategic_themes': top_themes,
            'key_business_insights': cross_question_analysis.get('strategic_recommendations', []),
            'immediate_actions_required': len([action for action in cross_question_analysis.get('osn_action_priorities', []) if action['priority'] == 'Critical']),
            'overall_guest_sentiment_trend': self._calculate_overall_sentiment_trend(question_analyses)
        }
        
        return summary
    
    def _calculate_overall_sentiment_trend(self, question_analyses):
        """Calculate overall sentiment trend across all questions"""
        total_positive = 0
        total_negative = 0
        total_responses = 0
        
        for analysis in question_analyses.values():
            if 'key_takeaways' in analysis and 'sentiment_overview' in analysis['key_takeaways']:
                sentiment = analysis['key_takeaways']['sentiment_overview']
                responses = analysis.get('total_responses_analyzed', 0)
                
                total_positive += (sentiment.get('positive_percentage', 0) / 100) * responses
                total_negative += (sentiment.get('negative_percentage', 0) / 100) * responses
                total_responses += responses
        
        if total_responses > 0:
            overall_positive_pct = (total_positive / total_responses) * 100
            overall_negative_pct = (total_negative / total_responses) * 100
            
            if overall_positive_pct > 60:
                return "Predominantly Positive - Strong guest satisfaction foundation"
            elif overall_negative_pct > 40:
                return "Concerning Negative Trend - Requires immediate strategic intervention"
            else:
                return "Mixed Sentiment - Balanced approach needed with targeted improvements"
        
        return "Insufficient data for trend analysis"
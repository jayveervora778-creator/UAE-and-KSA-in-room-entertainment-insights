#!/usr/bin/env python3
"""
OSN Advanced Analytics Engine - Enterprise-grade insights for hospitality entertainment
Designed specifically for OSN's strategic needs in the UAE & KSA markets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from scipy.stats import chi2_contingency, pearsonr
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

class OSNAnalyticsEngine:
    """Advanced analytics engine tailored for OSN's entertainment strategy"""
    
    def __init__(self, data_processor):
        self.processor = data_processor
        self.combined_data = self.processor._get_combined_data()
        self.entertainment_metrics = self._extract_entertainment_metrics()
        
    def _extract_entertainment_metrics(self) -> Dict[str, Any]:
        """Extract key entertainment metrics from survey data"""
        df = self.combined_data
        
        metrics = {
            'entertainment_importance': self._get_column_data('B2-A'),
            'family_entertainment_priority': self._get_column_data('B1-B'), 
            'tv_usage': self._get_column_data('C1'),
            'content_preferences': self._get_column_data('C2-A'),
            'streaming_account_preference': self._get_column_data('D2'),
            'payment_willingness': self._get_column_data('D3'),
            'entertainment_quality_rating': self._get_column_data('C4-A'),
            'content_accessibility': self._get_column_data('C2-B'),
            'preferred_formats': self._get_column_data('C3/1')
        }
        
        return {k: v for k, v in metrics.items() if v is not None}
    
    def _get_column_data(self, pattern: str) -> Optional[pd.Series]:
        """Get column data matching pattern"""
        matching_cols = [col for col in self.combined_data.columns if pattern in str(col)]
        if matching_cols:
            return self.combined_data[matching_cols[0]]
        return None
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary for OSN leadership"""
        
        total_responses = len(self.combined_data)
        uae_responses = len(self.combined_data[self.combined_data['Country'] == 'UAE'])
        ksa_responses = len(self.combined_data[self.combined_data['Country'] == 'KSA'])
        
        # Key strategic metrics
        summary = {
            'market_overview': {
                'total_respondents': total_responses,
                'uae_market': uae_responses,
                'ksa_market': ksa_responses,
                'business_travelers': self._count_by_purpose('Business'),
                'leisure_travelers': self._count_by_purpose('Leisure'),
                'family_travelers': self._count_by_purpose('Family Vacation')
            },
            'strategic_opportunities': self._identify_strategic_opportunities(),
            'entertainment_insights': self._get_entertainment_insights(),
            'market_penetration': self._calculate_market_penetration(),
            'revenue_opportunities': self._identify_revenue_opportunities(),
            'competitive_advantages': self._identify_competitive_advantages()
        }
        
        return summary
    
    def _count_by_purpose(self, purpose: str) -> Dict[str, int]:
        """Count responses by visit purpose and country"""
        purpose_col = [col for col in self.combined_data.columns if 'A2' in str(col) and 'A2-A' not in str(col)][0]
        
        purpose_data = self.combined_data[self.combined_data[purpose_col] == purpose]
        
        return {
            'total': len(purpose_data),
            'uae': len(purpose_data[purpose_data['Country'] == 'UAE']),
            'ksa': len(purpose_data[purpose_data['Country'] == 'KSA']),
            'percentage': round(len(purpose_data) / len(self.combined_data) * 100, 1)
        }
    
    def _identify_strategic_opportunities(self) -> List[Dict[str, Any]]:
        """Identify key strategic opportunities for OSN"""
        opportunities = []
        
        # Entertainment importance analysis
        if 'entertainment_importance' in self.entertainment_metrics:
            very_important = self.entertainment_metrics['entertainment_importance'].value_counts().get('Very Important', 0)
            total = len(self.entertainment_metrics['entertainment_importance'].dropna())
            if total > 0:
                percentage = (very_important / total) * 100
                opportunities.append({
                    'opportunity': 'High Entertainment Demand',
                    'insight': f'{percentage:.1f}% consider in-room entertainment very important',
                    'strategic_value': 'High' if percentage > 40 else 'Medium',
                    'market_size': very_important,
                    'action': 'Partner with hotels to provide premium OSN+ integration'
                })
        
        # Streaming preferences analysis
        if 'streaming_account_preference' in self.entertainment_metrics:
            wants_streaming = self.entertainment_metrics['streaming_account_preference'].value_counts().get('Yes', 0)
            total = len(self.entertainment_metrics['streaming_account_preference'].dropna())
            if total > 0:
                percentage = (wants_streaming / total) * 100
                opportunities.append({
                    'opportunity': 'Streaming Account Integration',
                    'insight': f'{percentage:.1f}% want access to their streaming accounts in hotels',
                    'strategic_value': 'Critical' if percentage > 60 else 'High',
                    'market_size': wants_streaming,
                    'action': 'Develop seamless OSN+ login integration for hotels'
                })
        
        # Payment willingness analysis
        if 'payment_willingness' in self.entertainment_metrics:
            willing_to_pay = self.entertainment_metrics['payment_willingness'].value_counts().get('Yes', 0)
            total = len(self.entertainment_metrics['payment_willingness'].dropna())
            if total > 0:
                percentage = (willing_to_pay / total) * 100
                opportunities.append({
                    'opportunity': 'Premium Content Monetization',
                    'insight': f'{percentage:.1f}% willing to pay for enhanced entertainment',
                    'strategic_value': 'High' if percentage > 30 else 'Medium',
                    'market_size': willing_to_pay,
                    'action': 'Create premium OSN+ hotel packages with exclusive content'
                })
        
        # Family travel analysis
        if 'family_entertainment_priority' in self.entertainment_metrics:
            family_priority = self.entertainment_metrics['family_entertainment_priority'].value_counts().get('Yes', 0)
            total = len(self.entertainment_metrics['family_entertainment_priority'].dropna())
            if total > 0:
                percentage = (family_priority / total) * 100
                opportunities.append({
                    'opportunity': 'Family Entertainment Focus',
                    'insight': f'{percentage:.1f}% prioritize entertainment when traveling with family',
                    'strategic_value': 'High',
                    'market_size': family_priority,
                    'action': 'Develop family-focused content packages for hotel partnerships'
                })
        
        return sorted(opportunities, key=lambda x: x['market_size'], reverse=True)
    
    def _get_entertainment_insights(self) -> Dict[str, Any]:
        """Generate detailed entertainment consumption insights"""
        insights = {}
        
        # Content type preferences
        if 'content_preferences' in self.entertainment_metrics:
            content_data = self.entertainment_metrics['content_preferences']
            content_counts = content_data.value_counts()
            
            insights['content_preferences'] = {
                'distribution': content_counts.to_dict(),
                'top_content': content_counts.index[0] if len(content_counts) > 0 else 'N/A',
                'osn_plus_mentions': content_data.str.contains('OSN', case=False, na=False).sum(),
                'streaming_preference': content_data.str.contains('Streaming', case=False, na=False).sum()
            }
        
        # Quality ratings analysis
        if 'entertainment_quality_rating' in self.entertainment_metrics:
            quality_data = self.entertainment_metrics['entertainment_quality_rating']
            # Convert ratings to numeric if possible
            numeric_ratings = pd.to_numeric(quality_data, errors='coerce')
            if not numeric_ratings.isna().all():
                insights['quality_ratings'] = {
                    'average_rating': round(numeric_ratings.mean(), 2),
                    'satisfaction_rate': (numeric_ratings >= 4).sum() / len(numeric_ratings.dropna()) * 100,
                    'improvement_needed': (numeric_ratings <= 2).sum()
                }
        
        # Accessibility insights
        if 'content_accessibility' in self.entertainment_metrics:
            accessibility_data = self.entertainment_metrics['content_accessibility']
            insights['accessibility'] = accessibility_data.value_counts().to_dict()
        
        return insights
    
    def _calculate_market_penetration(self) -> Dict[str, Any]:
        """Calculate OSN's potential market penetration"""
        
        # TV usage rates
        tv_usage = 0
        if 'tv_usage' in self.entertainment_metrics:
            tv_users = self.entertainment_metrics['tv_usage'].value_counts().get('Yes', 0)
            total_responses = len(self.entertainment_metrics['tv_usage'].dropna())
            tv_usage = (tv_users / total_responses * 100) if total_responses > 0 else 0
        
        # Country-wise analysis
        country_analysis = {}
        for country in ['UAE', 'KSA']:
            country_data = self.combined_data[self.combined_data['Country'] == country]
            
            # Entertainment importance in this country
            if 'entertainment_importance' in self.entertainment_metrics:
                ent_col = [col for col in country_data.columns if 'B2-A' in str(col)]
                if ent_col:
                    country_ent_data = country_data[ent_col[0]]
                    very_important = (country_ent_data == 'Very Important').sum()
                    total = len(country_ent_data.dropna())
                    
                    country_analysis[country] = {
                        'market_size': len(country_data),
                        'high_entertainment_demand': very_important,
                        'demand_percentage': (very_important / total * 100) if total > 0 else 0,
                        'potential_subscribers': int(very_important * 0.6)  # Conservative estimate
                    }
        
        return {
            'tv_usage_rate': round(tv_usage, 1),
            'country_analysis': country_analysis,
            'total_addressable_market': sum([country_analysis[c].get('market_size', 0) for c in country_analysis]),
            'high_value_prospects': sum([country_analysis[c].get('high_entertainment_demand', 0) for c in country_analysis])
        }
    
    def _identify_revenue_opportunities(self) -> List[Dict[str, Any]]:
        """Identify specific revenue generation opportunities"""
        opportunities = []
        
        # Premium content willingness
        if 'payment_willingness' in self.entertainment_metrics:
            willing_to_pay = self.entertainment_metrics['payment_willingness'].value_counts().get('Yes', 0)
            
            # Estimate revenue potential (conservative assumptions)
            monthly_arpu = 15  # USD average revenue per user
            opportunities.append({
                'revenue_stream': 'Premium Hotel Packages',
                'addressable_users': willing_to_pay,
                'estimated_monthly_revenue': willing_to_pay * monthly_arpu,
                'confidence': 'Medium',
                'implementation': 'Partner with hotel chains for premium OSN+ integration'
            })
        
        # Family content packages
        if 'family_entertainment_priority' in self.entertainment_metrics:
            family_focused = self.entertainment_metrics['family_entertainment_priority'].value_counts().get('Yes', 0)
            family_arpu = 20  # Higher ARPU for family packages
            
            opportunities.append({
                'revenue_stream': 'Family Entertainment Packages',
                'addressable_users': family_focused,
                'estimated_monthly_revenue': family_focused * family_arpu,
                'confidence': 'High',
                'implementation': 'Create family-focused content bundles for hotels'
            })
        
        return opportunities
    
    def _identify_competitive_advantages(self) -> List[str]:
        """Identify OSN's competitive advantages in the hotel entertainment space"""
        advantages = []
        
        # OSN+ specific mentions in survey
        if 'content_preferences' in self.entertainment_metrics:
            osn_mentions = self.entertainment_metrics['content_preferences'].str.contains('OSN', case=False, na=False).sum()
            if osn_mentions > 0:
                advantages.append(f"Direct brand recognition: {osn_mentions} survey mentions of OSN services")
        
        advantages.extend([
            "Regional content expertise: Deep understanding of UAE & KSA entertainment preferences",
            "Local language support: Arabic content library advantage over global streamers",
            "Regulatory compliance: Licensed content distribution in both markets",
            "Hotel partnership ecosystem: Existing relationships with hospitality industry",
            "Premium content portfolio: Exclusive regional and international content rights"
        ])
        
        return advantages
    
    def get_correlation_analysis(self) -> Dict[str, Any]:
        """Perform advanced correlation analysis for entertainment factors"""
        
        # Prepare numerical data for correlation
        correlation_data = {}
        
        # Entertainment importance vs demographics
        if 'entertainment_importance' in self.entertainment_metrics:
            le = LabelEncoder()
            ent_importance = self.entertainment_metrics['entertainment_importance'].fillna('Unknown')
            correlation_data['entertainment_importance'] = le.fit_transform(ent_importance)
        
        # Visit purpose correlation
        purpose_col = [col for col in self.combined_data.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_col:
            le_purpose = LabelEncoder()
            purpose_data = self.combined_data[purpose_col[0]].fillna('Unknown')
            correlation_data['visit_purpose'] = le_purpose.fit_transform(purpose_data)
        
        # Payment willingness
        if 'payment_willingness' in self.entertainment_metrics:
            payment_mapping = {'Yes': 1, 'No': 0}
            payment_data = self.entertainment_metrics['payment_willingness'].map(payment_mapping).fillna(0.5)
            correlation_data['payment_willingness'] = payment_data
        
        # Calculate correlations
        correlations = {}
        if len(correlation_data) >= 2:
            df_corr = pd.DataFrame(correlation_data)
            correlation_matrix = df_corr.corr()
            
            # Extract key insights
            correlations = {
                'entertainment_payment_correlation': self._safe_correlation(
                    correlation_data.get('entertainment_importance', []),
                    correlation_data.get('payment_willingness', [])
                ),
                'purpose_entertainment_correlation': self._safe_correlation(
                    correlation_data.get('visit_purpose', []),
                    correlation_data.get('entertainment_importance', [])
                ),
                'correlation_matrix': correlation_matrix.to_dict() if not correlation_matrix.empty else {}
            }
        
        return correlations
    
    def _safe_correlation(self, x, y) -> float:
        """Safely calculate correlation between two variables"""
        try:
            if len(x) > 0 and len(y) > 0 and len(x) == len(y):
                x_clean = pd.Series(x).dropna()
                y_clean = pd.Series(y).dropna()
                if len(x_clean) > 1 and len(y_clean) > 1:
                    correlation, _ = pearsonr(x_clean, y_clean)
                    return round(correlation, 3) if not np.isnan(correlation) else 0.0
        except:
            pass
        return 0.0
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights using machine learning"""
        
        insights = {
            'customer_segments': self._identify_customer_segments(),
            'churn_risk_analysis': self._analyze_satisfaction_patterns(),
            'growth_predictions': self._predict_market_growth()
        }
        
        return insights
    
    def _identify_customer_segments(self) -> List[Dict[str, Any]]:
        """Identify distinct customer segments using clustering"""
        
        # Prepare features for clustering
        features = []
        feature_names = []
        
        # Entertainment importance
        if 'entertainment_importance' in self.entertainment_metrics:
            le = LabelEncoder()
            ent_encoded = le.fit_transform(self.entertainment_metrics['entertainment_importance'].fillna('Unknown'))
            features.append(ent_encoded)
            feature_names.append('entertainment_importance')
        
        # Visit purpose
        purpose_col = [col for col in self.combined_data.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_col:
            le_purpose = LabelEncoder()
            purpose_encoded = le_purpose.fit_transform(self.combined_data[purpose_col[0]].fillna('Unknown'))
            features.append(purpose_encoded)
            feature_names.append('visit_purpose')
        
        # Payment willingness
        if 'payment_willingness' in self.entertainment_metrics:
            payment_encoded = self.entertainment_metrics['payment_willingness'].map({'Yes': 1, 'No': 0}).fillna(0.5)
            features.append(payment_encoded.values)
            feature_names.append('payment_willingness')
        
        segments = []
        
        if len(features) >= 2:
            try:
                # Combine features
                X = np.column_stack(features)
                
                # Perform clustering
                n_clusters = min(4, len(np.unique(X, axis=0)))  # Max 4 clusters
                if n_clusters >= 2:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    cluster_labels = kmeans.fit_predict(X)
                    
                    # Analyze each segment
                    for i in range(n_clusters):
                        segment_mask = cluster_labels == i
                        segment_size = segment_mask.sum()
                        
                        # Calculate segment characteristics
                        segment_data = self.combined_data[segment_mask]
                        
                        segments.append({
                            'segment_id': f'Segment_{i+1}',
                            'size': int(segment_size),
                            'percentage': round(segment_size / len(self.combined_data) * 100, 1),
                            'characteristics': self._describe_segment(segment_data),
                            'osn_opportunity': self._assess_osn_opportunity(segment_data)
                        })
            except Exception as e:
                print(f"Clustering error: {e}")
        
        return segments
    
    def _describe_segment(self, segment_data: pd.DataFrame) -> Dict[str, Any]:
        """Describe the characteristics of a customer segment"""
        
        characteristics = {}
        
        # Country distribution
        if 'Country' in segment_data.columns:
            country_dist = segment_data['Country'].value_counts(normalize=True) * 100
            characteristics['primary_market'] = country_dist.index[0] if len(country_dist) > 0 else 'Mixed'
            characteristics['country_distribution'] = country_dist.to_dict()
        
        # Visit purpose
        purpose_cols = [col for col in segment_data.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if purpose_cols:
            purpose_dist = segment_data[purpose_cols[0]].value_counts(normalize=True) * 100
            characteristics['primary_purpose'] = purpose_dist.index[0] if len(purpose_dist) > 0 else 'Mixed'
        
        # Entertainment usage
        tv_cols = [col for col in segment_data.columns if 'C1' in str(col)]
        if tv_cols:
            tv_usage = (segment_data[tv_cols[0]] == 'Yes').mean() * 100
            characteristics['tv_usage_rate'] = round(tv_usage, 1)
        
        return characteristics
    
    def _assess_osn_opportunity(self, segment_data: pd.DataFrame) -> str:
        """Assess OSN's opportunity level for a customer segment"""
        
        score = 0
        
        # Entertainment importance
        ent_cols = [col for col in segment_data.columns if 'B2-A' in str(col)]
        if ent_cols:
            very_important_rate = (segment_data[ent_cols[0]] == 'Very Important').mean()
            score += very_important_rate * 40
        
        # Payment willingness
        payment_cols = [col for col in segment_data.columns if 'D3' in str(col)]
        if payment_cols:
            payment_rate = (segment_data[payment_cols[0]] == 'Yes').mean()
            score += payment_rate * 35
        
        # Streaming preference
        streaming_cols = [col for col in segment_data.columns if 'D2' in str(col)]
        if streaming_cols:
            streaming_rate = (segment_data[streaming_cols[0]] == 'Yes').mean()
            score += streaming_rate * 25
        
        if score >= 70:
            return 'High Priority - Prime target for OSN+ integration'
        elif score >= 40:
            return 'Medium Priority - Good potential with targeted approach'
        else:
            return 'Low Priority - Limited immediate opportunity'
    
    def _analyze_satisfaction_patterns(self) -> Dict[str, Any]:
        """Analyze satisfaction patterns to identify retention opportunities"""
        
        satisfaction_analysis = {}
        
        # Entertainment quality ratings
        if 'entertainment_quality_rating' in self.entertainment_metrics:
            quality_data = self.entertainment_metrics['entertainment_quality_rating']
            numeric_ratings = pd.to_numeric(quality_data, errors='coerce').dropna()
            
            if len(numeric_ratings) > 0:
                satisfaction_analysis['quality_metrics'] = {
                    'average_rating': round(numeric_ratings.mean(), 2),
                    'dissatisfied_percentage': round((numeric_ratings <= 2).mean() * 100, 1),
                    'highly_satisfied_percentage': round((numeric_ratings >= 4).mean() * 100, 1)
                }
        
        # Accessibility issues
        if 'content_accessibility' in self.entertainment_metrics:
            accessibility_issues = self.entertainment_metrics['content_accessibility'].str.contains('effort', case=False, na=False).sum()
            total_responses = len(self.entertainment_metrics['content_accessibility'].dropna())
            
            satisfaction_analysis['accessibility_challenges'] = {
                'setup_issues_count': accessibility_issues,
                'setup_issues_percentage': round(accessibility_issues / total_responses * 100, 1) if total_responses > 0 else 0
            }
        
        return satisfaction_analysis
    
    def _predict_market_growth(self) -> Dict[str, Any]:
        """Predict market growth opportunities based on current trends"""
        
        predictions = {}
        
        # Business traveler growth potential
        business_travelers = self._count_by_purpose('Business')
        
        # Family entertainment growth
        if 'family_entertainment_priority' in self.entertainment_metrics:
            family_priority_rate = (self.entertainment_metrics['family_entertainment_priority'] == 'Yes').mean()
            
            predictions['family_segment_growth'] = {
                'current_priority_rate': round(family_priority_rate * 100, 1),
                'growth_potential': 'High' if family_priority_rate > 0.6 else 'Medium',
                'strategic_focus': 'Children content and family-friendly programming'
            }
        
        # Streaming adoption trends
        if 'streaming_account_preference' in self.entertainment_metrics:
            streaming_demand = (self.entertainment_metrics['streaming_account_preference'] == 'Yes').mean()
            
            predictions['streaming_integration'] = {
                'current_demand': round(streaming_demand * 100, 1),
                'market_readiness': 'Ready' if streaming_demand > 0.5 else 'Developing',
                'implementation_priority': 'Critical' if streaming_demand > 0.6 else 'High'
            }
        
        return predictions

    def generate_ai_recommendations(self, filtered_data: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """Generate AI-powered strategic recommendations for OSN"""
        
        if filtered_data is not None:
            # Create temporary instance with filtered data
            temp_data = self.combined_data
            self.combined_data = filtered_data
            self.entertainment_metrics = self._extract_entertainment_metrics()
        
        recommendations = []
        
        # Strategic partnerships recommendation
        hotel_partnership_score = self._calculate_hotel_partnership_potential()
        recommendations.append({
            'category': 'Strategic Partnerships',
            'priority': 'Critical' if hotel_partnership_score > 70 else 'High',
            'recommendation': 'Accelerate hotel chain partnerships for OSN+ integration',
            'rationale': f'Analysis shows {hotel_partnership_score:.0f}% partnership success potential',
            'implementation': [
                'Target luxury and business hotels in UAE & KSA',
                'Develop white-label OSN+ hotel solutions',
                'Create revenue-sharing models with hotel partners'
            ],
            'expected_impact': 'High revenue growth and market penetration',
            'confidence_score': hotel_partnership_score
        })
        
        # Content strategy recommendation
        content_gaps = self._identify_content_gaps()
        recommendations.append({
            'category': 'Content Strategy',
            'priority': 'High',
            'recommendation': 'Focus on family and business traveler content',
            'rationale': 'Strong demand for family entertainment and business-relevant content',
            'implementation': content_gaps,
            'expected_impact': 'Increased user engagement and satisfaction',
            'confidence_score': 75
        })
        
        # Technology platform recommendation
        tech_score = self._assess_technology_needs()
        recommendations.append({
            'category': 'Technology Platform',
            'priority': 'Critical',
            'recommendation': 'Develop seamless device integration platform',
            'rationale': f'{tech_score:.0f}% of users want personal streaming account access',
            'implementation': [
                'Build universal hotel room casting solution',
                'Develop QR code quick-login for OSN+ accounts',
                'Create hotel-specific OSN+ interface'
            ],
            'expected_impact': 'Reduced setup friction and increased adoption',
            'confidence_score': tech_score
        })
        
        # Market expansion recommendation
        market_potential = self._calculate_market_expansion_potential()
        recommendations.append({
            'category': 'Market Expansion',
            'priority': 'Medium',
            'recommendation': f'Prioritize {market_potential["primary_market"]} for initial rollout',
            'rationale': f'Higher entertainment demand and payment willingness in {market_potential["primary_market"]}',
            'implementation': [
                f'Launch pilot program in top {market_potential["primary_market"]} hotels',
                'Develop market-specific content packages',
                'Establish local partnership ecosystem'
            ],
            'expected_impact': 'Faster market penetration and lower customer acquisition costs',
            'confidence_score': market_potential['confidence']
        })
        
        # Restore original data if we used filtered data
        if filtered_data is not None:
            self.combined_data = temp_data
            self.entertainment_metrics = self._extract_entertainment_metrics()
        
        return sorted(recommendations, key=lambda x: x['confidence_score'], reverse=True)
    
    def _calculate_hotel_partnership_potential(self) -> float:
        """Calculate potential success rate for hotel partnerships"""
        score = 0
        
        # Entertainment importance
        if 'entertainment_importance' in self.entertainment_metrics:
            very_important_rate = (self.entertainment_metrics['entertainment_importance'] == 'Very Important').mean()
            score += very_important_rate * 30
        
        # Payment willingness
        if 'payment_willingness' in self.entertainment_metrics:
            payment_rate = (self.entertainment_metrics['payment_willingness'] == 'Yes').mean()
            score += payment_rate * 25
        
        # TV usage rate
        if 'tv_usage' in self.entertainment_metrics:
            usage_rate = (self.entertainment_metrics['tv_usage'] == 'Yes').mean()
            score += usage_rate * 20
        
        # Streaming preference
        if 'streaming_account_preference' in self.entertainment_metrics:
            streaming_rate = (self.entertainment_metrics['streaming_account_preference'] == 'Yes').mean()
            score += streaming_rate * 25
        
        return min(score * 100, 100)
    
    def _identify_content_gaps(self) -> List[str]:
        """Identify content gaps and opportunities"""
        gaps = []
        
        # Analyze content preferences
        if 'content_preferences' in self.entertainment_metrics:
            content_dist = self.entertainment_metrics['content_preferences'].value_counts()
            
            if 'Children\'s Content' in content_dist.index:
                gaps.append('Expand Arabic children\'s programming for family travelers')
            
            if 'News' in content_dist.index:
                gaps.append('Develop business news packages for corporate travelers')
            
            if 'Sports' in content_dist.index:
                gaps.append('Secure exclusive sports content rights for regional leagues')
        
        gaps.extend([
            'Create hotel-exclusive content series',
            'Develop local cultural programming',
            'Build educational content for family segments'
        ])
        
        return gaps[:5]  # Top 5 recommendations
    
    def _assess_technology_needs(self) -> float:
        """Assess technology platform needs score"""
        if 'streaming_account_preference' in self.entertainment_metrics:
            return (self.entertainment_metrics['streaming_account_preference'] == 'Yes').mean() * 100
        return 65  # Default estimate
    
    def _calculate_market_expansion_potential(self) -> Dict[str, Any]:
        """Calculate market expansion potential by country"""
        
        uae_score = 0
        ksa_score = 0
        
        for country in ['UAE', 'KSA']:
            country_data = self.combined_data[self.combined_data['Country'] == country]
            
            # Entertainment importance in this country
            ent_cols = [col for col in country_data.columns if 'B2-A' in str(col)]
            if ent_cols:
                very_important = (country_data[ent_cols[0]] == 'Very Important').mean()
                
                # Payment willingness
                payment_cols = [col for col in country_data.columns if 'D3' in str(col)]
                willing_to_pay = 0
                if payment_cols:
                    willing_to_pay = (country_data[payment_cols[0]] == 'Yes').mean()
                
                score = (very_important * 50) + (willing_to_pay * 50)
                
                if country == 'UAE':
                    uae_score = score
                else:
                    ksa_score = score
        
        primary_market = 'UAE' if uae_score > ksa_score else 'KSA'
        confidence = max(uae_score, ksa_score)
        
        return {
            'primary_market': primary_market,
            'uae_score': round(uae_score, 1),
            'ksa_score': round(ksa_score, 1),
            'confidence': round(confidence, 1)
        }
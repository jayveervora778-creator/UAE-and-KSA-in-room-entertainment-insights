#!/usr/bin/env python3
"""
Dynamic Question Visualization Engine
Enables multi-question dynamic visualization inspired by Egypt delivery dashboard patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from collections import defaultdict
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer

class DynamicQuestionEngine:
    """Advanced engine for dynamic multi-question visualization"""
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.question_catalog = {}
        self.chart_types_map = {}
        self.comparison_modes = ['overall', 'by_country', 'by_nationality', 'by_visit_purpose']
        self._build_question_catalog()
    
    def _build_question_catalog(self):
        """Build comprehensive catalog of all available questions"""
        try:
            combined_df = self.data_processor._get_combined_data()
            if combined_df.empty:
                return
            
            # Extract question information from the data processor
            question_mapping = getattr(self.data_processor, 'question_mapping', {})
            response_legends = getattr(self.data_processor, 'response_legends', {})
            
            # Build catalog from actual columns and any available mapping
            for column in combined_df.columns:
                col_str = str(column)
                
                # Skip utility columns
                if col_str in ['S. No.', 'Country', 'Unnamed']:
                    continue
                
                # Determine question type and metadata
                question_info = self._analyze_column(combined_df, column, question_mapping, response_legends)
                
                if question_info:
                    self.question_catalog[column] = question_info
            
            print(f"Built question catalog with {len(self.question_catalog)} questions")
            
        except Exception as e:
            print(f"Error building question catalog: {e}")
            import traceback
            traceback.print_exc()
    
    def _analyze_column(self, df: pd.DataFrame, column: str, question_mapping: Dict, response_legends: Dict) -> Optional[Dict]:
        """Analyze a column to determine its question type and properties"""
        
        col_data = df[column].dropna()
        if len(col_data) == 0:
            return None
        
        col_str = str(column)
        question_info = {
            'column_name': column,
            'display_name': self._generate_display_name(column, question_mapping),
            'data_type': None,
            'chart_types': [],
            'unique_values': len(col_data.unique()),
            'response_count': len(col_data),
            'sample_values': col_data.head(3).tolist()
        }
        
        # Determine data type and suitable charts
        unique_vals = col_data.unique()
        
        # Check if it's categorical
        if question_info['unique_values'] <= 20:  # Categorical
            question_info['data_type'] = 'categorical'
            question_info['categories'] = [str(val) for val in unique_vals if str(val) not in ['nan', 'None']]
            
            # Determine best chart types for categorical data
            if question_info['unique_values'] <= 5:
                question_info['chart_types'] = ['pie', 'donut', 'bar', 'horizontal_bar']
            else:
                question_info['chart_types'] = ['bar', 'horizontal_bar', 'grouped_bar']
            
        elif self._is_numeric_column(col_data):  # Numeric
            question_info['data_type'] = 'numeric'
            question_info['min_value'] = float(col_data.min())
            question_info['max_value'] = float(col_data.max())
            question_info['mean_value'] = float(col_data.mean())
            question_info['chart_types'] = ['histogram', 'box_plot', 'scatter', 'line']
            
        elif self._is_text_column(col_data):  # Text
            question_info['data_type'] = 'text'
            question_info['avg_text_length'] = col_data.astype(str).str.len().mean()
            question_info['chart_types'] = ['word_cloud', 'sentiment_analysis', 'text_analysis']
            
        else:  # Mixed or other
            question_info['data_type'] = 'mixed'
            question_info['chart_types'] = ['table', 'summary']
        
        # Add question category based on column pattern
        question_info['category'] = self._categorize_question(column)
        
        return question_info
    
    def _generate_display_name(self, column: str, question_mapping: Dict) -> str:
        """Generate user-friendly display name for question"""
        
        # Check if we have explicit mapping
        if column in question_mapping:
            return question_mapping[column]
        
        # Generate from column name
        col_str = str(column)
        
        # Common patterns
        patterns = {
            'A1': 'Nationality',
            'A2': 'Visit Purpose',
            'A3': 'Hotel Stay Frequency',
            'B1-A': 'Entertainment Priority (Adults)',
            'B1-B': 'Entertainment Priority (Children)',
            'B2-A': 'Entertainment Importance',
            'C1': 'TV System Usage',
            'C2-A': 'Content Preferences',
            'C3': 'Viewing Duration',
            'C4-A': 'Experience Rating',
            'D1': 'Streaming Awareness',
            'D2': 'Streaming Access Preference',
            'D3': 'Payment Willingness'
        }
        
        for pattern, name in patterns.items():
            if pattern in col_str:
                return name
        
        # Fallback: clean column name
        return col_str.replace('_', ' ').replace('-', ' ').title()
    
    def _categorize_question(self, column: str) -> str:
        """Categorize questions into logical groups"""
        
        col_str = str(column).upper()
        
        if any(prefix in col_str for prefix in ['A1', 'A2', 'A3']):
            return 'Demographics & Travel'
        elif any(prefix in col_str for prefix in ['B1', 'B2']):
            return 'Entertainment Preferences'
        elif any(prefix in col_str for prefix in ['C1', 'C2', 'C3', 'C4']):
            return 'Current Experience'
        elif any(prefix in col_str for prefix in ['D1', 'D2', 'D3']):
            return 'Future Preferences'
        else:
            return 'Other'
    
    def _is_numeric_column(self, data: pd.Series) -> bool:
        """Check if column contains numeric data"""
        try:
            pd.to_numeric(data)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_text_column(self, data: pd.Series) -> bool:
        """Check if column contains substantial text responses"""
        text_samples = data.astype(str).head(10)
        return any(len(str(val).split()) > 3 for val in text_samples)
    
    def get_question_catalog(self) -> Dict[str, Any]:
        """Get the complete question catalog organized by category"""
        
        categorized = defaultdict(list)
        
        for question_id, question_info in self.question_catalog.items():
            category = question_info['category']
            categorized[category].append({
                'id': question_id,
                'name': question_info['display_name'],
                'type': question_info['data_type'],
                'charts': question_info['chart_types'],
                'responses': question_info['response_count']
            })
        
        return {
            'categories': dict(categorized),
            'total_questions': len(self.question_catalog),
            'comparison_modes': self.comparison_modes
        }
    
    def generate_dynamic_chart(self, question_id: str, chart_type: str, comparison_mode: str = 'overall', filters: Dict = None) -> Dict[str, Any]:
        """Generate dynamic chart data for specified question and parameters"""
        
        if question_id not in self.question_catalog:
            return {'error': f'Question {question_id} not found'}
        
        question_info = self.question_catalog[question_id]
        
        if chart_type not in question_info['chart_types']:
            return {'error': f'Chart type {chart_type} not supported for question {question_id}'}
        
        try:
            # Get filtered data
            filtered_df = self.data_processor.filter_data(filters) if filters else self.data_processor._get_combined_data()
            
            if filtered_df.empty:
                return {'error': 'No data available with current filters'}
            
            # Generate chart based on type and comparison mode
            chart_data = self._generate_chart_data(filtered_df, question_id, question_info, chart_type, comparison_mode)
            
            # Add metadata
            chart_data['metadata'] = {
                'question_name': question_info['display_name'],
                'total_responses': len(filtered_df),
                'chart_type': chart_type,
                'comparison_mode': comparison_mode,
                'applied_filters': filters or {}
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _generate_chart_data(self, df: pd.DataFrame, question_id: str, question_info: Dict, chart_type: str, comparison_mode: str) -> Dict[str, Any]:
        """Generate specific chart data based on parameters"""
        
        column_data = df[question_id].dropna()
        
        if comparison_mode == 'overall':
            return self._generate_overall_chart(column_data, question_info, chart_type)
        
        elif comparison_mode == 'by_country':
            return self._generate_comparison_chart(df, question_id, 'Country', chart_type, question_info)
        
        elif comparison_mode == 'by_nationality':
            # Find nationality column (A1)
            nationality_cols = [col for col in df.columns if 'A1' in str(col)]
            if nationality_cols:
                return self._generate_comparison_chart(df, question_id, nationality_cols[0], chart_type, question_info)
        
        elif comparison_mode == 'by_visit_purpose':
            # Find visit purpose column (A2)
            purpose_cols = [col for col in df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
            if purpose_cols:
                return self._generate_comparison_chart(df, question_id, purpose_cols[0], chart_type, question_info)
        
        # Fallback to overall
        return self._generate_overall_chart(column_data, question_info, chart_type)
    
    def _generate_overall_chart(self, data: pd.Series, question_info: Dict, chart_type: str) -> Dict[str, Any]:
        """Generate chart for overall data without comparison"""
        
        chart_data = {'type': chart_type, 'title': f"{question_info['display_name']} - Overall Distribution"}
        
        if chart_type in ['pie', 'donut']:
            value_counts = data.value_counts()
            chart_data['data'] = {
                'labels': [str(label) for label in value_counts.index.tolist()],
                'data': value_counts.values.tolist(),
                'colors': self._generate_colors(len(value_counts))
            }
        
        elif chart_type in ['bar', 'horizontal_bar']:
            value_counts = data.value_counts()
            chart_data['data'] = {
                'labels': [str(label) for label in value_counts.index.tolist()],
                'data': value_counts.values.tolist(),
                'backgroundColor': self._generate_colors(len(value_counts))
            }
        
        elif chart_type == 'histogram':
            if question_info['data_type'] == 'numeric':
                numeric_data = pd.to_numeric(data, errors='coerce').dropna()
                hist_data, bin_edges = np.histogram(numeric_data, bins=10)
                chart_data['data'] = {
                    'labels': [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(hist_data))],
                    'data': hist_data.tolist(),
                    'backgroundColor': self._generate_colors(len(hist_data))
                }
        
        elif chart_type == 'text_analysis':
            text_analysis = self._analyze_text_data(data)
            chart_data.update(text_analysis)
        
        return chart_data
    
    def _generate_comparison_chart(self, df: pd.DataFrame, question_col: str, comparison_col: str, chart_type: str, question_info: Dict) -> Dict[str, Any]:
        """Generate comparison chart across different groups"""
        
        # Clean data
        clean_df = df[[question_col, comparison_col]].dropna()
        
        if len(clean_df) == 0:
            return {'error': 'No data available for comparison'}
        
        chart_data = {
            'type': chart_type,
            'title': f"{question_info['display_name']} by {self._generate_display_name(comparison_col, {})}"
        }
        
        if chart_type in ['grouped_bar', 'stacked_bar']:
            # Create crosstab for grouped comparison
            crosstab = pd.crosstab(clean_df[comparison_col], clean_df[question_col])
            
            chart_data['data'] = {
                'categories': [str(cat) for cat in crosstab.index.tolist()],
                'series': [
                    {
                        'name': str(col),
                        'data': crosstab[col].tolist(),
                        'backgroundColor': self._generate_colors(len(crosstab.columns))[i]
                    }
                    for i, col in enumerate(crosstab.columns)
                ]
            }
        
        elif chart_type == 'percentage_stacked':
            # Normalized crosstab
            crosstab_norm = pd.crosstab(clean_df[comparison_col], clean_df[question_col], normalize='index') * 100
            
            chart_data['data'] = {
                'categories': [str(cat) for cat in crosstab_norm.index.tolist()],
                'series': [
                    {
                        'name': str(col),
                        'data': [round(val, 1) for val in crosstab_norm[col].tolist()],
                        'backgroundColor': self._generate_colors(len(crosstab_norm.columns))[i]
                    }
                    for i, col in enumerate(crosstab_norm.columns)
                ]
            }
        
        return chart_data
    
    def _analyze_text_data(self, text_data: pd.Series) -> Dict[str, Any]:
        """Analyze text data for insights"""
        
        text_responses = []
        sentiment_scores = []
        
        for text in text_data:
            if isinstance(text, str) and len(text.strip()) > 10:
                text_responses.append(text)
                
                # Sentiment analysis
                blob = TextBlob(text)
                sentiment_scores.append(blob.sentiment.polarity)
        
        if not text_responses:
            return {'type': 'text_summary', 'message': 'No substantial text responses found'}
        
        # Sentiment distribution
        positive = len([s for s in sentiment_scores if s > 0.1])
        negative = len([s for s in sentiment_scores if s < -0.1]) 
        neutral = len(sentiment_scores) - positive - negative
        
        # Keyword extraction using TF-IDF
        keywords = []
        try:
            if len(text_responses) >= 3:
                tfidf = TfidfVectorizer(max_features=15, stop_words='english', ngram_range=(1, 2))
                tfidf_matrix = tfidf.fit_transform(text_responses)
                feature_names = tfidf.get_feature_names_out()
                scores = np.mean(tfidf_matrix.toarray(), axis=0)
                
                keyword_scores = list(zip(feature_names, scores))
                keyword_scores.sort(key=lambda x: x[1], reverse=True)
                keywords = [{'word': kw, 'score': round(score, 3)} for kw, score in keyword_scores[:10]]
        
        except Exception as e:
            print(f"Keyword extraction failed: {e}")
        
        return {
            'type': 'text_analysis',
            'sentiment_distribution': {
                'labels': ['Positive', 'Neutral', 'Negative'],
                'data': [positive, neutral, negative],
                'colors': ['#28a745', '#ffc107', '#dc3545']
            },
            'keywords': keywords,
            'total_responses': len(text_responses),
            'avg_sentiment': round(np.mean(sentiment_scores), 3) if sentiment_scores else 0
        }
    
    def _generate_colors(self, count: int) -> List[str]:
        """Generate color palette for charts"""
        base_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
            '#DDA0DD', '#98D8C8', '#F06292', '#AED581', '#FFB74D',
            '#81C784', '#64B5F6', '#E57373', '#9575CD', '#4DB6AC'
        ]
        
        # Extend colors if needed
        while len(base_colors) < count:
            base_colors.extend(base_colors)
        
        return base_colors[:count]
    
    def generate_multi_question_dashboard(self, question_ids: List[str], filters: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive dashboard with multiple questions"""
        
        dashboard_data = {
            'charts': {},
            'insights': [],
            'metadata': {
                'questions_count': len(question_ids),
                'applied_filters': filters or {},
                'total_responses': 0
            }
        }
        
        # Get filtered data once
        filtered_df = self.data_processor.filter_data(filters) if filters else self.data_processor._get_combined_data()
        dashboard_data['metadata']['total_responses'] = len(filtered_df)
        
        # Generate charts for each question
        for question_id in question_ids:
            if question_id in self.question_catalog:
                question_info = self.question_catalog[question_id]
                
                # Choose best chart type
                best_chart_type = question_info['chart_types'][0] if question_info['chart_types'] else 'bar'
                
                # Generate chart with country comparison by default
                chart_data = self.generate_dynamic_chart(question_id, best_chart_type, 'by_country', filters)
                dashboard_data['charts'][question_id] = chart_data
        
        # Generate cross-question insights
        dashboard_data['insights'] = self._generate_cross_question_insights(filtered_df, question_ids)
        
        return dashboard_data
    
    def _generate_cross_question_insights(self, df: pd.DataFrame, question_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate insights across multiple questions"""
        
        insights = []
        
        try:
            # Sample insight: Entertainment importance vs payment willingness
            ent_cols = [col for col in df.columns if 'B2-A' in str(col)]
            payment_cols = [col for col in df.columns if 'D3' in str(col)]
            
            if ent_cols and payment_cols:
                high_ent = df[df[ent_cols[0]] == 'Very Important']
                willing_to_pay = (high_ent[payment_cols[0]] == 'Yes').sum() if len(high_ent) > 0 else 0
                total_high_ent = len(high_ent)
                
                if total_high_ent > 0:
                    payment_rate = (willing_to_pay / total_high_ent) * 100
                    insights.append({
                        'type': 'cross_analysis',
                        'title': 'Entertainment Priority vs Payment Willingness',
                        'description': f'Of guests who rate entertainment as "Very Important" ({total_high_ent} responses), {payment_rate:.1f}% are willing to pay premium for enhanced entertainment services.',
                        'data_point': f'{willing_to_pay}/{total_high_ent}',
                        'confidence': 'High' if total_high_ent >= 20 else 'Medium'
                    })
            
            # Country comparison insight
            if 'Country' in df.columns:
                country_dist = df['Country'].value_counts()
                insights.append({
                    'type': 'geographic',
                    'title': 'Market Distribution',
                    'description': f'Survey responses: {" | ".join([f"{country}: {count}" for country, count in country_dist.items()])}',
                    'data_point': f'{len(df)} total responses',
                    'confidence': 'High'
                })
            
        except Exception as e:
            print(f"Error generating cross-question insights: {e}")
        
        return insights
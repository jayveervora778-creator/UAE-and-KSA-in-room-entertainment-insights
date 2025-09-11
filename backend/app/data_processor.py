#!/usr/bin/env python3
"""
Data processing module for survey data analysis
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import json

class SurveyDataProcessor:
    """Process and analyze survey data"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.raw_data = {}
        self.processed_data = {}
        self.question_mapping = {}
        self.text_responses = {}
        self._load_data()
        self._process_data()
    
    def _load_data(self):
        """Load raw data from Excel file"""
        try:
            # Load both sheets
            xl = pd.ExcelFile(self.data_file)
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(self.data_file, sheet_name=sheet_name)
                self.raw_data[sheet_name] = df
                print(f"Loaded {sheet_name}: {df.shape}")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def _process_data(self):
        """Process raw data into structured format"""
        for sheet_name, df in self.raw_data.items():
            # Clean and structure the data
            processed_df = self._clean_sheet_data(df, sheet_name)
            self.processed_data[sheet_name] = processed_df
            
            # Extract question mappings
            self._extract_questions(df, sheet_name)
            
            # Extract text responses for NLP
            self._extract_text_responses(processed_df, sheet_name)
    
    def _clean_sheet_data(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Clean and structure sheet data"""
        # Skip header rows and get actual survey responses
        # Based on analysis, actual data starts from row 3 (index 2)
        if len(df) > 3:
            # Find the row where actual responses start
            response_start_idx = 2  # Skip Question and Response rows
            data_df = df.iloc[response_start_idx:].copy()
            
            # Use the question row as column names where possible
            question_row = df.iloc[0] if len(df) > 0 else None
            response_row = df.iloc[1] if len(df) > 1 else None
            
            # Create better column names
            new_columns = []
            for i, col in enumerate(df.columns):
                if question_row is not None and pd.notna(question_row.iloc[i]):
                    q_text = str(question_row.iloc[i]).strip()
                    if len(q_text) > 3:  # Valid question
                        new_columns.append(q_text[:50] + "..." if len(q_text) > 50 else q_text)
                    else:
                        new_columns.append(col)
                else:
                    new_columns.append(col)
            
            data_df.columns = new_columns
            
            # Reset index
            data_df = data_df.reset_index(drop=True)
            
            # Add country information based on sheet name
            country = 'UAE' if 'UAE' in sheet_name else 'KSA' if 'KSA' in sheet_name else 'Unknown'
            data_df['Country'] = country
            
            return data_df
        
        return df
    
    def _extract_questions(self, df: pd.DataFrame, sheet_name: str):
        """Extract question mappings from the raw data"""
        if sheet_name not in self.question_mapping:
            self.question_mapping[sheet_name] = {}
        
        if len(df) > 1:
            question_row = df.iloc[0]
            response_options_row = df.iloc[1]
            
            for col_idx, col_name in enumerate(df.columns):
                if col_idx < len(question_row):
                    question = question_row.iloc[col_idx]
                    options = response_options_row.iloc[col_idx] if col_idx < len(response_options_row) else None
                    
                    if pd.notna(question) and str(question).strip():
                        self.question_mapping[sheet_name][col_name] = {
                            'question': str(question).strip(),
                            'options': str(options).strip() if pd.notna(options) else None
                        }
    
    def _extract_text_responses(self, df: pd.DataFrame, sheet_name: str):
        """Extract text responses for NLP analysis"""
        if sheet_name not in self.text_responses:
            self.text_responses[sheet_name] = {}
        
        # Identify text response columns (longer text, not categorical)
        for col in df.columns:
            if col in df.columns:
                # Get non-null values
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    # Check if it's likely a text response column
                    sample_values = non_null_values.head(10)
                    string_values = sample_values.astype(str)
                    avg_length = string_values.str.len().mean()
                    
                    # Consider it text if average length > 20 chars and has varied content
                    if avg_length > 20 and len(string_values.unique()) > len(string_values) * 0.5:
                        self.text_responses[sheet_name][col] = non_null_values.tolist()
    
    def get_countries(self) -> List[str]:
        """Get list of countries in the data"""
        countries = set()
        for sheet_name, df in self.processed_data.items():
            if 'Country' in df.columns:
                countries.update(df['Country'].unique())
        return sorted(list(countries))
    
    def get_nationalities(self, country: Optional[str] = None) -> List[str]:
        """Get list of nationalities"""
        nationalities = set()
        for sheet_name, df in self.processed_data.items():
            if country and 'Country' in df.columns:
                df = df[df['Country'] == country]
            
            # Look for nationality column (usually A1)
            for col in df.columns:
                if 'nationality' in col.lower() or col == 'A1':
                    nationalities.update(df[col].dropna().unique())
        
        return sorted(list(nationalities))
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get all available filter options"""
        filters = {
            'countries': self.get_countries(),
            'nationalities': self.get_nationalities()
        }
        
        # Add other categorical filters
        categorical_columns = []
        for sheet_name, df in self.processed_data.items():
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].nunique() <= 20:  # Reasonable category count
                    if col not in ['Country'] and col not in categorical_columns:
                        categorical_columns.append(col)
        
        for col in categorical_columns[:10]:  # Limit to top 10 for performance
            values = set()
            for df in self.processed_data.values():
                if col in df.columns:
                    values.update(df[col].dropna().unique())
            filters[col] = sorted(list(values))
        
        return filters
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on provided filters"""
        combined_df = pd.concat([df for df in self.processed_data.values()], ignore_index=True)
        
        for filter_col, filter_val in filters.items():
            if filter_val and filter_col in combined_df.columns:
                if isinstance(filter_val, list):
                    combined_df = combined_df[combined_df[filter_col].isin(filter_val)]
                else:
                    combined_df = combined_df[combined_df[filter_col] == filter_val]
        
        return combined_df
    
    def get_summary_stats(self, filtered_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Get summary statistics"""
        if filtered_df is None:
            filtered_df = pd.concat([df for df in self.processed_data.values()], ignore_index=True)
        
        stats = {
            'total_responses': len(filtered_df),
            'countries': filtered_df['Country'].value_counts().to_dict() if 'Country' in filtered_df.columns else {},
            'response_distribution': {}
        }
        
        # Add response distributions for key questions
        for col in filtered_df.columns:
            if filtered_df[col].dtype == 'object' and filtered_df[col].nunique() <= 10:
                stats['response_distribution'][col] = filtered_df[col].value_counts().to_dict()
        
        return stats
    
    def analyze_text_responses(self, column: str, country: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text responses using NLP"""
        all_texts = []
        
        # Collect text responses
        for sheet_name, texts in self.text_responses.items():
            if column in texts:
                if country:
                    # Filter by country if specified
                    df = self.processed_data[sheet_name]
                    if 'Country' in df.columns:
                        country_df = df[df['Country'] == country]
                        # Match texts to filtered data (simplified approach)
                        all_texts.extend(texts[column])
                else:
                    all_texts.extend(texts[column])
        
        if not all_texts:
            return {'error': 'No text responses found'}
        
        # Clean texts
        cleaned_texts = [str(text).strip() for text in all_texts if text and str(text).strip()]
        
        if not cleaned_texts:
            return {'error': 'No valid text responses found'}
        
        # Sentiment analysis
        sentiments = []
        for text in cleaned_texts:
            blob = TextBlob(text)
            sentiments.append({
                'text': text,
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            })
        
        # Overall sentiment summary
        avg_polarity = np.mean([s['polarity'] for s in sentiments])
        avg_subjectivity = np.mean([s['subjectivity'] for s in sentiments])
        
        # Keyword extraction using TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words='english',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            keywords = [
                {'word': feature_names[i], 'score': float(mean_scores[i])}
                for i in np.argsort(mean_scores)[::-1][:10]
            ]
        except Exception as e:
            keywords = []
        
        # Theme clustering (simplified)
        themes = []
        if len(cleaned_texts) >= 3:
            try:
                n_clusters = min(5, len(cleaned_texts) // 2)
                vectorizer_cluster = TfidfVectorizer(stop_words='english', max_features=50)
                X = vectorizer_cluster.fit_transform(cleaned_texts)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(X)
                
                for i in range(n_clusters):
                    cluster_texts = [cleaned_texts[j] for j in range(len(cleaned_texts)) if clusters[j] == i]
                    themes.append({
                        'theme_id': i,
                        'sample_texts': cluster_texts[:3],
                        'count': len(cluster_texts)
                    })
            except Exception as e:
                themes = []
        
        return {
            'total_responses': len(cleaned_texts),
            'sentiment_summary': {
                'average_polarity': float(avg_polarity),
                'average_subjectivity': float(avg_subjectivity),
                'sentiment_label': self._get_sentiment_label(avg_polarity)
            },
            'top_keywords': keywords,
            'themes': themes,
            'sample_responses': cleaned_texts[:5]
        }
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity score to sentiment label"""
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def get_raw_data_json(self, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Get raw data in JSON format for frontend display"""
        if sheet_name and sheet_name in self.processed_data:
            df = self.processed_data[sheet_name]
            return {
                'sheet_name': sheet_name,
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'shape': df.shape
            }
        else:
            # Return all sheets
            result = {}
            for sheet_name, df in self.processed_data.items():
                result[sheet_name] = {
                    'data': df.to_dict('records'),
                    'columns': list(df.columns),
                    'shape': df.shape
                }
            return result
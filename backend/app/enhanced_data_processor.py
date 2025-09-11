#!/usr/bin/env python3
"""
Enhanced data processing module for survey data analysis
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

class EnhancedSurveyDataProcessor:
    """Enhanced processor for survey data with proper column mapping"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.raw_sheets = {}
        self.processed_data = {}
        self.question_mapping = {}
        self.text_responses = {}
        self.column_mapping = {}
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Load and process data with proper column mapping"""
        try:
            # Load raw Excel data
            xl = pd.ExcelFile(self.data_file)
            print(f"Loading Excel file with sheets: {xl.sheet_names}")
            
            for sheet_name in xl.sheet_names:
                # Load the raw sheet
                raw_df = pd.read_excel(self.data_file, sheet_name=sheet_name)
                self.raw_sheets[sheet_name] = raw_df
                print(f"Loaded {sheet_name}: {raw_df.shape}")
                
                # Process the sheet
                processed_df, questions, text_cols = self._process_sheet(raw_df, sheet_name)
                
                if processed_df is not None and not processed_df.empty:
                    self.processed_data[sheet_name] = processed_df
                    self.question_mapping[sheet_name] = questions
                    self.text_responses[sheet_name] = text_cols
                    print(f"Processed {sheet_name}: {processed_df.shape} with {len(questions)} questions")
        
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def _process_sheet(self, df: pd.DataFrame, sheet_name: str) -> Tuple[pd.DataFrame, Dict, Dict]:
        """Process individual sheet with proper structure analysis"""
        try:
            if len(df) < 3:
                return None, {}, {}
            
            # Analyze the sheet structure
            # Row 0: Question text
            # Row 1: Response options/codes
            # Row 2+: Actual survey responses
            
            question_row = df.iloc[0] if len(df) > 0 else pd.Series()
            options_row = df.iloc[1] if len(df) > 1 else pd.Series()
            
            # Start processing from row 2 (actual responses)
            data_rows = df.iloc[2:].copy()
            
            # Create proper column mapping
            column_mapping = {}
            questions = {}
            
            for i, (col_name, question) in enumerate(question_row.items()):
                # Get the original column name and question text
                original_col = df.columns[i]
                question_text = str(question).strip() if pd.notna(question) else ""
                options_text = str(options_row.iloc[i]).strip() if i < len(options_row) and pd.notna(options_row.iloc[i]) else ""
                
                # Create a clean column name
                if len(question_text) > 5 and question_text != "Question":
                    clean_name = self._clean_column_name(question_text)
                    column_mapping[original_col] = clean_name
                    questions[clean_name] = {
                        'question': question_text,
                        'options': options_text,
                        'original_column': original_col
                    }
                else:
                    # Keep original name for non-question columns
                    column_mapping[original_col] = original_col
            
            # Apply column mapping
            data_rows = data_rows.rename(columns=column_mapping)
            
            # Add country information
            country = 'UAE' if 'UAE' in sheet_name else 'KSA' if 'KSA' in sheet_name else 'Unknown'
            data_rows['Country'] = country
            
            # Clean and process the data
            processed_df = self._clean_data_rows(data_rows)
            
            # Extract text responses
            text_columns = self._identify_text_columns(processed_df, questions)
            
            return processed_df, questions, text_columns
        
        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")
            return None, {}, {}
    
    def _clean_column_name(self, text: str) -> str:
        """Create clean column name from question text"""
        # Take first 40 characters and clean
        clean = text[:40]
        # Remove special characters, keep alphanumeric and spaces
        clean = re.sub(r'[^\w\s-]', '', clean)
        # Replace multiple spaces with single space
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean
    
    def _clean_data_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the actual survey response data"""
        # Remove rows that are obviously headers or empty
        cleaned_df = df.copy()
        
        # Remove rows where most values are NaN
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Remove rows that look like headers (e.g., containing "Response", "Question")
        header_patterns = ['Response', 'Question', 'S. No.', 'Status']
        for pattern in header_patterns:
            mask = cleaned_df.astype(str).apply(lambda x: x.str.contains(pattern, case=False, na=False)).any(axis=1)
            cleaned_df = cleaned_df[~mask]
        
        # Reset index
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        return cleaned_df
    
    def _identify_text_columns(self, df: pd.DataFrame, questions: Dict) -> Dict[str, List]:
        """Identify columns containing text responses for NLP analysis"""
        text_columns = {}
        
        for col in df.columns:
            if col == 'Country':
                continue
                
            try:
                # Get non-null values
                non_null_values = df[col].dropna()
                if len(non_null_values) < 5:  # Need minimum responses
                    continue
                
                # Convert to string and check characteristics
                str_values = non_null_values.astype(str)
                
                # Calculate average length
                avg_length = str_values.str.len().mean()
                
                # Check for text patterns (long responses, varied content)
                unique_ratio = len(str_values.unique()) / len(str_values)
                
                # Consider it a text column if:
                # 1. Average length > 15 characters
                # 2. High uniqueness ratio (> 0.3)
                # 3. Contains alphabetic characters
                has_letters = str_values.str.contains(r'[a-zA-Z]', na=False).any()
                
                if avg_length > 15 and unique_ratio > 0.3 and has_letters:
                    # Filter out obviously non-text responses
                    text_responses = []
                    for response in str_values:
                        # Skip numeric-only, single character, or obviously coded responses
                        if (len(str(response)) > 10 and 
                            not str(response).isdigit() and 
                            not str(response) in ['1', '2', '3', '4', '5', '99', 'A1', 'A2', 'A3', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']):
                            text_responses.append(response)
                    
                    if len(text_responses) >= 3:  # Minimum viable text responses
                        text_columns[col] = text_responses
                        print(f"Identified text column '{col}': {len(text_responses)} responses")
                
            except Exception as e:
                continue
        
        return text_columns
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get comprehensive filter options"""
        filters = {
            'countries': self.get_countries(),
            'nationalities': self.get_nationalities()
        }
        
        # Add survey-specific filters
        combined_df = self._get_combined_data()
        
        # Key survey question filters
        survey_filters = {
            'visit_purpose': 'What was the primary purpose of your visit',
            'hotel_frequency': 'How many times have you stayed in a hotel',
            'entertainment_importance': 'How important is in-room entertainment',
            'streaming_usage': 'Did you use the in-room TV or entertainment',
            'content_preference': 'What type of content did you watch'
        }
        
        for filter_key, question_pattern in survey_filters.items():
            matching_cols = [col for col in combined_df.columns 
                           if question_pattern.lower() in col.lower()]
            
            if matching_cols:
                col = matching_cols[0]
                try:
                    unique_vals = combined_df[col].dropna().astype(str).unique()
                    # Filter out obviously coded responses and keep meaningful ones
                    meaningful_vals = []
                    for val in unique_vals:
                        if (len(str(val)) > 0 and 
                            str(val) not in ['nan', '1', '2', '3', '4', '5', '99'] and
                            not str(val).startswith('A') and 
                            not str(val).startswith('B')):
                            meaningful_vals.append(val)
                    
                    if meaningful_vals:
                        filters[filter_key] = sorted(meaningful_vals)[:10]  # Limit options
                except Exception:
                    continue
        
        return filters
    
    def get_countries(self) -> List[str]:
        """Get list of countries"""
        countries = set()
        for df in self.processed_data.values():
            if 'Country' in df.columns:
                countries.update(df['Country'].dropna().unique())
        return sorted(list(countries))
    
    def get_nationalities(self) -> List[str]:
        """Get list of nationalities from survey responses"""
        nationalities = set()
        
        # Look for nationality question in processed data
        for sheet_name, df in self.processed_data.items():
            questions = self.question_mapping.get(sheet_name, {})
            
            # Find nationality column
            nationality_col = None
            for col, question_info in questions.items():
                if 'nationality' in question_info['question'].lower():
                    nationality_col = col
                    break
            
            if nationality_col and nationality_col in df.columns:
                unique_vals = df[nationality_col].dropna().astype(str).unique()
                # Filter for actual nationality names (longer than single characters/numbers)
                for val in unique_vals:
                    if (len(str(val)) > 2 and 
                        not str(val).isdigit() and 
                        str(val) not in ['A1', 'Question']):
                        nationalities.add(val)
        
        return sorted(list(nationalities))[:20]  # Limit to top 20
    
    def _get_combined_data(self) -> pd.DataFrame:
        """Get combined dataset from all sheets"""
        if not self.processed_data:
            return pd.DataFrame()
        
        dfs = list(self.processed_data.values())
        if not dfs:
            return pd.DataFrame()
        
        # Find common columns
        common_cols = set(dfs[0].columns)
        for df in dfs[1:]:
            common_cols = common_cols.intersection(set(df.columns))
        
        # Combine datasets with common columns
        combined_dfs = []
        for df in dfs:
            combined_dfs.append(df[list(common_cols)])
        
        return pd.concat(combined_dfs, ignore_index=True)
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the dataset"""
        combined_df = self._get_combined_data()
        
        if combined_df.empty:
            return combined_df
        
        for filter_name, filter_value in filters.items():
            if not filter_value or filter_value in ['', 'all', 'All']:
                continue
            
            # Handle different filter types
            if filter_name == 'country' and 'Country' in combined_df.columns:
                combined_df = combined_df[combined_df['Country'] == filter_value]
            
            elif filter_name == 'nationality':
                # Find nationality column
                nationality_cols = [col for col in combined_df.columns 
                                  if 'nationality' in col.lower()]
                if nationality_cols:
                    combined_df = combined_df[combined_df[nationality_cols[0]].astype(str) == str(filter_value)]
            
            else:
                # Generic filter - find matching column
                matching_cols = [col for col in combined_df.columns 
                               if filter_name.replace('_', ' ').lower() in col.lower()]
                if matching_cols:
                    col = matching_cols[0]
                    combined_df = combined_df[combined_df[col].astype(str) == str(filter_value)]
        
        return combined_df
    
    def get_summary_stats(self, filtered_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Get comprehensive summary statistics"""
        if filtered_df is None:
            filtered_df = self._get_combined_data()
        
        if filtered_df.empty:
            return {'total_responses': 0, 'countries': {}, 'analysis': {}}
        
        # Basic stats
        stats = {
            'total_responses': len(filtered_df),
            'countries': {},
            'analysis': {}
        }
        
        # Country distribution
        if 'Country' in filtered_df.columns:
            stats['countries'] = filtered_df['Country'].value_counts().to_dict()
        
        # Key survey analysis
        for col in filtered_df.columns:
            if col == 'Country':
                continue
            
            try:
                # Convert to string first to avoid type comparison issues
                col_series = filtered_df[col].dropna().astype(str)
                
                # Skip if too many unique values (likely text/ID columns)
                unique_count = col_series.nunique()
                if unique_count > 20:
                    continue
                
                # Get value distribution
                value_counts = col_series.value_counts()
                if len(value_counts) > 0 and len(value_counts) <= 10:
                    # Clean up the column name for display
                    display_name = col[:50] + "..." if len(col) > 50 else col
                    stats['analysis'][display_name] = value_counts.head(5).to_dict()
            
            except Exception as e:
                print(f"Error processing column {col} in summary stats: {e}")
                continue
        
        return stats
    
    def analyze_text_responses(self, column: str, country: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced NLP analysis of text responses"""
        all_texts = []
        
        # Collect text responses from all sheets
        for sheet_name, text_cols in self.text_responses.items():
            # Find matching column (partial match)
            matching_col = None
            for col_name in text_cols.keys():
                if column.lower() in col_name.lower() or col_name.lower() in column.lower():
                    matching_col = col_name
                    break
            
            if matching_col:
                texts = text_cols[matching_col]
                
                # Filter by country if specified
                if country:
                    df = self.processed_data.get(sheet_name)
                    if df is not None and 'Country' in df.columns:
                        country_mask = df['Country'] == country
                        # Simple approach: take proportional sample
                        country_ratio = country_mask.sum() / len(df)
                        sample_size = int(len(texts) * country_ratio)
                        texts = texts[:sample_size] if sample_size > 0 else texts
                
                all_texts.extend(texts)
        
        if not all_texts:
            return {'error': f'No text responses found for column: {column}'}
        
        # Clean and validate texts
        cleaned_texts = []
        for text in all_texts:
            text_str = str(text).strip()
            if (len(text_str) > 5 and 
                text_str.lower() not in ['nan', 'none', 'null'] and
                not text_str.isdigit()):
                cleaned_texts.append(text_str)
        
        if len(cleaned_texts) < 3:
            return {'error': f'Insufficient text responses found: {len(cleaned_texts)}'}
        
        # Perform comprehensive NLP analysis
        try:
            # Sentiment Analysis
            sentiments = []
            for text in cleaned_texts:
                blob = TextBlob(text)
                sentiments.append({
                    'text': text,
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                })
            
            avg_polarity = np.mean([s['polarity'] for s in sentiments])
            avg_subjectivity = np.mean([s['subjectivity'] for s in sentiments])
            
            # Keyword Extraction
            keywords = []
            try:
                vectorizer = TfidfVectorizer(
                    max_features=30,
                    stop_words='english',
                    ngram_range=(1, 3),
                    min_df=2
                )
                tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
                feature_names = vectorizer.get_feature_names_out()
                mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
                
                keyword_scores = [(feature_names[i], float(mean_scores[i])) 
                                for i in np.argsort(mean_scores)[::-1]]
                keywords = [{'word': word, 'score': score} 
                          for word, score in keyword_scores[:15]]
            except Exception as e:
                print(f"Keyword extraction error: {e}")
                keywords = []
            
            # Theme Analysis
            themes = []
            try:
                if len(cleaned_texts) >= 5:
                    n_clusters = min(5, max(2, len(cleaned_texts) // 10))
                    vectorizer_cluster = TfidfVectorizer(
                        stop_words='english', 
                        max_features=100,
                        min_df=2
                    )
                    X = vectorizer_cluster.fit_transform(cleaned_texts)
                    
                    if X.shape[0] >= n_clusters:
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        clusters = kmeans.fit_predict(X)
                        
                        for i in range(n_clusters):
                            cluster_texts = [cleaned_texts[j] for j in range(len(cleaned_texts)) 
                                           if clusters[j] == i]
                            if cluster_texts:
                                themes.append({
                                    'theme_id': i + 1,
                                    'sample_texts': cluster_texts[:3],
                                    'count': len(cluster_texts),
                                    'percentage': round(len(cluster_texts) / len(cleaned_texts) * 100, 1)
                                })
            except Exception as e:
                print(f"Theme analysis error: {e}")
                themes = []
            
            # Sentiment distribution
            sentiment_dist = {
                'positive': len([s for s in sentiments if s['polarity'] > 0.1]),
                'neutral': len([s for s in sentiments if -0.1 <= s['polarity'] <= 0.1]),
                'negative': len([s for s in sentiments if s['polarity'] < -0.1])
            }
            
            return {
                'total_responses': len(cleaned_texts),
                'sentiment_summary': {
                    'average_polarity': round(float(avg_polarity), 3),
                    'average_subjectivity': round(float(avg_subjectivity), 3),
                    'sentiment_label': self._get_sentiment_label(avg_polarity),
                    'distribution': sentiment_dist
                },
                'top_keywords': keywords,
                'themes': themes,
                'sample_responses': cleaned_texts[:8],
                'insights': self._generate_insights(cleaned_texts, avg_polarity, keywords, themes)
            }
        
        except Exception as e:
            print(f"NLP analysis error: {e}")
            return {
                'error': f'Analysis failed: {str(e)}',
                'total_responses': len(cleaned_texts),
                'sample_responses': cleaned_texts[:5]
            }
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity to sentiment label"""
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _generate_insights(self, texts: List[str], polarity: float, keywords: List, themes: List) -> List[str]:
        """Generate actionable insights from the analysis"""
        insights = []
        
        # Sentiment insights
        if polarity > 0.3:
            insights.append("Strong positive sentiment indicates high satisfaction levels")
        elif polarity < -0.3:
            insights.append("Negative sentiment suggests areas needing improvement")
        else:
            insights.append("Mixed sentiment indicates varied guest experiences")
        
        # Keyword insights
        if keywords:
            top_words = [k['word'] for k in keywords[:3]]
            insights.append(f"Key topics of concern: {', '.join(top_words)}")
        
        # Theme insights
        if themes:
            largest_theme = max(themes, key=lambda x: x['count'])
            insights.append(f"Primary theme represents {largest_theme['percentage']}% of responses")
        
        # Volume insights
        if len(texts) > 100:
            insights.append("High response volume provides statistically significant insights")
        elif len(texts) < 20:
            insights.append("Limited responses - consider gathering more feedback")
        
        return insights
    
    def get_text_columns(self) -> Dict[str, List[str]]:
        """Get available text columns for analysis"""
        result = {}
        for sheet_name, text_cols in self.text_responses.items():
            result[sheet_name] = list(text_cols.keys())
        return result
    
    def get_raw_data(self, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Get raw data for viewing"""
        if sheet_name and sheet_name in self.processed_data:
            df = self.processed_data[sheet_name]
            return {
                'sheet_name': sheet_name,
                'data': df.head(100).to_dict('records'),  # Limit for performance
                'columns': list(df.columns),
                'shape': df.shape,
                'questions': self.question_mapping.get(sheet_name, {})
            }
        else:
            result = {}
            for sheet_name, df in self.processed_data.items():
                result[sheet_name] = {
                    'data': df.head(50).to_dict('records'),  # Smaller limit for multiple sheets
                    'columns': list(df.columns),
                    'shape': df.shape,
                    'questions': self.question_mapping.get(sheet_name, {})
                }
            return result
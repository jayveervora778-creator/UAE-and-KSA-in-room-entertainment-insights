#!/usr/bin/env python3
"""
Corrected data processing module for survey data analysis
Properly handles the exact Excel structure with 200 responses per sheet
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class CorrectedSurveyDataProcessor:
    """Corrected processor that properly handles the Excel structure"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.raw_sheets = {}
        self.processed_data = {}
        self.question_mapping = {}
        self.response_legends = {}
        self.text_responses = {}
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Load and process data with proper Excel structure handling"""
        try:
            xl = pd.ExcelFile(self.data_file)
            print(f"Loading Excel file with sheets: {xl.sheet_names}")
            
            for sheet_name in xl.sheet_names:
                # Load raw sheet without headers
                raw_df = pd.read_excel(self.data_file, sheet_name=sheet_name, header=None)
                self.raw_sheets[sheet_name] = raw_df
                print(f"Loaded {sheet_name}: {raw_df.shape}")
                
                # Process the sheet properly
                processed_df = self._process_sheet_correctly(raw_df, sheet_name)
                
                if processed_df is not None and not processed_df.empty:
                    self.processed_data[sheet_name] = processed_df
                    print(f"Processed {sheet_name}: {processed_df.shape} - {len(processed_df)} actual responses")
        
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_sheet_correctly(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Process sheet with correct understanding of Excel structure"""
        try:
            if len(df) < 5:
                return None
            
            # Extract the structure properly:
            # Row 0: Question codes (A1, A2, etc.)
            # Row 1: Question text  
            # Row 2: Response legends
            # Row 3: Data column headers
            # Row 4+: Actual survey data
            
            question_codes_row = df.iloc[0]
            questions_row = df.iloc[1] 
            legends_row = df.iloc[2]
            headers_row = df.iloc[3]
            
            # Start from row 4 for actual data
            data_df = df.iloc[4:].copy()
            
            # Use the headers from row 3
            data_df.columns = headers_row.values
            
            # Remove rows where S. No. is NaN (these are not valid responses)
            if 'S. No.' in data_df.columns:
                data_df = data_df.dropna(subset=['S. No.'])
            
            # Reset index
            data_df = data_df.reset_index(drop=True)
            
            # Add country information based on sheet name
            country = 'UAE' if 'UAE' in sheet_name else 'KSA'
            data_df['Country'] = country
            
            # Store question mapping and legends
            self._extract_questions_and_legends(question_codes_row, questions_row, legends_row, sheet_name)
            
            # Process text responses
            self._extract_text_responses_corrected(data_df, sheet_name)
            
            # Apply response legend mapping
            self._apply_response_legends(data_df, sheet_name)
            
            print(f"Final processed data for {sheet_name}: {len(data_df)} responses")
            return data_df
            
        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_questions_and_legends(self, codes_row, questions_row, legends_row, sheet_name):
        """Extract question mappings and response legends"""
        if sheet_name not in self.question_mapping:
            self.question_mapping[sheet_name] = {}
        if sheet_name not in self.response_legends:
            self.response_legends[sheet_name] = {}
        
        for i, (code, question, legend) in enumerate(zip(codes_row, questions_row, legends_row)):
            if pd.notna(code) and pd.notna(question) and str(code).strip() and str(question).strip():
                code_str = str(code).strip()
                question_str = str(question).strip()
                
                # Store question mapping
                self.question_mapping[sheet_name][code_str] = {
                    'question': question_str,
                    'legend': str(legend) if pd.notna(legend) else None
                }
                
                # Parse response legends
                if pd.notna(legend) and str(legend).strip():
                    legend_str = str(legend).strip()
                    legend_mapping = self._parse_legend(legend_str)
                    if legend_mapping:
                        self.response_legends[sheet_name][code_str] = legend_mapping
    
    def _parse_legend(self, legend_str: str) -> Dict[str, str]:
        """Parse legend string into mapping dict"""
        mapping = {}
        
        # Look for patterns like "1. Business\n2. Leisure"
        lines = legend_str.split('\n')
        for line in lines:
            line = line.strip()
            # Match patterns like "1. Business" or "99. Other"
            match = re.match(r'(\d+)\.\s*(.+)', line)
            if match:
                code = match.group(1)
                label = match.group(2).strip()
                mapping[code] = label
        
        return mapping
    
    def _apply_response_legends(self, df: pd.DataFrame, sheet_name: str):
        """Apply response legends to convert codes to readable labels"""
        legends = self.response_legends.get(sheet_name, {})
        
        for question_code, legend_mapping in legends.items():
            # Find columns that match this question code
            matching_cols = [col for col in df.columns if question_code in str(col)]
            
            for col in matching_cols:
                if col in df.columns:
                    # Apply mapping
                    df[col] = df[col].astype(str).map(lambda x: legend_mapping.get(str(x), x) if str(x) != 'nan' else None)
    
    def _extract_text_responses_corrected(self, df: pd.DataFrame, sheet_name: str):
        """Extract text responses correctly"""
        if sheet_name not in self.text_responses:
            self.text_responses[sheet_name] = {}
        
        for col in df.columns:
            if col in ['S. No.', 'Status', 'Respondent', 'Country']:
                continue
            
            try:
                # Get non-null values
                non_null_values = df[col].dropna()
                if len(non_null_values) < 3:
                    continue
                
                # Convert to string and analyze
                str_values = non_null_values.astype(str)
                
                # Check if it's likely a text column
                avg_length = str_values.str.len().mean()
                unique_ratio = len(str_values.unique()) / len(str_values)
                
                # Look for actual text responses (not just numbers or codes)
                text_like_responses = []
                for val in str_values:
                    val_str = str(val).strip()
                    # Skip numeric codes, single characters, and obvious non-text
                    if (len(val_str) > 8 and 
                        not val_str.isdigit() and 
                        not val_str in ['1', '2', '3', '4', '5', '99', 'nan'] and
                        any(c.isalpha() for c in val_str)):
                        text_like_responses.append(val_str)
                
                # If we have enough actual text responses, include this column
                if len(text_like_responses) >= 5:
                    self.text_responses[sheet_name][col] = text_like_responses
                    print(f"Text column '{col}': {len(text_like_responses)} responses")
            
            except Exception as e:
                continue
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get comprehensive and correct filter options"""
        filters = {
            'countries': self.get_countries(),
            'nationalities': self.get_nationalities()
        }
        
        # Add proper survey question filters
        combined_df = self._get_combined_data()
        
        if combined_df.empty:
            return filters
        
        # Visit purpose (A2 question)
        visit_purpose_cols = [col for col in combined_df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
        if visit_purpose_cols:
            purposes = combined_df[visit_purpose_cols[0]].dropna().unique()
            purposes = [p for p in purposes if str(p) not in ['nan', 'None']]
            filters['visit_purpose'] = sorted(list(purposes))
        
        # Hotel frequency (A3 question)
        frequency_cols = [col for col in combined_df.columns if 'A3' in str(col)]
        if frequency_cols:
            frequencies = combined_df[frequency_cols[0]].dropna().unique()
            frequencies = [f for f in frequencies if str(f) not in ['nan', 'None']]
            filters['hotel_frequency'] = sorted(list(frequencies))
        
        # Entertainment importance
        entertainment_cols = [col for col in combined_df.columns if 'entertainment' in str(col).lower() and 'important' in str(col).lower()]
        if entertainment_cols:
            importance = combined_df[entertainment_cols[0]].dropna().unique()
            importance = [i for i in importance if str(i) not in ['nan', 'None']]
            filters['entertainment_importance'] = sorted(list(importance))
        
        return filters
    
    def get_countries(self) -> List[str]:
        """Get list of countries"""
        countries = set()
        for df in self.processed_data.values():
            if 'Country' in df.columns:
                countries.update(df['Country'].unique())
        return sorted(list(countries))
    
    def get_nationalities(self) -> List[str]:
        """Get nationalities from A1 column"""
        nationalities = set()
        
        for sheet_name, df in self.processed_data.items():
            # Look for A1 column (nationality)
            nationality_col = None
            for col in df.columns:
                if 'A1' in str(col):
                    nationality_col = col
                    break
            
            if nationality_col and nationality_col in df.columns:
                values = df[nationality_col].dropna().unique()
                for val in values:
                    val_str = str(val).strip()
                    if val_str and val_str not in ['nan', 'None'] and len(val_str) > 2:
                        # Clean nationality names
                        val_str = val_str.replace('\xa0', ' ').strip()
                        nationalities.add(val_str)
        
        return sorted(list(nationalities))
    
    def _get_combined_data(self) -> pd.DataFrame:
        """Get properly combined dataset"""
        if not self.processed_data:
            return pd.DataFrame()
        
        # Simply concatenate all processed dataframes
        dfs = []
        for df in self.processed_data.values():
            dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True, sort=False)
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to get filtered dataset"""
        combined_df = self._get_combined_data()
        
        if combined_df.empty:
            return combined_df
        
        for filter_name, filter_value in filters.items():
            if not filter_value or filter_value in ['', 'all', 'All']:
                continue
            
            if filter_name == 'country' and 'Country' in combined_df.columns:
                combined_df = combined_df[combined_df['Country'] == filter_value]
            
            elif filter_name == 'nationality':
                # Find A1 column
                nationality_cols = [col for col in combined_df.columns if 'A1' in str(col)]
                if nationality_cols:
                    combined_df = combined_df[combined_df[nationality_cols[0]] == filter_value]
            
            elif filter_name == 'visit_purpose':
                # Find A2 column
                purpose_cols = [col for col in combined_df.columns if 'A2' in str(col) and 'A2-A' not in str(col)]
                if purpose_cols:
                    combined_df = combined_df[combined_df[purpose_cols[0]] == filter_value]
            
            elif filter_name == 'hotel_frequency':
                # Find A3 column
                frequency_cols = [col for col in combined_df.columns if 'A3' in str(col)]
                if frequency_cols:
                    combined_df = combined_df[combined_df[frequency_cols[0]] == filter_value]
        
        return combined_df
    
    def get_summary_stats(self, filtered_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Get accurate summary statistics"""
        if filtered_df is None:
            filtered_df = self._get_combined_data()
        
        if filtered_df.empty:
            return {'total_responses': 0, 'countries': {}, 'analysis': {}}
        
        stats = {
            'total_responses': len(filtered_df),
            'countries': {},
            'analysis': {}
        }
        
        # Country distribution
        if 'Country' in filtered_df.columns:
            stats['countries'] = filtered_df['Country'].value_counts().to_dict()
        
        # Key analysis for main survey questions
        analysis_columns = [
            ('A1', 'Nationality Distribution'),
            ('A2', 'Visit Purpose'),
            ('A3', 'Hotel Stay Frequency'),
        ]
        
        for col_pattern, display_name in analysis_columns:
            matching_cols = [col for col in filtered_df.columns if col_pattern in str(col)]
            if matching_cols:
                col = matching_cols[0]
                if 'A2-A' not in col:  # Skip the "Other" specification columns
                    value_counts = filtered_df[col].dropna().value_counts()
                    if len(value_counts) > 0:
                        stats['analysis'][display_name] = value_counts.head(8).to_dict()
        
        return stats
    
    def analyze_text_responses(self, column: str, country: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text responses with proper handling"""
        all_texts = []
        
        # Find matching text columns across sheets
        for sheet_name, text_cols in self.text_responses.items():
            matching_cols = [col for col in text_cols.keys() if column.lower() in col.lower()]
            
            if matching_cols:
                col_name = matching_cols[0]
                texts = text_cols[col_name]
                
                # Filter by country if specified
                if country:
                    # Get the sheet's data to filter by country
                    df = self.processed_data.get(sheet_name)
                    if df is not None and 'Country' in df.columns:
                        country_responses = df[df['Country'] == country]
                        # Take proportional sample based on country filter
                        if len(country_responses) > 0:
                            ratio = len(country_responses) / len(df)
                            sample_size = max(1, int(len(texts) * ratio))
                            texts = texts[:sample_size]
                
                all_texts.extend(texts)
        
        if not all_texts:
            return {'error': f'No text responses found for: {column}'}
        
        return self._perform_nlp_analysis(all_texts, column)
    
    def _perform_nlp_analysis(self, texts: List[str], column_name: str) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis"""
        if len(texts) < 3:
            return {'error': f'Insufficient text responses: {len(texts)}'}
        
        try:
            # Sentiment Analysis
            sentiments = []
            for text in texts:
                blob = TextBlob(text)
                sentiments.append({
                    'text': text,
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                })
            
            avg_polarity = np.mean([s['polarity'] for s in sentiments])
            avg_subjectivity = np.mean([s['subjectivity'] for s in sentiments])
            
            # Sentiment distribution
            positive_count = len([s for s in sentiments if s['polarity'] > 0.1])
            negative_count = len([s for s in sentiments if s['polarity'] < -0.1])
            neutral_count = len(texts) - positive_count - negative_count
            
            # Keyword extraction
            keywords = []
            try:
                vectorizer = TfidfVectorizer(
                    max_features=25,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=2 if len(texts) > 10 else 1
                )
                tfidf_matrix = vectorizer.fit_transform(texts)
                feature_names = vectorizer.get_feature_names_out()
                mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
                
                keyword_pairs = [(feature_names[i], float(mean_scores[i])) 
                               for i in np.argsort(mean_scores)[::-1]]
                keywords = [{'word': word, 'score': score} for word, score in keyword_pairs[:15]]
            except:
                keywords = []
            
            # Theme clustering
            themes = []
            try:
                if len(texts) >= 5:
                    n_clusters = min(4, max(2, len(texts) // 8))
                    vectorizer_theme = TfidfVectorizer(stop_words='english', max_features=50, min_df=1)
                    X = vectorizer_theme.fit_transform(texts)
                    
                    if X.shape[0] >= n_clusters:
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        clusters = kmeans.fit_predict(X)
                        
                        for i in range(n_clusters):
                            cluster_texts = [texts[j] for j in range(len(texts)) if clusters[j] == i]
                            if cluster_texts:
                                themes.append({
                                    'theme_id': i + 1,
                                    'count': len(cluster_texts),
                                    'percentage': round(len(cluster_texts) / len(texts) * 100, 1),
                                    'sample_texts': cluster_texts[:3]
                                })
            except:
                themes = []
            
            return {
                'total_responses': len(texts),
                'column_analyzed': column_name,
                'sentiment_summary': {
                    'average_polarity': round(float(avg_polarity), 3),
                    'average_subjectivity': round(float(avg_subjectivity), 3),
                    'sentiment_label': self._get_sentiment_label(avg_polarity),
                    'distribution': {
                        'positive': positive_count,
                        'neutral': neutral_count,
                        'negative': negative_count
                    }
                },
                'top_keywords': keywords,
                'themes': sorted(themes, key=lambda x: x['count'], reverse=True),
                'sample_responses': texts[:8],
                'insights': self._generate_insights(texts, avg_polarity, keywords, themes)
            }
        
        except Exception as e:
            print(f"NLP analysis error: {e}")
            return {
                'error': f'Analysis failed: {str(e)}',
                'total_responses': len(texts),
                'sample_responses': texts[:5]
            }
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity to sentiment label"""
        if polarity > 0.2:
            return 'Positive'
        elif polarity < -0.2:
            return 'Negative' 
        else:
            return 'Neutral'
    
    def _generate_insights(self, texts: List[str], polarity: float, keywords: List, themes: List) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        # Sentiment insights
        if polarity > 0.3:
            insights.append("Strong positive sentiment indicates high guest satisfaction")
        elif polarity < -0.3:
            insights.append("Negative sentiment highlights areas needing improvement")
        else:
            insights.append("Mixed sentiment suggests varied guest experiences")
        
        # Keyword insights
        if keywords and len(keywords) >= 3:
            top_terms = [k['word'] for k in keywords[:3]]
            insights.append(f"Most discussed topics: {', '.join(top_terms)}")
        
        # Theme insights
        if themes:
            largest_theme = max(themes, key=lambda x: x['count'])
            insights.append(f"Primary concern category represents {largest_theme['percentage']}% of feedback")
        
        # Volume insights
        if len(texts) > 50:
            insights.append("High response volume provides statistically reliable insights")
        elif len(texts) < 15:
            insights.append("Limited feedback - consider collecting more responses")
        
        return insights
    
    def get_text_columns(self) -> Dict[str, List[str]]:
        """Get available text response columns"""
        result = {}
        for sheet_name, text_cols in self.text_responses.items():
            # Create readable column names
            readable_cols = []
            for col in text_cols.keys():
                # Try to find the question text for this column
                question_text = None
                for code, info in self.question_mapping.get(sheet_name, {}).items():
                    if code in str(col):
                        question_text = info['question']
                        break
                
                if question_text:
                    readable_cols.append(question_text[:60] + "..." if len(question_text) > 60 else question_text)
                else:
                    readable_cols.append(col)
            
            result[sheet_name] = readable_cols
        return result
    
    def get_raw_data(self, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Get properly formatted raw data"""
        if sheet_name and sheet_name in self.processed_data:
            df = self.processed_data[sheet_name]
            questions = self.question_mapping.get(sheet_name, {})
            
            return {
                'sheet_name': sheet_name,
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'shape': df.shape,
                'questions': questions,
                'response_legends': self.response_legends.get(sheet_name, {})
            }
        else:
            result = {}
            for sheet_name, df in self.processed_data.items():
                questions = self.question_mapping.get(sheet_name, {})
                result[sheet_name] = {
                    'data': df.head(50).to_dict('records'),  # Limit for performance
                    'columns': list(df.columns),
                    'shape': df.shape,
                    'questions': questions,
                    'response_legends': self.response_legends.get(sheet_name, {})
                }
            return result
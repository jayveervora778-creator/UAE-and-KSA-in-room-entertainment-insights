#!/usr/bin/env python3
"""
Fixed data processing module that properly handles multi-response questions
Correctly processes B1-A and other multi-choice survey questions
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class FixedMultiResponseProcessor:
    """Fixed processor that correctly handles multi-response questions"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.raw_sheets = {}
        self.processed_data = {}
        self.question_mapping = {}
        self.response_legends = {}
        self.text_responses = {}
        self.multi_response_questions = {}
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Load and process data with proper multi-response handling"""
        try:
            xl = pd.ExcelFile(self.data_file)
            print(f"Loading Excel file with sheets: {xl.sheet_names}")
            
            for sheet_name in xl.sheet_names:
                # Load raw sheet without headers
                raw_df = pd.read_excel(self.data_file, sheet_name=sheet_name, header=None)
                self.raw_sheets[sheet_name] = raw_df
                print(f"Loaded {sheet_name}: {raw_df.shape}")
                
                # Process the sheet with multi-response handling
                processed_df = self._process_sheet_with_multiresponse(raw_df, sheet_name)
                
                if processed_df is not None and not processed_df.empty:
                    self.processed_data[sheet_name] = processed_df
                    print(f"Processed {sheet_name}: {processed_df.shape} - {len(processed_df)} actual responses")
        
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_sheet_with_multiresponse(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Process sheet with correct multi-response question handling"""
        try:
            if len(df) < 5:
                return None
            
            # Extract structure:
            # Row 0: Question codes (A1, A2, B1-A, etc.)
            # Row 1: Question text  
            # Row 2: Response legends
            # Row 3: Data column headers (A1, B1-A/1, B1-A/2, etc.)
            # Row 4+: Actual survey data
            
            question_codes_row = df.iloc[0]
            questions_row = df.iloc[1] 
            legends_row = df.iloc[2]
            headers_row = df.iloc[3]
            
            # Start from row 4 for actual data
            data_df = df.iloc[4:].copy()
            data_df.columns = headers_row.values
            
            # Remove rows where S. No. is NaN
            if 'S. No.' in data_df.columns:
                data_df = data_df.dropna(subset=['S. No.'])
            
            data_df = data_df.reset_index(drop=True)
            
            # Add country information
            country = 'UAE' if 'UAE' in sheet_name else 'KSA'
            data_df['Country'] = country
            
            # Extract questions and legends
            self._extract_questions_and_legends_fixed(question_codes_row, questions_row, legends_row, headers_row, sheet_name)
            
            # Process multi-response questions (like B1-A)
            data_df = self._process_multiresponse_questions(data_df, sheet_name)
            
            # Process text responses
            self._extract_text_responses_corrected(data_df, sheet_name)
            
            # Apply response legends for single-response questions
            self._apply_response_legends_fixed(data_df, sheet_name)
            
            print(f"Final processed data for {sheet_name}: {len(data_df)} responses")
            return data_df
            
        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_questions_and_legends_fixed(self, codes_row, questions_row, legends_row, headers_row, sheet_name):
        """Extract question mappings and identify multi-response questions"""
        if sheet_name not in self.question_mapping:
            self.question_mapping[sheet_name] = {}
        if sheet_name not in self.response_legends:
            self.response_legends[sheet_name] = {}
        if sheet_name not in self.multi_response_questions:
            self.multi_response_questions[sheet_name] = {}
        
        # First, identify multi-response question patterns
        multi_response_patterns = {}
        
        for i, header in enumerate(headers_row):
            if pd.notna(header):
                header_str = str(header).strip()
                # Look for patterns like B1-A/1, B1-A/2, etc.
                match = re.match(r'([A-Z0-9-]+)/(\d+)', header_str)
                if match:
                    base_code = match.group(1)
                    sub_index = match.group(2)
                    
                    if base_code not in multi_response_patterns:
                        multi_response_patterns[base_code] = []
                    multi_response_patterns[base_code].append((i, header_str, sub_index))
        
        # Store multi-response question info
        for base_code, columns in multi_response_patterns.items():
            # Find the corresponding question text and legend
            question_text = None
            legend_text = None
            
            for i, (code, question, legend) in enumerate(zip(codes_row, questions_row, legends_row)):
                if pd.notna(code) and str(code).strip() == base_code:
                    question_text = str(question).strip() if pd.notna(question) else None
                    legend_text = str(legend).strip() if pd.notna(legend) else None
                    break
            
            if question_text:
                self.multi_response_questions[sheet_name][base_code] = {
                    'question': question_text,
                    'legend': legend_text,
                    'columns': columns,
                    'legend_mapping': self._parse_legend(legend_text) if legend_text else {}
                }
        
        # Store regular single-response questions
        for i, (code, question, legend) in enumerate(zip(codes_row, questions_row, legends_row)):
            if pd.notna(code) and pd.notna(question) and str(code).strip() and str(question).strip():
                code_str = str(code).strip()
                question_str = str(question).strip()
                
                # Skip if this is already handled as multi-response
                if code_str not in multi_response_patterns:
                    self.question_mapping[sheet_name][code_str] = {
                        'question': question_str,
                        'legend': str(legend) if pd.notna(legend) else None
                    }
                    
                    # Parse response legends for single-response questions
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
    
    def _process_multiresponse_questions(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Process multi-response questions into aggregated columns"""
        multi_questions = self.multi_response_questions.get(sheet_name, {})
        
        for question_code, info in multi_questions.items():
            columns = info['columns']
            legend_mapping = info['legend_mapping']
            
            print(f"Processing multi-response question {question_code}: {info['question']}")
            
            # Create aggregated response counts for this question
            response_counts = {}
            
            for _, column_header, sub_index in columns:
                if column_header in df.columns:
                    # Get all non-null responses from this column
                    responses = df[column_header].dropna()
                    
                    for response in responses:
                        response_str = str(int(float(response))) if pd.notna(response) else None
                        if response_str and response_str in legend_mapping:
                            label = legend_mapping[response_str]
                            response_counts[label] = response_counts.get(label, 0) + 1
            
            print(f"  Response distribution: {response_counts}")
            
            # Store this for later use in visualizations
            self.multi_response_questions[sheet_name][question_code]['response_counts'] = response_counts
            
            # Also create individual choice columns for correlation analysis
            for choice_label in legend_mapping.values():
                new_col = f"{question_code}_{choice_label.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}"
                df[new_col] = 0
                
                # Mark 1 for respondents who chose this option
                for _, column_header, sub_index in columns:
                    if column_header in df.columns:
                        for idx, response in df[column_header].items():
                            if pd.notna(response):
                                response_str = str(int(float(response)))
                                if response_str in legend_mapping and legend_mapping[response_str] == choice_label:
                                    df.at[idx, new_col] = 1
            
            # Remove the original sub-columns to avoid confusion
            for _, column_header, sub_index in columns:
                if column_header in df.columns:
                    df = df.drop(columns=[column_header])
        
        return df
    
    def _apply_response_legends_fixed(self, df: pd.DataFrame, sheet_name: str):
        """Apply response legends for single-response questions only"""
        legends = self.response_legends.get(sheet_name, {})
        
        for question_code, legend_mapping in legends.items():
            # Find columns that match this question code (but avoid multi-response columns)
            matching_cols = []
            for col in df.columns:
                if question_code in str(col) and '/' not in str(col) and '_' not in str(col):
                    matching_cols.append(col)
            
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
            
            # Skip the auto-generated binary columns for multi-response
            if any(pattern in str(col) for pattern in ['B1-A_', 'C2-A_', 'C3_']):
                continue
            
            try:
                # Get non-null values
                non_null_values = df[col].dropna()
                if len(non_null_values) < 3:
                    continue
                
                # Convert to string and analyze
                str_values = non_null_values.astype(str)
                
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
    
    def get_multiresponse_data(self) -> Dict[str, Dict[str, Any]]:
        """Get multi-response question data for visualization"""
        result = {}
        
        for sheet_name, multi_questions in self.multi_response_questions.items():
            result[sheet_name] = {}
            
            for question_code, info in multi_questions.items():
                result[sheet_name][question_code] = {
                    'question': info['question'],
                    'response_counts': info.get('response_counts', {}),
                    'total_responses': sum(info.get('response_counts', {}).values())
                }
        
        return result
    
    def get_combined_multiresponse_data(self) -> Dict[str, Dict[str, Any]]:
        """Get combined multi-response data across all sheets"""
        combined = {}
        
        multi_data = self.get_multiresponse_data()
        
        # Combine across sheets
        for sheet_name, questions in multi_data.items():
            for question_code, info in questions.items():
                if question_code not in combined:
                    combined[question_code] = {
                        'question': info['question'],
                        'response_counts': info['response_counts'].copy(),
                        'total_responses': info['total_responses']
                    }
                else:
                    # Combine response counts
                    for choice, count in info['response_counts'].items():
                        combined[question_code]['response_counts'][choice] = combined[question_code]['response_counts'].get(choice, 0) + count
                    combined[question_code]['total_responses'] += info['total_responses']
        
        return combined
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get comprehensive filter options"""
        filters = {
            'countries': self.get_countries(),
            'nationalities': self.get_nationalities()
        }
        
        # Add proper survey question filters
        combined_df = self._get_combined_data()
        
        if combined_df.empty:
            return filters
        
        # Visit purpose (A2 question)
        visit_purpose_cols = [col for col in combined_df.columns if col == 'A2']
        if visit_purpose_cols:
            purposes = combined_df[visit_purpose_cols[0]].dropna().unique()
            purposes = [p for p in purposes if str(p) not in ['nan', 'None']]
            filters['visit_purpose'] = sorted(list(purposes))
        
        # Hotel frequency (A3 question)
        frequency_cols = [col for col in combined_df.columns if col == 'A3']
        if frequency_cols:
            frequencies = combined_df[frequency_cols[0]].dropna().unique()
            frequencies = [f for f in frequencies if str(f) not in ['nan', 'None']]
            filters['hotel_frequency'] = sorted(list(frequencies))
        
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
            if 'A1' in df.columns:
                values = df['A1'].dropna().unique()
                for val in values:
                    val_str = str(val).strip()
                    if val_str and val_str not in ['nan', 'None'] and len(val_str) > 2:
                        val_str = val_str.replace('\xa0', ' ').strip()
                        nationalities.add(val_str)
        
        return sorted(list(nationalities))
    
    def _get_combined_data(self) -> pd.DataFrame:
        """Get properly combined dataset"""
        if not self.processed_data:
            return pd.DataFrame()
        
        dfs = list(self.processed_data.values())
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
            
            elif filter_name == 'nationality' and 'A1' in combined_df.columns:
                combined_df = combined_df[combined_df['A1'] == filter_value]
            
            elif filter_name == 'visit_purpose' and 'A2' in combined_df.columns:
                combined_df = combined_df[combined_df['A2'] == filter_value]
            
            elif filter_name == 'hotel_frequency' and 'A3' in combined_df.columns:
                combined_df = combined_df[combined_df['A3'] == filter_value]
        
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
            if col_pattern in filtered_df.columns:
                value_counts = filtered_df[col_pattern].dropna().value_counts()
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
                'sample_responses': texts[:8]
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
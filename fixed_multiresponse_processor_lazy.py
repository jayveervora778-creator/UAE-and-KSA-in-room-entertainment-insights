#!/usr/bin/env python3
"""
Fixed data processing module with lazy loading to avoid import hangs
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
    """Fixed processor with lazy data loading"""
    
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.raw_sheets = {}
        self.processed_data = {}
        self.question_mapping = {}
        self.response_legends = {}
        self.text_responses = {}
        self.multi_response_questions = {}
        self._data_loaded = False
    
    def _ensure_data_loaded(self):
        """Lazy load data only when needed"""
        if not self._data_loaded:
            self._load_and_process_data()
            self._data_loaded = True
    
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
            
            # Extract structure
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
    
    def get_combined_multiresponse_data(self) -> Dict[str, Dict[str, Any]]:
        """Get combined multi-response data across all sheets"""
        self._ensure_data_loaded()
        
        combined = {}
        
        # Combine across sheets
        for sheet_name, multi_questions in self.multi_response_questions.items():
            for question_code, info in multi_questions.items():
                if 'response_counts' in info and info['response_counts']:
                    if question_code not in combined:
                        combined[question_code] = {
                            'question': info['question'],
                            'response_counts': info['response_counts'].copy(),
                            'total_responses': sum(info['response_counts'].values())
                        }
                    else:
                        # Combine response counts
                        for choice, count in info['response_counts'].items():
                            combined[question_code]['response_counts'][choice] = combined[question_code]['response_counts'].get(choice, 0) + count
                        combined[question_code]['total_responses'] = sum(combined[question_code]['response_counts'].values())
        
        return combined
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """Get comprehensive filter options"""
        self._ensure_data_loaded()
        
        filters = {
            'countries': self.get_countries(),
            'nationalities': self.get_nationalities()
        }
        
        # Add proper survey question filters
        combined_df = self._get_combined_data()
        
        if combined_df.empty:
            return filters
        
        # Visit purpose (A2 question)
        if 'A2' in combined_df.columns:
            purposes = combined_df['A2'].dropna().unique()
            purposes = [p for p in purposes if str(p) not in ['nan', 'None']]
            filters['visit_purpose'] = sorted(list(purposes))
        
        # Hotel frequency (A3 question)
        if 'A3' in combined_df.columns:
            frequencies = combined_df['A3'].dropna().unique()
            frequencies = [f for f in frequencies if str(f) not in ['nan', 'None']]
            filters['hotel_frequency'] = sorted(list(frequencies))
        
        return filters
    
    def get_countries(self) -> List[str]:
        """Get list of countries"""
        self._ensure_data_loaded()
        
        countries = set()
        for df in self.processed_data.values():
            if 'Country' in df.columns:
                countries.update(df['Country'].unique())
        return sorted(list(countries))
    
    def get_nationalities(self) -> List[str]:
        """Get nationalities from A1 column"""
        self._ensure_data_loaded()
        
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
        self._ensure_data_loaded()
        
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
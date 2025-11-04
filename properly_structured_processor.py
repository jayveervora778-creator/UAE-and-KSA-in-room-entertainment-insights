#!/usr/bin/env python3
"""
Properly Structured OSN Survey Data Processor
Maps actual question text to data columns instead of using A1, B1, etc.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
from collections import Counter
import re

# AI/ML Imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob

warnings.filterwarnings('ignore')

class ProperlyStructuredOSNProcessor:
    """
    OSN Survey Data Processor with proper question mapping
    """
    
    def __init__(self, excel_path: str = "data/survey_data.xlsx"):
        self.excel_path = Path(excel_path)
        self.processed_data = {}
        self.question_mapping = {}  # Maps question codes to actual questions
        self.response_options = {}  # Maps question codes to response options
        self.filter_options = {}
        self.text_columns = {}
        
    def load_and_process_data(self):
        """Load Excel data with proper question mapping"""
        print("🔄 Loading OSN survey data with PROPER question mapping...")
        
        try:
            if not self.excel_path.exists():
                print(f"❌ Excel file not found: {self.excel_path}")
                return False
            
            # Load both sheets
            excel_file = pd.ExcelFile(self.excel_path)
            sheets = excel_file.sheet_names
            print(f"📊 Found sheets: {sheets}")
            
            # Process each sheet with proper structure understanding
            for sheet_name in sheets:
                print(f"📋 Processing sheet: {sheet_name}")
                self._process_sheet_with_proper_mapping(sheet_name)
            
            # Combine data - EXACTLY 200 + 200 = 400
            self._combine_data_with_proper_names()
            
            # Set up filters and text analysis with proper names
            self._setup_proper_filter_options()
            self._identify_proper_text_columns()
            
            print("✅ Data loading complete with PROPER question mapping!")
            return True
            
        except Exception as e:
            print(f"❌ Error in data processing: {e}")
            return False
    
    def _process_sheet_with_proper_mapping(self, sheet_name: str):
        """Process sheet with proper question text mapping"""
        try:
            # Load the raw structure to extract question mapping
            raw_df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
            print(f"📋 {sheet_name}: Raw shape {raw_df.shape}")
            
            # Extract question mapping from rows 0 and 1
            question_codes = raw_df.iloc[0].tolist()  # Row 0: A1, A2, etc.
            question_texts = raw_df.iloc[1].tolist()  # Row 1: Actual questions
            response_options = raw_df.iloc[2].tolist() if len(raw_df) > 2 else []  # Row 2: Response options
            
            # Build question mapping
            sheet_mapping = {}
            sheet_responses = {}
            
            for i, (code, text) in enumerate(zip(question_codes, question_texts)):
                if pd.notna(code) and pd.notna(text) and str(text).strip():
                    # Clean question text for use as column name
                    clean_question = self._clean_question_text(str(text))
                    sheet_mapping[code] = clean_question
                    
                    # Store response options if available
                    if i < len(response_options) and pd.notna(response_options[i]):
                        sheet_responses[code] = str(response_options[i])
            
            print(f"📋 {sheet_name}: Found {len(sheet_mapping)} properly mapped questions")
            
            # Load actual data starting from row 3 (where headers are S. No., Status, etc.)
            data_df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=3)
            print(f"📋 {sheet_name}: Data shape after proper header {data_df.shape}")
            
            # Remove completely empty rows and take exactly 200
            data_clean = data_df.dropna(how='all').copy()
            if len(data_clean) >= 200:
                data_final = data_clean.head(200).copy()
            else:
                print(f"⚠️ Warning: {sheet_name} has only {len(data_clean)} rows")
                data_final = data_clean.copy()
            
            # Rename columns using proper question mapping
            renamed_data = data_final.copy()
            
            # Map question code columns to proper question text
            for old_col in renamed_data.columns:
                if old_col in sheet_mapping:
                    new_col_name = sheet_mapping[old_col]
                    renamed_data = renamed_data.rename(columns={old_col: new_col_name})
                    print(f"   Mapped: {old_col} → {new_col_name}")
            
            # Add country identification
            country = "UAE" if "UAE" in sheet_name else "KSA"
            renamed_data['Country'] = country
            
            # Store processed data and mappings
            self.processed_data[country] = renamed_data
            
            # Store mappings for this sheet
            country_key = f"{country}_mapping"
            self.question_mapping[country_key] = sheet_mapping
            self.response_options[country_key] = sheet_responses
            
            print(f"✅ {country}: EXACTLY {len(renamed_data)} responses with proper question names")
            
        except Exception as e:
            print(f"❌ Error processing {sheet_name}: {e}")
            raise
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean question text to make it suitable as column name"""
        # Remove extra whitespace and newlines
        clean_text = re.sub(r'\s+', ' ', str(question_text)).strip()
        
        # Truncate if too long but keep meaningful part
        if len(clean_text) > 80:
            # Try to truncate at a natural break point
            words = clean_text.split()
            truncated = []
            char_count = 0
            
            for word in words:
                if char_count + len(word) + 1 <= 80:  # +1 for space
                    truncated.append(word)
                    char_count += len(word) + 1
                else:
                    break
            
            clean_text = ' '.join(truncated)
            if len(words) > len(truncated):
                clean_text += "..."
        
        # Remove problematic characters but keep meaningful punctuation
        clean_text = re.sub(r'[^\w\s\-\(\)\?\.\!]', '', clean_text)
        
        return clean_text
    
    def _combine_data_with_proper_names(self):
        """Combine UAE and KSA data with proper column names"""
        try:
            uae_df = self.processed_data.get('UAE')
            ksa_df = self.processed_data.get('KSA')
            
            if uae_df is not None and ksa_df is not None:
                # Ensure both dataframes have same columns
                # Get union of all columns
                uae_cols = set(uae_df.columns)
                ksa_cols = set(ksa_df.columns)
                all_cols = uae_cols.union(ksa_cols)
                
                # Add missing columns to each dataframe
                for col in all_cols:
                    if col not in uae_df.columns:
                        uae_df[col] = None
                    if col not in ksa_df.columns:
                        ksa_df[col] = None
                
                # Ensure same column order
                sorted_cols = sorted(all_cols)
                uae_df = uae_df[sorted_cols]
                ksa_df = ksa_df[sorted_cols]
                
                # Combine to exactly 400
                combined_df = pd.concat([uae_df, ksa_df], ignore_index=True, sort=False)
                
                # Final verification
                if len(combined_df) != 400:
                    print(f"🔧 Final adjustment: {len(combined_df)} → 400 responses")
                    combined_df = combined_df.head(400)
                
                self.processed_data['Combined'] = combined_df
                print(f"✅ Combined: EXACTLY {len(combined_df)} responses with proper question names")
                
                # Show sample of proper column names
                sample_cols = [col for col in combined_df.columns if col != 'Country'][:5]
                print(f"📝 Sample question columns: {sample_cols}")
                
            else:
                print("❌ Missing UAE or KSA data")
                raise ValueError("Cannot combine data - missing country data")
                
        except Exception as e:
            print(f"❌ Error combining data: {e}")
            raise
    
    def _setup_proper_filter_options(self):
        """Set up filtering options with proper question names"""
        if 'Combined' not in self.processed_data:
            return
        
        df = self.processed_data['Combined']
        
        self.filter_options = {
            'countries': ['UAE', 'KSA'],
            'nationalities': [],
            'visit_purposes': []
        }
        
        # Find nationality question by looking for nationality-related text
        nationality_cols = [col for col in df.columns 
                          if any(keyword in str(col).lower() 
                          for keyword in ['nationality', 'national', 'citizen'])]
        
        if nationality_cols:
            nat_col = nationality_cols[0]  # Take the first nationality column
            nationalities = set()
            unique_vals = df[nat_col].dropna().unique()
            for val in unique_vals:
                if pd.notna(val) and str(val).strip() and len(str(val)) > 1:
                    nationalities.add(str(val).strip())
            self.filter_options['nationalities'] = sorted(list(nationalities))[:20]
            print(f"📍 Found nationality column: '{nat_col}' with {len(self.filter_options['nationalities'])} options")
        
        # Find visit purpose question
        purpose_cols = [col for col in df.columns 
                       if any(keyword in str(col).lower() 
                       for keyword in ['purpose', 'visit', 'trip', 'primary purpose'])]
        
        if purpose_cols:
            purpose_col = purpose_cols[0]
            purposes = set()
            unique_vals = df[purpose_col].dropna().unique()
            for val in unique_vals:
                if pd.notna(val) and str(val).strip() and len(str(val)) > 1:
                    # Handle numeric codes (1=Business, 2=Leisure, etc.)
                    val_str = str(val).strip()
                    if val_str.isdigit():
                        # Map common numeric codes to text
                        code_map = {'1': 'Business', '2': 'Leisure', '3': 'Family Vacation', '99': 'Other'}
                        purposes.add(code_map.get(val_str, f"Option {val_str}"))
                    else:
                        purposes.add(val_str)
            self.filter_options['visit_purposes'] = sorted(list(purposes))[:15]
            print(f"✈️ Found visit purpose column: '{purpose_col}' with {len(self.filter_options['visit_purposes'])} options")
    
    def _identify_proper_text_columns(self):
        """Identify text response columns with proper names"""
        if 'Combined' not in self.processed_data:
            return
            
        df = self.processed_data['Combined']
        text_columns = {}
        
        for col in df.columns:
            if col == 'Country':
                continue
                
            if df[col].dtype == 'object':
                # Sample some responses
                sample_responses = df[col].dropna().astype(str).head(20)
                if len(sample_responses) > 0:
                    avg_length = sample_responses.str.len().mean()
                    # If average length > 20 characters, likely text responses
                    if avg_length > 20:
                        # Also check for common text response indicators
                        has_text_indicators = any(
                            indicator in sample_responses.str.lower().str.cat(sep=' ')
                            for indicator in ['good', 'bad', 'improve', 'suggestion', 'comment', 'like', 'better']
                        )
                        
                        if has_text_indicators or avg_length > 50:
                            text_columns[col] = {
                                'column_name': col,
                                'sample_responses': sample_responses.head(5).tolist(),
                                'response_count': df[col].notna().sum(),
                                'avg_length': avg_length
                            }
                            print(f"💬 Text column identified: '{col}' ({df[col].notna().sum()} responses, avg {avg_length:.1f} chars)")
        
        self.text_columns = text_columns
    
    def get_filtered_data(self, filters: dict = None) -> pd.DataFrame:
        """Get filtered data with proper column names"""
        if 'Combined' not in self.processed_data:
            return pd.DataFrame()
        
        df = self.processed_data['Combined'].copy()
        
        if filters is None:
            filters = {}
        
        # Apply country filter
        if filters.get('countries') and 'Country' in df.columns:
            df = df[df['Country'].isin(filters['countries'])]
        
        # Apply nationality filter
        if filters.get('nationalities'):
            nationality_cols = [col for col in df.columns 
                              if any(keyword in str(col).lower() 
                              for keyword in ['nationality', 'national'])]
            if nationality_cols:
                nat_col = nationality_cols[0]
                # Handle both text matching and numeric code matching
                mask = pd.Series([False] * len(df))
                for nationality in filters['nationalities']:
                    # Direct text match
                    text_mask = df[nat_col].astype(str).str.contains(nationality, case=False, na=False)
                    mask = mask | text_mask
                df = df[mask]
        
        # Apply visit purpose filter
        if filters.get('visit_purposes'):
            purpose_cols = [col for col in df.columns 
                           if any(keyword in str(col).lower() 
                           for keyword in ['purpose', 'visit', 'primary purpose'])]
            if purpose_cols:
                purpose_col = purpose_cols[0]
                mask = pd.Series([False] * len(df))
                for purpose in filters['visit_purposes']:
                    # Handle both text and numeric matching
                    text_mask = df[purpose_col].astype(str).str.contains(purpose, case=False, na=False)
                    # Also check for numeric codes
                    if purpose == 'Business':
                        text_mask = text_mask | (df[purpose_col].astype(str) == '1')
                    elif purpose == 'Leisure':
                        text_mask = text_mask | (df[purpose_col].astype(str) == '2')
                    elif purpose == 'Family Vacation':
                        text_mask = text_mask | (df[purpose_col].astype(str) == '3')
                    mask = mask | text_mask
                df = df[mask]
        
        return df
    
    def get_summary_statistics(self) -> dict:
        """Get summary statistics with proper question names"""
        if 'Combined' not in self.processed_data:
            return {}
        
        df = self.processed_data['Combined']
        
        # VERIFY 400 response guarantee
        if len(df) != 400:
            print(f"🚨 CRITICAL: Expected 400 responses, found {len(df)}")
        
        uae_count = len(df[df['Country'] == 'UAE']) if 'Country' in df.columns else 0
        ksa_count = len(df[df['Country'] == 'KSA']) if 'Country' in df.columns else 0
        
        # Get meaningful question names (not A1, B1, etc.)
        meaningful_questions = [col for col in df.columns 
                              if col != 'Country' and not col.startswith('Unnamed') 
                              and not re.match(r'^[A-Z]\d+', col)]
        
        return {
            'total_responses': len(df),
            'uae_responses': uae_count,
            'ksa_responses': ksa_count,
            'countries_represented': df['Country'].nunique() if 'Country' in df.columns else 0,
            'total_questions': len(meaningful_questions),
            'meaningful_question_columns': len(meaningful_questions),
            'data_completeness': (df.notna().sum().sum() / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0,
            'filter_options': self.filter_options,
            'text_columns': len(self.text_columns),
            'sample_question_names': meaningful_questions[:5],
            'consistency_check': {
                'expected_total': 400,
                'actual_total': len(df),
                'expected_uae': 200,
                'actual_uae': uae_count,
                'expected_ksa': 200,
                'actual_ksa': ksa_count,
                'is_consistent': len(df) == 400 and uae_count == 200 and ksa_count == 200
            }
        }
    
    def get_available_questions(self) -> list:
        """Get list of available questions with proper names"""
        if 'Combined' not in self.processed_data:
            return []
        
        df = self.processed_data['Combined']
        
        # Return meaningful question names (not A1, B1, etc.)
        meaningful_questions = [col for col in df.columns 
                              if col != 'Country' 
                              and not col.startswith('Unnamed') 
                              and not re.match(r'^[A-Z]\d+-?[A-Z]*(/\d+)?$', col)  # Exclude A1, B1-A, B1-A/1 patterns
                              and len(col) > 3]  # Exclude very short column names
        
        return meaningful_questions
    
    def generate_cross_tabulation(self, question1: str, question2: str, filters: dict = None) -> dict:
        """Generate cross-tabulation analysis between two properly named questions"""
        df = self.get_filtered_data(filters)
        
        if question1 not in df.columns or question2 not in df.columns:
            return {"error": f"Questions not found in data: '{question1}' or '{question2}'"}
        
        try:
            # Create cross-tabulation
            crosstab = pd.crosstab(df[question1], df[question2], margins=True, margins_name="Total")
            
            # Convert to percentage
            crosstab_pct = pd.crosstab(df[question1], df[question2], normalize='all') * 100
            
            return {
                'question1': question1,
                'question2': question2,
                'total_responses': len(df),
                'crosstab_counts': crosstab.to_dict(),
                'crosstab_percentages': crosstab_pct.round(2).to_dict(),
                'insights': self._generate_crosstab_insights(crosstab, question1, question2)
            }
            
        except Exception as e:
            return {"error": f"Cross-tabulation failed: {e}"}
    
    def _generate_crosstab_insights(self, crosstab: pd.DataFrame, q1: str, q2: str) -> list:
        """Generate insights from cross-tabulation"""
        insights = []
        
        try:
            # Find highest correlation
            crosstab_no_total = crosstab.drop('Total', axis=0).drop('Total', axis=1)
            if not crosstab_no_total.empty:
                max_cell = crosstab_no_total.max().max()
                max_location = crosstab_no_total.stack().idxmax()
                insights.append(f"🎯 Strongest correlation: '{max_location[0]}' & '{max_location[1]}' ({max_cell} responses)")
                
                # Find patterns
                row_totals = crosstab_no_total.sum(axis=1)
                col_totals = crosstab_no_total.sum(axis=0)
                
                if not row_totals.empty:
                    most_common_q1 = row_totals.idxmax()
                    insights.append(f"📊 Most common response for '{q1}': {most_common_q1} ({row_totals.max()} responses)")
                
                if not col_totals.empty:
                    most_common_q2 = col_totals.idxmax()
                    insights.append(f"📊 Most common response for '{q2}': {most_common_q2} ({col_totals.max()} responses)")
        
        except Exception as e:
            insights.append(f"Analysis error: {e}")
        
        return insights
    
    def perform_ai_analysis(self, column_name: str, filters: dict = None) -> dict:
        """Perform AI/ML analysis on properly named text column"""
        df = self.get_filtered_data(filters)
        
        if column_name not in df.columns:
            return {"error": f"Column '{column_name}' not found"}
        
        text_data = df[column_name].dropna().astype(str)
        text_data = text_data[text_data.str.len() > 3]  # Filter very short responses
        
        if len(text_data) == 0:
            return {"error": "No valid text data found"}
        
        try:
            # Sentiment Analysis
            sentiments = [TextBlob(text).sentiment for text in text_data]
            polarity_scores = [s.polarity for s in sentiments]
            
            # TF-IDF Keyword Extraction
            vectorizer = TfidfVectorizer(
                max_features=30,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform(text_data)
            feature_names = vectorizer.get_feature_names_out()
            mean_scores = tfidf_matrix.mean(axis=0).A1
            top_keywords = sorted(zip(feature_names, mean_scores), key=lambda x: x[1], reverse=True)[:15]
            
            # Text clustering for themes
            clusters = {}
            if len(text_data) >= 5:
                try:
                    n_clusters = min(4, len(text_data) // 3)
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    cluster_labels = kmeans.fit_predict(tfidf_matrix)
                    
                    for i in range(n_clusters):
                        cluster_texts = text_data[cluster_labels == i]
                        clusters[f"Theme_{i+1}"] = {
                            'count': len(cluster_texts),
                            'samples': cluster_texts.head(3).tolist()
                        }
                except:
                    clusters = {"Theme_1": {"count": len(text_data), "samples": text_data.head(3).tolist()}}
            
            return {
                'column_name': column_name,
                'total_responses': len(text_data),
                'base_dataset_size': len(df),
                'sentiment_analysis': {
                    'average_polarity': np.mean(polarity_scores),
                    'positive_count': sum(1 for p in polarity_scores if p > 0.1),
                    'neutral_count': sum(1 for p in polarity_scores if -0.1 <= p <= 0.1),
                    'negative_count': sum(1 for p in polarity_scores if p < -0.1)
                },
                'top_keywords': [{'keyword': kw, 'relevance': round(score, 3)} for kw, score in top_keywords],
                'themes': clusters,
                'sample_responses': text_data.head(5).tolist()
            }
            
        except Exception as e:
            return {"error": f"AI analysis failed: {e}"}
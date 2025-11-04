#!/usr/bin/env python3
"""
ENHANCED OSN Survey Data Processor with Better Question Names and Word Cloud Support
✅ ALL nationalities included
✅ Proper question names (no more 'Unnamed')  
✅ Word cloud ready text analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import re

warnings.filterwarnings('ignore')

class EnhancedOSNProcessor:
    """
    Enhanced processor with better question handling and text analysis support
    """
    
    def __init__(self, excel_path: str = "data/survey_data.xlsx"):
        self.excel_path = Path(excel_path)
        self.data = None
        self.questions = {}
        self.filters = {}
        self.question_mapping = {}  # Maps codes to actual questions
        self.response_options = {}  # Maps question codes to their response options
        self.text_questions = []    # Questions suitable for word cloud analysis
        
    def load_data(self):
        """Load data with enhanced question mapping and text analysis support"""
        print("🔄 Loading survey data (ENHANCED - Better Questions + Word Cloud Support)...")
        
        try:
            # Step 1: Load the complete question mapping from Excel headers
            self._load_question_mapping()
            
            # Step 2: Load exactly 200 from each sheet
            uae_df = self._load_sheet("Guests (UAE)")
            ksa_df = self._load_sheet("Guests Online (KSA)")
            
            if uae_df is None or ksa_df is None:
                return False
            
            # Step 3: Add country and combine to exactly 400
            uae_df = uae_df.copy()
            ksa_df = ksa_df.copy()
            uae_df['Country'] = 'UAE'
            ksa_df['Country'] = 'KSA'
            
            self.data = pd.concat([uae_df, ksa_df], ignore_index=True)
            
            # Step 4: GUARANTEE exactly 400 responses
            if len(self.data) != 400:
                print(f"⚠️ Adjusting from {len(self.data)} to 400 responses")
                self.data = self.data.head(400)
            
            # Step 5: Apply enhanced column mapping with proper question names
            self._apply_enhanced_mapping()
            
            # Step 6: Clean data VALUES without losing responses
            self._clean_values_preserve_count()
            
            # Step 7: Identify text-based questions for word cloud analysis
            self._identify_text_questions()
            
            # Step 8: Setup filters
            self._setup_enhanced_filters()
            
            print(f"✅ ENHANCED: Successfully loaded exactly {len(self.data)} responses")
            print(f"   UAE: {len(self.data[self.data['Country'] == 'UAE'])}")
            print(f"   KSA: {len(self.data[self.data['Country'] == 'KSA'])}")
            print(f"   Text Analysis Questions: {len(self.text_questions)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _load_question_mapping(self):
        """Load question codes, actual question text, and response options from Excel headers"""
        try:
            # Load the header rows to build mapping
            df_codes = pd.read_excel(self.excel_path, sheet_name="Guests (UAE)", header=None, nrows=1, skiprows=0)
            df_questions = pd.read_excel(self.excel_path, sheet_name="Guests (UAE)", header=None, nrows=1, skiprows=1)
            df_options = pd.read_excel(self.excel_path, sheet_name="Guests (UAE)", header=None, nrows=1, skiprows=2)
            
            # Build mapping from question codes to actual questions and response options
            for col_idx in range(len(df_codes.columns)):
                code = df_codes.iloc[0, col_idx]
                question = df_questions.iloc[0, col_idx]
                options = df_options.iloc[0, col_idx]
                
                # Process question mapping
                if not pd.isna(question) and str(question).strip() and 'Unnamed' not in str(question):
                    clean_question = str(question).strip()
                    if len(clean_question) > 5:  # Only meaningful questions
                        self.question_mapping[str(code)] = clean_question
                
                # Process response options
                if not pd.isna(options) and str(options).strip() and str(options) != 'Response':
                    options_text = str(options).strip()
                    # Parse formatted options like "1. Business\n2. Leisure\n3. Family Vacation\n99. Other"
                    if '\n' in options_text and any(char.isdigit() for char in options_text):
                        parsed_options = self._parse_response_options(options_text)
                        if parsed_options:
                            self.response_options[str(code)] = parsed_options
            
            print(f"📋 Loaded {len(self.question_mapping)} question mappings")
            print(f"📝 Loaded {len(self.response_options)} response option sets")
            
        except Exception as e:
            print(f"⚠️ Could not load question mapping: {e}")
            self.question_mapping = {}
            self.response_options = {}
    
    def _load_sheet(self, sheet_name: str):
        """Load exactly 200 responses from sheet"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=3)
            df_clean = df.dropna(how='all')
            result = df_clean.head(200).copy() if len(df_clean) >= 200 else df_clean.copy()
            print(f"📋 {sheet_name}: {len(result)} responses loaded")
            return result
        except Exception as e:
            print(f"❌ Error loading {sheet_name}: {e}")
            return None
    
    def _apply_enhanced_mapping(self):
        """Apply enhanced column mapping using actual question text"""
        if self.data is None:
            return
        
        # Enhanced column mapping with proper question names
        enhanced_mapping = {
            'A1': 'Nationality',
            'A2': 'Visit Purpose',
            'A2-A': 'Visit Purpose (Other)',
            'A3': 'Hotel Stays Per Year',
            'B1-A/1': 'Hotel Choice Reason 1',
            'B1-A/2': 'Hotel Choice Reason 2', 
            'B1-A/3': 'Hotel Choice Reason 3',
            'B1-B': 'Entertainment Priority with Family',
            'B2-A': 'Entertainment Importance Rating',
            'B2-B': 'Entertainment Experience Story',
            'C1': 'Used In-Room Entertainment',
            'C2-B': 'Content Accessibility',
            'C4-A': 'Entertainment Quality Rating',
            'C4-B': 'Entertainment Improvement Suggestions',
            'D2': 'Streaming Account Preference',
            'D3': 'Willingness to Pay for Enhancement',
            'D4': 'Acceptable Price Range',
            'D5': 'General Entertainment Suggestions'
        }
        
        # Apply mapping while keeping original columns that don't map
        renamed_data = {}
        
        for col in self.data.columns:
            if col in enhanced_mapping:
                renamed_data[enhanced_mapping[col]] = self.data[col]
            elif col == 'Country':
                renamed_data[col] = self.data[col]
            elif col in self.question_mapping:
                # Use the actual question text from Excel headers
                question_text = self.question_mapping[col]
                # Truncate very long questions for better UI
                if len(question_text) > 60:
                    question_text = question_text[:57] + "..."
                renamed_data[question_text] = self.data[col]
            elif not ('Unnamed' in str(col) or 'Status' in str(col) or 'Respondent' in str(col) or 'S. No.' in str(col)):
                # Keep other meaningful columns with cleaned names
                clean_name = str(col).strip()
                if clean_name and len(clean_name) > 1:
                    renamed_data[clean_name] = self.data[col]
        
        self.data = pd.DataFrame(renamed_data)
        print(f"📝 ENHANCED: Mapped to {len(self.data.columns)} columns (no more 'Unnamed')")
        print(f"📋 Available questions: {[col for col in self.data.columns if col != 'Country'][:5]}...")
    
    def _parse_response_options(self, options_text):
        """Parse response options from formatted text like '1. Business\n2. Leisure\n3. Family Vacation\n99. Other'"""
        try:
            lines = options_text.split('\n')
            options = []
            
            for line in lines:
                line = line.strip()
                if line and '.' in line:
                    # Extract the text after the number and dot
                    parts = line.split('.', 1)
                    if len(parts) == 2:
                        option_text = parts[1].strip()
                        if option_text:
                            options.append(option_text)
            
            return options if len(options) > 1 else None  # Only return if we have multiple options
            
        except Exception as e:
            print(f"⚠️ Error parsing options '{options_text}': {e}")
            return None
    
    def _identify_text_questions(self):
        """Identify questions suitable for word cloud analysis (text/opinion based)"""
        text_indicators = [
            'story', 'experience', 'suggest', 'comment', 'opinion', 'feedback', 
            'improvement', 'other', 'specify', 'describe', 'explain', 'what',
            'how', 'why', 'Entertainment Experience Story', 'Entertainment Improvement Suggestions',
            'General Entertainment Suggestions', 'Visit Purpose (Other)'
        ]
        
        self.text_questions = []
        
        for col in self.data.columns:
            if col == 'Country':
                continue
                
            col_lower = str(col).lower()
            
            # Check if column name contains text indicators
            if any(indicator in col_lower for indicator in text_indicators):
                # Additional check: see if the column actually contains text data
                sample_data = self.data[col].dropna().head(10)
                if len(sample_data) > 0:
                    # Check if responses are mostly text (not just numbers)
                    text_responses = 0
                    for response in sample_data:
                        response_str = str(response).strip()
                        if len(response_str) > 5 and not response_str.replace('.','').isdigit():
                            text_responses += 1
                    
                    if text_responses > len(sample_data) * 0.3:  # At least 30% text responses
                        self.text_questions.append(col)
        
        print(f"🔤 Identified {len(self.text_questions)} text analysis questions:")
        for q in self.text_questions:
            print(f"   - {q}")
    
    def _clean_values_preserve_count(self):
        """Clean data values while preserving ALL 400 responses"""
        
        # Clean nationality - normalize but don't filter out
        if 'Nationality' in self.data.columns:
            print("🧹 Normalizing nationality data (keeping all responses)...")
            
            def normalize_nationality(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                val_str = str(value).strip()
                
                # Comprehensive normalizations to fix duplicates
                normalizations = {
                    'India': 'Indian',
                    'UAE': 'Emirati', 
                    'UAE ': 'Emirati',
                    'Emiratis': 'Emirati',
                    'Saudi Arabia': 'Saudi Arabian',
                    'Saudi Arabia ': 'Saudi Arabian', 
                    'SaudiArabian': 'Saudi Arabian',
                    'Saudi\\xa0Arabian': 'Saudi Arabian',
                    'Egypt ': 'Egyptian',
                    'Egypt': 'Egyptian',
                    'Egyptian.': 'Egyptian',
                    'Biritish': 'British',
                    'Pakistan': 'Pakistani',
                    'Pakistani\\xa0': 'Pakistani',
                    'Philippines': 'Filipino',
                    'Filipano': 'Filipino',
                    'Australia ': 'Australian',
                    'Australia': 'Australian',
                    'Austrailian': 'Australian',
                    'USA ': 'American',
                    'USA': 'American',
                    'Germany': 'German',
                    'Jordan': 'Jordanian',
                    'Lebanon': 'Lebanese',
                    'Kuwait': 'Kuwaiti',
                    'Kuwati': 'Kuwaiti',
                    'Bahrain': 'Bahraini',
                    'Croatia': 'Croatian',
                    'Palestine': 'Palestinian',
                    'Ethiopia': 'Ethiopian'
                }
                
                return normalizations.get(val_str, val_str)
            
            self.data['Nationality'] = self.data['Nationality'].apply(normalize_nationality)
        
        # Convert visit purpose codes to meaningful text
        if 'Visit Purpose' in self.data.columns:
            print("🧹 Converting visit purpose codes...")
            
            def convert_visit_purpose(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                val_str = str(value).strip()
                
                if val_str in ['1', '1.0']:
                    return 'Business'
                elif val_str in ['2', '2.0']:
                    return 'Leisure'
                elif val_str in ['3', '3.0']:
                    return 'Family Vacation'
                elif val_str in ['99', '99.0']:
                    return 'Other'
                else:
                    # Keep original value if it's already text
                    return val_str if val_str else 'Not Specified'
            
            self.data['Visit Purpose'] = self.data['Visit Purpose'].apply(convert_visit_purpose)
        
        # Convert hotel frequency codes
        if 'Hotel Stays Per Year' in self.data.columns:
            print("🧹 Converting hotel frequency codes...")
            
            def convert_hotel_frequency(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                val_str = str(value).strip()
                
                if val_str in ['1', '1.0']:
                    return '1-2 times'
                elif val_str in ['2', '2.0']:
                    return '3-5 times'
                elif val_str in ['3', '3.0']:
                    return 'More than 5 times'
                else:
                    return val_str if val_str else 'Not Specified'
            
            self.data['Hotel Stays Per Year'] = self.data['Hotel Stays Per Year'].apply(convert_hotel_frequency)
        
        # Convert hotel choice reason codes to meaningful text
        hotel_choice_columns = [col for col in self.data.columns if 'Hotel Choice Reason' in col]
        if hotel_choice_columns:
            print("🧹 Converting hotel choice reason codes...")
            
            def convert_hotel_choice_reason(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                val_str = str(value).strip()
                
                # Map based on B1-A response options from Excel
                choice_mapping = {
                    '1': 'Location',
                    '1.0': 'Location',
                    '2': 'Price', 
                    '2.0': 'Price',
                    '3': 'Brand Reputation',
                    '3.0': 'Brand Reputation',
                    '4': 'Amenities (gym, pool, etc.)',
                    '4.0': 'Amenities (gym, pool, etc.)',
                    '5': 'In-room Entertainment',
                    '5.0': 'In-room Entertainment',
                    '6': 'Family-friendly Features',
                    '6.0': 'Family-friendly Features',
                    '7': 'Guest Reviews',
                    '7.0': 'Guest Reviews',
                    '99': 'Other',
                    '99.0': 'Other'
                }
                
                return choice_mapping.get(val_str, val_str if val_str else 'Not Specified')
            
            for col in hotel_choice_columns:
                self.data[col] = self.data[col].apply(convert_hotel_choice_reason)
        
        print(f"✅ ENHANCED: Data cleaned, still have exactly {len(self.data)} responses")
    
    def _setup_enhanced_filters(self):
        """Setup enhanced filter options with ALL nationalities"""
        if self.data is None:
            return
        
        self.filters = {
            'countries': ['UAE', 'KSA'],
            'nationalities': [],
            'visit_purposes': [],
            'hotel_frequency': [],
            'entertainment_ratings': [],
            'text_questions': self.text_questions
        }
        
        # Get ALL nationality options (user specifically requested all nationalities)
        if 'Nationality' in self.data.columns:
            nationalities = self.data['Nationality'].value_counts()
            # Include ALL nationalities except 'Not Specified'
            self.filters['nationalities'] = sorted([nat for nat in nationalities.index 
                                                  if nat != 'Not Specified' and pd.notna(nat)])
        
        # Get visit purpose options
        if 'Visit Purpose' in self.data.columns:
            purposes = self.data['Visit Purpose'].dropna().unique()
            self.filters['visit_purposes'] = sorted([p for p in purposes if p != 'Not Specified'])
        
        # Get hotel frequency options
        if 'Hotel Stays Per Year' in self.data.columns:
            frequencies = self.data['Hotel Stays Per Year'].dropna().unique()
            self.filters['hotel_frequency'] = sorted([f for f in frequencies if f != 'Not Specified'])
        
        # Get entertainment ratings
        if 'Entertainment Quality Rating' in self.data.columns:
            ratings = self.data['Entertainment Quality Rating'].dropna().unique()
            self.filters['entertainment_ratings'] = sorted([int(r) for r in ratings if not pd.isna(r)])
        
        print(f"🎯 ENHANCED Filter options:")
        print(f"   Nationalities ({len(self.filters['nationalities'])}): ALL INCLUDED")
        print(f"   Visit Purposes: {self.filters['visit_purposes']}")
        print(f"   Hotel Frequency: {self.filters['hotel_frequency']}")
        print(f"   Text Analysis Questions: {len(self.filters['text_questions'])}")
    
    def get_filtered_data(self, country_filter=None, nationality_filter=None, purpose_filter=None, frequency_filter=None):
        """Get filtered data"""
        if self.data is None:
            return pd.DataFrame()
        
        df = self.data.copy()
        
        if country_filter:
            df = df[df['Country'].isin(country_filter)]
        
        if nationality_filter and 'Nationality' in df.columns:
            df = df[df['Nationality'].isin(nationality_filter)]
        
        if purpose_filter and 'Visit Purpose' in df.columns:
            df = df[df['Visit Purpose'].isin(purpose_filter)]
        
        if frequency_filter and 'Hotel Stays Per Year' in df.columns:
            df = df[df['Hotel Stays Per Year'].isin(frequency_filter)]
        
        return df
    
    def get_summary_stats(self):
        """Get summary statistics"""
        if self.data is None:
            return {}
        
        # Get meaningful question names (exclude metadata columns)
        meaningful_questions = [col for col in self.data.columns 
                              if col not in ['Country', 'S. No.'] and 'Unnamed' not in str(col)]
        
        return {
            'total_responses': len(self.data),
            'uae_responses': len(self.data[self.data['Country'] == 'UAE']),
            'ksa_responses': len(self.data[self.data['Country'] == 'KSA']),
            'total_questions': len(meaningful_questions),
            'available_questions': meaningful_questions,
            'text_questions': self.text_questions,
            'filter_options': self.filters,
            'response_options': self.response_options
        }
    
    def get_text_responses_for_wordcloud(self, question, filters=None):
        """Get text responses for word cloud analysis"""
        if question not in self.text_questions:
            return []
        
        if filters:
            df = self.get_filtered_data(
                country_filter=filters.get('countries'),
                nationality_filter=filters.get('nationalities'),
                purpose_filter=filters.get('purposes'),
                frequency_filter=filters.get('frequency')
            )
        else:
            df = self.data
        
        if question not in df.columns:
            return []
        
        # Get non-null text responses
        responses = df[question].dropna().astype(str)
        
        # Filter out very short responses and numbers-only responses
        text_responses = []
        for response in responses:
            response_clean = response.strip()
            if len(response_clean) > 3 and not response_clean.replace('.','').replace('-','').isdigit():
                text_responses.append(response_clean)
        
        return text_responses
    
    def get_cross_tabulation(self, question1, question2, filters=None):
        """Cross-tabulation analysis"""
        if filters:
            df = self.get_filtered_data(
                country_filter=filters.get('countries'),
                nationality_filter=filters.get('nationalities'),
                purpose_filter=filters.get('purposes'),
                frequency_filter=filters.get('frequency')
            )
        else:
            df = self.data
        
        if question1 not in df.columns or question2 not in df.columns:
            return None
        
        try:
            crosstab = pd.crosstab(df[question1], df[question2])
            
            combinations = []
            for idx in crosstab.index:
                for col in crosstab.columns:
                    count = crosstab.loc[idx, col]
                    if count > 0:
                        combinations.append({
                            'question1_value': str(idx),
                            'question2_value': str(col), 
                            'count': int(count),
                            'percentage': round((count / len(df)) * 100, 1)
                        })
            
            combinations.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'total_responses': len(df),
                'question1': question1,
                'question2': question2,
                'combinations': combinations[:10]
            }
            
        except Exception as e:
            print(f"Cross-tabulation error: {e}")
            return None
    
    def generate_insights(self, filtered_data, analysis_type="overview"):
        """Generate business insights with OSN focus"""
        if filtered_data is None or len(filtered_data) == 0:
            return "No data available for analysis."
        
        insights = []
        
        # Core market insights
        insights.append(f"📊 **Market Analysis**: {len(filtered_data)} guest responses analyzed")
        
        if 'Nationality' in filtered_data.columns:
            top_nationality = filtered_data['Nationality'].value_counts().index[0]
            nat_percentage = (filtered_data['Nationality'].value_counts().iloc[0] / len(filtered_data)) * 100
            insights.append(f"🌍 **Key Market**: {top_nationality} guests represent {nat_percentage:.1f}% of analyzed responses")
        
        if 'Visit Purpose' in filtered_data.columns:
            top_purpose = filtered_data['Visit Purpose'].value_counts().index[0]
            purpose_percentage = (filtered_data['Visit Purpose'].value_counts().iloc[0] / len(filtered_data)) * 100
            insights.append(f"✈️ **Primary Visit Purpose**: {top_purpose} dominates at {purpose_percentage:.1f}%")
        
        if 'Entertainment Quality Rating' in filtered_data.columns:
            avg_rating = filtered_data['Entertainment Quality Rating'].mean()
            insights.append(f"⭐ **Entertainment Satisfaction**: Average rating {avg_rating:.1f}/5 - {'Excellent' if avg_rating >= 4.5 else 'Good' if avg_rating >= 4 else 'Needs Improvement'}")
        
        # OSN-specific strategic insights
        insights.append("💼 **OSN Strategic Implications**:")
        insights.append("   • Focus entertainment content development on identified top guest segments")
        insights.append("   • Tailor streaming services to match primary visit purposes and cultural preferences")  
        insights.append("   • Leverage guest satisfaction data to enhance competitive positioning")
        
        return "\n\n".join(insights)
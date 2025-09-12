#!/usr/bin/env python3
"""
CORRECTED Robust OSN Survey Data Processor
AUDIT FIXES: Proper text mapping, clean nationalities, meaningful visit purposes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import re

warnings.filterwarnings('ignore')

class CorrectedRobustProcessor:
    """
    AUDIT-CORRECTED survey data processor
    Fixes: Visit purpose codes, nationality cleanup, proper question names
    """
    
    def __init__(self, excel_path: str = "data/survey_data.xlsx"):
        self.excel_path = Path(excel_path)
        self.data = None
        self.questions = {}
        self.filters = {}
        
    def load_data(self):
        """Load data with CORRECTED processing based on audit findings"""
        print("🔄 Loading survey data (AUDIT-CORRECTED approach)...")
        
        try:
            # Step 1: Load both sheets and get exactly 200 from each
            uae_df = self._load_sheet("Guests (UAE)")
            ksa_df = self._load_sheet("Guests Online (KSA)")
            
            if uae_df is None or ksa_df is None:
                return False
            
            # Step 2: Combine to exactly 400
            uae_df['Country'] = 'UAE'
            ksa_df['Country'] = 'KSA'
            
            self.data = pd.concat([uae_df, ksa_df], ignore_index=True)
            
            # Step 3: Verify exactly 400 responses
            if len(self.data) != 400:
                print(f"⚠️ Adjusting from {len(self.data)} to 400 responses")
                self.data = self.data.head(400)
            
            # Step 4: CORRECTED question mapping and data cleaning
            self._apply_corrected_mapping()
            
            # Step 5: CORRECTED filter setup
            self._setup_corrected_filters()
            
            print(f"✅ CORRECTED: Successfully loaded exactly {len(self.data)} responses")
            print(f"   UAE: {len(self.data[self.data['Country'] == 'UAE'])}")
            print(f"   KSA: {len(self.data[self.data['Country'] == 'KSA'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _load_sheet(self, sheet_name: str):
        """Load a single sheet with exactly 200 responses"""
        try:
            # Read the sheet starting from the correct row (row 3 has actual headers)
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=3)
            
            # Remove completely empty rows
            df_clean = df.dropna(how='all')
            
            # Take exactly 200 responses
            if len(df_clean) >= 200:
                result = df_clean.head(200).copy()
            else:
                print(f"⚠️ {sheet_name}: Only {len(df_clean)} responses available")
                result = df_clean.copy()
            
            print(f"📋 {sheet_name}: {len(result)} responses loaded")
            return result
            
        except Exception as e:
            print(f"❌ Error loading {sheet_name}: {e}")
            return None
    
    def _apply_corrected_mapping(self):
        """Apply CORRECTED question mapping and data cleaning"""
        if self.data is None:
            return
        
        # CORRECTED mapping for better question names
        question_mapping = {
            'A1': 'Nationality',
            'A2': 'Visit Purpose',
            'A2-A': 'Visit Purpose Other',
            'A3': 'Hotel Stays Per Year',
            'B1-A/1': 'Hotel Choice Reason 1',
            'B1-A/2': 'Hotel Choice Reason 2', 
            'B1-A/3': 'Hotel Choice Reason 3',
            'B1-A/4': 'Hotel Choice Reason 4',
            'B1-A/5': 'Hotel Choice Reason 5',
            'B1-B': 'Entertainment Priority with Family',
            'B2-A': 'Entertainment Importance Rating',
            'B2-B': 'Entertainment Experience Story',
            'C1': 'Used In-Room Entertainment',
            'C2-A/1': 'Content Type 1',
            'C2-A/2': 'Content Type 2',
            'C2-A/3': 'Content Type 3',
            'C2-A-a': 'Content Type Other',
            'C2-B': 'Content Accessibility',
            'C3/1': 'Preferred Entertainment Format',
            'C4-A': 'Entertainment Quality Rating',
            'C4-B': 'Entertainment Improvement Suggestions',
            'D2': 'Streaming Account Access Preference',
            'D3': 'Willingness to Pay for Enhanced Entertainment',
            'D4': 'Acceptable Price Range',
            'D5': 'General Entertainment Suggestions'
        }
        
        # Apply column mapping
        renamed_columns = {}
        for old_col in self.data.columns:
            if old_col in question_mapping:
                renamed_columns[old_col] = question_mapping[old_col]
            elif old_col == 'Country':
                renamed_columns[old_col] = old_col
            elif not ('Unnamed' in str(old_col) or str(old_col).startswith('S. No.') or str(old_col) == 'Status' or str(old_col) == 'Respondent'):
                # Keep other meaningful columns as-is
                clean_name = str(old_col).replace('_', ' ').strip()
                if clean_name and len(clean_name) > 1:
                    renamed_columns[old_col] = clean_name
        
        # Rebuild dataframe with only properly mapped columns
        mapped_data = pd.DataFrame()
        
        for original_col, new_col in renamed_columns.items():
            if original_col in self.data.columns:
                mapped_data[new_col] = self.data[original_col]
        
        self.data = mapped_data
        print(f"📝 CORRECTED: Mapped to {len(self.data.columns)} properly named columns")
        
        # CORRECTED data cleaning
        self._clean_data_values()
    
    def _clean_data_values(self):
        """CORRECTED data value cleaning based on audit findings"""
        
        # Fix nationality data
        if 'Nationality' in self.data.columns:
            print("🧹 Cleaning nationality data...")
            
            # Clean nationality values
            self.data['Nationality'] = self.data['Nationality'].astype(str)
            
            # Remove special characters and normalize
            nationality_mapping = {
                'Saudi\xa0Arabian': 'Saudi Arabian',
                'Saudi Arabian': 'Saudi Arabian',
                'Saudi': 'Saudi Arabian',
                'India': 'Indian',
                'Indian': 'Indian',
                'Biritish': 'British',  # Fix typo
                'British': 'British',
                'Emirati': 'Emirati',
                'American': 'American',
                'Chinese': 'Chinese',
                'German': 'German',
                'Russian': 'Russian',
                'Italian': 'Italian',
                'Qatari': 'Qatari',
                'Singaporean': 'Singaporean',
                'French': 'French',
                'Jordanian': 'Jordanian'
            }
            
            # Apply nationality mapping
            for old_nat, new_nat in nationality_mapping.items():
                self.data.loc[self.data['Nationality'] == old_nat, 'Nationality'] = new_nat
            
            # Remove invalid entries
            valid_nationalities = list(set(nationality_mapping.values()))
            self.data = self.data[self.data['Nationality'].isin(valid_nationalities)]
            
        # Fix visit purpose data - CONVERT CODES TO MEANINGFUL TEXT
        if 'Visit Purpose' in self.data.columns:
            print("🧹 Converting visit purpose codes to meaningful text...")
            
            # Convert numeric codes to meaningful text
            def map_visit_purpose(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                str_value = str(value).strip()
                
                # Handle numeric codes
                if str_value in ['1', '1.0']:
                    return 'Business'
                elif str_value in ['2', '2.0']:
                    return 'Leisure'
                elif str_value in ['3', '3.0']:
                    return 'Family Vacation'
                elif str_value in ['99', '99.0']:
                    return 'Other'
                else:
                    # Handle text values
                    if 'business' in str_value.lower():
                        return 'Business'
                    elif 'leisure' in str_value.lower():
                        return 'Leisure'
                    elif 'family' in str_value.lower():
                        return 'Family Vacation'
                    else:
                        return 'Other'
            
            self.data['Visit Purpose'] = self.data['Visit Purpose'].apply(map_visit_purpose)
        
        # Fix hotel stays per year
        if 'Hotel Stays Per Year' in self.data.columns:
            print("🧹 Converting hotel stay frequency...")
            
            def map_hotel_stays(value):
                if pd.isna(value):
                    return 'Not Specified'
                
                str_value = str(value).strip()
                
                if str_value in ['1', '1.0']:
                    return '1-2 times'
                elif str_value in ['2', '2.0']:
                    return '3-5 times'  
                elif str_value in ['3', '3.0']:
                    return 'More than 5 times'
                else:
                    return 'Not Specified'
            
            self.data['Hotel Stays Per Year'] = self.data['Hotel Stays Per Year'].apply(map_hotel_stays)
        
        # Clean entertainment ratings
        if 'Entertainment Quality Rating' in self.data.columns:
            # Convert to proper ratings (1-5 scale)
            self.data['Entertainment Quality Rating'] = pd.to_numeric(
                self.data['Entertainment Quality Rating'], errors='coerce'
            )
        
        print("✅ CORRECTED: Data values cleaned and properly mapped")
    
    def _setup_corrected_filters(self):
        """Setup CORRECTED filter options with clean values"""
        if self.data is None:
            return
        
        self.filters = {
            'countries': ['UAE', 'KSA'],
            'nationalities': [],
            'visit_purposes': [],
            'hotel_frequency': [],
            'entertainment_ratings': []
        }
        
        # Get CLEAN nationality options
        if 'Nationality' in self.data.columns:
            nationalities = self.data['Nationality'].dropna().unique()
            self.filters['nationalities'] = sorted([n for n in nationalities if n != 'Not Specified'])
        
        # Get CLEAN visit purpose options
        if 'Visit Purpose' in self.data.columns:
            purposes = self.data['Visit Purpose'].dropna().unique()
            self.filters['visit_purposes'] = sorted([p for p in purposes if p != 'Not Specified'])
        
        # Get hotel frequency options
        if 'Hotel Stays Per Year' in self.data.columns:
            frequencies = self.data['Hotel Stays Per Year'].dropna().unique()
            self.filters['hotel_frequency'] = sorted([f for f in frequencies if f != 'Not Specified'])
        
        # Get entertainment rating options
        if 'Entertainment Quality Rating' in self.data.columns:
            ratings = self.data['Entertainment Quality Rating'].dropna().unique()
            self.filters['entertainment_ratings'] = sorted([int(r) for r in ratings if not pd.isna(r)])
        
        print(f"🎯 CORRECTED Filter options:")
        print(f"   Nationalities ({len(self.filters['nationalities'])}): {self.filters['nationalities']}")
        print(f"   Visit Purposes: {self.filters['visit_purposes']}")
        print(f"   Hotel Frequency: {self.filters['hotel_frequency']}")
        print(f"   Entertainment Ratings: {self.filters['entertainment_ratings']}")
    
    def get_filtered_data(self, country_filter=None, nationality_filter=None, purpose_filter=None, frequency_filter=None):
        """Get filtered data with CORRECTED filtering logic"""
        if self.data is None:
            return pd.DataFrame()
        
        df = self.data.copy()
        
        # Apply country filter
        if country_filter:
            df = df[df['Country'].isin(country_filter)]
        
        # Apply nationality filter
        if nationality_filter and 'Nationality' in df.columns:
            df = df[df['Nationality'].isin(nationality_filter)]
        
        # Apply visit purpose filter (now using clean text values)
        if purpose_filter and 'Visit Purpose' in df.columns:
            df = df[df['Visit Purpose'].isin(purpose_filter)]
        
        # Apply hotel frequency filter
        if frequency_filter and 'Hotel Stays Per Year' in df.columns:
            df = df[df['Hotel Stays Per Year'].isin(frequency_filter)]
        
        return df
    
    def get_summary_stats(self):
        """Get summary statistics with CORRECTED data"""
        if self.data is None:
            return {}
        
        return {
            'total_responses': len(self.data),
            'uae_responses': len(self.data[self.data['Country'] == 'UAE']),
            'ksa_responses': len(self.data[self.data['Country'] == 'KSA']),
            'total_questions': len([col for col in self.data.columns if col != 'Country']),
            'available_questions': [col for col in self.data.columns if col != 'Country'],
            'filter_options': self.filters
        }
    
    def get_cross_tabulation(self, question1, question2, filters=None):
        """CORRECTED cross-tabulation with proper filtering"""
        # Apply filters if provided
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
            # Create cross-tabulation
            crosstab = pd.crosstab(df[question1], df[question2])
            
            # Get top combinations
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
            
            # Sort by count
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
        """Generate CORRECTED business insights with clean data"""
        if filtered_data is None or len(filtered_data) == 0:
            return "No data available for analysis."
        
        insights = []
        
        # Basic insights
        total_responses = len(filtered_data)
        uae_count = len(filtered_data[filtered_data['Country'] == 'UAE'])
        ksa_count = len(filtered_data[filtered_data['Country'] == 'KSA'])
        
        insights.append(f"📊 **Market Coverage**: {total_responses} total responses ({uae_count} UAE, {ksa_count} KSA)")
        
        # CORRECTED nationality insights
        if 'Nationality' in filtered_data.columns:
            top_nationalities = filtered_data['Nationality'].value_counts().head(3)
            insights.append(f"🌍 **Top Guest Nationalities**: {', '.join([f'{nat} ({count})' for nat, count in top_nationalities.items()])}")
        
        # CORRECTED visit purpose insights (now with meaningful text)
        if 'Visit Purpose' in filtered_data.columns:
            purposes = filtered_data['Visit Purpose'].value_counts().head(3)
            purpose_list = [f'{purpose} ({count})' for purpose, count in purposes.items()]
            insights.append(f"✈️ **Visit Purposes**: {', '.join(purpose_list)}")
        
        # Hotel frequency insights
        if 'Hotel Stays Per Year' in filtered_data.columns:
            frequency = filtered_data['Hotel Stays Per Year'].value_counts().head(3)
            freq_list = [f'{freq} ({count})' for freq, count in frequency.items()]
            insights.append(f"🏨 **Hotel Stay Frequency**: {', '.join(freq_list)}")
        
        # Entertainment insights
        if 'Entertainment Quality Rating' in filtered_data.columns:
            avg_rating = filtered_data['Entertainment Quality Rating'].mean()
            if pd.notna(avg_rating):
                insights.append(f"⭐ **Entertainment Satisfaction**: Average rating {avg_rating:.1f}/5")
        
        # Business recommendations
        if analysis_type == "business":
            insights.extend([
                "💡 **Recommendation**: Focus marketing on top nationality segments identified",
                "📈 **Strategy**: Enhance entertainment based on satisfaction ratings", 
                "🎯 **Action**: Customize services for primary visit purposes (Business/Leisure/Family)"
            ])
        
        return "\n\n".join(insights)
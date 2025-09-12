#!/usr/bin/env python3
"""
Simple, Robust OSN Survey Data Processor
Focus: Clean 400 responses, proper question mapping, reliable filters
No over-engineering - just what works consistently
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import re

warnings.filterwarnings('ignore')

class SimpleRobustProcessor:
    """
    Simple, reliable survey data processor
    Goal: Always return exactly 400 responses with clean question names
    """
    
    def __init__(self, excel_path: str = "data/survey_data.xlsx"):
        self.excel_path = Path(excel_path)
        self.data = None
        self.questions = {}
        self.filters = {}
        
    def load_data(self):
        """Load data with the simplest possible approach that works"""
        print("🔄 Loading survey data (simple approach)...")
        
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
            
            # Step 4: Clean up question names
            self._clean_question_names()
            
            # Step 5: Set up simple filters
            self._setup_filters()
            
            print(f"✅ Successfully loaded exactly {len(self.data)} responses")
            print(f"   UAE: {len(self.data[self.data['Country'] == 'UAE'])}")
            print(f"   KSA: {len(self.data[self.data['Country'] == 'KSA'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _load_sheet(self, sheet_name: str):
        """Load a single sheet with exactly 200 responses"""
        try:
            # Read the sheet starting from the correct row
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
    
    def _clean_question_names(self):
        """Clean column names to be more readable"""
        if self.data is None:
            return
        
        # Create mapping for better question names
        question_mapping = {
            'A1': 'Nationality',
            'A2': 'Visit Purpose', 
            'A3': 'Hotel Stays Per Year',
            'B1-A/1': 'Hotel Choice Reason 1',
            'B1-A/2': 'Hotel Choice Reason 2', 
            'B1-A/3': 'Hotel Choice Reason 3',
            'B1-B': 'Entertainment Priority with Family',
            'B2-A': 'Entertainment Importance Rating',
            'B2-B': 'Entertainment Experience Story',
            'C1': 'Used In-Room Entertainment',
            'C2-A/1': 'Content Type 1',
            'C2-A/2': 'Content Type 2',
            'C2-A/3': 'Content Type 3',
            'C2-B': 'Content Accessibility',
            'C3/1': 'Preferred Entertainment Format',
            'C4-A': 'Entertainment Quality Rating',
            'C4-B': 'Improvement Suggestions',
            'D2': 'Streaming Account Access Preference',
            'D3': 'Willingness to Pay for Enhanced Entertainment',
            'D4': 'Acceptable Price Range',
            'D5': 'General Entertainment Suggestions'
        }
        
        # Apply mapping and clean remaining names
        new_columns = []
        for col in self.data.columns:
            if col in question_mapping:
                new_columns.append(question_mapping[col])
            elif col == 'Country':
                new_columns.append(col)
            elif 'Unnamed' in str(col):
                # Skip unnamed columns
                continue
            else:
                # Clean other column names
                clean_name = str(col).replace('_', ' ').strip()
                if clean_name and len(clean_name) > 1:
                    new_columns.append(clean_name)
                else:
                    continue
        
        # Rebuild dataframe with only mapped columns
        mapped_data = pd.DataFrame()
        col_index = 0
        
        for original_col in self.data.columns:
            if original_col in question_mapping:
                mapped_data[question_mapping[original_col]] = self.data[original_col]
            elif original_col == 'Country':
                mapped_data[original_col] = self.data[original_col]
            elif not ('Unnamed' in str(original_col) or str(original_col).startswith('S. No.')):
                if pd.notna(original_col) and str(original_col).strip():
                    clean_name = str(original_col).replace('_', ' ').strip()
                    if len(clean_name) > 1:
                        mapped_data[clean_name] = self.data[original_col]
        
        self.data = mapped_data
        print(f"📝 Mapped to {len(self.data.columns)} clean columns")
        
        # Store question info
        self.questions = {col: col for col in self.data.columns if col != 'Country'}
    
    def _setup_filters(self):
        """Set up simple, reliable filters"""
        if self.data is None:
            return
        
        self.filters = {
            'countries': ['UAE', 'KSA'],
            'nationalities': [],
            'visit_purposes': [],
            'entertainment_ratings': []
        }
        
        # Get nationality options
        if 'Nationality' in self.data.columns:
            nationalities = self.data['Nationality'].dropna().unique()
            self.filters['nationalities'] = [str(n).strip() for n in nationalities if pd.notna(n) and str(n).strip()][:15]
        
        # Get visit purpose options  
        if 'Visit Purpose' in self.data.columns:
            purposes = self.data['Visit Purpose'].dropna().unique()
            # Map numeric codes to text
            purpose_map = {1: 'Business', 2: 'Leisure', 3: 'Family Vacation', 99: 'Other'}
            mapped_purposes = []
            for p in purposes:
                if pd.notna(p):
                    if str(p).isdigit():
                        mapped_purposes.append(purpose_map.get(int(p), f"Purpose {p}"))
                    else:
                        mapped_purposes.append(str(p).strip())
            self.filters['visit_purposes'] = list(set(mapped_purposes))[:10]
        
        # Get entertainment ratings
        if 'Entertainment Quality Rating' in self.data.columns:
            ratings = self.data['Entertainment Quality Rating'].dropna().unique()
            self.filters['entertainment_ratings'] = [str(r) for r in sorted(ratings) if pd.notna(r)][:10]
        
        print(f"🎯 Filter options ready:")
        print(f"   Nationalities: {len(self.filters['nationalities'])}")
        print(f"   Visit Purposes: {len(self.filters['visit_purposes'])}")
        print(f"   Entertainment Ratings: {len(self.filters['entertainment_ratings'])}")
    
    def get_filtered_data(self, country_filter=None, nationality_filter=None, purpose_filter=None):
        """Get filtered data with simple, reliable filtering"""
        if self.data is None:
            return pd.DataFrame()
        
        df = self.data.copy()
        
        # Apply country filter
        if country_filter:
            df = df[df['Country'].isin(country_filter)]
        
        # Apply nationality filter
        if nationality_filter and 'Nationality' in df.columns:
            df = df[df['Nationality'].isin(nationality_filter)]
        
        # Apply purpose filter
        if purpose_filter and 'Visit Purpose' in df.columns:
            # Handle both numeric and text matching
            mask = pd.Series([False] * len(df))
            for purpose in purpose_filter:
                if purpose == 'Business':
                    mask |= (df['Visit Purpose'] == 1) | df['Visit Purpose'].astype(str).str.contains('Business', case=False, na=False)
                elif purpose == 'Leisure':
                    mask |= (df['Visit Purpose'] == 2) | df['Visit Purpose'].astype(str).str.contains('Leisure', case=False, na=False)
                elif purpose == 'Family Vacation':
                    mask |= (df['Visit Purpose'] == 3) | df['Visit Purpose'].astype(str).str.contains('Family', case=False, na=False)
                else:
                    mask |= df['Visit Purpose'].astype(str).str.contains(str(purpose), case=False, na=False)
            df = df[mask] if mask.any() else df
        
        return df
    
    def get_summary_stats(self):
        """Get basic summary statistics"""
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
        """Simple cross-tabulation between two questions"""
        # Apply filters if provided
        if filters:
            df = self.get_filtered_data(
                country_filter=filters.get('countries'),
                nationality_filter=filters.get('nationalities'),
                purpose_filter=filters.get('purposes')
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
                'combinations': combinations[:10]  # Top 10 combinations
            }
            
        except Exception as e:
            print(f"Cross-tabulation error: {e}")
            return None
    
    def generate_insights(self, filtered_data, analysis_type="overview"):
        """Generate simple business insights"""
        if filtered_data is None or len(filtered_data) == 0:
            return "No data available for analysis."
        
        insights = []
        
        # Basic insights
        total_responses = len(filtered_data)
        uae_count = len(filtered_data[filtered_data['Country'] == 'UAE'])
        ksa_count = len(filtered_data[filtered_data['Country'] == 'KSA'])
        
        insights.append(f"📊 **Market Coverage**: {total_responses} total responses ({uae_count} UAE, {ksa_count} KSA)")
        
        # Nationality insights
        if 'Nationality' in filtered_data.columns:
            top_nationalities = filtered_data['Nationality'].value_counts().head(3)
            insights.append(f"🌍 **Top Guest Nationalities**: {', '.join([f'{nat} ({count})' for nat, count in top_nationalities.items()])}")
        
        # Visit purpose insights
        if 'Visit Purpose' in filtered_data.columns:
            purposes = filtered_data['Visit Purpose'].value_counts().head(3)
            purpose_text = []
            for purpose, count in purposes.items():
                if purpose == 1 or 'business' in str(purpose).lower():
                    purpose_text.append(f"Business ({count})")
                elif purpose == 2 or 'leisure' in str(purpose).lower():
                    purpose_text.append(f"Leisure ({count})")
                elif purpose == 3 or 'family' in str(purpose).lower():
                    purpose_text.append(f"Family ({count})")
                else:
                    purpose_text.append(f"{purpose} ({count})")
            insights.append(f"✈️ **Visit Purposes**: {', '.join(purpose_text)}")
        
        # Entertainment insights
        if 'Entertainment Quality Rating' in filtered_data.columns:
            avg_rating = filtered_data['Entertainment Quality Rating'].mean()
            if pd.notna(avg_rating):
                insights.append(f"⭐ **Entertainment Satisfaction**: Average rating {avg_rating:.1f}/5")
        
        # Business recommendations
        if analysis_type == "business":
            insights.extend([
                "💡 **Recommendation**: Focus marketing efforts on top nationality segments",
                "📈 **Strategy**: Enhance entertainment offerings based on satisfaction ratings", 
                "🎯 **Action**: Customize services for primary visit purposes identified"
            ])
        
        return "\n\n".join(insights)
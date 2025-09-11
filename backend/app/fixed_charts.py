#!/usr/bin/env python3
"""
Fixed chart generation with proper data handling for undefined legends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

def get_fixed_dynamic_charts(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate properly formatted chart data with no undefined values"""
    
    charts = {}
    
    # 1. Entertainment Importance by Country (Fixed)
    ent_col = 'B2-A'
    if ent_col in df.columns and 'Country' in df.columns:
        # Clean data first
        clean_df = df[[ent_col, 'Country']].dropna()
        
        if len(clean_df) > 0:
            country_ent = clean_df.groupby('Country')[ent_col].value_counts(normalize=True).unstack(fill_value=0) * 100
            
            # Ensure all expected categories exist
            expected_categories = ['Very Important', 'Somewhat Important', 'Not Important']
            for cat in expected_categories:
                if cat not in country_ent.columns:
                    country_ent[cat] = 0
            
            # Reorder columns
            country_ent = country_ent[expected_categories]
            
            charts['entertainment_importance_by_country'] = {
                'type': 'grouped_bar',
                'title': 'Entertainment Importance by Market',
                'data': {
                    'countries': country_ent.index.tolist(),
                    'series': [
                        {
                            'name': cat,
                            'data': [round(float(val), 1) for val in country_ent[cat].tolist()],
                            'backgroundColor': ['#28a745', '#ffc107', '#dc3545'][i]
                        }
                        for i, cat in enumerate(expected_categories)
                    ]
                }
            }
    
    # 2. Content Preferences Distribution (Fixed - Handle multiple columns)
    content_preferences = {}
    content_cols = [col for col in df.columns if col.startswith('C2-A/') and col != 'C2-A-a']
    
    if content_cols:
        for col in content_cols:
            # Extract the content type from the column data
            col_data = df[col].dropna()
            if len(col_data) > 0:
                content_type = col_data.iloc[0]  # Get the content type name
                count = len(col_data)
                content_preferences[content_type] = count
    
    if content_preferences:
        # Sort by count and take top 8
        sorted_content = sorted(content_preferences.items(), key=lambda x: x[1], reverse=True)[:8]
        
        charts['content_preferences_distribution'] = {
            'type': 'pie',
            'title': 'Guest Content Preferences',
            'data': {
                'labels': [item[0] for item in sorted_content],
                'data': [int(item[1]) for item in sorted_content],
                'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F06292'][:len(sorted_content)]
            }
        }
    
    # 3. Payment Willingness Analysis (Fixed)
    payment_col = 'D3'
    purpose_col = 'A2'
    
    if payment_col in df.columns and purpose_col in df.columns:
        # Clean data
        clean_df = df[[payment_col, purpose_col]].dropna()
        
        if len(clean_df) > 0:
            payment_by_purpose = clean_df.groupby(purpose_col)[payment_col].value_counts(normalize=True).unstack(fill_value=0) * 100
            
            # Ensure Yes/No columns exist
            if 'Yes' not in payment_by_purpose.columns:
                payment_by_purpose['Yes'] = 0
            if 'No' not in payment_by_purpose.columns:
                payment_by_purpose['No'] = 0
            
            charts['payment_willingness_analysis'] = {
                'type': 'stacked_bar',
                'title': 'Payment Willingness by Visitor Type',
                'data': {
                    'categories': payment_by_purpose.index.tolist(),
                    'series': [
                        {
                            'name': 'Willing to Pay',
                            'data': [round(float(val), 1) for val in payment_by_purpose['Yes'].tolist()],
                            'backgroundColor': '#28a745'
                        },
                        {
                            'name': 'Not Willing',
                            'data': [round(float(val), 1) for val in payment_by_purpose['No'].tolist()],
                            'backgroundColor': '#dc3545'
                        }
                    ]
                }
            }
    
    # 4. Revenue Funnel (Fixed with actual data)
    total_respondents = len(df)
    
    # Calculate actual funnel metrics
    tv_usage_count = 0
    if 'C1' in df.columns:
        tv_usage_count = (df['C1'] == 'Yes').sum()
    
    high_importance_count = 0
    if 'B2-A' in df.columns:
        high_importance_count = (df['B2-A'] == 'Very Important').sum()
    
    willing_to_pay_count = 0
    if 'D3' in df.columns:
        willing_to_pay_count = (df['D3'] == 'Yes').sum()
    
    streaming_preference_count = 0
    if 'D2' in df.columns:
        streaming_preference_count = (df['D2'] == 'Yes').sum()
    
    charts['revenue_potential_funnel'] = {
        'type': 'funnel',
        'title': 'OSN Revenue Opportunity Funnel',
        'data': {
            'stages': [
                {'name': 'Total Survey Respondents', 'value': int(total_respondents), 'color': '#E3F2FD'},
                {'name': 'Use Entertainment Systems', 'value': int(tv_usage_count), 'color': '#BBDEFB'},
                {'name': 'Rate Entertainment Very Important', 'value': int(high_importance_count), 'color': '#90CAF9'},
                {'name': 'Willing to Pay for Premium', 'value': int(willing_to_pay_count), 'color': '#64B5F6'},
                {'name': 'Want Streaming Integration', 'value': int(streaming_preference_count), 'color': '#42A5F5'}
            ]
        }
    }
    
    # 5. Market Heatmap (Fixed with actual calculations)
    opportunities = []
    
    for country in df['Country'].unique():
        country_data = df[df['Country'] == country]
        
        # Calculate entertainment demand
        ent_demand = 50.0  # Default
        if 'B2-A' in country_data.columns:
            ent_demand = (country_data['B2-A'] == 'Very Important').mean() * 100
        
        # Calculate payment willingness
        pay_willingness = 50.0  # Default
        if 'D3' in country_data.columns:
            pay_willingness = (country_data['D3'] == 'Yes').mean() * 100
        
        opportunity_score = (ent_demand + pay_willingness) / 2
        
        opportunities.append({
            'country': str(country),
            'entertainment_demand': round(float(ent_demand), 1),
            'payment_willingness': round(float(pay_willingness), 1),
            'opportunity_score': round(float(opportunity_score), 1)
        })
    
    charts['market_opportunity_heatmap'] = {
        'type': 'matrix',
        'title': 'Market Opportunity Matrix',
        'data': opportunities
    }
    
    # 6. Visit Purpose vs Entertainment Correlation (New)
    if 'A2' in df.columns and 'B2-A' in df.columns:
        clean_df = df[['A2', 'B2-A']].dropna()
        
        if len(clean_df) > 0:
            crosstab = pd.crosstab(clean_df['A2'], clean_df['B2-A'], normalize='index') * 100
            
            charts['purpose_entertainment_correlation'] = {
                'type': 'heatmap',
                'title': 'Visit Purpose vs Entertainment Importance',
                'data': {
                    'x_categories': crosstab.columns.tolist(),
                    'y_categories': crosstab.index.tolist(),
                    'values': [[round(float(val), 1) for val in row] for row in crosstab.values.tolist()]
                }
            }
    
    # 7. Streaming vs Traditional TV Preferences (New)
    streaming_data = {}
    if 'D2' in df.columns:
        streaming_counts = df['D2'].value_counts()
        streaming_data = {
            'labels': streaming_counts.index.tolist(),
            'data': [int(x) for x in streaming_counts.values],
            'colors': ['#28a745', '#dc3545', '#ffc107'][:len(streaming_counts)]
        }
        
        charts['streaming_preferences'] = {
            'type': 'doughnut',
            'title': 'Streaming Account Access Preference',
            'data': streaming_data
        }
    
    return charts

def get_entertainment_viz_data_fixed(df: pd.DataFrame) -> Dict[str, Any]:
    """Fixed visualization data without undefined values"""
    
    viz_data = {}
    
    # Entertainment importance distribution (Fixed)
    if 'B2-A' in df.columns:
        importance_data = df['B2-A'].value_counts()
        viz_data['importance_distribution'] = {
            'labels': importance_data.index.tolist(),
            'data': [int(x) for x in importance_data.values],
            'colors': ['#28a745', '#ffc107', '#dc3545']
        }
    
    # TV usage by country (Fixed)
    if 'C1' in df.columns and 'Country' in df.columns:
        clean_df = df[['C1', 'Country']].dropna()
        tv_by_country = clean_df.groupby('Country')['C1'].value_counts().unstack(fill_value=0)
        
        # Ensure Yes/No columns exist
        if 'Yes' not in tv_by_country.columns:
            tv_by_country['Yes'] = 0
        if 'No' not in tv_by_country.columns:
            tv_by_country['No'] = 0
        
        viz_data['tv_usage_by_country'] = {
            'countries': tv_by_country.index.tolist(),
            'yes_data': [int(x) for x in tv_by_country['Yes'].tolist()],
            'no_data': [int(x) for x in tv_by_country['No'].tolist()]
        }
    
    # Payment willingness trends (Fixed)
    if 'D3' in df.columns:
        payment_data = df['D3'].value_counts()
        viz_data['payment_willingness'] = {
            'labels': payment_data.index.tolist(),
            'data': [int(x) for x in payment_data.values]
        }
    
    return viz_data
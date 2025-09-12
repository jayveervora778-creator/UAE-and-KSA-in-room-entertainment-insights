#!/usr/bin/env python3
"""
Fixed chart generation with proper data handling for undefined legends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

def get_fixed_dynamic_charts(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate properly formatted chart data with no undefined values"""
    
    # Separate static charts (don't change with filtering) from dynamic charts
    static_charts = {}
    filterable_charts = {}
    
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
            
            filterable_charts['entertainment_importance_by_country'] = {
                'type': 'bar',
                'title': 'Entertainment Importance by Market',
                'data': {
                    'labels': country_ent.index.tolist(),
                    'datasets': [
                        {
                            'label': cat,
                            'data': [round(float(val), 1) for val in country_ent[cat].tolist()],
                            'backgroundColor': ['#28a745', '#ffc107', '#dc3545'][i],
                            'borderColor': ['#28a745', '#ffc107', '#dc3545'][i],
                            'borderWidth': 1
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
        
        static_charts['content_preferences_distribution'] = {
            'type': 'pie',
            'title': 'Guest Content Preferences',
            'data': {
                'labels': [item[0] for item in sorted_content],
                'datasets': [{
                    'data': [int(item[1]) for item in sorted_content],
                    'backgroundColor': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F06292'][:len(sorted_content)],
                    'borderWidth': 1
                }]
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
            
            filterable_charts['payment_willingness_analysis'] = {
                'type': 'bar',
                'title': 'Payment Willingness by Visitor Type',
                'data': {
                    'labels': payment_by_purpose.index.tolist(),
                    'datasets': [
                        {
                            'label': 'Willing to Pay',
                            'data': [round(float(val), 1) for val in payment_by_purpose['Yes'].tolist()],
                            'backgroundColor': '#28a745',
                            'borderColor': '#28a745',
                            'borderWidth': 1
                        },
                        {
                            'label': 'Not Willing',
                            'data': [round(float(val), 1) for val in payment_by_purpose['No'].tolist()],
                            'backgroundColor': '#dc3545',
                            'borderColor': '#dc3545',
                            'borderWidth': 1
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
    
    # Convert funnel to horizontal bar chart for Chart.js
    funnel_stages = [
        {'name': 'Survey Respondents', 'value': int(total_respondents), 'color': '#E3F2FD'},
        {'name': 'Use TV/Entertainment', 'value': int(tv_usage_count), 'color': '#BBDEFB'},
        {'name': 'High Entertainment Priority', 'value': int(high_importance_count), 'color': '#90CAF9'},
        {'name': 'Willing to Pay Premium', 'value': int(willing_to_pay_count), 'color': '#64B5F6'},
        {'name': 'Want Streaming Access', 'value': int(streaming_preference_count), 'color': '#42A5F5'}
    ]
    
    filterable_charts['survey_response_analysis'] = {
        'type': 'bar',
        'title': 'Survey Response Trends (Sample Data Only)',
        'subtitle': 'Based on 400 respondents - not market sizing',
        'options': {
            'indexAxis': 'y'
        },
        'data': {
            'labels': [stage['name'] for stage in funnel_stages],
            'datasets': [{
                'label': 'Count',
                'data': [stage['value'] for stage in funnel_stages],
                'backgroundColor': [stage['color'] for stage in funnel_stages],
                'borderWidth': 1
            }]
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
    
    # Convert matrix to scatter plot for Chart.js
    filterable_charts['market_opportunity_heatmap'] = {
        'type': 'scatter',
        'title': 'Market Opportunity Matrix',
        'data': {
            'datasets': [{
                'label': 'Market Opportunities',
                'data': [
                    {
                        'x': opp['entertainment_demand'],
                        'y': opp['payment_willingness'],
                        'label': opp['country']
                    }
                    for opp in opportunities
                ],
                'backgroundColor': ['#007bff', '#28a745', '#ffc107', '#dc3545'][:len(opportunities)],
                'pointRadius': 8
            }]
        }
    }
    
    # 6. Visit Purpose vs Entertainment Correlation (New)
    if 'A2' in df.columns and 'B2-A' in df.columns:
        clean_df = df[['A2', 'B2-A']].dropna()
        
        if len(clean_df) > 0:
            crosstab = pd.crosstab(clean_df['A2'], clean_df['B2-A'], normalize='index') * 100
            
            # Convert heatmap to grouped bar chart for better Chart.js support
            static_charts['purpose_entertainment_correlation'] = {
                'type': 'bar',
                'title': 'Visit Purpose vs Entertainment Importance',
                'data': {
                    'labels': crosstab.index.tolist(),
                    'datasets': [
                        {
                            'label': importance_level,
                            'data': [round(float(val), 1) for val in crosstab[importance_level].values],
                            'backgroundColor': ['#28a745', '#ffc107', '#dc3545'][i],
                            'borderColor': ['#28a745', '#ffc107', '#dc3545'][i],
                            'borderWidth': 1
                        }
                        for i, importance_level in enumerate(crosstab.columns)
                    ]
                }
            }
    
    # 7. Streaming vs Traditional TV Preferences (New)
    streaming_data = {}
    if 'D2' in df.columns:
        streaming_counts = df['D2'].value_counts()
        streaming_data = {
            'labels': streaming_counts.index.tolist(),
            'datasets': [{
                'data': [int(x) for x in streaming_counts.values],
                'backgroundColor': ['#28a745', '#dc3545', '#ffc107'][:len(streaming_counts)],
                'borderWidth': 1
            }]
        }
        
        static_charts['streaming_preferences'] = {
            'type': 'doughnut',
            'title': 'Streaming Account Access Preference',
            'data': streaming_data
        }
    
    # Combine charts with proper categorization
    return {
        'charts': {**static_charts, **filterable_charts},
        'static_charts': static_charts,
        'filterable_charts': filterable_charts,
        'chart_metadata': {
            'static_count': len(static_charts),
            'filterable_count': len(filterable_charts),
            'total_charts': len(static_charts) + len(filterable_charts),
            'categories': {
                'static': list(static_charts.keys()),
                'filterable': list(filterable_charts.keys())
            }
        }
    }

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
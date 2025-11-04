#!/usr/bin/env python3
"""
Light chart configuration to ensure all Plotly charts use light theme
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

def configure_light_charts():
    """Configure Plotly to use light theme globally"""
    
    # Set default template to light theme
    pio.templates.default = "plotly_white"
    
    # Configure light theme settings
    light_layout = dict(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font_color='#374151',
        font_family='Arial, sans-serif',
        title_font_color='#1f2937',
        xaxis=dict(
            color='#374151',
            gridcolor='#e5e7eb',
            linecolor='#d1d5db'
        ),
        yaxis=dict(
            color='#374151',
            gridcolor='#e5e7eb',
            linecolor='#d1d5db'
        ),
        legend=dict(
            bgcolor='#FFFFFF',
            bordercolor='#e5e7eb',
            font_color='#374151'
        )
    )
    
    return light_layout

def apply_light_theme_to_figure(fig):
    """Apply light theme to any Plotly figure"""
    
    fig.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font_color='#374151',
        font_family='Arial, sans-serif',
        title_font_color='#1f2937',
        xaxis=dict(
            color='#374151',
            gridcolor='#e5e7eb',
            linecolor='#d1d5db',
            tickcolor='#9ca3af'
        ),
        yaxis=dict(
            color='#374151',
            gridcolor='#e5e7eb',
            linecolor='#d1d5db',
            tickcolor='#9ca3af'
        ),
        legend=dict(
            bgcolor='#FFFFFF',
            bordercolor='#e5e7eb',
            font_color='#374151'
        ),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # Update traces to use light-friendly colors
    fig.update_traces(
        line_color='#667eea',
        marker_color='#667eea',
        textfont_color='#374151'
    )
    
    return fig

# Set global configuration when module is imported
configure_light_charts()
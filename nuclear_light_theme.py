#!/usr/bin/env python3
"""
Nuclear Light Theme - Aggressive CSS to kill ALL dark themes
"""

import streamlit as st

def apply_nuclear_light_theme():
    """Apply nuclear-level CSS to force light theme on everything"""
    st.markdown("""
    <style>
        /* === NUCLEAR LIGHT THEME ENFORCEMENT === */
        /* Override EVERYTHING with light theme */
        * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* Root CSS variables override */
        :root {
            --background-color: #FFFFFF !important;
            --text-color: #374151 !important;
            --border-color: #d1d5db !important;
            --primary-color: #667eea !important;
        }
        
        /* === STREAMLIT COMPONENTS === */
        .stApp {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        .main .block-container {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === AGGRESSIVE DROPDOWN FIXES === */
        .stSelectbox,
        .stSelectbox *,
        .stSelectbox div,
        .stSelectbox span,
        .stMultiSelect,
        .stMultiSelect *,
        .stMultiSelect div,
        .stMultiSelect span {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 2px solid #d1d5db !important;
            border-radius: 6px !important;
        }
        
        /* Target ALL possible dropdown selectors */
        [class*="select"],
        [class*="Select"],
        [class*="dropdown"],
        [class*="Dropdown"],
        [class*="menu"],
        [class*="Menu"],
        [role="combobox"],
        [role="listbox"],
        [role="option"],
        [aria-haspopup="listbox"],
        [data-baseweb*="select"],
        [data-testid*="select"] {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
        }
        
        /* === PLOTLY CHART THEME FIXES === */
        .js-plotly-plot,
        .js-plotly-plot *,
        .plotly,
        .plotly *,
        .plot-container,
        .plot-container *,
        .main-svg,
        .main-svg * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            fill: #374151 !important;
        }
        
        /* Plotly specific elements */
        .modebar {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
        }
        
        .modebar-btn {
            background: #f8f9fa !important;
            background-color: #f8f9fa !important;
            color: #374151 !important;
            fill: #374151 !important;
        }
        
        /* === CSS CLASS TARGETING === */
        /* Target any CSS class that might contain dark styling */
        [class*="css-"],
        [class*="st-"],
        [class*="react-"],
        [class*="base-"],
        [class*="theme-"] {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === INLINE STYLE OVERRIDE === */
        /* Force override any inline styles */
        [style] {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === SIDEBAR === */
        .stSidebar,
        .stSidebar * {
            background: #f9fafb !important;
            background-color: #f9fafb !important;
            color: #374151 !important;
        }
        
        /* === TEXT ELEMENTS === */
        h1, h2, h3, h4, h5, h6,
        p, span, div, label,
        input, textarea, select {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === BUTTONS === */
        .stButton button {
            background: #667eea !important;
            background-color: #667eea !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        
        /* === CHARTS AND PLOTS === */
        .stPlotlyChart,
        .stPlotlyChart * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
        }
        
        /* === EXPANDERS === */
        .stExpander,
        .stExpander * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 1px solid #e5e7eb !important;
        }
        
        /* === METRICS === */
        .stMetric,
        .stMetric * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === DATAFRAMES === */
        .stDataFrame,
        .stDataFrame * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
        
        /* === COMPREHENSIVE OVERRIDE === */
        /* Target absolutely everything */
        body,
        html,
        div,
        span,
        input,
        select,
        button,
        ul,
        li,
        ol,
        table,
        tr,
        td,
        th,
        form,
        fieldset,
        legend,
        textarea,
        svg,
        g,
        path,
        rect,
        circle {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
            fill: #374151 !important;
            stroke: #374151 !important;
        }
        
        /* === FINAL NUCLEAR OPTION === */
        /* If all else fails, use !important on absolutely everything */
        * {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
            fill: #374151 !important;
        }
        
        *:before,
        *:after {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: #374151 !important;
        }
    </style>
    """, unsafe_allow_html=True)
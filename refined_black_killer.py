#!/usr/bin/env python3
"""
Refined Black Element Killer - Precise targeting without breaking chart content
"""

import streamlit as st

def apply_refined_black_killer():
    """Apply refined CSS to eliminate black areas without breaking charts"""
    st.markdown("""
    <style>
        /* === REFINED PLOTLY CHART FIXES === */
        /* Ensure plotly charts have white backgrounds without breaking content */
        .js-plotly-plot {
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
        }
        
        /* Target only plot background elements, not data */
        .plotly .bg,
        .js-plotly-plot .bg,
        .plot-container .bg,
        svg.main-svg .bg {
            fill: #FFFFFF !important;
            background-color: #FFFFFF !important;
        }
        
        /* Preserve chart data visualization elements */
        .js-plotly-plot path:not(.bg),
        .js-plotly-plot rect:not(.bg),
        .js-plotly-plot circle,
        .js-plotly-plot line,
        .js-plotly-plot text,
        .js-plotly-plot g[class*="trace"],
        .js-plotly-plot g[class*="scatter"],
        .js-plotly-plot g[class*="bar"],
        .js-plotly-plot g[class*="pie"] {
            /* Let charts render with their natural colors */
        }
        
        /* Ensure axis and grid elements are visible */
        .js-plotly-plot .xaxis,
        .js-plotly-plot .yaxis,
        .js-plotly-plot .gridlines,
        .js-plotly-plot .tick,
        .js-plotly-plot .xtick,
        .js-plotly-plot .ytick {
            stroke: #374151 !important;
            color: #374151 !important;
        }
        
        /* === DROPDOWN TEXT AREA FIXES === */
        /* Text formatting and areas around text in dropdowns */
        .stSelectbox span,
        .stSelectbox div span,
        .stSelectbox > div > div span,
        .stMultiSelect span,
        .stMultiSelect div span {
            background-color: transparent !important;
            color: #1f2937 !important;
        }
        
        /* Dropdown containers (but not content) */
        .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            color: #1f2937 !important;
        }
        
        /* === REFINED CHART BACKGROUND FIXES === */
        /* Only target chart container backgrounds, NOT content */
        .js-plotly-plot {
            background-color: #FFFFFF !important;
        }
        
        .plot-container {
            background-color: #FFFFFF !important;
        }
        
        div.plotly-graph-div {
            background-color: #FFFFFF !important;
        }
        
        /* Target only specific background elements */
        .js-plotly-plot .bg,
        .plotly .bg,
        .plot-container .bg {
            fill: #FFFFFF !important;
        }
        
        /* Chart paper background only */
        .js-plotly-plot .plotly .paper {
            fill: #FFFFFF !important;
        }
        
        /* === STREAMLIT CHART CONTAINERS === */
        .stPlotlyChart {
            background-color: #FFFFFF !important;
        }
        
        /* === REFINED DROPDOWN SELECTION STYLING === */
        /* Replace harsh blue outline with subtle styling */
        .stSelectbox > div > div:focus-within {
            border-color: #94a3b8 !important;
            box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.3) !important;
        }
        
        .stMultiSelect > div > div:focus-within {
            border-color: #94a3b8 !important;
            box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.3) !important;
        }
        
        /* === SPECIFIC BLACK BACKGROUND TARGETING === */
        /* Only target actual black backgrounds, not chart content */
        [style*="background-color: black"]:not(path):not(rect):not(circle),
        [style*="background: black"]:not(path):not(rect):not(circle),
        [style*="background-color: #000"]:not(path):not(rect):not(circle),
        [style*="background-color: rgb(0, 0, 0)"]:not(path):not(rect):not(circle) {
            background-color: #FFFFFF !important;
            color: #1f2937 !important;
        }
        
        /* === MODEBAR FIXES === */
        .modebar {
            background-color: #FFFFFF !important;
        }
        
        .modebar-btn {
            background-color: #f8f9fa !important;
            color: #1f2937 !important;
        }
        
        /* === TEXT ELEMENTS === */
        /* Ensure text is readable without breaking chart elements */
        .stSelectbox input,
        .stMultiSelect input {
            background-color: transparent !important;
            color: #1f2937 !important;
        }
        
        /* === SVG ARROW FIXES === */
        /* Only target dropdown arrows, not chart SVGs */
        .stSelectbox svg:not(.main-svg),
        .stMultiSelect svg:not(.main-svg) {
            background-color: transparent !important;
            color: #6b7280 !important;
            fill: #6b7280 !important;
        }
        
        /* === PRESERVE CHART CONTENT === */
        /* Explicitly preserve chart data elements */
        .js-plotly-plot path,
        .js-plotly-plot rect:not(.bg),
        .js-plotly-plot circle,
        .js-plotly-plot line,
        .js-plotly-plot text,
        .plotly path,
        .plotly rect:not(.bg),
        .plotly circle,
        .plotly line {
            /* Do NOT override - let charts render normally */
        }
    </style>
    """, unsafe_allow_html=True)
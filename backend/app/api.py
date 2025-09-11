#!/usr/bin/env python3
"""
API endpoints for the survey dashboard
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from .enhanced_data_processor import EnhancedSurveyDataProcessor as SurveyDataProcessor
from .config import Config
import traceback

bp = Blueprint('api', __name__)

# Global data processor instance
data_processor = None

def get_data_processor():
    """Get or create data processor instance"""
    global data_processor
    # Force refresh of data processor to ensure we're using the enhanced version
    try:
        print("Initializing Enhanced Data Processor...")
        data_processor = SurveyDataProcessor(Config.SURVEY_DATA_FILE)
        print(f"Data processor initialized successfully with {len(data_processor.processed_data)} sheets")
        return data_processor
    except Exception as e:
        print(f"Error initializing data processor: {e}")
        traceback.print_exc()
        return None

@bp.route('/filters')
@login_required
def get_filters():
    """Get available filter options"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        filters = processor.get_filter_options()
        return jsonify(filters)
    except Exception as e:
        print(f"Error getting filters: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/summary')
@login_required
def get_summary():
    """Get summary statistics"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        # Get filters from query parameters
        filters = {}
        if request.args.get('country'):
            filters['Country'] = request.args.get('country')
        if request.args.get('nationality'):
            filters['nationality'] = request.args.get('nationality')
        
        # Apply filters
        filtered_df = processor.filter_data(filters) if filters else None
        stats = processor.get_summary_stats(filtered_df)
        
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting summary: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/text-analysis')
@login_required
def analyze_text():
    """Analyze text responses using NLP"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        column = request.args.get('column')
        country = request.args.get('country')
        
        if not column:
            return jsonify({'error': 'Column parameter required'}), 400
        
        analysis = processor.analyze_text_responses(column, country)
        return jsonify(analysis)
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/raw-data')
@login_required
def get_raw_data():
    """Get raw survey data"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        sheet_name = request.args.get('sheet')
        data = processor.get_raw_data_json(sheet_name)
        
        return jsonify(data)
    except Exception as e:
        print(f"Error getting raw data: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/questions')
@login_required
def get_questions():
    """Get question mappings"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        return jsonify(processor.question_mapping)
    except Exception as e:
        print(f"Error getting questions: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/text-columns')
@login_required
def get_text_columns():
    """Get available text response columns for NLP analysis"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        text_columns = {}
        for sheet_name, columns in processor.text_responses.items():
            text_columns[sheet_name] = list(columns.keys())
        
        return jsonify(text_columns)
    except Exception as e:
        print(f"Error getting text columns: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/data/filtered')
@login_required
def get_filtered_data():
    """Get filtered survey data"""
    try:
        processor = get_data_processor()
        if processor is None:
            return jsonify({'error': 'Data processor not available'}), 500
        
        # Parse filters from request
        filters = {}
        for key, value in request.args.items():
            if value and value.lower() != 'all':
                filters[key] = value
        
        filtered_df = processor.filter_data(filters)
        
        # Convert to JSON-serializable format
        result = {
            'data': filtered_df.to_dict('records'),
            'columns': list(filtered_df.columns),
            'total_records': len(filtered_df),
            'applied_filters': filters
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting filtered data: {e}")
        return jsonify({'error': str(e)}), 500
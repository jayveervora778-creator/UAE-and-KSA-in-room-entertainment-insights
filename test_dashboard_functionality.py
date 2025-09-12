#!/usr/bin/env python3
"""
Test Dashboard Functionality - Verify all components are working
"""

import pandas as pd
import requests
import time
from comprehensive_data_processor import ComprehensiveOSNProcessor

def test_data_processor():
    """Test the data processor initialization and basic functionality"""
    print("🧪 Testing Data Processor...")
    
    try:
        # Initialize processor
        processor = ComprehensiveOSNProcessor("data/survey_data.xlsx")
        
        # Load and process data
        success = processor.load_and_process_data()
        
        if not success:
            print("❌ Data loading failed")
            return False
        
        # Test summary statistics
        stats = processor.get_summary_statistics()
        print(f"✅ Total responses: {stats.get('total_responses', 0)}")
        print(f"✅ Countries: {stats.get('countries_represented', 0)}")
        print(f"✅ Questions: {stats.get('total_questions', 0)}")
        
        # Test filtering
        filters = {'countries': ['UAE', 'KSA'], 'nationalities': [], 'visit_purposes': []}
        filtered_data = processor.get_filtered_data(filters)
        print(f"✅ Filtered data shape: {filtered_data.shape}")
        
        # Test text analysis if text columns exist
        if processor.text_columns:
            text_col = list(processor.text_columns.keys())[0]
            analysis = processor.perform_text_analysis(text_col, filters)
            print(f"✅ Text analysis on '{text_col}': {analysis.get('total_responses', 0)} responses analyzed")
        
        # Test business insights
        insights = processor.generate_business_insights(filters)
        print(f"✅ Business insights generated: {len(insights)} categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processor test failed: {e}")
        return False

def test_dashboard_endpoint():
    """Test if the dashboard is accessible via HTTP"""
    print("🌐 Testing Dashboard Endpoint...")
    
    try:
        # Test local endpoint
        response = requests.get("http://localhost:8502", timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard is accessible at localhost:8502")
            return True
        else:
            print(f"⚠️ Dashboard returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard endpoint test failed: {e}")
        return False

def test_theme_files():
    """Test that theme files are properly imported"""
    print("🎨 Testing Theme Files...")
    
    try:
        from refined_light_theme import apply_refined_light_theme
        from refined_black_killer import apply_refined_black_killer
        
        print("✅ Refined light theme imported successfully")
        print("✅ Refined black killer imported successfully")
        
        # Test if they're callable
        if callable(apply_refined_light_theme) and callable(apply_refined_black_killer):
            print("✅ Theme functions are callable")
            return True
        else:
            print("❌ Theme functions are not callable")
            return False
            
    except ImportError as e:
        print(f"❌ Theme import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Dashboard Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Data Processor", test_data_processor),
        ("Theme Files", test_theme_files), 
        ("Dashboard Endpoint", test_dashboard_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is fully functional.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
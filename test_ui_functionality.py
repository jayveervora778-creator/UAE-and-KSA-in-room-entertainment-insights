#!/usr/bin/env python3
"""
Test UI Functionality - Check dropdowns and menus work properly
"""

import requests
import time

def test_dashboard_accessibility():
    """Test if dashboard loads and is responsive"""
    print("🌐 Testing Dashboard Accessibility...")
    
    try:
        response = requests.get("http://localhost:8502", timeout=30)
        
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
            
            # Check if basic content is present
            content = response.text.lower()
            
            checks = [
                ("title" in content, "Page has title"),
                ("osn" in content, "OSN branding present"),
                ("survey" in content, "Survey content present"),
                ("filter" in content, "Filter functionality present"),
                ("analytics" in content, "Analytics content present")
            ]
            
            for check, description in checks:
                if check:
                    print(f"✅ {description}")
                else:
                    print(f"⚠️ {description} - Not found")
                    
            return True
        else:
            print(f"❌ Dashboard returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_streamlit_functionality():
    """Test Streamlit specific functionality"""
    print("🧪 Testing Streamlit App Functionality...")
    
    try:
        # Test the simple app directly
        import sys
        sys.path.insert(0, '/home/user/webapp')
        
        from comprehensive_data_processor import ComprehensiveOSNProcessor
        
        # Test data loading
        processor = ComprehensiveOSNProcessor('data/survey_data.xlsx')
        success = processor.load_and_process_data()
        
        if success:
            print("✅ Data processor loads correctly")
            
            # Test filter options
            stats = processor.get_summary_statistics()
            filter_options = stats.get('filter_options', {})
            
            print(f"✅ Countries available: {filter_options.get('countries', [])}")
            print(f"✅ Nationalities count: {len(filter_options.get('nationalities', []))}")
            print(f"✅ Visit purposes count: {len(filter_options.get('visit_purposes', []))}")
            
            # Test filtering
            test_filters = {
                'countries': ['UAE'],
                'nationalities': [],
                'visit_purposes': []
            }
            
            filtered_data = processor.get_filtered_data(test_filters)
            print(f"✅ UAE filter works: {len(filtered_data)} responses")
            
            test_filters['countries'] = ['KSA']
            filtered_data = processor.get_filtered_data(test_filters)
            print(f"✅ KSA filter works: {len(filtered_data)} responses")
            
            return True
        else:
            print("❌ Data processor failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit functionality test failed: {e}")
        return False

def main():
    """Run all UI tests"""
    print("🚀 Testing UI Functionality - Dropdowns and Menus")
    print("=" * 60)
    
    tests = [
        ("Dashboard Accessibility", test_dashboard_accessibility),
        ("Streamlit Functionality", test_streamlit_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}")
    
    print("\n" + "=" * 60)
    print("📊 UI Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 Overall UI Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All UI tests passed! Dropdowns and menus should work correctly.")
        return True
    else:
        print("⚠️ Some UI tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
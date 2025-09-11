#!/usr/bin/env python3
"""
Test Chart.js loading in the dashboard
"""
import requests
import time

def test_chartjs_availability():
    """Test if Chart.js loads properly after login"""
    print("🔍 Testing Chart.js Library Loading...")
    
    session = requests.Session()
    
    # Login first
    login_data = {'username': 'admin', 'password': 'surveydash2024'}
    response = session.post('https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev/login', json=login_data)
    
    if response.status_code == 200 and response.json().get('success'):
        print("✅ Login successful")
        
        # Access the simple dashboard page
        dashboard_response = session.get('https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev/simple-dashboard')
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard page accessible")
            
            # Check if Chart.js script tags are in the HTML
            html_content = dashboard_response.text
            
            if 'Chart.js' in html_content or 'chart.js' in html_content or 'chart.min.js' in html_content:
                print("✅ Chart.js script tags found in HTML")
                
                # Check multiple CDN sources
                cdn_sources = [
                    'cdn.jsdelivr.net/npm/chart.js',
                    'cdnjs.cloudflare.com/ajax/libs/Chart.js',
                    'unpkg.com/chart.js'
                ]
                
                for cdn in cdn_sources:
                    if cdn in html_content:
                        print(f"✅ Found CDN source: {cdn}")
                
                # Check if the fallback loading script is present
                if 'loadChartJS' in html_content:
                    print("✅ Chart.js fallback loading script present")
                else:
                    print("❌ Chart.js fallback loading script missing")
                
                # Check if initialization function is present
                if 'initializeDashboard' in html_content:
                    print("✅ Dashboard initialization function present")
                else:
                    print("❌ Dashboard initialization function missing")
                    
                return True
            else:
                print("❌ Chart.js script tags not found in HTML")
                return False
        else:
            print(f"❌ Dashboard page not accessible: {dashboard_response.status_code}")
            return False
    else:
        print("❌ Login failed")
        return False

def test_api_endpoints():
    """Test if the API endpoints are working"""
    print("\n🔗 Testing API Endpoints...")
    
    session = requests.Session()
    
    # Login
    login_data = {'username': 'admin', 'password': 'surveydash2024'}
    response = session.post('https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev/login', json=login_data)
    
    if response.status_code == 200 and response.json().get('success'):
        # Test charts API
        charts_response = session.get('https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev/enhanced_api/dynamic-charts')
        
        if charts_response.status_code == 200:
            charts_data = charts_response.json()
            if 'charts' in charts_data and len(charts_data['charts']) > 0:
                print(f"✅ Charts API working: {len(charts_data['charts'])} charts")
                
                # Test one chart format
                first_chart_key = list(charts_data['charts'].keys())[0]
                first_chart = charts_data['charts'][first_chart_key]
                
                if 'data' in first_chart and 'labels' in first_chart['data'] and 'datasets' in first_chart['data']:
                    print("✅ Chart format is correct (Chart.js compatible)")
                    return True
                else:
                    print("❌ Chart format is incorrect")
                    return False
            else:
                print("❌ No charts in API response")
                return False
        else:
            print(f"❌ Charts API failed: {charts_response.status_code}")
            return False
    else:
        print("❌ API test login failed")
        return False

if __name__ == '__main__':
    print("🧪 OSN Dashboard Chart.js Loading Test\n")
    
    chartjs_ok = test_chartjs_availability()
    api_ok = test_api_endpoints()
    
    if chartjs_ok and api_ok:
        print("\n🎉 All tests passed! Dashboard should be working.")
        print("\n📋 To test manually:")
        print("1. Go to: https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev")
        print("2. Login with: admin / surveydash2024")
        print("3. Wait for Chart.js to load and charts to display")
        print("4. Check browser console for any errors")
    else:
        print(f"\n❌ Tests failed - chartjs_ok: {chartjs_ok}, api_ok: {api_ok}")
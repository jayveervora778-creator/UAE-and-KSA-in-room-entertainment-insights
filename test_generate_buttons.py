#!/usr/bin/env python3
"""
Test script to verify all three generate button functionalities work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_osn_processor import EnhancedOSNProcessor
from osn_wordcloud_analyzer import OSNWordCloudAnalyzer
from advanced_text_insights_analyzer import AdvancedTextInsightsAnalyzer

def test_cross_analysis():
    """Test cross-analysis functionality"""
    print("🧪 Testing Cross-Analysis Generate Button...")
    
    processor = EnhancedOSNProcessor()
    success = processor.load_data()
    
    if not success:
        print("❌ Failed to load data")
        return False
    
    # Get stats to find questions with options
    stats = processor.get_summary_stats()
    response_options = stats.get('response_options', {})
    
    # Build proper questions list like the dashboard does
    question_definitions = {
        'A1': ('Nationality', 'Nationality'),
        'A2': ('What was the primary purpose of your visit?', 'Visit Purpose'),
        'A3': ('How many times have you stayed in a hotel over the past year?', 'Hotel Stays Per Year'),
        'B1-A': ('What were your top 3 reasons for choosing this hotel?', 'Hotel Choice Reason 1'),
        'B2-A': ('How important is in-room entertainment in shaping your hotel experience?', 'Entertainment Importance Rating'),
        'C1': ('Did you use the in-room TV or entertainment system during your stay?', 'Used In-Room Entertainment'),
        'D1': ('Do you currently subscribe to any streaming platforms?', 'D1/1'),
        'D2': ('Would you prefer access to your own streaming accounts in hotel?', 'Streaming Account Preference'),
        'D3': ('Would you be willing to pay for enhanced in-room entertainment?', 'Willingness to Pay for Enhancement'),
        'D4': ('What price range per day would be acceptable?', 'Acceptable Price Range')
    }
    
    proper_questions = []
    for code, (question_text, column_name) in question_definitions.items():
        if code in response_options and column_name in processor.data.columns:
            proper_questions.append(column_name)
    
    if len(proper_questions) < 2:
        print("❌ Need at least 2 questions for cross-analysis")
        print(f"   Found questions: {proper_questions}")
        return False
    
    # Test with first two questions
    question1 = proper_questions[0]
    question2 = proper_questions[1]
    
    print(f"   Testing: {question1} vs {question2}")
    
    # Test filters
    crosstab_filters = {
        'countries': ['UAE', 'KSA'],
        'nationalities': [],
        'purposes': [],
        'frequency': []
    }
    
    try:
        result = processor.get_cross_tabulation(question1, question2, crosstab_filters)
        
        if result and result.get('combinations'):
            print(f"✅ Cross-Analysis SUCCESS: {result['total_responses']} responses, {len(result['combinations'])} combinations")
            return True
        else:
            print("❌ Cross-Analysis returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Cross-Analysis ERROR: {str(e)}")
        return False

def test_word_cloud():
    """Test word cloud functionality"""
    print("\n🧪 Testing Word Cloud Generate Button...")
    
    processor = EnhancedOSNProcessor()
    success = processor.load_data()
    
    if not success:
        print("❌ Failed to load data")
        return False
    
    # Get text questions
    stats = processor.get_summary_stats()
    text_questions = stats['text_questions']
    
    if not text_questions:
        print("❌ No text questions available")
        return False
    
    # Test with first text question
    selected_text_question = text_questions[0]
    print(f"   Testing: {selected_text_question}")
    
    text_filters = {
        'countries': ['UAE', 'KSA'],
        'nationalities': [],
        'purposes': [],
        'frequency': []
    }
    
    try:
        text_responses = processor.get_text_responses_for_wordcloud(selected_text_question, text_filters)
        
        if text_responses:
            print(f"✅ Text extraction SUCCESS: {len(text_responses)} responses")
            
            # Test word cloud generation
            wordcloud_analyzer = OSNWordCloudAnalyzer()
            wordcloud_results = wordcloud_analyzer.generate_wordcloud_data(
                text_responses,
                max_words=50,
                osn_focus=True
            )
            
            if wordcloud_results and wordcloud_results.get('word_frequency'):
                print(f"✅ Word Cloud SUCCESS: {len(wordcloud_results['word_frequency'])} unique words")
                return True
            else:
                print("❌ Word Cloud generation failed")
                return False
        else:
            print("❌ No text responses found")
            return False
            
    except Exception as e:
        print(f"❌ Word Cloud ERROR: {str(e)}")
        return False

def test_advanced_insights():
    """Test advanced insights functionality"""
    print("\n🧪 Testing Advanced Insights Generate Button...")
    
    processor = EnhancedOSNProcessor()
    success = processor.load_data()
    
    if not success:
        print("❌ Failed to load data")
        return False
    
    # Get filtered data using the same method as dashboard
    filters = {
        'countries': ['UAE', 'KSA'],
        'nationalities': [],
        'purposes': [],
        'frequency': []
    }
    
    filtered_data = processor.get_filtered_data(
        country_filter=filters.get('countries'),
        nationality_filter=filters.get('nationalities'),
        purpose_filter=filters.get('purposes'),
        frequency_filter=filters.get('frequency')
    )
    
    if len(filtered_data) <= 10:
        print(f"❌ Need more than 10 responses for insights, got {len(filtered_data)}")
        return False
    
    # Get text questions
    stats = processor.get_summary_stats()
    text_questions = stats['text_questions']
    
    if not text_questions:
        print("❌ No text questions available")
        return False
    
    print(f"   Testing with {len(filtered_data)} responses and {len(text_questions)} text questions")
    
    try:
        insights_analyzer = AdvancedTextInsightsAnalyzer()
        insights_report = insights_analyzer.generate_comprehensive_insights_report(
            filtered_data, 
            text_questions
        )
        
        if insights_report and 'error' not in insights_report:
            print(f"✅ Advanced Insights SUCCESS: {insights_report.get('total_responses_analyzed', 0)} responses analyzed")
            return True
        else:
            print("❌ Advanced Insights returned error or no results")
            if insights_report:
                print(f"   Error details: {insights_report.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Advanced Insights ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing All Generate Button Functionalities\n")
    
    results = []
    
    # Test 1: Cross-Analysis
    results.append(("Cross-Analysis", test_cross_analysis()))
    
    # Test 2: Word Cloud
    results.append(("Word Cloud", test_word_cloud()))
    
    # Test 3: Advanced Insights
    results.append(("Advanced Insights", test_advanced_insights()))
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY:")
    print("=" * 40)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    if all_passed:
        print("🎉 ALL GENERATE BUTTONS ARE WORKING!")
    else:
        print("⚠️  SOME GENERATE BUTTONS NEED FIXES")
    
    return all_passed

if __name__ == "__main__":
    main()
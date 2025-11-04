#!/usr/bin/env python3
"""
OSN Word Cloud Analyzer
Advanced text analysis for OSN survey responses with intelligent filtering and visualization
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
import warnings

warnings.filterwarnings('ignore')

class OSNWordCloudAnalyzer:
    """
    Word cloud analyzer specifically designed for OSN guest survey insights
    """
    
    def __init__(self):
        self.osn_keywords = {
            'entertainment': ['entertainment', 'stream', 'movie', 'show', 'tv', 'netflix', 'content', 'video', 'film'],
            'experience': ['experience', 'service', 'quality', 'satisfaction', 'enjoy', 'comfort', 'convenience'],
            'hotel': ['hotel', 'room', 'stay', 'accommodation', 'hospitality', 'amenity', 'facility'],
            'technology': ['technology', 'tech', 'digital', 'online', 'internet', 'wifi', 'connection', 'device'],
            'preferences': ['prefer', 'like', 'want', 'need', 'choice', 'option', 'favorite', 'love', 'enjoy'],
            'issues': ['problem', 'issue', 'difficulty', 'trouble', 'poor', 'bad', 'slow', 'broken', 'fail']
        }
        
        self.stopwords = {
            'english': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
                       'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 
                       'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'i', 'you', 
                       'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 
                       'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'am', 'very', 
                       'so', 'too', 'now', 'then', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 
                       'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
                       'not', 'only', 'own', 'same', 'than', 'too', 'yes'],
            'arabic': ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'ان', 'أن', 'كان', 'كانت'],
            'common': ['good', 'great', 'nice', 'ok', 'okay', 'fine', 'well', 'best', 'better', 'much', 'many', 'get', 'got']
        }
    
    def preprocess_text(self, text_list, min_word_length=3, remove_numbers=True):
        """
        Preprocess text for word cloud analysis
        """
        if not text_list:
            return []
        
        processed_words = []
        
        for text in text_list:
            if pd.isna(text) or not str(text).strip():
                continue
            
            # Convert to string and lowercase
            text_str = str(text).lower().strip()
            
            # Remove special characters and extra whitespace
            text_str = re.sub(r'[^\w\s]', ' ', text_str)
            text_str = re.sub(r'\s+', ' ', text_str)
            
            # Split into words
            words = text_str.split()
            
            for word in words:
                word = word.strip()
                
                # Filter conditions
                if (len(word) >= min_word_length and 
                    word not in self.stopwords['english'] and 
                    word not in self.stopwords['arabic'] and 
                    word not in self.stopwords['common']):
                    
                    # Remove numbers if requested
                    if remove_numbers and word.isdigit():
                        continue
                    
                    # Remove mixed alphanumeric unless it contains meaningful content
                    if re.search(r'\d', word) and len(word) < 6:
                        continue
                    
                    processed_words.append(word)
        
        return processed_words
    
    def analyze_text_frequency(self, text_list, top_n=50):
        """
        Analyze word frequency in text responses
        """
        processed_words = self.preprocess_text(text_list)
        
        if not processed_words:
            return {}
        
        # Count word frequency
        word_counts = Counter(processed_words)
        
        # Get top N words
        top_words = dict(word_counts.most_common(top_n))
        
        return top_words
    
    def categorize_words_by_theme(self, word_frequency_dict):
        """
        Categorize words by OSN-relevant themes
        """
        categorized = {theme: {} for theme in self.osn_keywords.keys()}
        categorized['other'] = {}
        
        for word, frequency in word_frequency_dict.items():
            categorized_flag = False
            
            for theme, keywords in self.osn_keywords.items():
                if any(keyword in word or word in keyword for keyword in keywords):
                    categorized[theme][word] = frequency
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'][word] = frequency
        
        # Sort each category by frequency
        for theme in categorized:
            categorized[theme] = dict(sorted(categorized[theme].items(), 
                                           key=lambda x: x[1], reverse=True))
        
        return categorized
    
    def generate_wordcloud_data(self, text_list, max_words=100, osn_focus=True):
        """
        Generate word cloud data optimized for OSN insights
        """
        word_frequency = self.analyze_text_frequency(text_list, top_n=max_words*2)
        
        if not word_frequency:
            return {
                'word_frequency': {},
                'categorized': {},
                'osn_insights': "No meaningful text data found for analysis.",
                'total_responses': 0
            }
        
        # Apply OSN-focused filtering if requested
        if osn_focus:
            # Boost OSN-relevant terms
            osn_boosted = {}
            for word, freq in word_frequency.items():
                boost_factor = 1
                
                # Boost entertainment and hospitality related terms
                for theme_words in self.osn_keywords.values():
                    if any(keyword in word or word in keyword for keyword in theme_words):
                        boost_factor = 2
                        break
                
                # Boost sentiment and experience words
                experience_words = ['excellent', 'amazing', 'fantastic', 'perfect', 'wonderful', 
                                  'terrible', 'awful', 'disappointing', 'frustrating', 'impressed']
                if word in experience_words:
                    boost_factor = 3
                
                osn_boosted[word] = freq * boost_factor
            
            word_frequency = osn_boosted
        
        # Get top words for word cloud
        sorted_words = dict(sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)[:max_words])
        
        # Categorize words
        categorized = self.categorize_words_by_theme(sorted_words)
        
        # Generate insights
        insights = self._generate_text_insights(categorized, len(text_list))
        
        return {
            'word_frequency': sorted_words,
            'categorized': categorized,
            'osn_insights': insights,
            'total_responses': len(text_list)
        }
    
    def _generate_text_insights(self, categorized_words, total_responses):
        """
        Generate OSN-specific insights from text analysis
        """
        insights = []
        
        insights.append(f"📝 **Text Analysis Summary**: {total_responses} guest responses analyzed")
        
        # Entertainment insights
        if categorized_words['entertainment']:
            top_ent_word = list(categorized_words['entertainment'].keys())[0]
            ent_count = categorized_words['entertainment'][top_ent_word]
            insights.append(f"🎬 **Entertainment Focus**: '{top_ent_word}' mentioned {ent_count} times - key content priority")
        
        # Experience insights
        if categorized_words['experience']:
            top_exp_word = list(categorized_words['experience'].keys())[0]
            exp_count = categorized_words['experience'][top_exp_word]
            insights.append(f"⭐ **Guest Experience**: '{top_exp_word}' appears {exp_count} times - critical satisfaction factor")
        
        # Technology insights
        if categorized_words['technology']:
            top_tech_word = list(categorized_words['technology'].keys())[0]
            tech_count = categorized_words['technology'][top_tech_word]
            insights.append(f"💻 **Technology Focus**: '{top_tech_word}' mentioned {tech_count} times - infrastructure priority")
        
        # Issues insights
        if categorized_words['issues']:
            top_issue_word = list(categorized_words['issues'].keys())[0]
            issue_count = categorized_words['issues'][top_issue_word]
            insights.append(f"⚠️ **Service Issues**: '{top_issue_word}' flagged {issue_count} times - requires attention")
        
        # OSN strategic recommendations
        insights.append("💼 **OSN Strategic Recommendations**:")
        
        if categorized_words['entertainment']:
            insights.append("   • Prioritize entertainment content development based on guest feedback themes")
        
        if categorized_words['technology']:
            insights.append("   • Invest in technology infrastructure improvements highlighted by guests")
        
        if categorized_words['preferences']:
            insights.append("   • Customize service offerings to match expressed guest preferences")
        
        if categorized_words['issues']:
            insights.append("   • Address operational issues identified in guest feedback for competitive advantage")
        
        return "\n\n".join(insights)
    
    def export_wordcloud_format(self, word_frequency_dict, format_type="plotly"):
        """
        Export word cloud data in format suitable for visualization
        """
        if format_type == "plotly":
            # Format for Plotly word cloud
            words = list(word_frequency_dict.keys())
            frequencies = list(word_frequency_dict.values())
            
            return {
                'words': words,
                'frequencies': frequencies,
                'text': ' '.join([f"{word} " * freq for word, freq in word_frequency_dict.items()])
            }
        
        elif format_type == "simple":
            # Simple list format
            return [{'word': word, 'frequency': freq} for word, freq in word_frequency_dict.items()]
        
        return word_frequency_dict
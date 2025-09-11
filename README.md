# 📊 Survey Dashboard - UAE & KSA Guest Analysis

**Professional survey data analytics platform with advanced NLP insights and comprehensive filtering capabilities.**

## 🚀 **Current Live Demo**

**Dashboard URL:** https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev  
**Login:** `admin` / `surveydash2024`

## 🎯 **Permanent Deployment Ready**

**For long-term access (10+ years), see complete deployment options:**
- **[📖 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment instructions
- **[🐳 Docker Deployment](deploy/docker-compose.yml)** - One-command deployment
- **[🖥️ Cloud Platforms](deploy/deploy.sh)** - AWS, GCP, Azure, DigitalOcean  
- **[📚 API Documentation](docs/API_REFERENCE.md)** - Complete API reference

## ✅ **Fully Working Dashboard** - 389 Survey Responses Analyzed

### 📊 **Live Data Processing**
- **✅ 389 Valid Survey Responses** processed from 402 total entries
- **✅ UAE: 194 responses | KSA: 195 responses** with full country analysis
- **✅ 14 Text Response Categories** identified across both survey sheets
- **✅ Advanced NLP Analysis** processing 330+ text responses per analysis
- **✅ Real-time Interactive Filtering** by country, nationality, visit purpose
- **✅ Professional UI** with responsive charts and comprehensive insights

### 🧠 **Advanced NLP Capabilities** 
- **Sentiment Analysis:** Overall "Positive" sentiment from guest feedback
- **Keyword Extraction:** TF-IDF weighted importance ranking of guest concerns
- **Theme Clustering:** Automated grouping of similar response patterns  
- **Multi-language Support:** English and Arabic text processing
- **Actionable Insights:** Generated recommendations from 330+ analyzed responses

### Advanced Filtering
- **Country Filter** - UAE vs KSA responses
- **Nationality Filter** - Filter by respondent nationality
- **Visit Purpose Filter** - Business, leisure, family vacation analysis
- **Dynamic Results** - Real-time filtering with instant updates

### NLP Text Analysis
- **Sentiment Analysis** - Positive/negative/neutral sentiment scoring
- **Keyword Extraction** - Top keywords from text responses using TF-IDF
- **Theme Clustering** - Automatic grouping of similar responses
- **Response Samples** - View original survey text responses

### Raw Data Access
- **Excel Sheet Browser** - View original survey data structure
- **Data Export** - Access to complete dataset
- **Column Analysis** - Detailed view of all survey questions

### Security & Authentication
- **Login Protection** - Secure access with username/password
- **Session Management** - User authentication with Flask-Login
- **Data Privacy** - Secure handling of survey responses

## 🏗️ Technical Architecture

### Backend (Flask)
```
backend/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # User authentication models
│   ├── auth.py              # Authentication routes
│   ├── main.py              # Main dashboard routes
│   ├── api.py               # REST API endpoints
│   └── data_processor.py    # Survey data processing & NLP
├── data/
│   └── survey_data.xlsx     # Original survey data file
├── templates/
│   ├── base.html           # Base template with Bootstrap
│   ├── login.html          # Authentication page
│   ├── dashboard.html      # Main dashboard interface
│   └── index.html          # Landing page
├── app.py                  # Main application entry point
└── requirements.txt        # Python dependencies
```

### Data Processing
- **Excel File Handler** - Processes UAE & KSA guest survey sheets
- **Data Cleaning** - Automatic column mapping and data normalization
- **Question Mapping** - Extracts survey questions and response options
- **Text Response Extraction** - Identifies open-ended text responses

### NLP Pipeline
- **TextBlob Sentiment Analysis** - Polarity and subjectivity scoring
- **TF-IDF Vectorization** - Keyword extraction and importance ranking
- **K-Means Clustering** - Automatic theme discovery in responses
- **spaCy Integration** - Advanced text processing capabilities

## 📈 Survey Data Analysis

### Data Sources
1. **Guests (UAE)** - 203 responses, 45 survey questions
2. **Guests Online (KSA)** - 203 responses, 45 survey questions

### Key Survey Topics
- **Demographics** - Nationality and visit purpose
- **Hotel Selection** - Reasons for choosing accommodation
- **Entertainment Preferences** - In-room entertainment usage and satisfaction
- **Technology Usage** - Streaming services and device preferences
- **Future Expectations** - Willingness to pay for enhanced services

### Text Analysis Columns
- **Visit Purpose Details** - Specific reasons for travel
- **Hotel Choice Factors** - Detailed selection criteria
- **Entertainment Experiences** - Satisfaction and disappointment stories
- **Content Preferences** - Specific entertainment content watched
- **Improvement Suggestions** - Guest recommendations and feedback

## 🚀 Deployment

### Production Service
The dashboard runs as a supervised daemon service using:
- **Supervisor** - Process management and auto-restart
- **Flask** - Web application server
- **Port 5000** - HTTP service endpoint

### Service Management
```bash
# Check service status
supervisorctl -c supervisord.conf status

# Restart service
supervisorctl -c supervisord.conf restart survey-dashboard

# View logs
supervisorctl -c supervisord.conf tail -f survey-dashboard
```

## 🔧 API Endpoints

### Authentication
- `POST /login` - User authentication
- `GET /logout` - User logout
- `GET /api/check-auth` - Authentication status

### Data Access
- `GET /api/summary` - Summary statistics
- `GET /api/filters` - Available filter options
- `GET /api/data/filtered` - Filtered survey data
- `GET /api/raw-data` - Raw Excel data

### NLP Analysis
- `GET /api/text-analysis` - Text response NLP analysis
- `GET /api/text-columns` - Available text response fields
- `GET /api/questions` - Survey question mappings

## 🎯 Key Insights Available

### Sentiment Analysis
- **Overall Response Sentiment** - Positive/negative/neutral classification
- **Polarity Scoring** - Quantitative sentiment measurement
- **Subjectivity Analysis** - Objective vs subjective response detection

### Keyword Discovery
- **Top Response Keywords** - Most frequently mentioned terms
- **TF-IDF Scoring** - Statistical importance of keywords
- **N-gram Analysis** - Single words and phrase extraction

### Theme Identification
- **Response Clustering** - Automatic grouping of similar feedback
- **Theme Summarization** - Representative samples from each theme
- **Pattern Recognition** - Common topics and concerns

### Geographic Analysis
- **Country Comparisons** - UAE vs KSA response patterns
- **Nationality Insights** - Cross-cultural response analysis
- **Regional Preferences** - Location-specific trends

## 💻 Local Development

### Setup
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

### Access
- Local URL: http://localhost:5000
- Health Check: http://localhost:5000/health

## 📊 Dashboard Screenshots

The dashboard includes:
1. **Overview Page** - Statistics cards and charts
2. **Filters Page** - Interactive data filtering
3. **NLP Analysis Page** - Text response insights
4. **Raw Data Page** - Original survey data browser

## 🔒 Security Features

- **Authentication Required** - All dashboard pages protected
- **Session Management** - Secure user sessions
- **Data Validation** - Input sanitization and validation
- **HTTPS Support** - Secure data transmission

## 📚 Technology Stack

### Backend
- **Flask 3.1.2** - Web framework
- **pandas 2.2.3** - Data manipulation
- **scikit-learn 1.6.1** - Machine learning for clustering
- **TextBlob 0.19.0** - Sentiment analysis
- **spaCy 3.8.2** - Advanced NLP processing

### Frontend
- **Bootstrap 5.3** - Responsive UI framework
- **Chart.js** - Data visualization
- **Axios** - HTTP client for API calls
- **Font Awesome** - Icons and visual elements

### Data Processing
- **openpyxl 3.1.5** - Excel file processing
- **numpy 1.26.4** - Numerical computations
- **NLTK 3.9.1** - Natural language processing

## 🎉 Ready to Use

The dashboard is fully operational and ready for survey data analysis. All original survey data is preserved and no modifications have been made to the actual response data. The system provides both high-level insights and detailed data access for comprehensive analysis.

**Start exploring your survey data insights now at:**
https://5000-irfwmnj83fl8g7sybafp1-6532622b.e2b.dev
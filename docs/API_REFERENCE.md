# 📚 Survey Dashboard API Reference

Complete API documentation for the UAE & KSA Guest Survey Dashboard.

## 🔐 Authentication

All API endpoints require authentication via login session.

### Login
```http
POST /login
Content-Type: application/json

{
  "username": "admin",
  "password": "surveydash2024"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": "admin"
}
```

### Check Authentication Status
```http
GET /api/check-auth
```

**Response:**
```json
{
  "authenticated": true,
  "username": "admin"
}
```

### Logout
```http
GET /logout
```

## 📊 Data Endpoints

### Get Summary Statistics
```http
GET /api/summary
```

**Response:**
```json
{
  "total_responses": 389,
  "countries": {
    "UAE": 194,
    "KSA": 195
  },
  "analysis": {
    "What was the primary purpose of your visit": {
      "1": 145,
      "2": 87,
      "3": 115,
      "99": 52
    },
    "How many times have you stayed in a hotel": {
      "1": 223,
      "2": 128,
      "3": 47
    }
  }
}
```

### Get Filter Options
```http
GET /api/filters
```

**Response:**
```json
{
  "countries": ["UAE", "KSA"],
  "nationalities": ["Saudi Arabian", "Emirati", "Pakistani", "Indian", "Egyptian"],
  "visit_purpose": ["Business", "Leisure", "Family Vacation"],
  "hotel_frequency": ["1–2 times", "3–5 times", "More than 5 times"]
}
```

### Get Filtered Data
```http
GET /api/data/filtered?country=UAE&nationality=Saudi Arabian
```

**Parameters:**
- `country` (optional): Filter by country (UAE/KSA)
- `nationality` (optional): Filter by guest nationality
- `visit_purpose` (optional): Filter by visit purpose
- `hotel_frequency` (optional): Filter by hotel stay frequency

**Response:**
```json
{
  "total_records": 45,
  "applied_filters": {
    "country": "UAE",
    "nationality": "Saudi Arabian"
  },
  "columns": ["Country", "What is your nationality?", "What was the primary purpose"],
  "data": [
    {
      "Country": "UAE",
      "What is your nationality?": "Saudi Arabian",
      "What was the primary purpose": "Business"
    }
  ]
}
```

## 🧠 NLP Analysis Endpoints

### Get Text Response Columns
```http
GET /api/text-columns
```

**Response:**
```json
{
  "Guests (UAE)": [
    "Can you recall a hotel stay where entert",
    "What would have improved your rating",
    "Any suggestions to improve the in-room e"
  ],
  "Guests Online (KSA)": [
    "Can you recall a hotel stay where entert",
    "What would have improved your rating", 
    "Any suggestions to improve the in-room e"
  ]
}
```

### Analyze Text Responses
```http
GET /api/text-analysis?column=What would have improved your rating&country=UAE
```

**Parameters:**
- `column` (required): Name of text response column to analyze
- `country` (optional): Filter responses by country

**Response:**
```json
{
  "total_responses": 167,
  "sentiment_summary": {
    "average_polarity": 0.127,
    "average_subjectivity": 0.445,
    "sentiment_label": "Positive",
    "distribution": {
      "positive": 89,
      "neutral": 52,
      "negative": 26
    }
  },
  "top_keywords": [
    {"word": "entertainment", "score": 0.234},
    {"word": "tv channels", "score": 0.198},
    {"word": "streaming", "score": 0.187},
    {"word": "content", "score": 0.165}
  ],
  "themes": [
    {
      "theme_id": 1,
      "count": 67,
      "percentage": 40.1,
      "sample_texts": [
        "Better streaming services and more international channels",
        "More variety in TV channels and on-demand content",
        "Access to Netflix and other streaming platforms"
      ]
    },
    {
      "theme_id": 2, 
      "count": 45,
      "percentage": 26.9,
      "sample_texts": [
        "Faster internet connection for better streaming",
        "More reliable WiFi for entertainment streaming",
        "Better internet speed in rooms"
      ]
    }
  ],
  "sample_responses": [
    "More international TV channels and streaming services",
    "Better internet connection for streaming content",
    "Access to popular streaming platforms like Netflix"
  ],
  "insights": [
    "Strong positive sentiment indicates high satisfaction levels",
    "Key topics of concern: entertainment, streaming, channels",
    "Primary theme represents 40.1% of responses"
  ]
}
```

## 💾 Raw Data Endpoints

### Get Raw Survey Data
```http
GET /api/raw-data?sheet=Guests (UAE)
```

**Parameters:**
- `sheet` (optional): Specific sheet name, or omit for all sheets

**Response:**
```json
{
  "sheet_name": "Guests (UAE)",
  "shape": [194, 46],
  "columns": ["Country", "What is your nationality?", "What was the primary purpose"],
  "data": [
    {
      "Country": "UAE",
      "What is your nationality?": "Saudi Arabian", 
      "What was the primary purpose": "Business"
    }
  ],
  "questions": {
    "What is your nationality?": {
      "question": "What is your nationality?",
      "options": "Open text response",
      "original_column": "A1"
    }
  }
}
```

### Get Question Mappings
```http
GET /api/questions
```

**Response:**
```json
{
  "Guests (UAE)": {
    "What is your nationality?": {
      "question": "What is your nationality?", 
      "options": "Open text response",
      "original_column": "A1"
    },
    "What was the primary purpose of your visit": {
      "question": "What was the primary purpose of your visit?",
      "options": "1. Business\n2. Leisure\n3. Family Vacation\n99. Other",
      "original_column": "A2"
    }
  },
  "Guests Online (KSA)": {
    // Similar structure
  }
}
```

## ❤️ Health Check

### Health Status
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "survey-dashboard", 
  "version": "1.0.0"
}
```

## 🔄 Error Responses

### Authentication Error
**HTTP 401 Unauthorized**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

### Missing Parameters
**HTTP 400 Bad Request**  
```json
{
  "error": "Column parameter required"
}
```

### Server Error
**HTTP 500 Internal Server Error**
```json
{
  "error": "Data processor not available"
}
```

### Analysis Error
**HTTP 200 OK** (with error in response)
```json
{
  "error": "No text responses found for column: invalid_column"
}
```

## 📈 Rate Limits

- **Login:** 5 requests per minute per IP
- **API calls:** 30 requests per minute per IP  
- **Text analysis:** 10 requests per minute per user

## 🔧 Data Processing Details

### Survey Data Processing
- **Total Original Responses:** 402 (203 UAE + 203 KSA)
- **Valid Processed Responses:** 389 (194 UAE + 195 KSA)
- **Text Response Fields:** 7 per survey sheet
- **Question Categories:** 21 mapped questions per sheet

### NLP Analysis Capabilities
- **Sentiment Analysis:** TextBlob polarity and subjectivity scoring
- **Keyword Extraction:** TF-IDF vectorization with 1-3 word ngrams  
- **Theme Clustering:** K-means clustering (2-5 clusters based on data size)
- **Language Support:** English and Arabic text processing
- **Response Filtering:** Automatic removal of coded/invalid responses

### Performance Specifications
- **API Response Time:** < 2 seconds for data endpoints
- **NLP Analysis Time:** < 5 seconds for 300+ text responses
- **Concurrent Users:** 50+ with 2GB RAM
- **Data Cache:** In-memory caching for improved performance

## 🎯 Usage Examples

### JavaScript/Fetch API
```javascript
// Login
const loginResponse = await fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'surveydash2024' })
});

// Get summary
const summaryResponse = await fetch('/api/summary');
const summary = await summaryResponse.json();

// Analyze text
const analysisResponse = await fetch('/api/text-analysis?column=What would have improved your rating');
const analysis = await analysisResponse.json();
```

### Python/Requests
```python
import requests

# Login
session = requests.Session()
session.post('http://localhost:5000/login', json={
    'username': 'admin', 
    'password': 'surveydash2024'
})

# Get data
summary = session.get('http://localhost:5000/api/summary').json()
filters = session.get('http://localhost:5000/api/filters').json()

# NLP analysis
analysis = session.get('http://localhost:5000/api/text-analysis', params={
    'column': 'What would have improved your rating',
    'country': 'UAE'
}).json()
```

### cURL Examples
```bash
# Login and save session
curl -c cookies.txt -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"surveydash2024"}'

# Get summary with session
curl -b cookies.txt http://localhost:5000/api/summary

# Filtered data 
curl -b cookies.txt "http://localhost:5000/api/data/filtered?country=UAE&nationality=Saudi Arabian"

# Text analysis
curl -b cookies.txt "http://localhost:5000/api/text-analysis?column=What would have improved your rating"
```

---

## 📝 Notes

- All timestamps are in UTC
- Text responses are automatically cleaned and validated
- Large datasets are paginated for performance
- API responses include caching headers
- Error messages provide actionable troubleshooting information

**Complete API access for comprehensive survey data analysis! 📊**
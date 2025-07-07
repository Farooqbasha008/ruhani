# RUHANI Backend

A FastAPI-based backend for RUHANI - a culturally-inspired, invisible voice-based AI psychologist for enterprise employees.

## 🚀 Features

- **Voice-Based Therapy Sessions**: Real-time audio processing with Groq STT/LLM and ElevenLabs TTS
- **Sentiment Analysis**: AI-powered emotional state analysis
- **Wellness Tracking**: Comprehensive employee wellness monitoring
- **HR Analytics**: Organizational insights and risk assessment
- **Cultural Sensitivity**: Culturally-aware AI responses
- **HIPAA Compliance**: Secure data handling and privacy protection
- **Real-time Processing**: Async API endpoints for optimal performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   AI Services   │
│   (React)       │◄──►│   Backend       │◄──►│   (Groq,        │
│                 │    │                 │    │   ElevenLabs)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Snowflake     │
                       │   Database      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Coral         │
                       │   Protocol      │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Snowflake account
- API keys for:
  - [Groq](https://console.groq.com/) (LLM & STT)
  - [ElevenLabs](https://elevenlabs.io/) (TTS)
  - [Fetch.ai](https://console.fetch.ai/) (Public info)
  - [Coral Protocol](https://coralprotocol.com/) (Activity logging)

## 🛠️ Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and database credentials
   ```

4. **Set up Snowflake database:**
   ```bash
   # Run the schema file in your Snowflake console
   # Or use Snowflake CLI
   snowsql -f database_schema.sql
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
GROQ_API_KEY=your-groq-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
FETCHAI_API_KEY=your-fetchai-api-key
CORAL_API_KEY=your-coral-protocol-api-key

# Database
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_WAREHOUSE=your-warehouse
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=your-schema
SNOWFLAKE_ROLE=your-role
```

### Database Setup

1. Create a Snowflake account
2. Run the `database_schema.sql` file to create tables and views
3. Update your `.env` file with Snowflake credentials

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Employee Endpoints
- `POST /employee/onboard` - Onboard new employee
- `POST /employee/voice-session` - Process voice therapy session
- `POST /employee/wellness-check` - Submit wellness assessment
- `GET /employee/profile/{employee_id}` - Get employee profile
- `GET /employee/wellness-summary/{employee_id}` - Get wellness summary

#### HR Endpoints
- `GET /hr/insights` - Get organizational insights
- `GET /hr/trends` - Get wellness trends
- `GET /hr/at-risk` - Get at-risk employees
- `GET /hr/employees` - Get all employees

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. **Employee tokens**: Created during onboarding
2. **HR tokens**: Created for dashboard access
3. **Token expiration**: 30 minutes (configurable)

### Example Usage

```bash
# Employee onboarding
curl -X POST "http://localhost:8000/employee/onboard" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "department": "Engineering",
    "role": "Software Engineer"
  }'

# Voice session (with token)
curl -X POST "http://localhost:8000/employee/voice-session" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "audio_data": "base64-encoded-audio",
    "mood_rating": "4"
  }'
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

## 📊 Data Flow

1. **Employee Onboarding**:
   - Employee data stored in Snowflake
   - Public info gathered via Fetch.ai
   - JWT token generated

2. **Voice Session**:
   - Audio transcribed via Groq STT
   - Sentiment analyzed via Groq LLM
   - AI response generated
   - Voice response created via ElevenLabs
   - Session logged to Snowflake
   - Activity logged to Coral Protocol

3. **HR Analytics**:
   - Data queried from Snowflake
   - Insights generated
   - Risk assessment performed
   - Recommendations provided

## 🔒 Security & Compliance

- **HIPAA Compliance**: All data handling follows HIPAA guidelines
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configured for specific origins
- **Data Encryption**: Sensitive data encrypted in transit and at rest
- **Audit Logging**: All activities logged via Coral Protocol

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t ruhani-backend .
docker run -p 8000:8000 ruhani-backend
```

## 📈 Monitoring

- **Health Check**: `GET /health`
- **Service Status**: `GET /`
- **Logs**: Check application logs for errors
- **Database**: Monitor Snowflake query performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please contact the development team or create an issue in the repository. 
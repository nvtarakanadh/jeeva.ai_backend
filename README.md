# Jeeva AI Backend

This is the Django backend for the Jeeva AI healthcare application, providing AI-powered analysis of medical records and prescriptions.

## Features

- **Prescription Analysis**: Upload prescription images and get AI-powered analysis using Google Gemini
- **Health Record Analysis**: Analyze various types of health records with AI insights
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Configured for frontend communication
- **Database Models**: Structured storage for health records and AI analysis results

## Setup

### Prerequisites

- Python 3.8+
- Django 5.2+
- API Keys for:
  - Google Gemini AI
  - Firecrawl (optional, for enhanced medicine information)

### Installation

1. **Clone and navigate to the backend directory:**
   ```bash
   cd Jeeva_AI_BackEnd
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   copy env_example.txt .env
   
   # Edit .env with your actual values:
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   GEMINI_API_KEY=your-gemini-api-key-here
   FIRECRAWL_API_KEY=your-firecrawl-api-key-here
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver 8000
   ```

The API will be available at `http://localhost:8000/api/ai/`

## API Endpoints

### Health Check
- **GET** `/api/ai/health/` - Check if the backend is running

### Prescription Analysis
- **POST** `/api/ai/analyze/prescription/` - Analyze prescription image
  - Body: FormData with `image` file
  - Optional: `title`, `description`, `patient_id`, `uploaded_by`

### Health Record Analysis
- **POST** `/api/ai/analyze/health-record/` - Analyze health record data
  - Body: JSON with record details

### Get Analysis
- **GET** `/api/ai/analysis/{record_id}/` - Get analysis for specific record

### List Analyses
- **GET** `/api/ai/analyses/` - List all analyses

## API Usage Examples

### Analyze Prescription
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('title', 'Prescription Analysis');

const response = await fetch('http://localhost:8000/api/ai/analyze/prescription/', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
```

### Analyze Health Record
```javascript
const response = await fetch('http://localhost:8000/api/ai/analyze/health-record/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Lab Results',
    description: 'Blood test results',
    recordType: 'lab_test',
    serviceDate: '2024-01-15T10:00:00Z',
    patientId: 'patient-123',
    uploadedBy: 'doctor-456'
  }),
});

const result = await response.json();
```

## Database Models

### HealthRecord
- `id`: Primary key
- `patient_id`: Patient identifier
- `record_type`: Type of health record
- `title`: Record title
- `description`: Record description
- `file_url`: URL to uploaded file
- `file_name`: Original filename
- `file_type`: File type/extension
- `record_date`: Date of the record
- `uploaded_at`: Upload timestamp
- `uploaded_by`: User who uploaded
- `metadata`: Additional JSON data

### AIAnalysis
- `id`: Primary key
- `record_id`: Reference to health record
- `summary`: AI analysis summary
- `key_findings`: Array of key findings
- `risk_warnings`: Array of risk warnings
- `recommendations`: Array of recommendations
- `confidence`: Confidence score (0-1)
- `analysis_type`: Type of analysis performed
- `processed_at`: Analysis timestamp
- `record_title`: Title of analyzed record

## Configuration

### Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `GEMINI_API_KEY`: Google Gemini AI API key
- `FIRECRAWL_API_KEY`: Firecrawl API key (optional)
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of CORS origins

### CORS Configuration

The backend is configured to allow requests from the frontend. Update `CORS_ALLOWED_ORIGINS` in your `.env` file to include your frontend URL.

## Development

### Running Tests
```bash
python manage.py test
```

### Admin Interface
Access the Django admin at `http://localhost:8000/admin/` after creating a superuser.

### API Documentation
The API follows RESTful conventions. Use tools like Postman or curl to test endpoints.

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Use a production database (PostgreSQL recommended)
3. Set up proper CORS origins
4. Use a production WSGI server (Gunicorn)
5. Set up reverse proxy (Nginx)
6. Configure static file serving
7. Set up SSL/TLS certificates

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check `CORS_ALLOWED_ORIGINS` in your `.env` file
2. **API Key Errors**: Ensure `GEMINI_API_KEY` is set correctly
3. **Database Errors**: Run migrations with `python manage.py migrate`
4. **File Upload Issues**: Check file size limits and allowed file types

### Logs

Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## Contributing

1. Follow Django best practices
2. Add tests for new features
3. Update documentation
4. Use proper error handling
5. Follow RESTful API design principles

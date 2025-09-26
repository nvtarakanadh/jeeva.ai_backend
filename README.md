# Jeeva.AI Backend API

Django REST API backend for the Jeeva.AI health management platform.

## Features

- Patient and Doctor profile management
- Health records upload and management
- AI-powered health analytics using Gemini API
- Consent-based data sharing
- File upload support
- PostgreSQL database support

## Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-render-app.onrender.com,localhost
DATABASE_URL=postgresql://user:password@host:port/database
CORS_ALLOWED_ORIGINS=https://jeeva-ai-phi.vercel.app/,http://localhost:8080
GEMINI_API_KEY=your-gemini-api-key
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the development server:
```bash
python manage.py runserver
```

## Deployment

This project is configured for deployment on Render with:
- PostgreSQL database
- Gunicorn WSGI server
- WhiteNoise for static files
- Environment-based configuration

## API Endpoints

- `/api/profile/me/` - Profile management
- `/api/records/` - Health records CRUD
- `/api/consents/` - Consent management
- `/api/ai/insights/` - AI analytics
- `/api/records/upload/` - File upload

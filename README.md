# FastAPI Boilerplate

A production-ready FastAPI boilerplate with authentication, database integration, and security best practices.

## 🚀 Features

### Core Features
- **FastAPI Framework** - Modern, fast web framework for building APIs
- **JWT Authentication** - Secure token-based authentication
- **Google OAuth** - Social login integration
- **PostgreSQL Database** - Robust relational database with SQLAlchemy ORM
- **User Management** - Complete user CRUD operations with role-based access
- **Rate Limiting** - Protection against brute force attacks
- **Input Validation** - Comprehensive data validation and sanitization

### Security Features
- **Password Hashing** - Bcrypt password encryption
- **CORS Protection** - Configurable cross-origin resource sharing
- **Environment-based Configuration** - Secure configuration management
- **Request Logging** - Comprehensive audit trail
- **Error Handling** - Secure error responses without information leakage

### Development Features
- **Docker Support** - Containerized development and deployment
- **Database Migrations** - Alembic database version control
- **Structured Logging** - JSON-formatted logs with rotation
- **API Documentation** - Auto-generated OpenAPI/Swagger docs
- **Health Checks** - Application monitoring endpoints

## 📋 Requirements

- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   make init-db
   # or
   python init_db.py
   ```

6. **Create admin user**
   ```bash
   make create-admin
   # or
   python create_admin.py
   ```

7. **Run development server**
   ```bash
   make dev
   # or
   uvicorn app.main:app --reload
   ```

### Docker Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd fastapi2
   cp .env.example .env
   ```

2. **Start services**
   ```bash
   make up
   # or
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   make migrate
   ```

4. **View logs**
   ```bash
   make logs
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Optional |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Optional |
| `RATE_LIMIT_REQUESTS` | Rate limit requests per window | `5` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/auth/auth/google/callback` (development)
   - `https://yourdomain.com/api/auth/auth/google/callback` (production)

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login with email/password |
| `GET` | `/api/auth/google-login` | Initiate Google OAuth |
| `GET` | `/api/auth/auth/google/callback` | Google OAuth callback |
| `GET` | `/api/users/me` | Get current user profile |
| `POST` | `/api/users/` | Create new user |
| `GET` | `/health` | Health check endpoint |

## 🧪 Testing

```bash
# Run tests
make test

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## 🚀 Deployment

### Docker Production

1. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment setup**
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=false`
   - Use strong `SECRET_KEY`
   - Configure proper `ALLOWED_ORIGINS`

### Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Set strong database passwords
- [ ] Configure HTTPS in production
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Configure log rotation
- [ ] Set up monitoring and alerts

## 📁 Project Structure

```
fastapi2/
├── app/
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   ├── api.py          # API router configuration
│   │   └── deps.py         # Dependency injection
│   ├── core/
│   │   ├── config.py       # Application configuration
│   │   ├── security.py     # Security utilities
│   │   ├── logging.py      # Logging configuration
│   │   └── rate_limiter.py # Rate limiting
│   ├── db/
│   │   └── base.py         # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── main.py            # Application entry point
├── tests/                  # Test files
├── alembic/               # Database migrations
├── logs/                  # Application logs
├── docker-compose.yml     # Docker services
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── Makefile             # Development commands
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review existing issues and discussions
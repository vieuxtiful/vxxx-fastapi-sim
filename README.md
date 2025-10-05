# FastAPI Analysis Boilerplate

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready FastAPI boilerplate for building text analysis and processing APIs. This template provides a solid foundation for developing scalable analysis services with modern Python web technologies.

## Features

- 🚀 **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- 🔐 **Authentication**: JWT-based authentication with role-based access control
- 📡 **WebSocket Support**: Real-time communication for live analysis
- 📁 **File Processing**: Comprehensive file upload and processing capabilities
- 🗄️ **Database Integration**: SQLAlchemy ORM with async support
- 🔄 **Caching**: Redis integration for high-performance caching
- 📊 **Monitoring**: Built-in health checks and performance monitoring
- 🧪 **Testing**: Comprehensive test suite with pytest
- 📚 **Documentation**: Auto-generated API docs with OpenAPI/Swagger
- 🐳 **Docker Ready**: Containerized deployment configuration
- 🔧 **Development Tools**: Code formatting, linting, and type checking

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (optional, for caching)
- PostgreSQL (optional, for production database)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lexiq-team/fastapi-analysis-boilerplate.git
   cd fastapi-analysis-boilerplate
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## Project Structure

```
fastapi-analysis-boilerplate/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models for request/response
│   ├── services.py          # Business logic and service layer
│   ├── auth.py              # Authentication and authorization
│   ├── websocket.py         # WebSocket connection management
│   ├── utils.py             # Utility functions
│   ├── config.py            # Configuration management
│   └── database.py          # Database configuration
├── tests/
│   ├── __init__.py
│   ├── test_main.py         # API endpoint tests
│   ├── test_services.py     # Service layer tests
│   └── conftest.py          # Test configuration
├── docs/
│   ├── api.md               # API documentation
│   ├── deployment.md        # Deployment guide
│   └── development.md       # Development guide
├── examples/
│   ├── client_example.py    # Example API client
│   └── websocket_client.py  # WebSocket client example
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env.example            # Environment variables template
└── README.md               # This file
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/register` - User registration (if enabled)

### Analysis
- `POST /api/analyze` - Analyze text content
- `POST /api/analyze/batch` - Batch analysis of multiple texts
- `GET /api/analyze/status/{request_id}` - Get analysis status
- `WebSocket /ws/analysis` - Real-time analysis

### File Management
- `POST /api/files/upload` - Upload and process files
- `GET /api/files/{file_id}` - Get file information
- `DELETE /api/files/{file_id}` - Delete file

### Project Management
- `POST /api/projects` - Create new project
- `GET /api/projects` - Get user projects
- `GET /api/projects/{project_id}` - Get specific project
- `PUT /api/projects/{project_id}` - Update project

### Statistics & Reporting
- `GET /api/statistics` - Get analysis statistics
- `POST /api/reports/generate` - Generate custom reports

### Configuration
- `GET /api/config` - Get user configuration
- `PUT /api/config` - Update user configuration

## Usage Examples

### Basic Text Analysis

```python
import httpx

# Login to get token
login_response = httpx.post("http://localhost:8000/auth/login", json={
    "username": "your_username",
    "password": "your_password"
})
token = login_response.json()["data"]["token"]

# Analyze text
headers = {"Authorization": f"Bearer {token}"}
analysis_response = httpx.post(
    "http://localhost:8000/api/analyze",
    headers=headers,
    json={
        "content": "This is a sample text for analysis.",
        "language": "en",
        "domain": "general",
        "options": {
            "include_spelling_check": True,
            "include_grammar_check": False,
            "confidence_threshold": 0.5
        }
    }
)

result = analysis_response.json()
print(f"Analysis completed: {len(result['terms'])} terms analyzed")
```

### File Upload and Processing

```python
import httpx

headers = {"Authorization": f"Bearer {token}"}

# Upload file
with open("document.txt", "rb") as f:
    files = {"file": ("document.txt", f, "text/plain")}
    upload_response = httpx.post(
        "http://localhost:8000/api/files/upload",
        headers=headers,
        files=files,
        data={"file_type": "document"}
    )

file_info = upload_response.json()
print(f"File uploaded: {file_info['data']['file_id']}")
```

### WebSocket Real-time Analysis

```python
import asyncio
import websockets
import json

async def realtime_analysis():
    uri = "ws://localhost:8000/ws/analysis"
    
    async with websockets.connect(uri) as websocket:
        # Send text for analysis
        await websocket.send(json.dumps({
            "content": "Real-time analysis text",
            "language": "en",
            "domain": "general"
        }))
        
        # Receive results
        response = await websocket.recv()
        result = json.loads(response)
        print(f"Real-time result: {result}")

asyncio.run(realtime_analysis())
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Application
APP_NAME=Analysis API
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
# For SQLite: DATABASE_URL=sqlite+aiosqlite:///./app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIRECTORY=uploads

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
```

### Customizing the Analysis Engine

Replace the placeholder analysis logic in `app/services.py`:

```python
class AnalysisService(BaseService):
    async def _analyze_terms(self, content, language, domain, options):
        # Replace this with your actual analysis engine
        # Example: integrate with spaCy, transformers, or custom models
        
        # Your analysis logic here
        terms = []
        # ... your implementation
        
        return terms
```

## Development

### Setting up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run tests**
   ```bash
   pytest
   ```

4. **Code formatting**
   ```bash
   black app/
   isort app/
   ```

5. **Type checking**
   ```bash
   mypy app/
   ```

### Running with Docker

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run specific services**
   ```bash
   docker-compose up api redis postgres
   ```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

### Test Structure

- `tests/test_main.py` - API endpoint tests
- `tests/test_services.py` - Service layer tests
- `tests/test_auth.py` - Authentication tests
- `tests/conftest.py` - Test fixtures and configuration

## Deployment

### Production Deployment

1. **Using Docker**
   ```bash
   docker build -t analysis-api .
   docker run -p 8000:8000 analysis-api
   ```

2. **Using Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Environment Setup**
   - Set `DEBUG=False`
   - Use production database (PostgreSQL)
   - Configure Redis for caching
   - Set up proper logging
   - Configure reverse proxy (nginx)

### Health Monitoring

The application includes built-in health checks:

- `/health` - Overall application health
- Service-specific health checks for database, Redis, etc.
- Prometheus metrics endpoint (optional)

## Customization

### Adding New Endpoints

1. **Define models in `app/models.py`**
   ```python
   class NewRequest(BaseModel):
       data: str
       options: Optional[Dict[str, Any]] = None
   ```

2. **Implement service logic in `app/services.py`**
   ```python
   async def new_service_method(self, data: str) -> Dict[str, Any]:
       # Your logic here
       return {"result": "processed"}
   ```

3. **Add endpoint in `app/main.py`**
   ```python
   @app.post("/api/new-endpoint")
   async def new_endpoint(request: NewRequest):
       result = await service.new_service_method(request.data)
       return create_response(success=True, data=result)
   ```

### Integrating ML Models

```python
# In app/services.py
import torch
from transformers import AutoModel, AutoTokenizer

class AnalysisService(BaseService):
    async def initialize(self):
        await super().initialize()
        # Load your ML models
        self.model = AutoModel.from_pretrained("model-name")
        self.tokenizer = AutoTokenizer.from_pretrained("model-name")
    
    async def analyze_with_ml(self, text: str):
        # Your ML inference logic
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        return outputs
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/lexiq-team/fastapi-analysis-boilerplate/issues)
3. Create a [new issue](https://github.com/lexiq-team/fastapi-analysis-boilerplate/issues/new)

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Redis](https://redis.io/) - Caching and session storage

# Medical Document Management System

A secure and scalable Flask-based backend for managing medical documents with role-based access control, document storage, and AI-powered summarization.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Patient, Admin, Staff)
  - Secure password hashing with bcrypt

- **Document Management**
  - Secure document upload and storage using AWS S3
  - Document summarization using OpenAI's GPT model
  - Support for various document formats (PDF, images, text)

- **User Management**
  - User registration and profile management
  - Patient profile creation
  - Admin controls and system statistics

- **Security**
  - HTTPS enforcement
  - Secure file storage
  - Comprehensive audit logging
  - HIPAA-compliant architecture

## Tech Stack

- **Backend Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Task Queue**: Celery with Redis
- **File Storage**: AWS S3
- **AI Integration**: OpenAI GPT
- **Deployment**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose
- AWS Account with S3 access
- OpenAI API key
- Python 3.11+

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd medical-docs-backend
   ```

2. Create and configure the environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. Initialize the database:
   ```bash
   docker-compose exec web flask db upgrade
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and receive JWT
- `POST /auth/logout` - Logout and invalidate token
- `POST /auth/refresh` - Refresh access token

### User Management
- `GET /users/me` - Get current user details
- `GET /users/{id}` - Get user details (Admin only)
- `DELETE /users/{id}` - Delete user (Admin only)

### Document Management
- `POST /documents/upload` - Upload medical document
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document
- `GET /patients/{id}/documents` - Get patient's documents
- `POST /documents/{id}/summarize` - Generate document summary

### Admin Controls
- `GET /admin/stats` - Get system statistics
- `GET /admin/logs` - View audit logs

## Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run development server:
   ```bash
   flask run
   ```

4. Run Celery worker:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

## Testing

Run the test suite:
```bash
pytest
```

## Deployment

1. Update environment variables in `.env`
2. Build and deploy using Docker Compose:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

## Security Considerations

- All sensitive data is encrypted at rest and in transit
- AWS S3 bucket should be configured with appropriate permissions
- API keys and credentials should be securely managed
- Regular security audits and updates are recommended

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
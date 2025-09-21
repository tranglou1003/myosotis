# Myosotis 🌸
### Alzheimer Support System for Patients and Caregivers

[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#copyright)

Myosotis is a modern web application designed to support Alzheimer's patients and their caregivers with daily care management tools, memory aids, and family communication features. The system integrates advanced AI technology to create personalized experiences and optimal support.

## ✨ Key Features

### 🧠 Cognitive Support
- **MMSE Assessment**: Regular cognitive function evaluation
- **Memory Games**: Sudoku, Picture Recall, Memory Map
- **Progress Tracking**: Monitor health trends and improvements
- **Detailed Reports**: Charts and data analysis

### 🤖 AI Clone & Chatbot
- **AI Avatar**: Generate video avatars from voice and images
- **Voice Cloning**: Vietnamese and English voice synthesis
- **Smart Chatbot**: 24/7 AI-powered conversation support
- **Talking Face**: Natural conversation video generation

### 👥 User Management
- **Authentication**: Secure JWT-based login/registration
- **Personal Profiles**: User information management
- **Emergency Contacts**: Critical contact lists
- **Caregiver Guides**: Documentation and advice

### 🌐 Multilingual & Accessibility
- **Multilingual Support**: Vietnamese and English
- **Accessibility**: WCAG 2.1 AA compliant
- **Responsive Design**: Optimized for all devices
- **Session Management**: 24-hour session handling

## 🏗️ System Architecture

```mermaid
graph TB
    A[Frontend React] --> B[Backend FastAPI]
    A --> C[AI Clone Service]
    B --> D[PostgreSQL Database]
    B --> E[Static Assets]
    C --> F[Voice Clone TTS]
    C --> G[Sonic Talking Face]
    F --> H[Vietnamese TTS]
    F --> I[English TTS]
    G --> J[Video Generation]
```

## 📁 Project Structure

```
myosotis/
├── 🌐 frontend/                    # React TypeScript Application
│   ├── src/
│   │   ├── features/              # Feature modules (auth, ai-clone, chatbot)
│   │   ├── pages/                 # Page components
│   │   ├── components/            # Reusable UI components
│   │   ├── api/                   # API integration
│   │   └── locales/               # i18n translations
│   ├── package.json
│   └── Dockerfile
├── 🔧 backend/
│   ├── service/                   # Main FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/              # API routes (v1, v2)
│   │   │   ├── models/           # SQLAlchemy models
│   │   │   ├── services/         # Business logic
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── core/             # Configuration & security
│   │   ├── static/               # Media assets (images, audio, video)
│   │   ├── alembic/              # Database migrations
│   │   └── docker-compose.yml
│   └── ai_clone/                 # AI Clone Service
│       ├── app/                  # FastAPI AI service
│       └── ai_service/           # AI model implementations
│           ├── voiceclone_tts/   # Voice cloning service
│           └── Sonic/            # Talking face generation
└── 📚 README.md
```

## 🚀 Installation and Setup

### System Requirements

- **Node.js**: 18+
- **Python**: 3.10+
- **Docker & Docker Compose**: Latest
- **GPU**: NVIDIA RTX 4090+ (for AI Clone Service)
- **RAM**: 32GB+ (recommended)
- **Storage**: 100GB+ free space

### 1. Clone Repository

```bash
git clone https://github.com/your-org/myosotis.git
cd myosotis
```

### 2. Setup Frontend

```bash
cd frontend
npm install --legacy-peer-deps

# Create environment file
cp .env.example .env.local
# Update VITE_API_URL in .env.local

# Start development server
npm run dev
```

Frontend will run at: http://localhost:5173

### 3. Setup Backend Service

```bash
cd backend/service

# Create environment file
cp .env.example .env
# Update environment variables in .env

# Run with Docker
docker compose up -d --build
```

Backend API will run at: http://localhost:8777

### 4. Setup AI Clone Service

```bash
cd backend/ai_clone

# Run with Docker (requires GPU)
docker compose up -d --build
```

AI Clone Service will run at: http://localhost:8779

## 🔧 Environment Configuration

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8777
VITE_AI_CLONE_URL=http://localhost:8779
VITE_APP_NAME=Myosotis
VITE_APP_VERSION=1.0.0
```

### Backend Service (.env)
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=seadev
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/seadev
API_PREFIX=/api
PROJECT_NAME=Myosotis Backend
DEBUG=true
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### AI Clone Service (.env)
```env
API_HOST=0.0.0.0
API_PORT=8779
CUDA_VISIBLE_DEVICES=0
MAX_CONCURRENT_JOBS=4
TEMP_DIR=./temp_clone
PUBLIC_DIR=./public/human_clone
```

## 📊 API Documentation

### Backend Service
- **Swagger UI**: http://localhost:8777/docs
- **ReDoc**: http://localhost:8777/redoc
- **OpenAPI JSON**: http://localhost:8777/api/openapi.json

### AI Clone Service
- **Swagger UI**: http://localhost:8779/docs
- **ReDoc**: http://localhost:8779/redoc

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm run test
npm run lint
npm run type-check
```

### Backend Testing
```bash
cd backend/service
pytest -q
```

### AI Clone Testing
```bash
cd backend/ai_clone
# Test health endpoint
curl http://localhost:8779/health

# Test voice clone
curl -X POST http://localhost:8779/ai/human-clone/generate \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/vietnamese_request.json
```

## 🚀 Production Deployment

### Docker Compose Production
```bash
# Backend Service
cd backend/service
docker compose -f docker-compose.prod.yml up -d

# AI Clone Service
cd backend/ai_clone
docker compose -f docker-compose.prod.yml up -d

# Frontend (build static)
cd frontend
npm run build
# Serve static files with nginx
```

### Environment Variables for Production
```env
# Backend
DEBUG=false
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
DATABASE_URL=postgresql+psycopg2://user:pass@prod-db:5432/myosotis

# AI Clone
MAX_CONCURRENT_JOBS=2
CLEANUP_INTERVAL=3600
```

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Comprehensive data validation
- **Rate Limiting**: API rate limiting protection
- **File Upload Security**: Secure file handling
- **HTTPS**: SSL/TLS encryption in production

## 📈 Performance

### Frontend
- **Bundle Size**: Optimized with Vite
- **Code Splitting**: Lazy loading for better performance
- **Caching**: Efficient state management with Zustand
- **Accessibility**: WCAG 2.1 AA compliant

### Backend
- **Async Processing**: Non-blocking operations
- **Database Optimization**: Efficient queries with SQLAlchemy
- **Caching**: Redis caching for frequently accessed data
- **Load Balancing**: Horizontal scaling support

### AI Clone Service
- **GPU Acceleration**: NVIDIA CUDA optimization
- **Model Caching**: Efficient model loading and caching
- **Concurrent Processing**: Multiple job processing
- **Memory Management**: Optimized GPU memory usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- **Code Style**: Follow ESLint and Prettier configurations
- **Testing**: Maintain test coverage above 80%
- **Documentation**: Update README and API docs
- **Accessibility**: Ensure WCAG 2.1 AA compliance

## 📋 Roadmap

### Version 1.1.0 (Q4 2025)
- [ ] **Mobile App**: React Native mobile application
- [ ] **Advanced Analytics**: Detailed health analytics dashboard
- [ ] **Family Portal**: Enhanced family communication features
- [ ] **Voice Commands**: Voice-controlled interface

### Version 1.2.0 (Q1 2026)
- [ ] **IoT Integration**: Smart home device integration
- [ ] **Wearable Support**: Smartwatch and fitness tracker integration
- [ ] **Advanced AI**: More sophisticated AI conversation models
- [ ] **Multi-language**: Support for additional languages

### Version 2.0.0 (Q2 2026)
- [ ] **Real-time Monitoring**: Live health monitoring
- [ ] **Predictive Analytics**: AI-powered health predictions
- [ ] **Telemedicine**: Integrated video consultation
- [ ] **Enterprise Features**: Multi-tenant support

## 🐛 Troubleshooting

### Common Issues

#### Frontend Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Check environment variables
cat .env.local
```

#### Backend Issues
```bash
# Check database connection
docker compose logs db

# Reset database
docker compose down -v
docker compose up -d --build
```

#### AI Clone Issues
```bash
# Check GPU availability
nvidia-smi

# Monitor GPU memory
nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1

# Check service logs
docker compose logs ai-clone
```

## 📞 Support

### Documentation
- **API Docs**: Available at `/docs` endpoints
- **Component Library**: Storybook documentation
- **Architecture**: Detailed system architecture docs

### Contact Information

## 📜 License

**© 2025 Myosotis Team. All Rights Reserved.**

This software and associated documentation files (the "Software") are proprietary and confidential. The Software is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties.

### License Terms
- **Proprietary License**: This Software is licensed, not sold
- **Restricted Use**: Licensed for internal business use only
- **No Distribution**: Redistribution in any form is prohibited
- **No Modification**: Modification of source code is restricted
- **Commercial Use**: Contact licensing@seadev.com for commercial licensing

---
Contact Information
Myosotis Team

*This README was last updated on September 16, 2025*

# MatchWise AI - AI-Powered Resume Matching Platform

## 🚀 Project Overview

MatchWise AI is an intelligent resume comparison platform that uses AI to analyze job postings and optimize resumes for specific positions. The platform provides comprehensive job application assistance including resume analysis, cover letter generation, and matching scores.

## ✨ Features

### Core Functionality
- **AI Resume Analysis**: Intelligent comparison between resume and job requirements
- **Job Posting Scraping**: Automatic extraction of job details from URLs
- **Matching Score**: Percentage-based compatibility assessment
- **Tailored Resume Summary**: AI-generated resume optimization suggestions
- **Custom Work Experience**: Enhanced experience descriptions for specific roles
- **Cover Letter Generation**: Professional cover letters tailored to job postings
- **Visitor Counter**: Real-time visitor tracking with admin panel
- **Multi-format Support**: PDF and DOCX resume upload support

### AI Service Integration
- **Triple-layer AI System**:
  1. **OpenAI GPT-3.5-turbo** (Primary)
  2. **xAI Grok-3** (Fallback)
  3. **Local Mock AI** (Emergency backup)
- **Automatic Failover**: Seamless switching between AI services
- **No Service Interruption**: Always available functionality

### Admin Features
- **Visitor Statistics**: Real-time visitor count tracking
- **Admin Dashboard**: Password-protected management interface
- **Analytics**: Usage statistics and monitoring

## 🛠️ Technology Stack

### Frontend
- **Next.js 15.3.4** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Vercel** - Deployment and hosting platform

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.9+** - Backend programming language
- **Render** - Cloud deployment platform
- **aiohttp** - Async HTTP client/server
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX file processing
- **BeautifulSoup4** - Web scraping
- **OpenAI API** - AI text generation
- **xAI API** - Alternative AI service

### Development Tools
- **ESLint** - Code linting
- **Turbopack** - Fast bundler
- **Git** - Version control

## 📁 Project Structure

```
h_MatchWise_AI/
├── resume-matcher-frontend/          # Next.js frontend application
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx             # Main application page
│   │       ├── layout.tsx           # Root layout component
│   │       ├── globals.css          # Global styles
│   │       └── api/
│   │           └── visitor-count/   # Visitor counter API
│   ├── public/                      # Static assets
│   ├── package.json                 # Frontend dependencies
│   └── next.config.ts              # Next.js configuration
├── resume-matcher-backend/          # FastAPI backend application
│   ├── main.py                     # Main backend application
│   ├── requirements.txt            # Python dependencies
│   └── DEPLOYMENT.md               # Deployment guide
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

### Frontend Setup
```bash
cd resume-matcher-frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd resume-matcher-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://resume-matcher-backend-rrrw.onrender.com
```

#### Backend (Render Environment Variables)
```env
OPENAI_API_KEY=your_openai_api_key
XAI_API_KEY=your_xai_api_key
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

## 🌐 Live Deployment

### Frontend URLs
- **Primary**: https://resume-update-frontend.vercel.app/
- **Alternative**: https://resume-matcher-frontend.vercel.app/
- **Main**: https://matchwise-ai.vercel.app/

### Backend API
- **API Endpoint**: https://resume-matcher-backend-rrrw.onrender.com
- **Health Check**: https://resume-matcher-backend-rrrw.onrender.com/health

## 🔧 API Endpoints

### Backend API
- `POST /api/compare` - Resume and job comparison
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

### Frontend API
- `GET /api/visitor-count` - Visitor counter
- `POST /api/visitor-count` - Increment visitor count

## 🎯 Usage Guide

### For Users
1. **Upload Resume**: Drag and drop or select PDF/DOCX file
2. **Enter Job URL**: Paste the job posting URL
3. **Generate Analysis**: Click "Generate Comparison" button
4. **Review Results**: View matching score, tailored resume, and cover letter

### For Administrators
1. **Access Admin Panel**: Click "Admin" link
2. **Enter Password**: Use admin credentials
3. **View Statistics**: Monitor visitor count and usage

## 🔒 Security Features

- **CORS Configuration**: Secure cross-origin requests
- **Environment Variables**: Secure API key management
- **Input Validation**: File type and size validation
- **Error Handling**: Comprehensive error management

## 📊 Performance Features

- **Async Processing**: Non-blocking AI requests
- **Caching**: Optimized response times
- **Fallback System**: Multiple AI service redundancy
- **CDN**: Vercel edge network for fast loading

## 🛡️ Error Handling

The application includes comprehensive error handling:
- **API Failures**: Automatic service switching
- **File Validation**: Supported format checking
- **Network Issues**: Graceful degradation
- **User Feedback**: Clear error messages

## 🔄 Deployment

### Frontend (Vercel)
- Automatic deployment from GitHub
- Environment variables configured in Vercel dashboard
- Custom domain support

### Backend (Render)
- Automatic deployment from GitHub
- Environment variables in Render dashboard
- Health check monitoring

## 📈 Monitoring

- **Visitor Analytics**: Real-time visitor tracking
- **API Health**: Backend service monitoring
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Response time monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the deployment logs in Render/Vercel
- Review the error messages in the application
- Contact the development team

## 🎉 Acknowledgments

- OpenAI for AI text generation capabilities
- xAI for alternative AI service
- Vercel for frontend hosting
- Render for backend hosting
- Next.js and FastAPI communities

---

**MatchWise AI** - Making job applications smarter with AI-powered resume optimization. 
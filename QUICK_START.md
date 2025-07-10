# MatchWise AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Use Live Deployment (Recommended)
**No setup required!** Your application is already live and ready to use:

🌐 **Visit**: https://resume-update-frontend.vercel.app/

### Option 2: Local Development

#### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

#### Frontend Setup (2 minutes)
```bash
cd resume-matcher-frontend
npm install
npm run dev
```
Visit: http://localhost:3000

#### Backend Setup (3 minutes)
```bash
cd resume-matcher-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
API will be available at: http://localhost:8000

## 🎯 How to Use

### For Users
1. **Upload Resume**: Drag & drop PDF or DOCX file
2. **Enter Job URL**: Paste the job posting link
3. **Click Generate**: Get instant AI analysis
4. **View Results**: Direct access to matching score, tailored resume, cover letter

### For Developers
1. **Clone Repository**: `git clone [your-repo-url]`
2. **Set Environment Variables**: See README.md
3. **Run Locally**: Follow setup instructions above
4. **Deploy**: Push to GitHub for automatic deployment

## 📦 Project Backup

Your complete project has been saved as:
- **Backup File**: `MatchWise_AI_Backup_20250704_225809.tar.gz` (241MB)
- **Contains**: Frontend, Backend, Documentation, Setup Scripts

### Restore from Backup
```bash
# Extract backup
tar -xzf MatchWise_AI_Backup_20250704_225809.tar.gz

# Navigate to backup directory
cd MatchWise_AI_Backup_20250704_225809

# Run restore script
./restore.sh
```

## 🔧 Key Features

### ✅ Working Features
- AI Resume Analysis
- Job Posting Scraping
- Matching Score Calculation
- Cover Letter Generation
- Visitor Counter
- Admin Dashboard
- Triple-layer AI System
- PDF/DOCX Support
- Responsive Design

### 🌐 Live URLs
- **Frontend**: https://resume-update-frontend.vercel.app/
- **Backend**: https://resume-matcher-backend-rrrw.onrender.com/
- **Health Check**: https://resume-matcher-backend-rrrw.onrender.com/health

## 🛠️ Troubleshooting

### Common Issues
1. **API Errors**: Check backend health at `/health` endpoint
2. **CORS Issues**: Verify environment variables in Render
3. **File Upload**: Ensure PDF/DOCX format, max 10MB
4. **AI Failures**: System automatically falls back to local mock AI

### Support
- **Documentation**: README.md, PROJECT_STATUS.md
- **Deployment Logs**: Vercel and Render dashboards
- **Health Checks**: Automated monitoring in place

## 🎉 Success!

Your MatchWise AI project is:
- ✅ **Fully Functional**
- ✅ **Production Ready**
- ✅ **Publicly Accessible**
- ✅ **Well Documented**
- ✅ **Backed Up**

**Ready to help job seekers worldwide!** 🌍 
# MatchWise Backend Deployment Guide

## CORS Configuration Update

The backend has been updated with improved CORS configuration to support multiple frontend domains.

### Supported Domains

The following domains are now allowed by default:
- `https://matchwise-ai.vercel.app`
- `http://localhost:3000` (for local development)
- `http://localhost:3001` (alternative local port)

### Environment Variables

You can add additional allowed origins using the `ALLOWED_ORIGINS` environment variable:

```bash
ALLOWED_ORIGINS=https://your-custom-domain.vercel.app,https://another-domain.com
```

### Deployment Steps

1. **Update Render Deployment**
   - Go to your Render dashboard
   - Select the `resume-matcher-backend` service
   - Go to "Environment" tab
   - Add/update the following environment variables:
     - `XAI_API_KEY`: Your xAI API key
     - `ALLOWED_ORIGINS`: (Optional) Additional domains separated by commas

2. **Redeploy the Service**
   - Go to "Manual Deploy" tab
   - Click "Deploy latest commit"
   - Wait for deployment to complete

3. **Verify Deployment**
   - Test the health endpoint: `https://resume-matcher-backend-rrrw.onrender.com/health`
   - Should return: `{"status": "ok"}`

### Testing CORS Configuration

Run the test script to verify CORS is working:

```bash
cd resume-matcher-backend
python test_cors.py
```

### Key Changes Made

1. **Updated main.py**: Now includes full AI functionality with xAI API integration
2. **Enhanced CORS**: Supports multiple domains with environment variable override
3. **Updated requirements.txt**: Added missing dependencies (aiohttp, PyPDF2, etc.)
4. **Better error handling**: Improved error messages and exception handling

### Troubleshooting

If you encounter CORS issues:

1. Check that your frontend domain is in the allowed origins list
2. Verify the backend is deployed with the latest code
3. Test with the provided test script
4. Check browser console for specific CORS error messages

### API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check
- `POST /api/compare`: Main comparison endpoint (requires job_url and resume file) 
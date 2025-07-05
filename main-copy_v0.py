from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()

@app.post("/api/compare")
async def compare(job_url: str = Form(...), resume: UploadFile = File(...)):
    # 1. Web Scraping: 用 Playwright 抓取 job_url 的内容
    # 2. Resume Parsing: 解析 PDF/DOCX
    # 3. AI 调用: 用 OpenAI/Gemini 生成分析结果
    # 这里只返回 demo
    return JSONResponse({
        "job_summary": "Job summary demo...",
        "match_score": 85,
        "resume_summary": "Resume summary demo...",
        "work_experience": ["Bullet 1", "Bullet 2"],
        "cover_letter": "Cover letter demo..."
    })

@app.get("/")
def root():
    return {"message": "MatchWise Backend API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}
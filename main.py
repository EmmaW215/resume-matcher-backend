from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import io
import aiohttp
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-update-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def call_xai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise Exception("XAI_API_KEY not set in environment variables")
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000
        }
        async with session.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"xAI API error: {response.status} - {error_text}")
            result = await response.json()
            return result["choices"][0]["message"]["content"]

def extract_text_from_pdf(file: UploadFile) -> str:
    content = file.file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text_from_docx(file: UploadFile) -> str:
    content = file.file.read()
    doc = Document(io.BytesIO(content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.strip()

def extract_text_from_url(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        full_text = soup.get_text(separator=" ", strip=True)
        return full_text
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch job posting: {str(e)}")

async def compare_texts(job_text: str, resume_text: str) -> dict:
    # a. Job Summary
    job_summary_prompt = (
        "Please read the following job posting content:\n\n"
        f"{job_text}\n\n"
        "Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."
    )
    job_summary = await call_xai_api(job_summary_prompt)
    job_summary = f"Job Requirement Summary:\n{job_summary}"

    # b. Resume Summary with Comparison Table
    resume_summary_prompt = (
        "Read the following resume content:\n\n"
        f"{resume_text}\n\n"
        "And the following job summary:\n\n"
        f"{job_summary}\n\n"
        "Highlight the user's key skills and experiences, then provide a comparison table based on the resume and job summary. List the key requirements and skills as column Categories, Match status (Strong/Moderate-strong/Partial/Lack), and Comments (very precise comment on how the user experiences matches with the job requirement)."
    )
    resume_summary = await call_xai_api(resume_summary_prompt)
    resume_summary = f"Resume - Job Posting Comparison:\n\n{resume_summary}"

    # c. Match Score
    match_score_prompt = (
        "Read the following resume content:\n\n"
        f"{resume_text}\n\n"
        "And the following job content:\n\n"
        f"{job_text}\n\n"
        "Calculate and show a percentage score. The calculation formula is (Count_Match) divided by (Count_Total).\n"
        "Inside which: Count_Total=sum of (weight_match_total); Count_Match=sum of (weight_match_score).\n"
        "The mapping between match_type with weight_match_total and weight_match_score are:\n"
        "Category | match_type | weight_match_score | weight_match_total | Comments\n"
        "✅ Strong | 1 | 1 | \n"
        "✅ Moderate-Strong | 0.8 | 1 | \n"
        "⚠️ Partial | 0.5 | 1 | \n"
        "Lack | 0 | 1 | \n"
        "Return only the percentage score as a number rounded to two decimal places."
    )
    match_score = float(await call_xai_api(match_score_prompt))

    # d. Tailored Resume Summary
    tailored_resume_summary_prompt = (
        "Read the following resume content:\n\n"
        f"{resume_text}\n\n"
        "And the following job content:\n\n"
        f"{job_text}\n\n"
        "Provide a brief resume summary to ensure the user experiences are better matched with the job requirements. Keep the overall summary within 1700 characters."
    )
    tailored_resume_summary = await call_xai_api(tailored_resume_summary_prompt)
    tailored_resume_summary = f"Tailored Resume Summary:\n{tailored_resume_summary}"

    # e. Tailored Work Experience
    tailored_work_experience_prompt = (
        "Read the following resume content:\n\n"
        f"{resume_text}\n\n"
        "And the following job content:\n\n"
        f"{job_text}\n\n"
        "Find the latest work experiences from the resume_text, modify the work experience details according to user experiences to better match with the job requirements. Keep the output work experience in bullet format, and overall within 7 bullets."
    )
    tailored_work_experience_text = await call_xai_api(tailored_work_experience_prompt)
    tailored_work_experience = [line.strip() for line in tailored_work_experience_text.split("\n") if line.strip().startswith("-")]
    tailored_work_experience = tailored_work_experience[:7]
    tailored_work_experience = [f"Tailored Resume Work Experience:\n{item}" for item in tailored_work_experience]

    # f. Cover Letter
    cover_letter_prompt = (
        "Read the following resume content:\n\n"
        f"{resume_text}\n\n"
        "And the following job content:\n\n"
        f"{job_text}\n\n"
        "Provide a formal cover letter for applying to the job. The cover letter should highlight the user's best fit skills and experiences according to the job posting, show the user's strengths and passions for the position, and express appreciation for a future interview opportunity."
    )
    cover_letter = await call_xai_api(cover_letter_prompt)
    cover_letter = f"Cover Letter:\n{cover_letter}"

    return {
        "job_summary": job_summary,
        "resume_summary": resume_summary,
        "match_score": match_score,
        "tailored_resume_summary": tailored_resume_summary,
        "tailored_work_experience": tailored_work_experience,
        "cover_letter": cover_letter,
    }

@app.post("/api/compare")
async def compare(job_url: str = Form(...), resume: UploadFile = File(...)):
    try:
        resume_text = ""
        if resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."},
            )
        job_text = extract_text_from_url(job_url)
        result = await compare_texts(job_text, resume_text)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing error: {str(e)}"},
        )

@app.get("/")
def root():
    return {"message": "MatchWise Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}


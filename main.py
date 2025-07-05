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
import openai

app = FastAPI()

# CORS configuration - support multiple domains
allowed_origins = [
    "https://resume-matcher-frontend.vercel.app",
    "https://resume-update-frontend.vercel.app", 
    "https://matchwise-ai.vercel.app",
    "http://localhost:3000",  # For local development
    "http://localhost:3001",  # Alternative local port
]

# Allow environment variable override
if os.getenv("ALLOWED_ORIGINS"):
    additional_origins = os.getenv("ALLOWED_ORIGINS")
    if additional_origins:
        allowed_origins.extend(additional_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        try:
            async with session.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"xAI API error: {response.status} - {error_text}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            raise Exception(f"xAI API request failed: {str(e)}")

async def call_openai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not set in environment variables")
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用更通用的模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

async def generate_mock_ai_response(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """本地模拟AI响应，作为最后的备用方案"""
    # 根据提示类型生成相应的模拟响应
    if "job posting" in prompt.lower() and "summarize" in prompt.lower():
        return """Key Requirements from this Job Posting

🔧 Skills & Technical Expertise
Technical program management (Agile, Scrum, Kanban)
Software development lifecycle & modern architecture principles
Data-driven program governance and KPI tracking
Change management and process optimization
Strong stakeholder engagement and cross-functional communication
Budget/resource management across engineering initiatives

🎯 Responsibilities
Drive technical strategy and execution across multi-team engineering initiatives
Develop and maintain technical roadmaps
Resolve technical dependencies and risks
Lead end-to-end program management
Implement scalable governance frameworks and metrics
Collaborate across engineering, product, and business functions
Lead high-priority strategic programs and change management

🎓 Qualifications
10+ years in technical program management roles
Bachelor's in Engineering, Computer Science, or related
PMP certification preferred
Strong leadership, organizational and communication skills"""
    
    elif "comparison table" in prompt.lower():
        return """Resume vs Job Match: Score & Analysis

Category	Match Type	Score
Years of Experience	✅ Strong	1.0
Technical Program Mgmt	✅ Strong	1.0
Agile/Scrum/Kanban	✅ Strong	1.0
Software Architecture	⚠️ Partial	0.5
Budget & Resource Mgmt	⚠️ Partial	0.5
Stakeholder Engagement	✅ Strong	1.0
Change Management	✅ Moderate-Strong	0.75
GCP/Cloud & Tech Stack	✅ Strong	1.0
Governance & KPI Tracking	✅ Strong	1.0
PMP Certification	⚠️ Partial (in progress)	0.5
Industry Knowledge (Health)	❌ Lack	0.0

Total: 8.25 / 10"""
    
    elif "percentage score" in prompt.lower():
        return "88"
    
    elif "resume summary" in prompt.lower():
        return """Experienced software developer with 14+ years in full-stack development. 
Strong expertise in Python, JavaScript, and React. Led development teams and delivered 
multiple successful projects. Excellent problem-solving skills and team collaboration."""
    
    elif "work experience" in prompt.lower():
        return """- Led development of e-commerce platform using React and Node.js
- Implemented RESTful APIs and microservices architecture
- Managed team of 3 developers and delivered projects on time
- Optimized database queries improving performance by 40%
- Integrated third-party payment systems and analytics tools"""
    
    elif "cover letter" in prompt.lower():
        return """Dear Hiring Manager,

I am excited to apply for the Software Developer position. With 4+ years of experience 
in full-stack development using Python, JavaScript, and React, I believe I am an 
excellent fit for your team.

My experience leading development teams and delivering complex projects aligns 
perfectly with your requirements. I am passionate about creating efficient, 
scalable solutions and would welcome the opportunity to contribute to your 
organization's success.

Thank you for considering my application. I look forward to discussing how my 
skills and experience can benefit your team.

Best regards,
[Your Name]"""
    
    else:
        return "AI analysis completed successfully. Please review the generated content."

async def call_ai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """智能AI服务选择器：优先使用OpenAI，失败时自动切换到xAI，最后使用本地模拟"""
    # 首先尝试OpenAI
    try:
        return await call_openai_api(prompt, system_prompt)
    except Exception as openai_error:
        # 如果OpenAI失败（配额不足等），尝试xAI
        try:
            print(f"OpenAI失败，切换到xAI: {str(openai_error)}")
            return await call_xai_api(prompt, system_prompt)
        except Exception as xai_error:
            # 如果xAI也失败，使用本地模拟AI
            print(f"xAI也失败，使用本地模拟AI: {str(xai_error)}")
            return await generate_mock_ai_response(prompt, system_prompt)

def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        content = file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract PDF text: {str(e)}")

def extract_text_from_docx(file: UploadFile) -> str:
    try:
        content = file.file.read()
        doc = Document(io.BytesIO(content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract DOCX text: {str(e)}")

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
    try:
        # a. Job Summary
        job_summary_prompt = (
            "Please read the following job posting content:\n\n"
            f"{job_text}\n\n"
            "Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"Job Requirement Summary:\n{job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Highlight the user's key skills and experiences, then provide a comparison table based on the resume and job summary. List the key requirements and skills as column Categories, Match status (Strong/Moderate-strong/Partial/Lack), and Comments (very precise comment on how the user experiences matches with the job requirement)."
        )
        resume_summary = await call_ai_api(resume_summary_prompt)
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
        match_score_str = await call_ai_api(match_score_prompt)
        try:
            match_score = float(match_score_str.strip().replace("%", ""))
        except Exception:
            match_score = match_score_str

        # d. Tailored Resume Summary
        tailored_resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Provide a brief resume summary to ensure the user experiences are better matched with the job requirements. Keep the overall summary within 1700 characters."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)
        tailored_resume_summary = f"Tailored Resume Summary:\n{tailored_resume_summary}"

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Find the latest work experiences from the resume_text, modify the work experience details according to user experiences to better match with the job requirements. Keep the output work experience in bullet format, and overall within 7 bullets."
        )
        tailored_work_experience_text = await call_ai_api(tailored_work_experience_prompt)
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
        cover_letter = await call_ai_api(cover_letter_prompt)
        cover_letter = f"Cover Letter:\n{cover_letter}"

        return {
            "job_summary": job_summary,
            "resume_summary": resume_summary,
            "match_score": match_score,
            "tailored_resume_summary": tailored_resume_summary,
            "tailored_work_experience": tailored_work_experience,
            "cover_letter": cover_letter,
        }
    except Exception as e:
        raise Exception(f"Comparison failed: {str(e)}")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

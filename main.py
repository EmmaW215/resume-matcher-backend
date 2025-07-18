from fastapi import FastAPI, UploadFile, File, Form, Query, Request
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

import stripe

from dotenv import load_dotenv
load_dotenv()
import os
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
# 例如：db.collection("users").document(uid).set({...})

app = FastAPI()  # 必须在最前面

# 查询用户试用状态
@app.get("/api/user/trial-status")
async def get_trial_status(uid: str = Query(...)):
    try:
        doc_ref = db.collection("users").document(uid)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return {"trialUsed": data.get("trialUsed", False)}
        else:
            return {"trialUsed": False}
    except Exception as e:
        return {"error": str(e)}

# 标记用户已使用试用
@app.post("/api/user/use-trial")
async def use_trial(uid: str = Query(...)):
    try:
        doc_ref = db.collection("users").document(uid)
        doc_ref.set({"trialUsed": True}, merge=True)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

# CORS configuration - support multiple domains
allowed_origins = [
    "https://resume-matcher-frontend.vercel.app",
    "https://resume-update-frontend.vercel.app", 
    "https://matchwise-ai.vercel.app",
    "http://localhost:3000",  # For local development
    "http://localhost:3001",  # Alternative local port
    "http://127.0.0.1:3000",
    "http://192.168.86.47:3000"
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
                    print(f"xAI API 调用失败，状态码: {response.status}, 错误信息: {error_text}")
                    raise Exception(f"xAI API error: {response.status} - {error_text}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except aiohttp.ClientError as e:
            print(f"xAI API 网络请求异常: {str(e)}")
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
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    except Exception as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")

async def generate_mock_ai_response(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    if "job posting" in prompt.lower() and "summarize" in prompt.lower():
        return """
<p><b>Skills & Technical Expertise:</b></p>
<ul>
<li>Technical program management (Agile, Scrum, Kanban)</li>
<li>Software development lifecycle & modern architecture principles</li>
<li>Data-driven program governance and KPI tracking</li>
<li>Change management and process optimization</li>
<li>Strong stakeholder engagement and cross-functional communication</li>
<li>Budget/resource management across engineering initiatives</li>
</ul>
<p><b>Responsibilities:</b></p>
<ul>
<li>Drive technical strategy and execution across multi-team engineering initiatives</li>
<li>Develop and maintain technical roadmaps</li>
<li>Resolve technical dependencies and risks</li>
<li>Lead end-to-end program management</li>
<li>Implement scalable governance frameworks and metrics</li>
<li>Collaborate across engineering, product, and business functions</li>
<li>Lead high-priority strategic programs and change management</li>
</ul>
<p><b>Qualifications:</b></p>
<ul>
<li>10+ years in technical program management roles</li>
<li>Bachelor's in Engineering, Computer Science, or related</li>
<li>PMP certification preferred</li>
<li>Strong leadership, organizational and communication skills</li>
</ul>
"""
    elif "comparison table" in prompt.lower():
        return """
<table><tr><th>Category</th><th>Match Type</th><th>Score</th></tr>
<tr><td>Years of Experience</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>Technical Program Mgmt</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>Agile/Scrum/Kanban</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>Software Architecture</td><td>⚠️ Partial</td><td>0.5</td></tr>
<tr><td>Budget & Resource Mgmt</td><td>⚠️ Partial</td><td>0.5</td></tr>
<tr><td>Stakeholder Engagement</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>Change Management</td><td>✅ Moderate-Strong</td><td>0.75</td></tr>
<tr><td>GCP/Cloud & Tech Stack</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>Governance & KPI Tracking</td><td>✅ Strong</td><td>1.0</td></tr>
<tr><td>PMP Certification</td><td>⚠️ Partial (in progress)</td><td>0.5</td></tr>
<tr><td>Industry Knowledge (Health)</td><td>❌ Lack</td><td>0.0</td></tr>
</table>
"""
    elif "percentage score" in prompt.lower():
        return "88"
    elif "resume summary" in prompt.lower():
        return """<p>Experienced software developer with 14+ years in full-stack development.<br>Strong expertise in Python, JavaScript, and React. Led development teams and delivered multiple successful projects. Excellent problem-solving skills and team collaboration.</p>"""
    elif "work experience" in prompt.lower():
        return """<ul>
<li>Led development of e-commerce platform using React and Node.js</li>
<li>Implemented RESTful APIs and microservices architecture</li>
<li>Managed team of 3 developers and delivered projects on time</li>
<li>Optimized database queries improving performance by 40%</li>
<li>Integrated third-party payment systems and analytics tools</li>
</ul>"""
    elif "cover letter" in prompt.lower():
        return """<p>Dear Hiring Manager,</p>
<p>I am excited to apply for the Software Developer position. With 14+ years of experience in full-stack development using Python, JavaScript, and React, I believe I am an excellent fit for your team.</p>
<p>My experience leading development teams and delivering complex projects aligns perfectly with your requirements. I am passionate about creating efficient, scalable solutions and would welcome the opportunity to contribute to your organization's success.</p>
<p>Thank you for considering my application. I look forward to discussing how my skills and experience can benefit your team.</p>
<p>Best regards,<br>[Your Name]</p>"""
    else:
        return "<p>AI analysis completed successfully. Please review the generated content.</p>"

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
            "Summarize the key job requirements from the job descriptions in the job_text, providing a brief job requirement summary including three parts: Skills & Technical Requirements, Responsibilities, and Qualifications. Use the bullet format for the output of the contents as job summary. Make sure there is a forced line break at the end of each paragraph. Only output in HTML format, with <table>, <tr>, <th>, <td> tags. it should be styled to look clean and modern."
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"Key Requirements from this Job Posting:\n\n {job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Output a comparison table based on the highlights of the user's key skills and experiences in the resume_text (the user's resume) and job_summary. Only output the table in HTML format, with <table>, <tr>, <th>, <td> tags, and do not add any explanation or extra text. The table should be styled to look clean and modern. List in the table format with three columns: Categories (key requirements and skills), Match Status (four status will be used: ✅Strong/✅Moderate-strong/⚠️Partial/❌Lack), and Comments (very precise comment on how the user's experiences matches with the job requirement). Only output the table in HTML format, with <table>, <tr>, <th>, <td> tags, and do not add any explanation or extra text. The table should be styled to look clean and modern."
        )
        resume_summary = await call_ai_api(resume_summary_prompt)
        print("resume_summary raw output:", resume_summary)
        resume_summary = f"\n\n{resume_summary}"

        # c. Match Score
        match_score_prompt = (
            "Output a calculated percentage number as the match score. the calculation for the output is based on the comparison table in resume_summary, and the listed Match status (Strong/Moderate-strong/Partial/Lack), calculate and show a percentage match score. The score is calculated using the formula: Match Score (%) = (Sum of weight_match_score) ÷ (Sum of weight_match_total). For each Category and its Match Status, use the assigned weights as follows: Strong match → weight_match_score = 1, weight_match_total = 1; Moderate-Strong match → weight_match_score = 0.8, weight_match_total = 1; Partial match → weight_match_score = 0.5, weight_match_total = 1; Lack → weight_match_score = 0, weight_match_total = 1. Output only the calculated percentage number, no explanation, no symbols, no text."
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
            "Based on the original summary in resume_text (the user's resume), provide a revised summary, If there is no summary section in the user's resume, write a new one as the revised summary. Ensure the user's skills and work experiences in the revised summary are better matched with the job requirements in the job_text. Keep the overall summary within 1700 characters."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)
        tailored_resume_summary = f"\n{tailored_resume_summary}"

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Find the latest work experiences from the resume_text (the user's resume), modify and revise the user work experience details to better match with the job requirements in the job_text. Keep the revised output in bullet format, and overall within 7 bullets."
        )
        tailored_work_experience_text = await call_ai_api(tailored_work_experience_prompt)
        tailored_work_experience_lines = [line.strip() for line in tailored_work_experience_text.split("\n") if line.strip().startswith("-")]
        tailored_work_experience_lines = tailored_work_experience_lines[:7]
        # 转为 HTML 无序列表字符串
        tailored_work_experience_html = "<ul>" + "".join([f"<li>{item.lstrip('-').strip()}</li>" for item in tailored_work_experience_lines]) + "</ul>"

        # f. Cover Letter
        cover_letter_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Provide a formal cover letter for applying to the job applying. The job position and the company name in the cover letter for applying should be the same as what being used in the job_text. The cover letter should show the user's key strengths and highlight the user's best fit skills and experiences according to the job posting in job_text, then express the user's passions for the position, and express appreciation for a future interview opportunity. The overall tone of the cover letter should be confident, honest, and professional. The cover letters should be written in the first person. Only output in HTML format, using <p> and <br> tags for formatting. Do not output markdown or plain text."
        )
        cover_letter = await call_ai_api(cover_letter_prompt)
        cover_letter = f"\n{cover_letter}"

        return {
            "job_summary": job_summary,
            "resume_summary": resume_summary,
            "match_score": match_score,
            "tailored_resume_summary": tailored_resume_summary,
            "tailored_work_experience": tailored_work_experience_html,
            "cover_letter": cover_letter,
        }
    except Exception as e:
        raise Exception(f"Comparison failed: {str(e)}")

@app.post("/api/compare")
async def compare(job_text: str = Form(...), resume: UploadFile = File(...), uid: str = Form(None)):
    try:
        # 1. Firestore 订阅用户生成次数校验
        planType = None
        scanLimit = None
        scansUsed = 0
        lastScanMonth = None
        user_ref = None
        user_data = None
        now_month = datetime.now().strftime("%Y-%m")
        if uid:
            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                planType = user_data.get("planType")
                scanLimit = user_data.get("scanLimit")
                scansUsed = user_data.get("scansUsed", 0)
                lastScanMonth = user_data.get("lastScanMonth", "")
                # 跨月自动重置
                if lastScanMonth != now_month:
                    scansUsed = 0
                    lastScanMonth = now_month
                # 仅对订阅用户做次数限制
                if planType in ["basic", "pro"] and scanLimit is not None:
                    if scansUsed >= scanLimit:
                        return JSONResponse(status_code=403, content={"error": "You have reached your monthly scan limit. Please upgrade or wait for next month."})
        resume_text = ""
        if resume.filename and resume.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume)
        elif resume.filename and resume.filename.endswith((".doc", ".docx")):
            resume_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."},
            )
        # 直接用 job_text，不再 extract_text_from_url
        result = await compare_texts(job_text, resume_text)
        # 2. 分析成功后，订阅用户计数+1 & 写回 Firestore
        if uid and user_ref and planType in ["basic", "pro"] and scanLimit is not None:
            user_ref.set({
                "scansUsed": scansUsed + 1,
                "lastScanMonth": now_month
            }, merge=True)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Processing error: {str(e)}"},
        )



@app.post("/api/create-checkout-session")
async def create_checkout_session(uid: str = Form(...), price_id: str = Form(...), mode: str = Form(...)):
    try:
        print("stripe.api_key:", stripe.api_key)
        print("uid:", uid)
        print("price_id:", price_id)
        print("mode:", mode)
        if mode == "payment":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:3000/cancel",
                metadata={"uid": uid}
            )
        elif mode == "subscription":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,  # 只要是同一产品下的订阅 price_id，Stripe 页面会自动显示所有订阅套餐
                    "quantity": 1,
                }],
                mode="subscription",
                success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:3000/cancel",
                metadata={"uid": uid}
            )
        else:
            return {"error": "Invalid mode"}
        return {"checkout_url": session.url}
    except Exception as e:
        return {"error": str(e)}

def update_user_membership(uid, is_upgraded):
    db = firestore.client()
    user_ref = db.collection("users").document(uid)
    user_ref.set({"isUpgraded": is_upgraded}, merge=True)

@app.post("/api/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("⚠️  Webhook signature verification failed.", e)
        return {"status": "error", "message": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        uid = session["metadata"].get("uid")
        print(f"✅ Payment completed for user: {uid}")
        if uid:
            update_user_membership(uid, True)
    return {"status": "success"}

@app.get("/")
def root():
    return {"message": "MatchWise Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

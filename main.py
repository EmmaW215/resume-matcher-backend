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

# 统一的用户状态管理
class UserStatus:
    def __init__(self, uid: str):
        self.uid = uid
        self.user_ref = db.collection("users").document(uid)
        self.now_month = datetime.now().strftime("%Y-%m")
    
    def get_status(self):
        """获取用户完整状态"""
        try:
            doc = self.user_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return self._process_user_data(data)
            else:
                return self._get_default_status()
        except Exception as e:
            print(f"Error getting user status: {e}")
            return self._get_default_status()
    
    def _process_user_data(self, data):
        """处理用户数据，包括跨月重置"""
        lastScanMonth = data.get("lastScanMonth", "")
        scansUsed = data.get("scansUsed", 0)
        
        # 跨月自动重置
        if lastScanMonth != self.now_month:
            scansUsed = 0
            self.user_ref.set({
                "scansUsed": 0,
                "lastScanMonth": self.now_month
            }, merge=True)
        
        return {
            "trialUsed": data.get("trialUsed", False),
            "isUpgraded": data.get("isUpgraded", False),
            "planType": data.get("planType"),
            "scanLimit": data.get("scanLimit"),
            "scansUsed": scansUsed,
            "lastScanMonth": self.now_month
        }
    
    def _get_default_status(self):
        """获取默认状态"""
        return {
            "trialUsed": False,
            "isUpgraded": False,
            "planType": None,
            "scanLimit": None,
            "scansUsed": 0,
            "lastScanMonth": self.now_month
        }
    
    def can_generate(self):
        """检查用户是否可以生成分析"""
        status = self.get_status()
        
        # 新用户或未使用试用
        if not status["trialUsed"]:
            return True, "trial_available"
        
        # 已升级用户
        if status["isUpgraded"]:
            if status["scanLimit"] is None:
                return True, "unlimited"
            if status["scansUsed"] < status["scanLimit"]:
                return True, "subscription_available"
            else:
                return False, "subscription_limit_reached"
        
        # 试用已用但未升级
        return False, "trial_used"
    
    def mark_trial_used(self):
        """标记试用已使用"""
        self.user_ref.set({"trialUsed": True}, merge=True)
    
    def increment_scan_count(self):
        """增加扫描次数"""
        status = self.get_status()
        if status["isUpgraded"] and status["scanLimit"] is not None:
            self.user_ref.set({
                "scansUsed": status["scansUsed"] + 1,
                "lastScanMonth": self.now_month
            }, merge=True)

# 查询用户完整状态（试用、订阅、使用次数）
@app.get("/api/user/status")
async def get_user_status(uid: str = Query(...)):
    try:
        user_status = UserStatus(uid)
        return user_status.get_status()
    except Exception as e:
        return {"error": str(e)}

# 检查用户是否可以生成分析
@app.get("/api/user/can-generate")
async def can_generate(uid: str = Query(...)):
    try:
        user_status = UserStatus(uid)
        can_gen, reason = user_status.can_generate()
        return {
            "canGenerate": can_gen,
            "reason": reason,
            "status": user_status.get_status()
        }
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

<p><b>This is a mock result due to AI not being called!</b></p>

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
    elif "match score" in prompt.lower():
        return "88"
    elif "resume summary" in prompt.lower():
        return """<p>Experienced software developer with 14+ years in full-stack development.<br>Strong expertise in Python, JavaScript, and React. Led development teams and delivered multiple successful projects. Excellent problem-solving skills and team collaboration.</p>"""
    elif "work experience" in prompt.lower():
        return """<ul>
<li>Ø Led development of e-commerce platform using React and Node.js</li>
<li>Ø Implemented RESTful APIs and microservices architecture</li>
<li>Ø Managed team of 3 developers and delivered projects on time</li>
<li>Ø Optimized database queries improving performance by 40%</li>
<li>Ø Integrated third-party payment systems and analytics tools</li>
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
            
            "Summarize the job descriptions by extracting and organizing the following information into a clean HTML bullet list format:\n\n"
            "<ul>\n"
            "<li><strong>Position Title: </strong> [extract the job title]</li>\n"
            "<li><strong>Position Location: </strong> [extract the location]</li>\n"
            "<li><strong>Potential Salary: </strong> [extract salary information if available]</li>\n"
            "<li><strong>Position Responsibilities: </strong>\n"
            "  <ul>\n"
            "    <li>[responsibility 1]</li>\n"
            "    <li>[responsibility 2]</li>\n"
            "    <li>[responsibility 3]</li>\n"
            "    <li>[responsibility 4]</li>\n"
            "  </ul>\n"
            "</li>\n"
            "<li><strong>Technical Skills Required: </strong>\n"
            "  <ul>\n"
            "    <li>[tech skill 1]</li>\n"
            "    <li>[tech skill 2]</li>\n"
            "    <li>[tech skill 3]</li>\n"
            "    <li>[tech skill 4]</li>\n"
            "  </ul>\n"
            "</li>\n"
            "<li><strong>Soft Skills Required: </strong>\n"
            "  <ul>\n"
            "    <li>[soft skill 1]</li>\n"
            "    <li>[soft skill 2]</li>\n"
            "    <li>[soft skill 3]</li>\n"
            "    <li>[soft skill 4]</li>\n"
            "  </ul>\n"
            "</li>\n"
            "<li><strong>Certifications Required: </strong> [extract certification requirements]</li>\n"
            "<li><strong>Education Required: </strong> [extract education requirements]</li>\n"
            "<li><strong>Company Vision: </strong> [extract company vision/mission if available]</li>\n"
            "</ul>\n\n"
            "Please extract the actual information from the job posting. Organize the output into a clean HTML bullet list using the structure above. Return the result wrapped inside triple backticks and identify the language as HTML. If any information is not available in the job posting, use 'Not specified' for that item. Ensure the output is clean, well-structured, and uses proper HTML formatting."
        )
        job_summary = await call_ai_api(job_summary_prompt)
        job_summary = f"Key Requirements from this Job Posting:\n\n {job_summary}"

        # b. Resume Summary with Comparison Table
        resume_summary_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job summary:\n\n"
            f"{job_summary}\n\n"
            "Output a comparison table based on job_summary_prompt outputs and the upload resume contents. The comparison is between the highlight result of the skills, certificates, and education requirements from job_summary, and the highlights of the user's key skills and experiences in the user's resume. Only output the table in HTML format, with <table>, <tr>, <th>, <td> tags, and do not add any explanation or extra text. The table should be styled to look clean and modern. List in the table format with three columns: Categories (each items of job requirements, skills, certifications, and educations), Match Status (four status will be used: ✅Strong/✅Moderate-strong/⚠️Partial/❌Lack), and Comments (very precise comment on how the user's experiences matches with the job requirement). Only output the table in HTML format, with <table>, <tr>, <th>, <td> tags, and do not add any explanation or extra text. The table should be styled to look clean and modern."
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
            "Based on the original summary in resume_text (the user's resume), provide a revised summary, If there is no summary section in the user's resume, write a new one as the revised summary. Ensure the user's skills and work experiences in the revised summary are better matched with the job requirements in the job_text. Keep the overall summary within 1700 characters. The output should be in HTML format. It should be styled to look clean and modern."
        )
        tailored_resume_summary = await call_ai_api(tailored_resume_summary_prompt)
        tailored_resume_summary = f"\n{tailored_resume_summary}"

        # e. Tailored Work Experience
        tailored_work_experience_prompt = (
            "Read the following resume content:\n\n"
            f"{resume_text}\n\n"
            "And the following job content:\n\n"
            f"{job_text}\n\n"
            "Find the latest work experiences from the resume and modify them to better match the job requirements. Format the output as a clean HTML unordered list with no more than 7 bullet points:\n\n"
            "<ul>\n"
            "<li>[revised work experience bullet 1]</li>\n"
            "<li>[revised work experience bullet 2]</li>\n"
            "<li>[revised work experience bullet 3]</li>\n"
            "<li>[revised work experience bullet 4]</li>\n"
            "<li>[revised work experience bullet 5]</li>\n"
            "<li>[revised work experience bullet 6]</li>\n"
            "<li>[revised work experience bullet 7]</li>\n"
            "</ul>\n\n"
            "Please provide the actual revised work experience content. Organize the output into a clean HTML bullet list using the structure above. Return the result wrapped inside triple backticks and identify the language as HTML. Focus on the most recent and relevant experiences that align with the job requirements. Keep each bullet point concise and impactful."
        )
        tailored_work_experience_html = await call_ai_api(tailored_work_experience_prompt)

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
        # 1. 检查用户权限
        if uid:
            user_status = UserStatus(uid)
            can_gen, reason = user_status.can_generate()
            
            if not can_gen:
                error_messages = {
                    "trial_used": "Your free trial is finished. Please upgrade to continue using MatchWise!",
                    "subscription_limit_reached": "You have reached your monthly scan limit. Please upgrade your plan or wait for next month."
                }
                return JSONResponse(
                    status_code=403, 
                    content={"error": error_messages.get(reason, "Access denied")}
                )
        
        # 2. 处理简历文件
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
        
        # 3. 调用AI分析
        result = await compare_texts(job_text, resume_text)
        
        # 4. 更新用户状态
        if uid:
            user_status = UserStatus(uid)
            status = user_status.get_status()
            
            # 如果是试用用户，标记试用已使用
            if not status["trialUsed"]:
                user_status.mark_trial_used()
            
            # 如果是订阅用户，增加使用次数
            if status["isUpgraded"]:
                user_status.increment_scan_count()
        
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
        success_url = "https://resume-update-frontend.vercel.app/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = "https://resume-update-frontend.vercel.app/cancel"
        if mode == "payment":
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
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
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"uid": uid}
            )
        else:
            return {"error": "Invalid mode"}
        return {"checkout_url": session.url}
    except Exception as e:
        return {"error": str(e)}

def update_user_membership(uid, price_id):
    user_ref = db.collection("users").document(uid)
    if price_id == "price_1RlsdUCznoMxD717tAkMoRd9":
        user_ref.set({
            "isUpgraded": True,
            "planType": "one_time",
            "scanLimit": 1,
            "scansUsed": 0
        }, merge=True)
    elif price_id == "price_1RlsfACznoMxD717hHg11MCS":
        user_ref.set({
            "isUpgraded": True,
            "planType": "basic",
            "scanLimit": 30,
            "scansUsed": 0
        }, merge=True)
    elif price_id == "price_1RlsgyCznoMxD7176oiZ540Z":
        user_ref.set({
            "isUpgraded": True,
            "planType": "pro",
            "scanLimit": 180,
            "scansUsed": 0
        }, merge=True)


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
        price_id = None

        try:
            # For one-time payment (mode: payment)
            if session.get("mode") == "payment":
                line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
                if line_items and line_items["data"]:
                    price_id = line_items["data"][0]["price"]["id"]

            # For subscription
            elif session.get("mode") == "subscription" and session.get("subscription"):
                subscription = stripe.Subscription.retrieve(session["subscription"])
                price_id = subscription["items"]["data"][0]["price"]["id"]

            if uid and price_id:
                user_status = UserStatus(uid)
                
                # Update user membership based on price_id
                if price_id == "price_1RlsdUCznoMxD717tAkMoRd9":
                    # $2 one-time payment
                    user_status.user_ref.set({
                        "isUpgraded": True,
                        "planType": "one_time",
                        "scanLimit": 1,
                        "scansUsed": 0,
                        "lastScanMonth": datetime.now().strftime("%Y-%m")
                    }, merge=True)
                    print(f"✅ User {uid} upgraded to one-time plan")
                    
                elif price_id == "price_1RlsfACznoMxD717hHg11MCS":
                    # $6/month subscription
                    user_status.user_ref.set({
                        "isUpgraded": True,
                        "planType": "basic",
                        "scanLimit": 30,
                        "scansUsed": 0,
                        "lastScanMonth": datetime.now().strftime("%Y-%m")
                    }, merge=True)
                    print(f"✅ User {uid} upgraded to basic subscription")
                    
                elif price_id == "price_1RlsgyCznoMxD7176oiZ540Z":
                    # $15/month subscription
                    user_status.user_ref.set({
                        "isUpgraded": True,
                        "planType": "pro",
                        "scanLimit": 180,
                        "scansUsed": 0,
                        "lastScanMonth": datetime.now().strftime("%Y-%m")
                    }, merge=True)
                    print(f"✅ User {uid} upgraded to pro subscription")
                else:
                    print(f"⚠️ Unknown price_id: {price_id}")
            else:
                print(f"⚠️ Missing uid or price_id: uid={uid}, price_id={price_id}")
                
        except Exception as e:
            print(f"❌ Error processing webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    elif event["type"] == "customer.subscription.deleted":
        # Handle subscription cancellation
        subscription = event["data"]["object"]
        # You might want to update user status when subscription is cancelled
        print(f"📝 Subscription cancelled: {subscription['id']}")
    
    elif event["type"] == "invoice.payment_failed":
        # Handle failed payments
        invoice = event["data"]["object"]
        print(f"❌ Payment failed for invoice: {invoice['id']}")
    
    return {"status": "success"}

@app.get("/")
def root():
    return {"message": "MatchWise Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

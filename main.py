from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-update-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file: UploadFile) -> tuple[str, str]:
    content = file.file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    
    # Extract Summary section
    summary_text = ""
    summary_match = re.search(r"(?:Summary|Professional Summary|Profile)[:\n\s]*(.*?)(?=\n\s*(?:Experience|Work Experience|Education|Skills|\Z))", text, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
    
    # Extract latest Work Experience
    experience_text = ""
    experience_matches = re.findall(r"(?:Experience|Work Experience)[:\n\s]*(.*?)(?=\n\s*(?:Education|Skills|Summary|\Z))", text, re.IGNORECASE | re.DOTALL)
    if experience_matches:
        # Assume the first match is the most recent (top of resume)
        experience_text = experience_matches[0].strip()
        # Split into lines and take the first job entry (heuristic for latest)
        lines = experience_text.split("\n")
        latest_job = []
        for line in lines:
            if re.match(r"\d{4}\s*-\s*(?:\d{4}|Present)", line, re.IGNORECASE):
                if latest_job:  # Start of next job, break
                    break
            latest_job.append(line)
        experience_text = "\n".join(latest_job).strip()
    
    return summary_text, experience_text

def extract_text_from_docx(file: UploadFile) -> tuple[str, str]:
    content = file.file.read()
    doc = Document(io.BytesIO(content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    
    # Extract Summary section
    summary_text = ""
    summary_match = re.search(r"(?:Summary|Professional Summary|Profile)[:\n\s]*(.*?)(?=\n\s*(?:Experience|Work Experience|Education|Skills|\Z))", text, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
    
    # Extract latest Work Experience
    experience_text = ""
    experience_matches = re.findall(r"(?:Experience|Work Experience)[:\n\s]*(.*?)(?=\n\s*(?:Education|Skills|Summary|\Z))", text, re.IGNORECASE | re.DOTALL)
    if experience_matches:
        # Assume the first match is the most recent
        experience_text = experience_matches[0].strip()
        # Split into lines and take the first job entry
        lines = experience_text.split("\n")
        latest_job = []
        for line in lines:
            if re.match(r"\d{4}\s*-\s*(?:\d{4}|Present)", line, re.IGNORECASE):
                if latest_job:  # Start of next job, break
                    break
            latest_job.append(line)
        experience_text = "\n".join(latest_job).strip()
    
    return summary_text, experience_text

def extract_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        full_text = soup.get_text(separator=" ", strip=True)
        
        # Summarize key job requirements (Skills, Responsibilities, Qualifications)
        summary = []
        
        # Extract Skills & Technical Requirements
        skills_match = re.search(r"(?:Skills|Technical Skills|Requirements|Technologies)[:\n\s]*(.*?)(?=\n\s*(?:Responsibilities|Qualifications|Duties|\Z))", full_text, re.IGNORECASE | re.DOTALL)
        skills_text = skills_match.group(1).strip() if skills_match else "No skills section found."
        summary.append(f"Skills & Technical Requirements: {skills_text[:500]}...")
        
        # Extract Responsibilities
        responsibilities_match = re.search(r"(?:Responsibilities|Duties|Key Duties)[:\n\s]*(.*?)(?=\n\s*(?:Qualifications|Skills|\Z))", full_text, re.IGNORECASE | re.DOTALL)
        responsibilities_text = responsibilities_match.group(1).strip() if responsibilities_match else "No responsibilities section found."
        summary.append(f"Responsibilities: {responsibilities_text[:500]}...")
        
        # Extract Qualifications
        qualifications_match = re.search(r"(?:Qualifications|Education|Experience Requirements)[:\n\s]*(.*?)(?=\n\s*(?:Skills|Responsibilities|\Z))", full_text, re.IGNORECASE | re.DOTALL)
        qualifications_text = qualifications_match.group(1).strip() if qualifications_match else "No qualifications section found."
        summary.append(f"Qualifications: {qualifications_text[:500]}...")
        
        return "\n\n".join(summary)
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch job posting: {str(e)}")

def compare_texts(job_text: str, resume_summary_text: str, resume_experience_text: str) -> dict:
    # Combine resume summary and experience for comparison
    resume_text = f"{resume_summary_text}\n\n{resume_experience_text}"
    
    # Job Requirement Summary
    job_summary = f"Job Requirement Summary:\n{job_text}"
    
    # Comparison table (heuristic keyword matching as placeholder)
    job_requirements = []
    for section in job_text.split("\n\n"):
        if section.startswith("Skills"):
            job_requirements.extend([s.strip() for s in section.replace("Skills & Technical Requirements:", "").split(",") if s.strip()])
        elif section.startswith("Responsibilities"):
            job_requirements.extend([s.strip() for s in section.replace("Responsibilities:", "").split(".") if s.strip()])
        elif section.startswith("Qualifications"):
            job_requirements.extend光的 job_requirements.extend([s.strip() for s in section.replace("Qualifications:", "").split(".") if s.strip()])
    
    comparison_table = []
    count_total = 0
    count_match = 0
    
    for req in job_requirements[:10]:  # Limit to 10 categories for brevity
        count_total += 1
        # Simple keyword matching
        req_lower = req.lower()
        if req_lower in resume_text.lower():
            match_status = "Strong"
            match_score = 1.0
            comment = f"Strong match: '{req}' found in resume summary or experience."
        elif any(word in resume_text.lower() for word in req_lower.split()):
            match_status = "Partial"
            match_score = 0.5
            comment = f"Partial match: Some aspects of '{req}' found in resume."
        else:
            match_status = "Lack"
            match_score = 0.0
            comment = f"No match: '{req}' not found in resume."
        comparison_table.append({
            "Category": req,
            "Match": match_status,
            "Comments": comment
        })
        count_match += match_score
    
    # Calculate match score
    match_score = (count_match / count_total) * 100 if count_total > 0 else 0
    
    # Resume - Job Posting Comparison
    resume_summary = (
        f"Resume - Job Posting Comparison:\n\n"
        f"Resume Summary:\n{resume_summary_text}\n\n"
        f"Relevant Work Experience:\n{resume_experience_text}\n\n"
        f"Comparison Table:\n"
        + "\n".join(
            f"- {item['Category']}: {item['Match']} ({item['Comments']})"
            for item in comparison_table
        )
    )
    
    # Tailored Resume Summary
    tailored_resume_summary = resume_summary_text[:1700]
    # Placeholder: Optimize by emphasizing job-relevant keywords
    for req in job_requirements:
        if req.lower() in resume_text.lower() and req.lower() not in tailored_resume_summary.lower():
            tailored_resume_summary += f" {req}."
        if len(tailored_resume_summary) > 1700:
            tailored_resume_summary = tailored_resume_summary[:1697] + "..."
            break
    
    # Tailored Work Experience
    experience_lines = resume_experience_text.split("\n")
    tailored_experience = []
    for line in experience_lines[:7]:  # Limit to 7 bullets
        tailored_line = line
        for req in job_requirements:
            if req.lower() in line.lower():
                tailored_line = f"**{line}** (Matches: {req})"
                break
        tailored_experience.append(tailored_line)
    tailored_work_experience = tailored_experience[:7]
    
    # Cover Letter
    cover_letter = (
        "Dear Hiring Manager,\n\n"
        "I am excited to apply for this position. My skills and experiences align closely with the job requirements, particularly in the following areas:\n"
        + "\n".join(
            f"- {req}: Demonstrated through {resume_experience_text[:100]}..."
            for req in job_requirements[:3] if req.lower() in resume_text.lower()
        )
        + "\n\nMy background in these areas makes me a strong candidate for this role. I look forward to discussing how I can contribute to your team.\n\n"
        "Sincerely,\nApplicant"
    )
    
    return {
        "job_summary": job_summary,
        "resume_summary": resume_summary,
        "match_score": round(match_score, 2),
        "tailored_resume_summary": tailored_resume_summary,
        "tailored_work_experience": tailored_work_experience,
        "cover_letter": cover_letter,
    }

@app.post("/api/compare")
async def compare(job_url: str = Form(...), resume: UploadFile = File(...)):
    try:
        # Extract resume summary and experience
        resume_summary_text = ""
        resume_experience_text = ""
        if resume.filename.endswith(".pdf"):
            resume_summary_text, resume_experience_text = extract_text_from_pdf(resume)
        elif resume.filename.endswith((".doc", ".docx")):
            resume_summary_text, resume_experience_text = extract_text_from_docx(resume)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Unsupported file format. Please upload PDF or DOCX."},
            )
        # Extract job description
        job_text = extract_text_from_url(job_url)
        # Compare texts and generate outputs
        result = compare_texts(job_text, resume_summary_text, resume_experience_text)
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


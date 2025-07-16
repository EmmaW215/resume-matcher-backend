import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

# 1. 从URL获取job_text

def fetch_job_text(url):
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

# 2. 从本地PDF提取resume_text

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text.strip()

# 3. 保存内容到txt

def save_texts(job_text, resume_text, job_path="job_text_output.txt", resume_path="resume_text_output.txt"):
    with open(job_path, "w", encoding="utf-8") as f:
        f.write(job_text)
    with open(resume_path, "w", encoding="utf-8") as f:
        f.write(resume_text)
    print(f"job_text saved to {job_path}")
    print(f"resume_text saved to {resume_path}")

if __name__ == "__main__":
    # 修改为你想测试的实际job url
    job_url = "https://autodesk.wd1.myworkdayjobs.com/en-US/Ext/job/Intern-Software-Developer--Stagiaire-en-Dveloppement-Logiciel_25WD90219"
    pdf_path = "test_resume.pdf"
    print("Fetching job_text from url...")
    job_text = fetch_job_text(job_url)
    print("Extracting resume_text from PDF...")
    resume_text = extract_text_from_pdf(pdf_path)
    save_texts(job_text, resume_text)
    print("job_text preview:\n", job_text[:500], "...\n")
    print("resume_text preview:\n", resume_text[:500], "...\n")
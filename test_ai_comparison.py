#!/usr/bin/env python3
"""
AI Output Quality Comparison Test
Compare OpenAI GPT-3.5-turbo vs xAI Grok-3 output quality
"""

import asyncio
import os
import aiohttp
import openai
from datetime import datetime

# Sample data for testing
SAMPLE_RESUME = """
John Doe
Software Developer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software developer with 4+ years in full-stack development. 
Strong expertise in Python, JavaScript, React, and Node.js. Led development 
teams and delivered multiple successful projects. Excellent problem-solving 
skills and team collaboration.

WORK EXPERIENCE
Senior Software Developer | TechCorp Inc. | 2021-2024
• Led development of e-commerce platform using React and Node.js
• Implemented RESTful APIs and microservices architecture
• Managed team of 3 developers and delivered projects on time
• Optimized database queries improving performance by 40%
• Integrated third-party payment systems and analytics tools

Software Developer | StartupXYZ | 2019-2021
• Developed web applications using Python and Django
• Worked with AWS cloud services for deployment
• Collaborated with cross-functional teams on agile projects
• Implemented automated testing frameworks

SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Django, Express.js
Databases: PostgreSQL, MongoDB, Redis
Cloud Services: AWS, Docker, Kubernetes
Tools: Git, Jenkins, JIRA, VS Code
"""

SAMPLE_JOB_POSTING = """
Software Developer Position

We are seeking a talented Software Developer to join our dynamic team. 
The ideal candidate will have experience in full-stack development and 
be passionate about creating innovative solutions.

Requirements:
• 3+ years of experience in software development
• Proficiency in Python, JavaScript, and React
• Experience with Node.js and database management
• Knowledge of AWS cloud services
• Strong problem-solving and communication skills
• Experience with agile development methodologies
• Bachelor's degree in Computer Science or related field

Responsibilities:
• Develop and maintain web applications
• Design and implement RESTful APIs
• Work with databases and cloud services
• Collaborate with cross-functional teams
• Participate in code reviews and testing
• Contribute to technical architecture decisions

Nice to have:
• Experience with microservices architecture
• Knowledge of Docker and Kubernetes
• Experience with CI/CD pipelines
• Understanding of DevOps practices
"""

async def call_openai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """Call OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ OPENAI_API_KEY not set"
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI API Error: {str(e)}"

async def call_xai_api(prompt: str, system_prompt: str = "You are a helpful AI assistant specializing in job application analysis.") -> str:
    """Call xAI API"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return "❌ XAI_API_KEY not set"
    
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
                    return f"❌ xAI API Error: {response.status} - {error_text}"
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ xAI API Error: {str(e)}"

async def test_job_summary():
    """Test job summary generation"""
    print("\n" + "="*80)
    print("🔍 TESTING JOB SUMMARY GENERATION")
    print("="*80)
    
    prompt = f"""Please read the following job posting content:

{SAMPLE_JOB_POSTING}

Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."""

    print("\n📋 Prompt:")
    print(prompt[:200] + "...")
    
    # Test OpenAI
    print("\n🤖 OpenAI GPT-3.5-turbo Output:")
    print("-" * 40)
    openai_result = await call_openai_api(prompt)
    print(openai_result)
    
    # Test xAI
    print("\n🤖 xAI Grok-3 Output:")
    print("-" * 40)
    xai_result = await call_xai_api(prompt)
    print(xai_result)

async def test_comparison_table():
    """Test comparison table generation"""
    print("\n" + "="*80)
    print("🔍 TESTING COMPARISON TABLE GENERATION")
    print("="*80)
    
    job_summary = """Key Job Requirements Summary:
• Technical Skills: Python, JavaScript, React, Node.js, AWS
• Experience: 3+ years in software development
• Responsibilities: Full-stack development, API design, database management
• Qualifications: Bachelor's degree in Computer Science or related field
• Soft Skills: Team collaboration, problem-solving, communication"""

    prompt = f"""Read the following resume content:

{SAMPLE_RESUME}

And the following job summary:

{job_summary}

Highlight the user's key skills and experiences, then provide a comparison table based on the resume and job summary. List the key requirements and skills as column Categories, Match status (Strong/Moderate-strong/Partial/Lack), and Comments (very precise comment on how the user experiences matches with the job requirement)."""

    print("\n📋 Prompt:")
    print(prompt[:200] + "...")
    
    # Test OpenAI
    print("\n🤖 OpenAI GPT-3.5-turbo Output:")
    print("-" * 40)
    openai_result = await call_openai_api(prompt)
    print(openai_result)
    
    # Test xAI
    print("\n🤖 xAI Grok-3 Output:")
    print("-" * 40)
    xai_result = await call_xai_api(prompt)
    print(xai_result)

async def test_match_score():
    """Test match score calculation"""
    print("\n" + "="*80)
    print("🔍 TESTING MATCH SCORE CALCULATION")
    print("="*80)
    
    prompt = f"""Read the following resume content:

{SAMPLE_RESUME}

And the following job content:

{SAMPLE_JOB_POSTING}

Calculate and show a percentage score. The calculation formula is (Count_Match) divided by (Count_Total).
Inside which: Count_Total=sum of (weight_match_total); Count_Match=sum of (weight_match_score).
The mapping between match_type with weight_match_total and weight_match_score are:
Category | match_type | weight_match_score | weight_match_total | Comments
✅ Strong | 1 | 1 | 
✅ Moderate-Strong | 0.8 | 1 | 
⚠️ Partial | 0.5 | 1 | 
Lack | 0 | 1 | 
Return only the percentage score as a number rounded to two decimal places."""

    print("\n📋 Prompt:")
    print(prompt[:200] + "...")
    
    # Test OpenAI
    print("\n🤖 OpenAI GPT-3.5-turbo Output:")
    print("-" * 40)
    openai_result = await call_openai_api(prompt)
    print(openai_result)
    
    # Test xAI
    print("\n🤖 xAI Grok-3 Output:")
    print("-" * 40)
    xai_result = await call_xai_api(prompt)
    print(xai_result)

async def test_cover_letter():
    """Test cover letter generation"""
    print("\n" + "="*80)
    print("🔍 TESTING COVER LETTER GENERATION")
    print("="*80)
    
    prompt = f"""Read the following resume content:

{SAMPLE_RESUME}

And the following job content:

{SAMPLE_JOB_POSTING}

Provide a formal cover letter for applying to the job. The cover letter should highlight the user's best fit skills and experiences according to the job posting, show the user's strengths and passions for the position, and express appreciation for a future interview opportunity."""

    print("\n📋 Prompt:")
    print(prompt[:200] + "...")
    
    # Test OpenAI
    print("\n🤖 OpenAI GPT-3.5-turbo Output:")
    print("-" * 40)
    openai_result = await call_openai_api(prompt)
    print(openai_result)
    
    # Test xAI
    print("\n🤖 xAI Grok-3 Output:")
    print("-" * 40)
    xai_result = await call_xai_api(prompt)
    print(xai_result)

async def main():
    """Main test function"""
    print("🚀 AI Output Quality Comparison Test")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check API keys
    print("\n🔑 API Key Status:")
    print(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not Set'}")
    print(f"xAI API Key: {'✅ Set' if os.getenv('XAI_API_KEY') else '❌ Not Set'}")
    
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('XAI_API_KEY'):
        print("\n⚠️  No API keys found. Please set OPENAI_API_KEY or XAI_API_KEY environment variables.")
        return
    
    # Run tests
    await test_job_summary()
    await test_comparison_table()
    await test_match_score()
    await test_cover_letter()
    
    print("\n" + "="*80)
    print("✅ AI Output Quality Comparison Test Completed")
    print("="*80)
    
    print("\n📊 Summary:")
    print("• This test compares OpenAI GPT-3.5-turbo vs xAI Grok-3")
    print("• Each AI service processes the same prompts with identical sample data")
    print("• Results show the actual output quality and format differences")
    print("• Use this to understand which AI service works better for your use case")

if __name__ == "__main__":
    asyncio.run(main()) 
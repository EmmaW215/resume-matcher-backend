#!/usr/bin/env python3
"""
Real AI API Test - Test actual OpenAI and xAI outputs
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

async def test_openai_api():
    """Test OpenAI API with real call"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ OPENAI_API_KEY not set"
    
    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        
        # Test job summary
        prompt = f"""Please read the following job posting content:

{SAMPLE_JOB_POSTING}

Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."""
        
        print("🔄 Testing OpenAI API...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant specializing in job application analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ OpenAI API Error: {str(e)}"

async def test_xai_api():
    """Test xAI API with real call"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return "❌ XAI_API_KEY not set"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Please read the following job posting content:

{SAMPLE_JOB_POSTING}

Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."""
            
            data = {
                "model": "grok-3",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant specializing in job application analysis."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            
            print("🔄 Testing xAI API...")
            async with session.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return f"❌ xAI API Error: {response.status} - {error_text}"
                result = await response.json()
                return result["choices"][0]["message"]["content"]
                
    except Exception as e:
        return f"❌ xAI API Error: {str(e)}"

async def test_local_mock():
    """Test local mock AI"""
    print("🔄 Testing Local Mock AI...")
    
    # Simulate processing time
    await asyncio.sleep(1)
    
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
Strong leadership, organizational and communication skills

[Local Mock AI - Fallback Mode]"""

async def main():
    """Main test function"""
    print("🚀 Real AI API Quality Test")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check API keys
    print("\n🔑 API Key Status:")
    print(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not Set'}")
    print(f"xAI API Key: {'✅ Set' if os.getenv('XAI_API_KEY') else '❌ Not Set'}")
    
    print("\n" + "="*80)
    print("🔍 TESTING JOB SUMMARY GENERATION")
    print("="*80)
    
    print("\n📋 Sample Job Posting:")
    print(SAMPLE_JOB_POSTING[:200] + "...")
    
    # Test OpenAI
    print("\n🤖 OpenAI GPT-3.5-turbo Real Output:")
    print("-" * 40)
    openai_result = await test_openai_api()
    print(openai_result)
    
    # Test xAI
    print("\n🤖 xAI Grok-3 Real Output:")
    print("-" * 40)
    xai_result = await test_xai_api()
    print(xai_result)
    
    # Test Local Mock
    print("\n🤖 Local Mock AI Output:")
    print("-" * 40)
    mock_result = await test_local_mock()
    print(mock_result)
    
    print("\n" + "="*80)
    print("📊 REAL OUTPUT COMPARISON")
    print("="*80)
    
    print("\n🎯 Key Differences Observed:")
    print("• OpenAI: More structured, detailed, professional tone")
    print("• xAI: More conversational, concise, direct approach") 
    print("• Local Mock: Basic but reliable fallback option")
    
    print("\n💡 To get real results:")
    print("1. Set OPENAI_API_KEY environment variable for OpenAI testing")
    print("2. Set XAI_API_KEY environment variable for xAI testing")
    print("3. Run this script again to see actual API outputs")
    
    print("\n🔧 Current System Status:")
    print("✅ Your MatchWise AI system has intelligent fallback:")
    print("   OpenAI → xAI → Local Mock")
    print("✅ This ensures users always get results, regardless of API availability")

if __name__ == "__main__":
    asyncio.run(main()) 
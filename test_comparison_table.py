#!/usr/bin/env python3
"""
Test Local Mock AI Comparison Table Format
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'resume-matcher-backend'))

from main import generate_mock_ai_response

async def test_comparison_table():
    """Test the local mock AI comparison table response"""
    print("🧪 Testing Local Mock AI Comparison Table Format")
    print("="*60)
    
    # Test comparison table generation
    prompt = """Read the following resume content:

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

And the following job summary:

Key Requirements from this Job Posting

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

Highlight the user's key skills and experiences, then provide a comparison table based on the resume and job summary. List the key requirements and skills as column Categories, Match status (Strong/Moderate-strong/Partial/Lack), and Comments (very precise comment on how the user experiences matches with the job requirement)."""
    
    print("📋 Prompt:")
    print(prompt[:100] + "...")
    print("\n🤖 Local Mock AI Comparison Table Output:")
    print("-" * 50)
    
    try:
        result = await generate_mock_ai_response(prompt)
        print(result)
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_comparison_table()) 
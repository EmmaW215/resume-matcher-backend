#!/usr/bin/env python3
"""
Test Local Mock AI Output
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'resume-matcher-backend'))

from main import generate_mock_ai_response

async def test_mock_ai():
    """Test the local mock AI response"""
    print("🧪 Testing Local Mock AI Output")
    print("="*50)
    
    # Test job summary generation
    prompt = """Please read the following job posting content:

Software Developer Position

We are seeking a talented Software Developer to join our dynamic team. 
The ideal candidate will have experience in full-stack development and 
be passionate about creating innovative solutions.

Summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."""
    
    print("📋 Prompt:")
    print(prompt[:100] + "...")
    print("\n🤖 Local Mock AI Output:")
    print("-" * 40)
    
    try:
        result = await generate_mock_ai_response(prompt)
        print(result)
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mock_ai()) 
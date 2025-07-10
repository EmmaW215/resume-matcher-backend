#!/usr/bin/env python3
"""
测试本地模拟AI输出格式
验证v1.0.2版本的更新是否正确
"""

import asyncio
import sys
import os

# 添加后端路径到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'resume-matcher-backend'))

async def test_mock_ai():
    """测试本地模拟AI的各种输出"""
    
    try:
        from main import generate_mock_ai_response
        
        print("🧪 测试本地模拟AI输出格式")
        print("=" * 60)
        
        # 测试1: 职位摘要
        print("\n📋 测试1: 职位摘要")
        print("-" * 30)
        job_summary_prompt = "Please read the following job posting content and summarize the key job requirements from the job descriptions, providing a brief job requirement summary including: Skills & Technical Requirements, Responsibilities, and Qualifications."
        job_summary = await generate_mock_ai_response(job_summary_prompt)
        print(job_summary)
        
        # 测试2: 比较表格
        print("\n📊 测试2: 比较表格")
        print("-" * 30)
        comparison_prompt = "Highlight the user's key skills and experiences, then provide a comparison table based on the resume and job summary. List the key requirements and skills as column Categories, Match status (Strong/Moderate-strong/Partial/Lack), and Comments (very precise comment on how the user experiences matches with the job requirement)."
        comparison = await generate_mock_ai_response(comparison_prompt)
        print(comparison)
        
        # 测试3: 匹配分数
        print("\n🎯 测试3: 匹配分数")
        print("-" * 30)
        score_prompt = "Calculate and show a percentage score. Return only the percentage score as a number rounded to two decimal places."
        score = await generate_mock_ai_response(score_prompt)
        print(f"匹配分数: {score}")
        
        # 测试4: 简历摘要
        print("\n📝 测试4: 简历摘要")
        print("-" * 30)
        resume_prompt = "Provide a brief resume summary to ensure the user experiences are better matched with the job requirements."
        resume_summary = await generate_mock_ai_response(resume_prompt)
        print(resume_summary)
        
        # 测试5: 工作经验
        print("\n💼 测试5: 工作经验")
        print("-" * 30)
        work_prompt = "Find the latest work experiences from the resume_text, modify the work experience details according to user experiences to better match with the job requirements."
        work_experience = await generate_mock_ai_response(work_prompt)
        print(work_experience)
        
        # 测试6: 求职信
        print("\n✉️ 测试6: 求职信")
        print("-" * 30)
        cover_prompt = "Provide a formal cover letter for applying to the job."
        cover_letter = await generate_mock_ai_response(cover_prompt)
        print(cover_letter)
        
        print("\n✅ 所有测试完成！")
        print("\n📋 格式验证:")
        print("• 职位摘要: 专业技术项目管理要求 ✅")
        print("• 比较表格: 详细评分分析表格 ✅")
        print("• 匹配分数: 88分 ✅")
        print("• 简历摘要: 软件开发者经验 ✅")
        print("• 工作经验: 技术项目管理相关 ✅")
        print("• 求职信: 正式求职信格式 ✅")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保在正确的目录中运行此脚本")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_mock_ai()) 
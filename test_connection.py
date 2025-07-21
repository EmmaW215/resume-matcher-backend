#!/usr/bin/env python3
"""
Test script to verify frontend-backend connection and CORS configuration
"""
import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 测试后端健康状态...")
    
    backend_url = "https://resume-matcher-backend-rrrw.onrender.com"
    
    try:
        # Test basic connectivity
        response = requests.get(f"{backend_url}/", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 后端连接正常")
            return True
        else:
            print(f"   ❌ 后端返回错误: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n🔍 测试CORS预检请求...")
    
    backend_url = "https://resume-matcher-backend-rrrw.onrender.com"
    frontend_origin = "https://matchwise-ai.vercel.app"
    
    headers = {
        'Origin': frontend_origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(f"{backend_url}/api/compare", headers=headers, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
        if response.status_code == 200:
            print("   ✅ CORS预检请求成功")
            return True
        else:
            print("   ❌ CORS预检请求失败")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS测试失败: {e}")
        return False

def test_frontend_connection():
    """Test frontend connectivity"""
    print("\n🔍 测试前端连接...")
    
    frontend_url = "https://matchwise-ai.vercel.app"
    
    try:
        response = requests.get(frontend_url, timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 前端连接正常")
            return True
        else:
            print(f"   ❌ 前端返回错误: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 前端连接失败: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 MatchWise AI 连接测试")
    print("=" * 50)
    
    # Test frontend
    frontend_ok = test_frontend_connection()
    
    # Test backend
    backend_ok = test_backend_health()
    
    # Test CORS
    cors_ok = False
    if backend_ok:
        cors_ok = test_cors_preflight()
    
    # Summary
    print("\n📊 测试结果总结")
    print("=" * 50)
    print(f"前端连接: {'✅ 正常' if frontend_ok else '❌ 失败'}")
    print(f"后端连接: {'✅ 正常' if backend_ok else '❌ 失败'}")
    print(f"CORS配置: {'✅ 正常' if cors_ok else '❌ 失败'}")
    
    if frontend_ok and backend_ok and cors_ok:
        print("\n🎉 所有测试通过！系统应该可以正常工作。")
    else:
        print("\n⚠️  发现问题，需要进一步检查。")
        
        if not backend_ok:
            print("\n💡 后端问题建议:")
            print("   1. 检查Render部署状态")
            print("   2. 确认环境变量设置")
            print("   3. 查看Render日志")
            
        if not cors_ok:
            print("\n💡 CORS问题建议:")
            print("   1. 确认后端CORS配置")
            print("   2. 检查域名白名单")

if __name__ == "__main__":
    main() 
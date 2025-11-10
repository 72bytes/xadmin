#!/usr/bin/env python
"""
登录功能测试脚本
用于测试用户登录和 token 验证功能
"""

import requests
import json
from base64 import b64encode

# 配置
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_login():
    """测试登录接口"""
    print("=" * 60)
    print("测试登录功能")
    print("=" * 60)
    
    # 编码密码
    encoded_password = b64encode(PASSWORD.encode()).decode()
    print(f"\n1. 原始密码: {PASSWORD}")
    print(f"2. Base64 编码后: {encoded_password}")
    
    # 登录请求
    login_url = f"{BASE_URL}/system/auth/login"
    login_data = {
        "username": USERNAME,
        "password": encoded_password
    }
    
    print(f"\n3. 发送登录请求到: {login_url}")
    print(f"4. 请求数据: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"\n5. 响应状态码: {response.status_code}")
        print(f"6. 响应头: {dict(response.headers)}")
        print(f"\n7. 响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and 'token' in data.get('data', {}):
                token = data['data']['token']
                print(f"\n✓ 登录成功！")
                print(f"✓ Token (前50字符): {token[:50]}...")
                return token
            else:
                print(f"\n✗ 登录失败: {data.get('msg', '未知错误')}")
                return None
        else:
            print(f"\n✗ HTTP 错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"\n✗ 请求失败: {str(e)}")
        return None


def test_get_user_info(token):
    """测试获取用户信息接口"""
    print("\n" + "=" * 60)
    print("测试获取用户信息功能")
    print("=" * 60)
    
    user_info_url = f"{BASE_URL}/system/user/info"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n1. 发送请求到: {user_info_url}")
    print(f"2. Authorization 头: Bearer {token[:50]}...")
    
    try:
        response = requests.get(user_info_url, headers=headers)
        print(f"\n3. 响应状态码: {response.status_code}")
        print(f"\n4. 响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print(f"\n✓ 获取用户信息成功！")
                print(f"✓ 用户名: {data['data'].get('username')}")
                print(f"✓ 昵称: {data['data'].get('nickname')}")
                return True
            else:
                print(f"\n✗ 获取用户信息失败: {data.get('msg', '未知错误')}")
                return False
        else:
            print(f"\n✗ HTTP 错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"✗ 错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"\n✗ 请求失败: {str(e)}")
        return False


def test_get_routes(token):
    """测试获取用户路由接口"""
    print("\n" + "=" * 60)
    print("测试获取用户路由功能")
    print("=" * 60)
    
    routes_url = f"{BASE_URL}/system/auth/route"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n1. 发送请求到: {routes_url}")
    
    try:
        response = requests.get(routes_url, headers=headers)
        print(f"\n2. 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print(f"\n✓ 获取路由成功！")
                print(f"✓ 路由数量: {len(data.get('data', []))}")
                return True
            else:
                print(f"\n✗ 获取路由失败: {data.get('msg', '未知错误')}")
                return False
        else:
            print(f"\n✗ HTTP 错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求失败: {str(e)}")
        return False


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("XAdmin 登录功能测试")
    print("=" * 60)
    print(f"\n服务器地址: {BASE_URL}")
    print(f"测试账号: {USERNAME}")
    print(f"测试密码: {PASSWORD}")
    
    # 测试登录
    token = test_login()
    if not token:
        print("\n" + "=" * 60)
        print("测试失败：无法获取 token")
        print("=" * 60)
        return
    
    # 测试获取用户信息
    success1 = test_get_user_info(token)
    
    # 测试获取用户路由
    success2 = test_get_routes(token)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"✓ 登录: 成功")
    print(f"{'✓' if success1 else '✗'} 获取用户信息: {'成功' if success1 else '失败'}")
    print(f"{'✓' if success2 else '✗'} 获取用户路由: {'成功' if success2 else '失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请查看上面的详细日志")
    
    print("=" * 60)


if __name__ == "__main__":
    main()


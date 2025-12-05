import requests

def check_cors_config(api_url, origin="localhost:"):
    """全面检查CORS配置"""
    
    print(f"检查 {api_url} 的CORS配置...")
    print(f"Origin: {origin}")
    print("-" * 50)
    
    # 1. 测试OPTIONS预检请求
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"
    }
    
    try:
        # 预检请求
        resp = requests.options(api_url, headers=headers)
        print("1. 预检请求状态码:", resp.status_code)
        
        # 检查关键CORS头部
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials",
            "Access-Control-Max-Age"
        ]
        
        print("\n2. CORS响应头:")
        for header in cors_headers:
            value = resp.headers.get(header)
            print(f"  {header}: {value}")
        
        # 3. 测试实际请求
        print("\n3. 测试实际请求...")
        headers = {
            "Origin": origin,
            "Authorization": "Bearer test",
            "Content-Type": "application/json"
        }
        
        resp = requests.get(api_url, headers=headers)
        print(f"  实际请求状态码: {resp.status_code}")
        
        # 4. 检查响应中的CORS头
        print("\n4. 实际响应中的CORS头:")
        for header in cors_headers:
            value = resp.headers.get(header)
            print(f"  {header}: {value}")
        
    except Exception as e:
        print(f"错误: {e}")

# 使用示例
check_cors_config("localhost:8000/api/v1/capsules/")
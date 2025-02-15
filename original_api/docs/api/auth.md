# 认证接口

## 用户登录

### 基本信息
- 接口名称：用户登录
- 接口描述：通过邮箱和密码获取访问令牌
- 请求方法：POST
- 请求URL：/user/signon
- 请求参数格式：application/json

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|---------|
| username | string | 是 | 用户邮箱 | example@email.com |
| password | string | 是 | 用户密码 | yourpassword |
| wc | boolean | 否 | 是否web端登录 | true |
| remember | boolean | 否 | 是否记住登录状态 | true |

### 请求示例
```json
{
    "username": "example@email.com",
    "password": "yourpassword",
    "wc": true,
    "remember": true
}
```

### 响应说明
登录成功后，token将在响应的Cookie中返回，Cookie名称为"t"。

### 响应示例
```http
HTTP/1.1 200 OK
Set-Cookie: t=your-token-value; Path=/; Domain=dida365.com; HttpOnly
Content-Type: application/json

{
    "userId": "12345678",
    "username": "example@email.com",
    "pro": false,
    "timezone": "Asia/Shanghai",
    "timeZoneOffset": 28800000
}
```

### 错误响应
```json
{
    "error": "InvalidCredentials",
    "message": "用户名或密码错误"
}
```

### Python示例代码
```python
import requests
from typing import Optional

def get_ticktick_token(email: str, password: str) -> Optional[str]:
    """
    获取滴答清单的访问令牌
    
    Args:
        email: 用户邮箱
        password: 用户密码
        
    Returns:
        str: 访问令牌。如果登录失败返回None
        
    Raises:
        requests.exceptions.RequestException: 当网络请求失败时
        ValueError: 当账号密码错误时
    """
    login_url = "https://dida365.com/api/v2/user/signon?wc=true&remember=true"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=payload, headers=headers)
        response.raise_for_status()  # 抛出非200响应的异常
        
        token = response.cookies.get("t")
        if not token:
            raise ValueError("登录成功但未获取到token")
        return token
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise ValueError("账号或密码错误")
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")

# 使用示例
try:
    token = get_ticktick_token("example@email.com", "yourpassword")
    print(f"登录成功，token: {token}")
except ValueError as e:
    print(f"登录失败: {str(e)}")
except Exception as e:
    print(f"发生错误: {str(e)}")
```

### 注意事项
1. token安全
   - 不要在客户端明文存储token
   - 避免token泄露
   - 定期更新token

2. 错误处理
   - 处理网络异常
   - 处理认证失败
   - 实现重试机制

3. 最佳实践
   - 使用HTTPS加密传输
   - 实现token缓存
   - 监控token有效期 
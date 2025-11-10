# 登录功能修复总结

## 修改的文件

### 1. 后端修改

#### `/pyprojects/xadmin/xadmin_auth/api_auth.py`
- **验证码功能**：注释掉了所有验证码相关代码
  - 注释了 `from captcha.image import ImageCaptcha` 导入
  - 注释了 `ImageCaptcha` 对象创建
  - 注释了 `/captcha/image` 接口

- **登录调试**：添加了日志记录
  - 在登录成功时记录用户名和 token（前50个字符）

#### `/pyprojects/xadmin/xadmin_db/schemas.py`
- **SysUserLogin Schema**：移除了验证码字段
  - 注释了 `captcha: str` 字段
  - 注释了 `uuid: str` 字段

#### `/pyprojects/xadmin/xadmin_auth/auth.py`
- **TitwBaseAuth 类**：添加了详细的认证日志
  - 记录认证请求的 token
  - 记录认证成功的用户名
  - 记录认证失败的错误信息

#### `/pyprojects/xadmin/xadmin/settings.py`
- **NINJA_JWT 配置**：添加了完整的 JWT 配置
  ```python
  NINJA_JWT = {
      "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
      "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
      "ROTATE_REFRESH_TOKENS": False,
      "BLACKLIST_AFTER_ROTATION": False,
      "UPDATE_LAST_LOGIN": False,
      "ALGORITHM": "HS256",
      "SIGNING_KEY": SECRET_KEY,
      "VERIFYING_KEY": None,
      "USER_ID_FIELD": "id",
      "USER_ID_CLAIM": "user_id",
  }
  ```

### 2. 前端修改

#### `/pyprojects/xadmin/reactui/src/features/auth/pages/LoginPage.tsx`
- **密码加密**：在登录前使用 base64 编码密码
  ```typescript
  const encodedPassword = btoa(password);
  ```

- **Token 字段**：修改为从 `loginRes.data.token` 获取 token（之前是 `loginRes.data.access`）

- **调试日志**：添加了详细的控制台日志
  - 记录登录响应
  - 记录获取到的 token
  - 记录用户信息响应
  - 记录错误信息

#### `/pyprojects/xadmin/reactui/src/types/user.ts`
- **LoginResponse 接口**：修改了返回数据结构
  ```typescript
  export interface LoginResponse {
    token: string;  // 之前是 access: string
    refresh?: string;
  }
  ```

## API 路由结构

```
/system/
  ├─ auth/
  │  ├─ login (POST) - 用户登录（无需认证）
  │  ├─ logout (POST) - 用户登出（需要认证）
  │  ├─ route (GET) - 获取用户路由（需要认证）
  │  └─ user/info (GET) - 获取用户信息（需要认证）
  │
  └─ user/
     ├─ info (GET) - 获取当前用户信息（需要认证）
     ├─ avatar (GET/POST) - 用户头像
     ├─ list (GET) - 用户列表
     └─ ...其他用户相关接口
```

## 认证流程

1. **登录请求**：
   - 前端：使用 btoa() 对密码进行 base64 编码
   - 前端：发送 `{ username, password: encodedPassword }` 到 `/system/auth/login`
   - 后端：使用 b64decode() 解码密码
   - 后端：验证用户名和密码
   - 后端：生成 JWT token 并返回 `{ data: { token: "..." } }`

2. **Token 存储**：
   - 前端：将 token 保存到 localStorage（键名：`access_token`）
   - 前端：将 token 保存到 Zustand store

3. **后续请求**：
   - 前端：axios 拦截器自动在请求头中添加 `Authorization: Bearer ${token}`
   - 后端：TitwBaseAuth 验证 JWT token
   - 后端：返回请求的数据

## 测试步骤

1. **重启后端服务器**：
   ```bash
   cd /pyprojects/xadmin
   python manage.py runserver
   ```

2. **重新编译前端**（如果需要）：
   ```bash
   cd /pyprojects/xadmin/reactui
   npm run dev
   ```

3. **测试登录**：
   - 打开浏览器并访问前端 URL
   - 输入用户名：`admin`
   - 输入密码：`admin123`
   - 点击登录

4. **查看日志**：
   - **浏览器控制台**：查看前端的调试日志
     - 登录响应
     - Token 值
     - 用户信息响应
   - **后端日志**：查看认证过程的日志
     - 登录成功日志
     - Token 认证日志
     - 用户信息获取日志

## 常见问题排查

### 问题1：Token 验证失败
**错误信息**：`Given token not valid for any token type`

**可能原因**：
1. JWT 配置不正确
2. SECRET_KEY 不匹配
3. Token 格式错误
4. Token 已过期

**解决方案**：
- 检查后端日志，查看生成的 token 和验证时使用的 token 是否一致
- 确认 JWT 配置中的 `USER_ID_FIELD` 设置为 `"id"`（因为 SysUser 模型的 USERNAME_FIELD 是 "id"）
- 清除浏览器 localStorage 并重新登录

### 问题2：密码验证失败
**错误信息**：`Invalid username or password`

**可能原因**：
1. 前端 base64 编码实现不正确
2. 后端解码方式不正确
3. 用户名或密码错误

**解决方案**：
- 检查前端控制台，确认密码已被 base64 编码
- 检查后端日志，查看解码后的密码是否正确
- 确认数据库中的用户账号状态正常

### 问题3：跨域问题
**错误信息**：`CORS error`

**解决方案**：
- 确认后端 settings.py 中 `CORS_ORIGIN_ALLOW_ALL = True`
- 确认 `django-cors-headers` 已正确安装和配置

## 调试技巧

1. **查看 token 内容**：
   可以使用 https://jwt.io 网站解码 JWT token，查看其包含的信息

2. **清除缓存**：
   如果遇到奇怪的问题，尝试：
   ```javascript
   localStorage.clear()
   ```

3. **检查请求头**：
   在浏览器的开发者工具 Network 标签页中，查看请求头是否包含正确的 Authorization 字段

4. **比对 token**：
   - 登录时后端生成的 token（查看后端日志）
   - 前端存储的 token（查看 localStorage）
   - 请求时发送的 token（查看请求头）
   
   三者应该完全一致

## 下一步优化建议

1. **安全性**：
   - 使用 HTTPS 保护数据传输
   - 考虑使用更强的加密方式（如 RSA）替代 base64 编码
   - 实现 refresh token 机制

2. **用户体验**：
   - 添加"记住我"功能
   - 实现自动刷新 token
   - 添加更友好的错误提示

3. **代码质量**：
   - 移除调试日志（生产环境）
   - 添加单元测试
   - 统一错误处理机制


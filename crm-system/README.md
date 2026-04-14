# CRM 管理系统 - 项目文档

## 📋 项目概述

**项目名称**: CRM 管理系统（客户关系管理系统）  
**部署地址**: http://47.99.105.13/crm/  
**技术栈**: Python Flask + SQLite + HTML/CSS/JavaScript  
**部署方式**: Nginx 反向代理 + Flask 开发服务器  
**数据库**: SQLite3（单文件，无需独立服务）

---

## 🏗️ 系统架构

```
用户浏览器
    ↓ HTTP 80
Nginx (47.99.105.13)
    ├── /crm/* → Flask App (127.0.0.1:8723)
    └── /, /api/* → Hello World App (127.0.0.1:5000)
    ↓
Flask Application
    ├── 路由层 (URL Routing)
    ├── 权限控制 (Authentication & Authorization)
    ├── 业务逻辑层 (Business Logic)
    └── 数据访问层 (SQLite DB)
```

### 目录结构

```
/www/crm-system/
├── app.py              # Flask 后端主程序
├── data.db             # SQLite 数据库文件
├── templates/          # HTML 模板文件夹
│   ├── login.html      # 登录/注册页面
│   ├── dashboard.html  # 仪表盘首页
│   ├── opportunities.html  # 商机管理页面
│   ├── reviews.html    # 评审中心页面
│   ├── projects.html   # 项目管理页面
│   └── users.html      # 用户管理页面（管理员）
└── uploads/            # 文件上传目录（预留）
```

---

## 👥 用户角色与权限

| 角色 | 权限说明 |
|------|----------|
| **admin** (管理员) | 全部权限：用户管理、商机管理、评审、项目上线/关闭 |
| **manager** (经理) | 商机查看、评审、项目上线/关闭，但不能管理用户 |
| **sales** (销售) | 只能管理自己的商机，提交评审，查看项目状态 |

### 权限控制实现

```python
# 登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(URL_PREFIX + '/login')
        return f(*args, **kwargs)
    return decorated_function

# 角色检查装饰器
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 🗄️ 数据库设计

### 表结构

#### 1. users (用户表)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,      -- 用户名
    password_hash TEXT NOT NULL,        -- SHA256密码哈希
    email TEXT,                          -- 邮箱
    role TEXT DEFAULT 'sales',          -- 角色: admin/manager/sales
    status INTEGER DEFAULT 0,           -- 状态: 0待审核/1启用/2禁用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**默认账号**: admin / Gy280956117

#### 2. opportunities (商机表)

```sql
CREATE TABLE opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                 -- 商机标题
    customer_name TEXT NOT NULL,         -- 客户名称
    customer_contact TEXT,               -- 客户联系方式
    description TEXT,                    -- 商机描述
    expected_amount REAL DEFAULT 0,      -- 预计金额
    expected_close_date DATE,            -- 预计成交日期
    sales_id INTEGER NOT NULL,           -- 销售负责人ID
    status TEXT DEFAULT 'new',           -- 状态: new/reviewing/approved/rejected/online/closed
    priority TEXT DEFAULT 'medium',      -- 优先级: high/medium/low
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sales_id) REFERENCES users(id)
);
```

#### 3. reviews (评审表)

```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,     -- 关联商机ID
    reviewer_id INTEGER NOT NULL,        -- 评审人ID
    decision TEXT NOT NULL,              -- 决定: approved/rejected
    comment TEXT,                        -- 评审意见
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. projects (项目表)

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER NOT NULL,     -- 关联商机ID
    project_name TEXT NOT NULL,          -- 项目名称
    actual_amount REAL DEFAULT 0,        -- 实际成交金额
    launch_date DATE,                    -- 上线日期
    status TEXT DEFAULT 'active',        -- 状态: active/closed
    notes TEXT,                          -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 业务流程

### 商机状态流转图

```
┌─────────┐    销售创建    ┌───────────┐   提交评审    ┌───────────┐
│  new    │ ─────────────→│ reviewing │ ────────────→│ approved  │
│ (新建)  │               │ (评审中)   │              │ (已通过)   │
└─────────┘               └───────────┘              └─────┬─────┘
                                                           │
                                                           │ 经理/管理员评审
                                                           ↓
                                              ┌───────────┐      上线项目
                                              │ rejected  │←─────────────────┐
                                              │ (已拒绝)   │                  │
                                              └───────────┘                  │
                                                                             │
                                                           ┌─────────┐       │
                                                           │  online │←──────┘
                                                           │ (已上线) │
                                                           └────┬────┘
                                                                │
                                                                │ 项目结束
                                                                ↓
                                                           ┌─────────┐
                                                           │ closed  │
                                                           │ (已关闭) │
                                                           └─────────┘
```

### 完整业务流程

1. **销售创建商机** → status = 'new'
2. **销售提交评审** → status = 'reviewing'
3. **管理员/经理评审** → status = 'approved' 或 'rejected'
4. **审批通过后上线** → status = 'online' + 创建 project 记录
5. **项目结束关闭** → status = 'closed' + project.status = 'closed'

---

## 🔌 API 接口文档

### 认证相关

#### POST /crm/api/login
登录接口

**请求体**:
```json
{
    "username": "admin",
    "password": "Gy280956117"
}
```

**响应**:
```json
{
    "success": true,
    "message": "登录成功",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

#### POST /crm/api/logout
登出接口

#### POST /crm/api/register
注册接口（需要管理员审核）

---

### 用户管理（admin 权限）

#### GET /crm/api/users
获取所有用户列表

#### PUT /crm/api/users/{id}/role
修改用户角色
```json
{"role": "manager"}  // admin/manager/sales
```

#### PUT /crm/api/users/{id}/status
修改用户状态
```json
{"status": 1}  // 0待审核/1启用/2禁用
```

#### DELETE /crm/api/users/{id}
删除用户

---

### 商机管理

#### GET /crm/api/opportunities
获取商机列表
- admin/manager: 查看全部
- sales: 仅查看自己的

#### POST /crm/api/opportunities
创建商机
```json
{
    "title": "商机标题",
    "customer_name": "客户名称",
    "customer_contact": "联系方式",
    "expected_amount": 100000,
    "expected_close_date": "2026-06-01",
    "priority": "high",  // high/medium/low
    "description": "商机描述"
}
```

#### GET /crm/api/opportunities/{id}
获取商机详情

#### PUT /crm/api/opportunities/{id}/status
更新商机状态
```json
{"status": "reviewing"}  // new/reviewing/approved/rejected/online/closed
```

#### DELETE /crm/api/opportunities/{id}
删除商机

---

### 评审中心（admin/manager 权限）

#### GET /crm/api/reviews/pending
获取待评审列表

#### POST /crm/api/opportunities/{id}/review
提交评审
```json
{
    "decision": "approved",  // approved/rejected
    "comment": "评审意见"
}
```

---

### 项目管理

#### GET /crm/api/projects
获取项目列表

#### POST /crm/api/opportunities/{id}/launch
商机上线（创建项目）
```json
{
    "project_name": "项目名称",
    "actual_amount": 120000,
    "launch_date": "2026-03-20",
    "notes": "项目备注"
}
```

#### PUT /crm/api/projects/{id}/close
关闭项目

---

### 仪表盘

#### GET /crm/api/dashboard/stats
获取统计数据
```json
{
    "total": 10,           // 总商机数
    "pending_review": 2,   // 待评审数
    "online": 5,           // 已上线数
    "this_month": 3        // 本月新增
}
```

#### GET /crm/api/me
获取当前登录用户信息

---

## 🎨 前端页面说明

### 页面路由

| 路径 | 页面 | 权限 |
|------|------|------|
| /crm/login | 登录/注册 | 公开 |
| /crm/dashboard | 仪表盘 | 登录用户 |
| /crm/opportunities | 商机管理 | 登录用户 |
| /crm/reviews | 评审中心 | admin/manager |
| /crm/projects | 项目管理 | 登录用户 |
| /crm/users | 用户管理 | admin |

### 前端技术特点

- **纯原生 JS**: 无框架依赖，使用 fetch API 进行后端通信
- **Session 认证**: 使用 Flask session 维护登录状态
- **响应式布局**: CSS Grid + Flexbox 适配不同屏幕
- **模态框交互**: 新增/编辑使用模态框，避免页面跳转

### 核心函数

```javascript
// 页面跳转
function goTo(url) {
    window.location.href = url;
}

// API 请求示例
async function loadOpportunities() {
    const res = await fetch('/crm/api/opportunities');
    const data = await res.json();
    // 渲染列表
}
```

---

## ⚙️ 部署配置

### Nginx 配置

文件位置: `/www/server/panel/vhost/nginx/hello-api.conf`

```nginx
upstream flask_app {
    server 127.0.0.1:8723;
}

upstream hello_world {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name 47.99.105.13;
    
    # CRM 系统 - 子目录方式
    location /crm/ {
        proxy_pass http://flask_app/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Prefix /crm;
    }
    
    # Hello World 应用
    location / {
        proxy_pass http://hello_world;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/ {
        proxy_pass http://hello_world;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 启动命令

```bash
# 启动 Flask 应用（端口 8723）
cd /www/crm-system
nohup python3 app.py > /var/log/crm-system.log 2>&1 &

# 重启 Nginx
/etc/init.d/nginx reload
```

### 关键配置项

```python
# Flask 配置
app.secret_key = secrets.token_hex(32)  # Session 密钥
URL_PREFIX = '/crm'                      # URL 前缀
DB_PATH = '/www/crm-system/data.db'      # 数据库路径

# 运行配置
app.run(host='0.0.0.0', port=8723, debug=False)
```

---

## 🔐 安全注意事项

1. **密码存储**: 使用 SHA256 哈希，生产环境建议使用 bcrypt
2. **Session 安全**: 使用随机生成的 secret_key
3. **权限控制**: 每个 API 都有权限装饰器保护
4. **SQL 注入防护**: 使用参数化查询
5. **XSS 防护**: 前端渲染使用 textContent 而非 innerHTML

---

## 📝 迭代开发建议

### 可能的优化方向

1. **数据库迁移**: 从 SQLite 升级到 MySQL/PostgreSQL 支持更高并发
2. **密码加密**: 使用 bcrypt 替代 SHA256
3. **文件上传**: 完善 uploads 目录的文件上传功能
4. **搜索过滤**: 添加商机列表的搜索和筛选功能
5. **分页**: 大数据量时添加分页支持
6. **日志**: 添加操作日志记录
7. **邮件通知**: 注册/评审通过时发送邮件
8. **数据导出**: 支持 Excel/PDF 导出

### 代码维护

```bash
# 查看日志
tail -f /var/log/crm-system.log

# 备份数据库
cp /www/crm-system/data.db /backup/crm-data-$(date +%Y%m%d).db

# 重启服务
pkill -f "python3 app.py"
cd /www/crm-system && nohup python3 app.py > /var/log/crm-system.log 2>&1 &
```

---

## 📞 联系方式

**部署服务器**: 阿里云 ECS 47.99.105.13  
**开发维护**: OpenClaw Agent (Saber)  
**创建日期**: 2026-03-19

---

*文档版本: v1.0*  
*最后更新: 2026-03-19*

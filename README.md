# 极简商城 - Vue 3 + FastAPI + SQLite

基于 Vue 3 + Python FastAPI + SQLite 的极简线上商城系统。

## 技术栈

- **后端**: Python FastAPI + SQLite
- **前端**: Vue 3 + Element Plus + Vite
- **部署**: Docker + Docker Compose

## 功能模块

- ✅ 用户登录/注册（BCrypt加密）
- ✅ 商品列表/详情
- ✅ 购物车管理
- ✅ 订单生成

## 快速启动

### 1. 准备环境

```bash
# 安装 Docker 和 Docker Compose
```

### 2. 启动服务

```bash
cd mall
docker-compose up -d
```

### 3. 访问

- 前端: http://localhost:8080
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 本地开发

### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
mall/
├── backend/           # 后端代码
│   ├── main.py       # FastAPI入口
│   ├── database.py   # SQLite数据库
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.sh
├── frontend/         # 前端代码
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   ├── api/     # API封装
│   │   └── router/  # 路由配置
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── git_auto_push.py  # 自动推送脚本
├── issue_monitor.py  # Issue监控脚本
├── DEVELOPER_PROMPT.md # 开发Agent提示词
└── README.md
```

## 自动化脚本

### 自动推送 (git_auto_push.py)

每30分钟自动推送到GitHub：

```bash
python git_auto_push.py
```

### Issue监控 (issue_monitor.py)

每10分钟检测Bug Issue并自动修复：

```bash
pip install pygithub
python issue_monitor.py
```

## 环境变量

### 后端

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MALL_DATA_PATH | 数据库目录 | /app/data |

### 前端

| 变量 | 说明 | 默认值 |
|------|------|--------|
| VITE_API_URL | API地址 | http://localhost:8000 |

### Docker Compose

| 变量 | 说明 |
|------|------|
| GITHUB_TOKEN | GitHub Personal Access Token（用于自动推送和Issue监控） |

## 数据目录

- 本地开发: `./data/`
- Docker: `/volume2/docker/mall-data`

## API接口

- `POST /api/user/register` - 用户注册
- `POST /api/user/login` - 用户登录
- `GET /api/product/list` - 商品列表
- `GET /api/product/detail/{id}` - 商品详情
- `POST /api/cart/add` - 加入购物车
- `POST /api/cart/update` - 更新购物车
- `GET /api/cart/list` - 购物车列表
- `POST /api/order/create` - 创建订单
- `GET /api/order/list` - 订单列表

## GitHub仓库

```
https://github.com/zkk515/mall-vue-python.git
```

## License

MIT

# Timecapsule

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Vue](https://img.shields.io/badge/Vue.js-3.x-green)


## 📖 项目介绍 

该项目旨在开发一款以“时间”和“地点”为核心的数字记忆平台，通过在校园场景中捕捉
并保存具有情感意义的瞬间，实现校园记忆的数字化存储与共享。系统将连接在校生与校友
群体，使他们能够在特定地点回溯过往记忆，或为后来的学子留下数字足迹，从而促进校园
文化的传承与情感共鸣。

## 📸 截图展示

![截图2](docs/images/2.png)
![截图1](docs/images/1.png)
![截图3](docs/images/3.png)


## 🛠 技术栈 

* **Frontend**: Vue 3, Vite, Axios, Pinia
* **Backend**: Python, FastAPI, SQLAlchemy
* **Database**: MySQL 
* **Tools**: Docker, Git

## ⚡ 快速开始

### 环境要求
* Node.js >= 16
* Python >= 3.9
* MySQL >= 5.7

### 安装步骤

1. **克隆项目**
```bash
git clone https://gitlab.com/tj-cs-swe/CS10102302-2025/group15/timecapsule.git
cd timecapsule
```

2. **后端设置**
```bash
cd backend
conda env create -f environment.yml
conda activate TimeCapsule
docker compose up --build -d ##这一步前请先启动docker
docker exec -it timecapsule_backend python scripts/init_database.py
```

3. **前端设置**
```bash
cd frontend
npm install
npm run serve
```

4. **环境配置**

本项目依赖环境变量进行配置。请在 backend 目录下创建 .env 文件。您可以复制模板文件

5. **项目运行**
```bash
docker compose up -d ##后端
npm run dev          ##前端
```

6. **项目部署**
```bash
setup.sh
```

## 📂 目录主要结构
```Plaintext
Project-Name/
├── backend/               # 后端项目源码
│   ├── app/
│   │   ├── api/           # API 路由接口
│   │   ├── core/          # 核心配置 (config, security)
│   │   ├── crud/          # 数据库 CRUD 操作
│   │   ├── models/        # 数据库模型 (SQLAlchemy)
│   │   └── schemas/       # Pydantic 数据验证模型
│   ├── main.py            # 程序入口
│   └── requirements.txt
├── frontend/              # 前端项目源码
│   ├── src/
│   │   ├── router/        # 前端路由
│   │   ├── api/           # api
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── views/         # 页面视图
│   │   └── stores/        # 状态管理 (Pinia)
│   └── vite.config.ts
├── docs/                  # 项目文档与截图
└── README.md
```


## 📡 API 文档

本项目集成了 Swagger UI。启动后端服务后，访问以下地址查看交互式文档：

- Swagger UI: http://localhost:8000/docs

## 📄 许可证 | License

本项目遵循 [MIT License](LICENSE) 协议。
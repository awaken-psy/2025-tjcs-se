## 本地调试运行方法

先修改和添加后端的4个文件和feature-frontend-capsule分支上的一致

(注意这里的main.py中的cros部分代码只能本地调试用,.env的DB_HOST也是只能本地用)

(docker-compose.yml和init_database.py是否能用不知道)

创建后端容器

```bash
(base) PS D:\web-p\TimeCapsule\backend> conda env create -f environment.yml
(base) PS D:\web-p\TimeCapsule\backend> conda activate TimeCapsule
# 这步要打开dockerdesktop，如果下载镜像不行，要把setting-resource-proxy的手动设置代理关掉
(TimeCapsule) PS D:\web-p\TimeCapsule\backend> docker compose up --build -d
```

初始化数据库

```bash
(TimeCapsule) PS D:\web-p\TimeCapsule\backend> docker exec -it timecapsule_backend python scripts/init_database.py
```

查看docker环境,输出应有两个环境

```bash
(TimeCapsule) PS D:\web-p\TimeCapsule\backend> docker ps
CONTAINER ID   IMAGE             COMMAND                   CREATED          STATUS                   PORTS                               NAMES
4de02e6827e6   backend-backend   "uvicorn app.main:ap…"   7 minutes ago    Up 7 minutes             0.0.0.0:8000->8000/tcp              timecapsule_backend
880f69c6183d   mysql:8.0         "docker-entrypoint.s…"   11 minutes ago   Up 7 minutes (healthy)   0.0.0.0:3306->3306/tcp, 33060/tcp   timecapsule_mysql
```

设置日志为动态刷新

```bash
(TimeCapsule) PS D:\web-p\TimeCapsule\backend> docker logs -f timecapsule_backend
```

数据库操作

```bash
docker exec -it timecapsule_mysql bash
# root 密码是docker-compose.yml 中 MYSQL_ROOT_PASSWORD 的值
mysql -u root -p Markov@2025

......

\q  # 退出 mysql 客户端
exit  # 退出容器 bash
```

启动与停止docker

```bash
docker compose up -d

docker compose stop
```
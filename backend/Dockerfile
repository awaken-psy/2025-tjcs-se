FROM python:3.11
WORKDIR /app
COPY . /app

# 配置基础环境变量（非敏感信息）
ENV DB_TYPE=mysql
ENV DB_PORT=3306
ENV DB_ECHO=true
ENV APP_ENV=development
ENV APP_DEBUG=true

# 使用清华源加速安装
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# 移除额外的MySQL驱动安装，避免与pymysql冲突
# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple mysql-connector-python
EXPOSE 8000
CMD ["python", "app/main.py"]

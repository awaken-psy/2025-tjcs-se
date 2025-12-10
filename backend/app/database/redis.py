# app/database/redis.py (示例)
import redis
import os

# 从环境变量获取 Redis 连接配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost") 
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# 实例化全局 Redis 客户端
# 注意：在 Docker Compose 中，REDIS_HOST 应设置为 Docker 服务名 'redis'
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        password=REDIS_PASSWORD, 
        decode_responses=True # 确保返回的是字符串而不是字节
    )
    redis_client.ping()
    print("Redis 连接成功!")
except Exception as e:
    print(f"Redis 连接失败: {e}")
    redis_client = None # 如果连接失败，使用 None 占位
# 例如：在 app/core/exceptions.py 中定义

class RecordNotFoundException(Exception):
    """自定义异常：当请求的记录在数据库中不存在时抛出"""
    def __init__(self, message="请求的记录不存在"):
        self.message = message
        super().__init__(self.message)
        
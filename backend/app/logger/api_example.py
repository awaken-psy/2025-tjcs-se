"""
API日志装饰器使用示例
展示如何在FastAPI接口中使用api_logging装饰器
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.logger import api_logger, api_logging

# 创建路由器
example_router = APIRouter(prefix='/example', tags=['API日志示例'])


# 请求模型示例
class ExampleRequest(BaseModel):
    name: str
    message: Optional[str] = None


# 响应模型示例
class ExampleResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


@example_router.post("/test")
@api_logging(api_logger)  # 使用装饰器记录API调用
async def test_api_logging(req_data: ExampleRequest):
    """
    测试API日志装饰器的接口

    Args:
        request: FastAPI Request对象（装饰器需要）
        req_data: 请求数据

    Returns:
        JSON响应
    """
    # 模拟一些业务逻辑
    result_data = {
        "received_name": req_data.name,
        "received_message": req_data.message,
        "processing_time": "fast"
    }

    return ExampleResponse(
        success=True,
        message="API调用成功",
        data=result_data
    )


@example_router.get("/path-params/{user_id}")
@api_logging(api_logger)  # 使用装饰器记录API调用
async def test_path_params(user_id: int, query: str = "default"):
    """
    测试路径参数和查询参数的API

    Args:
        request: FastAPI Request对象
        user_id: 路径参数
        query: 查询参数

    Returns:
        JSON响应
    """
    return JSONResponse({
        "success": True,
        "user_id": user_id,
        "query_param": query,
        "message": f"获取到用户 {user_id} 的数据"
    })


@example_router.post("/error-example")
@api_logging(api_logger)  # 使用装饰器记录API调用
async def test_error_handling(req_data: ExampleRequest):
    """
    测试错误处理的API

    Args:
        request: FastAPI Request对象
        req_data: 请求数据

    Returns:
        JSON响应或抛出异常
    """
    # 模拟不同的错误情况
    if req_data.name == "error":
        raise ValueError("这是一个模拟的错误")
    elif req_data.name == "http_error":
        raise HTTPException(status_code=400, detail="这是一个HTTP异常")

    return ExampleResponse(
        success=True,
        message="处理成功",
        data={"input_name": req_data.name}
    )


# 使用说明注释
"""
使用API日志装饰器的步骤：

1. 导入必要的模块：
   from app.logger import api_logger, api_logging

2. 在API接口函数上添加装饰器：
   @api_logging(api_logger)

3. 装饰器会自动记录：
   - 接口名称（模块名.函数名）
   - 所有参数名和参数值（包括Pydantic模型）
   - 响应内容
   - 处理总用时（毫秒）
   - 异常信息（如果有）

4. 对于Pydantic模型参数，装饰器会自动调用.dict()方法获取数据

5. 装饰器支持：
   - 基本数据类型（str, int, float, bool）
   - Pydantic模型（自动转换为字典）
   - 普通对象（转换为字符串）
   - 字典、列表、元组（递归处理）
   - None值

示例用法：
   @api_logging(api_logger)
   async def create_capsule(request: CapsuleCreateRequest, user: AuthorizedUser):
       # 业务逻辑
       pass

注意事项：
- 所有日志都以JSON格式输出，便于分析
- 装饰器不会改变原函数的返回值
- 异常会被正确重新抛出，不影响业务逻辑
- 无法序列化的对象会显示类型名称
"""
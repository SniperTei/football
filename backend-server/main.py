from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    business_exception_handler,
    general_exception_handler
)
from app.service.exceptions import BusinessException

app = FastAPI(
    title="Football Platform API",
    description="足球球队数据管理平台 API",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, business_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Football Platform API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

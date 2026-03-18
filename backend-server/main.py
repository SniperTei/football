from contextlib import asynccontextmanager
import logging
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
from app.core.db_init import init_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting Football Platform API...")
    try:
        init_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # 数据库初始化失败不阻止应用启动
        # 因为数据库可能已经存在或者应用会稍后重试连接

    yield

    # 关闭时执行（可选）
    logger.info("Shutting down Football Platform API...")


app = FastAPI(
    title="Football Platform API",
    description="足球球队数据管理平台 API",
    version="2.0.0",
    lifespan=lifespan
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

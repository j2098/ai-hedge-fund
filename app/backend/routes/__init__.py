from fastapi import APIRouter

from app.backend.routes.hedge_fund import router as hedge_fund_router
from app.backend.routes.health import router as health_router

# 尝试导入Moomoo路由
try:
    from app.backend.routes.moomoo import router as moomoo_router
    MOOMOO_ROUTER_AVAILABLE = True
except ImportError:
    MOOMOO_ROUTER_AVAILABLE = False

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(hedge_fund_router, tags=["hedge-fund"])

# 如果Moomoo路由可用，则包含它
if MOOMOO_ROUTER_AVAILABLE:
    api_router.include_router(moomoo_router)

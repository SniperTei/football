from fastapi import APIRouter
from app.api.routes import auth, teams, team_members, players

api_router = APIRouter()

# 认证路由（公开）
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 球队路由（公开查看，需要登录才能修改）
api_router.include_router(teams.router, prefix="/teams", tags=["球队"])

# 球员路由（公开查看，需要登录才能修改）
api_router.include_router(players.router, prefix="/players", tags=["球员"])

# 球队成员权限路由（需要登录）
api_router.include_router(team_members.router, tags=["球队成员权限"])

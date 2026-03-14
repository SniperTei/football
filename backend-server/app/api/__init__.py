from fastapi import APIRouter
from app.api.routes import auth, teams, players, matches, match_players, stats

api_router = APIRouter()

# 认证路由（公开）
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 球队路由（公开查看，需要登录才能修改）
api_router.include_router(teams.router, prefix="/teams", tags=["球队"])

# 球员路由（公开查看，需要登录才能修改）
api_router.include_router(players.router, prefix="/players", tags=["球员"])

# 比赛路由（需要登录）
api_router.include_router(matches.router, prefix="/matches", tags=["比赛"])

# 比赛球员统计路由（需要登录）
api_router.include_router(match_players.router, prefix="/match-players", tags=["比赛球员统计"])

# 统计数据路由（公开）
api_router.include_router(stats.router, prefix="/stats", tags=["统计"])

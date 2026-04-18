"""
Excel 数据报表导出脚本
在 backend 容器内执行: python /app/scripts/export_excel.py <output_path>

导出 2 个 Sheet:
- 比赛记录: 日期、主队、客队、比分、类型、场地、状态
- 球员比赛统计: 比赛日期、球员姓名、球队、是否出场、进球、助攻、黄牌、红牌
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from app.core.database import SessionLocal
from app.models import Match, MatchPlayer


def export_excel(output_path: str):
    db = SessionLocal()
    try:
        # Sheet 1: 比赛记录
        matches = db.query(Match).order_by(Match.match_date.desc()).all()
        match_data = []
        for m in matches:
            match_data.append({
                '日期': m.match_date.strftime('%Y-%m-%d %H:%M'),
                '主队': m.home_team.name if m.home_team else '-',
                '客队': m.away_team.name if m.away_team else '-',
                '主队比分': m.home_score,
                '客队比分': m.away_score,
                '类型': m.match_type,
                '场地': m.venue or '-',
                '状态': m.status,
                '备注': m.notes or ''
            })

        # Sheet 2: 球员比赛统计
        player_stats = db.query(MatchPlayer).join(Match).order_by(Match.match_date.desc()).all()
        stats_data = []
        for ps in player_stats:
            stats_data.append({
                '比赛日期': ps.match.match_date.strftime('%Y-%m-%d %H:%M'),
                '球员姓名': ps.player.name if ps.player else '-',
                '球队': ps.team.name if ps.team else '-',
                '是否出场': '是' if ps.played else '否',
                '进球': ps.goals,
                '助攻': ps.assists,
                '黄牌': ps.yellow_cards,
                '红牌': ps.red_cards,
                '位置': ps.position or '-',
                '号码': ps.jersey_number or '-'
            })

        # 写入 Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            pd.DataFrame(match_data).to_excel(writer, sheet_name='比赛记录', index=False)
            pd.DataFrame(stats_data).to_excel(writer, sheet_name='球员统计', index=False)

        print(f"Excel 导出成功: {output_path}")
        print(f"  比赛记录: {len(match_data)} 条")
        print(f"  球员统计: {len(stats_data)} 条")
    finally:
        db.close()


if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else 'report.xlsx'
    export_excel(output)

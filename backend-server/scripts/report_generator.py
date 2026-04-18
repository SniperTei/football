"""
球队月度报告 PDF 生成模块
"""

import os
import calendar
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Integer as SaInteger

from app.models.match import Match, MatchStatus
from app.models.match_player import MatchPlayer
from app.models.player import Player
from app.models.team import Team


# ── 中文字体注册 ──────────────────────────────────────────────

_font_registered = False


def _register_font():
    global _font_registered
    if _font_registered:
        return
    _font_registered = True
    print(f"[DEBUG] Font search paths: {font_dirs}")

    # 优先查找项目 fonts 目录
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_dirs = [
        os.path.join(base_dir, "scripts", "fonts"),
        os.path.join(base_dir, "frontend-pc", "public", "fonts"),
        "/usr/share/fonts/truetype/wqy",
        "/usr/share/fonts/wqy-zenhei",
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/opentype/noto",
        "/System/Library/Fonts",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
        "/app/fonts",
    ]

    font_name = "ChineseFont"
    font_file = None
    for d in font_dirs:
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            lower = fname.lower()
            if lower.endswith((".ttf", ".ttc")):
                if any(
                    k in lower
                    for k in (
                        "pingfang",
                        "heiti",
                        "yahei",
                        "songti",
                        "noto",
                        "source",
                        "simhei",
                        "simsun",
                        "wqy",
                        "wenquanyi",
                    )
                ):
                    font_file = os.path.join(d, fname)
                    break
        if font_file:
            break

    if not font_file:
        candidates = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
            "/usr/share/fonts/wqy-zenhei/wqy-microhei.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
        for c in candidates:
            if os.path.exists(c):
                font_file = c
                break

    if font_file:
        try:
            print(f"[DEBUG] Found font: {font_file}")
            if font_file.lower().endswith(".ttc"):
                pdfmetrics.registerFont(TTFont(font_name, font_file, subfontIndex=0))
            else:
                pdfmetrics.registerFont(TTFont(font_name, font_file))
            print(f"[DEBUG] Font registered successfully: {font_name}")
            return
        except Exception as e:
            print(f"[DEBUG] Font register failed: {e}")

    # 最终 fallback: 使用 reportlab 内置字体（不支持中文，但不会崩溃）
    font_name = "Helvetica"


def _get_font_name() -> str:
    _register_font()
    return "ChineseFont" if "ChineseFont" in pdfmetrics._fonts else "Helvetica"


# ── 样式构建 ──────────────────────────────────────────────────


def _build_styles() -> Dict[str, ParagraphStyle]:
    font = _get_font_name()
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName=font,
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=6 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName=font,
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=8 * mm,
            textColor=colors.grey,
        ),
        "section": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading2"],
            fontName=font,
            fontSize=14,
            leading=20,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            textColor=colors.HexColor("#1a73e8"),
        ),
        "normal": ParagraphStyle(
            "NormalCN",
            parent=base["Normal"],
            fontName=font,
            fontSize=9,
            leading=14,
        ),
        "small": ParagraphStyle(
            "SmallCN",
            parent=base["Normal"],
            fontName=font,
            fontSize=8,
            leading=12,
        ),
        "highlight": ParagraphStyle(
            "Highlight",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#e6a23c"),
        ),
    }
    return styles


# ── 数据查询 ──────────────────────────────────────────────────


def _get_month_range(year: int, month: int):
    """返回月份起止 datetime"""
    start = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return start, end


def _query_team_matches(
    db: Session, team_id: int, start: datetime, end: datetime
) -> List[Match]:
    return (
        db.query(Match)
        .filter(
            Match.status == MatchStatus.COMPLETED,
            Match.match_date >= start,
            Match.match_date <= end,
            ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
        )
        .order_by(Match.match_date)
        .all()
    )


def _compute_team_stats(matches: List[Match], team_id: int) -> Dict[str, Any]:
    wins = draws = losses = goals_for = goals_against = clean_sheets = 0
    for m in matches:
        is_home = m.home_team_id == team_id
        gf = m.home_score if is_home else m.away_score
        ga = m.away_score if is_home else m.home_score
        gf = gf or 0
        ga = ga or 0
        goals_for += gf
        goals_against += ga
        if gf > ga:
            wins += 1
        elif gf == ga:
            draws += 1
        else:
            losses += 1
        if ga == 0:
            clean_sheets += 1

    total = len(matches)
    return {
        "total": total,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": round(wins / total * 100, 1) if total else 0,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_diff": goals_for - goals_against,
        "clean_sheets": clean_sheets,
    }


def _query_player_ranking(
    db: Session, match_ids: List[int], team_id: int, sort_col: str, limit: int = 10
) -> List[Dict]:
    if not match_ids:
        return []

    subq = (
        db.query(
            MatchPlayer.player_id,
            func.sum(MatchPlayer.goals).label("goals"),
            func.sum(MatchPlayer.assists).label("assists"),
            func.sum(func.cast(MatchPlayer.played, SaInteger)).label("played"),
        )
        .filter(MatchPlayer.match_id.in_(match_ids), MatchPlayer.team_id == team_id)
        .group_by(MatchPlayer.player_id)
        .subquery()
    )

    rows = (
        db.query(
            Player.name,
            subq.c.goals,
            subq.c.assists,
            subq.c.played,
        )
        .join(subq, Player.id == subq.c.player_id)
        .order_by(desc(getattr(subq.c, sort_col)))
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": i + 1,
            "name": r.name,
            "goals": int(r.goals or 0),
            "assists": int(r.assists or 0),
            "played": int(r.played or 0),
        }
        for i, r in enumerate(rows)
    ]


def _query_match_details(matches: List[Match], team_id: int) -> List[Dict]:
    result = []
    for m in matches:
        is_home = m.home_team_id == team_id
        gf = m.home_score if is_home else m.away_score
        ga = m.away_score if is_home else m.home_score
        gf = gf or 0
        ga = ga or 0
        if gf > ga:
            res = "胜"
        elif gf == ga:
            res = "平"
        else:
            res = "负"
        opponent = m.away_team.name if is_home else m.home_team.name
        result.append(
            {
                "date": m.match_date.strftime("%Y-%m-%d"),
                "opponent": opponent,
                "score": f"{gf}:{ga}",
                "venue": "主场" if is_home else "客场",
                "result": res,
            }
        )
    return result


def _compute_highlights(
    db: Session, match_ids: List[int], team_id: int, matches: List[Match]
) -> List[str]:
    highlights = []

    if not match_ids or not matches:
        return ["本月无比赛数据"]

    # 单场进球最多球员（帽子戏法等）
    if match_ids:
        top_scorer = (
            db.query(
                Player.name,
                MatchPlayer.match_id,
                MatchPlayer.goals,
            )
            .join(MatchPlayer, Player.id == MatchPlayer.player_id)
            .filter(
                MatchPlayer.match_id.in_(match_ids),
                MatchPlayer.team_id == team_id,
                MatchPlayer.goals > 0,
            )
            .order_by(desc(MatchPlayer.goals))
            .first()
        )
        if top_scorer and top_scorer.goals >= 3:
            highlights.append(
                f"帽子戏法: {top_scorer.name} 单场攻入 {top_scorer.goals} 球"
            )
        elif top_scorer and top_scorer.goals >= 2:
            highlights.append(
                f"梅开二度: {top_scorer.name} 单场攻入 {top_scorer.goals} 球"
            )

    # 零封场次
    stats = _compute_team_stats(matches, team_id)
    if stats["clean_sheets"] > 0:
        highlights.append(f"零封场次: {stats['clean_sheets']} 场")

    # 最大比分胜利
    best = None
    for m in matches:
        is_home = m.home_team_id == team_id
        gf = (m.home_score if is_home else m.away_score) or 0
        ga = (m.away_score if is_home else m.home_score) or 0
        diff = gf - ga
        if diff > 0:
            if best is None or diff > best[0]:
                opponent = m.away_team.name if is_home else m.home_team.name
                best = (diff, f"{gf}:{ga}", opponent)
    if best:
        highlights.append(f"最大比分胜利: {best[1]} 胜 {best[2]}")

    # 最多出场球员
    subq = (
        db.query(
            Player.name,
            func.sum(func.cast(MatchPlayer.played, SaInteger)).label("cnt"),
        )
        .join(MatchPlayer, Player.id == MatchPlayer.player_id)
        .filter(MatchPlayer.match_id.in_(match_ids), MatchPlayer.team_id == team_id)
        .group_by(Player.id, Player.name)
        .order_by(desc(func.sum(func.cast(MatchPlayer.played, SaInteger))))
        .first()
    )
    if subq and subq.cnt and subq.cnt > 0:
        highlights.append(f"铁人: {subq.name} 本月出场 {int(subq.cnt)} 次")

    return highlights if highlights else ["暂无高光数据"]


# ── PDF 构建辅助 ──────────────────────────────────────────────


def _make_table(
    headers: List[str],
    rows: List[List[str]],
    col_widths: List[float],
    styles: Dict[str, ParagraphStyle],
) -> Table:
    """构建统一风格的表格"""
    font = _get_font_name()
    header_cells = [Paragraph(h, styles["small"]) for h in headers]
    data = [header_cells]
    for row in rows:
        data.append([Paragraph(str(c), styles["small"]) for c in row])

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d0d0")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f5f7fa")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tbl


# ── 主函数 ────────────────────────────────────────────────────


def generate_monthly_report(
    db: Session, team_id: int, year: int, month: int, output_path: Optional[str] = None
) -> BytesIO:
    """
    生成球队月度报告 PDF

    Args:
        db: SQLAlchemy Session
        team_id: 球队 ID
        year: 年份
        month: 月份
        output_path: 可选，同时写入文件路径

    Returns:
        BytesIO containing PDF data
    """
    _register_font()
    styles = _build_styles()

    # ── 查询数据 ──
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise ValueError(f"球队 {team_id} 不存在")

    start, end = _get_month_range(year, month)
    matches = _query_team_matches(db, team_id, start, end)
    match_ids = [m.id for m in matches]
    team_stats = _compute_team_stats(matches, team_id)
    goal_ranking = _query_player_ranking(db, match_ids, team_id, "goals")
    assist_ranking = _query_player_ranking(db, match_ids, team_id, "assists")
    match_details = _query_match_details(matches, team_id)
    highlights = _compute_highlights(db, match_ids, team_id, matches)

    # ── 构建 PDF ──
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    story: list = []
    page_width = A4[0] - 4 * cm  # 可用宽度

    # 标题
    story.append(Paragraph(f"{team.name} 月度报告", styles["title"]))
    story.append(Paragraph(f"{year} 年 {month} 月", styles["subtitle"]))
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a73e8"))
    )
    story.append(Spacer(1, 4 * mm))

    # ── 1. 球队概况 ──
    story.append(Paragraph("球队概况", styles["section"]))
    overview_data = [
        [
            Paragraph("比赛场次", styles["small"]),
            Paragraph(str(team_stats["total"]), styles["small"]),
            Paragraph("胜", styles["small"]),
            Paragraph(str(team_stats["wins"]), styles["small"]),
            Paragraph("平", styles["small"]),
            Paragraph(str(team_stats["draws"]), styles["small"]),
            Paragraph("负", styles["small"]),
            Paragraph(str(team_stats["losses"]), styles["small"]),
        ],
        [
            Paragraph("胜率", styles["small"]),
            Paragraph(f"{team_stats['win_rate']}%", styles["small"]),
            Paragraph("进球", styles["small"]),
            Paragraph(str(team_stats["goals_for"]), styles["small"]),
            Paragraph("失球", styles["small"]),
            Paragraph(str(team_stats["goals_against"]), styles["small"]),
            Paragraph("净胜球", styles["small"]),
            Paragraph(str(team_stats["goal_diff"]), styles["small"]),
        ],
    ]
    cw = page_width / 8
    overview_tbl = Table(overview_data, colWidths=[cw] * 8)
    overview_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), _get_font_name()),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d0d0")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f5ff")),
                ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f0f5ff")),
                ("BACKGROUND", (4, 0), (4, -1), colors.HexColor("#f0f5ff")),
                ("BACKGROUND", (6, 0), (6, -1), colors.HexColor("#f0f5ff")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(overview_tbl)
    story.append(Spacer(1, 3 * mm))

    # 零封补充
    story.append(
        Paragraph(f"零封场次: {team_stats['clean_sheets']} 场", styles["normal"])
    )
    story.append(Spacer(1, 4 * mm))

    # ── 2. 射手榜 ──
    story.append(Paragraph("射手榜 Top 10", styles["section"]))
    if goal_ranking:
        rows = [
            [
                str(r["rank"]),
                r["name"],
                str(r["goals"]),
                str(r["assists"]),
                str(r["played"]),
            ]
            for r in goal_ranking
        ]
        story.append(
            _make_table(
                ["排名", "球员", "进球", "助攻", "出场"],
                rows,
                [1.2 * cm, page_width * 0.4, 2 * cm, 2 * cm, 2 * cm],
                styles,
            )
        )
    else:
        story.append(Paragraph("本月暂无进球数据", styles["normal"]))
    story.append(Spacer(1, 4 * mm))

    # ── 3. 助攻榜 ──
    story.append(Paragraph("助攻榜 Top 10", styles["section"]))
    if assist_ranking:
        rows = [
            [
                str(r["rank"]),
                r["name"],
                str(r["goals"]),
                str(r["assists"]),
                str(r["played"]),
            ]
            for r in assist_ranking
        ]
        story.append(
            _make_table(
                ["排名", "球员", "进球", "助攻", "出场"],
                rows,
                [1.2 * cm, page_width * 0.4, 2 * cm, 2 * cm, 2 * cm],
                styles,
            )
        )
    else:
        story.append(Paragraph("本月暂无助攻数据", styles["normal"]))
    story.append(Spacer(1, 4 * mm))

    # ── 4. 比赛明细 ──
    story.append(Paragraph("比赛明细", styles["section"]))
    if match_details:
        rows = [
            [m["date"], m["opponent"], m["score"], m["venue"], m["result"]]
            for m in match_details
        ]
        story.append(
            _make_table(
                ["日期", "对手", "比分", "主/客", "结果"],
                rows,
                [2.5 * cm, page_width * 0.35, 2 * cm, 1.8 * cm, 1.5 * cm],
                styles,
            )
        )
    else:
        story.append(Paragraph("本月暂无比赛", styles["normal"]))
    story.append(Spacer(1, 4 * mm))

    # ── 5. 高光时刻 ──
    story.append(Paragraph("高光时刻", styles["section"]))
    for h in highlights:
        story.append(Paragraph(f"  - {h}", styles["normal"]))

    # ── 页脚 ──
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(
        Paragraph(
            f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle(
                "Footer",
                parent=styles["small"],
                alignment=TA_CENTER,
                textColor=colors.grey,
            ),
        )
    )

    doc.build(story)

    # 可选写入文件
    if output_path:
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())
        buf.seek(0)

    buf.seek(0)
    return buf

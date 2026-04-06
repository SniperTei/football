"""
2026 FIFA World Cup 种子数据脚本
- 48 支球队（12 组 × 4 队）
- 72 场小组赛（C(4,2) × 12 = 72）

数据来源：2025-12-05 华盛顿抽签结果
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.wc_team import WCTeam
from app.models.wc_match import WCMatch


# fmt: off
WC_TEAMS = [
    # Group A
    {"name": "Mexico", "flag_url": "🇲🇽", "group_name": "A", "fifa_ranking": 15,
     "confederation": "CONCACAF", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 14, "recent_ga": 10, "wc_appearances": 17, "wc_best_result": "Quarter-finals (1970, 1986)",
     "wc_titles": 0, "key_players": json.dumps(["Santiago Giménez", "Hirving Lozano", "Edson Álvarez"]),
     "notes": "东道主之一，主场优势明显"},
    {"name": "Korea Republic", "flag_url": "🇰🇷", "group_name": "A", "fifa_ranking": 23,
     "confederation": "AFC", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 16, "recent_ga": 8, "wc_appearances": 11, "wc_best_result": "Semi-finals (2002)",
     "wc_titles": 0, "key_players": json.dumps(["Son Heung-min", "Lee Kang-in", "Kim Min-jae"]),
     "notes": "亚洲传统强队，孙兴慜领军"},
    {"name": "South Africa", "flag_url": "🇿🇦", "group_name": "A", "fifa_ranking": 57,
     "confederation": "CAF", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 10, "recent_ga": 9, "wc_appearances": 3, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Percy Tau", "Lyle Foster", "Ronwen Williams"]),
     "notes": "非洲杯常客，实力稳步提升"},
    {"name": "Czechia", "flag_url": "🇨🇿", "group_name": "A", "fifa_ranking": 42,
     "confederation": "UEFA", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 12, "recent_ga": 11, "wc_appearances": 1, "wc_best_result": "Group stage (2006)",
     "wc_titles": 0, "key_players": json.dumps(["Patrik Schick", "Vladimír Coufal", "Tomáš Souček"]),
     "notes": "捷克独立后第二次参加世界杯"},

    # Group B
    {"name": "Canada", "flag_url": "🇨🇦", "group_name": "B", "fifa_ranking": 47,
     "confederation": "CONCACAF", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 13, "recent_ga": 10, "wc_appearances": 3, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Alphonso Davies", "Jonathan David", "Cyle Larin"]),
     "notes": "东道主之一，近年来足球水平大幅提升"},
    {"name": "Switzerland", "flag_url": "🇨🇭", "group_name": "B", "fifa_ranking": 18,
     "confederation": "UEFA", "recent_wins": 5, "recent_draws": 3, "recent_losses": 2,
     "recent_gf": 13, "recent_ga": 8, "wc_appearances": 12, "wc_best_result": "Quarter-finals (1934, 1938, 1954)",
     "wc_titles": 0, "key_players": json.dumps(["Granit Xhaka", "Manuel Akanji", "Yann Sommer"]),
     "notes": "大赛常客，近几届均能小组出线"},
    {"name": "Qatar", "flag_url": "🇶🇦", "group_name": "B", "fifa_ranking": 52,
     "confederation": "AFC", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 11, "recent_ga": 12, "wc_appearances": 1, "wc_best_result": "Group stage (2022)",
     "wc_titles": 0, "key_players": json.dumps(["Akram Afif", "Almoez Ali", "Hassan Al-Haydos"]),
     "notes": "2022 世界杯主办国，积累了大赛经验"},
    {"name": "Bosnia and Herzegovina", "flag_url": "🇧🇦", "group_name": "B", "fifa_ranking": 66,
     "confederation": "UEFA", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 11, "recent_ga": 13, "wc_appearances": 1, "wc_best_result": "Group stage (2014)",
     "wc_titles": 0, "key_players": json.dumps(["Edin Džeko", "Miralem Pjanić", "Sead Kolašinac"]),
     "notes": "欧洲预选赛突围的黑马"},

    # Group C
    {"name": "Brazil", "flag_url": "🇧🇷", "group_name": "C", "fifa_ranking": 5,
     "confederation": "CONMEBOL", "recent_wins": 7, "recent_draws": 1, "recent_losses": 2,
     "recent_gf": 18, "recent_ga": 7, "wc_appearances": 22, "wc_best_result": "Champions (1958, 1962, 1970, 1994, 2002)",
     "wc_titles": 5, "key_players": json.dumps(["Vinícius Jr.", "Rodrygo", "Bruno Guimarães"]),
     "notes": "五届世界杯冠军，永远的热门"},
    {"name": "Morocco", "flag_url": "🇲🇦", "group_name": "C", "fifa_ranking": 12,
     "confederation": "CAF", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 15, "recent_ga": 6, "wc_appearances": 6, "wc_best_result": "Semi-finals (2022)",
     "wc_titles": 0, "key_players": json.dumps(["Achraf Hakimi", "Sofyan Amrabat", "Yassine Bounou"]),
     "notes": "2022 世界杯四强，非洲足球新标杆"},
    {"name": "Scotland", "flag_url": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "group_name": "C", "fifa_ranking": 34,
     "confederation": "UEFA", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 11, "recent_ga": 10, "wc_appearances": 8, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Andy Robertson", "Scott McTominay", "John McGinn"]),
     "notes": "时隔多年重返世界杯决赛圈"},
    {"name": "Haiti", "flag_url": "🇭🇹", "group_name": "C", "fifa_ranking": 83,
     "confederation": "CONCACAF", "recent_wins": 3, "recent_draws": 3, "recent_losses": 4,
     "recent_gf": 9, "recent_ga": 12, "wc_appearances": 1, "wc_best_result": "Group stage (1974)",
     "wc_titles": 0, "key_players": json.dumps(["Duckens Nazon", "Frantzdy Pierrot", "Bryan Alceus"]),
     "notes": "时隔 52 年重返世界杯"},

    # Group D
    {"name": "USA", "flag_url": "🇺🇸", "group_name": "D", "fifa_ranking": 16,
     "confederation": "CONCACAF", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 16, "recent_ga": 8, "wc_appearances": 11, "wc_best_result": "Semi-finals (1930)",
     "wc_titles": 0, "key_players": json.dumps(["Christian Pulisic", "Gio Reyna", "Folarin Balogun"]),
     "notes": "东道主之一，目标冲击八强"},
    {"name": "Australia", "flag_url": "🇦🇺", "group_name": "D", "fifa_ranking": 25,
     "confederation": "AFC", "recent_wins": 5, "recent_draws": 3, "recent_losses": 2,
     "recent_gf": 14, "recent_ga": 8, "wc_appearances": 6, "wc_best_result": "Round of 16 (2006)",
     "wc_titles": 0, "key_players": json.dumps(["Mathew Leckie", "Aaron Mooy", "Harry Souttar"]),
     "notes": "亚洲区劲旅，体能与对抗出色"},
    {"name": "Paraguay", "flag_url": "🇵🇾", "group_name": "D", "fifa_ranking": 55,
     "confederation": "CONMEBOL", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 10, "recent_ga": 11, "wc_appearances": 10, "wc_best_result": "Quarter-finals (2010)",
     "wc_titles": 0, "key_players": json.dumps(["Miguel Almirón", "Oscar Cardozo", "Antony Silva"]),
     "notes": "南美预选赛竞争激烈，成功突围"},
    {"name": "Turkiye", "flag_url": "🇹🇷", "group_name": "D", "fifa_ranking": 28,
     "confederation": "UEFA", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 14, "recent_ga": 10, "wc_appearances": 2, "wc_best_result": "Semi-finals (2002)",
     "wc_titles": 0, "key_players": json.dumps(["Hakan Çalhanoğlu", "Cengiz Ünder", "Çağlar Söyüncü"]),
     "notes": "时隔 24 年重返世界杯"},

    # Group E
    {"name": "Germany", "flag_url": "🇩🇪", "group_name": "E", "fifa_ranking": 3,
     "confederation": "UEFA", "recent_wins": 7, "recent_draws": 2, "recent_losses": 1,
     "recent_gf": 20, "recent_ga": 7, "wc_appearances": 20, "wc_best_result": "Champions (1954, 1974, 1990, 2014)",
     "wc_titles": 4, "key_players": json.dumps(["Jamal Musiala", "Florian Wirtz", "Joshua Kimmich"]),
     "notes": "四届世界杯冠军，新一代天才涌现"},
    {"name": "Ecuador", "flag_url": "🇪🇨", "group_name": "E", "fifa_ranking": 30,
     "confederation": "CONMEBOL", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 10, "recent_ga": 9, "wc_appearances": 4, "wc_best_result": "Round of 16 (2006)",
     "wc_titles": 0, "key_players": json.dumps(["Enner Valencia", "Moisés Caicedo", "Piero Hincapié"]),
     "notes": "南美高原主场是其优势，但客场也有进步"},
    {"name": "Ivory Coast", "flag_url": "🇨🇮", "group_name": "E", "fifa_ranking": 38,
     "confederation": "CAF", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 13, "recent_ga": 10, "wc_appearances": 3, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Sébastien Haller", "Nicolas Pépé", "Franck Kessié"]),
     "notes": "非洲杯冠军实力不俗"},
    {"name": "Curacao", "flag_url": "🇨🇼", "group_name": "E", "fifa_ranking": 80,
     "confederation": "CONCACAF", "recent_wins": 3, "recent_draws": 2, "recent_losses": 5,
     "recent_gf": 8, "recent_ga": 14, "wc_appearances": 0, "wc_best_result": "Debut",
     "wc_titles": 0, "key_players": json.dumps(["Leandro Bacuna", "Cuco Martina", "Juninho Bacuna"]),
     "notes": "首次参加世界杯决赛圈"},

    # Group F
    {"name": "Netherlands", "flag_url": "🇳🇱", "group_name": "F", "fifa_ranking": 7,
     "confederation": "UEFA", "recent_wins": 6, "recent_draws": 3, "recent_losses": 1,
     "recent_gf": 17, "recent_ga": 6, "wc_appearances": 11, "wc_best_result": "Runners-up (1974, 1978, 2010)",
     "wc_titles": 0, "key_players": json.dumps(["Virgil van Dijk", "Frenkie de Jong", "Cody Gakpo"]),
     "notes": "三届亚军，全攻全守传统的继承者"},
    {"name": "Japan", "flag_url": "🇯🇵", "group_name": "F", "fifa_ranking": 20,
     "confederation": "AFC", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 15, "recent_ga": 8, "wc_appearances": 7, "wc_best_result": "Round of 16 (2002, 2010, 2018, 2022)",
     "wc_titles": 0, "key_players": json.dumps(["Kaoru Mitoma", "Takefusa Kubo", "Wataru Endo"]),
     "notes": "亚洲技术流代表，2022 击败德国西班牙"},
    {"name": "Tunisia", "flag_url": "🇹🇳", "group_name": "F", "fifa_ranking": 35,
     "confederation": "CAF", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 10, "recent_ga": 9, "wc_appearances": 6, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Youssef Msakni", "Wahbi Khazri", "Dylan Bronn"]),
     "notes": "2022 世界杯击败法国，但未能出线"},
    {"name": "Sweden", "flag_url": "🇸🇪", "group_name": "F", "fifa_ranking": 26,
     "confederation": "UEFA", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 13, "recent_ga": 9, "wc_appearances": 12, "wc_best_result": "Runners-up (1958)",
     "wc_titles": 0, "key_players": json.dumps(["Alexander Isak", "Dejan Kulusevski", "Victor Lindelöf"]),
     "notes": "北欧劲旅，2018 世界杯八强"},

    # Group G
    {"name": "Belgium", "flag_url": "🇧🇪", "group_name": "G", "fifa_ranking": 6,
     "confederation": "UEFA", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 16, "recent_ga": 8, "wc_appearances": 14, "wc_best_result": "Third place (2018)",
     "wc_titles": 0, "key_players": json.dumps(["Kevin De Bruyne", "Romelu Lukaku", "Thibaut Courtois"]),
     "notes": "黄金一代末班车，仍有强大实力"},
    {"name": "Iran", "flag_url": "🇮🇷", "group_name": "G", "fifa_ranking": 22,
     "confederation": "AFC", "recent_wins": 5, "recent_draws": 3, "recent_losses": 2,
     "recent_gf": 13, "recent_ga": 8, "wc_appearances": 6, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Mehdi Taremi", "Sardar Azmoun", "Alireza Jahanbakhsh"]),
     "notes": "亚洲区预选赛表现出色"},
    {"name": "Egypt", "flag_url": "🇪🇬", "group_name": "G", "fifa_ranking": 37,
     "confederation": "CAF", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 12, "recent_ga": 9, "wc_appearances": 3, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Mohamed Salah", "Trezeguet", "Ahmed Hegazi"]),
     "notes": "萨拉赫领衔，非洲传统强队"},
    {"name": "New Zealand", "flag_url": "🇳🇿", "group_name": "G", "fifa_ranking": 92,
     "confederation": "OFC", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 10, "recent_ga": 10, "wc_appearances": 2, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Chris Wood", "Winston Reid", "Ryan Thomas"]),
     "notes": "大洋洲代表，2022 惜败附加赛"},

    # Group H
    {"name": "Spain", "flag_url": "🇪🇸", "group_name": "H", "fifa_ranking": 2,
     "confederation": "UEFA", "recent_wins": 8, "recent_draws": 1, "recent_losses": 1,
     "recent_gf": 22, "recent_ga": 6, "wc_appearances": 16, "wc_best_result": "Champions (2010)",
     "wc_titles": 1, "key_players": json.dumps(["Pedri", "Lamine Yamal", "Rodri"]),
     "notes": "传控足球鼻祖，新生代才华横溢"},
    {"name": "Uruguay", "flag_url": "🇺🇾", "group_name": "H", "fifa_ranking": 11,
     "confederation": "CONMEBOL", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 15, "recent_ga": 8, "wc_appearances": 14, "wc_best_result": "Champions (1930, 1950)",
     "wc_titles": 2, "key_players": json.dumps(["Darwin Núñez", "Federico Valverde", "José Giménez"]),
     "notes": "两届冠军，南美劲旅底蕴深厚"},
    {"name": "Saudi Arabia", "flag_url": "🇸🇦", "group_name": "H", "fifa_ranking": 60,
     "confederation": "AFC", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 10, "recent_ga": 12, "wc_appearances": 6, "wc_best_result": "Round of 16 (1994)",
     "wc_titles": 0, "key_players": json.dumps(["Salem Al-Dawsari", "Yasser Al-Shahrani", "Firas Al-Buraikan"]),
     "notes": "2022 世界杯爆冷击败阿根廷"},
    {"name": "Cabo Verde", "flag_url": "🇨🇻", "group_name": "H", "fifa_ranking": 72,
     "confederation": "CAF", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 10, "recent_ga": 11, "wc_appearances": 0, "wc_best_result": "Debut",
     "wc_titles": 0, "key_players": json.dumps(["Ryan Mendes", "Garry Rodrigues", "Vozinha"]),
     "notes": "首次参加世界杯决赛圈"},

    # Group I
    {"name": "France", "flag_url": "🇫🇷", "group_name": "I", "fifa_ranking": 1,
     "confederation": "UEFA", "recent_wins": 7, "recent_draws": 2, "recent_losses": 1,
     "recent_gf": 20, "recent_ga": 6, "wc_appearances": 16, "wc_best_result": "Champions (1998, 2018)",
     "wc_titles": 2, "key_players": json.dumps(["Kylian Mbappé", "Antoine Griezmann", "Aurélien Tchouaméni"]),
     "notes": "卫冕亚军，阵容深度冠绝全球"},
    {"name": "Senegal", "flag_url": "🇸🇳", "group_name": "I", "fifa_ranking": 17,
     "confederation": "CAF", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 14, "recent_ga": 7, "wc_appearances": 3, "wc_best_result": "Quarter-finals (2002)",
     "wc_titles": 0, "key_players": json.dumps(["Sadio Mané", "Iliman Ndiaye", "Édouard Mendy"]),
     "notes": "非洲杯冠军，特兰加雄狮"},
    {"name": "Norway", "flag_url": "🇳🇴", "group_name": "I", "fifa_ranking": 43,
     "confederation": "UEFA", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 12, "recent_ga": 10, "wc_appearances": 3, "wc_best_result": "Round of 16 (1998)",
     "wc_titles": 0, "key_players": json.dumps(["Erling Haaland", "Martin Ødegaard", "Alexander Sørloth"]),
     "notes": "哈兰德与厄德高双核，时隔多年回归"},
    {"name": "Iraq", "flag_url": "🇮🇶", "group_name": "I", "fifa_ranking": 55,
     "confederation": "AFC", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 11, "recent_ga": 10, "wc_appearances": 1, "wc_best_result": "Group stage (1986)",
     "wc_titles": 0, "key_players": json.dumps(["Aymen Hussein", "Amjad Attwan", "Ibrahim Bayesh"]),
     "notes": "时隔 40 年重返世界杯"},

    # Group J
    {"name": "Argentina", "flag_url": "🇦🇷", "group_name": "J", "fifa_ranking": 1,
     "confederation": "CONMEBOL", "recent_wins": 8, "recent_draws": 1, "recent_losses": 1,
     "recent_gf": 21, "recent_ga": 5, "wc_appearances": 18, "wc_best_result": "Champions (1978, 1986, 2022)",
     "wc_titles": 3, "key_players": json.dumps(["Lionel Messi", "Julián Álvarez", "Emiliano Martínez"]),
     "notes": "卫冕冠军，梅西最后一舞"},
    {"name": "Austria", "flag_url": "🇦🇹", "group_name": "J", "fifa_ranking": 22,
     "confederation": "UEFA", "recent_wins": 5, "recent_draws": 3, "recent_losses": 2,
     "recent_gf": 14, "recent_ga": 8, "wc_appearances": 7, "wc_best_result": "Third place (1954)",
     "wc_titles": 0, "key_players": json.dumps(["David Alaba", "Marcel Sabitzer", "Konrad Laimer"]),
     "notes": "欧洲预选赛表现出色"},
    {"name": "Algeria", "flag_url": "🇩🇿", "group_name": "J", "fifa_ranking": 40,
     "confederation": "CAF", "recent_wins": 5, "recent_draws": 2, "recent_losses": 3,
     "recent_gf": 13, "recent_ga": 9, "wc_appearances": 4, "wc_best_result": "Group stage",
     "wc_titles": 0, "key_players": json.dumps(["Riyad Mahrez", "Ismaël Bennacer", "Sofiane Feghouli"]),
     "notes": "北非雄鹰，2014 年差点出线"},
    {"name": "Jordan", "flag_url": "🇯🇴", "group_name": "J", "fifa_ranking": 65,
     "confederation": "AFC", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 10, "recent_ga": 10, "wc_appearances": 0, "wc_best_result": "Debut",
     "wc_titles": 0, "key_players": json.dumps(["Musa Al-Taamari", "Yazan Al-Naimat", "Noor Al-Rawabdeh"]),
     "notes": "首次参加世界杯决赛圈，亚洲杯黑马"},

    # Group K
    {"name": "Portugal", "flag_url": "🇵🇹", "group_name": "K", "fifa_ranking": 8,
     "confederation": "UEFA", "recent_wins": 7, "recent_draws": 1, "recent_losses": 2,
     "recent_gf": 19, "recent_ga": 7, "wc_appearances": 8, "wc_best_result": "Semi-finals (2006)",
     "wc_titles": 0, "key_players": json.dumps(["Bruno Fernandes", "Bernardo Silva", "Rafael Leão"]),
     "notes": "新一代人才济济，冲击首冠"},
    {"name": "Colombia", "flag_url": "🇨🇴", "group_name": "K", "fifa_ranking": 14,
     "confederation": "CONMEBOL", "recent_wins": 6, "recent_draws": 2, "recent_losses": 2,
     "recent_gf": 15, "recent_ga": 7, "wc_appearances": 6, "wc_best_result": "Quarter-finals (2014)",
     "wc_titles": 0, "key_players": json.dumps(["Luis Díaz", "James Rodríguez", "Dávinson Sánchez"]),
     "notes": "美洲杯表现抢眼"},
    {"name": "Uzbekistan", "flag_url": "🇺🇿", "group_name": "K", "fifa_ranking": 58,
     "confederation": "AFC", "recent_wins": 4, "recent_draws": 3, "recent_losses": 3,
     "recent_gf": 11, "recent_ga": 10, "wc_appearances": 0, "wc_best_result": "Debut",
     "wc_titles": 0, "key_players": json.dumps(["Eldor Shomurodov", "Otabek Shukurov", "Jaloliddin Masharipov"]),
     "notes": "首次参加世界杯决赛圈"},
    {"name": "DR Congo", "flag_url": "🇨🇩", "group_name": "K", "fifa_ranking": 61,
     "confederation": "CAF", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 11, "recent_ga": 12, "wc_appearances": 1, "wc_best_result": "Group stage (1974)",
     "wc_titles": 0, "key_players": json.dumps(["Cédric Bakambu", "Dieumerci Mbokani", "Chancel Mbemba"]),
     "notes": "时隔 52 年重返世界杯"},

    # Group L
    {"name": "England", "flag_url": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "group_name": "L", "fifa_ranking": 4,
     "confederation": "UEFA", "recent_wins": 7, "recent_draws": 2, "recent_losses": 1,
     "recent_gf": 19, "recent_ga": 6, "wc_appearances": 16, "wc_best_result": "Champions (1966)",
     "wc_titles": 1, "key_players": json.dumps(["Harry Kane", "Jude Bellingham", "Phil Foden"]),
     "notes": "三狮军团，连续两届大赛进决赛"},
    {"name": "Croatia", "flag_url": "🇭🇷", "group_name": "L", "fifa_ranking": 10,
     "confederation": "UEFA", "recent_wins": 5, "recent_draws": 3, "recent_losses": 2,
     "recent_gf": 14, "recent_ga": 8, "wc_appearances": 6, "wc_best_result": "Runners-up (2018)",
     "wc_titles": 0, "key_players": json.dumps(["Luka Modrić", "Joško Gvardiol", "Andrej Kramarić"]),
     "notes": "大赛型球队，2018 亚军 2022 季军"},
    {"name": "Panama", "flag_url": "🇵🇦", "group_name": "L", "fifa_ranking": 48,
     "confederation": "CONCACAF", "recent_wins": 3, "recent_draws": 3, "recent_losses": 4,
     "recent_gf": 8, "recent_ga": 12, "wc_appearances": 1, "wc_best_result": "Group stage (2018)",
     "wc_titles": 0, "key_players": json.dumps(["Adalberto Carrasquilla", "José Fajardo", "Michael Murillo"]),
     "notes": "第二次参加世界杯决赛圈"},
    {"name": "Ghana", "flag_url": "🇬🇭", "group_name": "L", "fifa_ranking": 68,
     "confederation": "CAF", "recent_wins": 4, "recent_draws": 2, "recent_losses": 4,
     "recent_gf": 10, "recent_ga": 12, "wc_appearances": 4, "wc_best_result": "Quarter-finals (2010)",
     "wc_titles": 0, "key_players": json.dumps(["Mohammed Kudus", "Thomas Partey", "Jordan Ayew"]),
     "notes": "非洲黑星，2010 年差点进四强"},
]
# fmt: on


def seed():
    db: Session = SessionLocal()

    try:
        # --- 插入球队 ---
        print("正在插入球队数据...")
        teams_created = 0
        teams_skipped = 0
        team_map = {}  # name -> WCTeam object

        for team_data in WC_TEAMS:
            existing = db.query(WCTeam).filter(WCTeam.name == team_data["name"]).first()
            if existing:
                team_map[team_data["name"]] = existing
                teams_skipped += 1
                continue

            team = WCTeam(**team_data)
            db.add(team)
            db.flush()
            team_map[team_data["name"]] = team
            teams_created += 1

        db.commit()
        print(f"  球队: 创建 {teams_created}, 跳过 {teams_skipped}")

        # --- 生成小组赛 ---
        print("正在生成小组赛...")
        teams_by_group = {}
        for team in team_map.values():
            teams_by_group.setdefault(team.group_name, []).append(team)

        # 每组按 name 排序以确保固定顺序
        for group_name in teams_by_group:
            teams_by_group[group_name].sort(key=lambda t: t.name)

        pairings = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]

        matches_created = 0
        matches_skipped = 0
        match_number = 1

        for group_name in sorted(teams_by_group.keys()):
            teams = teams_by_group[group_name]
            if len(teams) != 4:
                print(f"  ⚠️  组 {group_name} 只有 {len(teams)} 支球队，跳过")
                continue

            for home_idx, away_idx in pairings:
                existing = db.query(WCMatch).filter(
                    WCMatch.match_number == match_number
                ).first()
                if existing:
                    matches_skipped += 1
                    match_number += 1
                    continue

                match = WCMatch(
                    match_number=match_number,
                    home_team_id=teams[home_idx].id,
                    away_team_id=teams[away_idx].id,
                    stage="group",
                    group_name=group_name,
                    status="scheduled",
                )
                db.add(match)
                matches_created += 1
                match_number += 1

        db.commit()
        print(f"  比赛: 创建 {matches_created}, 跳过 {matches_skipped}")
        print(f"\n✅ 种子数据完成！球队 {teams_created + teams_skipped}, 比赛 {matches_created + matches_skipped}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

# 🎣 钓鱼佬永不空军 — FishCast Engine v2.1

> "今天不空军！" — 基于 69 种鱼行为学和实时气象的智能钓鱼决策系统

## ✨ 功能

| 功能 | 说明 |
|:-----|:------|
| 🗺️ **地图定位** | Leaflet + OpenStreetMap，点击定位或浏览器自动定位 |
| 💧 **水体识别** | Overpass API 自动查询最近湖泊/河流/水库 |
| 🌤️ **实时天气** | Open-Meteo 免费API，自动获取气温、气压、湿度、风速风向 |
| 🐟 **69 种鱼** | 48 种淡水鱼 + 21 种海水鱼，涵盖全国常见鱼种 |
| 📊 **六部评分** | 水温(户部) / 天气(兵部) / 季节(礼部) / 地形(工部) / 应激(刑部) |
| 🪝 **钓具推荐** | 每种鱼配套钩型 + 钩号 + 主线/子线/钓竿 |
| 🥫 **打窝策略** | 窝料配方 + 打窝方法 |
| 📖 **钓法技巧** | 调漂、标点、手法要点、季节性建议 |
| ⏰ **出钓时间** | 清晨/上午/中午/下午/黄昏/夜间六时段推荐 |
| 🌊 **海钓模式** | 黑鲷、真鲷、石斑、鲅鱼、金枪鱼等 21 种海水鱼 |

## 🚀 在线演示

👉 **[eluckydog.github.io/fishcast-engine](https://eluckydog.github.io/fishcast-engine/)**

打开页面 → 允许定位 → 选鱼种 → 选时间 → 点评估 → 出钓策略

## 📦 快速开始 (CLI)

```bash
git clone https://github.com/eluckydog/fishcast-engine.git
cd fishcast-engine
pip install -e .

# CLI 用法
fishcast 鲤鱼 --temp 26 --pressure 1015
fishcast 黑鲷 --temp 24 --pressure 1018 --weather 晴
fishcast --list-fish         # 查看所有鱼种
fishcast 鲫鱼 --temp 18 --json  # JSON 输出
```

### Python API

```python
from engine.core import FishCastV2, FishingCondition

engine = FishCastV2()
result = engine.evaluate("鲤鱼", temp=26, pressure=1015, weather="晴")
print(result["score"], result["advice"])
```

## 🏗️ 架构

```
fishcast-engine/
├── data/
│   └── fish_species.json     # 69 种鱼完整数据
├── engine/
│   └── core.py               # 六部决策引擎
├── docs/
│   ├── index.html            # 交互式 Web 界面
│   ├── data/fish_species.json
│   └── .nojekyll
├── fishcast/                 # 旧版 CLI (保持兼容)
├── SKILL.md                  # AI Agent 接口
└── README.md
```

## 🔗 数据来源

| 数据 | 来源 | 许可 |
|:-----|:-----|:----:|
| 🗺️ 地图瓦片 | OpenStreetMap | ODbL |
| 💧 水体数据 | Overpass API (OSM) | ODbL |
| 🌤️ 实时天气 | Open-Meteo | 免费开源 |
| 🐟 鱼种数据 | cnfishbase + 实战经验 | 自编 |

## 📜 许可证

MIT License

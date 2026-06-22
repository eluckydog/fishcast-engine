# 🎣 钓鱼佬永不空军 — FishCast Engine v2.0

> "今天不空军！" — 基于多鱼种行为学和气象学的智能钓鱼决策引擎

## 新增功能 (v2.0)

- 🗺️ **地图定位** — Leaflet + OpenStreetMap，点击地图或自动定位
- 💧 **水体识别** — Overpass API 自动查询最近湖泊/河流
- 🌤️ **实时天气** — Open-Meteo 自动获取气温、气压、风
- 🐟 **38 种淡水鱼** — 含鱼钩、线组、打窝、钓法推荐
- 📊 **六部评分** — 水温(户部) / 天气(兵部) / 季节(礼部) / 地形(工部) / 应激(刑部)
- 🪝 **钓具推荐** — 每种鱼配套钩型/线组/竿长建议
- 🥫 **打窝策略** — 窝料配方 + 打窝方法
- 📖 **钓法技巧** — 调漂、标点、手法要点

## 在线演示

👉 [eluckydog.github.io/fishcast-engine](https://eluckydog.github.io/fishcast-engine/)

## 快速使用

```bash
pip install -e .
fishcast 鲤鱼 --temp 26 --pressure 1015
```

## 数据来源

- 鱼种数据: cnfishbase + 实战经验
- 地图: OpenStreetMap + Leaflet
- 水体: Overpass API (OSM)
- 天气: Open-Meteo (免费开源)

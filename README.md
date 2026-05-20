# 🎣 钓鱼佬永不空军 — FishCast Engine

> "今天不空军！" — 基于 28 种鱼种行为学和气象学的智能钓鱼决策引擎

## 功能

- **六部决策引擎**: 户部·溶氧 / 工部·地形 / 吏部·鱼种 / 刑部·应激 / 兵部·天气 / 礼部·评分
- 覆盖 **28 种** 常见淡水鱼种
- **9 类** 地形分析（入水口、回水湾、水草区等）
- 城市/野外河道智能修正
- 应激风险评估（温差、缺氧、气压骤降）
- Open-Meteo 天气回退方案

## 安装

```bash
pip install fishcast
```

本地安装：

```bash
git clone <repo-url>
cd fishcast
pip install -e .
```

## 快速入门

### 命令行

```bash
# 基础用法
fishcast 鲤鱼 --temp 26 --pressure 1015

# 更多参数
fishcast 翘嘴 --temp 22 --pressure 1008 --weather 晴

# 列出所有鱼种
fishcast --list-fish

# JSON 输出
fishcast 鲫鱼 --temp 15 --json
```

### Python API

```python
from fishcast import FishCastEngine, FishingCondition

engine = FishCastEngine()
result = engine.evaluate("鲤鱼", FishingCondition(temp=26, pressure=1015, season="summer"))
print(f"评分: {result['score']}")
print(f"建议: {result['advice']}")
```

## 项目结构

```
SKILL.md                          # AI 智能体接口
setup.py                          # Python 包配置
fishing_geo_bridge.py             # 地理桥接脚本

fishcast/                         # 核心引擎包
├── __init__.py
├── __main__.py                   # CLI 入口
├── engine.py                     # 六部决策引擎
└── data/
    ├── fish-preferences_data.py  # 鱼种偏好数据
    ├── river-correction_data.py  # 河道修正
    └── terrain-types_data.py     # 地形类型

data/                             # JSON 原始数据
├── fish-preferences.json
├── river-correction.json
└── terrain-types.json

references/                       # 参考文档
├── api-integration.md            # API 集成说明
└── fishing-rules.md              # 钓鱼规则

LICENSE                           # 私有许可证
```

## License

FISHCAST PRIVATE LICENSE 1.0 — 闭源，仅供个人使用。详见 LICENSE。

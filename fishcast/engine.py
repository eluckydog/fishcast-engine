"""
FishCast Engine - 核心决策引擎 (闭源)
==================================
含六部协作（户部/工部/吏部/刑部/兵部/礼部）的完整钓鱼决策链。
"""
import json, base64, math, os
from typing import Optional, Dict, List, Any


def _load_blob(blob_path: str) -> dict:
    """加载闭源数据"""
    with open(blob_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    _, _, payload = raw.partition("BLOB = '''")
    payload, _, _ = payload.partition("'''")
    payload = payload.strip()
    return json.loads(base64.b64decode(payload).decode('utf-8'))


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FISH_DATA = _load_blob(os.path.join(DATA_DIR, "fish-preferences_data.py"))
TERRAIN_DATA = _load_blob(os.path.join(DATA_DIR, "terrain-types_data.py"))
RIVER_DATA = _load_blob(os.path.join(DATA_DIR, "river-correction_data.py"))


class FishingCondition:
    """出钓条件"""
    def __init__(self, **kwargs):
        self.temp = kwargs.get("temp", 20)
        self.pressure = kwargs.get("pressure", 1013)
        self.weather = kwargs.get("weather", "晴")
        self.wind_speed = kwargs.get("wind_speed", 2)
        self.humidity = kwargs.get("humidity", 60)
        self.river_type = kwargs.get("river_type", "wild")
        self.lat = kwargs.get("lat", None)
        self.lng = kwargs.get("lng", None)
        self.season = kwargs.get("season", "spring")
        self.hour = kwargs.get("hour", 8)
        self.pressure_trend = kwargs.get("pressure_trend", "stable")


class FishCastEngine:
    """
    钓鱼决策引擎 - 六部协作完整实现

    用法:
        engine = FishCastEngine()
        result = engine.evaluate("鲤鱼", FishingCondition(temp=26, pressure=1015, ...))
        print(result["score"], result["advice"])
    """

    def __init__(self):
        self._fish_index = {f["name"]: f for f in FISH_DATA["fish_species"]}
        self._terrain_index = {t["code"]: t for t in TERRAIN_DATA["terrain_types"]}

    def list_fish_species(self) -> List[str]:
        """列出支持的鱼种"""
        return list(self._fish_index.keys())

    def evaluate(self, fish_name: str, condition: FishingCondition) -> Dict[str, Any]:
        """
        六部协作评估出钓策略

        Args:
            fish_name: 目标鱼种名称
            condition: 出钓条件

        Returns:
            dict: {score, advice, details, ...}
        """
        # 吏部：查鱼种
        fish = self._fish_index.get(fish_name)
        if fish is None:
            return {"score": 0, "advice": f"不支持鱼种: {fish_name}", "details": {}}

        # 户部：溶氧与水温分析
        water_temp, do_level = self._analyze_water(condition)

        # 工部：地形分析
        terrain_analysis = self._analyze_terrain(condition, fish)

        # 刑部：应激风险评估
        stress = self._assess_stress(condition, fish, water_temp, do_level)

        # 礼部：综合评分
        score, breakdown = self._compute_score(fish, condition, water_temp, do_level,
                                                terrain_analysis, stress)

        # 兵部：时段建议
        time_advice = self._get_time_advice(condition, fish)

        # 出钓建议
        if score > 75:
            advice = "强烈建议 - 黄金窗口"
        elif score > 60:
            advice = "可以出钓"
        elif score > 40:
            advice = "勉强可钓 - 需特殊技巧"
        else:
            advice = "不建议 - 改日或夜钓"

        return {
            "score": round(score, 1),
            "advice": advice,
            "fish": fish_name,
            "water_temp": round(water_temp, 1),
            "do_level": round(do_level, 1),
            "stress": stress,
            "terrain": terrain_analysis,
            "time_advice": time_advice,
            "breakdown": breakdown,
            "bait_suggestions": fish.get("bait_types", [])[:3],
            "method_suggestions": fish.get("fishing_method", [])
        }

    def _analyze_water(self, c: FishingCondition) -> tuple:
        """户部：溶解氧与水温分析"""
        # 基础溶氧（按季节）
        do_base = {"winter": 11.5, "spring": 9, "autumn": 9, "summer": 6}.get(c.season, 9)

        # 气压修正
        if c.pressure > 1020:
            do_factor = 1.15
        elif c.pressure < 990:
            do_factor = 0.7
        elif c.pressure < 1010:
            do_factor = 0.85
        else:
            do_factor = 1.0

        # 气压趋势修正
        trend_factor = 1.0
        if c.pressure_trend == "rising":
            trend_factor = 1.1
        elif c.pressure_trend == "falling":
            trend_factor = 0.8

        # 河道修正
        river_cfg = RIVER_DATA["river_type_correction"].get(c.river_type)
        river_do = river_cfg["correction_factors"]["基础溶氧系数"]["value"] if river_cfg else 1.0

        do_level = do_base * do_factor * trend_factor * river_do

        # 水温
        lat_factor = 1.0
        if c.lat is not None:
            lat_abs = abs(c.lat)
            if lat_abs >= 40:
                lat_factor = 0.9
            elif lat_abs <= 30:
                lat_factor = 1.1
        water_temp = c.temp * lat_factor
        if river_cfg and c.season == "summer":
            water_temp += river_cfg["correction_factors"]["夏季水温偏移"]["value"]

        return water_temp, do_level

    def _analyze_terrain(self, c: FishingCondition, fish: dict) -> List[Dict]:
        """工部：地形分析"""
        preferred = fish.get("preferred_terrain", [])
        river_cfg = RIVER_DATA["river_type_correction"].get(c.river_type, {})
        valid = river_cfg.get("valid_terrains", {}).get("优先", []) or \
                [t["code"] for t in TERRAIN_DATA["terrain_types"]]

        candidates = []
        for code in valid:
            if code not in self._terrain_index:
                continue
            t = self._terrain_index[code]
            match = code in preferred
            food = t.get("food_score", 50)
            do_bonus = t.get("local_do_correction", 0)

            candidates.append({
                "code": code,
                "name": t["name"],
                "match": match,
                "food_score": food,
                "do_bonus": f"+{do_bonus}%" if do_bonus > 0 else str(do_bonus) if do_bonus < 0 else "0",
                "risk": t.get("风险提示", "无"),
                "method": t.get("钓法建议", [])
            })

        candidates.sort(key=lambda x: (x["match"], x["food_score"]), reverse=True)
        return candidates[:3]

    def _assess_stress(self, c: FishingCondition, fish: dict,
                       water_temp: float, do_level: float) -> Dict:
        """刑部：应激风险评估"""
        triggers = fish.get("stress_triggers", {})
        optimal = fish.get("optimal_temp", {})
        opt_do = fish.get("optimal_do", 4.0)

        issues = []
        severity = 1.0

        # 温差评估
        temp_diff = abs(water_temp - (optimal.get("min", 15) + optimal.get("max", 25)) / 2)
        if temp_diff > 8:
            issues.append("重度温差应激")
            severity *= 0.5
        elif temp_diff > 5:
            issues.append("中度温差应激")
            severity *= 0.8
        elif temp_diff > 3:
            issues.append("轻度温差应激")
            severity *= 0.9

        # 溶氧评估
        if do_level < 3:
            issues.append("重度缺氧应激")
            severity *= 0.5
        elif do_level < opt_do * 0.7:
            issues.append("轻度缺氧应激")
            severity *= 0.8

        # 气压评估
        if c.pressure < 990:
            issues.append("低压应激")
            severity *= 0.7
        elif c.pressure_trend == "falling" and c.pressure < 1000:
            issues.append("气压骤降应激")
            severity *= 0.8

        return {
            "level": "无" if severity >= 1.0 else "轻度" if severity >= 0.8 else "中度" if severity >= 0.6 else "重度",
            "issues": issues,
            "factor": round(severity, 2)
        }

    def _compute_score(self, fish: dict, c: FishingCondition,
                       water_temp: float, do_level: float,
                       terrain: list, stress: dict) -> tuple:
        """礼部：综合评分"""
        opt_min = fish.get("optimal_temp", {}).get("min", 15)
        opt_max = fish.get("optimal_temp", {}).get("max", 28)
        feed_min = fish.get("feeding_temp", {}).get("min", 5)
        feed_max = fish.get("feeding_temp", {}).get("max", 35)
        opt_do = fish.get("optimal_do", 4.0)

        # 温度系数
        if feed_min <= water_temp <= feed_max:
            mid = (opt_min + opt_max) / 2
            temp_coeff = max(0, 100 - abs(water_temp - mid) * 5)
        else:
            temp_coeff = 0

        # 溶氧系数
        do_coeff = min(do_level / opt_do * 100, 100) if do_level >= 1 else 0

        # 地形系数
        terrain_coeff = 50
        if terrain:
            best_match = terrain[0]
            if best_match["match"]:
                terrain_coeff = 90 + best_match.get("food_score", 50) * 0.1
            else:
                terrain_coeff = 30 + best_match.get("food_score", 50) * 0.3

        # 食物系数
        food_coeff = terrain[0]["food_score"] * 0.75 if terrain else 50

        # 加权综合
        raw_score = temp_coeff * 0.35 + do_coeff * 0.35 + terrain_coeff * 0.2 + food_coeff * 0.1

        # 应激修正
        final_score = raw_score * stress.get("factor", 1.0)

        breakdown = {
            "temp_coeff": round(temp_coeff, 1),
            "do_coeff": round(do_coeff, 1),
            "terrain_coeff": round(terrain_coeff, 1),
            "food_coeff": round(food_coeff, 1),
            "stress_factor": stress.get("factor", 1.0),
            "raw_score": round(raw_score, 1)
        }

        return final_score, breakdown

    def _get_time_advice(self, c: FishingCondition, fish: dict) -> Dict:
        """兵部：时段建议"""
        best_seasons = fish.get("best_seasons", ["spring", "autumn"])
        season_ok = c.season in best_seasons

        # 钓层建议
        if c.temp < 10:
            layer = "钓深/钓底"
        elif c.temp < 20:
            layer = "全层可钓"
        elif c.temp < 26:
            layer = "钓浅/钓浮"
        else:
            layer = "钓荫凉/钓深"

        # 时段建议
        hour = c.hour
        if 6 <= hour < 9:
            period = "清晨窗口期"
            quality = "优秀"
        elif 17 <= hour < 21:
            period = "傍晚窗口期"
            quality = "优秀"
        elif 10 <= hour < 15 and c.season == "winter":
            period = "中午窗口期"
            quality = "良好"
        else:
            period = "非最佳时段"
            quality = "一般"

        return {
            "season_match": season_ok,
            "period": period,
            "quality": quality,
            "layer": layer,
        }


def quick_rating(fish_name: str, temp: float, pressure: float = 1013,
                 weather: str = "晴", river_type: str = "wild",
                 season: str = None) -> Dict:
    """
    快速出钓评分（一行调用）

    Args:
        fish_name: 鱼种
        temp: 气温 °C
        pressure: 气压 hPa
        weather: 天气
        river_type: 河道类型(urban/wild)
        season: 季节(自动推算)

    Returns:
        {score, advice, ...}
    """
    import datetime
    if season is None:
        m = datetime.datetime.now().month
        if 3 <= m <= 5:
            season = "spring"
        elif 6 <= m <= 8:
            season = "summer"
        elif 9 <= m <= 11:
            season = "autumn"
        else:
            season = "winter"

    cond = FishingCondition(
        temp=temp, pressure=pressure, weather=weather,
        river_type=river_type, season=season
    )
    engine = FishCastEngine()
    return engine.evaluate(fish_name, cond)

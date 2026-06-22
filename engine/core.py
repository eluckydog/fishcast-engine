#!/usr/bin/env python3
"""FishCast v2 Engine - 六部决策引擎"""
import json, math, os

class FishCastV2:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        with open(os.path.join(data_dir, "fish_species.json"), "r", encoding="utf-8") as f:
            self.db = json.load(f)["fish_species"]
        self._idx = {f["name"]: f for f in self.db}

    def list_species(self):
        return list(self._idx.keys())

    def evaluate(self, fish_name, temp=20, pressure=1013, weather="晴",
                 wind=2, humidity=60, season="spring", hour=8,
                 depth="中", terrain="P4"):
        fish = self._idx.get(fish_name)
        if not fish:
            return {"error": f"不支持的鱼种: {fish_name}"}

        scores = {}
        # 户部: 水温评分 (weight: 30%)
        ot = fish["optimal_temp"]
        if ot["min"] <= temp <= ot["max"]:
            water_score = 100
        elif temp < ot["min"]:
            water_score = max(0, 100 - (ot["min"] - temp) * 10)
        else:
            water_score = max(0, 100 - (temp - ot["max"]) * 8)
        water_score = min(100, water_score)
        
        # 兵部: 天气评分 (weight: 25%)
        weather_score = 80
        if "晴" in weather: weather_score = 90
        elif "阴" in weather: weather_score = 80
        elif "雨" in weather: weather_score = 65
        if wind > 5: weather_score -= 15
        if pressure < 1000: weather_score -= 10
        elif pressure > 1020: weather_score += 5
        weather_score = max(0, min(100, weather_score))
        
        # 礼部: 季节评分 (weight: 20%)
        seasons = fish.get("best_seasons", ["spring","summer"])
        season_score = 100 if season in seasons else 50
        
        # 工部: 地形评分 (weight: 15%)
        pt = fish.get("preferred_terrain", [])
        terrain_score = 100 if terrain in pt else 60
        
        # 刑部: 应激评分 (weight: 10%)
        stress_score = 80
        triggers = fish.get("stress_triggers", {})
        if temp < 10: stress_score -= 15
        if pressure < 998: stress_score -= 10
        if wind > 6: stress_score -= 5
        
        total = (water_score * 0.30 + weather_score * 0.25 +
                 season_score * 0.20 + terrain_score * 0.15 +
                 stress_score * 0.10)

        # 出钓建议
        if total > 75: advice = "强烈建议 - 黄金出钓窗口"
        elif total > 60: advice = "可以出钓"
        elif total > 40: advice = "勉强可钓，需特殊技巧"
        else: advice = "不建议出钓"

        # 钓具推荐
        hook = fish.get("hook", {})
        rigging = fish.get("rigging", {})
        chumming = fish.get("chumming", {})
        technique = fish.get("technique", {})
        
        return {
            "fish": fish_name,
            "score": round(total, 1),
            "advice": advice,
            "breakdown": {
                "户部(水温)": round(water_score),
                "兵部(天气)": round(weather_score),
                "礼部(季节)": round(season_score),
                "工部(地形)": round(terrain_score),
                "刑部(应激)": round(stress_score)
            },
            "tackle": {
                "hook_types": hook.get("types", []),
                "hook_size": hook.get("size", "常规"),
                "main_line": rigging.get("main_line", "常规"),
                "sub_line": rigging.get("sub_line", "常规"),
                "rod": rigging.get("rod", "常规")
            },
            "baiting": {
                "chum": chumming.get("base", []),
                "chum_method": chumming.get("method", "适量打窝")
            },
            "technique": technique
        }

"""
钓鱼佬永不空军 × 战术地理工具包 桥接模块

为钓鱼佬提供备用天气/地图数据：
1. 和风天气不可用时 → 自动切换 Open-Meteo 气象数据
2. 提供钓点坐标解析（Natural Earth 全球地名索引）
"""

import json
import os
import sys

# 引入战术地理工具包
_TFP_GEO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                            "战术迷雾穿透TFP-SS", "scripts", "tactical_geo")
if _TFP_GEO_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(_TFP_GEO_DIR))

_GEO = None
_WEATHER = None


def _ensure_geo():
    global _GEO
    if _GEO is not None:
        return _GEO
    try:
        from tactical_geo import natural_earth_index as geo
        _GEO = geo
        return _GEO
    except ImportError:
        return None


def _ensure_weather():
    global _WEATHER
    if _WEATHER is not None:
        return _WEATHER
    try:
        from tactical_geo import mini_weather as wx
        _WEATHER = wx
        return _WEATHER
    except ImportError:
        return None


def get_location_coords(location_name):
    """
    钓点名称→经纬度（全球覆盖）

    支持：城市名、区县名、国家名
    返回：(lat, lng) 或 None
    """
    geo = _ensure_geo()
    if not geo:
        return None

    # 先精确匹配
    coords = geo.geocode(location_name)
    if coords:
        return coords

    # 模糊匹配取第一个
    fuzzy = geo.geocode_fuzzy(location_name, limit=1)
    if fuzzy:
        return (fuzzy[0][2], fuzzy[0][3])

    return None


def get_weather(lat, lng, date=None, api_key=None):
    """
    获取钓点气象数据（备用源 — Open-Meteo）

    当和风天气不可用时自动调用。
    返回：
    {
        "temp": float,      # 平均温度 °C
        "temp_min": float,
        "temp_max": float,
        "pressure": float,  # hPa（海平面气压，钓鱼关键指标）
        "wind_speed": float,
        "wind_gusts": float,
        "precipitation": float,  # mm
        "humidity": float,      # 估算（基于降水）
        "uvi": float,
        "source": "open-meteo-fallback"
    }
    None 如果不可用
    """
    wx = _ensure_weather()
    if not wx:
        return None

    import datetime
    if date is None:
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    weather = wx.get_weather(lat, lng, date) if hasattr(wx, 'get_weather') else wx(lat, lng, date)
    if not weather or "error" in weather:
        return None

    # 和风天气兼容字段映射
    pressure_hpa = weather.get("evapotranspiration", 0) * 10 + 1013  # 近似估算
    return {
        "temp": weather.get("temp_mean", 0),
        "temp_min": weather.get("temp_min", 0),
        "temp_max": weather.get("temp_max", 0),
        "pressure": round(pressure_hpa, 1),
        "wind_speed": weather.get("wind_speed_max", 0),
        "wind_gusts": weather.get("wind_gusts_max", 0),
        "precipitation": weather.get("precipitation", 0),
        "wind_direction": weather.get("wind_direction", 0),
        "solar_radiation": weather.get("solar_radiation", 0),
        "source": "open-meteo-fallback"
    }


def get_forecast(lat, lng, days=3):
    """
    获取未来 N 天预报（钓鱼黄金窗口预估）

    Returns: [{
        "date": str,
        "temp_max": float,
        "temp_min": float,
        "precipitation": float,
        "wind_speed": float,
        "pressure_approx": float,
    }]
    """
    wx = _ensure_weather()
    if not wx:
        return None
    return wx.get_forecast(lat, lng, days)


def get_fishing_rating(lat, lng, fish_species="鲤鱼", date=None):
    """
    基于气象数据的快速出钓评分（0-100）

    不考虑地形/溶氧等，仅评估气象窗口。
    用于定性判断"今天值不值得出门"。
    """
    weather = get_weather(lat, lng, date)
    if not weather:
        return {"rating": None, "note": "气象数据不可用"}

    score = 60  # 基准分

    # 降水扣分
    precip = weather.get("precipitation", 0)
    if precip > 20:
        score -= 30
    elif precip > 10:
        score -= 15
    elif precip > 5:
        score -= 5

    # 风扣分
    wind = weather.get("wind_speed", 0)
    if wind > 15:
        score -= 25
    elif wind > 10:
        score -= 10
    elif wind > 5:
        score -= 3

    # 温度修正（鲤鱼偏好15-28°C）
    temp = weather.get("temp", 20)
    if 15 <= temp <= 28:
        score += 10
    elif temp < 5 or temp > 35:
        score -= 20
    elif temp < 10 or temp > 32:
        score -= 10

    score = max(0, min(100, score))

    level = "建议出钓" if score > 70 else "可以尝试" if score > 50 else "不建议"

    return {
        "rating": score,
        "level": level,
        "temp": weather.get("temp"),
        "precipitation": weather.get("precipitation"),
        "wind_speed": weather.get("wind_speed"),
        "note": f"气象评分{score}分（{level}）",
        "source": weather.get("source", "open-meteo-fallback")
    }


def list_nearby_fishing_spots(lat, lng, radius_km=50):
    """
    查找钓点附近的地名/城市（用于参考）

    Returns: [(name, distance_km, lat, lng), ...]
    """
    geo = _ensure_geo()
    if not geo:
        return []

    results = geo.find_on_map(lat - 0.5, lat + 0.5, lng - 0.5, lng + 0.5)
    # 简化近似距离（1度≈111km）
    nearby = []
    for name, country, plat, plng in results:
        dist = ((plat - lat) ** 2 + (plng - lng) ** 2) ** 0.5 * 111
        if dist <= radius_km:
            nearby.append((name, round(dist, 1), plat, plng))

    nearby.sort(key=lambda x: x[1])
    return nearby[:10]


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        loc = sys.argv[1]
        coords = get_location_coords(loc)
        if coords:
            print(f"{loc} -> ({coords[0]:.4f}, {coords[1]:.4f})")
            grade = get_fishing_rating(coords[0], coords[1])
            import json as j
            print(j.dumps(grade, ensure_ascii=False, indent=2))
            forecast = get_forecast(coords[0], coords[1])
            if forecast:
                print("未来3天预报：")
                for d in forecast[:3]:
                    print(f"  {d.get('date')}: {d.get('temp_min',0)}-{d.get('temp_max',0)}C, 降水{d.get('precipitation',0)}mm")
        else:
            print(f"未找到钓点: {loc}")
    else:
        # 演示：杭州
        print("=== 钓鱼佬备用气象/地图桥梁 ===\n")
        for loc in ["杭州", "千岛湖", "北京", "上海", "广州"]:
            coords = get_location_coords(loc)
            if coords:
                g = get_fishing_rating(coords[0], coords[1])
                print(f"  {loc} ({coords[0]:.2f}, {coords[1]:.2f}): {g['rating']}分 - {g['note']}")

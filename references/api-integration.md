# API接入指南

本文档详细说明钓鱼决策智能体所需的天气API和地图API的申请、配置和使用方法。

## 一、天气API（和风天气）

### 1.1 API概述

**服务提供商**：和风天气
**官网**：https://www.qweather.com/
**开发者平台**：https://dev.qweather.com/

**核心功能**：
- 实时天气数据（温度、气压、风力、湿度、天气现象）
- 3小时天气预报（用于计算气压趋势）
- 逐日天气预报（用于未来几天的出钓规划）

### 1.2 申请流程

#### 步骤1：注册账号
1. 访问 https://console.qweather.com/
2. 点击"注册"创建账号
3. 完成邮箱验证

#### 步骤2：创建应用
1. 登录后进入控制台
2. 点击"创建项目"或"添加应用"
3. 填写应用信息：
   - 应用名称：钓鱼决策智能体
   - 应用类型：Web应用/桌面应用
   - 使用场景：个人学习/商业项目
4. 提交后等待审核（通常1-2小时）

#### 步骤3：获取API Key
1. 审核通过后，在"项目管理"页面找到创建的应用
2. 复制应用Key（API Key），格式如：`abc123def456`

#### 步骤4：选择订阅套餐
和风天气提供多种订阅套餐：

| 套餐 | 价格 | 免费额度 | 说明 |
|------|------|---------|------|
| 免费版 | ¥0 | 1000次/天 | 适合个人使用 |
| 标准版 | ¥99/月 | 10000次/天 | 适合商业项目 |
| 专业版 | ¥499/月 | 100000次/天 | 企业级应用 |

**推荐**：初期使用免费版，如不够可升级。

### 1.3 API调用说明

#### 实时天气API

**接口地址**：
```
GET https://devapi.qweather.com/v7/weather/now
```

**请求参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | String | 是 | 地点ID或经纬度（如：101010100 或 39.90498,116.40529） |
| key | String | 是 | 你的API Key |

**请求示例**：
```bash
curl "https://devapi.qweather.com/v7/weather/now?location=39.90498,116.40529&key=你的API_Key"
```

**返回示例**：
```json
{
  "code": "200",
  "updateTime": "2024-04-15T14:00+08:00",
  "now": {
    "obsTime": "2024-04-15T14:00",
    "temp": 26,
    "feelsLike": 27,
    "icon": "100",
    "text": "晴",
    "wind360": 45,
    "windDir": "东北风",
    "windScale": 3,
    "windSpeed": 15,
    "humidity": 70,
    "precip": 0,
    "pressure": 1015,
    "vis": 10,
    "cloud": 10
  }
}
```

#### 3小时预报API

**接口地址**：
```
GET https://devapi.qweather.com/v7/weather/3h
```

**请求参数**：同实时天气API

**请求示例**：
```bash
curl "https://devapi.qweather.com/v7/weather/3h?location=39.90498,116.40529&key=你的API_Key"
```

**返回示例**：
```json
{
  "code": "200",
  "updateTime": "2024-04-15T14:00+08:00",
  "hourly": [
    {
      "fxTime": "2024-04-15T14:00+08:00",
      "temp": 26,
      "icon": "100",
      "text": "晴",
      "wind360": 45,
      "windDir": "东北风",
      "windScale": 3,
      "windSpeed": 15,
      "humidity": 70,
      "pop": 0,
      "precip": 0,
      "pressure": 1015,
      "cloud": 10
    },
    {
      "fxTime": "2024-04-15T17:00+08:00",
      "temp": 24,
      "icon": "100",
      "text": "晴",
      "wind360": 45,
      "windDir": "东北风",
      "windScale": 3,
      "windSpeed": 15,
      "humidity": 72,
      "pop": 0,
      "precip": 0,
      "pressure": 1014,
      "cloud": 10
    }
  ]
}
```

### 1.4 气压趋势计算

根据3小时预报数据计算气压趋势：

```python
def calculate_pressure_trend(pressure_list):
    """
    计算气压趋势
    pressure_list: 气压值列表 [当前, 3小时后, 6小时后, ...]
    返回: "rising", "falling", "stable"
    """
    if len(pressure_list) < 2:
        return "stable"

    delta = pressure_list[-1] - pressure_list[0]

    if delta > 2:
        return "rising"
    elif delta < -2:
        return "falling"
    else:
        return "stable"
```

### 1.5 错误处理

常见错误码：

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| 200 | 成功 | 正常处理 |
| 204 | 无数据 | 提示用户"暂无天气数据" |
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | API Key错误 | 检查API Key是否正确 |
| 402 | API额度超限 | 提示用户"API调用次数超限，请充值" |
| 404 | 地点不存在 | 提示用户"位置信息错误，请重新输入" |

---

## 二、地图API（高德地图）

### 2.1 API概述

**服务提供商**：高德地图
**官网**：https://lbs.amap.com/
**开发者平台**：https://console.amap.com/

**核心功能**：
- 地理编码（地址转经纬度）
- 逆地理编码（经纬度转地址/区域类型）
- POI搜索（搜索钓鱼点、水域等）
- 路径规划（计算到钓点的距离）

### 2.2 申请流程

#### 步骤1：注册账号
1. 访问 https://console.amap.com/
2. 点击"注册"创建账号
3. 完成手机号验证

#### 步骤2：创建应用
1. 登录后进入控制台
2. 点击"应用管理" → "我的应用" → "创建新应用"
3. 填写应用信息：
   - 应用名称：钓鱼决策智能体
   - 应用类型：Web服务/浏览器端
4. 提交后创建应用

#### 步骤3：添加Key
1. 在应用详情页点击"添加Key"
2. 选择Key类型：
   - Web服务：用于服务端API调用
   - Web端：用于前端地图显示
3. 选择服务：
   - 地理编码（逆地理编码）
   - 搜索服务
4. 提交后获取Key，格式如：`abc123def456`

#### 步骤4：选择套餐

高德地图提供免费个人开发版：

| 套餐 | 价格 | 免费额度 | 说明 |
|------|------|---------|------|
| 个人开发者 | ¥0 | 30万次/天 | 适合个人使用 |

**推荐**：免费个人开发者版完全够用。

### 2.3 API调用说明

#### 地理编码API（地址转经纬度）

**接口地址**：
```
GET https://restapi.amap.com/v3/geocode/geo
```

**请求参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| address | String | 是 | 地址（如：北京市朝阳区） |
| city | String | 否 | 指定查询城市 |
| key | String | 是 | 你的Key |

**请求示例**：
```bash
curl "https://restapi.amap.com/v3/geocode/geo?address=北京市朝阳区&key=你的Key"
```

**返回示例**：
```json
{
  "status": "1",
  "info": "OK",
  "infocode": "10000",
  "count": "1",
  "geocodes": [
    {
      "formatted_address": "北京市朝阳区",
      "country": "中国",
      "province": "北京市",
      "citycode": "010",
      "adcode": "110105",
      "level": "区县",
      "location": "116.443403,39.921394"
    }
  ]
}
```

#### 逆地理编码API（经纬度转地址）

**接口地址**：
```
GET https://restapi.amap.com/v3/geocode/regeo
```

**请求参数**：
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | String | 是 | 经纬度（经度,纬度） |
| key | String | 是 | 你的Key |

**请求示例**：
```bash
curl "https://restapi.amap.com/v3/geocode/regeo?location=116.443403,39.921394&key=你的Key"
```

**返回示例**：
```json
{
  "status": "1",
  "info": "OK",
  "infocode": "10000",
  "regeocode": {
    "formatted_address": "北京市朝阳区三里屯街道",
    "addressComponent": {
      "country": "中国",
      "province": "北京市",
      "city": "北京市",
      "district": "朝阳区",
      "adcode": "110105",
      "township": "三里屯街道"
    }
  }
}
```

#### 河道类型判断

根据逆地理编码返回的信息判断河道类型：

```python
def judge_river_type(address_component):
    """
    判断河道类型
    返回: "urban" 或 "wild"
    """
    district = address_component.get("district", "")
    township = address_component.get("township", "")

    # 城市关键词
    urban_keywords = ["市区", "城区", "市中心", "内环", "二环", "三环", "城区街道"]

    # 判断
    for keyword in urban_keywords:
        if keyword in district or keyword in township:
            return "urban"

    return "wild"
```

### 2.4 错误处理

常见错误码：

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| 10000 | 请求正常 | 正常处理 |
| 10001 | key不正确或过期 | 检查Key是否正确 |
| 10002 | 没有权限使用相应的服务 | 检查Key的服务权限 |
| 10003 | 访问已超出日配额 | 提示用户"API调用次数超限，明天再试" |
| 10004 | 用户签名未通过 | 检查签名算法 |
| 10005 | 请求非法参数 | 检查请求参数格式 |

---

## 三、配置管理

### 3.1 配置文件结构

在智能体目录下创建配置文件 `.env`：

```bash
# 和风天气API配置
QWEATHER_API_KEY=你的和风天气API_Key
QWEATHER_API_BASE_URL=https://devapi.qweather.com/v7

# 高德地图API配置
AMAP_API_KEY=你的高德地图Key
AMAP_API_BASE_URL=https://restapi.amap.com/v3
```

### 3.2 配置加载代码

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY")
AMAP_API_KEY = os.getenv("AMAP_API_KEY")
```

### 3.3 环境变量检查

在智能体启动时检查API配置：

```python
def check_api_config():
    """检查API配置"""
    errors = []

    if not QWEATHER_API_KEY:
        errors.append("和风天气API Key未配置")

    if not AMAP_API_KEY:
        errors.append("高德地图API Key未配置")

    if errors:
        print("⚠️ API配置缺失：")
        for error in errors:
            print(f"  - {error}")
        print("\n请在 .env 文件中配置API Key，详见 api-integration.md")
        return False

    return True
```

---

## 四、使用示例

### 4.1 获取完整天气数据

```python
import requests

def get_weather_data(lat, lng):
    """
    获取完整天气数据
    返回: {
        "temp": 温度,
        "pressure": 气压,
        "pressure_trend": 气压趋势,
        "sky": 天气现象,
        "wind_speed": 风速,
        "humidity": 湿度
    }
    """
    # 1. 获取实时天气
    now_url = f"https://devapi.qweather.com/v7/weather/now?location={lat},{lng}&key={QWEATHER_API_KEY}"
    now_response = requests.get(now_url).json()

    # 2. 获取3小时预报
    forecast_url = f"https://devapi.qweather.com/v7/weather/3h?location={lat},{lng}&key={QWEATHER_API_KEY}"
    forecast_response = requests.get(forecast_url).json()

    # 3. 提取数据
    now = now_response.get("now", {})
    hourly = forecast_response.get("hourly", [])

    # 4. 计算气压趋势
    pressure_list = [h.get("pressure") for h in hourly[:3]]
    pressure_trend = calculate_pressure_trend(pressure_list)

    # 5. 返回结构化数据
    return {
        "temp": now.get("temp"),
        "pressure": now.get("pressure"),
        "pressure_trend": pressure_trend,
        "sky": now.get("text"),
        "wind_speed": now.get("windScale"),
        "humidity": now.get("humidity")
    }
```

### 4.2 地址转经纬度

```python
def address_to_latlng(address):
    """
    地址转经纬度
    返回: (lat, lng)
    """
    url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&key={AMAP_API_KEY}"
    response = requests.get(url).json()

    if response.get("status") == "1":
        location = response["geocodes"][0]["location"]
        lng, lat = location.split(",")
        return float(lat), float(lng)
    else:
        return None, None
```

### 4.3 获取河道类型

```python
def get_river_type(lat, lng):
    """
    获取河道类型
    返回: "urban" 或 "wild"
    """
    url = f"https://restapi.amap.com/v3/geocode/regeo?location={lng},{lat}&key={AMAP_API_KEY}"
    response = requests.get(url).json()

    if response.get("status") == "1":
        address_component = response["regeocode"]["addressComponent"]
        return judge_river_type(address_component)
    else:
        return "wild"  # 默认野外
```

### 4.4 完整环境参数获取

```python
def get_environment_params(location_input):
    """
    获取完整环境参数
    location_input: 可以为地址或经纬度
    返回: 标准化环境参数JSON
    """
    # 1. 判断输入类型并获取经纬度
    if isinstance(location_input, str):
        # 地址输入
        lat, lng = address_to_latlng(location_input)
    else:
        # 经纬度输入
        lat, lng = location_input

    if lat is None or lng is None:
        return None

    # 2. 获取天气数据
    weather_data = get_weather_data(lat, lng)

    # 3. 获取河道类型
    river_type = get_river_type(lat, lng)

    # 4. 计算季节和昼夜
    import datetime
    now = datetime.datetime.now()
    month = now.month
    hour = now.hour

    if 3 <= month <= 5:
        season = "spring"
    elif 6 <= month <= 8:
        season = "summer"
    elif 9 <= month <= 11:
        season = "autumn"
    else:
        season = "winter"

    is_daytime = 6 <= hour < 18

    # 5. 返回标准化环境参数
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "river_type": river_type
        },
        "weather": weather_data,
        "time": {
            "season": season,
            "hour": hour,
            "is_daytime": is_daytime
        }
    }
```

---

## 五、常见问题

### Q1: API调用失败怎么办？

**A**: 请按以下步骤排查：
1. 检查API Key是否正确
2. 检查API额度是否用完
3. 检查网络连接是否正常
4. 查看API返回的错误码，对照错误码表处理

### Q2: 免费版API够用吗？

**A**:
- 和风天气免费版：1000次/天，个人使用完全够用
- 高德地图免费版：30万次/天，个人使用完全够用

### Q3: 如何保护API Key安全？

**A**:
1. 不要将API Key硬编码在代码中
2. 使用环境变量或配置文件管理
3. 不要将包含API Key的代码上传到公开仓库
4. 定期更换API Key

### Q4: 可以使用其他天气/地图API吗？

**A**: 可以，但需要修改API调用代码。支持替代方案：
- 天气API：OpenWeatherMap、彩云天气
- 地图API：百度地图、腾讯地图

---

**API配置完成标志**：
- ✅ 已申请和风天气API Key
- ✅ 已申请高德地图API Key
- ✅ 已创建.env配置文件
- ✅ 已测试API调用成功
- ✅ 已集成到智能体中

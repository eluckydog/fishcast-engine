"""
FishCast CLI - 钓鱼佬永不空军 命令行界面
=====================================
用法: python -m fishcast <鱼种> --temp 26 --pressure 1015
      python -m fishcast --list-fish
"""
import argparse, sys, json
from .engine import FishCastEngine, FishingCondition


def main():
    parser = argparse.ArgumentParser(
        description="钓鱼佬永不空军 - FishCast 钓鱼决策引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python -m fishcast 鲤鱼 --temp 26 --pressure 1015
  python -m fishcast 翘嘴 --temp 22 --pressure 1008 --river-type urban
  python -m fishcast --list-fish
  python -m fishcast 鲫鱼 --temp 15 --json
""")
    parser.add_argument("fish", nargs="?", help="目标鱼种")
    parser.add_argument("--temp", type=float, default=20, help="气温 (C)")
    parser.add_argument("--pressure", type=float, default=1013, help="气压 (hPa)")
    parser.add_argument("--weather", default="晴", help="天气")
    parser.add_argument("--wind", type=float, default=2, help="风力 (级)")
    parser.add_argument("--river-type", choices=["wild", "urban"], default="wild", help="河道类型")
    parser.add_argument("--lat", type=float, help="纬度")
    parser.add_argument("--lng", type=float, help="经度")
    parser.add_argument("--season", choices=["spring","summer","autumn","winter"], help="季节")
    parser.add_argument("--pressure-trend", choices=["rising","falling","stable"], default="stable")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--list-fish", action="store_true", help="列出所有鱼种")

    args = parser.parse_args()

    if args.list_fish:
        engine = FishCastEngine()
        print("\n".join(f"  {f}" for f in engine.list_fish_species()))
        return

    if not args.fish:
        parser.print_help()
        return

    engine = FishCastEngine()
    result = engine.evaluate(
        args.fish,
        FishingCondition(
            temp=args.temp, pressure=args.pressure, weather=args.weather,
            wind_speed=args.wind, river_type=args.river_type,
            lat=args.lat, lng=args.lng, season=args.season,
            pressure_trend=args.pressure_trend
        )
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    bar = "=" * 50
    print(f"\n{bar}")
    print(f"  钓鱼佬永不空军 - 决策报告")
    print(f"{bar}")
    print(f"  目标鱼种: {result['fish']}")
    print(f"  综合评分: {result['score']}/100")
    print(f"  出钓建议: {result['advice']}")
    print(f"{'-' * 50}")
    print(f"  水温: {result['water_temp']}C")
    print(f"  溶氧: {result['do_level']} mg/L")
    print(f"  应激: {result['stress']['level']} " +
          (f"({', '.join(result['stress']['issues'])})" if result['stress']['issues'] else ""))
    print(f"{'-' * 50}")

    if result['terrain']:
        print(f"  最佳钓点: {result['terrain'][0]['name']} ({result['terrain'][0]['code']})")
        print(f"  食物潜力: {result['terrain'][0]['food_score']}")

    print(f"  推荐钓法: {', '.join(result['method_suggestions'])}")
    print(f"  推荐饵料: {', '.join(result['bait_suggestions'])}")

    if result['time_advice']:
        ta = result['time_advice']
        print(f"  最佳时段: {ta['period']} ({ta['quality']})")
        print(f"  钓层建议: {ta['layer']}")

    print(f"\n  [详细评分]")
    for k, v in result.get('breakdown', {}).items():
        print(f"    {k}: {v}")
    print(f"{bar}\n")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
SRC = str(PROJ / "data" / "raw" / "SHEVDC_OV6N7709.csv")
OUT_DIR = str(PROJ / "data" / "processed")
(PROJ / "data" / "processed").mkdir(parents=True, exist_ok=True)
SRC = str(PROJ / "data" / "processed" / "SHEVDC_清洗后数据.csv")
OUT = str(PROJ / "data" / "processed" / "SHEVDC_时间戳转换.csv")

"""
时间戳转换脚本
输入：SHEVDC_清洗后数据.csv（time 字段为 'YYYY-MM-DD HH:MM:SS' 字符串）
输出：SHEVDC_时间戳转换.csv（保留原始所有字段，新增标准时间字段）

转换内容（时区按北京时间 UTC+8 处理，并在字段说明中标注）：
1. timestamp_unix    — Unix 时间戳（秒，UTC）
2. datetime_iso      — ISO 8601 标准格式（带 +08:00 时区）
3. date              — 日期 (YYYY-MM-DD)
4. time_hms          — 时分秒 (HH:MM:SS)
5. hour / minute / second — 拆分
6. elapsed_sec       — 相对首条记录的累计秒数
"""
import csv
from datetime import datetime, timedelta, timezone



CST = timezone(timedelta(hours=8))  # 北京时间 UTC+8

with open(SRC, encoding="utf-8", newline="") as fp:
    reader = csv.reader(fp)
    header = next(reader)
    rows = list(reader)

# 解析首条记录作为基准
first_dt = None
out_rows = []

for row in rows:
    raw = row[0]  # time
    dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")

    # 视为北京时间（UTC+8），用显式时区计算 Unix 时间戳
    dt_aware = dt.replace(tzinfo=CST)
    unix_ts = int(dt_aware.timestamp())

    if first_dt is None:
        first_dt = dt
    elapsed = int((dt - first_dt).total_seconds())

    iso = dt.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
    date = dt.strftime("%Y-%m-%d")
    time_hms = dt.strftime("%H:%M:%S")
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    out_rows.append([
        raw, unix_ts, iso, date, time_hms, hour, minute, second, elapsed
    ] + row[1:])

# 写表头
new_header = [
    "time_raw", "timestamp_unix", "datetime_iso", "date", "time_hms",
    "hour", "minute", "second", "elapsed_sec"
] + header[1:]

with open(OUT, "w", encoding="utf-8", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(new_header)
    w.writerows(out_rows)

print(f"转换完成，共 {len(out_rows)} 行")
print(f"输出: {OUT}")
print(f"时间范围: {out_rows[0][0]} ~ {out_rows[-1][0]}")
print(f"Unix时间戳范围: {out_rows[0][1]} ~ {out_rows[-1][1]}")
print(f"累计时长: {out_rows[-1][8]} 秒 = {out_rows[-1][8]/3600:.2f} 小时")
print("\n示例（首行）:")
print(dict(zip(new_header, out_rows[0])))

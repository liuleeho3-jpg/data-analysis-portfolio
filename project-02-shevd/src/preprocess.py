# -*- coding: utf-8 -*-

from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
SRC = str(PROJ / "data" / "raw" / "SHEVDC_OV6N7709.csv")
OUT_DIR = str(PROJ / "data" / "processed")
(PROJ / "data" / "processed").mkdir(parents=True, exist_ok=True)

"""
数据预处理（修订版）：更合理的异常值检测
异常值判定采用「物理合理性边界 + 3σ」混合方法，避免 IQR 对时间序列的误报。
"""
import csv
import statistics
from collections import Counter



with open(SRC, encoding="utf-8", newline="") as fp:
    reader = csv.reader(fp)
    header = next(reader)
    data = [dict(zip(header, row)) for row in reader]
n = len(data)

# 数值化
NUM = ["speed","summileage","sumvoltage","sumcurrent","soc",
       "insulationresistance","max_cell_volt","min_cell_volt","max_temp","min_temp"]
def f(v):
    try: return float(v)
    except: return None
for d in data:
    for c in NUM:
        d[c] = f(d[c])

# ===== 异常值检测（物理边界 + 3σ）=====
# 物理合理性边界（新能源汽车遥测的工程合理范围）
PHYSICAL = {
    "speed":              (0, 200),      # 车速 0~200 km/h
    "summileage":         (0, 1e6),      # 累计里程非负
    "sumvoltage":         (200, 450),    # 电池总电压
    "sumcurrent":         (-400, 400),   # 总电流
    "soc":                (0, 100),      # SOC 0~100%
    "insulationresistance":(100, 100000),# 绝缘电阻
    "max_cell_volt":      (2.5, 4.5),    # 单体电压
    "min_cell_volt":      (2.5, 4.5),
    "max_temp":           (-40, 80),     # 温度
    "min_temp":           (-40, 80),
}

outlier_records = []
outlier_summary = {}

for col in NUM:
    vals = [d[col] for d in data if d[col] is not None]
    mean = statistics.mean(vals)
    std = statistics.pstdev(vals)
    lo_3s, hi_3s = mean - 3*std, mean + 3*std
    lo_p, hi_p = PHYSICAL[col]

    cnt_phys = cnt_3s = 0
    for idx, d in enumerate(data):
        v = d[col]
        if v is None:
            continue
        is_phys = v < lo_p or v > hi_p
        is_3s = v < lo_3s or v > hi_3s
        if is_phys or is_3s:
            cnt_phys += is_phys
            cnt_3s += is_3s
            outlier_records.append({
                "行号": idx+2, "字段": col, "值": v,
                "物理越界": "是" if is_phys else "否",
                "3σ越界": "是" if is_3s else "否",
                "类型": "物理越界" if is_phys else ("统计离群" if is_3s else ""),
            })
    outlier_summary[col] = {
        "物理越界数": cnt_phys, "3σ越界数": cnt_3s,
        "物理范围": (lo_p, hi_p), "3σ范围": (round(lo_3s,2), round(hi_3s,2)),
    }

print("=== 异常值检测汇总（物理边界 + 3σ）===")
for col, s in outlier_summary.items():
    print(f"  {col}: 物理越界={s['物理越界数']}, 3σ离群={s['3σ越界数']}, 物理范围{s['物理范围']}")

# ===== 特征工程 =====
DERIVED = ["volt_diff","temp_diff","avg_cell_volt","is_charging","power"]
for d in data:
    d["volt_diff"] = round(d["max_cell_volt"] - d["min_cell_volt"], 4)
    d["temp_diff"] = d["max_temp"] - d["min_temp"]
    d["avg_cell_volt"] = round((d["max_cell_volt"] + d["min_cell_volt"]) / 2, 4)
    d["is_charging"] = 1 if d["chargestatus"] == "2" else 0
    d["power"] = round(d["sumvoltage"] * d["sumcurrent"] / 1000.0, 3)

# 保存预处理后数据
out_header = header + DERIVED + ["is_outlier"]
outlier_lines = set(r["行号"] for r in outlier_records)
with open(OUT_DIR + r"\SHEVDC_预处理后数据.csv", "w", encoding="utf-8", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(out_header)
    for idx, d in enumerate(data):
        row = [d[c] for c in header] + [d[c] for c in DERIVED] + [1 if idx+2 in outlier_lines else 0]
        w.writerow(row)

# 异常值清单
with open(OUT_DIR + r"\异常值清单.csv", "w", encoding="utf-8", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(["行号","字段","值","物理越界","3σ越界","异常类型"])
    for r in outlier_records:
        w.writerow([r["行号"], r["字段"], r["值"], r["物理越界"], r["3σ越界"], r["类型"]])

# ===== 描述性统计 =====
stat_header = ["特征","样本数","均值","方差","标准差","最小值","25%分位","中位数","75%分位","最大值","极差"]
stat_rows = []
ALL = NUM + ["volt_diff","temp_diff","avg_cell_volt","power"]
for col in ALL:
    vals = [d[col] for d in data if d[col] is not None]
    if not vals: continue
    s = sorted(vals)
    def q(p):
        k = (len(s)-1)*p; lo = int(k); hi = min(lo+1, len(s)-1)
        return s[lo] + (s[hi]-s[lo])*(k-lo)
    stat_rows.append([
        col, len(vals), round(statistics.mean(vals),4),
        round(statistics.pvariance(vals),4), round(statistics.pstdev(vals),4),
        round(min(vals),4), round(q(0.25),4), round(q(0.5),4),
        round(q(0.75),4), round(max(vals),4), round(max(vals)-min(vals),4),
    ])
with open(OUT_DIR + r"\描述性统计表.csv", "w", encoding="utf-8", newline="") as fp:
    w = csv.writer(fp); w.writerow(stat_header); w.writerows(stat_rows)

print(f"\n异常值总数: {len(outlier_records)}")
print(f"输出: 预处理后数据 / 异常值清单 / 描述性统计表")

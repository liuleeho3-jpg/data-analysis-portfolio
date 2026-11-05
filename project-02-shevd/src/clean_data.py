# -*- coding: utf-8 -*-

from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
SRC = str(PROJ / "data" / "raw" / "SHEVDC_OV6N7709.csv")
OUT_DIR = str(PROJ / "data" / "processed")
(PROJ / "data" / "processed").mkdir(parents=True, exist_ok=True)

"""
新能源汽车遥测数据清洗脚本
规则：
1. 保留原始数据（只读，不修改原表）
2. 缺失值：ffill 字符串（summileage）—— 前后正常值100%一致时可唯一推算 → 前向填充补齐，记录原行号/缺失字段/补充值/计算依据
3. 无法确认的缺失值 → 放入异常清单（本数据无此类）
4. 数值异常（里程跳变）→ 不删除不修改，放入异常清单，待人工确认
5. 完全重复记录 → 保留一条，其余标记并移除（本数据无重复）
输出：清洗后数据表 + 异常处理记录
"""
import csv
import os



CLEAN_CSV = os.path.join(OUT_DIR, "SHEVDC_清洗后数据.csv")
RECORD_CSV = os.path.join(OUT_DIR, "异常处理记录.csv")

# 读取原始数据（保留原始行号）
rows = []
with open(SRC, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    for i, row in enumerate(reader, start=2):  # 行号从2开始（第1行是表头）
        rows.append((i, row))

# 列索引（0-based）
IDX_TIME = 0
IDX_MILEAGE = 5  # summileage

# ---- 第一步：处理 summileage 的 ffill ----
n = len(rows)
segment_issues = []  # 无法唯一推算的段
fix_records = []     # 补齐记录

# 找出所有 ffill 段
segs = []
i = 0
while i < n:
    if rows[i][1][IDX_MILEAGE] == "ffill":
        s = i
        while i < n and rows[i][1][IDX_MILEAGE] == "ffill":
            i += 1
        e = i - 1
        # 段前正常值
        before = None
        for t in range(s - 1, -1, -1):
            if rows[t][1][IDX_MILEAGE] != "ffill":
                before = rows[t][1][IDX_MILEAGE]
                break
        # 段后正常值
        after = None
        for t in range(e + 1, n):
            if rows[t][1][IDX_MILEAGE] != "ffill":
                after = rows[t][1][IDX_MILEAGE]
                break
        segs.append((s, e, before, after))
    else:
        i += 1

for s, e, before, after in segs:
    if before is not None and after is not None and before == after:
        # 前后一致 → 唯一推算
        fill_val = before
        for t in range(s, e + 1):
            fix_records.append({
                "原行号": rows[t][0],
                "缺失字段": "summileage",
                "补充值": fill_val,
                "计算依据": f"ffill段前值=段后值={fill_val}，前后一致，唯一推算（前向填充）",
            })
            rows[t][1][IDX_MILEAGE] = fill_val
    elif after is None and before is not None:
        # 文件末尾的 ffill 段（无后值）：检查段内所有行 speed 是否恒为 0
        all_stopped = all(rows[t][1][4] in ("0.0", "0", "0.00") for t in range(s, e + 1))
        if all_stopped:
            # 车速恒为0，里程必然停滞 → 唯一推算为段前值
            fill_val = before
            for t in range(s, e + 1):
                fix_records.append({
                    "原行号": rows[t][0],
                    "缺失字段": "summileage",
                    "补充值": fill_val,
                    "计算依据": f"文件末尾ffill段，段前值={before}，且段内speed恒为0（车辆静止，里程不增长），唯一推算",
                })
                rows[t][1][IDX_MILEAGE] = fill_val
        else:
            segment_issues.append((s, e, before, after))
            for t in range(s, e + 1):
                fix_records.append({
                    "原行号": rows[t][0],
                    "缺失字段": "summileage",
                    "补充值": "",
                    "计算依据": "无法唯一推算（末尾段且speed非恒0），放入异常清单",
                })
    else:
        # 前后值不一致 或 其他无法唯一推算情况
        segment_issues.append((s, e, before, after))
        for t in range(s, e + 1):
            fix_records.append({
                "原行号": rows[t][0],
                "缺失字段": "summileage",
                "补充值": "",
                "计算依据": f"ffill段前值={before} 段后值={after}，前后不一致，无法唯一推算，放入异常清单",
            })

# ---- 第二步：数值异常检测（里程跳变）----
# 在补齐后的里程序列上检测异常跳变（相邻正常值差值 > 1 km 视为异常，因为正常步长是0或+1）
mileage_abnormal = []
prev_m = None
prev_line = None
for k in range(n):
    val = rows[k][1][IDX_MILEAGE]
    try:
        val_f = float(val)
    except (ValueError, TypeError):
        continue
    if prev_m is not None:
        d = val_f - prev_m
        if d < 0:
            mileage_abnormal.append({
                "原行号": rows[k][0],
                "异常字段": "summileage",
                "异常类型": "里程回退",
                "异常值": val,
                "前值": prev_m,
                "差值": round(d, 1),
                "处理方式": "未修改，暂不参与汇总，待人工确认",
            })
        elif d > 1:
            mileage_abnormal.append({
                "原行号": rows[k][0],
                "异常字段": "summileage",
                "异常类型": "里程异常跳变(Δ>1km)",
                "异常值": val,
                "前值": prev_m,
                "差值": round(d, 1),
                "处理方式": "未修改，暂不参与汇总，待人工确认",
            })
    prev_m = val_f
    prev_line = rows[k][0]

# ---- 第三步：重复记录检测（整行除time外完全相同）----
# 本数据 time 唯一，无完全重复。检测 time 重复情况（应无）
from collections import OrderedDict
seen_time = OrderedDict()
dup_records = []
for k in range(n):
    t = rows[k][1][IDX_TIME]
    if t in seen_time:
        dup_records.append({
            "原行号": rows[k][0],
            "异常字段": "time",
            "异常类型": "重复时间戳",
            "异常值": t,
            "前值": "",
            "差值": "",
            "处理方式": "标记重复并移除（保留首次出现）",
        })
    else:
        seen_time[t] = rows[k][0]

# 移除重复行（若有）
if dup_records:
    dup_lines = set(d["原行号"] for d in dup_records)
    rows = [r for r in rows if r[0] not in dup_lines]

# ---- 输出清洗后数据表 ----
with open(CLEAN_CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(header)
    for line_no, row in rows:
        w.writerow(row)

# ---- 输出异常处理记录 ----
with open(RECORD_CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    # 两个表共用一个列结构，分类放在"异常类型"里区分"缺失补齐"与"异常"
    w.writerow(["原行号", "缺失字段/异常字段", "补充值/异常值", "计算依据/处理方式"])
    # 只输出"已补齐"的记录（补充值非空）
    for rec in fix_records:
        if rec["补充值"] != "":
            w.writerow([rec["原行号"], rec["缺失字段"], rec["补充值"], rec["计算依据"]])
    for rec in mileage_abnormal:
        w.writerow([rec["原行号"], rec["异常字段"]+"("+rec["异常类型"]+")",
                    rec["异常值"], rec["处理方式"]+" 前值="+str(rec["前值"])+" 差值="+str(rec["差值"])])
    for rec in dup_records:
        w.writerow([rec["原行号"], rec["异常字段"], rec["异常值"], rec["处理方式"]])

# 汇总
print("=== 清洗完成 ===")
print(f"原始数据行数: {n}")
print(f"ffill 补齐条数: {len(fix_records)}")
print(f"ffill 段前后不一致(无法唯一推算)段数: {len(segment_issues)}")
print(f"里程异常跳变条数: {len(mileage_abnormal)}")
print(f"重复记录条数: {len(dup_records)}")
print(f"清洗后数据行数: {len(rows)}")
print(f"\n输出文件:")
print(f"  清洗后数据: {CLEAN_CSV}")
print(f"  异常处理记录: {RECORD_CSV}")

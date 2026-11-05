# 数据分析作品集 · Data Analysis Portfolio

> 统计学专业（大三）→ 数据分析 / 商业分析 / 银行风控方向
> 这里记录我用真实数据做的分析项目：每个项目都包含「问题 → 数据 → 方法 → 结论 → 局限」，而不只是代码。

## 项目一览

| # | 项目 | 主题 | 核心方法 | 状态 |
|---|------|------|----------|------|
| 1 | [泰坦尼克号生存分析](./project-01-titanic/) | 分类与统计检验 | 描述统计、卡方检验、logistic 回归 | ✅ 已完成 |
| 2 | [SHEVDC 车辆运行数据分析](./project-02-shevd/) | 时序与工况分析 | 工况识别、能量积分、电池一致性、充电会话识别 | ✅ 已完成 |
| 3 | CPI / 社零时间序列预测 | 预测 | ADF 平稳性检验、ARIMA、MAE/RMSE | 📋 计划中 |
| 4 | 银行信贷违约预测 | 风控 | logistic 回归、ROC-AUC、阈值权衡 | 📋 计划中 |

## 技能栈

- **Python**：pandas、numpy、matplotlib、scipy、scikit-learn
- **SQL**：SELECT / JOIN / GROUP BY / 子查询 / 窗口函数
- **统计方法**：描述统计、假设检验、回归分析、时间序列、抽样
- **时序与工程数据**：采样间隔/缺口处理、工况识别、能量积分、一致性指标（电压/温度极差）
- **工具**：Jupyter、Git/GitHub、Excel、Power BI

## 目录结构

```
data-analysis-portfolio/
├── README.md                  # 本文件（作品集首页）
├── .gitignore
├── project-01-titanic/        # 项目 1：泰坦尼克生存分析（已完成）
│   ├── README.md              # 项目说明：结论、方法、复现步骤
│   ├── data/                  # titanic.csv（59 KB，直接提交）
│   ├── notebooks/             # 分析过程（含全部输出与图表）
│   ├── images/                # 图表 PNG，README 里引用
│   └── docs/                  # 写作模板、学习笔记
└── project-02-shevd/          # 项目 2：SHEVDC 车辆运行数据分析（已完成）
    ├── README.md              # 结论：214 km / 21.5 kWh/100km / 2 次慢充
    ├── data/                  # 数据说明（原始 CSV 不入库）
    ├── notebooks/             # 分析过程（含全部输出与图表）
    └── images/                # 4 张图表
```

## 学习日志

每周日更新一行，招聘方看的是"持续交付"，不是"学了很多"。

| 周次 | 日期 | 本周产出 | 卡点 / 下一步 |
|------|------|----------|----------------|
| W1 | 2026.11.02–11.08 | 环境 + 数据 + 项目 1、项目 2 完成（2 个 notebook + 2 份 README + 7 张图，已推送） | 下一步：W2 时间序列（ADF + ARIMA） |
| W2 | 2026.11.09–11.15 | _待填_ | _待填_ |

## 怎么用这个仓库

1. 新项目先复制 `project-01-titanic/docs/README写作模板.md`，按【】提示逐项填写，写完删掉提示。
2. 每周至少一次 `git commit`，commit message 写清楚做了什么（如 `feat: add chi-square test for sex vs survived`）。
3. 图表放 `images/`，README 里用相对路径引用，保证 GitHub 网页能直接看到。
4. 不造假：数字必须是代码跑出来的，结论必须能讲清"所以呢"。

## 联系

- GitHub：[@liuleeho3-jpg](https://github.com/liuleeho3-jpg)

---

*配套学习计划见本地文件 `数据分析双线学习计划_2026.11-2027.08.xlsx`（计划表，不纳入仓库）。*

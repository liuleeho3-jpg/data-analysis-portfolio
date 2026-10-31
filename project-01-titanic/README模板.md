# 泰坦尼克号生存分析

> **一句话结论**：【示例】泰坦尼克号乘客的生还率主要由性别和舱位决定：女性生还率（74.2%）是男性（18.9%）的近 4 倍，头等舱生还率（63.0%）也是三等舱（24.2%）的 2.6 倍；卡方检验显示这两个差异都高度显著（p < 0.001）。
> ⚠️ 写你自己的数字，本文所有数字均为示例。

![Python](https://img.shields.io/badge/Python-3.11-blue)
![pandas](https://img.shields.io/badge/pandas-2.x-150458)
![scikit--learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E)

---

## 1. 项目背景与研究问题

**背景**：泰坦尼克号沉没时，救生艇优先安排妇女和儿童。但"优先"到底有多强？舱位（社会阶层）是否也在起作用？这些因素中哪个影响最大？

我把它拆成三个递进的问题，这也是数据分析最常见的三步：

| 编号 | 研究问题 | 方法 |
|------|----------|------|
| Q1 | 性别、舱位、年龄与生还率的关系有多大？ | 描述统计 + 可视化 |
| Q2 | 这些差异是抽样波动，还是真的显著？ | 卡方检验 / t 检验 |
| Q3 | 控制其他变量后，每个因素的独立影响有多大？ | logistic 回归（系数 / OR） |

**为什么值得做**：一个完整的数据分析闭环——清洗 → 描述 → 检验 → 建模 → 解释。面试时更容易讲出"为什么这么做"，而不是"我调了个包"。

> 【替换】在这里写一句你自己做这个项目的动机，比如课程作业、入门练手。

## 2. 数据

- **来源**：Kaggle - [Titanic: Machine Learning from Disaster](https://www.kaggle.com/competitions/titanic)
- **规模**：训练集 891 行 × 12 列；测试集 418 行
- **许可证**：公开竞赛数据（仅用于学习）

| 字段 | 含义 | 类型 | 缺失 |
|------|------|------|------|
| PassengerId | 乘客编号 | int | 0 |
| Survived | 是否生还（1=是，0=否） | int | 0 |
| Pclass | 舱位等级（1/2/3） | int | 0 |
| Name | 姓名 | str | 0 |
| Sex | 性别 | str | 0 |
| Age | 年龄 | float | **177** |
| SibSp | 兄弟姐妹/配偶数 | int | 0 |
| Parch | 父母/子女数 | int | 0 |
| Ticket | 票号 | str | 0 |
| Fare | 票价 | float | 0 |
| Cabin | 舱位号 | str | **687** |
| Embarked | 登船港口（C/Q/S） | str | **2** |

**数据局限（必写）**：样本只包含已知生还情况的乘客，存在幸存者偏差；Cabin 缺失 77%，不适合作为主变量；这是历史数据，没有"实验控制"，只能做相关性解释，不能做因果结论。

## 3. 分析流程

| 步骤 | Notebook | 内容 | 关键产出 |
|------|----------|------|----------|
| ① 数据概览 | `notebooks/01_数据概览.ipynb` | 形状、类型、缺失率、目标变量分布 | 字段表 + 缺失率表 |
| ② 描述统计与可视化 | `notebooks/02_描述统计.ipynb` | 分组均值、交叉表、柱状图/箱线图/热力图 | 3–5 张图 |
| ③ 假设检验 | `notebooks/03_可视化与检验.ipynb` | 卡方检验（性别×生还、舱位×生还）、t 检验（年龄） | p 值与解释 |
| ④ 建模与评估 | `notebooks/04_建模.ipynb` | 特征处理、logistic 回归、混淆矩阵、AUC | 模型 + 系数解释 |

## 4. 主要发现

> 下面的数字是**示例**，请用你自己代码的输出替换，并确保每个数字都能在 notebook 里找到出处。

1. **整体生还率 38.4%**（342 / 891）。
2. **性别差异最大**：女性 74.2% vs 男性 18.9%；卡方检验 χ² = 【填】, p < 0.001 → 拒绝"性别与生还独立"。
3. **舱位差异显著**：1 等 63.0%、2 等 47.3%、3 等 24.2%；p < 0.001。
4. **年龄**：儿童（<12 岁）生还率明显更高；成人年龄差异不显著（t 检验 p = 【填】）。
5. **logistic 回归**：控制舱位与年龄后，女性生还的 OR ≈ 【填】（95% CI 【填】–【填】）；Pclass 每升高一级，生还几率下降约 【填】%。
6. **模型**：准确率 【填】%、AUC 【填】；主要错误是把"三等舱男性中少数生还者"预测为死亡。

**结论（业务含义）**：救援优先级确实偏向妇女儿童，但阶层差异同样明显——在同等性别下，头等舱生还概率显著更高。这不是"性别决定生死"，而是"性别 + 阶层共同作用"。

**【图 1】各组生还率对比**（放 `images/survival_by_sex_pclass.png`）

**【图 2】模型 AUC 曲线**（放 `images/roc_curve.png`）

## 5. 方法与取舍（面试会问）

| 选择 | 为什么 | 替代方案与代价 |
|------|--------|----------------|
| 卡方检验而不是直接比均值 | 两个变量都是分类变量，检验独立性 | 直接比较会忽略抽样误差 |
| logistic 回归而不是线性回归 | 标签是 0/1，线性回归预测值会超出 [0,1] | 树模型可解释性差，样本 891 也容易过拟合 |
| 报告 OR（优势比）而不是裸系数 | OR 可以直接说"几倍" | 系数单位是 log-odds，非专业读者看不懂 |
| Age 用中位数填充 | 缺失 20%，删行会丢样本 | 用模型预测填充更准，但入门阶段过度复杂 |
| Cabin 不进入主模型 | 缺失 77%，且与 Pclass 高度相关 | 可以转成"有无舱位"哑变量，作为改进项 |

## 6. 如何复现

```bash
git clone https://github.com/你的用户名/data-analysis-portfolio.git
cd data-analysis-portfolio/project-01-titanic

# 建议虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

jupyter lab
# 按 notebooks/01 → 04 的顺序运行
```

**数据下载**（任选其一）：

```bash
# 方式 1：Kaggle 官网下载 train.csv（需登录）
# 方式 2：备用镜像（无需账号，891 行，列名一致）
curl -L -o data/titanic.csv https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv
```

## 7. 项目结构

```
project-01-titanic/
├── README.md
├── requirements.txt
├── data/
│   └── titanic.csv
├── notebooks/
│   ├── 01_数据概览.ipynb
│   ├── 02_描述统计.ipynb
│   ├── 03_可视化与检验.ipynb
│   └── 04_建模.ipynb
└── images/
    ├── survival_by_sex_pclass.png
    └── roc_curve.png
```

## 8. 局限与改进方向

- 数据为历史观测数据，**只能解释相关性，不能下因果结论**；
- 未做交叉验证和调参，模型指标可能高估；
- 未利用 Name 中的称谓（Mr/Mrs/Miss）和 Ticket 分组信息，这是已知的有效特征；
- 改进：加入家庭规模特征（SibSp + Parch + 1）、5 折交叉验证、随机森林对比。

## 9. 参考

- [Kaggle Titanic 竞赛](https://www.kaggle.com/competitions/titanic)
- [Datawhale 动手学数据分析](https://github.com/datawhalechina/hands-on-data-analysis)
- 《利用 Python 进行数据分析》（Wes McKinney）

---

## 写作检查清单（提交前逐项打勾）

- [ ] 一句话结论在最上面，且是**自己的数字**
- [ ] 每个图都有 1–2 句解释（"这张图说明了什么"），不是只放图
- [ ] p 值有解释（p < 0.05 意味着什么、不意味着什么）
- [ ] 写了数据局限和"不能下因果结论"
- [ ] 复现步骤别人能照着跑通（requirements.txt 完整）
- [ ] 能在 3 分钟内讲完：问题 → 方法 → 发现 → 局限
- [ ] 没有"我学会了 pandas 的 xx 函数"这类流水账，全部围绕结论

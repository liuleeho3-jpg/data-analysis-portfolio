# 数据说明（data/）

## 文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `titanic.csv` | 约 60 KB | 泰坦尼克号训练集，891 行 × 12 列 |

## 获取方式

```bash
# 备用镜像（无需 Kaggle 账号，已核对：891 行，列名与 Kaggle 一致）
curl -L -o data/titanic.csv https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv
```

也可以从 Kaggle 官网下载后重命名：https://www.kaggle.com/competitions/titanic/data

## 为什么提交数据文件

这份数据不到 1 MB 且完全公开，直接提交可以让别人 clone 后立刻复现。
如果以后处理几十 MB 以上的数据，请不要提交，改为在本文件写清下载地址和校验方式。

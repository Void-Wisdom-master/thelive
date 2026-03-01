# 八字排盘系统 (BaZi Calculator)

一个基于 Streamlit 的八字排盘和十神分析系统。

## 功能特性

- 根据公历日期和时辰计算八字（四柱八字）
- 自动判断十神关系

## 项目结构

```
bazi-calculator/
├── app.py                 # Streamlit 主应用
├── requirements.txt       # 项目依赖
├── src/
│   ├── __init__.py
│   ├── calendar_utils.py  # 农历转换工具
│   ├── bazi_calculator.py # 八字计算核心
│   └── shishen.py         # 十神判断逻辑
└── README.md
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
streamlit run app.py
```

## 使用说明

1. 选择出生日期（公历）
2. 选择出生时辰
3. 选择性别
4. 点击"开始排盘"按钮
5. 查看八字和十神分析结果

## 技术栈

- Python 3.8+
- Streamlit
- Lunarcalendar (农历转换)
- 传统命理学算法

## 部署

### Streamlit Cloud 部署

1. 将代码推送到 GitHub 仓库
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 连接你的 GitHub 仓库
4. 选择 `app.py` 作为主文件
5. 点击部署

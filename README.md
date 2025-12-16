# 社交网络图论分析系统

一个用于课程设计的完整示例项目，展示了图论在社交网络分析中的典型应用：
- 合成无标度社交网络（Barabási–Albert, BA）
- 计算网络基本结构指标
- 识别关键用户（多种中心性）
- 检测社区并分析其结构特征（支持算法切换）
- 生成多种可视化图
- 提供 Streamlit 交互式应用与命令行两种运行方式

---

## 🌟 亮点特性

- 模块化、可复现：随机种子受控，结果可重复；模块清晰，便于复用
- 社区算法可切换：支持自动选择/Louvain（python-louvain）/Louvain（NetworkX）/Girvan–Newman
- 颜色不重复：针对大量社区的可视化，引入可扩展的高区分度调色板，避免同色问题
- 缓存友好：自定义 `hash_funcs` 支持 `nx.Graph` 在 Streamlit 中安全缓存
- 交互清晰：
  - 侧边栏：网络规模、BA 参数、随机种子、重新生成
  - 顶部：社区算法选择与“当前社区数”即时刷新
  - 页面内：用户/社区单框模糊搜索（在对应标签页内使用）

---

## 📁 目录结构

```
.
├── app.py                      # Streamlit 交互应用（推荐入口）
├── main.py                     # 命令行程序（批量输出图片/CSV/报告）
├── data_generator.py           # BA 网络生成与节点/边属性填充
├── network_analysis.py         # 基本指标、中心性计算与解释
├── community_detection.py      # 社区检测封装（Louvain/GN）
├── visualization.py            # Matplotlib 可视化（网络/统计/对比）
├── requirements.txt            # 依赖列表
├── test_modules.py             # 快速模块自检脚本
├── README.md                   # 项目说明（本文件）
├── USAGE.md                    # 使用说明（详细步骤）
└── results/                    # 运行后生成的结果目录（图片/CSV/报告）
```

---

## 🚀 快速开始

### 1) 安装依赖

```bash
# 建议使用虚拟环境（conda 或 venv）
pip install -r requirements.txt
```

### 2) 交互式运行（推荐）

```bash
# 使用 Streamlit 运行（避免直接 python app.py）
python -m streamlit run app.py
# 或
streamlit run app.py
```

打开浏览器访问 http://localhost:8501。

### 3) 命令行运行（批量输出）

```bash
python main.py --nodes 300 --m 3 --seed 42 --out ./results
```

输出内容见“运行产物”章节。

---

## 🔧 功能说明

### 1. 数据生成（data_generator.py）
- 使用 `networkx.barabasi_albert_graph(n, m, seed)` 构造无标度网络
- 为节点添加 `user_id / join_time / activity_level` 属性
- 为边添加 `relationship_type / interaction_count` 属性

### 2. 网络分析（network_analysis.py）
- 基本指标：节点数、边数、密度、平均度、平均聚类系数、平均最短路径长度、网络直径、度分布统计
- 中心性：度中心性、介数中心性、接近中心性、特征向量中心性、综合中心性加权排名
- 结果解释：对“小世界”“无标度”等现象给出简要分析

### 3. 社区检测（community_detection.py & app.py）
- 支持算法：
  - 自动选择（优先 `python-louvain`，若不可用回退 `networkx` 实现，再回退 Girvan–Newman）
  - Louvain（python-louvain）
  - Louvain（NetworkX 内置，`seed=42`）
  - Girvan–Newman（备选，开销较大）
- Streamlit 顶部“社区检测算法选择”与“运行所选算法”按钮
- “当前社区数”会在运行后即时刷新，保证与提示一致
- 社区结构分析：密度、凝聚力（内部边 / 全部边）、内外部边对比等

### 4. 可视化（visualization.py）
- 社区着色网络图：
  - 自定义 `_get_distinct_colors`，聚合多套离散调色板，不足再用 HSV 均匀采样，避免颜色重复
  - 图例自适应多列展示
- 中心性着色网络图：节点大小/颜色代表综合中心性
- 度分布（线性/对数）
- 中心性对比柱状图、社区统计图（规模/密度/凝聚力/内外部边）

### 5. 交互（app.py）
- 侧边栏：节点数、BA 参数、随机种子；“生成/重新生成网络”可清空缓存并重建网络
- 标签页：
  - 网络基本分析
  - 关键用户识别（单框模糊搜索用户）
  - 社区结构检测（单框模糊搜索社区）
  - 网络可视化（社区/中心性，布局可选：spring/circular/kamada_kawai）
  - 统计报告（可下载 .txt 报告与 .csv 数据）
- 缓存：使用 `@st.cache_data(hash_funcs={nx.Graph: _nx_graph_hasher})`，为 `nx.Graph` 提供可复现哈希

---

## 📦 运行产物（main.py）

默认输出到 `./results/`：
- 图片：
  - 01_network_communities.png
  - 02_network_centrality.png
  - 03_degree_distribution.png
  - 04_centrality_comparison.png
  - 05_community_statistics.png
- 数据：
  - basic_metrics.json
  - centrality.csv
  - community_stats.csv
- 报告：
  - report.txt（综合分析文本）

---

## ❓常见问题

- Q: 直接 `python app.py` 只打印日志不启动网页？
  - A: 需用 `streamlit run app.py` 或 `python -m streamlit run app.py` 启动。
- Q: 社区颜色为什么会重复？
  - A: 已在 `visualization.py` 中使用扩展调色与 HSV 采样避免重复；社区很多时颜色仍保持区分度。
- Q: 运行后“当前社区数”与提示不一致？
  - A: 已通过占位符实时刷新指标；若仍不一致，浏览器强刷或点击“生成/重新生成网络”清缓存。

---

## 📝 许可证

项目仅用于教学与课程设计用途。

---

## 📌 版本摘要

- 2025-12-16
  - 新增：社区算法选择器与即时刷新“当前社区数”
  - 新增：高区分度社区调色板，解决大社区数量下颜色重复
  - 改进：自定义 `hash_funcs` 支持 `nx.Graph` 缓存
  - 调整：移除首页副标题文本，简化抬头

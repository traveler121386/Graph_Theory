# 使用说明（USAGE）

本文档介绍如何在本项目中快速上手、正确运行以及导出结果。

---

## 1. 环境准备

建议使用 Python 3.8+，并在虚拟环境（conda/venv）中安装依赖。

```bash
# 1) 克隆或进入项目目录后
# 2) 创建并激活虚拟环境（任选其一）
# conda create -n sna python=3.10 -y && conda activate sna
# python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 3) 安装依赖
pip install -r requirements.txt
```

注意：如果系统中安装了 d2l 之类要求固定 numpy/matplotlib/pandas 版本的包，建议使用独立虚拟环境，以免依赖冲突。

---

## 2. 交互式运行（推荐）

必须用 Streamlit 方式启动，直接 `python app.py` 不会启动网页界面。

```bash
# 推荐写法（兼容性最好）
python -m streamlit run app.py
# 或
streamlit run app.py
```

启动后，终端会输出访问地址（通常为 http://localhost:8501 ）。

### 2.1 页面结构

- 顶部：
  - 标题
  - 社区检测算法选择（自动/Louvain/NetworkX/GN）和“运行所选算法”按钮
  - 当前社区数（按钮运行后即时刷新）
- 左侧侧边栏：
  - 节点数量（用户数）
  - BA 模型参数 m（每个新节点的连接数）
  - 随机种子
  - 生成/重新生成网络（清空缓存并重建网络）
- 标签页：
  - 网络基本分析：规模/密度/聚类系数/路径长度等
  - 关键用户识别：中心性对比；下拉框支持模糊搜索用户
  - 社区结构检测：统计表与图；下拉框支持模糊搜索社区
  - 网络可视化：
    - 社区着色：使用高区分度调色板，避免大量社区颜色相同
    - 中心性着色：节点大小与颜色映射综合中心性
    - 布局可选：spring/circular/kamada_kawai
  - 统计报告：可下载 TXT 报告与 CSV 数据

### 2.2 缓存机制

- 为了提升性能，项目用 `@st.cache_data` 缓存分析与社区检测结果
- 对 `nx.Graph` 对象使用自定义哈希 `_nx_graph_hasher`，只基于拓扑（节点/边），保证可复现
- 点击“生成/重新生成网络”会 `st.cache_resource.clear()` 与 `st.cache_data.clear()`，确保结果更新

---

## 3. 命令行运行

适用于一次性批量导出可视化图片、CSV 与报告。

```bash
python main.py --nodes 300 --m 3 --seed 42 --out ./results
```

参数：
- `--nodes`：节点数量（默认 300）
- `--m`：BA 模型参数（默认 3）
- `--seed`：随机种子（默认 42）
- `--out`：输出目录（默认 ./results）

输出文件（位于 `--out` 指定目录）：
- 图片：
  - 01_network_communities.png（社区着色）
  - 02_network_centrality.png（中心性着色）
  - 03_degree_distribution.png（度分布）
  - 04_centrality_comparison.png（中心性对比）
  - 05_community_statistics.png（社区统计）
- 数据：
  - basic_metrics.json（基本指标）
  - centrality.csv（中心性）
  - community_stats.csv（社区统计）
- 报告：
  - report.txt（综合分析文本）

---

## 4. 模块说明

### 4.1 data_generator.py
- `SocialNetworkGenerator.generate_complete_network(n_nodes, m)`: 生成 BA 网络并附加节点/边属性。

### 4.2 network_analysis.py
- `NetworkAnalyzer.run_all_analysis()`: 计算基本指标与中心性并输出解释。

### 4.3 community_detection.py
- `CommunityDetector.detect_communities_louvain()`：默认 Louvain 检测（python-louvain / NetworkX 回退）。
- `CommunityDetector.detect_communities_girvan_newman()`：Girvan–Newman 作为备选。

### 4.4 visualization.py
- `NetworkVisualizer.visualize_network_with_communities()`：社区着色（高区分度调色板）。
- `NetworkVisualizer.visualize_network_with_centrality()`：中心性着色。
- 其余方法用于生成度分布、中心性对比、社区统计等图表。

### 4.5 app.py
- Streamlit 应用入口；提供参数控制、算法切换、搜索、图表与报告下载。

### 4.6 main.py
- 命令行入口；一键批量导出全部成果。

---

## 5. 常见问题（FAQ）

1) 页面顶部“当前社区数”和提示不一致？
- 现在点击“运行所选算法”后会即时刷新该指标；如仍不一致，强制刷新浏览器或点击“生成/重新生成网络”。

2) 社区颜色重复或区分度不够？
- 已引入 `_get_distinct_colors`，聚合多套调色板+HSV 补色，适合社区数量较多的情况。

3) 直接 `python app.py` 不能打开网页？
- 需要 `streamlit run app.py` 启动。

4) 想强制某种社区算法？
- 顶部“社区检测算法选择”切换即可，也可在代码中调用 `detect_communities(G, algo="girvan_newman")` 等。

5) 如何获得可复现的 Louvain 结果？
- NetworkX 版本已使用 `seed=42`；若使用 python-louvain，可在其调用中设置 `random_state=42`（可在 community_detection.py 中调整）。

---

## 6. 参考建议

- 小规模演示：`--nodes 100`，运行更快，适合课堂展示
- 中等规模研究：`--nodes 300 --m 3`（默认）
- 大规模尝试：`--nodes 1000 --m 5`（耗时与内存需求更高）

---

## 7. 版本信息

- 更新时间：2025-12-16
- 更新内容：
  - 顶部社区算法选择与指标即时刷新
  - 自定义 Graph 哈希，Streamlit 缓存更稳定
  - 社区可视化采用高区分度调色方案
  - 移除首页副标题，简洁呈现

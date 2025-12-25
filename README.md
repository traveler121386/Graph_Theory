# 社交网络图论分析系统

一个用于课程设计的完整示例项目，展示了图论在社交网络分析中的典型应用。系统采用模块化设计，提供独立的实验脚本，每个实验的结果保存在对应的输出目录中，便于管理和分析。

## 🌟 项目特点

- **模块化设计**：核心功能分离为独立模块，便于维护和扩展
- **实验脚本化**：每个实验都有独立的脚本，一键运行即可生成结果
- **结果分类存储**：每个实验的结果保存在独立的 `resultX/` 目录中
- **可复现性**：使用固定随机种子，确保结果可复现
- **算法可切换**：支持多种社区检测算法（Louvain/Girvan-Newman）
- **交互式界面**：提供 Streamlit 交互应用，方便参数调整和结果查看
- **完整可视化**：生成多种图表，直观展示网络特征

---

## 📁 项目结构

```
NetWork/
├── 核心模块/
│   ├── data_generator.py          # BA网络生成与节点/边属性填充
│   ├── network_analysis.py         # 基本指标、中心性计算与解释
│   ├── community_detection.py     # 社区检测封装（Louvain/GN）
│   ├── visualization.py           # Matplotlib可视化（网络/统计/对比）
│   ├── app.py                     # Streamlit交互应用
│   └── main.py                    # 主程序（完整分析流程，可选）
│
├── 实验脚本/
│   ├── experiment1.py              # 实验一：网络生成与基本特性验证
│   ├── experiment2.py             # 实验二：中心性指标计算与关键用户识别
│   ├── algorithm_comparison.py    # 实验三：社区检测算法对比分析
│   ├── performance_test.py        # 实验四：网络规模对算法性能的影响
│   ├── plot_performance.py        # 实验四：性能曲线图生成
│   └── test_experiment5.py        # 实验五：交互式系统功能验证
│
├── 输出目录/
│   ├── result1/                   # 实验一输出（网络基本特性）
│   ├── result2/                   # 实验二输出（中心性分析）
│   ├── result3/                   # 实验三输出（算法对比）
│   ├── result4/                   # 实验四输出（性能测试）
│   ├── result5/                   # 实验五输出（功能测试）
│   └── results/                   # main.py的完整分析输出（可选）
│
├── 文档/
│   ├── README.md                  # 项目说明（本文件）
│   ├── 实验操作指南.md            # 详细的实验操作指南
│   ├── 实验设计.md                # 实验设计文档
│   ├── USAGE.md                   # 使用说明
│   └── PRESENTATION.md            # 演示说明
│
└── 配置文件/
    ├── requirements.txt            # Python依赖列表
    └── test_modules.py            # 模块测试脚本
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 验证环境（可选）
python test_modules.py
```

### 2. 运行实验

系统提供了5个独立的实验脚本，按顺序运行即可：

```bash
# 实验一：网络生成与基本特性验证
python experiment1.py
# 输出目录: result1/

# 实验二：中心性指标计算与关键用户识别
python experiment2.py
# 输出目录: result2/

# 实验三：社区检测算法对比分析
python algorithm_comparison.py
# 输出目录: result3/

# 实验四：网络规模对算法性能的影响
python performance_test.py        # 生成性能测试数据
python plot_performance.py        # 生成性能曲线图
# 输出目录: result4/

# 实验五：交互式系统功能验证
python test_experiment5.py
# 输出目录: result5/
```

### 3. 交互式运行（可选）

```bash
# 启动Streamlit交互应用
streamlit run app.py
```

打开浏览器访问 http://localhost:8501

### 4. 完整分析（可选）

如果想运行完整的分析流程（包含所有功能），可以使用：

```bash
python main.py --nodes 300 --m 3 --seed 42 --out ./results
```

---

## 📊 各实验说明

### 实验一：网络生成与基本特性验证

**脚本**：`experiment1.py`  
**输出目录**：`result1/`

**功能**：
- 使用BA模型生成无标度社交网络
- 计算网络基本指标（节点数、边数、密度、聚类系数等）
- 生成度分布图（验证幂律分布）

**输出文件**：
- `basic_metrics.json` - 基本指标JSON文件
- `网络基本特性指标表.csv` - 基本指标表格
- `03_degree_distribution.png` - 度分布图

### 实验二：中心性指标计算与关键用户识别

**脚本**：`experiment2.py`  
**输出目录**：`result2/`

**功能**：
- 计算四种中心性指标（度、介数、接近、特征向量）
- 计算综合中心性排名
- 识别关键用户

**输出文件**：
- `centrality.csv` - 所有用户的完整中心性数据
- `用户中心性指标排名表.csv` - 排名前15的关键用户
- `04_centrality_comparison.png` - 中心性对比柱状图

### 实验三：社区检测算法对比分析

**脚本**：`algorithm_comparison.py`  
**输出目录**：`result3/`

**功能**：
- 对比Louvain和Girvan-Newman两种算法
- 计算模块度、社区数、运行时间等指标
- 生成算法对比表格

**输出文件**：
- `算法对比表.csv` - 两种算法的对比表格
- `社区统计_Louvain.csv` - Louvain算法详细统计
- `社区统计_Girvan-Newman.csv` - Girvan-Newman算法详细统计
- `社区检测对比表.csv` - 社区检测详细统计

### 实验四：网络规模对算法性能的影响

**脚本**：`performance_test.py` + `plot_performance.py`  
**输出目录**：`result4/`

**功能**：
- 测试不同规模网络下的算法性能
- 记录各模块的运行时间
- 生成性能曲线图

**输出文件**：
- `性能测试结果表.csv` - 性能测试数据
- `性能测试曲线图.png` - 综合性能分析图（4个子图）
- `性能测试单图.png` - 单一总时间曲线图

### 实验五：交互式系统功能验证

**脚本**：`test_experiment5.py`  
**输出目录**：`result5/`

**功能**：
- 自动测试所有功能模块
- 验证参数调整、算法选择、数据展示等功能
- 生成功能测试报告和统计图表

**输出文件**：
- `交互式系统功能测试表.csv` - 功能测试结果
- `功能模块统计表.csv` - 模块通过率统计
- `测试报告.txt` - 完整测试报告
- `测试结果统计图.png` - 测试结果统计图
- `响应时间对比图.png` - 响应时间对比图

---

## 🔧 核心功能模块

### 1. 数据生成（data_generator.py）

- 使用 `networkx.barabasi_albert_graph()` 构造无标度网络
- 为节点添加 `user_id / join_time / activity_level` 属性
- 为边添加 `relationship_type / interaction_count` 属性

### 2. 网络分析（network_analysis.py）

- **基本指标**：节点数、边数、密度、平均度、平均聚类系数、平均最短路径长度、网络直径、度分布统计
- **中心性指标**：度中心性、介数中心性、接近中心性、特征向量中心性
- **综合中心性**：加权求和模型，权重向量 $$W=[0.3, 0.3, 0.2, 0.2]$$
- **结果解释**：对"小世界""无标度"等现象给出简要分析

### 3. 社区检测（community_detection.py）

- **支持算法**：
  - Louvain（python-louvain，优先）
  - Louvain（NetworkX 内置）
  - Girvan–Newman（备选）
- **社区分析**：密度、凝聚力（内部边 / 全部边）、内外部边对比等

### 4. 可视化（visualization.py）

- **社区着色网络图**：高区分度调色板，避免颜色重复
- **中心性着色网络图**：节点大小/颜色代表综合中心性
- **度分布图**：线性坐标和对数坐标
- **中心性对比图**：柱状图对比
- **社区统计图**：规模/密度/凝聚力/内外部边

### 5. 交互应用（app.py）

- **侧边栏**：节点数、BA参数、随机种子、重新生成网络
- **算法选择**：社区检测算法选择器
- **标签页**：
  - 网络基本分析
  - 关键用户识别（支持用户搜索）
  - 社区结构检测（支持社区搜索）
  - 网络可视化（多种布局和着色方式）
  - 统计报告（可下载）

---

## 📦 输出文件说明

### 各实验输出目录

| 实验 | 输出目录 | 主要文件 |
|------|---------|---------|
| 实验一 | `result1/` | basic_metrics.json<br>网络基本特性指标表.csv<br>03_degree_distribution.png |
| 实验二 | `result2/` | centrality.csv<br>用户中心性指标排名表.csv<br>04_centrality_comparison.png |
| 实验三 | `result3/` | 算法对比表.csv<br>社区统计_Louvain.csv<br>社区统计_Girvan-Newman.csv |
| 实验四 | `result4/` | 性能测试结果表.csv<br>性能测试曲线图.png<br>性能测试单图.png |
| 实验五 | `result5/` | 交互式系统功能测试表.csv<br>功能模块统计表.csv<br>测试报告.txt |

### 完整分析输出（可选）

运行 `python main.py` 后，会在 `results/` 目录下生成：

**数据文件**：
- `basic_metrics.json` - 网络基本指标
- `centrality.csv` - 所有用户的中心性数据
- `community_stats.csv` - 社区统计信息
- `report.txt` - 综合分析文本报告

**可视化图片**：
- `01_network_communities.png` - 社区着色网络图
- `02_network_centrality.png` - 中心性着色网络图
- `03_degree_distribution.png` - 度分布图
- `04_centrality_comparison.png` - 中心性对比图
- `05_community_statistics.png` - 社区统计图

---

## 🎯 使用场景

### 课程设计/实验报告

1. 运行各实验脚本生成结果
2. 从对应的 `resultX/` 目录中提取数据表格和图片
3. 参考 `实验操作指南.md` 进行分析
4. 将结果插入论文或报告

### 快速演示

```bash
# 启动交互式应用
streamlit run app.py
```

在浏览器中调整参数，实时查看分析结果。

### 批量分析

```bash
# 运行完整分析流程
python main.py --nodes 300 --m 3 --seed 42 --out ./results
```

---

## 📚 文档说明

- **README.md** - 项目总体说明（本文件）
- **实验操作指南.md** - 详细的实验操作步骤和结果说明
- **实验设计.md** - 实验设计文档（包含代码实现和结果分析）
- **USAGE.md** - 使用说明（Streamlit应用详细说明）

---

## ❓ 常见问题

### Q1: 如何修改网络规模？

**A**: 修改实验脚本中的参数，例如：

```python
# 在 experiment1.py 中修改
n_nodes = 500  # 改为500节点
```

### Q2: 如何确保结果可复现？

**A**: 所有脚本使用固定随机种子（`seed=42`），相同参数下结果完全一致。

### Q3: 为什么实验三需要单独运行脚本？

**A**: `main.py` 默认只运行 Louvain 算法。要对比两种算法，必须运行 `algorithm_comparison.py`。

### Q4: Streamlit应用无法启动？

**A**: 确保使用正确的命令：

```bash
streamlit run app.py
```

不要直接运行 `python app.py`。

### Q5: 实验四需要运行两个脚本吗？

**A**: 是的：
1. `performance_test.py` - 生成性能测试数据
2. `plot_performance.py` - 生成性能曲线图

### Q6: 输出文件在哪里？

**A**: 所有输出文件保存在对应的 `result1/` 到 `result5/` 目录中。

---

## 🔬 技术栈

- **Python 3.8+**
- **NetworkX 3.2.1** - 图论算法和数据结构
- **Matplotlib 3.8.2** - 数据可视化
- **Pandas 2.1.3** - 数据处理和分析
- **NumPy 1.26.3** - 数值计算
- **Streamlit 1.28.1** - 交互式Web应用
- **python-louvain 0.16** - Louvain社区检测算法

---

## 📝 许可证

项目仅用于教学与课程设计用途。

---

## 📌 版本信息

- **当前版本**：v2.0
- **更新日期**：2025-12-16

### 主要更新

- ✅ 创建独立的实验脚本（experiment1-5）
- ✅ 实验结果分类存储（result1-5目录）
- ✅ 完善实验操作指南
- ✅ 优化项目结构，删除临时文件
- ✅ 修复性能测试脚本的bug

---

## 🎓 课程设计建议

完成所有实验后，建议按以下结构整理实验报告：

1. **实验环境**：硬件、软件、依赖版本
2. **实验一结果**：网络基本特性指标表 + 度分布图
3. **实验二结果**：用户中心性排名表 + 中心性对比图
4. **实验三结果**：算法对比表 + 社区统计图
5. **实验四结果**：性能测试结果表 + 时间-规模曲线图
6. **实验五结果**：功能测试表 + 界面截图
7. **结果分析**：对每个实验的结果进行详细分析
8. **结论**：总结系统性能和算法效果

所有实验数据表格和图片都可以直接从对应的 `resultX/` 目录中获取。

---

## 📞 获取帮助

- 查看 `实验操作指南.md` 获取详细的实验步骤
- 查看 `USAGE.md` 了解Streamlit应用的详细使用方法
- 运行 `python test_modules.py` 验证环境配置

---

**祝实验顺利！** 🎉

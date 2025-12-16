"""
Streamlit 交互应用
提供图论在社交网络分析中应用的交互式展示平台
"""

import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import sys
import hashlib

# 导入自定义模块
from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from community_detection import CommunityDetector
from visualization import NetworkVisualizer


# 页面配置
st.set_page_config(
    page_title="社交网络图论分析",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def _nx_graph_hasher(g: nx.Graph) -> str:
    """为 NetworkX Graph 定义稳定的哈希函数，用于 Streamlit 缓存。
    仅基于拓扑（节点与边）来生成摘要，忽略属性以提升速度与稳定性。
    """
    try:
        nodes = tuple(sorted(g.nodes()))
        edges = tuple(sorted((min(u, v), max(u, v)) for u, v in g.edges()))
        payload = repr((nodes, edges)).encode("utf-8")
        return hashlib.md5(payload).hexdigest()
    except Exception:
        # 兜底：使用规模特征，虽然可能命中率更高，但能保证不报错
        return f"n{g.number_of_nodes()}-e{g.number_of_edges()}-d{nx.density(g):.6f}"


@st.cache_resource
def load_network_data(n_nodes=300, m=3, seed=42):
    """加载网络数据（缓存）"""
    generator = SocialNetworkGenerator(seed=seed)
    G = generator.generate_complete_network(n_nodes=n_nodes, m=m)
    return G


@st.cache_data(hash_funcs={nx.Graph: _nx_graph_hasher})
def analyze_network(G):
    """分析网络（缓存）- 使用自定义哈希函数缓存 Graph 结果"""
    analyzer = NetworkAnalyzer(G)
    results = analyzer.run_all_analysis()
    return results


@st.cache_data(hash_funcs={nx.Graph: _nx_graph_hasher})
def detect_communities(G, algo: str = "auto"):
    """检测社区（缓存）- 支持算法选择
    algo 取值："auto" | "louvain_pl" | "louvain_nx" | "girvan_newman"
    返回: (detector, results) 且 results['algo_used'] 标明实际使用算法
    """
    detector = CommunityDetector(G)
    algo_used = None
    try:
        if algo == "louvain_pl":
            # 强制 python-louvain
            try:
                import community as community_louvain  # noqa: F401
                detector.detect_communities_louvain()
                algo_used = "Louvain (python-louvain)"
            except Exception:
                # 回退到 NetworkX Louvain
                import networkx.algorithms.community as nx_community  # noqa: F401
                communities_generator = nx_community.louvain_communities(G, seed=42)
                detector.communities = {i: comm for i, comm in enumerate(communities_generator)}
                detector._build_community_map()
                algo_used = "Louvain (NetworkX) [fallback]"
        elif algo == "louvain_nx":
            import networkx.algorithms.community as nx_community  # noqa: F401
            communities_generator = nx_community.louvain_communities(G, seed=42)
            detector.communities = {i: comm for i, comm in enumerate(communities_generator)}
            detector._build_community_map()
            algo_used = "Louvain (NetworkX)"
        elif algo == "girvan_newman":
            detector.detect_communities_girvan_newman()
            algo_used = "Girvan–Newman"
        else:
            # auto: 先 python-louvain，再 NetworkX，最后 GN
            try:
                import community as community_louvain  # noqa: F401
                detector.detect_communities_louvain()
                algo_used = "Louvain (python-louvain)"
            except Exception:
                try:
                    import networkx.algorithms.community as nx_community  # noqa: F401
                    communities_generator = nx_community.louvain_communities(G, seed=42)
                    detector.communities = {i: comm for i, comm in enumerate(communities_generator)}
                    detector._build_community_map()
                    algo_used = "Louvain (NetworkX)"
                except Exception:
                    detector.detect_communities_girvan_newman()
                    algo_used = "Girvan–Newman [fallback]"
    except Exception:
        # 最终兜底
        detector.detect_communities_girvan_newman()
        algo_used = "Girvan–Newman [fallback]"

    # 后续统一分析
    stats_df = detector.analyze_community_structure()
    detector.analyze_community_meaning(stats_df)
    results = detector.analysis_results
    results['algo_used'] = algo_used
    return detector, results


def main():
    """主函数"""
    
    # 标题和描述
    st.markdown("""
    <div style='text-align: center; padding: 8px 0 4px 0;'>
        <h1>🌐 社交网络图论分析系统</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏配置
    st.sidebar.markdown("## ⚙️ 配置参数")
    
    # 网络参数
    st.sidebar.markdown("### 网络生成参数")
    n_nodes = st.sidebar.slider("节点数量（用户数）", 50, 500, 300, step=50)
    m = st.sidebar.slider("BA模型参数（每个新节点的连接数）", 1, 10, 3)
    seed = st.sidebar.number_input("随机种子", value=42)
    
    # 加载数据
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 生成/重新生成网络", use_container_width=True):
        st.cache_resource.clear()
        st.cache_data.clear()
    
    # 加载网络
    with st.spinner("正在加载网络数据..."):
        G = load_network_data(n_nodes, m, seed)

    # 预先计算分析（已缓存，首次会稍慢，之后复用）
    with st.spinner("正在进行网络分析（首次会稍慢）..."):
        analysis_results = analyze_network(G)
    centrality_df = analysis_results['centrality']

    # 默认社区检测结果（auto），用于首次加载与兜底
    default_detector, default_comm_results = detect_communities(G, algo="auto")
    # 如果 session 中已有用户选择的算法结果，则优先使用
    community_results = st.session_state.get('community_results', default_comm_results)
    community_detector_map = st.session_state.get('community_detector_map', default_detector.community_map)
    community_stats = community_results['community_stats']

    # === 社区检测算法选择（放在页面标题下方，全局生效） ===
    st.markdown("### 🧩 社区检测算法选择")
    colA, colB, colC = st.columns([3, 1, 2])
    with colA:
        algo_label = st.selectbox(
            "选择社区检测算法",
            options=[
                "自动选择（优先 Louvain，失败回退 GN）",
                "Louvain（python-louvain）",
                "Louvain（NetworkX 内置）",
                "Girvan–Newman",
            ],
            index=0,
            help="推荐使用自动选择：优先 Louvain，若环境不满足则自动回退"
        )
    with colB:
        run_algo = st.button("运行所选算法", use_container_width=True)
    with colC:
        metric_ph = st.empty()
        metric_ph.metric("当前社区数", len(community_stats))

    algo_map = {
        "自动选择（优先 Louvain，失败回退 GN）": "auto",
        "Louvain（python-louvain）": "louvain_pl",
        "Louvain（NetworkX 内置）": "louvain_nx",
        "Girvan–Newman": "girvan_newman",
    }

    if run_algo:
        with st.spinner("正在执行社区检测..."):
            det, res = detect_communities(G, algo=algo_map[algo_label])
        st.session_state['community_results'] = res
        st.session_state['community_detector_map'] = det.community_map
        community_results = res
        community_detector_map = det.community_map
        community_stats = res['community_stats']
        # 立刻刷新“当前社区数”指标，避免与提示不一致
        metric_ph.metric("当前社区数", len(community_stats))
        st.success(f"算法完成：{res.get('algo_used','未知')}，检测到 {len(community_stats)} 个社区")

    # ===== 全局模糊搜索（单一搜索框：用户或社区） =====
    

    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 网络基本分析",
        "🎯 关键用户识别",
        "🔍 社区结构检测",
        "🎨 网络可视化",
        "📈 统计报告"
    ])
    
    # ==================== 标签页1: 网络基本分析 ====================
    with tab1:
        st.markdown("## 📊 网络基本结构分析")
        
        # 获取基本指标
        metrics = analysis_results['basic_metrics']
        
        # 显示关键指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("节点数", metrics['节点数'])
        with col2:
            st.metric("边数", metrics['边数'])
        with col3:
            st.metric("网络密度", f"{metrics['网络密度']:.4f}")
        with col4:
            st.metric("平均度", f"{metrics['平均度']:.2f}")
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("平均聚类系数", f"{metrics['平均聚类系数']:.4f}")
        with col6:
            st.metric("平均最短路径", f"{metrics['平均最短路径长度']:.2f}")
        with col7:
            st.metric("网络直径", metrics['网络直径'])
        with col8:
            st.metric("最大度", metrics['最大度'])
        
        # 详细指标表格
        st.markdown("### 📋 详细指标表格")
        metrics_df = pd.DataFrame({
            '指标': list(metrics.keys()),
            '数值': list(metrics.values())
        })
        st.dataframe(metrics_df, use_container_width=True)
        
        # 度分布可视化
        st.markdown("### 📊 度分布分析")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 线性坐标")
            degrees = [d for n, d in G.degree()]
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(degrees, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
            ax.set_xlabel('节点度数', fontsize=12)
            ax.set_ylabel('节点数量', fontsize=12)
            ax.set_title('度分布（线性坐标）', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### 对数坐标（验证幂律分布）")
            degree_counts = {}
            for d in degrees:
                degree_counts[d] = degree_counts.get(d, 0) + 1
            
            degrees_unique = sorted(degree_counts.keys())
            counts = [degree_counts[d] for d in degrees_unique]
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.loglog(degrees_unique, counts, 'o-', color='red', markersize=8, linewidth=2)
            ax.set_xlabel('节点度数 (log)', fontsize=12)
            ax.set_ylabel('节点数量 (log)', fontsize=12)
            ax.set_title('度分布（对数坐标）', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, which='both')
            st.pyplot(fig)
        
        # 网络特性分析说明
        st.markdown("### 💡 网络特性分析")
        with st.expander("点击查看详细分析说明"):
            st.markdown(f"""
            **网络密度**: {metrics['网络密度']:.4f}
            - 表示网络中实际存在的边数与可能的最大边数的比例
            - 值越小说明网络越稀疏，用户之间的直接连接越少
            
            **平均聚类系数**: {metrics['平均聚类系数']:.4f}
            - 衡量用户的朋友之间也是朋友的概率
            - 值越大说明网络中的社团结构越明显
            
            **平均最短路径长度**: {metrics['平均最短路径长度']:.2f}
            - 任意两个用户之间的平均距离
            - 较小的值表现出"小世界"特性
            
            **网络直径**: {metrics['网络直径']}
            - 网络中最远的两个节点之间的距离
            - 反映网络的整体规模
            """)
    
    # ==================== 标签页2: 关键用户识别 ====================
    with tab2:
        st.markdown("## 🎯 关键用户识别 - 网络中心性分析")
        
        # 获取中心性数据
        centrality_df = analysis_results['centrality']
        
        # 中心性指标说明
        st.markdown("### 📚 中心性指标说明")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **度中心性 (Degree Centrality)**
            - 衡量一个节点的直接连接数
            - 值越大说明用户的朋友越多
            - 代表"社交明星"
            """)
        with col2:
            st.markdown("""
            **介数中心性 (Betweenness Centrality)**
            - 衡量一个节点在最短路径中出现的频率
            - 值越大说明用户越是信息流通的枢纽
            - 代表"信息桥梁"
            """)
        
        # 排名前N的关键用户
        st.markdown("### 🌟 排名前N的关键用户")
        n_top = st.slider("显示前N个用户", 5, 50, 15)
        
        top_n = centrality_df.head(n_top)
        
        # 显示表格
        display_df = top_n[['用户', '度中心性', '介数中心性', '接近中心性', '综合中心性']].copy()
        display_df['排名'] = range(1, len(display_df) + 1)
        display_df = display_df[['排名', '用户', '度中心性', '介数中心性', '接近中心性', '综合中心性']]
        
        st.dataframe(display_df, use_container_width=True)
        
        # 中心性对比图
        st.markdown("### 📊 中心性指标对比")
        fig, ax = plt.subplots(figsize=(14, 6))
        
        x = np.arange(len(top_n))
        width = 0.2
        
        ax.bar(x - 1.5*width, top_n['度中心性'], width, label='度中心性', alpha=0.8)
        ax.bar(x - 0.5*width, top_n['介数中心性'], width, label='介数中心性', alpha=0.8)
        ax.bar(x + 0.5*width, top_n['接近中心性'], width, label='接近中心性', alpha=0.8)
        ax.bar(x + 1.5*width, top_n['综合中心性'], width, label='综合中心性', alpha=0.8)
        
        ax.set_xlabel('用户', fontsize=12)
        ax.set_ylabel('中心性值', fontsize=12)
        ax.set_title(f'排名前{n_top}的关键用户 - 中心性指标对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([u.replace('User_', '') for u in top_n['用户']], rotation=45, ha='right')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 用户详细信息（单一搜索框：在下拉框中直接输入进行模糊搜索）
        st.markdown("### 👤 用户详细信息")
        st.markdown("---")
        user_list = centrality_df['用户'].tolist()
        selected_user = st.selectbox(
            "输入或选择用户（支持模糊搜索，如：User_042 或 42）",
            options=user_list,
            index=0,
            placeholder="输入用户ID或关键字进行搜索",
            key="select_user"
        )
        user_data = centrality_df[centrality_df['用户'] == selected_user].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("度中心性", f"{user_data['度中心性']:.4f}")
        with col2:
            st.metric("介数中心性", f"{user_data['介数中心性']:.4f}")
        with col3:
            st.metric("接近中心性", f"{user_data['接近中心性']:.4f}")
        with col4:
            st.metric("综合排名分数", f"{user_data['综合中心性']:.4f}")
    
    # ==================== 标签页3: 社区检测 ====================
    with tab3:
        st.markdown("## 🔍 社区结构检测")
        
        # 使用顶部已计算的社区结果（缓存）
        # community_stats 已在顶部计算
        
        st.markdown("### 📊 社区统计信息")
        st.markdown("---")
        st.dataframe(community_stats[['社区ID', '节点数', '内部边数', '外部边数', '社区密度', '社区凝聚力']], 
                    use_container_width=True)
        
        # 社区统计可视化
        st.markdown("### 📈 社区统计可视化")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 各社区的节点数")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(community_stats['社区ID'], community_stats['节点数'], color='skyblue', alpha=0.8)
            ax.set_xlabel('社区', fontsize=11)
            ax.set_ylabel('节点数', fontsize=11)
            ax.set_title('各社区的节点数', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### 各社区的内部密度")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(community_stats['社区ID'], community_stats['社区密度'], color='lightcoral', alpha=0.8)
            ax.set_xlabel('社区', fontsize=11)
            ax.set_ylabel('密度', fontsize=11)
            ax.set_title('各社区的内部密度', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            st.pyplot(fig)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### 各社区的凝聚力")
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(community_stats['社区ID'], community_stats['社区凝聚力'], color='lightgreen', alpha=0.8)
            ax.set_xlabel('社区', fontsize=11)
            ax.set_ylabel('凝聚力', fontsize=11)
            ax.set_title('各社区的凝聚力', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            st.pyplot(fig)
        
        with col4:
            st.markdown("#### 内外部边数对比")
            fig, ax = plt.subplots(figsize=(8, 5))
            x = np.arange(len(community_stats))
            width = 0.35
            ax.bar(x - width/2, community_stats['内部边数'], width, label='内部边', alpha=0.8)
            ax.bar(x + width/2, community_stats['外部边数'], width, label='外部边', alpha=0.8)
            ax.set_xlabel('社区', fontsize=11)
            ax.set_ylabel('边数', fontsize=11)
            ax.set_title('各社区的内外部边数', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(community_stats['社区ID'])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            st.pyplot(fig)
        
        # 社区详细信息（单一搜索框：在下拉框中直接输入进行模糊搜索）
        st.markdown("### 📋 社区详细信息")
        st.markdown("---")
        community_list = community_stats['社区ID'].tolist()
        selected_community = st.selectbox(
            "输入或选择社区（支持模糊搜索，如：C2 或 2）",
            options=community_list,
            index=0,
            placeholder="输入社区ID或关键字进行搜索",
            key="select_community"
        )
        
        comm_data = community_stats[community_stats['社区ID'] == selected_community].iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("节点数", comm_data['节点数'])
        with col2:
            st.metric("社区密度", f"{comm_data['社区密度']:.4f}")
        with col3:
            st.metric("社区凝聚力", f"{comm_data['社区凝聚力']:.4f}")
        with col4:
            st.metric("内部边数", comm_data['内部边数'])
    
    # ==================== 标签页4: 网络可视化 ====================
    with tab4:
        st.markdown("## 🎨 网络可视化展示")
        
        # 可视化选项
        viz_type = st.radio("选择可视化类型", 
                           ["社区着色", "中心性着色"],
                           horizontal=True)
        
        layout_type = st.selectbox("选择布局方式", 
                                  ["spring", "circular", "kamada_kawai"])
        
        visualizer = NetworkVisualizer(G, community_detector_map, centrality_df)
        
        with st.spinner("正在生成可视化..."):
            if viz_type == "社区着色":
                fig, ax = visualizer.visualize_network_with_communities(
                    figsize=(14, 10),
                    layout_type=layout_type
                )
            else:
                fig, ax = visualizer.visualize_network_with_centrality(
                    figsize=(14, 10),
                    layout_type=layout_type
                )
        
        st.pyplot(fig)
        
        # 可视化说明
        if viz_type == "社区着色":
            st.markdown("""
            **说明**:
            - 不同颜色的节点代表不同的社区
            - 节点大小相同
            - 标签显示排名前15的关键用户
            """)
        else:
            st.markdown("""
            **说明**:
            - 节点大小和颜色深度表示用户的重要性（综合中心性）
            - 颜色越深、节点越大，说明用户越重要
            - 标签显示排名前20的关键用户
            """)
    
    # ==================== 标签页5: 统计报告 ====================
    with tab5:
        st.markdown("## 📈 综合统计报告")
        
        # 生成报告
        report = generate_report(G, analysis_results, community_results)
        
        st.markdown(report)
        
        # 下载报告
        st.markdown("### 📥 下载报告")
        col1, col2 = st.columns(2)
        
        with col1:
            # 下载为文本
            st.download_button(
                label="📄 下载为文本文件",
                data=report,
                file_name="社交网络分析报告.txt",
                mime="text/plain"
            )
        
        with col2:
            # 下载数据表格
            combined_data = pd.concat([
                centrality_df.rename(columns={'用户': '用户_中心性'}),
                community_stats
            ], axis=1)
            
            csv = combined_data.to_csv(index=False)
            st.download_button(
                label="📊 下载数据表格",
                data=csv,
                file_name="社交网络分析数据.csv",
                mime="text/csv"
            )


def generate_report(G, analysis_results, detection_results):
    """生成综合分析报告"""
    
    metrics = analysis_results['basic_metrics']
    centrality_df = analysis_results['centrality']
    community_stats = detection_results['community_stats']
    
    report = f"""
# 社交网络图论分析综合报告

## 1. 执行摘要

本报告对一个包含 {metrics['节点数']} 个节点和 {metrics['边数']} 条边的社交网络进行了全面的图论分析。
通过应用网络中心性分析、社区检测等图论方法，识别了网络中的关键用户和社区结构。

---

## 2. 网络基本特性

### 2.1 网络规模
- **节点数（用户数）**: {metrics['节点数']}
- **边数（关系数）**: {metrics['边数']}
- **网络密度**: {metrics['网络密度']:.4f}
- **平均度**: {metrics['平均度']:.2f}
- **最大度**: {metrics['最大度']}
- **最小度**: {metrics['最小度']}

### 2.2 网络拓扑特性
- **平均聚类系数**: {metrics['平均聚类系数']:.4f}
  - 表示网络中的社团结构强度
  - 值越大说明用户倾向于形成紧密的小圈子
  
- **平均最短路径长度**: {metrics['平均最短路径长度']:.2f}
  - 表现出"小世界"特性
  - 任意两个用户通过较少的中间人即可连接
  
- **网络直径**: {metrics['网络直径']}
  - 网络中最远的两个节点之间的距离

### 2.3 网络模型
- **生成模型**: Barabási–Albert (BA) 无标度网络
- **模型特点**:
  - 幂律度分布：少数高度数节点（hub）和大量低度数节点
  - 小世界特性：高聚类系数和小平均路径长度
  - 符合真实社交网络的特征

---

## 3. 关键用户识别

### 3.1 中心性指标分析

排名前5的关键用户：

"""
    
    top_5 = centrality_df.head(5)
    for idx, row in top_5.iterrows():
        report += f"""
**{idx+1}. {row['用户']}**
- 度中心性: {row['度中心性']:.4f}
- 介数中心性: {row['介数中心性']:.4f}
- 接近中心性: {row['接近中心性']:.4f}
- 综合排名分数: {row['综合中心性']:.4f}
"""
    
    report += f"""

### 3.2 用户角色分析

**社交明星** (度中心性最高)
- 拥有最多的直接朋友
- 在社交网络中影响力大
- 适合作为信息传播的源头

**信息桥梁** (介数中心性最高)
- 连接不同的社区
- 对网络连通性至关重要
- 适合作为跨社区的信息传递者

**网络中心** (接近中心性最高)
- 位于网络的中心位置
- 能快速到达其他用户
- 适合作为信息汇聚点

---

## 4. 社区结构检测

### 4.1 社区统计

检测到 {len(community_stats)} 个社区

"""
    
    for idx, row in community_stats.iterrows():
        report += f"""
**{row['社区ID']}**
- 节点数: {row['节点数']} ({row['节点数']/metrics['节点数']*100:.1f}%)
- 内部边数: {row['内部边数']}
- 外部边数: {row['外部边数']}
- 社区密度: {row['社区密度']:.4f}
- 社区凝聚力: {row['社区凝聚力']:.4f}
"""
    
    avg_cohesion = community_stats['社区凝聚力'].mean()
    
    report += f"""

### 4.2 社区特性分析

- **平均社区凝聚力**: {avg_cohesion:.4f}
- **社区划分质量**: {'优秀' if avg_cohesion > 0.5 else '良好' if avg_cohesion > 0.3 else '一般'}
- **社区多样性**: {'高' if community_stats['节点数'].std() > 20 else '中等' if community_stats['节点数'].std() > 10 else '低'}

社区凝聚力越高，说明社区内部连接越紧密，社区间连接越少，社区划分越清晰。

---

## 5. 结论与建议

### 5.1 网络特征总结

1. **网络结构**: 该社交网络具有典型的无标度网络特征，存在少数高度数节点和大量低度数节点。

2. **社团结构**: 网络中存在明显的社区结构，用户倾向于形成紧密的小圈子。

3. **连通性**: 网络具有小世界特性，任意两个用户之间的距离较小。

### 5.2 实际应用建议

1. **信息传播**: 优先选择度中心性高的用户作为信息源，可以快速覆盖大量用户。

2. **跨社区连接**: 利用介数中心性高的用户进行跨社区的信息传递。

3. **社区运营**: 针对不同社区的特点进行差异化的运营策略。

4. **网络优化**: 加强社区间的连接，提高网络的整体连通性。

---

## 6. 技术说明

- **数据生成**: Barabási–Albert 无标度网络模型
- **中心性分析**: 度中心性、介数中心性、接近中心性、特征向量中心性
- **社区检测**: Louvain 算法
- **可视化工具**: NetworkX, Matplotlib
- **分析框架**: Python, Streamlit

---

*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report


if __name__ == "__main__":
    main()


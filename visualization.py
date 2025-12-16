"""
可视化模块
使用 Matplotlib 进行网络可视化展示
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.colors as mcolors
import numpy as np
from typing import Dict, Tuple
import pandas as pd


class NetworkVisualizer:
    """网络可视化器"""
    
    def __init__(self, G: nx.Graph, community_map: Dict = None, centrality_df: pd.DataFrame = None):
        """
        初始化可视化器
        
        Args:
            G: 输入的网络图
            community_map: 节点到社区的映射
            centrality_df: 中心性指标 DataFrame
        """
        self.G = G
        self.community_map = community_map or {}
        self.centrality_df = centrality_df
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _get_layout(self, layout_type: str = 'spring', seed: int = 42) -> Dict:
        """
        获取节点布局
        
        Args:
            layout_type: 布局类型 ('spring', 'circular', 'kamada_kawai')
            seed: 随机种子
        
        Returns:
            节点位置字典
        """
        print(f"计算 {layout_type} 布局...")
        
        if layout_type == 'spring':
            # Spring 布局（力导向图）
            pos = nx.spring_layout(self.G, k=0.5, iterations=50, seed=seed)
        elif layout_type == 'circular':
            # 圆形布局
            pos = nx.circular_layout(self.G)
        elif layout_type == 'kamada_kawai':
            # Kamada-Kawai 布局
            pos = nx.kamada_kawai_layout(self.G)
        else:
            pos = nx.spring_layout(self.G, k=0.5, iterations=50, seed=seed)
        
        return pos

    def _get_distinct_colors(self, n: int, seed: int = 42):
        """生成 n 个尽量区分度高的颜色，数量可扩展。
        先使用多套离散调色板，不足时再用 HSV 均匀取样补足；保证可复现。
        """
        rng = np.random.default_rng(seed)
        palette = []
        # 汇总多套离散调色板（优先高可读性）
        base_maps = [
            'tab20', 'tab20b', 'tab20c', 'tab10',
            'Set3', 'Set2', 'Set1', 'Accent', 'Dark2',
            'Pastel1', 'Pastel2'
        ]
        for name in base_maps:
            cmap = plt.get_cmap(name)
            if hasattr(cmap, 'colors') and cmap.colors is not None:
                palette.extend(list(cmap.colors))
            else:
                # 若不是 ListedColormap，均匀采样 20 个颜色
                palette.extend([cmap(i/20) for i in range(20)])
        # 去重（按 RGB 取 3 位小数）
        unique = []
        seen = set()
        for c in palette:
            key = tuple(round(x, 3) for x in c[:3])
            if key not in seen:
                seen.add(key)
                # 统一为 RGBA
                if len(c) == 3:
                    unique.append((*c, 1.0))
                else:
                    unique.append(c)
        palette = unique
        # 若仍不足，使用 HSV 等距补足
        if len(palette) < n:
            m = n - len(palette)
            for i in range(m):
                h = (i / max(1, m))
                s = 0.65
                v = 0.95
                rgb = mcolors.hsv_to_rgb([h, s, v])
                palette.append((*rgb, 1.0))
        # 为避免相邻颜色过近，随机打散但可复现
        idx = rng.permutation(len(palette))[:n]
        return [palette[i] for i in idx]
    
    def visualize_network_with_communities(self, figsize: Tuple = (16, 12), 
                                          layout_type: str = 'spring',
                                          save_path: str = None):
        """
        可视化网络，用颜色区分社区
        
        Args:
            figsize: 图形大小
            layout_type: 布局类型
            save_path: 保存路径（可选）
        """
        print("\n" + "="*60)
        print("🎨 生成网络可视化图 - 社区着色")
        print("="*60)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 获取布局
        pos = self._get_layout(layout_type)
        
        # 为不同社区分配颜色
        communities = {}
        for node, comm_id in self.community_map.items():
            communities.setdefault(comm_id, []).append(node)
        comm_ids = sorted(communities.keys())
        palette = self._get_distinct_colors(len(comm_ids), seed=42)
        
        legend_handles = []
        for color, comm_id in zip(palette, comm_ids):
            nodes = communities[comm_id]
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=nodes,
                node_color=[color],
                node_size=300,
                ax=ax,
                alpha=0.85
            )
            legend_handles.append(mpatches.Patch(color=color, label=f"社区 {comm_id}"))
        
        # 绘制边
        nx.draw_networkx_edges(
            self.G, pos,
            width=0.5,
            alpha=0.25,
            edge_color="#888888",
            ax=ax
        )
        
        # 绘制节点标签（仅显示关键节点）
        if self.centrality_df is not None:
            top_nodes = self.centrality_df.head(15)['用户'].tolist()
            labels = {node: node.replace('User_', '') for node in top_nodes}
            nx.draw_networkx_labels(
                self.G, pos,
                labels=labels,
                font_size=8,
                font_color='black',
                ax=ax
            )
        
        ax.set_title('社交网络可视化 - 社区结构\n(节点颜色表示不同社区)', 
                    fontsize=16, fontweight='bold', pad=20)
        if legend_handles:
            ncol = min(4, max(1, len(legend_handles)//8 + 1))
            ax.legend(handles=legend_handles, loc='upper left', fontsize=9, ncol=ncol, frameon=False)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图形已保存到: {save_path}")
        
        return fig, ax
    
    def visualize_network_with_centrality(self, figsize: Tuple = (16, 12),
                                         layout_type: str = 'spring',
                                         save_path: str = None):
        """
        可视化网络，节点大小反映中心性
        
        Args:
            figsize: 图形大小
            layout_type: 布局类型
            save_path: 保存路径（可选）
        """
        print("\n" + "="*60)
        print("🎨 生成网络可视化图 - 中心性着色")
        print("="*60)
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 获取布局
        pos = self._get_layout(layout_type)
        
        # 获取中心性值
        if self.centrality_df is not None:
            centrality_dict = dict(zip(self.centrality_df['用户'], 
                                      self.centrality_df['综合中心性']))
        else:
            centrality_dict = dict(nx.degree_centrality(self.G))
        
        # 节点大小基于中心性
        node_sizes = [max(100, centrality_dict.get(node, 0) * 3000) 
                     for node in self.G.nodes()]
        
        # 节点颜色基于中心性
        node_colors = [centrality_dict.get(node, 0) for node in self.G.nodes()]
        
        # 绘制节点
        nodes = nx.draw_networkx_nodes(
            self.G, pos,
            node_size=node_sizes,
            node_color=node_colors,
            cmap='YlOrRd',
            alpha=0.8,
            ax=ax
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.G, pos,
            width=0.5,
            alpha=0.2,
            ax=ax
        )
        
        # 绘制关键节点标签
        if self.centrality_df is not None:
            top_nodes = self.centrality_df.head(20)['用户'].tolist()
            labels = {node: node.replace('User_', '') for node in top_nodes}
            nx.draw_networkx_labels(
                self.G, pos,
                labels=labels,
                font_size=7,
                font_color='black',
                ax=ax
            )
        
        ax.set_title('社交网络可视化 - 中心性分析\n(节点大小和颜色表示用户重要性)', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # 添加颜色条
        cbar = plt.colorbar(nodes, ax=ax, label='综合中心性')
        
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图形已保存到: {save_path}")
        
        return fig, ax
    
    def visualize_degree_distribution(self, figsize: Tuple = (12, 5),
                                     save_path: str = None):
        """
        可视化度分布（对数-对数图）
        
        Args:
            figsize: 图形大小
            save_path: 保存路径（可选）
        """
        print("\n" + "="*60)
        print("📊 生成度分布图")
        print("="*60)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 获取度分布
        degrees = [d for n, d in self.G.degree()]
        
        # 线性图
        ax1.hist(degrees, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_xlabel('节点度数', fontsize=12)
        ax1.set_ylabel('节点数量', fontsize=12)
        ax1.set_title('度分布（线性坐标）', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 对数-对数图（验证幂律分布）
        degree_counts = {}
        for d in degrees:
            degree_counts[d] = degree_counts.get(d, 0) + 1
        
        degrees_unique = sorted(degree_counts.keys())
        counts = [degree_counts[d] for d in degrees_unique]
        
        ax2.loglog(degrees_unique, counts, 'o-', color='red', markersize=8, linewidth=2)
        ax2.set_xlabel('节点度数 (log)', fontsize=12)
        ax2.set_ylabel('节点数量 (log)', fontsize=12)
        ax2.set_title('度分布（对数坐标）- 验证幂律分布', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图形已保存到: {save_path}")
        
        return fig, (ax1, ax2)
    
    def visualize_centrality_comparison(self, figsize: Tuple = (14, 6),
                                       save_path: str = None):
        """
        可视化中心性指标对比
        
        Args:
            figsize: 图形大小
            save_path: 保存路径（可选）
        """
        print("\n" + "="*60)
        print("📊 生成中心性指标对比图")
        print("="*60)
        
        if self.centrality_df is None:
            print("⚠️  没有中心性数据，跳过此可视化")
            return None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 获取前15个关键用户
        top_15 = self.centrality_df.head(15)
        
        x = np.arange(len(top_15))
        width = 0.2
        
        # 绘制柱状图
        ax.bar(x - 1.5*width, top_15['度中心性'], width, label='度中心性', alpha=0.8)
        ax.bar(x - 0.5*width, top_15['介数中心性'], width, label='介数中心性', alpha=0.8)
        ax.bar(x + 0.5*width, top_15['接近中心性'], width, label='接近中心性', alpha=0.8)
        ax.bar(x + 1.5*width, top_15['综合中心性'], width, label='综合中心性', alpha=0.8)
        
        ax.set_xlabel('用户', fontsize=12)
        ax.set_ylabel('中心性值', fontsize=12)
        ax.set_title('排名前15的关键用户 - 中心性指标对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([u.replace('User_', '') for u in top_15['用户']], 
                           rotation=45, ha='right')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图形已保存到: {save_path}")
        
        return fig, ax
    
    def visualize_community_statistics(self, community_stats: pd.DataFrame,
                                      figsize: Tuple = (14, 6),
                                      save_path: str = None):
        """
        可视化社区统计信息
        
        Args:
            community_stats: 社区统计 DataFrame
            figsize: 图形大小
            save_path: 保存路径（可选）
        """
        print("\n" + "="*60)
        print("📊 生成社区统计图")
        print("="*60)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. 社区大小
        ax1.bar(community_stats['社区ID'], community_stats['节点数'], color='skyblue', alpha=0.8)
        ax1.set_xlabel('社区', fontsize=11)
        ax1.set_ylabel('节点数', fontsize=11)
        ax1.set_title('各社区的节点数', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. 社区密度
        ax2.bar(community_stats['社区ID'], community_stats['社区密度'], color='lightcoral', alpha=0.8)
        ax2.set_xlabel('社区', fontsize=11)
        ax2.set_ylabel('密度', fontsize=11)
        ax2.set_title('各社区的内部密度', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. 社区凝聚力
        ax3.bar(community_stats['社区ID'], community_stats['社区凝聚力'], color='lightgreen', alpha=0.8)
        ax3.set_xlabel('社区', fontsize=11)
        ax3.set_ylabel('凝聚力', fontsize=11)
        ax3.set_title('各社区的凝聚力', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 内外部边数对比
        x = np.arange(len(community_stats))
        width = 0.35
        ax4.bar(x - width/2, community_stats['内部边数'], width, label='内部边', alpha=0.8)
        ax4.bar(x + width/2, community_stats['外部边数'], width, label='外部边', alpha=0.8)
        ax4.set_xlabel('社区', fontsize=11)
        ax4.set_ylabel('边数', fontsize=11)
        ax4.set_title('各社区的内外部边数', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(community_stats['社区ID'])
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 图形已保存到: {save_path}")
        
        return fig, ((ax1, ax2), (ax3, ax4))
    
    def generate_all_visualizations(self, community_stats: pd.DataFrame = None,
                                   output_dir: str = './results'):
        """
        生成所有可视化图形
        
        Args:
            community_stats: 社区统计 DataFrame
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*60)
        print("🎨 生成所有可视化图形")
        print("="*60)
        
        # 1. 社区着色的网络图
        self.visualize_network_with_communities(
            save_path=f'{output_dir}/01_network_communities.png'
        )
        
        # 2. 中心性着色的网络图
        self.visualize_network_with_centrality(
            save_path=f'{output_dir}/02_network_centrality.png'
        )
        
        # 3. 度分布图
        self.visualize_degree_distribution(
            save_path=f'{output_dir}/03_degree_distribution.png'
        )
        
        # 4. 中心性对比图
        self.visualize_centrality_comparison(
            save_path=f'{output_dir}/04_centrality_comparison.png'
        )
        
        # 5. 社区统计图
        if community_stats is not None:
            self.visualize_community_statistics(
                community_stats,
                save_path=f'{output_dir}/05_community_statistics.png'
            )
        
        print(f"\n✓ 所有可视化图形已保存到 {output_dir}")


def main():
    """测试可视化模块"""
    from data_generator import SocialNetworkGenerator
    from network_analysis import NetworkAnalyzer
    from community_detection import CommunityDetector
    
    # 生成网络
    generator = SocialNetworkGenerator(seed=42)
    G = generator.generate_complete_network(n_nodes=300, m=3)
    
    # 分析网络
    analyzer = NetworkAnalyzer(G)
    analyzer.run_all_analysis()
    centrality_df = analyzer.analysis_results['centrality']
    
    # 检测社区
    detector = CommunityDetector(G)
    detector.run_all_detection()
    community_stats = detector.analysis_results['community_stats']
    
    # 可视化
    visualizer = NetworkVisualizer(G, detector.community_map, centrality_df)
    visualizer.generate_all_visualizations(community_stats)
    
    print("\n" + "="*60)
    print("可视化模块测试完成")
    print("="*60)


if __name__ == "__main__":
    main()


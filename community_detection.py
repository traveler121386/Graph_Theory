"""
社区检测模块
使用 Louvain 算法进行社区检测和分析
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np

try:
    from networkx.algorithms import community
    import networkx.algorithms.community as nx_community
except ImportError:
    pass


class CommunityDetector:
    """社区检测器"""
    
    def __init__(self, G: nx.Graph):
        """
        初始化社区检测器
        
        Args:
            G: 输入的网络图
        """
        self.G = G
        self.communities = None
        self.community_map = {}
        self.analysis_results = {}
    
    def detect_communities_louvain(self) -> Dict[int, set]:
        """
        使用 Louvain 算法进行社区检测
        
        Louvain 算法说明：
        - 是一种贪心优化算法，通过最大化模块度来检测社区
        - 优点：速度快、精度高、可扩展性好
        - 适用于大规模网络
        
        Returns:
            社区字典 {社区ID: 节点集合}
        """
        print("\n" + "="*60)
        print("🔍 社区结构检测 - Louvain 算法")
        print("="*60)
        
        print("\n正在执行 Louvain 算法...")
        
        try:
            # 尝试使用 python-louvain 库
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(self.G)
                
                # 转换为社区集合格式
                communities = {}
                for node, comm_id in partition.items():
                    if comm_id not in communities:
                        communities[comm_id] = set()
                    communities[comm_id].add(node)
                
            except ImportError:
                # 如果没有 python-louvain，使用 NetworkX 的 Louvain 实现
                print("使用 NetworkX 内置的 Louvain 算法...")
                communities_generator = nx_community.louvain_communities(self.G, seed=42)
                communities = {i: comm for i, comm in enumerate(communities_generator)}
        
        except Exception as e:
            print(f"Louvain 算法执行失败: {e}")
            print("使用 Girvan-Newman 算法作为备选...")
            communities = self.detect_communities_girvan_newman()
        
        self.communities = communities
        self._build_community_map()
        
        print(f"\n✓ 社区检测完成")
        print(f"  - 检测到的社区数: {len(communities)}")
        
        return communities
    
    def detect_communities_girvan_newman(self) -> Dict[int, set]:
        """
        使用 Girvan-Newman 算法进行社区检测（备选方案）
        
        Girvan-Newman 算法说明：
        - 基于边的介数中心性，迭代删除介数最高的边
        - 优点：理论基础扎实，结果可解释性强
        - 缺点：计算复杂度较高，不适合大规模网络
        
        Returns:
            社区字典 {社区ID: 节点集合}
        """
        print("\n正在执行 Girvan-Newman 算法...")
        
        # 获取最优的社区划分
        communities_generator = nx_community.girvan_newman(self.G)
        
        # 计算模块度，找到最优的社区数
        best_modularity = -1
        best_communities = None
        
        for communities in communities_generator:
            modularity = nx_community.modularity(self.G, communities)
            if modularity > best_modularity:
                best_modularity = modularity
                best_communities = communities
        
        # 转换为字典格式
        communities_dict = {i: comm for i, comm in enumerate(best_communities)}
        
        self.communities = communities_dict
        self._build_community_map()
        
        print(f"✓ Girvan-Newman 算法完成")
        print(f"  - 检测到的社区数: {len(communities_dict)}")
        print(f"  - 模块度: {best_modularity:.4f}")
        
        return communities_dict
    
    def _build_community_map(self):
        """构建节点到社区的映射"""
        self.community_map = {}
        for comm_id, nodes in self.communities.items():
            for node in nodes:
                self.community_map[node] = comm_id
    
    def analyze_community_structure(self) -> pd.DataFrame:
        """
        分析社区结构特征
        
        Returns:
            社区统计信息 DataFrame
        """
        print("\n" + "-"*60)
        print("📊 社区结构特征分析")
        print("-"*60)
        
        community_stats = []
        
        for comm_id, nodes in self.communities.items():
            # 创建社区子图
            subgraph = self.G.subgraph(nodes).copy()
            
            # 计算社区内部指标
            n_nodes = len(nodes)
            n_edges = subgraph.number_of_edges()
            
            # 内部边数和外部边数
            internal_edges = n_edges
            external_edges = 0
            for node in nodes:
                for neighbor in self.G.neighbors(node):
                    if neighbor not in nodes:
                        external_edges += 1
            
            # 社区密度
            if n_nodes > 1:
                max_edges = n_nodes * (n_nodes - 1) / 2
                density = internal_edges / max_edges if max_edges > 0 else 0
            else:
                density = 0
            
            # 平均聚类系数
            if n_nodes > 1:
                avg_clustering = nx.average_clustering(subgraph)
            else:
                avg_clustering = 0
            
            # 社区凝聚力 = 内部边数 / (内部边数 + 外部边数)
            cohesion = internal_edges / (internal_edges + external_edges) if (internal_edges + external_edges) > 0 else 0
            
            community_stats.append({
                '社区ID': f'C{comm_id}',
                '节点数': n_nodes,
                '内部边数': internal_edges,
                '外部边数': external_edges,
                '社区密度': density,
                '平均聚类系数': avg_clustering,
                '社区凝聚力': cohesion,
                '代表节点': list(nodes)[:3]  # 前3个节点作为代表
            })
        
        stats_df = pd.DataFrame(community_stats)
        stats_df = stats_df.sort_values('节点数', ascending=False)
        
        self.analysis_results['community_stats'] = stats_df
        
        # 打印社区统计
        print("\n社区统计信息:")
        print("-"*60)
        for idx, row in stats_df.iterrows():
            print(f"\n{row['社区ID']}:")
            print(f"  节点数: {row['节点数']}")
            print(f"  内部边数: {row['内部边数']}")
            print(f"  外部边数: {row['外部边数']}")
            print(f"  社区密度: {row['社区密度']:.4f}")
            print(f"  平均聚类系数: {row['平均聚类系数']:.4f}")
            print(f"  社区凝聚力: {row['社区凝聚力']:.4f}")
        
        return stats_df
    
    def analyze_community_meaning(self, stats_df: pd.DataFrame) -> str:
        """
        分析社区的含义和特征
        
        Args:
            stats_df: 社区统计 DataFrame
        
        Returns:
            分析说明文本
        """
        print("\n" + "-"*60)
        print("💡 社区划分结果及其意义")
        print("-"*60)
        
        analysis = []
        
        analysis.append(f"\n【社区数量】")
        analysis.append(f"检测到 {len(self.communities)} 个社区")
        analysis.append(f"这表明社交网络中存在明显的社团结构")
        
        # 分析最大社区
        largest_comm = stats_df.iloc[0]
        analysis.append(f"\n【最大社区】")
        analysis.append(f"社区: {largest_comm['社区ID']}")
        analysis.append(f"节点数: {largest_comm['节点数']} ({largest_comm['节点数']/self.G.number_of_nodes()*100:.1f}%)")
        analysis.append(f"社区密度: {largest_comm['社区密度']:.4f}")
        analysis.append(f"含义: 这是网络中最大的用户群体，可能代表一个主要的兴趣圈子或社交群体")
        
        # 分析社区凝聚力
        avg_cohesion = stats_df['社区凝聚力'].mean()
        analysis.append(f"\n【社区凝聚力】")
        analysis.append(f"平均社区凝聚力: {avg_cohesion:.4f}")
        if avg_cohesion > 0.5:
            analysis.append(f"说明: 社区内部连接紧密，社区间连接较少")
            analysis.append(f"      这是良好的社区划分，表明用户确实聚集在不同的群体中")
        else:
            analysis.append(f"说明: 社区间存在较多连接，可能存在跨社区的关键用户")
        
        # 分析社区多样性
        size_std = stats_df['节点数'].std()
        analysis.append(f"\n【社区多样性】")
        analysis.append(f"社区大小标准差: {size_std:.2f}")
        if size_std > 20:
            analysis.append(f"说明: 社区大小差异较大，网络中既有大型社团也有小型社团")
        else:
            analysis.append(f"说明: 社区大小相对均匀")
        
        # 分析社区间的连接
        analysis.append(f"\n【社区间连接】")
        total_external = stats_df['外部边数'].sum()
        total_internal = stats_df['内部边数'].sum()
        external_ratio = total_external / (total_internal + total_external) if (total_internal + total_external) > 0 else 0
        analysis.append(f"内部边数占比: {(1-external_ratio)*100:.1f}%")
        analysis.append(f"外部边数占比: {external_ratio*100:.1f}%")
        analysis.append(f"说明: 外部边数占比越低，社区划分越清晰")
        
        result_text = "\n".join(analysis)
        print(result_text)
        
        return result_text
    
    def get_community_for_node(self, node: str) -> int:
        """
        获取节点所属的社区
        
        Args:
            node: 节点名称
        
        Returns:
            社区ID
        """
        return self.community_map.get(node, -1)
    
    def run_all_detection(self) -> Dict:
        """
        运行所有社区检测分析
        
        Returns:
            包含所有分析结果的字典
        """
        # 检测社区
        self.detect_communities_louvain()
        
        # 分析社区结构
        stats_df = self.analyze_community_structure()
        self.analyze_community_meaning(stats_df)
        
        return self.analysis_results


def main():
    """测试社区检测模块"""
    from data_generator import SocialNetworkGenerator
    
    # 生成网络
    generator = SocialNetworkGenerator(seed=42)
    G = generator.generate_complete_network(n_nodes=300, m=3)
    
    # 检测社区
    detector = CommunityDetector(G)
    results = detector.run_all_detection()
    
    print("\n" + "="*60)
    print("社区检测模块测试完成")
    print("="*60)


if __name__ == "__main__":
    main()


"""
网络分析模块
计算网络的基本结构特性和中心性指标
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np


class NetworkAnalyzer:
    """网络分析器"""
    
    def __init__(self, G: nx.Graph):
        """
        初始化分析器
        
        Args:
            G: 输入的网络图
        """
        self.G = G
        self.analysis_results = {}
    
    def calculate_basic_metrics(self) -> Dict:
        """
        计算网络的基本指标
        
        Returns:
            包含基本指标的字典
        """
        print("\n" + "="*60)
        print("📊 网络基本结构分析")
        print("="*60)
        
        metrics = {}
        
        # 1. 节点数和边数
        metrics['节点数'] = self.G.number_of_nodes()
        metrics['边数'] = self.G.number_of_edges()
        
        # 2. 网络密度
        metrics['网络密度'] = nx.density(self.G)
        
        # 3. 平均度
        degrees = [d for n, d in self.G.degree()]
        metrics['平均度'] = np.mean(degrees)
        metrics['最大度'] = max(degrees)
        metrics['最小度'] = min(degrees)
        
        # 4. 聚类系数
        metrics['平均聚类系数'] = nx.average_clustering(self.G)
        
        # 5. 平均最短路径长度（仅对连通图）
        if nx.is_connected(self.G):
            metrics['平均最短路径长度'] = nx.average_shortest_path_length(self.G)
            metrics['网络直径'] = nx.diameter(self.G)
        else:
            # 对于非连通图，计算最大连通分量的指标
            largest_cc = max(nx.connected_components(self.G), key=len)
            G_largest = self.G.subgraph(largest_cc).copy()
            metrics['平均最短路径长度'] = nx.average_shortest_path_length(G_largest)
            metrics['网络直径'] = nx.diameter(G_largest)
            metrics['连通分量数'] = nx.number_connected_components(self.G)
        
        # 6. 度分布统计
        metrics['度分布_均值'] = np.mean(degrees)
        metrics['度分布_中位数'] = np.median(degrees)
        metrics['度分布_标准差'] = np.std(degrees)
        
        # 打印结果
        print(f"\n基本指标:")
        print(f"  节点数: {metrics['节点数']}")
        print(f"  边数: {metrics['边数']}")
        print(f"  网络密度: {metrics['网络密度']:.4f}")
        print(f"  平均度: {metrics['平均度']:.2f}")
        print(f"  最大度: {metrics['最大度']}")
        print(f"  最小度: {metrics['最小度']}")
        print(f"  平均聚类系数: {metrics['平均聚类系数']:.4f}")
        print(f"  平均最短路径长度: {metrics['平均最短路径长度']:.2f}")
        print(f"  网络直径: {metrics['网络直径']}")
        
        self.analysis_results['basic_metrics'] = metrics
        return metrics
    
    def analyze_network_characteristics(self, metrics: Dict) -> str:
        """
        分析网络特性的含义
        
        Args:
            metrics: 基本指标字典
        
        Returns:
            分析说明文本
        """
        print("\n" + "-"*60)
        print("📈 网络特性分析说明")
        print("-"*60)
        
        analysis = []
        
        # 密度分析
        density = metrics['网络密度']
        if density < 0.01:
            analysis.append(f"• 网络密度({density:.4f})较低，说明网络是稀疏的，大多数用户之间没有直接连接")
        else:
            analysis.append(f"• 网络密度({density:.4f})，说明网络连接程度中等")
        
        # 聚类系数分析
        clustering = metrics['平均聚类系数']
        analysis.append(f"• 平均聚类系数({clustering:.4f})表示用户的朋友圈中，朋友之间也有连接的概率")
        if clustering > 0.3:
            analysis.append("  这表明网络中存在明显的社团结构，用户倾向于形成紧密的小圈子")
        
        # 平均路径长度分析
        avg_path = metrics['平均最短路径长度']
        analysis.append(f"• 平均最短路径长度({avg_path:.2f})表示任意两个用户之间的距离")
        if avg_path < 10:
            analysis.append("  这体现了'小世界'特性，即使网络很大，任意两个用户也能通过较少的中间人连接")
        
        # 度分布分析
        analysis.append(f"• 度分布的标准差({metrics['度分布_标准差']:.2f})较大，说明网络中存在度数差异")
        analysis.append("  这是无标度网络的典型特征：少数hub节点连接众多用户，大多数节点度数较低")
        
        result_text = "\n".join(analysis)
        print(result_text)
        
        return result_text
    
    def calculate_centrality_measures(self) -> pd.DataFrame:
        """
        计算各种中心性指标
        
        Returns:
            包含中心性指标的 DataFrame
        """
        print("\n" + "="*60)
        print("🎯 关键用户识别 - 网络中心性分析")
        print("="*60)
        
        # 1. 度中心性
        print("\n计算度中心性...")
        degree_centrality = nx.degree_centrality(self.G)
        
        # 2. 介数中心性
        print("计算介数中心性...")
        betweenness_centrality = nx.betweenness_centrality(self.G)
        
        # 3. 接近中心性
        print("计算接近中心性...")
        closeness_centrality = nx.closeness_centrality(self.G)
        
        # 4. 特征向量中心性
        print("计算特征向量中心性...")
        try:
            eigenvector_centrality = nx.eigenvector_centrality(self.G, max_iter=1000)
        except:
            eigenvector_centrality = {node: 0 for node in self.G.nodes()}
        
        # 构建 DataFrame
        centrality_df = pd.DataFrame({
            '用户': list(self.G.nodes()),
            '度中心性': [degree_centrality[node] for node in self.G.nodes()],
            '介数中心性': [betweenness_centrality[node] for node in self.G.nodes()],
            '接近中心性': [closeness_centrality[node] for node in self.G.nodes()],
            '特征向量中心性': [eigenvector_centrality[node] for node in self.G.nodes()],
        })
        
        # 计算综合中心性排名
        centrality_df['综合中心性'] = (
            centrality_df['度中心性'] / centrality_df['度中心性'].max() * 0.3 +
            centrality_df['介数中心性'] / centrality_df['介数中心性'].max() * 0.3 +
            centrality_df['接近中心性'] / centrality_df['接近中心性'].max() * 0.2 +
            centrality_df['特征向量中心性'] / centrality_df['特征向量中心性'].max() * 0.2
        )
        
        # 排序
        centrality_df = centrality_df.sort_values('综合中心性', ascending=False)
        
        self.analysis_results['centrality'] = centrality_df
        
        # 打印前10个关键用户
        print("\n🌟 排名前10的关键用户:")
        print("-"*60)
        top_10 = centrality_df.head(10)
        for idx, row in top_10.iterrows():
            print(f"\n{idx+1}. {row['用户']}")
            print(f"   度中心性: {row['度中心性']:.4f} (连接数最多)")
            print(f"   介数中心性: {row['介数中心性']:.4f} (信息流通枢纽)")
            print(f"   接近中心性: {row['接近中心性']:.4f} (距离其他用户最近)")
            print(f"   综合排名分数: {row['综合中心性']:.4f}")
        
        return centrality_df
    
    def analyze_key_users(self, centrality_df: pd.DataFrame) -> str:
        """
        分析关键用户的特征和作用
        
        Args:
            centrality_df: 中心性指标 DataFrame
        
        Returns:
            分析说明文本
        """
        print("\n" + "-"*60)
        print("👥 关键用户特征分析")
        print("-"*60)
        
        analysis = []
        
        # 分析度中心性最高的用户
        top_degree = centrality_df.iloc[0]
        analysis.append(f"\n【度中心性最高的用户】")
        analysis.append(f"用户: {top_degree['用户']}")
        analysis.append(f"直接连接数: {int(top_degree['度中心性'] * self.G.number_of_nodes())}")
        analysis.append(f"作用: 这类用户是'社交明星'，拥有最多的直接朋友")
        
        # 分析介数中心性最高的用户
        top_between = centrality_df.nlargest(1, '介数中心性').iloc[0]
        analysis.append(f"\n【介数中心性最高的用户】")
        analysis.append(f"用户: {top_between['用户']}")
        analysis.append(f"介数中心性: {top_between['介数中心性']:.4f}")
        analysis.append(f"作用: 这类用户是'信息桥梁'，在网络中连接不同的社区")
        analysis.append(f"      他们对信息传播和网络连通性至关重要")
        
        # 分析接近中心性最高的用户
        top_close = centrality_df.nlargest(1, '接近中心性').iloc[0]
        analysis.append(f"\n【接近中心性最高的用户】")
        analysis.append(f"用户: {top_close['用户']}")
        analysis.append(f"接近中心性: {top_close['接近中心性']:.4f}")
        analysis.append(f"作用: 这类用户位于网络的'中心位置'，能快速到达其他用户")
        
        result_text = "\n".join(analysis)
        print(result_text)
        
        return result_text
    
    def get_degree_distribution(self) -> Dict:
        """
        获取度分布信息
        
        Returns:
            度分布字典
        """
        degrees = [d for n, d in self.G.degree()]
        degree_counts = {}
        for d in degrees:
            degree_counts[d] = degree_counts.get(d, 0) + 1
        
        return degree_counts
    
    def run_all_analysis(self) -> Dict:
        """
        运行所有分析
        
        Returns:
            包含所有分析结果的字典
        """
        # 基本指标
        metrics = self.calculate_basic_metrics()
        self.analyze_network_characteristics(metrics)
        
        # 中心性分析
        centrality_df = self.calculate_centrality_measures()
        self.analyze_key_users(centrality_df)
        
        return self.analysis_results


def main():
    """测试网络分析模块"""
    from data_generator import SocialNetworkGenerator
    
    # 生成网络
    generator = SocialNetworkGenerator(seed=42)
    G = generator.generate_complete_network(n_nodes=300, m=3)
    
    # 分析网络
    analyzer = NetworkAnalyzer(G)
    results = analyzer.run_all_analysis()
    
    print("\n" + "="*60)
    print("网络分析模块测试完成")
    print("="*60)


if __name__ == "__main__":
    main()


"""
数据生成模块
使用 Barabási–Albert (BA) 无标度网络模型生成社交网络数据
"""

import networkx as nx
import random
from typing import Tuple


class SocialNetworkGenerator:
    """社交网络数据生成器"""
    
    def __init__(self, seed: int = 42):
        """
        初始化生成器
        
        Args:
            seed: 随机种子，保证可复现性
        """
        self.seed = seed
        random.seed(seed)
        # 设置 numpy 随机种子以增强可复现性
        try:
            import numpy as np
            np.random.seed(seed)
        except Exception:
            pass
    
    def generate_ba_network(self, n_nodes: int = 300, m: int = 3) -> nx.Graph:
        """
        使用 Barabási–Albert 模型生成无标度网络
        
        Args:
            n_nodes: 节点数量（用户数）
            m: 每个新节点连接的现有节点数
        
        Returns:
            生成的无向图
        
        说明：
            BA 模型的优点：
            1. 生成的网络具有幂律度分布，符合真实社交网络特征
            2. 存在少数高度数节点（hub），大多数低度数节点
            3. 具有小世界特性（小平均路径长度、高聚类系数）
            4. 符合"富人更富"的优先连接机制
        """
        print(f"正在生成 BA 无标度网络...")
        print(f"  - 节点数: {n_nodes}")
        print(f"  - 每个新节点的连接数: {m}")
        
        # 生成 BA 网络
        G = nx.barabasi_albert_graph(n_nodes, m, seed=self.seed)
        
        # 为节点添加用户ID标签
        node_mapping = {i: f"User_{i:03d}" for i in G.nodes()}
        G = nx.relabel_nodes(G, node_mapping)
        
        print(f"✓ 网络生成完成")
        print(f"  - 实际节点数: {G.number_of_nodes()}")
        print(f"  - 实际边数: {G.number_of_edges()}")
        
        return G
    
    def add_node_attributes(self, G: nx.Graph) -> nx.Graph:
        """
        为节点添加属性信息
        
        Args:
            G: 输入图
        
        Returns:
            添加属性后的图
        """
        # 为每个节点添加用户属性
        for node in G.nodes():
            G.nodes[node]['user_id'] = node
            G.nodes[node]['join_time'] = random.randint(2015, 2024)
            G.nodes[node]['activity_level'] = random.choice(['高', '中', '低'])
        
        return G
    
    def add_edge_attributes(self, G: nx.Graph) -> nx.Graph:
        """
        为边添加属性信息
        
        Args:
            G: 输入图
        
        Returns:
            添加属性后的图
        """
        # 为每条边添加关系属性
        for u, v in G.edges():
            G[u][v]['relationship_type'] = random.choice(['朋友', '关注', '互动'])
            G[u][v]['interaction_count'] = random.randint(1, 100)
        
        return G
    
    def generate_complete_network(self, n_nodes: int = 300, m: int = 3) -> nx.Graph:
        """
        生成完整的社交网络（包含节点和边的属性）
        
        Args:
            n_nodes: 节点数量
            m: BA 模型参数
        
        Returns:
            完整的社交网络图
        """
        # 生成基础网络
        G = self.generate_ba_network(n_nodes, m)
        
        # 添加节点属性
        G = self.add_node_attributes(G)
        
        # 添加边属性
        G = self.add_edge_attributes(G)
        
        return G


def main():
    """测试数据生成模块"""
    generator = SocialNetworkGenerator(seed=42)
    G = generator.generate_complete_network(n_nodes=300, m=3)
    
    print("\n" + "="*50)
    print("数据生成模块测试完成")
    print("="*50)
    print(f"节点数: {G.number_of_nodes()}")
    print(f"边数: {G.number_of_edges()}")
    print(f"样本节点属性: {dict(G.nodes['User_000'])}")
    print(f"样本边属性: {dict(G['User_000']['User_001'])}")


if __name__ == "__main__":
    main()


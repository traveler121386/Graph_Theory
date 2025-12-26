# 附录：核心代码清单

> 说明：以下仅列出项目中直接实现主要算法与数据处理逻辑的核心类 / 函数。实验驱动脚本、可视化以及测试文件未列入，避免冗余。

---

## A. SocialNetworkGenerator  （data_generator.py）
```python
class SocialNetworkGenerator:
    """社交网络数据生成器"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        try:
            import numpy as np
            np.random.seed(seed)
        except Exception:
            pass

    def generate_ba_network(self, n_nodes: int = 300, m: int = 3) -> nx.Graph:
        """使用 Barabási–Albert 模型生成无标度网络"""
        G = nx.barabasi_albert_graph(n_nodes, m, seed=self.seed)
        node_mapping = {i: f"User_{i:03d}" for i in G.nodes()}
        return nx.relabel_nodes(G, node_mapping)

    def add_node_attributes(self, G: nx.Graph) -> nx.Graph:
        for node in G.nodes():
            G.nodes[node]['user_id'] = node
            G.nodes[node]['join_time'] = random.randint(2015, 2024)
            G.nodes[node]['activity_level'] = random.choice(['高', '中', '低'])
        return G

    def add_edge_attributes(self, G: nx.Graph) -> nx.Graph:
        for u, v in G.edges():
            G[u][v]['relationship_type'] = random.choice(['朋友', '关注', '互动'])
            G[u][v]['interaction_count'] = random.randint(1, 100)
        return G

    def generate_complete_network(self, n_nodes: int = 300, m: int = 3) -> nx.Graph:
        G = self.generate_ba_network(n_nodes, m)
        self.add_node_attributes(G)
        self.add_edge_attributes(G)
        return G
```

---

## B. NetworkAnalyzer  （network_analysis.py）
```python
class NetworkAnalyzer:
    def calculate_basic_metrics(self) -> Dict:
        metrics = {
            '节点数': self.G.number_of_nodes(),
            '边数': self.G.number_of_edges(),
            '网络密度': nx.density(self.G),
        }
        degrees = [d for _, d in self.G.degree()]
        metrics.update({
            '平均度': np.mean(degrees),
            '最大度': max(degrees),
            '最小度': min(degrees),
            '平均聚类系数': nx.average_clustering(self.G),
        })
        if nx.is_connected(self.G):
            metrics['平均最短路径长度'] = nx.average_shortest_path_length(self.G)
            metrics['网络直径'] = nx.diameter(self.G)
        else:
            largest_cc = max(nx.connected_components(self.G), key=len)
            sub = self.G.subgraph(largest_cc)
            metrics['平均最短路径长度'] = nx.average_shortest_path_length(sub)
            metrics['网络直径'] = nx.diameter(sub)
        return metrics

    def calculate_centrality_measures(self) -> pd.DataFrame:
        degree = nx.degree_centrality(self.G)
        betweenness = nx.betweenness_centrality(self.G)
        closeness = nx.closeness_centrality(self.G)
        eigen = nx.eigenvector_centrality(self.G, max_iter=1000)
        df = pd.DataFrame({
            '用户': list(self.G.nodes()),
            '度中心性': [degree[n] for n in self.G.nodes()],
            '介数中心性': [betweenness[n] for n in self.G.nodes()],
            '接近中心性': [closeness[n] for n in self.G.nodes()],
            '特征向量中心性': [eigen[n] for n in self.G.nodes()],
        })
        df['综合中心性'] = (
            df['度中心性']/df['度中心性'].max()*0.3 +
            df['介数中心性']/df['介数中心性'].max()*0.3 +
            df['接近中心性']/df['接近中心性'].max()*0.2 +
            df['特征向量中心性']/df['特征向量中心性'].max()*0.2
        )
        return df.sort_values('综合中心性', ascending=False)
```

---

## C. CommunityDetector  （community_detection.py）
```python
class CommunityDetector:
    def detect_communities_louvain(self) -> Dict[int, set]:
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(self.G)
            comms = {}
            for node, cid in partition.items():
                comms.setdefault(cid, set()).add(node)
        except ImportError:
            comms_gen = nx_community.louvain_communities(self.G, seed=42)
            comms = {i: c for i, c in enumerate(comms_gen)}
        self.communities = comms
        return comms
```

---

## D. performance_test  （performance_test.py）
```python
def performance_test(n_nodes, m=3, seed=42):
    generator = SocialNetworkGenerator(seed=seed)
    G = generator.generate_complete_network(n_nodes=n_nodes, m=m)

    analyzer = NetworkAnalyzer(G)
    analyzer.calculate_basic_metrics()
    analyzer.calculate_centrality_measures()

    detector = CommunityDetector(G)
    detector.detect_communities_louvain()
```

---

> 通过上述四个类 / 函数即可完整复现论文中的数据生成、网络指标分析、社区划分及性能评估流程。其余辅助脚本（可视化、测试）在项目源码中提供，因篇幅限制不附录于此。


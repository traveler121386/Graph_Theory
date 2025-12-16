"""
主程序：整合数据生成、网络分析、社区检测与可视化
用法：
    python main.py --nodes 300 --m 3 --seed 42 --out ./results
"""

import argparse
import os
import json
import pandas as pd

from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from community_detection import CommunityDetector
from visualization import NetworkVisualizer


def generate_text_report(G, analysis_results, detection_results) -> str:
    """生成综合分析文本报告（用于命令行运行保存）"""
    metrics = analysis_results['basic_metrics']
    centrality_df = analysis_results['centrality']
    community_stats = detection_results['community_stats']

    report = f"""
社交网络图论分析综合报告
====================================

1. 数据与方法概述
- 数据来源：合成数据（BA 无标度网络模型）
- 图类型：无向图（好友关系）
- 节点表示用户；边表示用户之间的社交关系

2. 网络基本结构特性
- 节点数：{metrics['节点数']}
- 边数：{metrics['边数']}
- 网络密度：{metrics['网络密度']:.4f}
- 平均度：{metrics['平均度']:.2f}
- 平均聚类系数：{metrics['平均聚类系数']:.4f}
- 平均最短路径长度：{metrics['平均最短路径长度']:.2f}
- 网络直径：{metrics['网络直径']}

解释：密度较低说明网络稀疏；较高的聚类系数与较小的平均最短路径长度共同体现“小世界”特性；
度分布的长尾反映了少数枢纽（hub）与多数低度数节点并存的无标度特征。

3. 关键用户识别（中心性分析）
- 采用指标：度中心性、介数中心性、接近中心性、特征向量中心性
- 综合中心性排名前5的用户：
"""
    top_5 = centrality_df.head(5)
    for i, row in enumerate(top_5.itertuples(index=False), start=1):
        report += (
            f"\n{i}. {row.用户}\n"
            f"   - 度中心性: {row.度中心性:.4f}\n"
            f"   - 介数中心性: {row.介数中心性:.4f}\n"
            f"   - 接近中心性: {row.接近中心性:.4f}\n"
            f"   - 综合中心性: {row.综合中心性:.4f}\n"
        )

    report += f"""

4. 社区结构与意义
- 检测算法：Louvain（若不可用则回退 Girvan–Newman）
- 检测到的社区数量：{len(community_stats)}
"""
    for _, row in community_stats.iterrows():
        report += (
            f"\n{row['社区ID']}\n"
            f"  - 节点数: {row['节点数']} ({row['节点数']/metrics['节点数']*100:.1f}%)\n"
            f"  - 社区密度: {row['社区密度']:.4f}\n"
            f"  - 社区凝聚力: {row['社区凝聚力']:.4f}\n"
            f"  - 内部边数: {row['内部边数']}  外部边数: {row['外部边数']}\n"
        )

    report += """

应用建议：
- 信息传播：优先选择度中心性高的用户作为信息源；
- 跨社区连接：利用介数中心性高的用户搭桥；
- 社区运营：依据不同社区的规模与凝聚力制定差异化策略。

技术栈：Python、NetworkX、Matplotlib、Pandas（可视化与数据处理），Streamlit（可选交互展示）。
"""
    return report


def main():
    parser = argparse.ArgumentParser(description="社交网络图论分析（命令行）")
    parser.add_argument('--nodes', type=int, default=300, help='节点数量')
    parser.add_argument('--m', type=int, default=3, help='BA 模型参数：每个新节点的连接数')
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    parser.add_argument('--out', type=str, default='./results', help='输出目录')
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # 1) 生成网络
    generator = SocialNetworkGenerator(seed=args.seed)
    G = generator.generate_complete_network(n_nodes=args.nodes, m=args.m)

    # 2) 网络分析
    analyzer = NetworkAnalyzer(G)
    analysis_results = analyzer.run_all_analysis()

    # 3) 社区检测
    detector = CommunityDetector(G)
    detection_results = detector.run_all_detection()

    # 4) 可视化输出
    visualizer = NetworkVisualizer(G, detector.community_map, analysis_results['centrality'])
    visualizer.generate_all_visualizations(detection_results['community_stats'], output_dir=args.out)

    # 5) 保存数值结果
    # 基本指标
    with open(os.path.join(args.out, 'basic_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(analysis_results['basic_metrics'], f, ensure_ascii=False, indent=2)

    # 中心性表
    analysis_results['centrality'].to_csv(os.path.join(args.out, 'centrality.csv'), index=False)

    # 社区统计
    detection_results['community_stats'].to_csv(os.path.join(args.out, 'community_stats.csv'), index=False)

    # 6) 保存文本报告
    report_text = generate_text_report(G, analysis_results, detection_results)
    with open(os.path.join(args.out, 'report.txt'), 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("\n" + "="*60)
    print("所有分析完成。输出已保存到:", os.path.abspath(args.out))
    print("- basic_metrics.json / centrality.csv / community_stats.csv / report.txt")
    print("- 以及 5 张可视化图片 PNG 文件")
    print("="*60)


if __name__ == '__main__':
    main()


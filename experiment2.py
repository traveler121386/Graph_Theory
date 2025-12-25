"""
实验二：中心性指标计算与关键用户识别
输出目录: result2/
"""

import os
import pandas as pd
from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from visualization import NetworkVisualizer

def main():
    """实验二主函数"""
    print("="*80)
    print("实验二：中心性指标计算与关键用户识别")
    print("="*80)
    
    # 创建输出目录
    output_dir = 'result2'
    os.makedirs(output_dir, exist_ok=True)
    
    # 参数设置
    n_nodes = 300
    m = 3
    seed = 42
    
    print(f"\n网络参数: 节点数={n_nodes}, BA参数m={m}, 随机种子={seed}")
    print(f"输出目录: {output_dir}/\n")
    
    # 1) 生成网络
    print("正在生成网络...")
    generator = SocialNetworkGenerator(seed=seed)
    G = generator.generate_complete_network(n_nodes=n_nodes, m=m)
    print(f"✓ 网络生成完成\n")
    
    # 2) 计算中心性
    print("正在计算中心性指标...")
    analyzer = NetworkAnalyzer(G)
    analysis_results = analyzer.run_all_analysis()
    centrality_df = analysis_results['centrality']
    
    # 3) 保存完整中心性数据
    centrality_df.to_csv(os.path.join(output_dir, 'centrality.csv'), 
                         index=False, encoding='utf-8-sig')
    
    # 4) 保存排名前15的用户
    top_15 = centrality_df.head(15).copy()
    top_15.insert(0, '排名', range(1, len(top_15) + 1))
    top_15.to_csv(os.path.join(output_dir, '用户中心性指标排名表.csv'), 
                  index=False, encoding='utf-8-sig')
    
    # 5) 生成中心性对比图
    print("正在生成中心性对比图...")
    visualizer = NetworkVisualizer(G, community_map={}, centrality_df=centrality_df)
    visualizer.visualize_centrality_comparison(
        save_path=os.path.join(output_dir, '04_centrality_comparison.png')
    )
    
    print("\n" + "="*80)
    print("✓ 实验二完成！")
    print("="*80)
    print(f"\n生成的文件（保存在 {output_dir}/ 目录）:")
    print("  - centrality.csv (所有用户的完整数据)")
    print("  - 用户中心性指标排名表.csv (前15名)")
    print("  - 04_centrality_comparison.png")
    print("="*80)

if __name__ == '__main__':
    main()


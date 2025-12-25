"""
实验一：网络生成与基本特性验证
输出目录: result1/
"""

import os
import json
import pandas as pd
from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from visualization import NetworkVisualizer

def main():
    """实验一主函数"""
    print("="*80)
    print("实验一：网络生成与基本特性验证")
    print("="*80)
    
    # 创建输出目录
    output_dir = 'result1'
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
    print(f"✓ 网络生成完成: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边\n")
    
    # 2) 网络分析
    print("正在进行网络分析...")
    analyzer = NetworkAnalyzer(G)
    analysis_results = analyzer.run_all_analysis()
    metrics = analysis_results['basic_metrics']
    
    # 3) 保存基本指标
    with open(os.path.join(output_dir, 'basic_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    
    # 转换为CSV
    metrics_df = pd.DataFrame({
        '指标': list(metrics.keys()),
        '数值': list(metrics.values())
    })
    metrics_df.to_csv(os.path.join(output_dir, '网络基本特性指标表.csv'), 
                      index=False, encoding='utf-8-sig')
    
    # 4) 生成度分布图
    print("正在生成度分布图...")
    visualizer = NetworkVisualizer(G)
    visualizer.visualize_degree_distribution(
        save_path=os.path.join(output_dir, '03_degree_distribution.png')
    )
    
    print("\n" + "="*80)
    print("✓ 实验一完成！")
    print("="*80)
    print(f"\n生成的文件（保存在 {output_dir}/ 目录）:")
    print("  - basic_metrics.json")
    print("  - 网络基本特性指标表.csv")
    print("  - 03_degree_distribution.png")
    print("="*80)

if __name__ == '__main__':
    main()


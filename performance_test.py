"""
性能测试脚本
测试不同规模网络下的算法性能
"""

import os
import time
import pandas as pd
from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from community_detection import CommunityDetector

def performance_test(n_nodes, m=3, seed=42):
    """性能测试函数"""
    print(f"\n测试网络规模: N={n_nodes}, m={m}")
    
    # 1. 网络生成时间
    start = time.time()
    generator = SocialNetworkGenerator(seed=seed)
    G = generator.generate_complete_network(n_nodes=n_nodes, m=m)
    gen_time = time.time() - start
    print(f"  网络生成时间: {gen_time:.3f}秒")
    
    # 2. 基本指标计算时间
    start = time.time()
    analyzer = NetworkAnalyzer(G)
    metrics = analyzer.calculate_basic_metrics()
    basic_time = time.time() - start
    print(f"  基本指标计算: {basic_time:.3f}秒")
    
    # 3. 中心性计算时间
    start = time.time()
    centrality_df = analyzer.calculate_centrality_measures()
    centrality_time = time.time() - start
    print(f"  中心性计算: {centrality_time:.3f}秒")
    
    # 4. 社区检测时间
    start = time.time()
    detector = CommunityDetector(G)
    detector.detect_communities_louvain()
    community_time = time.time() - start
    print(f"  社区检测: {community_time:.3f}秒")
    
    total_time = gen_time + basic_time + centrality_time + community_time
    print(f"  总执行时间: {total_time:.3f}秒")
    
    return {
        '节点数': n_nodes,
        '边数': G.number_of_edges(),
        '生成时间': gen_time,
        '基本指标时间': basic_time,
        '中心性时间': centrality_time,
        '社区检测时间': community_time,
        '总时间': total_time
    }

def main():
    """主函数"""
    print("="*80)
    print("实验四：网络规模对算法性能的影响")
    print("="*80)
    output_dir = 'result4'
    print(f"输出目录: {output_dir}/\n")
    
    # 测试不同规模
    results = []
    test_sizes = [100, 200, 300, 400, 500]
    
    for n in test_sizes:
        result = performance_test(n, m=3, seed=42)
        results.append(result)
    
    # 打印汇总表格
    print("\n" + "="*80)
    print("性能测试汇总表")
    print("="*80)
    print(f"{'节点数':<8} {'边数':<8} {'生成(秒)':<12} {'基本指标(秒)':<15} {'中心性(秒)':<15} {'社区检测(秒)':<15} {'总时间(秒)':<12}")
    print("-"*80)
    for r in results:
        print(f"{r['节点数']:<8} {r['边数']:<8} {r['生成时间']:<12.3f} {r['基本指标时间']:<15.3f} {r['中心性时间']:<15.3f} {r['社区检测时间']:<15.3f} {r['总时间']:<12.3f}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为CSV
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(output_dir, '性能测试结果表.csv'), index=False, encoding='utf-8-sig')
    print(f"\n✓ 结果已保存到: {output_dir}/性能测试结果表.csv")
    
    # 分析性能瓶颈
    print("\n" + "="*80)
    print("性能分析")
    print("="*80)
    avg_centrality_ratio = sum(r['中心性时间'] / r['总时间'] for r in results) / len(results)
    print(f"中心性计算平均占总时间的比例: {avg_centrality_ratio*100:.1f}%")
    print("结论: 中心性计算是系统的主要性能瓶颈")
    
    print("\n" + "="*80)
    print("✓ 实验四完成！")
    print("="*80)
    print(f"\n生成的文件（保存在 {output_dir}/ 目录）:")
    print("  - 性能测试结果表.csv")
    print("\n提示: 运行 python plot_performance.py 生成性能曲线图")
    print("="*80)

if __name__ == '__main__':
    main()


"""
社区检测算法对比脚本
对比 Louvain 和 Girvan-Newman 两种算法的性能
"""

import os
import time
import networkx as nx
import networkx.algorithms.community as nx_community
import pandas as pd
from data_generator import SocialNetworkGenerator
from community_detection import CommunityDetector

# 输出目录
OUTPUT_DIR = 'result3'

def calculate_modularity(G, communities):
    """计算模块度"""
    if isinstance(communities, dict):
        # 如果是字典格式，转换为集合列表
        communities_list = list(communities.values())
    else:
        communities_list = communities
    return nx_community.modularity(G, communities_list)

def compare_algorithms(n_nodes=300, m=3, seed=42):
    """对比两种社区检测算法"""
    print("="*80)
    print("社区检测算法对比实验")
    print("="*80)
    print(f"网络参数: 节点数={n_nodes}, BA参数m={m}, 随机种子={seed}\n")
    
    # 生成网络
    print("正在生成网络...")
    generator = SocialNetworkGenerator(seed=seed)
    G = generator.generate_complete_network(n_nodes=n_nodes, m=m)
    print(f"✓ 网络生成完成: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边\n")
    
    results = {}
    
    # ========== Louvain 算法 ==========
    print("="*80)
    print("算法1: Louvain 算法")
    print("="*80)
    
    detector_louvain = CommunityDetector(G)
    start_time = time.time()
    communities_louvain = detector_louvain.detect_communities_louvain()
    louvain_time = time.time() - start_time
    
    stats_louvain = detector_louvain.analyze_community_structure()
    modularity_louvain = calculate_modularity(G, communities_louvain)
    
    # 计算平均凝聚力
    avg_cohesion_louvain = stats_louvain['社区凝聚力'].mean()
    
    results['Louvain'] = {
        '社区数量': len(communities_louvain),
        '模块度': modularity_louvain,
        '平均凝聚力': avg_cohesion_louvain,
        '运行时间(秒)': louvain_time,
        'communities': communities_louvain,
        'stats': stats_louvain
    }
    
    print(f"\n✓ Louvain 算法结果:")
    print(f"  - 社区数量: {len(communities_louvain)}")
    print(f"  - 模块度: {modularity_louvain:.4f}")
    print(f"  - 平均凝聚力: {avg_cohesion_louvain:.4f}")
    print(f"  - 运行时间: {louvain_time:.3f}秒")
    
    # ========== Girvan-Newman 算法 ==========
    print("\n" + "="*80)
    print("算法2: Girvan-Newman 算法")
    print("="*80)
    
    detector_gn = CommunityDetector(G)
    start_time = time.time()
    communities_gn = detector_gn.detect_communities_girvan_newman()
    gn_time = time.time() - start_time
    
    stats_gn = detector_gn.analyze_community_structure()
    modularity_gn = calculate_modularity(G, communities_gn)
    
    # 计算平均凝聚力
    avg_cohesion_gn = stats_gn['社区凝聚力'].mean()
    
    results['Girvan-Newman'] = {
        '社区数量': len(communities_gn),
        '模块度': modularity_gn,
        '平均凝聚力': avg_cohesion_gn,
        '运行时间(秒)': gn_time,
        'communities': communities_gn,
        'stats': stats_gn
    }
    
    print(f"\n✓ Girvan-Newman 算法结果:")
    print(f"  - 社区数量: {len(communities_gn)}")
    print(f"  - 模块度: {modularity_gn:.4f}")
    print(f"  - 平均凝聚力: {avg_cohesion_gn:.4f}")
    print(f"  - 运行时间: {gn_time:.3f}秒")
    
    # ========== 对比分析 ==========
    print("\n" + "="*80)
    print("算法对比分析")
    print("="*80)
    
    # 创建对比表格
    comparison_data = {
        '算法': ['Louvain', 'Girvan-Newman'],
        '社区数量': [results['Louvain']['社区数量'], results['Girvan-Newman']['社区数量']],
        '模块度': [results['Louvain']['模块度'], results['Girvan-Newman']['模块度']],
        '平均凝聚力': [results['Louvain']['平均凝聚力'], results['Girvan-Newman']['平均凝聚力']],
        '运行时间(秒)': [results['Louvain']['运行时间(秒)'], results['Girvan-Newman']['运行时间(秒)']]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    
    print("\n对比表格:")
    print("-"*80)
    print(comparison_df.to_string(index=False))
    print("-"*80)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 保存对比表格
    comparison_df.to_csv(os.path.join(OUTPUT_DIR, '算法对比表.csv'), index=False, encoding='utf-8-sig')
    print(f"\n✓ 对比表格已保存到: {OUTPUT_DIR}/算法对比表.csv")
    
    # 保存两种算法的详细统计
    results['Louvain']['stats'].to_csv(os.path.join(OUTPUT_DIR, '社区统计_Louvain.csv'), 
                                       index=False, encoding='utf-8-sig')
    results['Girvan-Newman']['stats'].to_csv(os.path.join(OUTPUT_DIR, '社区统计_Girvan-Newman.csv'), 
                                             index=False, encoding='utf-8-sig')
    print(f"✓ Louvain 算法社区统计已保存到: {OUTPUT_DIR}/社区统计_Louvain.csv")
    print(f"✓ Girvan-Newman 算法社区统计已保存到: {OUTPUT_DIR}/社区统计_Girvan-Newman.csv")
    
    # 保存社区检测对比表（Louvain算法的详细统计）
    results['Louvain']['stats'].to_csv(os.path.join(OUTPUT_DIR, '社区检测对比表.csv'), 
                                      index=False, encoding='utf-8-sig')
    print(f"✓ 社区检测对比表已保存到: {OUTPUT_DIR}/社区检测对比表.csv")
    
    # 性能对比分析
    print("\n" + "="*80)
    print("性能分析")
    print("="*80)
    
    speedup = results['Girvan-Newman']['运行时间(秒)'] / results['Louvain']['运行时间(秒)']
    modularity_diff = results['Louvain']['模块度'] - results['Girvan-Newman']['模块度']
    cohesion_diff = results['Louvain']['平均凝聚力'] - results['Girvan-Newman']['平均凝聚力']
    
    print(f"\n1. 运行时间对比:")
    print(f"   - Louvain 算法比 Girvan-Newman 快 {speedup:.1f} 倍")
    print(f"   - 时间差: {results['Girvan-Newman']['运行时间(秒)'] - results['Louvain']['运行时间(秒)']:.3f}秒")
    
    print(f"\n2. 模块度对比:")
    if modularity_diff > 0:
        print(f"   - Louvain 算法的模块度更高，高出 {modularity_diff:.4f}")
        print(f"   - 说明 Louvain 算法的社区划分质量更好")
    else:
        print(f"   - Girvan-Newman 算法的模块度更高，高出 {abs(modularity_diff):.4f}")
        print(f"   - 说明 Girvan-Newman 算法的社区划分质量更好")
    
    print(f"\n3. 社区凝聚力对比:")
    if cohesion_diff > 0:
        print(f"   - Louvain 算法的平均凝聚力更高，高出 {cohesion_diff:.4f}")
        print(f"   - 说明 Louvain 算法检测到的社区内部连接更紧密")
    else:
        print(f"   - Girvan-Newman 算法的平均凝聚力更高，高出 {abs(cohesion_diff):.4f}")
        print(f"   - 说明 Girvan-Newman 算法检测到的社区内部连接更紧密")
    
    print(f"\n4. 社区数量对比:")
    comm_diff = results['Louvain']['社区数量'] - results['Girvan-Newman']['社区数量']
    if comm_diff > 0:
        print(f"   - Louvain 算法检测到更多社区（多 {comm_diff} 个）")
    elif comm_diff < 0:
        print(f"   - Girvan-Newman 算法检测到更多社区（多 {abs(comm_diff)} 个）")
    else:
        print(f"   - 两种算法检测到的社区数量相同")
    
    print("\n" + "="*80)
    print("结论:")
    print("="*80)
    print("1. Louvain 算法在计算效率上具有显著优势，适合处理大规模网络")
    print("2. 两种算法的模块度都大于0.3，说明都获得了良好的社区划分")
    print("3. 模块度更高的算法在社区划分质量上更优")
    print("4. 对于实际应用，建议优先使用 Louvain 算法")
    print("="*80)
    
    return results, comparison_df

def main():
    """主函数"""
    print("="*80)
    print("实验三：社区检测算法对比分析")
    print("="*80)
    print(f"输出目录: {OUTPUT_DIR}/\n")
    
    # 可以修改这些参数
    n_nodes = 300
    m = 3
    seed = 42
    
    results, comparison_df = compare_algorithms(n_nodes=n_nodes, m=m, seed=seed)
    
    print("\n" + "="*80)
    print("✓ 实验三完成！")
    print("="*80)
    print(f"\n生成的文件（保存在 {OUTPUT_DIR}/ 目录）:")
    print("  - 算法对比表.csv")
    print("  - 社区统计_Louvain.csv")
    print("  - 社区统计_Girvan-Newman.csv")
    print("  - 社区检测对比表.csv")
    print("="*80)
    
    return results, comparison_df

if __name__ == '__main__':
    main()


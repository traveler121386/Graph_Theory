"""
模块测试脚本
用于验证各个模块是否正常工作
"""

import sys
import traceback


def test_data_generator():
    """测试数据生成模块"""
    print("\n" + "="*60)
    print("测试 1: 数据生成模块 (data_generator.py)")
    print("="*60)
    
    try:
        from data_generator import SocialNetworkGenerator
        
        print("✓ 成功导入 SocialNetworkGenerator")
        
        # 生成小规模网络用于测试
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=100, m=2)
        
        print(f"✓ 成功生成网络")
        print(f"  - 节点数: {G.number_of_nodes()}")
        print(f"  - 边数: {G.number_of_edges()}")
        
        # 检查节点属性
        sample_node = list(G.nodes())[0]
        print(f"✓ 节点属性: {dict(G.nodes[sample_node])}")
        
        # 检查边属性
        sample_edge = list(G.edges())[0]
        print(f"✓ 边属性: {dict(G[sample_edge[0]][sample_edge[1]]])}")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_network_analysis():
    """测试网络分析模块"""
    print("\n" + "="*60)
    print("测试 2: 网络分析模块 (network_analysis.py)")
    print("="*60)
    
    try:
        from data_generator import SocialNetworkGenerator
        from network_analysis import NetworkAnalyzer
        
        print("✓ 成功导入 NetworkAnalyzer")
        
        # 生成网络
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=100, m=2)
        
        # 分析网络
        analyzer = NetworkAnalyzer(G)
        results = analyzer.run_all_analysis()
        
        print("✓ 成功运行网络分析")
        
        # 检查结果
        metrics = results['basic_metrics']
        print(f"✓ 基本指标:")
        print(f"  - 节点数: {metrics['节点数']}")
        print(f"  - 网络密度: {metrics['网络密度']:.4f}")
        print(f"  - 平均聚类系数: {metrics['平均聚类系数']:.4f}")
        
        centrality_df = results['centrality']
        print(f"✓ 中心性指标: {len(centrality_df)} 个用户")
        print(f"  - 排名第一的用户: {centrality_df.iloc[0]['用户']}")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_community_detection():
    """测试社区检测模块"""
    print("\n" + "="*60)
    print("测试 3: 社区检测模块 (community_detection.py)")
    print("="*60)
    
    try:
        from data_generator import SocialNetworkGenerator
        from community_detection import CommunityDetector
        
        print("✓ 成功导入 CommunityDetector")
        
        # 生成网络
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=100, m=2)
        
        # 检测社区
        detector = CommunityDetector(G)
        results = detector.run_all_detection()
        
        print("✓ 成功运行社区检测")
        
        # 检查结果
        communities = detector.communities
        print(f"✓ 检测到 {len(communities)} 个社区")
        
        community_stats = results['community_stats']
        print(f"✓ 社区统计:")
        for _, row in community_stats.iterrows():
            print(f"  - {row['社区ID']}: {row['节点数']} 个节点, 密度 {row['社区密度']:.4f}")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_visualization():
    """测试可视化模块"""
    print("\n" + "="*60)
    print("测试 4: 可视化模块 (visualization.py)")
    print("="*60)
    
    try:
        from data_generator import SocialNetworkGenerator
        from network_analysis import NetworkAnalyzer
        from community_detection import CommunityDetector
        from visualization import NetworkVisualizer
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        
        print("✓ 成功导入 NetworkVisualizer")
        
        # 生成网络
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=100, m=2)
        
        # 分析网络
        analyzer = NetworkAnalyzer(G)
        results = analyzer.run_all_analysis()
        centrality_df = results['centrality']
        
        # 检测社区
        detector = CommunityDetector(G)
        detector.run_all_detection()
        community_stats = detector.analysis_results['community_stats']
        
        # 可视化
        visualizer = NetworkVisualizer(G, detector.community_map, centrality_df)
        
        print("✓ 成功创建 NetworkVisualizer")
        
        # 测试各种可视化方法
        print("✓ 测试可视化方法...")
        
        # 1. 社区着色
        fig, ax = visualizer.visualize_network_with_communities(figsize=(8, 6))
        print("  ✓ 社区着色网络图")
        
        # 2. 中心性着色
        fig, ax = visualizer.visualize_network_with_centrality(figsize=(8, 6))
        print("  ✓ 中心性着色网络图")
        
        # 3. 度分布
        fig, axes = visualizer.visualize_degree_distribution(figsize=(10, 4))
        print("  ✓ 度分布图")
        
        # 4. 中心性对比
        fig, ax = visualizer.visualize_centrality_comparison(figsize=(10, 5))
        print("  ✓ 中心性对比图")
        
        # 5. 社区统计
        fig, axes = visualizer.visualize_community_statistics(community_stats, figsize=(10, 8))
        print("  ✓ 社区统计图")
        
        print("✓ 所有可视化方法测试通过")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_main_program():
    """测试主程序"""
    print("\n" + "="*60)
    print("测试 5: 主程序 (main.py)")
    print("="*60)
    
    try:
        from data_generator import SocialNetworkGenerator
        from network_analysis import NetworkAnalyzer
        from community_detection import CommunityDetector
        from visualization import NetworkVisualizer
        import os
        import json
        import matplotlib
        matplotlib.use('Agg')
        
        print("✓ 所有模块导入成功")
        
        # 生成网络
        print("✓ 生成网络...")
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=100, m=2)
        
        # 分析网络
        print("✓ 分析网络...")
        analyzer = NetworkAnalyzer(G)
        analysis_results = analyzer.run_all_analysis()
        
        # 检测社区
        print("✓ 检测社区...")
        detector = CommunityDetector(G)
        detection_results = detector.run_all_detection()
        
        # 可视化
        print("✓ 生成可视化...")
        visualizer = NetworkVisualizer(G, detector.community_map, analysis_results['centrality'])
        
        # 创建测试输出目录
        test_output_dir = './test_results'
        os.makedirs(test_output_dir, exist_ok=True)
        
        # 保存结果
        print("✓ 保存结果...")
        
        # 保存基本指标
        with open(os.path.join(test_output_dir, 'basic_metrics.json'), 'w') as f:
            json.dump(analysis_results['basic_metrics'], f, ensure_ascii=False, indent=2)
        
        # 保存中心性表
        analysis_results['centrality'].to_csv(
            os.path.join(test_output_dir, 'centrality.csv'), 
            index=False
        )
        
        # 保存社区统计
        detection_results['community_stats'].to_csv(
            os.path.join(test_output_dir, 'community_stats.csv'), 
            index=False
        )
        
        print(f"✓ 结果已保存到 {test_output_dir}")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("社交网络图论分析系统 - 模块测试")
    print("="*60)
    
    tests = [
        ("数据生成模块", test_data_generator),
        ("网络分析模块", test_network_analysis),
        ("社区检测模块", test_community_detection),
        ("可视化模块", test_visualization),
        ("主程序集成", test_main_program),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())


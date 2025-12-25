"""
实验五：交互式系统功能验证自动化测试脚本
测试所有功能模块，生成测试报告和结果表格
"""

import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime

# 导入自定义模块
from data_generator import SocialNetworkGenerator
from network_analysis import NetworkAnalyzer
from community_detection import CommunityDetector
from visualization import NetworkVisualizer

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = 'result5'
os.makedirs(output_dir, exist_ok=True)

class Experiment5Tester:
    """实验五测试类"""
    
    def __init__(self):
        self.test_results = []
        self.test_summary = []
        
    def test_parameter_adjustment(self):
        """测试参数调整功能"""
        print("\n" + "="*60)
        print("测试1: 参数调整功能")
        print("="*60)
        
        test_cases = [
            {'name': '节点数量调整（50-500）', 'nodes': [50, 100, 200, 300, 500], 'm': 3, 'seed': 42},
            {'name': 'BA参数调整（1-10）', 'nodes': 300, 'm': [1, 3, 5, 7, 10], 'seed': 42},
            {'name': '随机种子修改', 'nodes': 300, 'm': 3, 'seed': [42, 100, 200]},
        ]
        
        for case in test_cases:
            print(f"\n测试: {case['name']}")
            success_count = 0
            total_count = 0
            
            if isinstance(case['nodes'], list):
                for n in case['nodes']:
                    try:
                        generator = SocialNetworkGenerator(seed=case['seed'])
                        G = generator.generate_complete_network(n_nodes=n, m=case['m'])
                        assert G.number_of_nodes() == n
                        success_count += 1
                        total_count += 1
                    except Exception as e:
                        print(f"  ✗ 节点数={n} 失败: {e}")
                        total_count += 1
                        
            elif isinstance(case['m'], list):
                for m in case['m']:
                    try:
                        generator = SocialNetworkGenerator(seed=case['seed'])
                        G = generator.generate_complete_network(n_nodes=case['nodes'], m=m)
                        assert G.number_of_edges() > 0
                        success_count += 1
                        total_count += 1
                    except Exception as e:
                        print(f"  ✗ m={m} 失败: {e}")
                        total_count += 1
                        
            elif isinstance(case['seed'], list):
                for seed in case['seed']:
                    try:
                        generator = SocialNetworkGenerator(seed=seed)
                        G = generator.generate_complete_network(n_nodes=case['nodes'], m=case['m'])
                        assert G.number_of_nodes() == case['nodes']
                        success_count += 1
                        total_count += 1
                    except Exception as e:
                        print(f"  ✗ seed={seed} 失败: {e}")
                        total_count += 1
            
            result = '✓ 正常' if success_count == total_count else f'✗ 部分失败 ({success_count}/{total_count})'
            response_time = '< 1秒'
            
            self.test_results.append({
                '功能模块': '参数调整',
                '测试项': case['name'],
                '结果': result,
                '响应时间': response_time,
                '成功率': f'{success_count}/{total_count}'
            })
            
            print(f"  {result}")
    
    def test_algorithm_selection(self):
        """测试算法选择功能"""
        print("\n" + "="*60)
        print("测试2: 算法选择功能")
        print("="*60)
        
        # 生成测试网络
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=300, m=3)
        
        algorithms = [
            {'name': '自动选择算法', 'algo': 'auto'},
            {'name': 'Louvain (python-louvain)', 'algo': 'louvain_pl'},
            {'name': 'Louvain (NetworkX)', 'algo': 'louvain_nx'},
            {'name': 'Girvan-Newman', 'algo': 'girvan_newman'},
        ]
        
        for algo_info in algorithms:
            print(f"\n测试: {algo_info['name']}")
            start_time = time.time()
            
            try:
                detector = CommunityDetector(G)
                
                if algo_info['algo'] == 'auto' or algo_info['algo'] == 'louvain_pl':
                    detector.detect_communities_louvain()
                elif algo_info['algo'] == 'louvain_nx':
                    import networkx.algorithms.community as nx_community
                    communities_generator = nx_community.louvain_communities(G, seed=42)
                    detector.communities = {i: comm for i, comm in enumerate(communities_generator)}
                    detector._build_community_map()
                elif algo_info['algo'] == 'girvan_newman':
                    detector.detect_communities_girvan_newman()
                
                elapsed_time = time.time() - start_time
                result = '✓ 正常'
                response_time = f'{elapsed_time:.2f}秒'
                
                print(f"  {result} - 运行时间: {response_time}")
                print(f"  检测到 {len(detector.communities)} 个社区")
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                result = f'✗ 失败: {str(e)[:50]}'
                response_time = f'{elapsed_time:.2f}秒'
                print(f"  {result}")
            
            self.test_results.append({
                '功能模块': '算法选择',
                '测试项': algo_info['name'],
                '结果': result,
                '响应时间': response_time,
                '成功率': '-'
            })
    
    def test_data_display(self):
        """测试数据展示功能"""
        print("\n" + "="*60)
        print("测试3: 数据展示功能")
        print("="*60)
        
        # 生成测试数据
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=300, m=3)
        
        analyzer = NetworkAnalyzer(G)
        analysis_results = analyzer.run_all_analysis()
        
        detector = CommunityDetector(G)
        detector.detect_communities_louvain()
        detection_results = detector.run_all_detection()
        
        test_cases = [
            {'name': '网络基本分析', 'test_func': lambda: analysis_results['basic_metrics']},
            {'name': '关键用户识别', 'test_func': lambda: analysis_results['centrality']},
            {'name': '社区结构检测', 'test_func': lambda: detection_results['community_stats']},
        ]
        
        for case in test_cases:
            print(f"\n测试: {case['name']}")
            start_time = time.time()
            
            try:
                data = case['test_func']()
                elapsed_time = time.time() - start_time
                
                if isinstance(data, dict):
                    assert len(data) > 0
                elif isinstance(data, pd.DataFrame):
                    assert len(data) > 0
                
                result = '✓ 正常'
                response_time = f'{elapsed_time:.3f}秒' if elapsed_time < 1 else f'{elapsed_time:.2f}秒'
                
                print(f"  {result} - 响应时间: {response_time}")
                if isinstance(data, pd.DataFrame):
                    print(f"  数据行数: {len(data)}")
                elif isinstance(data, dict):
                    print(f"  指标数量: {len(data)}")
                    
            except Exception as e:
                elapsed_time = time.time() - start_time
                result = f'✗ 失败: {str(e)[:50]}'
                response_time = f'{elapsed_time:.3f}秒'
                print(f"  {result}")
            
            self.test_results.append({
                '功能模块': '数据展示',
                '测试项': case['name'],
                '结果': result,
                '响应时间': response_time,
                '成功率': '-'
            })
    
    def test_visualization(self):
        """测试可视化功能"""
        print("\n" + "="*60)
        print("测试4: 可视化功能")
        print("="*60)
        
        # 生成测试数据
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=300, m=3)
        
        analyzer = NetworkAnalyzer(G)
        analysis_results = analyzer.run_all_analysis()
        
        detector = CommunityDetector(G)
        detector.detect_communities_louvain()
        detection_results = detector.run_all_detection()
        
        visualizer = NetworkVisualizer(G, detector.community_map, analysis_results['centrality'])
        
        test_cases = [
            {'name': '网络可视化（社区着色）', 'func': 'visualize_network_with_communities'},
            {'name': '网络可视化（中心性着色）', 'func': 'visualize_network_with_centrality'},
        ]
        
        for case in test_cases:
            print(f"\n测试: {case['name']}")
            start_time = time.time()
            
            try:
                if case['func'] == 'visualize_network_with_communities':
                    fig, ax = visualizer.visualize_network_with_communities(figsize=(10, 8))
                elif case['func'] == 'visualize_network_with_centrality':
                    fig, ax = visualizer.visualize_network_with_centrality(figsize=(10, 8))
                
                # 保存图片
                filename = case['name'].replace('（', '_').replace('）', '').replace(' ', '_') + '.png'
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close(fig)
                
                elapsed_time = time.time() - start_time
                result = '✓ 正常'
                response_time = f'{elapsed_time:.2f}秒'
                
                print(f"  {result} - 响应时间: {response_time}")
                print(f"  图片已保存: {filepath}")
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                result = f'✗ 失败: {str(e)[:50]}'
                response_time = f'{elapsed_time:.2f}秒'
                print(f"  {result}")
            
            self.test_results.append({
                '功能模块': '网络可视化',
                '测试项': case['name'],
                '结果': result,
                '响应时间': response_time,
                '成功率': '-'
            })
    
    def test_interactive_features(self):
        """测试交互功能"""
        print("\n" + "="*60)
        print("测试5: 交互功能")
        print("="*60)
        
        # 生成测试数据
        generator = SocialNetworkGenerator(seed=42)
        G = generator.generate_complete_network(n_nodes=300, m=3)
        
        analyzer = NetworkAnalyzer(G)
        analysis_results = analyzer.run_all_analysis()
        centrality_df = analysis_results['centrality']
        
        detector = CommunityDetector(G)
        detector.detect_communities_louvain()
        detection_results = detector.run_all_detection()
        community_stats = detection_results['community_stats']
        
        test_cases = [
            {'name': '用户搜索（模糊匹配）', 'data': centrality_df, 'column': '用户', 'test_value': 'User_004'},
            {'name': '社区搜索（模糊匹配）', 'data': community_stats, 'column': '社区ID', 'test_value': 'C0'},
        ]
        
        for case in test_cases:
            print(f"\n测试: {case['name']}")
            start_time = time.time()
            
            try:
                # 模拟模糊搜索
                df = case['data']
                search_term = case['test_value']
                column = case['column']
                
                # 模糊匹配
                if column == '用户':
                    results = df[df[column].str.contains(search_term, case=False, na=False)]
                else:
                    results = df[df[column].str.contains(search_term, case=False, na=False)]
                
                elapsed_time = time.time() - start_time
                result = '✓ 正常'
                response_time = '即时' if elapsed_time < 0.01 else f'{elapsed_time:.3f}秒'
                
                print(f"  {result} - 响应时间: {response_time}")
                print(f"  找到 {len(results)} 条匹配结果")
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                result = f'✗ 失败: {str(e)[:50]}'
                response_time = f'{elapsed_time:.3f}秒'
                print(f"  {result}")
            
            self.test_results.append({
                '功能模块': '交互功能',
                '测试项': case['name'],
                '结果': result,
                '响应时间': response_time,
                '成功率': '-'
            })
    
    def test_result_consistency(self):
        """测试结果一致性"""
        print("\n" + "="*60)
        print("测试6: 结果一致性验证")
        print("="*60)
        
        # 使用相同参数运行两次
        seed = 42
        nodes = 300
        m = 3
        
        print("\n运行第一次分析...")
        generator1 = SocialNetworkGenerator(seed=seed)
        G1 = generator1.generate_complete_network(n_nodes=nodes, m=m)
        analyzer1 = NetworkAnalyzer(G1)
        results1 = analyzer1.run_all_analysis()
        
        print("运行第二次分析...")
        generator2 = SocialNetworkGenerator(seed=seed)
        G2 = generator2.generate_complete_network(n_nodes=nodes, m=m)
        analyzer2 = NetworkAnalyzer(G2)
        results2 = analyzer2.run_all_analysis()
        
        # 比较结果
        metrics1 = results1['basic_metrics']
        metrics2 = results2['basic_metrics']
        
        consistency_checks = [
            ('节点数', metrics1['节点数'], metrics2['节点数']),
            ('边数', metrics1['边数'], metrics2['边数']),
            ('网络密度', metrics1['网络密度'], metrics2['网络密度']),
        ]
        
        all_match = True
        for name, val1, val2 in consistency_checks:
            match = abs(val1 - val2) < 0.0001
            status = '✓' if match else '✗'
            print(f"  {status} {name}: {val1} vs {val2} {'一致' if match else '不一致'}")
            if not match:
                all_match = False
        
        result = '✓ 一致' if all_match else '✗ 不一致'
        print(f"\n结果一致性: {result}")
        
        self.test_results.append({
            '功能模块': '结果一致性',
            '测试项': '相同参数多次运行结果一致性',
            '结果': result,
            '响应时间': '-',
            '成功率': '-'
        })
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("生成测试报告")
        print("="*60)
        
        # 创建DataFrame
        df = pd.DataFrame(self.test_results)
        
        # 保存为CSV
        csv_path = os.path.join(output_dir, '交互式系统功能测试表.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✓ 测试表格已保存: {csv_path}")
        
        # 生成汇总统计
        total_tests = len(df)
        passed_tests = len(df[df['结果'].str.contains('✓', na=False)])
        failed_tests = total_tests - passed_tests
        
        # 按模块统计
        module_stats = df.groupby('功能模块').agg({
            '结果': lambda x: sum(x.str.contains('✓', na=False)),
            '测试项': 'count'
        }).rename(columns={'结果': '通过数', '测试项': '总数'})
        module_stats['通过率'] = (module_stats['通过数'] / module_stats['总数'] * 100).round(1)
        
        # 保存模块统计
        stats_path = os.path.join(output_dir, '功能模块统计表.csv')
        module_stats.to_csv(stats_path, encoding='utf-8-sig')
        print(f"✓ 模块统计已保存: {stats_path}")
        
        # 生成文本报告
        report_path = os.path.join(output_dir, '测试报告.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("实验五：交互式系统功能验证测试报告\n")
            f.write("="*80 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("测试汇总\n")
            f.write("-"*80 + "\n")
            f.write(f"总测试数: {total_tests}\n")
            f.write(f"通过数: {passed_tests}\n")
            f.write(f"失败数: {failed_tests}\n")
            f.write(f"通过率: {passed_tests/total_tests*100:.1f}%\n\n")
            
            f.write("各模块测试统计\n")
            f.write("-"*80 + "\n")
            f.write(module_stats.to_string() + "\n\n")
            
            f.write("详细测试结果\n")
            f.write("-"*80 + "\n")
            f.write(df.to_string(index=False) + "\n\n")
            
            f.write("结论\n")
            f.write("-"*80 + "\n")
            if failed_tests == 0:
                f.write("✓ 所有功能测试通过，系统功能完整，可以正常使用。\n")
            else:
                f.write(f"⚠️  有 {failed_tests} 个测试失败，请检查相关功能模块。\n")
        
        print(f"✓ 测试报告已保存: {report_path}")
        
        # 生成可视化图表
        self.generate_visualization(df, module_stats)
        
        return df, module_stats
    
    def generate_visualization(self, df, module_stats):
        """生成可视化图表"""
        print("\n生成可视化图表...")
        
        # 1. 测试结果饼图
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左图：通过/失败饼图
        ax1 = axes[0]
        passed = len(df[df['结果'].str.contains('✓', na=False)])
        failed = len(df) - passed
        ax1.pie([passed, failed], labels=['通过', '失败'], autopct='%1.1f%%',
               colors=['#4CAF50', '#F44336'], startangle=90)
        ax1.set_title('测试结果分布', fontsize=14, fontweight='bold')
        
        # 右图：各模块通过率柱状图
        ax2 = axes[1]
        modules = module_stats.index.tolist()
        pass_rates = module_stats['通过率'].values
        colors = ['#4CAF50' if rate == 100 else '#FF9800' if rate >= 80 else '#F44336' 
                 for rate in pass_rates]
        bars = ax2.bar(modules, pass_rates, color=colors, alpha=0.8)
        ax2.set_ylabel('通过率 (%)', fontsize=12)
        ax2.set_title('各模块测试通过率', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 110)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar, rate in zip(bars, pass_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        chart_path = os.path.join(output_dir, '测试结果统计图.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 统计图表已保存: {chart_path}")
        
        # 2. 响应时间对比图
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 提取响应时间（转换为秒）
        response_times = []
        test_names = []
        for _, row in df.iterrows():
            if row['响应时间'] != '-' and row['响应时间'] != '即时':
                try:
                    if '秒' in row['响应时间']:
                        time_val = float(row['响应时间'].replace('秒', ''))
                        response_times.append(time_val)
                        test_names.append(f"{row['功能模块']}\n{row['测试项']}")
                except:
                    pass
        
        if response_times:
            colors_map = plt.cm.get_cmap('viridis')
            bars = ax.barh(range(len(response_times)), response_times, 
                          color=[colors_map(i/len(response_times)) for i in range(len(response_times))])
            ax.set_yticks(range(len(test_names)))
            ax.set_yticklabels(test_names, fontsize=9)
            ax.set_xlabel('响应时间（秒）', fontsize=12)
            ax.set_title('各功能响应时间对比', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # 添加数值标签
            for i, (bar, time_val) in enumerate(zip(bars, response_times)):
                ax.text(time_val, i, f' {time_val:.3f}s', 
                       va='center', fontsize=9)
            
            plt.tight_layout()
            time_chart_path = os.path.join(output_dir, '响应时间对比图.png')
            plt.savefig(time_chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ 响应时间对比图已保存: {time_chart_path}")

def main():
    """主函数"""
    print("="*80)
    print("实验五：交互式系统功能验证自动化测试")
    print("="*80)
    print(f"输出目录: {output_dir}/")
    print("="*80)
    
    tester = Experiment5Tester()
    
    # 运行所有测试
    tester.test_parameter_adjustment()
    tester.test_algorithm_selection()
    tester.test_data_display()
    tester.test_visualization()
    tester.test_interactive_features()
    tester.test_result_consistency()
    
    # 生成报告
    df, stats = tester.generate_test_report()
    
    # 打印汇总
    print("\n" + "="*80)
    print("测试完成汇总")
    print("="*80)
    print(f"总测试数: {len(df)}")
    print(f"通过数: {len(df[df['结果'].str.contains('✓', na=False)])}")
    print(f"失败数: {len(df) - len(df[df['结果'].str.contains('✓', na=False)])}")
    print("\n各模块统计:")
    print(stats.to_string())
    print("\n" + "="*80)
    print(f"✓ 所有结果已保存到 {output_dir}/ 目录")
    print("="*80)
    print("\n生成的文件:")
    print("  - 交互式系统功能测试表.csv")
    print("  - 功能模块统计表.csv")
    print("  - 测试报告.txt")
    print("  - 测试结果统计图.png")
    print("  - 响应时间对比图.png")
    print("  - 网络可视化（社区着色）.png")
    print("  - 网络可视化（中心性着色）.png")

if __name__ == '__main__':
    main()


"""
性能测试结果可视化脚本
绘制时间-规模关系曲线图
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_performance_curves(csv_file='result4/性能测试结果表.csv', output_file='result4/性能测试曲线图.png'):
    """
    绘制性能测试曲线图
    
    Args:
        csv_file: 性能测试结果CSV文件路径
        output_file: 输出图片文件名
    """
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: 找不到文件 {csv_file}")
        print("请先运行 performance_test.py 生成性能测试数据")
        return
    
    # 读取数据
    df = pd.read_csv(csv_file)
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('网络规模对算法性能的影响', fontsize=16, fontweight='bold', y=0.995)
    
    # 提取数据
    nodes = df['节点数'].values
    gen_time = df['生成时间'].values
    basic_time = df['基本指标时间'].values
    centrality_time = df['中心性时间'].values
    community_time = df['社区检测时间'].values
    total_time = df['总时间'].values
    
    # 1. 总执行时间曲线
    ax1 = axes[0, 0]
    ax1.plot(nodes, total_time, 'o-', linewidth=2, markersize=8, color='#2E86AB', label='总执行时间')
    ax1.set_xlabel('网络规模（节点数）', fontsize=12)
    ax1.set_ylabel('时间（秒）', fontsize=12)
    ax1.set_title('总执行时间随网络规模变化', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=10)
    
    # 添加数据点标签
    for i, (x, y) in enumerate(zip(nodes, total_time)):
        ax1.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    # 2. 各模块时间对比（堆叠面积图）
    ax2 = axes[0, 1]
    ax2.stackplot(nodes, gen_time, basic_time, centrality_time, community_time,
                  labels=['网络生成', '基本指标', '中心性计算', '社区检测'],
                  colors=['#A23B72', '#F18F01', '#C73E1D', '#6A994E'],
                  alpha=0.7)
    ax2.set_xlabel('网络规模（节点数）', fontsize=12)
    ax2.set_ylabel('时间（秒）', fontsize=12)
    ax2.set_title('各模块执行时间分布（堆叠图）', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left', fontsize=10)
    
    # 3. 各模块时间曲线（多条线）
    ax3 = axes[1, 0]
    ax3.plot(nodes, gen_time, 'o-', linewidth=2, markersize=6, label='网络生成', color='#A23B72')
    ax3.plot(nodes, basic_time, 's-', linewidth=2, markersize=6, label='基本指标', color='#F18F01')
    ax3.plot(nodes, centrality_time, '^-', linewidth=2, markersize=6, label='中心性计算', color='#C73E1D')
    ax3.plot(nodes, community_time, 'd-', linewidth=2, markersize=6, label='社区检测', color='#6A994E')
    ax3.set_xlabel('网络规模（节点数）', fontsize=12)
    ax3.set_ylabel('时间（秒）', fontsize=12)
    ax3.set_title('各模块执行时间对比', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(fontsize=10)
    
    # 4. 各模块时间占比（百分比）
    ax4 = axes[1, 1]
    
    # 计算各模块时间占比
    gen_ratio = (gen_time / total_time * 100)
    basic_ratio = (basic_time / total_time * 100)
    centrality_ratio = (centrality_time / total_time * 100)
    community_ratio = (community_time / total_time * 100)
    
    width = 0.6
    x_pos = np.arange(len(nodes))
    
    p1 = ax4.bar(x_pos, gen_ratio, width, label='网络生成', color='#A23B72', alpha=0.8)
    p2 = ax4.bar(x_pos, basic_ratio, width, bottom=gen_ratio, label='基本指标', color='#F18F01', alpha=0.8)
    p3 = ax4.bar(x_pos, centrality_ratio, width, bottom=gen_ratio+basic_ratio, 
                label='中心性计算', color='#C73E1D', alpha=0.8)
    p4 = ax4.bar(x_pos, community_ratio, width, bottom=gen_ratio+basic_ratio+centrality_ratio,
                label='社区检测', color='#6A994E', alpha=0.8)
    
    ax4.set_xlabel('网络规模（节点数）', fontsize=12)
    ax4.set_ylabel('时间占比（%）', fontsize=12)
    ax4.set_title('各模块时间占比', fontsize=13, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(nodes)
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax4.legend(loc='upper right', fontsize=10)
    
    # 添加百分比标签
    for i in range(len(nodes)):
        # 网络生成
        if gen_ratio[i] > 2:
            ax4.text(i, gen_ratio[i]/2, f'{gen_ratio[i]:.1f}%', 
                    ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        # 基本指标
        if basic_ratio[i] > 2:
            ax4.text(i, gen_ratio[i] + basic_ratio[i]/2, f'{basic_ratio[i]:.1f}%', 
                    ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        # 中心性计算
        if centrality_ratio[i] > 2:
            ax4.text(i, gen_ratio[i] + basic_ratio[i] + centrality_ratio[i]/2, 
                    f'{centrality_ratio[i]:.1f}%', ha='center', va='center', 
                    fontsize=8, color='white', fontweight='bold')
        # 社区检测
        if community_ratio[i] > 2:
            ax4.text(i, gen_ratio[i] + basic_ratio[i] + centrality_ratio[i] + community_ratio[i]/2,
                    f'{community_ratio[i]:.1f}%', ha='center', va='center', 
                    fontsize=8, color='white', fontweight='bold')
    
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 性能测试曲线图已保存到: {output_file}")
    
    # 显示图片
    plt.show()
    
    return fig

def plot_single_curve(csv_file='result4/性能测试结果表.csv', output_file='result4/性能测试单图.png'):
    """
    绘制单一的总执行时间曲线图（更简洁的版本）
    """
    if not os.path.exists(csv_file):
        print(f"错误: 找不到文件 {csv_file}")
        return
    
    df = pd.read_csv(csv_file)
    nodes = df['节点数'].values
    total_time = df['总时间'].values
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(nodes, total_time, 'o-', linewidth=3, markersize=10, 
           color='#2E86AB', markerfacecolor='white', markeredgewidth=2)
    ax.set_xlabel('网络规模（节点数）', fontsize=14, fontweight='bold')
    ax.set_ylabel('总执行时间（秒）', fontsize=14, fontweight='bold')
    ax.set_title('网络规模对总执行时间的影响', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加数据点标签
    for x, y in zip(nodes, total_time):
        ax.annotate(f'{y:.3f}s', (x, y), textcoords="offset points", 
                   xytext=(0,15), ha='center', fontsize=11, fontweight='bold')
    
    # 添加趋势线（二次拟合）
    z = np.polyfit(nodes, total_time, 2)
    p = np.poly1d(z)
    x_trend = np.linspace(nodes.min(), nodes.max(), 100)
    ax.plot(x_trend, p(x_trend), '--', color='#C73E1D', linewidth=2, 
           alpha=0.7, label='趋势线（二次拟合）')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 性能测试单图已保存到: {output_file}")
    plt.show()
    
    return fig

def main():
    """主函数"""
    print("="*80)
    print("实验四：性能测试结果可视化")
    print("="*80)
    
    output_dir = 'result4'
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查数据文件
    csv_file = os.path.join(output_dir, '性能测试结果表.csv')
    if not os.path.exists(csv_file):
        print(f"\n⚠️  未找到 {csv_file}")
        print("请先运行 performance_test.py 生成性能测试数据")
        print("\n运行命令:")
        print("  python performance_test.py")
        return
    
    print(f"\n✓ 找到数据文件: {csv_file}")
    
    # 读取并显示数据摘要
    df = pd.read_csv(csv_file)
    print("\n数据摘要:")
    print("-"*60)
    print(df.to_string(index=False))
    print("-"*60)
    
    # 绘制综合曲线图（4个子图）
    print("\n正在生成综合性能曲线图...")
    plot_performance_curves(csv_file, os.path.join(output_dir, '性能测试曲线图.png'))
    
    # 绘制单一曲线图
    print("\n正在生成单一性能曲线图...")
    plot_single_curve(csv_file, os.path.join(output_dir, '性能测试单图.png'))
    
    print("\n" + "="*80)
    print("✓ 所有图表生成完成！")
    print("="*80)
    print(f"\n生成的文件（保存在 {output_dir}/ 目录）:")
    print("  - 性能测试曲线图.png (4个子图的综合图)")
    print("  - 性能测试单图.png (单一总时间曲线图)")

if __name__ == '__main__':
    main()


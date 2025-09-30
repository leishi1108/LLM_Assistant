"""
主程序入口
"""

from agent.core import GraphBuilder
from agent.utils import log_debug_info


def create_graph():
    """创建并编译图"""
    log_debug_info("开始创建图", "初始化图构建器", "INFO")
    
    try:
        builder = GraphBuilder()
        graph = builder.compile()
        
        log_debug_info("图创建成功", {
            "节点数量": len(builder.builder.nodes),
            "边数量": len(builder.builder.edges)
        }, "INFO")
        
        return graph
    except Exception as e:
        log_debug_info("图创建失败", f"错误: {str(e)}", "ERROR")
        raise


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建图
    graph = create_graph()
    
    log_debug_info("系统启动完成", "LLM-Assistant 已就绪", "INFO")
    
    return graph


# if __name__ == "__main__":
#     graph = main()
#     print("图已创建，可以开始使用")

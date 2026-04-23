/**
 * 获取 AI 生成的数据分析报告
 * 
 * 现在支持三种不同的专业分析维度：
 * @param reportType 'analysis' | 'behavior' | 'recommendation'
 */
export async function callDeepSeekAPI(reportType: string): Promise<string> {
  try {
    // 根据报告类型请求后端特定的深度分析接口
    const response = await fetch(`http://localhost:5000/api/ai/analysis-report/${reportType}`);
    
    if (!response.ok) {
      throw new Error(`后端 AI 接口调用失败: ${response.status}`);
    }

    const data = await response.json();
    return data.report || '无法生成报告内容';
  } catch (error) {
    console.error('获取 AI 报告错误:', error);
    return `### 生成失败\n无法连接到 AI 服务。请确保 Python 后端已启动且配置了有效的 DeepSeek API Key。\n\n错误信息: ${error instanceof Error ? error.message : String(error)}`;
  }
}

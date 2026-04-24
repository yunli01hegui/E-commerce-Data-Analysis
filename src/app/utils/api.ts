import { BASE_URL } from '../data/mockData';

/**
 * 获取 AI 生成的数据分析报告
 * 
 * 现在支持三种不同的专业分析维度，并支持强制刷新。
 */
export async function callDeepSeekAPI(reportType: string, force: boolean = false): Promise<{ report: string; updated_at?: string }> {
  try {
    const response = await fetch(`${BASE_URL}/ai/analysis-report/${reportType}?force=${force}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `后端 AI 接口调用失败: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('获取 AI 报告错误:', error);
    return { 
      report: `### 生成失败\n无法连接到 AI 服务。\n\n错误信息: ${error instanceof Error ? error.message : String(error)}`,
      updated_at: ''
    };
  }
}

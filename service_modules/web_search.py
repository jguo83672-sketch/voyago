"""
网络搜索模块
支持多种搜索API（Google Custom Search, DuckDuckGo, SerpAPI等）
"""
import os
import requests
from typing import List, Dict, Optional


class WebSearcher:
    """网络搜索器"""

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """
        初始化搜索器

        Args:
            api_key: 搜索API密钥
            search_engine_id: 搜索引擎ID（用于Google Custom Search）
        """
        self.api_key = api_key or os.getenv('SEARCH_API_KEY')
        self.search_engine_id = search_engine_id or os.getenv('SEARCH_ENGINE_ID')
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"

    def google_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        使用Google Custom Search API搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.api_key or not self.search_engine_id:
            print("未配置Google Search API，使用模拟数据")
            return self._mock_search(query)

        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': num_results
        }

        try:
            response = requests.get(self.google_search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                })

            return results
        except Exception as e:
            print(f"Google Search API调用失败: {str(e)}")
            return self._mock_search(query)

    def _mock_search(self, query: str) -> List[Dict]:
        """
        模拟搜索结果（当API不可用时使用）

        Args:
            query: 搜索关键词

        Returns:
            模拟搜索结果
        """
        # 基于关键词生成一些通用的旅游信息
        mock_results = []

        # 提取目的地名称
        destination = query.split('旅游')[0] if '旅游' in query else query

        mock_results.append({
            'title': f'{destination}旅游攻略大全',
            'snippet': f'{destination}必游景点、美食推荐、交通指南等全方位旅游攻略。',
            'link': '#'
        })
        mock_results.append({
            'title': f'{destination}最佳旅游时间',
            'snippet': f'了解{destination}的最佳旅游季节和气候特点，选择最佳出行时间。',
            'link': '#'
        })
        mock_results.append({
            'title': f'{destination}特色美食推荐',
            'snippet': f'{destination}地道美食、网红餐厅、必吃小吃等美食攻略。',
            'link': '#'
        })
        mock_results.append({
            'title': f'{destination}住宿指南',
            'snippet': f'{destination}酒店、民宿、青年旅社等住宿推荐和预订指南。',
            'link': '#'
        })
        mock_results.append({
            'title': f'{destination}交通攻略',
            'snippet': f'如何到达{destination}、当地交通方式、出行注意事项等。',
            'link': '#'
        })

        return mock_results

    def search_destination_info(self, destination: str, interests: List[str] = None) -> Dict:
        """
        搜索目的地相关信息

        Args:
            destination: 目的地名称
            interests: 兴趣列表

        Returns:
            格式化的目的地信息
        """
        info = {
            'destination': destination,
            'best_time': '',
            'weather': '',
            'transportation': '',
            'accommodation': '',
            'food': '',
            'attractions': [],
            'tips': []
        }

        # 搜索最佳旅游时间
        results = self.google_search(f'{destination}最佳旅游时间', 3)
        if results:
            info['best_time'] = results[0]['snippet']

        # 搜索交通信息
        results = self.google_search(f'{destination}交通攻略', 2)
        if results:
            info['transportation'] = results[0]['snippet']

        # 搜索住宿信息
        results = self.google_search(f'{destination}住宿推荐', 2)
        if results:
            info['accommodation'] = results[0]['snippet']

        # 搜索美食信息
        results = self.google_search(f'{destination}美食推荐', 3)
        if results:
            info['food'] = '\n'.join([r['snippet'] for r in results])

        # 搜索景点信息
        attractions_query = f'{destination}必游景点'
        if interests:
            attractions_query += f' {", ".join(interests)}'
        results = self.google_search(attractions_query, 5)
        if results:
            info['attractions'] = [{'name': r['title'], 'description': r['snippet']} for r in results]

        # 搜索旅游贴士
        results = self.google_search(f'{destination}旅游注意事项', 3)
        if results:
            info['tips'] = [r['snippet'] for r in results]

        return info

    def format_for_ai(self, search_info: Dict) -> str:
        """
        格式化搜索结果供AI使用

        Args:
            search_info: 搜索信息字典

        Returns:
            格式化的文本
        """
        text = f"""
【网络搜索信息 - {search_info['destination']}】
"""

        if search_info.get('best_time'):
            text += f"\n最佳旅游时间：\n{search_info['best_time']}\n"

        if search_info.get('transportation'):
            text += f"\n交通信息：\n{search_info['transportation']}\n"

        if search_info.get('accommodation'):
            text += f"\n住宿建议：\n{search_info['accommodation']}\n"

        if search_info.get('food'):
            text += f"\n美食推荐：\n{search_info['food']}\n"

        if search_info.get('attractions'):
            text += "\n热门景点：\n"
            for attr in search_info['attractions']:
                text += f"- {attr['name']}：{attr['description']}\n"

        if search_info.get('tips'):
            text += "\n旅游贴士：\n"
            for i, tip in enumerate(search_info['tips'], 1):
                text += f"{i}. {tip}\n"

        return text


# 便捷函数
def create_searcher(api_key: Optional[str] = None, search_engine_id: Optional[str] = None) -> WebSearcher:
    """创建搜索器实例"""
    return WebSearcher(api_key, search_engine_id)

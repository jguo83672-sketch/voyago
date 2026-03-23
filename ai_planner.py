"""
AI行程规划服务模块
集成DeepSeek API进行智能行程规划
"""
import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class AIPlanner:
    """AI行程规划器"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI规划器

        Args:
            api_key: DeepSeek API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self._searcher = None

    @property
    def searcher(self):
        """延迟加载搜索器"""
        if self._searcher is None:
            from web_search import create_searcher
            self._searcher = create_searcher()
        return self._searcher

    def collect_destination_data(self, destinations: List[Dict]) -> str:
        """
        收集目的地数据

        Args:
            destinations: 目的地列表

        Returns:
            格式化的目的地信息字符串
        """
        destination_info = []
        for dest in destinations:
            info = f"""
目的地：{dest['name']}
国家：{dest['country']}
城市：{dest['city']}
描述：{dest['description']}
评分：{dest['rating']}
标签：{dest['tags']}
"""
            destination_info.append(info)
        return "\n".join(destination_info)

    def collect_guide_data(self, guides: List[Dict]) -> str:
        """
        收集攻略数据

        Args:
            guides: 攻略列表

        Returns:
            格式化的攻略信息字符串
        """
        guide_info = []
        for guide in guides[:5]:  # 最多取前5个攻略
            info = f"""
攻略标题：{guide['title']}
内容摘要：{guide['content'][:500]}...
分类：{guide['category']}
浏览量：{guide['view_count']}
"""
            guide_info.append(info)
        return "\n".join(guide_info)

    def collect_itinerary_data(self, itineraries: List[Dict]) -> str:
        """
        收集现有行程数据

        Args:
            itineraries: 行程列表

        Returns:
            格式化的行程信息字符串
        """
        itinerary_info = []
        for itin in itineraries[:3]:  # 最多取前3个行程
            info = f"""
行程标题：{itin['title']}
天数：{itin['days']}
预算：{itin['budget']}
描述：{itin['description']}
"""
            itinerary_info.append(info)
        return "\n".join(itinerary_info)

    def search_web_info(self, destination: str, days: int, interests: List[str]) -> str:
        """
        使用网络搜索API搜索目的地信息

        Args:
            destination: 目的地名称
            days: 行程天数
            interests: 兴趣列表

        Returns:
            搜索结果信息
        """
        try:
            # 使用真实的网络搜索
            search_info = self.searcher.search_destination_info(destination, interests)
            formatted_info = self.searcher.format_for_ai(search_info)
            return formatted_info
        except Exception as e:
            print(f"网络搜索失败，使用模拟数据: {str(e)}")
            # 降级到模拟数据
            search_info = f"""
{destination}旅游信息：
- 最佳旅游时间：全年适宜
- 特色活动：根据兴趣{interests}推荐相关活动
- 交通：{destination}交通便利，可乘坐飞机、高铁等
- 住宿：有多种档次的酒店和民宿可选
- 美食：当地特色美食丰富
- 注意事项：{days}天的行程建议合理安排休息时间
"""
            return search_info

    def build_prompt(self, user_requirements: Dict, context_data: Dict) -> str:
        """
        构建AI提示词（简化版本）

        Args:
            user_requirements: 用户需求
            context_data: 上下文数据（目的地、攻略、行程等）

        Returns:
            格式化的提示词
        """
        # 限制上下文数据的长度
        dest_info = context_data.get('destinations', '')[:500]
        guide_info = context_data.get('guides', '')[:300]
        web_info = context_data.get('web_info', '')[:300]

        prompt = f"""
为{user_requirements['destination']}制定{user_requirements['days']}天行程规划。

需求：
- 天数：{user_requirements['days']}天
- 预算：{user_requirements.get('budget', '不限')}
- 人数：{user_requirements.get('travelers', 1)}人
- 风格：{user_requirements.get('style', '休闲舒适')}
- 兴趣：{user_requirements.get('interests', '无')}

参考信息：
目的地：{dest_info}
网络信息：{web_info}

请输出JSON格式：
{{
    "summary": "简短概述",
    "daily_plans": [
        {{
            "day": 1,
            "title": "主题",
            "description": "描述",
            "activities": [
                {{
                    "time": "时间",
                    "activity": "活动",
                    "location": "地点",
                    "estimated_cost": "费用"
                }}
            ],
            "meals": {{"breakfast": "", "lunch": "", "dinner": ""}},
            "accommodation": "住宿建议",
            "estimated_budget": "当天预算"
        }}
    ],
    "total_budget": "总预算",
    "packing_list": ["物品1", "物品2"],
    "important_tips": ["提示1", "提示2"]
}}

只输出JSON，不要其他文字。"""
        return prompt

    def call_deepseek_api(self, prompt: str, max_retries: int = 2) -> Dict:
        """
        调用DeepSeek API（带重试机制）

        Args:
            prompt: 提示词
            max_retries: 最大重试次数

        Returns:
            API响应结果
        """
        if not self.api_key:
            raise ValueError("未设置DEEPSEEK_API_KEY，请在环境变量中配置")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 减少max_tokens以避免超时
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的旅行规划师，擅长制定详细、实用的旅行行程。只输出JSON格式，不要包含其他文字说明。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000  # 减少token数量
        }

        for attempt in range(max_retries):
            try:
                # 逐次增加超时时间
                timeout = 60 if attempt == 0 else 90
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                result = response.json()

                # 提取AI返回的内容
                content = result['choices'][0]['message']['content']

                # 尝试解析JSON
                try:
                    # 清理可能的前后缀标记
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()

                    parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError as e:
                    # 如果JSON解析失败，返回原始内容
                    return {
                        "error": "JSON解析失败",
                        "raw_content": content,
                        "message": str(e)
                    }

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"API调用超时，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"API调用超时（已重试{max_retries}次），网络可能较慢或API响应时间过长")
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"API调用失败: {str(e)}，正在重试 ({attempt + 1}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"API调用失败（已重试{max_retries}次）: {str(e)}")

        return {}

    def plan_itinerary(
        self,
        destination: str,
        days: int,
        budget: Optional[float] = None,
        start_date: Optional[str] = None,
        travelers: int = 1,
        interests: Optional[List[str]] = None,
        style: str = "休闲舒适",
        special_needs: str = "",
        context_data: Optional[Dict] = None
    ) -> Dict:
        """
        规划行程

        Args:
            destination: 目的地
            days: 天数
            budget: 预算
            start_date: 出发日期
            travelers: 出行人数
            interests: 兴趣爱好列表
            style: 旅行风格
            special_needs: 特殊需求
            context_data: 上下文数据（目的地、攻略、行程等）

        Returns:
            行程规划结果
        """
        # 构建用户需求
        user_requirements = {
            'destination': destination,
            'days': days,
            'budget': f"{budget}元" if budget else "不限",
            'start_date': start_date,
            'travelers': travelers,
            'interests': ', '.join(interests) if interests else '无特殊偏好',
            'style': style,
            'special_needs': special_needs
        }

        # 收集网络搜索信息
        web_info = self.search_web_info(destination, days, interests or [])

        # 整理上下文数据
        if context_data is None:
            context_data = {}
        context_data['web_info'] = web_info

        # 构建提示词
        prompt = self.build_prompt(user_requirements, context_data)

        # 调用API
        try:
            result = self.call_deepseek_api(prompt)
            return {
                'success': True,
                'data': result,
                'requirements': user_requirements
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '行程规划失败，请稍后重试'
            }

    def suggest_destinations(self, interests: List[str], days: int, budget: Optional[float] = None) -> Dict:
        """
        根据兴趣推荐目的地

        Args:
            interests: 兴趣列表
            days: 天数
            budget: 预算

        Returns:
            推荐的目的地列表
        """
        prompt = f"""
根据以下条件推荐3-5个适合的旅游目的地：

兴趣偏好：{', '.join(interests)}
旅游天数：{days}天
预算：{f'{budget}元' if budget else '不限'}

请按照以下JSON格式输出：
{{
    "recommendations": [
        {{
            "name": "目的地名称",
            "country": "国家",
            "city": "城市",
            "reason": "推荐理由",
            "estimated_budget": "预算估算",
            "best_season": "最佳季节"
        }}
    ]
}}

请直接输出JSON格式，不要包含其他文字说明。
"""

        try:
            result = self.call_deepseek_api(prompt)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 便捷函数
def create_planner(api_key: Optional[str] = None) -> AIPlanner:
    """创建AI规划器实例"""
    return AIPlanner(api_key)

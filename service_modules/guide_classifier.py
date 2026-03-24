"""
攻略分类模块
使用 DeepSeek AI 对攻略内容进行自动分类
"""

import os
import requests
import json


class GuideClassifier:
    """攻略分类器"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"

        # 预定义的分类
        self.categories = [
            "美食攻略",
            "交通攻略",
            "住宿攻略",
            "景点攻略",
            "购物攻略",
            "文化攻略",
            "历史攻略",
            "自然攻略",
            "亲子攻略",
            "情侣攻略",
            "亲子攻略",
            "探险攻略",
            "休闲攻略",
            "商务攻略",
            "摄影攻略",
            "自驾攻略"
        ]

    def classify(self, title: str, content: str) -> dict:
        """
        对攻略进行分类

        Args:
            title: 攻略标题
            content: 攻略内容

        Returns:
            分类结果，包含 category 和 confidence
        """
        # 构建提示词
        categories_str = "、".join(self.categories)
        prompt = f"""请根据以下攻略的标题和内容，将其归类到以下分类之一：

分类列表：{categories_str}

攻略标题：{title}

攻略内容：{content}

请只返回一个分类名称，不要包含其他文字。
"""

        try:
            # 调用 DeepSeek API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的旅游攻略分类助手，能够准确地将旅游攻略归类到正确的分类中。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 50
            }

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            category = result['choices'][0]['message']['content'].strip()

            # 验证分类是否在预定义列表中
            if category not in self.categories:
                # 如果不在，选择最接近的分类或默认为"综合攻略"
                category = "综合攻略"

            return {
                "category": category,
                "confidence": 0.9  # 简化处理，实际可以从 API 响应中获取
            }

        except Exception as e:
            print(f"分类失败: {str(e)}")
            # 分类失败时返回默认分类
            return {
                "category": "综合攻略",
                "confidence": 0.5
            }

    def suggest_destination(self, title: str, content: str) -> str:
        """
        从攻略内容中提取目的地信息

        Args:
            title: 攻略标题
            content: 攻略内容

        Returns:
            目的地名称
        """
        prompt = f"""请从以下攻略中提取主要目的地（城市或景点名称），只返回目的地名称，不要包含其他文字。

攻略标题：{title}

攻略内容：{content[:500]}
"""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 50
            }

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            destination = result['choices'][0]['message']['content'].strip()

            return destination if destination else ""

        except Exception as e:
            print(f"提取目的地失败: {str(e)}")
            return ""

    def suggest_title(self, content: str) -> str:
        """
        根据内容生成标题

        Args:
            content: 攻略内容

        Returns:
            建议的标题
        """
        prompt = f"""请为以下旅游攻略内容生成一个简洁吸引人的标题（不超过30字）：

{content[:300]}

只返回标题，不要包含其他文字。
"""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            title = result['choices'][0]['message']['content'].strip()

            return title if title else "我的旅行攻略"

        except Exception as e:
            print(f"生成标题失败: {str(e)}")
            return "我的旅行攻略"


# 创建全局分类器实例
_classifier = None


def get_classifier():
    """获取分类器实例"""
    global _classifier
    if _classifier is None:
        from flask import current_app
        api_key = current_app.config.get('DEEPSEEK_API_KEY', '')

        if not api_key:
            raise Exception("DeepSeek API Key 配置缺失，请在 .env 文件中配置 DEEPSEEK_API_KEY")

        _classifier = GuideClassifier(api_key)

    return _classifier


def classify_guide(title: str, content: str) -> dict:
    """对攻略进行分类"""
    classifier = get_classifier()
    return classifier.classify(title, content)


def suggest_destination(title: str, content: str) -> str:
    """提取目的地信息"""
    classifier = get_classifier()
    return classifier.suggest_destination(title, content)


def suggest_guide_title(content: str) -> str:
    """生成建议标题"""
    classifier = get_classifier()
    return classifier.suggest_title(content)

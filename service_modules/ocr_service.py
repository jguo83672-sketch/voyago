"""
百度 OCR 服务模块
用于识别上传的攻略图片中的文字
"""

import requests
import base64
import time
from typing import Dict, List


class BaiduOCR:
    """百度智能云 OCR 客户端"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_expire_time = 0

    def get_access_token(self) -> str:
        """获取访问令牌"""
        current_time = int(time.time())
        if self.access_token and current_time < self.token_expire_time - 300:
            return self.access_token

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        response = requests.post(url, params=params)
        response.raise_for_status()
        result = response.json()

        if "access_token" not in result:
            raise Exception(f"获取access_token失败: {result}")

        self.access_token = result["access_token"]
        self.token_expire_time = current_time + result.get("expires_in", 2592000)
        return self.access_token

    def recognize_text(self, image_data: bytes, use_accuracy: bool = True) -> str:
        """
        识别图片中的文字

        Args:
            image_data: 图片字节数据
            use_accuracy: 是否使用高精度识别

        Returns:
            识别出的文字内容
        """
        # 将图片转为 base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 获取 access_token
        token = self.get_access_token()

        # 选择 API
        if use_accuracy:
            url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        else:
            url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

        # 发送请求
        params = {"access_token": token}
        data = {"image": image_base64, "language_type": "CHN_ENG"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, params=params, data=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        # 检查错误
        if "error_code" in result:
            raise Exception(f"API错误 [{result['error_code']}]: {result.get('error_msg', '未知错误')}")

        # 提取文字
        words_result = result.get("words_result", [])
        return '\n'.join([item["words"] for item in words_result])

    def recognize_with_position(self, image_data: bytes) -> List[Dict]:
        """
        识别图片中的文字（带位置信息）

        Args:
            image_data: 图片字节数据

        Returns:
            包含文字和位置信息的列表
        """
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        token = self.get_access_token()
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"

        params = {"access_token": token}
        data = {"image": image_base64, "language_type": "CHN_ENG"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, params=params, data=data, headers=headers)
        response.raise_for_status()
        result = response.json()

        if "error_code" in result:
            raise Exception(f"API错误 [{result['error_code']}]: {result.get('error_msg', '未知错误')}")

        return result.get("words_result", [])


# 创建全局 OCR 实例
_ocr_client = None


def get_ocr_client():
    """获取 OCR 客户端实例"""
    global _ocr_client
    if _ocr_client is None:
        from flask import current_app
        api_key = current_app.config.get('BAIDU_OCR_API_KEY', '')
        secret_key = current_app.config.get('BAIDU_OCR_SECRET_KEY', '')

        if not api_key or not secret_key:
            raise Exception("百度 OCR 配置缺失，请在 .env 文件中配置 BAIDU_OCR_API_KEY 和 BAIDU_OCR_SECRET_KEY")

        _ocr_client = BaiduOCR(api_key, secret_key)

    return _ocr_client


def recognize_guide_image(image_data: bytes) -> str:
    """
    识别攻略图片中的文字

    Args:
        image_data: 图片字节数据

    Returns:
        识别出的文字内容
    """
    ocr = get_ocr_client()
    return ocr.recognize_text(image_data, use_accuracy=True)

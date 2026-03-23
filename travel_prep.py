"""
旅行准备模块
提供酒店和机票推荐功能
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class TravelPrepService:
    """旅行准备服务类"""

    # 模拟酒店数据库
    HOTEL_DATABASE = {
        "beijing": [
            {
                "name": "北京华尔道夫酒店",
                "rating": 4.8,
                "price_per_night": 1800,
                "location": "东城区金鱼胡同5-15号",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "会议室", "SPA"],
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
                "source": "携程"
            },
            {
                "name": "北京瑰丽酒店",
                "rating": 4.9,
                "price_per_night": 2200,
                "location": "朝阳区呼家楼京广中心",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA", "商务中心"],
                "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400",
                "source": "携程"
            },
            {
                "name": "北京丽思卡尔顿酒店",
                "rating": 4.7,
                "price_per_night": 2000,
                "location": "朝阳区建国路83号",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "会议室", "礼宾服务"],
                "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400",
                "source": "携程"
            },
            {
                "name": "7天连锁酒店(北京王府井店)",
                "rating": 4.2,
                "price_per_night": 350,
                "location": "东城区王府井大街",
                "amenities": ["免费WiFi", "早餐", "24小时前台"],
                "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400",
                "source": "携程"
            },
            {
                "name": "如家酒店(北京故宫店)",
                "rating": 4.3,
                "price_per_night": 400,
                "location": "东城区东华门大街",
                "amenities": ["免费WiFi", "早餐", "停车场"],
                "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400",
                "source": "携程"
            }
        ],
        "shanghai": [
            {
                "name": "上海浦东丽思卡尔顿酒店",
                "rating": 4.9,
                "price_per_night": 2800,
                "location": "浦东新区陆家嘴世纪大道8号",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA", "行政酒廊"],
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
                "source": "携程"
            },
            {
                "name": "上海外滩华尔道夫酒店",
                "rating": 4.8,
                "price_per_night": 3000,
                "location": "黄浦区中山东一路2号",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA", "历史建筑"],
                "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400",
                "source": "携程"
            },
            {
                "name": "汉庭酒店(上海南京东路店)",
                "rating": 4.4,
                "price_per_night": 500,
                "location": "黄浦区南京东路",
                "amenities": ["免费WiFi", "早餐", "24小时前台"],
                "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400",
                "source": "携程"
            }
        ],
        "guangzhou": [
            {
                "name": "广州四季酒店",
                "rating": 4.8,
                "price_per_night": 2200,
                "location": "天河区珠江新城珠江东路",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA", "商务中心"],
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
                "source": "携程"
            },
            {
                "name": "广州白云希尔顿酒店",
                "rating": 4.7,
                "price_per_night": 1800,
                "location": "白云区白云大道北",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "会议室"],
                "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400",
                "source": "携程"
            },
            {
                "name": "7天酒店(广州北京路店)",
                "rating": 4.2,
                "price_per_night": 300,
                "location": "越秀区北京路",
                "amenities": ["免费WiFi", "早餐"],
                "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400",
                "source": "携程"
            }
        ],
        "tokyo": [
            {
                "name": "东京半岛酒店",
                "rating": 4.9,
                "price_per_night": 5000,
                "location": "千代田区有乐町1-1-1",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA", "米其林餐厅"],
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
                "source": "Agoda"
            },
            {
                "name": "东京安达仕酒店",
                "rating": 4.8,
                "price_per_night": 4500,
                "location": "港区虎之门新城森大厦",
                "amenities": ["免费WiFi", "游泳池", "健身房", "餐厅", "SPA"],
                "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=400",
                "source": "Agoda"
            },
            {
                "name": "APA酒店(新宿)",
                "rating": 4.3,
                "price_per_night": 800,
                "location": "新宿区歌舞伎町",
                "amenities": ["免费WiFi", "早餐", "24小时前台"],
                "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=400",
                "source": "Agoda"
            }
        ]
    }

    # 模拟机票数据库
    FLIGHT_DATABASE = {
        "北京-东京": [
            {
                "airline": "中国国航",
                "flight_number": "CA183",
                "departure_time": "08:30",
                "arrival_time": "12:45",
                "duration": "3小时15分",
                "price": 3500,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            },
            {
                "airline": "全日空",
                "flight_number": "NH955",
                "departure_time": "10:00",
                "arrival_time": "14:20",
                "duration": "3小时20分",
                "price": 3800,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            },
            {
                "airline": "东方航空",
                "flight_number": "MU575",
                "departure_time": "14:30",
                "arrival_time": "18:45",
                "duration": "3小时15分",
                "price": 3200,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            }
        ],
        "北京-上海": [
            {
                "airline": "中国国航",
                "flight_number": "CA1501",
                "departure_time": "07:30",
                "arrival_time": "09:45",
                "duration": "2小时15分",
                "price": 800,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            },
            {
                "airline": "东方航空",
                "flight_number": "MU511",
                "departure_time": "10:00",
                "arrival_time": "12:15",
                "duration": "2小时15分",
                "price": 750,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            },
            {
                "airline": "南方航空",
                "flight_number": "CZ3102",
                "departure_time": "15:00",
                "arrival_time": "17:15",
                "duration": "2小时15分",
                "price": 780,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            }
        ],
        "广州-东京": [
            {
                "airline": "日本航空",
                "flight_number": "JL887",
                "departure_time": "09:30",
                "arrival_time": "15:00",
                "duration": "4小时30分",
                "price": 3200,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            },
            {
                "airline": "南方航空",
                "flight_number": "CZ385",
                "departure_time": "13:00",
                "arrival_time": "18:30",
                "duration": "4小时30分",
                "price": 3000,
                "class_type": "经济舱",
                "stops": 0,
                "source": "携程"
            }
        ]
    }

    @staticmethod
    def get_hotel_recommendations(
        destination_city: str,
        check_in: str,
        check_out: str,
        budget: Optional[float] = None,
        guest_count: int = 1
    ) -> List[Dict]:
        """
        获取酒店推荐

        Args:
            destination_city: 目的地城市
            check_in: 入住日期 (YYYY-MM-DD)
            check_out: 退房日期 (YYYY-MM-DD)
            budget: 预算上限
            guest_count: 入住人数

        Returns:
            酒店推荐列表
        """
        # 模拟匹配城市（简化处理）
        city_key = TravelPrepService._match_city(destination_city)
        hotels = TravelPrepService.HOTEL_DATABASE.get(city_key, [])

        # 计算住宿天数
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            nights = (check_out_date - check_in_date).days
        except:
            nights = 1

        # 根据预算筛选
        if budget:
            hotels = [h for h in hotels if h['price_per_night'] * nights <= budget]

        # 添加预订链接（模拟）
        for hotel in hotels:
            hotel['booking_url'] = f"https://www.ctrip.com/hotel/detail?hotel={hotel['name']}"
            hotel['total_price'] = hotel['price_per_night'] * nights

        # 按评分排序
        hotels.sort(key=lambda x: x['rating'], reverse=True)

        return hotels

    @staticmethod
    def get_flight_recommendations(
        departure_city: str,
        arrival_city: str,
        date: str,
        budget: Optional[float] = None
    ) -> List[Dict]:
        """
        获取机票推荐

        Args:
            departure_city: 出发城市
            arrival_city: 到达城市
            date: 出行日期 (YYYY-MM-DD)
            budget: 预算上限

        Returns:
            机票推荐列表
        """
        # 构建搜索键
        route_key = f"{departure_city}-{arrival_city}"
        flights = TravelPrepService.FLIGHT_DATABASE.get(route_key, [])

        # 根据预算筛选
        if budget:
            flights = [f for f in flights if f['price'] <= budget]

        # 添加预订链接（模拟）
        for flight in flights:
            flight['booking_url'] = f"https://www.ctrip.com/flight/detail?flight={flight['flight_number']}"

        # 按价格排序
        flights.sort(key=lambda x: x['price'])

        return flights

    @staticmethod
    def _match_city(city: str) -> str:
        """
        城市名称匹配

        Args:
            city: 城市名称

        Returns:
            匹配的数据库键
        """
        city_lower = city.lower()
        if '北京' in city or 'beijing' in city_lower or 'peking' in city_lower:
            return 'beijing'
        elif '上海' in city or 'shanghai' in city_lower:
            return 'shanghai'
        elif '广州' in city or 'guangzhou' in city_lower or 'canton' in city_lower:
            return 'guangzhou'
        elif '东京' in city or 'tokyo' in city_lower:
            return 'tokyo'
        else:
            # 默认返回北京
            return 'beijing'

    @staticmethod
    def generate_prep_checklist(days: int) -> List[Dict]:
        """
        生成旅行准备清单

        Args:
            days: 行程天数

        Returns:
            准备清单分类
        """
        checklist = {
            "证件类": [
                {"name": "身份证/护照", "required": True, "checked": False},
                {"name": "签证(如需)", "required": True if days > 7 else False, "checked": False},
                {"name": "机票订单", "required": True, "checked": False},
                {"name": "酒店订单", "required": True, "checked": False},
                {"name": "旅行保险", "required": False, "checked": False}
            ],
            "衣物类": [
                {"name": "换洗衣物(至少{}套)".format(days), "required": True, "checked": False},
                {"name": "外套(视天气而定)", "required": False, "checked": False},
                {"name": "睡衣", "required": True, "checked": False},
                {"name": "内衣裤", "required": True, "checked": False},
                {"name": "舒适的鞋子", "required": True, "checked": False}
            ],
            "洗漱用品": [
                {"name": "牙刷/牙膏", "required": True, "checked": False},
                {"name": "洗发水/沐浴露", "required": True, "checked": False},
                {"name": "毛巾", "required": True, "checked": False},
                {"name": "防晒霜", "required": False, "checked": False},
                {"name": "护肤品", "required": False, "checked": False}
            ],
            "电子设备": [
                {"name": "手机及充电器", "required": True, "checked": False},
                {"name": "转换插头", "required": False, "checked": False},
                {"name": "移动电源", "required": True, "checked": False},
                {"name": "相机", "required": False, "checked": False}
            ],
            "药品类": [
                {"name": "常用药品", "required": False, "checked": False},
                {"name": "感冒药", "required": False, "checked": False},
                {"name": "晕车药/晕机药", "required": False, "checked": False},
                {"name": "创可贴", "required": False, "checked": False}
            ],
            "其他": [
                {"name": "现金/银行卡", "required": True, "checked": False},
                {"name": "水壶", "required": False, "checked": False},
                {"name": "雨伞", "required": False, "checked": False},
                {"name": "零食", "required": False, "checked": False}
            ]
        }
        return checklist


# 便捷函数
def create_prep_service() -> TravelPrepService:
    """创建旅行准备服务实例"""
    return TravelPrepService()

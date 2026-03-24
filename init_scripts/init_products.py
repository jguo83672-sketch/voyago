"""
初始化旅行用品商店数据
"""
from app import app, db
from models import TravelProduct

def init_products():
    """初始化商品数据"""
    with app.app_context():
        # 清空现有商品
        TravelProduct.query.delete()

        # 商品数据
        products = [
            # 行李箱
            {
                "name": "Voyago联名 20寸登机箱",
                "description": "轻便耐用，符合航空公司登机尺寸要求。采用优质ABS材质，静音万向轮，TSA密码锁。",
                "category": "行李箱",
                "subcategory": "登机箱",
                "brand": "Voyago",
                "price": 399,
                "original_price": 599,
                "stock": 100,
                "image_url": "https://img.freepik.com/free-photo/travel-suitcase-isolated-white-background_136403-2950.jpg",
                "rating": 4.8,
                "sales_count": 256,
                "is_featured": True,
                "tags": "登机箱,便携,商务"
            },
            {
                "name": "Voyago联名 24寸行李箱",
                "description": "大容量设计，适合3-5天短途旅行。铝合金边框，静音滚轮，多重保护锁。",
                "category": "行李箱",
                "subcategory": "中号行李箱",
                "brand": "Voyago",
                "price": 599,
                "original_price": 799,
                "stock": 80,
                "image_url": "https://img.freepik.com/free-photo/luggage-suitcase-isolated_439236-8.jpg",
                "rating": 4.7,
                "sales_count": 189,
                "is_featured": True,
                "tags": "行李箱,大容量,耐用"
            },
            {
                "name": "Voyago联名 28寸大行李箱",
                "description": "超大容量，适合长途旅行。双层拉链，多功能隔层，保护性更强。",
                "category": "行李箱",
                "subcategory": "大号行李箱",
                "brand": "Voyago",
                "price": 799,
                "original_price": 999,
                "stock": 60,
                "image_url": "https://img.freepik.com/free-photo/blue-travel-suitcase_23-2147639884.jpg",
                "rating": 4.9,
                "sales_count": 134,
                "is_featured": False,
                "tags": "行李箱,超大容量,长途"
            },

            # 洗漱包
            {
                "name": "Voyago旅行洗漱包",
                "description": "多隔层设计，干湿分离。防水材质，挂钩设计，方便悬挂使用。",
                "category": "洗漱包",
                "subcategory": "洗漱包",
                "brand": "Voyago",
                "price": 89,
                "original_price": 129,
                "stock": 200,
                "image_url": "https://img.freepik.com/free-photo/toiletry-bag-isolated-white_23-2148627268.jpg",
                "rating": 4.6,
                "sales_count": 423,
                "is_featured": True,
                "tags": "洗漱包,防水,便携"
            },
            {
                "name": "Voyago双层化妆包",
                "description": "双层设计，上放化妆品，下放洗漱用品。透明可视，取用方便。",
                "category": "洗漱包",
                "subcategory": "化妆包",
                "brand": "Voyago",
                "price": 129,
                "original_price": 179,
                "stock": 150,
                "image_url": "https://img.freepik.com/free-photo/cosmetic-bag-isolated-white-background_23-2148460179.jpg",
                "rating": 4.7,
                "sales_count": 287,
                "is_featured": False,
                "tags": "化妆包,双层,便携"
            },

            # 一次性用品
            {
                "name": "Voyago一次性洗漱套装（10件套）",
                "description": "包含牙刷、牙膏、毛巾、香皂、梳子等10件一次性用品，旅行必备。",
                "category": "一次性用品",
                "subcategory": "洗漱套装",
                "brand": "Voyago",
                "price": 39,
                "original_price": 59,
                "stock": 300,
                "image_url": "https://img.freepik.com/free-photo/travel-kit-toiletries_23-2148627265.jpg",
                "rating": 4.5,
                "sales_count": 567,
                "is_featured": True,
                "tags": "一次性,套装,便携"
            },
            {
                "name": "Voyago一次性拖鞋（5双）",
                "description": "舒适防滑，酒店必备。棉质鞋底，穿着舒适。",
                "category": "一次性用品",
                "subcategory": "拖鞋",
                "brand": "Voyago",
                "price": 29,
                "original_price": None,
                "stock": 400,
                "image_url": "https://img.freepik.com/free-photo/white-slippers-isolated-white-background_23-2148627266.jpg",
                "rating": 4.4,
                "sales_count": 789,
                "is_featured": False,
                "tags": "一次性,拖鞋,防滑"
            },
            {
                "name": "Voyago一次性毛巾（5条）",
                "description": "加厚压缩毛巾，吸水性好，小巧便携，旅行露营必备。",
                "category": "一次性用品",
                "subcategory": "毛巾",
                "brand": "Voyago",
                "price": 25,
                "original_price": None,
                "stock": 350,
                "image_url": "https://img.freepik.com/free-photo/compressed-towel-travel_23-2148627267.jpg",
                "rating": 4.3,
                "sales_count": 445,
                "is_featured": False,
                "tags": "一次性,毛巾,便携"
            },

            # 转换插头
            {
                "name": "Voyago全球通用转换插头",
                "description": "覆盖150+国家，USB+Type-C双快充，智能识别设备，安全保护。",
                "category": "转换插头",
                "subcategory": "万能转换插头",
                "brand": "Voyago",
                "price": 159,
                "original_price": 229,
                "stock": 150,
                "image_url": "https://img.freepik.com/free-photo/travel-adapter-isolated-white_23-2148627269.jpg",
                "rating": 4.8,
                "sales_count": 345,
                "is_featured": True,
                "tags": "转换插头,全球通用,快充"
            },
            {
                "name": "Voyago欧洲转换插头",
                "description": "专为欧洲旅行设计，双USB接口，小巧便携。",
                "category": "转换插头",
                "subcategory": "欧洲插头",
                "brand": "Voyago",
                "price": 79,
                "original_price": 99,
                "stock": 200,
                "image_url": "https://img.freepik.com/free-photo/european-travel-adapter_23-2148627270.jpg",
                "rating": 4.6,
                "sales_count": 234,
                "is_featured": False,
                "tags": "转换插头,欧洲,USB"
            },
            {
                "name": "Voyago美式转换插头",
                "description": "美国/加拿大专用，三孔+USB设计，满足多设备充电。",
                "category": "转换插头",
                "subcategory": "美式插头",
                "brand": "Voyago",
                "price": 89,
                "original_price": 119,
                "stock": 180,
                "image_url": "https://img.freepik.com/free-photo/us-travel-adapter_23-2148627271.jpg",
                "rating": 4.7,
                "sales_count": 189,
                "is_featured": False,
                "tags": "转换插头,美国,USB"
            },

            # 电话卡
            {
                "name": "Voyago日本电话卡（7天）",
                "description": "高速4G网络，无限流量，包含日本号码，方便联系。",
                "category": "电话卡",
                "subcategory": "日本卡",
                "brand": "Voyago",
                "price": 199,
                "original_price": 249,
                "stock": 250,
                "image_url": "https://img.freepik.com/free-photo/sim-card-isolated-white-background_23-2148627272.jpg",
                "rating": 4.8,
                "sales_count": 456,
                "is_featured": True,
                "tags": "电话卡,日本,4G"
            },
            {
                "name": "Voyago韩国电话卡（7天）",
                "description": "高速网络，无限流量，包含韩国号码，可接听电话。",
                "category": "电话卡",
                "subcategory": "韩国卡",
                "brand": "Voyago",
                "price": 179,
                "original_price": 229,
                "stock": 200,
                "image_url": "https://img.freepik.com/free-phone/sim-card-korea_23-2148627273.jpg",
                "rating": 4.7,
                "sales_count": 323,
                "is_featured": False,
                "tags": "电话卡,韩国,无限流量"
            },
            {
                "name": "Voyago欧洲电话卡（15天）",
                "description": "覆盖30+欧洲国家，高速4G，无限流量，含欧洲号码。",
                "category": "电话卡",
                "subcategory": "欧洲卡",
                "brand": "Voyago",
                "price": 399,
                "original_price": 499,
                "stock": 150,
                "image_url": "https://img.freepik.com/free-phone/european-sim-card_23-2148627274.jpg",
                "rating": 4.6,
                "sales_count": 234,
                "is_featured": False,
                "tags": "电话卡,欧洲,多国"
            },

            # 其他用品
            {
                "name": "Voyago旅行枕",
                "description": "记忆棉材质，贴合颈部曲线，可折叠收纳，飞机火车必备。",
                "category": "其他",
                "subcategory": "旅行枕",
                "brand": "Voyago",
                "price": 89,
                "original_price": 129,
                "stock": 180,
                "image_url": "https://img.freepik.com/free-photo/travel-pillow-isolated-white_23-2148627275.jpg",
                "rating": 4.7,
                "sales_count": 445,
                "is_featured": True,
                "tags": "旅行枕,记忆棉,便携"
            },
            {
                "name": "Voyago旅行三件套",
                "description": "旅行枕+眼罩+耳塞，完美旅行伴侣，助你轻松入眠。",
                "category": "其他",
                "subcategory": "套装",
                "brand": "Voyago",
                "price": 149,
                "original_price": 199,
                "stock": 160,
                "image_url": "https://img.freepik.com/free-photo/travel-set-isolated-white_23-2148627276.jpg",
                "rating": 4.8,
                "sales_count": 367,
                "is_featured": False,
                "tags": "套装,睡眠,便携"
            }
        ]

        # 创建商品
        for product_data in products:
            product = TravelProduct(**product_data)
            db.session.add(product)

        db.session.commit()
        print(f"✓ 成功初始化 {len(products)} 件商品")

if __name__ == '__main__':
    init_products()

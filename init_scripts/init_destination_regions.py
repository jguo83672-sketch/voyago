"""
目的地分类初始化脚本
1. 添加境内/境外分类字段到数据库
2. 迁移现有目的地数据
3. 初始化境内省份和境外地区数据
"""
from app import app, db
from models import Destination
from sqlalchemy import text

# 境内省份列表
DOMESTIC_PROVINCES = [
    '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
    '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
    '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
    '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆',
    '香港', '澳门', '台湾'
]

# 境外大洲+地区数据
INTERNATIONAL_REGIONS = {
    '亚洲': {
        '东南亚': ['泰国', '新加坡', '马来西亚', '印度尼西亚', '越南', '菲律宾', '柬埔寨', '老挝', '缅甸'],
        '东亚': ['日本', '韩国', '朝鲜'],
        '南亚': ['印度', '尼泊尔', '斯里兰卡', '马尔代夫', '孟加拉国'],
        '中亚': ['哈萨克斯坦', '乌兹别克斯坦', '吉尔吉斯斯坦'],
        '西亚': ['土耳其', '阿联酋', '以色列', '沙特阿拉伯', '伊朗', '卡塔尔']
    },
    '欧洲': {
        '西欧': ['法国', '英国', '德国', '荷兰', '比利时', '卢森堡'],
        '南欧': ['意大利', '西班牙', '葡萄牙', '希腊', '克罗地亚'],
        '北欧': ['挪威', '瑞典', '丹麦', '芬兰', '冰岛'],
        '东欧': ['俄罗斯', '波兰', '捷克', '匈牙利', '罗马尼亚'],
        '中欧': ['奥地利', '瑞士']
    },
    '北美洲': {
        '北美洲': ['美国', '加拿大', '墨西哥'],
        '中美洲': ['巴拿马', '哥斯达黎加', '古巴']
    },
    '南美洲': {
        '南美洲': ['巴西', '阿根廷', '智利', '秘鲁', '哥伦比亚', '乌拉圭']
    },
    '非洲': {
        '北非': ['埃及', '摩洛哥', '突尼斯'],
        '东非': ['肯尼亚', '坦桑尼亚', '埃塞俄比亚'],
        '南非': ['南非', '纳米比亚', '博茨瓦纳']
    },
    '大洋洲': {
        '大洋洲': ['澳大利亚', '新西兰', '斐济']
    }
}

def add_database_fields():
    """添加境内/境外分类字段到数据库"""
    print("=" * 50)
    print("步骤 1/3: 添加数据库字段")
    print("=" * 50)
    try:
        db.session.execute(text("ALTER TABLE destinations ADD COLUMN region_type VARCHAR(20) DEFAULT 'domestic'"))
        db.session.execute(text("ALTER TABLE destinations ADD COLUMN province VARCHAR(50)"))
        db.session.execute(text("ALTER TABLE destinations ADD COLUMN continent VARCHAR(50)"))
        db.session.execute(text("ALTER TABLE destinations ADD COLUMN area VARCHAR(50)"))
        db.session.commit()
        print("✅ 数据库字段添加成功!")
        print("   - region_type (境内/境外)")
        print("   - province (省份)")
        print("   - continent (大洲)")
        print("   - area (地区)")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  字段已存在,跳过此步骤")
        else:
            raise

def migrate_existing_data():
    """迁移现有目的地数据"""
    print("\n" + "=" * 50)
    print("步骤 2/3: 迁移现有数据")
    print("=" * 50)

    destinations = Destination.query.all()
    if not destinations:
        print("⚠️  没有需要迁移的现有数据")
        return

    domestic_count = 0
    international_count = 0

    # 常见的境内目的地判断关键词
    domestic_keywords = ['中国', '北京', '上海', '广州', '深圳', '杭州', '西安', '成都',
                     '重庆', '南京', '武汉', '长沙', '厦门', '桂林', '三亚', '丽江',
                     '苏州', '青岛', '大连', '哈尔滨', '拉萨', '乌鲁木齐', '宁夏',
                     '青海', '贵州', '云南', '四川', '浙江', '江苏', '山东', '辽宁',
                     '吉林', '黑龙江', '内蒙古', '新疆', '西藏', '广西', '海南', '广东',
                     '福建', '江西', '湖南', '湖北', '河南', '河北', '山西', '陕西',
                     '甘肃', '宁夏', '青海', '台湾', '香港', '澳门']

    for dest in destinations:
        is_domestic = False

        # 判断是否为境内数据
        for keyword in domestic_keywords:
            if keyword in dest.name or (dest.country and keyword in dest.country):
                is_domestic = True
                break

        if is_domestic:
            # 标记为境内
            dest.region_type = 'domestic'
            dest.province = dest.country if dest.country else dest.name
            dest.continent = None
            dest.area = None
            domestic_count += 1
            print(f"  [境内] {dest.name} -> {dest.province}")
        else:
            # 标记为境外-东南亚(默认)
            dest.region_type = 'international'
            dest.continent = '亚洲'
            dest.area = '东南亚'
            dest.province = None
            international_count += 1
            print(f"  [境外] {dest.name} -> {dest.continent} - {dest.area}")

    db.session.commit()
    print(f"\n✅ 迁移完成! 境内: {domestic_count}个, 境外: {international_count}个")

def init_destination_data():
    """初始化境内省份和境外地区数据"""
    print("\n" + "=" * 50)
    print("步骤 3/3: 初始化目的地数据")
    print("=" * 50)

    domestic_added = 0
    international_added = 0

    # 初始化境内省份
    print("\n初始化境内省份...")
    for province in DOMESTIC_PROVINCES:
        existing = Destination.query.filter_by(
            name=province,
            region_type='domestic',
            province=province
        ).first()

        if not existing:
            dest = Destination(
                name=province,
                region_type='domestic',
                province=province,
                description=f'{province}旅游目的地',
                rating=4.5
            )
            db.session.add(dest)
            domestic_added += 1
            print(f"  + 境内: {province}")

    # 初始化境外大洲+地区
    print("\n初始化境外地区...")
    for continent, areas in INTERNATIONAL_REGIONS.items():
        for area, countries in areas.items():
            for country in countries:
                existing = Destination.query.filter_by(
                    name=country,
                    region_type='international',
                    continent=continent,
                    area=area,
                    country=country
                ).first()

                if not existing:
                    dest = Destination(
                        name=country,
                        region_type='international',
                        continent=continent,
                        area=area,
                        country=country,
                        description=f'{country}旅游目的地',
                        rating=4.5
                    )
                    db.session.add(dest)
                    international_added += 1
                    print(f"  + 境外: {continent} - {area} - {country}")

    db.session.commit()
    print(f"\n✅ 初始化完成! 境内: {domestic_added}个, 境外: {international_added}个")

def main():
    """主函数:执行所有初始化步骤"""
    print("\n🌍 Voyago 目的地分类初始化 🌍\n")

    # 步骤1: 添加数据库字段
    add_database_fields()

    # 步骤2: 迁移现有数据
    migrate_existing_data()

    # 步骤3: 初始化新数据
    init_destination_data()

    print("\n" + "=" * 50)
    print("🎉 全部完成! 目的地分类系统已就绪")
    print("=" * 50)
    print("\n提示: 重启Flask应用以使更改生效\n")

if __name__ == '__main__':
    main()

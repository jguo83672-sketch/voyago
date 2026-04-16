// 高德地图配置
const AMAP_KEY = '8c5652200d248bdd1f8ba1d0cd966392';

// 城市坐标映射（用于自动定位）
const CITY_COORDINATES = {
    '北京': [39.9042, 116.4074],
    '上海': [31.2304, 121.4737],
    '广州': [23.1291, 113.2644],
    '深圳': [22.5431, 114.0579],
    '成都': [30.5728, 104.0668],
    '杭州': [31.2741, 120.1551],
    '西安': [34.3416, 108.9398],
    '武汉': [30.5928, 114.3055],
    '重庆': [29.5630, 106.5516],
    '南京': [32.0603, 118.7969],
    '天津': [39.3434, 117.3616],
    '苏州': [31.2990, 120.5853],
    '青岛': [36.0671, 120.3826],
    '大连': [38.9140, 121.6147],
    '厦门': [24.4798, 118.0819],
    '昆明': [25.0389, 102.7183],
    '宁波': [29.8683, 121.5440],
    '无锡': [31.4912, 120.3119],
    '长沙': [28.2282, 112.9388],
    '郑州': [34.7466, 113.6254],
    '沈阳': [41.8057, 123.4328],
    '哈尔滨': [45.8038, 126.5349],
    '三亚': [18.2528, 109.5119],
    '桂林': [25.2742, 110.2909],
    '拉萨': [29.6500, 91.1000],
    '乌鲁木齐': [43.8256, 87.6168],
    '兰州': [36.0611, 103.8343],
    '呼和浩特': [40.8414, 111.7519],
    '太原': [37.8706, 112.5489],
    '石家庄': [38.0428, 114.5149],
    '济南': [36.6512, 117.1201],
    '合肥': [31.8206, 117.2272],
    '福州': [26.0745, 119.2965],
    '南昌': [28.6895, 115.8942],
    '贵阳': [26.6470, 106.6302],
    '南宁': [22.8170, 108.3665],
    '海口': [20.0458, 110.1989],
    '西宁': [36.6171, 101.7782],
    '银川': [38.4681, 106.2731],
    '台北': [25.0320, 121.5654],
    '高雄': [22.6273, 120.3014],
    '台中': [24.1477, 120.6736],
    '香港': [22.3193, 114.1694],
    '澳门': [22.1987, 113.5439],
    '东京': [35.6762, 139.6503],
    '大阪': [34.6937, 135.5023],
    '京都': [35.0116, 135.7681],
    '横滨': [35.4437, 139.6380],
    '名古屋': [35.1815, 136.9066],
    '福冈': [33.5904, 130.4017],
    '札幌': [43.0618, 141.3545],
    '首尔': [37.5665, 126.9780],
    '釜山': [35.1796, 129.0756],
    '仁川': [37.4563, 126.7052],
    '济州': [33.4996, 126.5312],
    '曼谷': [13.7563, 100.5018],
    '清迈': [18.7883, 98.9853],
    '普吉': [7.8804, 98.3923],
    '新加坡': [1.3521, 103.8198],
    '吉隆坡': [3.1390, 101.6869],
    '槟城': [5.4141, 100.3288],
    '雅加达': [-6.2088, 106.8456],
    '巴厘岛': [-8.4095, 115.1889],
    '马尼拉': [14.5995, 120.9842],
    '河内': [21.0285, 105.8542],
    '胡志明': [10.8231, 106.6297],
    '金边': [11.5564, 104.9282],
    '仰光': [16.8661, 96.1951],
    '巴黎': [48.8566, 2.3522],
    '伦敦': [51.5074, -0.1278],
    '纽约': [40.7128, -74.0060],
    '洛杉矶': [34.0522, -118.2437],
    '旧金山': [37.7749, -122.4194],
    '芝加哥': [41.8781, -87.6298],
    '华盛顿': [38.9072, -77.0369],
    '波士顿': [42.3601, -71.0589],
    '迈阿密': [25.7617, -80.1918],
    '拉斯维加斯': [36.1699, -115.1398],
    '西雅图': [47.6062, -122.3321],
    '悉尼': [-33.8688, 151.2093],
    '墨尔本': [-37.8136, 144.9631],
    '布里斯班': [-27.4698, 153.0251],
    '迪拜': [25.2048, 55.2708],
    '罗马': [41.9028, 12.4964],
    '威尼斯': [45.4408, 12.3155],
    '佛罗伦萨': [43.7696, 11.2558],
    '米兰': [45.4642, 9.1900],
    '巴塞罗那': [41.3851, 2.1734],
    '马德里': [40.4168, -3.7038],
    '阿姆斯特丹': [52.3676, 4.9041],
    '柏林': [52.5200, 13.4050],
    '慕尼黑': [48.1351, 11.5820],
    '汉堡': [55.6761, 9.9937],
    '维也纳': [48.2082, 16.3738],
    '布拉格': [50.0755, 14.4378],
    '苏黎世': [47.3769, 8.5417],
    '斯德哥尔摩': [59.3293, 18.0686],
    '哥本哈根': [55.6761, 12.5683],
    '赫尔辛基': [60.1695, 24.9354],
    '奥斯陆': [59.9139, 10.7522],
    '温哥华': [49.2827, -123.1207],
    '多伦多': [43.6532, -79.3832],
    '蒙特利尔': [45.5017, -73.5673],
    '开罗': [30.0444, 31.2357],
    '约翰内斯堡': [-26.2041, 28.0473],
    '开普敦': [-33.9249, 18.4241],
    '伊斯坦布尔': [41.0082, 28.9784],
    '莫斯科': [55.7558, 37.6173],
    '圣彼得堡': [59.9343, 30.3351]
};

// 省份坐标映射
const PROVINCE_COORDINATES = {
    '北京': [39.9042, 116.4074],
    '上海': [31.2304, 121.4737],
    '天津': [39.3434, 117.3616],
    '河北': [38.0428, 114.5149],
    '山西': [37.8706, 112.5489],
    '内蒙古': [40.8414, 111.7519],
    '辽宁': [41.8057, 123.4328],
    '吉林': [43.8171, 125.3235],
    '黑龙江': [45.8038, 126.5349],
    '江苏': [32.0603, 118.7969],
    '浙江': [30.2741, 120.1551],
    '安徽': [31.8206, 117.2272],
    '福建': [26.0745, 119.2965],
    '江西': [28.6895, 115.8942],
    '山东': [36.6512, 117.1201],
    '河南': [34.7466, 113.6254],
    '湖北': [30.5928, 114.3055],
    '湖南': [28.2282, 112.9388],
    '广东': [23.1291, 113.2644],
    '广西': [22.8170, 108.3665],
    '海南': [20.0458, 110.1989],
    '重庆': [29.5630, 106.5516],
    '四川': [30.5728, 104.0668],
    '贵州': [26.6470, 106.6302],
    '云南': [25.0389, 102.7183],
    '西藏': [29.6500, 91.1000],
    '陕西': [34.3416, 108.9398],
    '甘肃': [36.0611, 103.8343],
    '青海': [36.6171, 101.7782],
    '宁夏': [38.4681, 106.2731],
    '新疆': [43.8256, 87.6168],
    '香港': [22.3193, 114.1694],
    '澳门': [22.1987, 113.5439],
    '台湾': [25.0320, 121.5654]
};

/**
 * 创建可交互的选点地图
 * @param {string} elementId - 地图容器元素ID
 * @param {function} onLocationSelect - 选中位置时的回调函数，参数为 {lat, lng, address}
 * @param {object} options - 可选配置
 * @param {number} options.defaultLat - 默认纬度
 * @param {number} options.defaultLng - 默认经度
 * @param {number} options.defaultZoom - 默认缩放级别
 */
function createPickerMap(elementId, onLocationSelect, options = {}) {
    // 默认中心点（中国）
    const defaultLat = options.defaultLat || 35.8617;
    const defaultLng = options.defaultLng || 104.1954;
    const defaultZoom = options.defaultZoom || 4;

    // 初始化地图
    const map = L.map(elementId).setView([defaultLat, defaultLng], defaultZoom);

    // 添加高德地图瓦片层
    L.tileLayer(`https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}&key=${AMAP_KEY}`, {
        subdomains: ['1', '2', '3', '4'],
        minZoom: 3,
        maxZoom: 18,
        attribution: '© 高德地图'
    }).addTo(map);

    // 添加当前标记
    let currentMarker = null;

    // 如果有默认坐标，添加标记
    if (options.defaultLat && options.defaultLng) {
        currentMarker = L.marker([options.defaultLat, options.defaultLng], {
            draggable: true
        }).addTo(map);

        // 标记拖动事件
        currentMarker.on('dragend', function(e) {
            const position = e.target.getLatLng();
            updateMarker(position);
        });
    }

    // 地图点击事件
    map.on('click', function(e) {
        const { lat, lng } = e.latlng;

        // 如果已有标记，更新位置
        if (currentMarker) {
            currentMarker.setLatLng([lat, lng]);
        } else {
            // 创建新标记
            currentMarker = L.marker([lat, lng], {
                draggable: true
            }).addTo(map);

            // 标记拖动事件
            currentMarker.on('dragend', function(e) {
                const position = e.target.getLatLng();
                updateMarker(position);
            });
        }

        updateMarker({ lat, lng });
    });

    // 更新标记位置并触发回调
    function updateMarker(position) {
        if (currentMarker) {
            currentMarker.bindPopup(`<b>选定位置</b><br>纬度: ${position.lat.toFixed(6)}<br>经度: ${position.lng.toFixed(6)}`).openPopup();

            // 获取地址信息（使用逆地理编码）
            fetch(`https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}&location=${position.lng},${position.lat}`)
                .then(response => response.json())
                .then(data => {
                    let address = '未知位置';
                    if (data.regeocode && data.regeocode.formatted_address) {
                        address = data.regeocode.formatted_address;
                    }

                    // 触发回调
                    if (onLocationSelect) {
                        onLocationSelect({
                            lat: position.lat,
                            lng: position.lng,
                            address: address
                        });
                    }
                })
                .catch(error => {
                    console.error('获取地址失败:', error);
                    // 即使获取地址失败，也触发回调
                    if (onLocationSelect) {
                        onLocationSelect({
                            lat: position.lat,
                            lng: position.lng,
                            address: `纬度: ${position.lat.toFixed(6)}, 经度: ${position.lng.toFixed(6)}`
                        });
                    }
                });
        }
    }

    return map;
}

/**
 * 创建只读展示地图
 * @param {string} elementId - 地图容器元素ID
 * @param {Array} markers - 标记数组，每个元素为 {lat, lng, title, description}
 * @param {object} options - 可选配置
 * @param {number} options.defaultLat - 默认纬度
 * @param {number} options.defaultLng - 默认经度
 * @param {number} options.defaultZoom - 默认缩放级别
 * @param {boolean} options.autoFit - 是否自动调整视图以包含所有标记
 * @param {boolean} options.showRoute - 是否显示路线连接
 * @param {string} options.routeColor - 路线颜色
 */
function createDisplayMap(elementId, markers = [], options = {}) {
    if (markers.length === 0) {
        console.warn('没有标记点，无法创建地图');
        return null;
    }

    // 计算中心点
    let centerLat, centerLng, zoom;

    if (options.autoFit !== false && markers.length > 0) {
        // 计算所有标记的平均位置
        const avgLat = markers.reduce((sum, m) => sum + m.lat, 0) / markers.length;
        const avgLng = markers.reduce((sum, m) => sum + m.lng, 0) / markers.length;
        centerLat = avgLat;
        centerLng = avgLng;
        zoom = options.defaultZoom || (markers.length > 1 ? 5 : 10);
    } else {
        centerLat = options.defaultLat || markers[0].lat;
        centerLng = options.defaultLng || markers[0].lng;
        zoom = options.defaultZoom || 10;
    }

    // 初始化地图
    const map = L.map(elementId).setView([centerLat, centerLng], zoom);

    // 添加高德地图瓦片层
    L.tileLayer(`https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}&key=${AMAP_KEY}`, {
        subdomains: ['1', '2', '3', '4'],
        minZoom: 3,
        maxZoom: 18,
        attribution: '© 高德地图'
    }).addTo(map);

    // 添加标记
    const markerObjects = [];
    markers.forEach((marker, index) => {
        // 创建自定义图标（带序号）
        let icon;
        if (marker.sequence !== undefined) {
            icon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: #3b82f6; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">${marker.sequence}</div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
        }

        const m = L.marker([marker.lat, marker.lng], icon ? { icon } : {}).addTo(map);

        // 添加弹出窗口
        if (marker.title || marker.description) {
            const popupContent = marker.description
                ? `<b>${marker.title}</b><br>${marker.description}`
                : `<b>${marker.title}</b>`;
            m.bindPopup(popupContent);
        }

        markerObjects.push(m);
    });

    // 绘制路线
    if (options.showRoute && markers.length > 1) {
        const routeColor = options.routeColor || '#3b82f6';
        const latlngs = markers.map(m => [m.lat, m.lng]);

        L.polyline(latlngs, {
            color: routeColor,
            weight: 3,
            opacity: 0.7,
            dashArray: '10, 10'
        }).addTo(map);
    }

    // 自动调整视图以包含所有标记
    if (options.autoFit !== false && markerObjects.length > 1) {
        const group = new L.featureGroup(markerObjects);
        map.fitBounds(group.getBounds().pad(0.1));
    }

    return map;
}

/**
 * 根据城市/省份名称获取坐标
 * @param {string} name - 城市或省份名称
 * @returns {Array|null} 坐标数组 [lat, lng] 或 null
 */
function getCoordinatesByName(name) {
    // 优先匹配城市
    if (CITY_COORDINATES[name]) {
        return CITY_COORDINATES[name];
    }
    // 其次匹配省份
    if (PROVINCE_COORDINATES[name]) {
        return PROVINCE_COORDINATES[name];
    }
    return null;
}

/**
 * 使用高德地图API进行地理编码（地址转坐标）
 * @param {string} address - 地址
 * @returns {Promise} 返回 {lat, lng, address}
 */
function geocodeAddress(address) {
    return fetch(`https://restapi.amap.com/v3/geocode/geo?key=${AMAP_KEY}&address=${encodeURIComponent(address)}`)
        .then(response => response.json())
        .then(data => {
            if (data.geocodes && data.geocodes.length > 0) {
                const location = data.geocodes[0].location.split(',');
                return {
                    lng: parseFloat(location[0]),
                    lat: parseFloat(location[1]),
                    address: data.geocodes[0].formatted_address
                };
            }
            return null;
        });
}

/**
 * 使用高德地图API进行逆地理编码（坐标转地址）
 * @param {number} lng - 经度
 * @param {number} lat - 纬度
 * @returns {Promise} 返回地址字符串
 */
function reverseGeocode(lng, lat) {
    return fetch(`https://restapi.amap.com/v3/geocode/regeo?key=${AMAP_KEY}&location=${lng},${lat}`)
        .then(response => response.json())
        .then(data => {
            if (data.regeocode && data.regeocode.formatted_address) {
                return data.regeocode.formatted_address;
            }
            return null;
        });
}

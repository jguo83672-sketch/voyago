import os

def create_upload_directories():
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

    directories = [
        os.path.join(base_path, 'destinations'),
        os.path.join(base_path, 'guides'),
        os.path.join(base_path, 'itineraries'),
        os.path.join(base_path, 'communities'),
        os.path.join(base_path, 'events'),
        os.path.join(base_path, 'avatars'),
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")
        else:
            print(f"目录已存在: {directory}")

    print("\n上传目录初始化完成!")

if __name__ == '__main__':
    create_upload_directories()

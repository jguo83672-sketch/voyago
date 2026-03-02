import os
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif', 'webp']

def save_upload_file(file, upload_folder, subfolder='images'):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        subfolder_path = os.path.join(upload_folder, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        
        filepath = os.path.join(subfolder_path, unique_filename)
        file.save(filepath)
        
        # 处理图片：调整大小并保存缩略图
        try:
            img = Image.open(filepath)
            img.thumbnail((1200, 800))
            img.save(filepath, optimize=True, quality=85)
            
            # 创建缩略图
            thumb_filename = f"thumb_{unique_filename}"
            thumb_path = os.path.join(subfolder_path, thumb_filename)
            img.thumbnail((400, 300))
            img.save(thumb_path, optimize=True, quality=85)
            
        except Exception as e:
            print(f"Error processing image: {e}")
        
        return os.path.join(subfolder, unique_filename).replace('\\', '/')
    return None

def delete_file(filepath, upload_folder):
    if filepath:
        full_path = os.path.join(upload_folder, filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
            
        # 删除缩略图
        filename = os.path.basename(filepath)
        thumb_path = os.path.join(upload_folder, os.path.dirname(filepath), f'thumb_{filename}')
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

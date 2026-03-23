from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///voyago.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 百度 OCR 配置
app.config['BAIDU_OCR_API_KEY'] = os.getenv('BAIDU_OCR_API_KEY', '2BQropxwTK1upuWv8TKQ37iy')
app.config['BAIDU_OCR_SECRET_KEY'] = os.getenv('BAIDU_OCR_SECRET_KEY', 'CPGDTRAfJjif1FzBe3wW5B7wO6C2y2CE')

# DeepSeek AI 配置
app.config['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', '')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录访问此页面'

from routes import *
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import os

# app.py 파일이 있는 디렉토리의 절대 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask-Login 및 세션 관리를 위한 필수 설정
    # 실제 환경에서는 복잡하고 무작위의 키를 사용해야 합니다.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-secret'

    # SQLite 데이터베이스 URI 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASE_DIR, 'menu_data.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

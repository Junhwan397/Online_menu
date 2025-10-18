from flask import Flask
from config import Config
from .extensions import db, migrate
from flask_login import LoginManager  # 1. LoginManager를 가져옵니다.

# 2. LoginManager 인스턴스를 생성합니다.
login_manager = LoginManager()


def create_app(config_class=Config):
    # Flask 애플리케이션 인스턴스 생성
    app = Flask(__name__)

    # 설정 로드 (SECRET_KEY 포함)
    app.config.from_object(config_class)

    # 확장 기능 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. create_app 함수 내에서 LoginManager를 초기화합니다.
    login_manager.init_app(app)

    # 4. 로그인 페이지의 엔드포인트를 login_manager.login_view에 지정합니다.
    # 'main'은 블루프린트 이름이며, 'login_page'는 뷰 함수 이름입니다.
    login_manager.login_view = 'main.login_page'

    # 5. 세션에서 사용자 ID를 기반으로 사용자 객체를 로드하는 user_loader 함수를 정의합니다.
    @login_manager.user_loader
    def load_user(user_id):
        # 순환 참조 문제를 피하기 위해 user_loader 내에서 모델을 지역적으로 임포트합니다.
        from .models import User
        return User.query.get(int(user_id))

    # ----------------------------------------------------
    # 블루프린트 등록
    # ----------------------------------------------------
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from . import models

    return app

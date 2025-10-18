from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 확장 기능을 정의
db = SQLAlchemy()
migrate = Migrate()

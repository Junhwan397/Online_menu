from menu_app import create_app, db

# 애플리케이션 팩토리를 사용하여 앱 인스턴스 생성
app = create_app()

# flask run 또는 python app.py 명령으로 실행하기 위함
if __name__ == '__main__':
    app.run(debug=True)


from menu_app import create_app, db

# 애플리케이션 팩토리를 사용하여 앱 인스턴스 생성
#http://127.0.0.1:5000/menu/GTAJ7AE6
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


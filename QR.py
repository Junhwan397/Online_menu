import qrcode

# ------------------------------
# 1. QR 코드에 담을 데이터 정의
# ------------------------------
# 사용자 기기에서 메뉴 정보를 조회할 서버 주소(베이스 URL)를 가정합니다.
# 실제 앱에서는 이 URL로 접속하여 'r_id=12345'를 분석해 식당 정보를 가져옵니다.
BASE_URL = "https://test1.com"
RESTAURANT_ID = "12345"  # 식당 고유 ID
DATA_TO_ENCODE = f"{BASE_URL}?r_id={RESTAURANT_ID}"

# ------------------------------
# 2. QR 코드 생성 및 설정
# ------------------------------

# QRCode 객체 생성
qr = qrcode.QRCode(
    # 버전(verision): 1부터 40까지의 QR 코드 크기. None이면 자동으로 크기를 결정합니다.
    version=1,
    # 오류 정정 레벨(error_correction):
    # L(약 7%), M(약 15%), Q(약 25%), H(약 30%)
    # H로 설정하면 코드가 일부 손상되어도 복구가 가능합니다.
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    # 박스 크기(box_size): QR 코드의 한 '셀'의 픽셀 수
    box_size=10,
    # 테두리(border): QR 코드 주변의 공백 셀 수
    border=4,
)

# 데이터 추가
qr.add_data(DATA_TO_ENCODE)
qr.make(fit=True)

# ------------------------------
# 3. 이미지 파일로 저장
# ------------------------------

# 이미지 생성 (fill_color: 검은색, back_color: 흰색)
img = qr.make_image(fill_color="black", back_color="white")

# 파일 이름 정의
file_name = f"restaurant_{RESTAURANT_ID}_qr.png"

# 이미지 저장
img.save(file_name)

print(f"✅ QR 코드 생성 완료! 파일 이름: {file_name}")
print(f"➡️ 인코딩된 데이터: {DATA_TO_ENCODE}")
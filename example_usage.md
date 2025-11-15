# API 사용 예시 가이드

## 1. 공공데이터포털 API 사용하기

### 인증 방식: `apiKey`

#### Step 1: API 키 발급
1. [공공데이터포털](https://www.data.go.kr/) 회원가입
2. 원하는 API 검색 (예: "미세먼지")
3. 활용신청 → 승인 대기 (보통 1-2시간)
4. 마이페이지에서 일반 인증키(Encoding/Decoding) 확인

#### Step 2: Python 예제
```python
import requests

# API 정보
api_key = "발급받은_API_키"
url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

params = {
    'serviceKey': api_key,
    'returnType': 'json',
    'numOfRows': '10',
    'pageNo': '1',
    'sidoName': '서울',
    'ver': '1.0'
}

response = requests.get(url, params=params)
data = response.json()
print(data)
```

#### Step 3: JavaScript 예제
```javascript
const apiKey = "발급받은_API_키";
const url = `http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty?serviceKey=${apiKey}&returnType=json&sidoName=서울`;

fetch(url)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

---

## 2. 카카오맵 API 사용하기

### 인증 방식: `apiKey`

#### Step 1: API 키 발급
1. [카카오 개발자 센터](https://developers.kakao.com/) 가입
2. 내 애플리케이션 → 애플리케이션 추가하기
3. 앱 설정 → 플랫폼 설정 → 웹 플랫폼 등록 (도메인)
4. JavaScript 키 또는 REST API 키 복사

#### Step 2: HTML + JavaScript 예제
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>카카오맵</title>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=발급받은_JavaScript_키"></script>
</head>
<body>
    <div id="map" style="width:500px;height:400px;"></div>
    <script>
        var container = document.getElementById('map');
        var options = {
            center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울시청
            level: 3
        };
        var map = new kakao.maps.Map(container, options);
    </script>
</body>
</html>
```

#### Step 3: 주소 검색 (REST API)
```python
import requests

api_key = "발급받은_REST_API_키"
url = "https://dapi.kakao.com/v2/local/search/address.json"

headers = {"Authorization": f"KakaoAK {api_key}"}
params = {"query": "서울 강남구 테헤란로"}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(data)
```

---

## 3. 네이버 검색 API 사용하기

### 인증 방식: `apiKey`

#### Step 1: API 키 발급
1. [네이버 개발자 센터](https://developers.naver.com/) 가입
2. Application → 애플리케이션 등록
3. 검색 API 선택
4. Client ID, Client Secret 발급

#### Step 2: Python 예제
```python
import requests

client_id = "발급받은_Client_ID"
client_secret = "발급받은_Client_Secret"
url = "https://openapi.naver.com/v1/search/blog.json"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

params = {
    "query": "파이썬",
    "display": 10,
    "start": 1,
    "sort": "sim"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

for item in data['items']:
    print(f"제목: {item['title']}")
    print(f"링크: {item['link']}\n")
```

---

## 4. 금융결제원 오픈뱅킹 API 사용하기

### 인증 방식: `OAuth`

#### Step 1: 사전 준비
1. [오픈뱅킹 센터](https://www.openbanking.or.kr/) 회원가입
2. 이용기관 등록 (개인/사업자)
3. 앱 등록 → Client ID, Client Secret 발급

#### Step 2: OAuth 토큰 발급
```python
import requests

# 1. 사용자 인증 (Authorization Code 방식)
auth_url = "https://testapi.openbanking.or.kr/oauth/2.0/authorize"
params = {
    "response_type": "code",
    "client_id": "발급받은_Client_ID",
    "redirect_uri": "http://localhost:8080/callback",
    "scope": "login inquiry transfer",
    "state": "random_string",
    "auth_type": "0"
}
# 사용자를 이 URL로 리다이렉트 → 인증 후 code 받음

# 2. Access Token 발급
token_url = "https://testapi.openbanking.or.kr/oauth/2.0/token"
data = {
    "code": "받은_authorization_code",
    "client_id": "발급받은_Client_ID",
    "client_secret": "발급받은_Client_Secret",
    "redirect_uri": "http://localhost:8080/callback",
    "grant_type": "authorization_code"
}

response = requests.post(token_url, data=data)
token_data = response.json()
access_token = token_data['access_token']

# 3. 계좌 잔액 조회
balance_url = "https://testapi.openbanking.or.kr/v2.0/account/balance/fin_num"
headers = {"Authorization": f"Bearer {access_token}"}
params = {
    "bank_tran_id": "M202300001U00001",
    "fintech_use_num": "핀테크이용번호",
    "tran_dtime": "20230101123000"
}

response = requests.get(balance_url, headers=headers, params=params)
print(response.json())
```

---

## 5. 기상청 날씨 API 사용하기

### 인증 방식: `apiKey`

#### Step 1: API 키 발급
[공공데이터포털](https://www.data.go.kr/)에서 "기상청 단기예보" 검색 후 활용신청

#### Step 2: Python 예제
```python
import requests
from datetime import datetime

api_key = "발급받은_API_키"
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 현재 시간
now = datetime.now()
base_date = now.strftime("%Y%m%d")
base_time = now.strftime("%H00")

params = {
    'serviceKey': api_key,
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'JSON',
    'base_date': base_date,
    'base_time': base_time,
    'nx': '60',  # 격자 X (서울)
    'ny': '127'  # 격자 Y (서울)
}

response = requests.get(url, params=params)
data = response.json()

for item in data['response']['body']['items']['item']:
    category = item['category']
    value = item['obsrValue']
    print(f"{category}: {value}")
```

---

## 6. 한국투자증권 KIS API 사용하기

### 인증 방식: `OAuth`

#### Step 1: 계좌 개설 및 API 신청
1. 한국투자증권 계좌 개설
2. [KIS Developers](https://apiportal.koreainvestment.com/) 가입
3. 앱 등록 → APP_KEY, APP_SECRET 발급
4. 모의투자 or 실전투자 선택

#### Step 2: 토큰 발급 및 주식 시세 조회
```python
import requests
import json

APP_KEY = "발급받은_APP_KEY"
APP_SECRET = "발급받은_APP_SECRET"
BASE_URL = "https://openapi.koreainvestment.com:9443"  # 실전투자

# 1. Access Token 발급
token_url = f"{BASE_URL}/oauth2/tokenP"
headers = {"content-type": "application/json"}
data = {
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
}

response = requests.post(token_url, headers=headers, data=json.dumps(data))
access_token = response.json()['access_token']

# 2. 주식 현재가 조회 (삼성전자: 005930)
price_url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
headers = {
    "content-type": "application/json; charset=utf-8",
    "authorization": f"Bearer {access_token}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST01010100"
}
params = {
    "fid_cond_mrkt_div_code": "J",
    "fid_input_iscd": "005930"
}

response = requests.get(price_url, headers=headers, params=params)
price_data = response.json()
print(f"삼성전자 현재가: {price_data['output']['stck_prpr']}원")
```

---

## 주의사항 및 팁

### ✅ 공통 주의사항
1. **API 키 보안**: 절대 GitHub 등에 공개하지 말 것 (환경변수 사용 권장)
2. **호출 제한**: 대부분 API는 일일/시간당 호출 제한이 있음
3. **테스트 환경**: 실서비스 전 테스트 환경에서 충분히 테스트
4. **에러 처리**: 항상 try-catch 구문으로 예외 처리

### 🔐 환경변수 사용 예시
```python
# .env 파일
API_KEY=your_api_key_here
CLIENT_SECRET=your_secret_here

# Python 코드
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')
```

### 📊 호출 제한 확인
각 API 문서에서 확인:
- 공공데이터: 일반적으로 1일 1,000~10,000건
- 네이버/카카오: API별로 상이 (보통 일 25,000건)
- 금융 API: 실시간 제한이 더 엄격함

### 🛠️ 추천 개발 도구
- **Postman**: API 테스트용
- **Insomnia**: REST API 클라이언트
- **curl**: 커맨드라인 테스트
- **requests** (Python): HTTP 라이브러리
- **axios** (JavaScript): Promise 기반 HTTP 클라이언트

---

## 더 많은 정보

각 API의 상세한 사용법은 해당 API의 공식 문서를 참고하세요.
이 저장소는 API 목록을 제공하며, 각 API 링크를 클릭하면 공식 문서로 이동합니다.

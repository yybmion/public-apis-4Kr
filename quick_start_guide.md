# ⚡ Public APIs - 빠른 시작 가이드

Public APIs 4 Korea에 등록된 API를 **5분 안에** 시작하는 방법을 안내합니다.

## 🎯 이 가이드의 목표

- ✅ API 키 발급받기 (2분)
- ✅ 첫 번째 API 호출하기 (3분)
- ✅ 결과 확인하기

---

## 📋 준비물

1. **Python 3.7 이상** 또는 **Node.js 14 이상**
2. **인터넷 연결**
3. **이메일 주소** (회원가입용)

---

## 🚀 레벨 1: 초급 (인증 불필요)

### 공공데이터포털 - 미세먼지 정보 조회

가장 쉽게 시작할 수 있는 API입니다.

#### Step 1: API 키 발급 (2분)

1. [공공데이터포털](https://www.data.go.kr/) 접속
2. 회원가입 및 로그인
3. 검색창에 "대기오염정보 조회 서비스" 입력
4. **활용신청** 버튼 클릭
5. 1~2시간 후 승인 (이메일 확인)
6. **마이페이지 > 일반 인증키** 확인

#### Step 2: 코드 작성 (3분)

**Python:**
```python
import requests

# 발급받은 인증키 (디코딩 키)
SERVICE_KEY = "여기에_인증키_입력"

url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

params = {
    'serviceKey': SERVICE_KEY,
    'returnType': 'json',
    'numOfRows': '5',
    'pageNo': '1',
    'sidoName': '서울',
    'ver': '1.0'
}

response = requests.get(url, params=params)
data = response.json()

# 결과 출력
items = data['response']['body']['items']
for item in items:
    print(f"{item['stationName']}: PM10={item['pm10Value']}, PM2.5={item['pm25Value']}")
```

**JavaScript (Node.js):**
```javascript
const axios = require('axios');

const SERVICE_KEY = '여기에_인증키_입력';
const url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty';

axios.get(url, {
  params: {
    serviceKey: SERVICE_KEY,
    returnType: 'json',
    numOfRows: '5',
    pageNo: '1',
    sidoName: '서울',
    ver: '1.0'
  }
}).then(response => {
  const items = response.data.response.body.items;
  items.forEach(item => {
    console.log(`${item.stationName}: PM10=${item.pm10Value}, PM2.5=${item.pm25Value}`);
  });
}).catch(error => {
  console.error('에러:', error);
});
```

#### Step 3: 실행

```bash
# Python
python dustcheck.py

# Node.js
node dustcheck.js
```

**예상 출력:**
```
종로구: PM10=30, PM2.5=15
중구: PM10=28, PM2.5=14
용산구: PM10=32, PM2.5=16
성동구: PM10=29, PM2.5=15
광진구: PM10=31, PM2.5=15
```

---

## 🚀 레벨 2: 중급 (REST API 키)

### 카카오맵 - 주소 검색

간단한 REST API로 위치 정보를 얻습니다.

#### Step 1: API 키 발급 (2분)

1. [카카오 개발자](https://developers.kakao.com/) 접속
2. 로그인 (카카오 계정)
3. **내 애플리케이션 > 애플리케이션 추가하기**
4. 앱 이름 입력 후 저장
5. **앱 설정 > 요약 정보**에서 **REST API 키** 복사

#### Step 2: 코드 작성

**Python:**
```python
import requests

REST_API_KEY = "여기에_REST_API_키_입력"

url = "https://dapi.kakao.com/v2/local/search/address.json"

headers = {
    "Authorization": f"KakaoAK {REST_API_KEY}"
}

params = {
    "query": "서울특별시 중구 세종대로 110"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['documents']:
    result = data['documents'][0]
    print(f"주소: {result['address_name']}")
    print(f"위도: {result['y']}")
    print(f"경도: {result['x']}")
else:
    print("검색 결과가 없습니다.")
```

**cURL:**
```bash
curl -G https://dapi.kakao.com/v2/local/search/address.json \
  --data-urlencode "query=서울특별시 중구 세종대로 110" \
  -H "Authorization: KakaoAK 여기에_REST_API_키"
```

**예상 출력:**
```
주소: 서울 중구 태평로1가 31
위도: 37.56682095214089
경도: 126.97839076050163
```

---

## 🚀 레벨 3: 고급 (OAuth 2.0)

### 네이버 로그인

사용자 프로필 정보를 가져옵니다.

#### Step 1: API 키 발급 (3분)

1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. **Application > 애플리케이션 등록**
3. **애플리케이션 이름** 입력
4. **사용 API**: 네이버 로그인 선택
5. **서비스 URL**: http://localhost:8080
6. **Callback URL**: http://localhost:8080/callback
7. **등록하기** 클릭
8. **Client ID**, **Client Secret** 복사

#### Step 2: 로그인 URL 생성

**Python (Flask):**
```python
from flask import Flask, request, redirect
import requests
from urllib.parse import urlencode

app = Flask(__name__)

CLIENT_ID = "여기에_Client_ID"
CLIENT_SECRET = "여기에_Client_Secret"
REDIRECT_URI = "http://localhost:8080/callback"

@app.route('/')
def index():
    # 네이버 로그인 URL
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'random_state'
    }
    url = f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"
    return f'<a href="{url}">네이버 로그인</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Access Token 발급
    token_url = "https://nid.naver.com/oauth2.0/token"
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'state': state
    }

    token_response = requests.post(token_url, data=token_params)
    token_data = token_response.json()
    access_token = token_data['access_token']

    # 프로필 조회
    profile_url = "https://openapi.naver.com/v1/nid/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()

    if profile_data['resultcode'] == '00':
        user = profile_data['response']
        return f"""
        <h1>로그인 성공!</h1>
        <p>이름: {user.get('name', '')}</p>
        <p>이메일: {user.get('email', '')}</p>
        <p>닉네임: {user.get('nickname', '')}</p>
        """
    else:
        return "로그인 실패"

if __name__ == '__main__':
    app.run(port=8080)
```

#### Step 3: 실행

```bash
pip install flask requests
python app.py
```

브라우저에서 http://localhost:8080 접속

---

## 🎯 카테고리별 추천 시작 API

### 🏛 정부/공공 데이터
- ⭐ **기상청 단기예보** - 날씨 정보
- ⭐ **공공데이터포털** - 다양한 공공 데이터
- 난이도: ★☆☆☆☆

### 🗺 지도/위치
- ⭐ **카카오맵** - 주소 검색, 지도 표시
- ⭐ **네이버 지도** - Geocoding
- 난이도: ★★☆☆☆

### 💵 금융
- ⭐ **한국은행 환율** - 실시간 환율
- 난이도: ★☆☆☆☆
- ⚠️ **오픈뱅킹** - 계좌 조회 (OAuth 필요)
- 난이도: ★★★★☆

### 🚗 교통
- ⭐ **서울시 버스 도착정보** - 실시간 버스 위치
- 난이도: ★★☆☆☆

### 🤖 AI
- ⭐ **네이버 파파고** - 번역
- ⭐ **CLOVA OCR** - 이미지 문자 인식
- 난이도: ★★★☆☆

### 🛍 쇼핑
- ⭐ **네이버 쇼핑 검색** - 상품 검색
- 난이도: ★★☆☆☆

---

## 🔧 환경 설정

### Python 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 필요한 패키지 설치
pip install requests
pip install python-dotenv  # 환경 변수 관리
```

### 환경 변수 관리 (.env 파일)

```bash
# .env 파일 생성
PUBLIC_DATA_KEY=여기에_공공데이터_키
KAKAO_REST_API_KEY=여기에_카카오_키
NAVER_CLIENT_ID=여기에_네이버_ID
NAVER_CLIENT_SECRET=여기에_네이버_시크릿
```

```python
# Python 코드
from dotenv import load_dotenv
import os

load_dotenv()

SERVICE_KEY = os.getenv('PUBLIC_DATA_KEY')
```

### Node.js 환경 설정

```bash
# 프로젝트 초기화
npm init -y

# 필요한 패키지 설치
npm install axios
npm install dotenv
```

**.env 파일:**
```
PUBLIC_DATA_KEY=여기에_공공데이터_키
KAKAO_REST_API_KEY=여기에_카카오_키
```

**JavaScript 코드:**
```javascript
require('dotenv').config();
const axios = require('axios');

const SERVICE_KEY = process.env.PUBLIC_DATA_KEY;
```

---

## ⚠️ 자주 발생하는 에러

### 1. 403 Forbidden

**원인:**
- API 키가 승인 대기 중
- 도메인/IP 등록 필요

**해결:**
```python
# 공공데이터: 디코딩 키 사용 확인
SERVICE_KEY = "발급받은_디코딩_키"  # 인코딩 키 X

# 카카오/네이버: 플랫폼 등록 확인
# 카카오 개발자 > 앱 설정 > 플랫폼 > 웹 도메인 등록
```

### 2. CORS 에러 (브라우저)

**원인:**
- 브라우저에서 직접 API 호출 시

**해결:**
```javascript
// 백엔드 서버에서 API 호출
// 또는 프록시 서버 사용
```

### 3. SSL 인증서 오류

**원인:**
- 일부 공공 API의 인증서 문제

**해결:**
```python
# 임시 해결 (개발 환경만)
response = requests.get(url, verify=False)
```

### 4. 인코딩 문제

**원인:**
- 한글 파라미터 인코딩

**해결:**
```python
from urllib.parse import quote

params = {
    'sidoName': quote('서울')  # URL 인코딩
}
```

---

## 📚 다음 단계

### 1단계 완료 후:
- [API 상세 사용 가이드](./api_detailed_guide.md) 읽기
- [데이터 사용 범위 가이드](./data_usage_guide.md) 확인

### 2단계: 실전 프로젝트
- 미세먼지 알림 앱
- 부동산 시세 조회 대시보드
- 날씨 기반 옷 추천 서비스

### 3단계: 고급 주제
- OAuth 2.0 인증 구현
- Rate Limiting & Caching
- 에러 처리 및 재시도 로직
- 프로덕션 배포

---

## 🆘 도움말

### 공식 문서
- [공공데이터포털 가이드](https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do)
- [카카오 개발자 문서](https://developers.kakao.com/)
- [네이버 개발자 문서](https://developers.naver.com/)

### 커뮤니티
- [GitHub Issues](https://github.com/yybmion/public-apis-4Kr/issues)
- [공공데이터포털 Q&A](https://www.data.go.kr/tcs/css/selectCustCenterBoardView.do)

### 문의
- 이 저장소에 Issue 등록
- Pull Request로 개선사항 제안

---

**작성일**: 2025년 11월 15일

이 가이드로 5분 안에 첫 번째 API 호출에 성공하셨나요?
더 많은 예제는 [example_usage.md](./example_usage.md)를 참고하세요!

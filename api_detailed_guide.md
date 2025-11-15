# 📚 Public APIs - 카테고리별 상세 사용 가이드

이 문서는 Public APIs 4 Korea에 등록된 **모든 API**의 상세 사용 방법, 파라미터, 응답 형식을 제공합니다.

## 📖 목차

- [🏛 정부 & 공공기관 API](#-정부--공공기관-api)
- [🗺 지도 & 위치 API](#-지도--위치-api)
- [💵 금융 & 결제 API](#-금융--결제-api)
- [📱 통신사 API](#-통신사-api)
- [🚗 교통 API](#-교통-api)
- [☀️ 날씨 & 환경 API](#-날씨--환경-api)
- [🏥 의료 & 보건 API](#-의료--보건-api)
- [🎓 교육 API](#-교육-api)
- [🏘 부동산 API](#-부동산-api)
- [🎭 문화 & 관광 API](#-문화--관광-api)
- [📊 통계 & 데이터 API](#-통계--데이터-api)
- [🤖 AI & 머신러닝 API](#-ai--머신러닝-api)
- [🛍 쇼핑 & 이커머스 API](#-쇼핑--이커머스-api)
- [📦 배송 & 물류 API](#-배송--물류-api)
- [🍔 음식 & 음료 API](#-음식--음료-api)
- [🎮 게임 & 엔터테인먼트 API](#-게임--엔터테인먼트-api)
- [📺 미디어 & 콘텐츠 API](#-미디어--콘텐츠-api)
- [👥 소셜 & 커뮤니케이션 API](#-소셜--커뮤니케이션-api)
- [<img src="./assets/logo-naver.png" width="16" height="16"/> 네이버 API](#-네이버-api)
- [<img src="./assets/logo-kakao.png" width="16" height="16"/> 카카오 API](#-카카오-api)

---

## 🏛 정부 & 공공기관 API

### 1. 공공데이터포털

**API 문서:** https://www.data.go.kr/

#### 사용 방법

**1단계: API 키 발급**
```
1. 공공데이터포털 회원가입
2. 원하는 API 검색 (예: "미세먼지", "실거래가")
3. 활용신청 클릭
4. 승인 대기 (1~2시간)
5. 마이페이지 > 일반 인증키 확인
```

**2단계: 인증키 디코딩**
```javascript
// 공공데이터는 Encoding/Decoding 두 가지 키 제공
// URL 파라미터에는 Decoding 키 사용
const serviceKey = "발급받은_디코딩_키";
```

**3단계: API 호출 예제**

**미세먼지 정보 조회 (Python)**
```python
import requests
import json

# API 정보
service_key = "발급받은_디코딩_키"
url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"

# 요청 파라미터
params = {
    'serviceKey': service_key,
    'returnType': 'json',      # json 또는 xml
    'numOfRows': '10',          # 한 페이지 결과 수
    'pageNo': '1',              # 페이지 번호
    'sidoName': '서울',         # 시도명
    'ver': '1.0'                # 버전
}

# API 호출
response = requests.get(url, params=params)
data = response.json()

# 응답 데이터 파싱
if data['response']['header']['resultCode'] == '00':
    items = data['response']['body']['items']
    for item in items:
        station = item['stationName']
        pm10 = item['pm10Value']
        pm25 = item['pm25Value']
        print(f"{station}: PM10={pm10}, PM2.5={pm25}")
else:
    print(f"에러: {data['response']['header']['resultMsg']}")
```

**응답 예시:**
```json
{
  "response": {
    "header": {
      "resultCode": "00",
      "resultMsg": "NORMAL_SERVICE"
    },
    "body": {
      "items": [
        {
          "stationName": "종로구",
          "dataTime": "2025-11-15 14:00",
          "pm10Value": "30",
          "pm25Value": "15",
          "o3Value": "0.025",
          "no2Value": "0.030",
          "coValue": "0.4",
          "so2Value": "0.003"
        }
      ],
      "numOfRows": 10,
      "pageNo": 1,
      "totalCount": 25
    }
  }
}
```

**주요 파라미터:**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| serviceKey | String | O | 인증키 |
| returnType | String | X | 응답 형식 (json/xml) |
| numOfRows | Integer | X | 페이지당 결과 수 (기본 10) |
| pageNo | Integer | X | 페이지 번호 (기본 1) |
| sidoName | String | O | 시도명 (서울, 경기 등) |

---

### 2. 기상청 단기예보 API

**API 문서:** https://www.data.go.kr/data/15084084/openapi.do

#### 초단기실황 조회

```python
import requests
from datetime import datetime, timedelta

service_key = "발급받은_디코딩_키"
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 현재 시간 기준 (발표 시각은 매시각 30분)
now = datetime.now()
if now.minute < 30:
    now = now - timedelta(hours=1)
base_date = now.strftime("%Y%m%d")
base_time = now.strftime("%H") + "30"

params = {
    'serviceKey': service_key,
    'pageNo': '1',
    'numOfRows': '10',
    'dataType': 'JSON',
    'base_date': base_date,  # 발표일자 (yyyyMMdd)
    'base_time': base_time,  # 발표시각 (HHmm)
    'nx': '60',              # 예보지점 X좌표
    'ny': '127'              # 예보지점 Y좌표
}

response = requests.get(url, params=params)
data = response.json()

# 카테고리 코드
category_names = {
    'T1H': '기온',
    'RN1': '1시간 강수량',
    'UUU': '동서바람성분',
    'VVV': '남북바람성분',
    'REH': '습도',
    'PTY': '강수형태',
    'VEC': '풍향',
    'WSD': '풍속'
}

items = data['response']['body']['items']['item']
for item in items:
    category = item['category']
    value = item['obsrValue']
    print(f"{category_names.get(category, category)}: {value}")
```

**응답 예시:**
```json
{
  "response": {
    "header": {
      "resultCode": "00",
      "resultMsg": "NORMAL_SERVICE"
    },
    "body": {
      "dataType": "JSON",
      "items": {
        "item": [
          {
            "baseDate": "20251115",
            "baseTime": "1400",
            "category": "T1H",
            "nx": 60,
            "ny": 127,
            "obsrValue": "15.3"
          },
          {
            "category": "RN1",
            "obsrValue": "0"
          },
          {
            "category": "REH",
            "obsrValue": "45"
          }
        ]
      }
    }
  }
}
```

**격자 좌표 변환:**
```python
# 위경도를 격자 좌표로 변환하는 함수
def latlon_to_grid(lat, lon):
    """
    위경도를 기상청 격자 좌표로 변환
    """
    RE = 6371.00877  # 지구 반경
    GRID = 5.0       # 격자 간격 (km)
    SLAT1 = 30.0     # 투영 위도1
    SLAT2 = 60.0     # 투영 위도2
    OLON = 126.0     # 기준점 경도
    OLAT = 38.0      # 기준점 위도
    XO = 43          # 기준점 X좌표
    YO = 136         # 기준점 Y좌표

    # 계산 로직 (생략 - 기상청 매뉴얼 참조)
    # 서울시청 예시: (37.5665, 126.9780) -> (60, 127)

    return nx, ny

# 서울 주요 지점 좌표
locations = {
    '서울시청': (60, 127),
    '강남역': (61, 126),
    '인천공항': (55, 124),
    '수원': (60, 121),
    '부산시청': (98, 76)
}
```

---

### 3. 한국관광공사 TourAPI

**API 문서:** https://api.visitkorea.or.kr/

#### 지역 기반 관광정보 조회

```python
import requests

service_key = "발급받은_인증키"
url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"

params = {
    'serviceKey': service_key,
    'numOfRows': '10',
    'pageNo': '1',
    'MobileOS': 'ETC',
    'MobileApp': 'AppTest',
    '_type': 'json',
    'listYN': 'Y',
    'arrange': 'A',        # 정렬 (A=제목순, B=조회순, C=수정일순)
    'contentTypeId': '12', # 콘텐츠 타입 (12=관광지, 14=문화시설, 15=행사)
    'areaCode': '1',       # 지역코드 (1=서울, 6=부산)
    'sigunguCode': ''      # 시군구코드
}

response = requests.get(url, params=params)
data = response.json()

items = data['response']['body']['items']['item']
for item in items:
    title = item['title']
    addr = item.get('addr1', '')
    tel = item.get('tel', '')
    print(f"{title}\n주소: {addr}\n전화: {tel}\n")
```

**콘텐츠 타입 코드:**
| 코드 | 분류 |
|-----|------|
| 12 | 관광지 |
| 14 | 문화시설 |
| 15 | 축제/공연/행사 |
| 25 | 여행코스 |
| 28 | 레포츠 |
| 32 | 숙박 |
| 38 | 쇼핑 |
| 39 | 음식점 |

**지역 코드:**
| 코드 | 지역 | 코드 | 지역 |
|-----|------|-----|------|
| 1 | 서울 | 2 | 인천 |
| 3 | 대전 | 4 | 대구 |
| 5 | 광주 | 6 | 부산 |
| 7 | 울산 | 8 | 세종 |
| 31 | 경기 | 32 | 강원 |
| 33 | 충북 | 34 | 충남 |
| 35 | 경북 | 36 | 경남 |
| 37 | 전북 | 38 | 전남 |
| 39 | 제주 | | |

---

### 4. 통계청 KOSIS API

**API 문서:** https://kosis.kr/serviceInfo/openAPIGuide.do

#### 통계표 조회

```python
import requests

api_key = "발급받은_API_KEY"
url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"

params = {
    'method': 'getList',
    'apiKey': api_key,
    'itmId': 'T10+',              # 항목코드
    'objL1': 'ALL',               # 분류1
    'objL2': '',                  # 분류2
    'objL3': '',                  # 분류3
    'objL4': '',                  # 분류4
    'objL5': '',                  # 분류5
    'objL6': '',                  # 분류6
    'objL7': '',                  # 분류7
    'objL8': '',                  # 분류8
    'format': 'json',             # json, xml, sdmx
    'jsonVD': 'Y',                # json value direct
    'prdSe': 'M',                 # 주기 (M=월, Q=분기, Y=년)
    'startPrdDe': '202301',       # 시작시점
    'endPrdDe': '202312',         # 종료시점
    'loadGubun': '2',             # 1=메타, 2=데이터
    'orgId': '101',               # 기관코드
    'tblId': 'DT_1B040A3'         # 통계표코드
}

response = requests.get(url, params=params)
data = response.json()

for item in data:
    prd_de = item['PRD_DE']      # 시점
    dt_value = item['DT']        # 값
    c1_nm = item.get('C1_NM', '') # 분류1명
    print(f"{prd_de}: {c1_nm} = {dt_value}")
```

**주요 통계표:**
| 통계표 ID | 통계명 |
|----------|--------|
| DT_1B040A3 | 소비자물가지수 |
| DT_1B040M5 | 생산자물가지수 |
| DT_1YL20631 | 인구총조사 |
| DT_1YL12891 | 가계동향조사 |

---

## 🗺 지도 & 위치 API

### 1. 카카오맵 API

**API 문서:** https://apis.map.kakao.com/web/guide/

#### JavaScript SDK - 지도 표시

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>카카오맵</title>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=발급받은_JavaScript_키"></script>
</head>
<body>
    <div id="map" style="width:100%;height:400px;"></div>
    <script>
        var mapContainer = document.getElementById('map');
        var mapOption = {
            center: new kakao.maps.LatLng(37.5665, 126.9780), // 서울시청
            level: 3 // 확대 레벨 (1~14)
        };
        var map = new kakao.maps.Map(mapContainer, mapOption);

        // 마커 추가
        var markerPosition = new kakao.maps.LatLng(37.5665, 126.9780);
        var marker = new kakao.maps.Marker({
            position: markerPosition
        });
        marker.setMap(map);

        // 인포윈도우 추가
        var infowindow = new kakao.maps.InfoWindow({
            content: '<div style="padding:5px;">서울시청</div>'
        });
        infowindow.open(map, marker);
    </script>
</body>
</html>
```

#### REST API - 주소 검색

```python
import requests

rest_api_key = "발급받은_REST_API_키"
url = "https://dapi.kakao.com/v2/local/search/address.json"

headers = {
    "Authorization": f"KakaoAK {rest_api_key}"
}

params = {
    "query": "서울특별시 중구 세종대로 110"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['documents']:
    result = data['documents'][0]
    address = result['address']

    print(f"주소명: {address['address_name']}")
    print(f"위도: {address['y']}")
    print(f"경도: {address['x']}")
    print(f"우편번호: {address.get('zip_code', '')}")
else:
    print("검색 결과가 없습니다.")
```

**응답 예시:**
```json
{
  "meta": {
    "total_count": 1
  },
  "documents": [
    {
      "address_name": "서울 중구 태평로1가 31",
      "address_type": "REGION_ADDR",
      "x": "126.97839076050163",
      "y": "37.56682095214089",
      "address": {
        "address_name": "서울 중구 태평로1가 31",
        "region_1depth_name": "서울",
        "region_2depth_name": "중구",
        "region_3depth_name": "태평로1가",
        "mountain_yn": "N",
        "main_address_no": "31",
        "sub_address_no": "",
        "zip_code": "04520"
      },
      "road_address": {
        "address_name": "서울 중구 세종대로 110",
        "region_1depth_name": "서울",
        "region_2depth_name": "중구",
        "region_3depth_name": "태평로1가",
        "road_name": "세종대로",
        "underground_yn": "N",
        "main_building_no": "110",
        "sub_building_no": "",
        "building_name": "서울특별시청",
        "zone_no": "04524"
      }
    }
  ]
}
```

#### 키워드 검색

```python
url = "https://dapi.kakao.com/v2/local/search/keyword.json"

params = {
    "query": "카페",
    "category_group_code": "CE7",  # 카테고리 (CE7=카페, FD6=음식점)
    "x": "126.9780",               # 중심 경도
    "y": "37.5665",                # 중심 위도
    "radius": "1000",              # 반경 (m)
    "sort": "distance"             # 정렬 (distance=거리순, accuracy=정확도순)
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

for place in data['documents']:
    print(f"장소명: {place['place_name']}")
    print(f"주소: {place['address_name']}")
    print(f"거리: {place['distance']}m")
    print(f"전화: {place.get('phone', '')}\n")
```

**카테고리 그룹 코드:**
| 코드 | 카테고리 |
|-----|---------|
| MT1 | 대형마트 |
| CS2 | 편의점 |
| PS3 | 어린이집, 유치원 |
| SC4 | 학교 |
| AC5 | 학원 |
| PK6 | 주차장 |
| OL7 | 주유소, 충전소 |
| SW8 | 지하철역 |
| BK9 | 은행 |
| CT1 | 문화시설 |
| AG2 | 중개업소 |
| PO3 | 공공기관 |
| AT4 | 관광명소 |
| AD5 | 숙박 |
| FD6 | 음식점 |
| CE7 | 카페 |
| HP8 | 병원 |
| PM9 | 약국 |

---

### 2. 네이버 지도 (네이버 클라우드)

**API 문서:** https://www.ncloud.com/product/applicationService/maps

#### Geocoding (주소 → 좌표)

```python
import requests

client_id = "발급받은_Client_ID"
client_secret = "발급받은_Client_Secret"

url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"

headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret
}

params = {
    "query": "서울특별시 중구 세종대로 110"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['status'] == 'OK' and data['addresses']:
    result = data['addresses'][0]
    print(f"주소: {result['roadAddress']}")
    print(f"위도: {result['y']}")
    print(f"경도: {result['x']}")
```

#### Reverse Geocoding (좌표 → 주소)

```python
url = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"

params = {
    "coords": "126.9780,37.5665",  # 경도,위도
    "orders": "roadaddr,addr",     # 도로명주소,지번주소
    "output": "json"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['status']['code'] == 0:
    result = data['results'][0]
    region = result['region']
    land = result['land']

    print(f"도로명주소: {result.get('roadAddress', '')}")
    print(f"지번주소: {land.get('address', '')}")
    print(f"우편번호: {land.get('zipcode', '')}")
```

#### Directions 5 (경로 탐색)

```python
url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"

params = {
    "start": "126.9780,37.5665",   # 출발지 (경도,위도)
    "goal": "129.0756,35.1796",    # 목적지 (경도,위도)
    "option": "trafast"             # 경로 옵션 (trafast=실시간빠른길)
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['code'] == 0:
    route = data['route']['trafast'][0]
    summary = route['summary']

    print(f"거리: {summary['distance']/1000:.1f}km")
    print(f"소요시간: {summary['duration']//60000}분")
    print(f"택시요금: {summary['taxiFare']:,}원")
    print(f"통행료: {summary['tollFare']:,}원")
```

**경로 옵션:**
| 옵션 | 설명 |
|-----|------|
| trafast | 실시간 빠른 길 |
| tracomfort | 실시간 편한 길 |
| traoptimal | 실시간 최적 |
| traavoidtoll | 무료 우선 |
| traavoidcaronly | 자동차 전용 도로 회피 |

---

## 💵 금융 & 결제 API

### 1. 금융결제원 오픈뱅킹

**API 문서:** https://openapi.kftc.or.kr/

#### OAuth 2.0 인증 흐름

**1단계: 사용자 인증 (Authorization Code 방식)**

```python
import requests
from urllib.parse import urlencode

client_id = "발급받은_Client_ID"
redirect_uri = "http://localhost:8080/callback"

# 사용자 인증 URL 생성
auth_params = {
    "response_type": "code",
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "scope": "login inquiry transfer",
    "state": "random_string_12345",
    "auth_type": "0"  # 0=최초인증, 2=재인증
}

auth_url = f"https://testapi.openbanking.or.kr/oauth/2.0/authorize?{urlencode(auth_params)}"
print(f"사용자를 이 URL로 리다이렉트: {auth_url}")

# 사용자 인증 후 redirect_uri로 code가 전달됨
# http://localhost:8080/callback?code=AUTHORIZATION_CODE&state=random_string_12345
```

**2단계: Access Token 발급**

```python
client_secret = "발급받은_Client_Secret"
authorization_code = "받은_AUTHORIZATION_CODE"

token_url = "https://testapi.openbanking.or.kr/oauth/2.0/token"

data = {
    "code": authorization_code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "grant_type": "authorization_code"
}

response = requests.post(token_url, data=data)
token_data = response.json()

access_token = token_data['access_token']
refresh_token = token_data['refresh_token']
user_seq_no = token_data['user_seq_no']

print(f"Access Token: {access_token}")
print(f"유효기간: {token_data['expires_in']}초")
```

**응답 예시:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 7776000,
  "scope": "inquiry transfer",
  "user_seq_no": "1100001234"
}
```

**3단계: 사용자 등록 계좌 조회**

```python
url = "https://testapi.openbanking.or.kr/v2.0/account/list"

headers = {
    "Authorization": f"Bearer {access_token}"
}

params = {
    "user_seq_no": user_seq_no,
    "include_cancel_yn": "N",  # 해지계좌 포함 여부
    "sort_order": "D"          # 정렬 (D=내림차순, A=오름차순)
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['rsp_code'] == 'A0000':
    res_list = data['res_list']
    for account in res_list:
        print(f"은행: {account['bank_name']}")
        print(f"계좌번호: {account['account_num']}")
        print(f"핀테크이용번호: {account['fintech_use_num']}\n")
```

**4단계: 잔액 조회**

```python
url = "https://testapi.openbanking.or.kr/v2.0/account/balance/fin_num"

fintech_use_num = "핀테크이용번호"
bank_tran_id = "M202311151U" + user_seq_no[:9]  # 기관거래고유번호
tran_dtime = datetime.now().strftime("%Y%m%d%H%M%S")

params = {
    "bank_tran_id": bank_tran_id,
    "fintech_use_num": fintech_use_num,
    "tran_dtime": tran_dtime
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['rsp_code'] == 'A0000':
    print(f"계좌잔액: {int(data['balance_amt']):,}원")
    print(f"출금가능금액: {int(data['available_amt']):,}원")
```

**5단계: 거래내역 조회**

```python
url = "https://testapi.openbanking.or.kr/v2.0/account/transaction_list/fin_num"

from_date = "20250101"
to_date = "20251115"

params = {
    "bank_tran_id": bank_tran_id,
    "fintech_use_num": fintech_use_num,
    "inquiry_type": "A",        # A=All, I=입금, O=출금
    "inquiry_base": "D",        # D=일자, T=시간
    "from_date": from_date,
    "to_date": to_date,
    "sort_order": "D",
    "tran_dtime": tran_dtime
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['rsp_code'] == 'A0000':
    res_list = data['res_list']
    for txn in res_list:
        tran_date = txn['tran_date']
        tran_type = txn['tran_type']
        inout_type = "출금" if txn['inout_type'] == "O" else "입금"
        tran_amt = int(txn['tran_amt'])
        after_balance = int(txn['after_balance_amt'])

        print(f"{tran_date} {inout_type} {tran_amt:,}원 (잔액: {after_balance:,}원)")
```

**6단계: 출금이체**

```python
url = "https://testapi.openbanking.or.kr/v2.0/transfer/withdraw/fin_num"

data = {
    "bank_tran_id": bank_tran_id,
    "cntr_account_type": "N",
    "cntr_account_num": "1234567890",
    "dps_print_content": "입금표시내용",
    "fintech_use_num": fintech_use_num,
    "wd_print_content": "출금표시내용",
    "tran_amt": "10000",
    "tran_dtime": tran_dtime,
    "req_client_name": "홍길동",
    "req_client_fintech_use_num": fintech_use_num,
    "req_client_num": "HONGGILDONG1234",
    "transfer_purpose": "TR",   # TR=송금
    "recv_client_name": "김철수",
    "recv_client_bank_code": "097",
    "recv_client_account_num": "1234567890"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result['rsp_code'] == 'A0000':
    print(f"이체 성공: {result['wd_limit_remain_amt']}원 남음")
else:
    print(f"이체 실패: {result['rsp_message']}")
```

---

### 2. 한국투자증권 KIS API

**API 문서:** https://apiportal.koreainvestment.com/

#### OAuth 토큰 발급

```python
import requests
import json

APP_KEY = "발급받은_APP_KEY"
APP_SECRET = "발급받은_APP_SECRET"
BASE_URL = "https://openapi.koreainvestment.com:9443"  # 실전투자

token_url = f"{BASE_URL}/oauth2/tokenP"

headers = {
    "content-type": "application/json"
}

data = {
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
}

response = requests.post(token_url, headers=headers, data=json.dumps(data))
token_data = response.json()

access_token = token_data['access_token']
print(f"Access Token: {access_token}")
print(f"유효기간: {token_data['expires_in']}초")
```

#### 국내 주식 현재가 조회

```python
url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

headers = {
    "content-type": "application/json; charset=utf-8",
    "authorization": f"Bearer {access_token}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET,
    "tr_id": "FHKST01010100"  # 거래ID (현재가 조회)
}

params = {
    "fid_cond_mrkt_div_code": "J",  # 시장분류코드 (J=주식)
    "fid_input_iscd": "005930"      # 종목코드 (005930=삼성전자)
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['rt_cd'] == '0':
    output = data['output']
    print(f"종목명: {output['prdt_name']}")
    print(f"현재가: {int(output['stck_prpr']):,}원")
    print(f"전일대비: {output['prdy_vrss_sign']} {int(output['prdy_vrss']):,}원")
    print(f"등락률: {float(output['prdy_ctrt']):.2f}%")
    print(f"거래량: {int(output['acml_vol']):,}주")
```

#### 국내 주식 호가 조회

```python
url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"

headers['tr_id'] = "FHKST01010200"  # 호가 조회

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data['rt_cd'] == '0':
    output = data['output1']

    # 매도 호가
    print("=== 매도 호가 ===")
    for i in range(10, 0, -1):
        askp = int(output[f'askp{i}'])
        askp_rsqn = int(output[f'askp_rsqn{i}'])
        print(f"{askp:,}원 - {askp_rsqn:,}주")

    # 매수 호가
    print("\n=== 매수 호가 ===")
    for i in range(1, 11):
        bidp = int(output[f'bidp{i}'])
        bidp_rsqn = int(output[f'bidp_rsqn{i}'])
        print(f"{bidp:,}원 - {bidp_rsqn:,}주")
```

#### 주식 주문 (매수)

```python
url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"

headers['tr_id'] = "TTTC0802U"  # 현금 매수 주문

CANO = "계좌번호앞8자리"
ACNT_PRDT_CD = "계좌번호뒤2자리"

data = {
    "CANO": CANO,
    "ACNT_PRDT_CD": ACNT_PRDT_CD,
    "PDNO": "005930",        # 종목코드
    "ORD_DVSN": "00",        # 주문구분 (00=지정가, 01=시장가)
    "ORD_QTY": "10",         # 주문수량
    "ORD_UNPR": "70000",     # 주문단가
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result['rt_cd'] == '0':
    print(f"주문번호: {result['output']['KRX_FWDG_ORD_ORGNO']}")
    print(f"주문시각: {result['output']['ORD_TMD']}")
else:
    print(f"주문 실패: {result['msg1']}")
```

**주문 구분 코드:**
| 코드 | 설명 |
|-----|------|
| 00 | 지정가 |
| 01 | 시장가 |
| 02 | 조건부지정가 |
| 03 | 최유리지정가 |
| 04 | 최우선지정가 |
| 05 | 장전 시간외 |
| 06 | 장후 시간외 |
| 07 | 시간외 단일가 |

---

## 🤖 AI & 머신러닝 API

### 1. 네이버 CLOVA Studio

**API 문서:** https://api.ncloud-docs.com/docs/ai-naver-clovastudio

#### Completion (텍스트 생성)

```python
import requests
import json

API_KEY = "발급받은_API_KEY"
API_KEY_PRIMARY_VAL = "발급받은_Primary_Key"
REQUEST_ID = "고유_요청_ID"

url = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"

headers = {
    "X-NCP-CLOVASTUDIO-API-KEY": API_KEY,
    "X-NCP-APIGW-API-KEY": API_KEY_PRIMARY_VAL,
    "X-NCP-CLOVASTUDIO-REQUEST-ID": REQUEST_ID,
    "Content-Type": "application/json; charset=utf-8"
}

data = {
    "messages": [
        {
            "role": "system",
            "content": "당신은 친절한 AI 어시스턴트입니다."
        },
        {
            "role": "user",
            "content": "한국의 수도는 어디인가요?"
        }
    ],
    "topP": 0.8,
    "topK": 0,
    "maxTokens": 256,
    "temperature": 0.5,
    "repeatPenalty": 5.0,
    "stopBefore": [],
    "includeAiFilters": True
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result['status']['code'] == '20000':
    message = result['result']['message']
    print(f"응답: {message['content']}")
    print(f"사용 토큰: {result['result']['inputLength']} (입력) + {result['result']['outputLength']} (출력)")
else:
    print(f"에러: {result['status']['message']}")
```

#### 요약 (Summarization)

```python
url = "https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize"

headers = {
    "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
    "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
    "Content-Type": "application/json"
}

text = """
긴 텍스트 내용...
여러 문단으로 구성된 긴 글을 입력합니다.
"""

data = {
    "document": {
        "content": text
    },
    "option": {
        "language": "ko",
        "model": "news",
        "tone": "2",        # 0=formal, 1=informal, 2=both
        "summaryCount": 3   # 요약 문장 수
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(f"요약: {result['summary']}")
```

---

### 2. Upstage Solar API

**API 문서:** https://developers.upstage.ai/

#### Chat Completion

```python
import requests

API_KEY = "발급받은_API_KEY"
url = "https://api.upstage.ai/v1/solar/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "solar-1-mini-chat",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "한국의 전통 음식을 3가지 알려주세요."
        }
    ],
    "max_tokens": 500,
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(result['choices'][0]['message']['content'])
```

#### Document AI (OCR)

```python
url = "https://api.upstage.ai/v1/document-ai/ocr"

files = {
    'document': open('document.pdf', 'rb')
}

response = requests.post(url, headers=headers, files=files)
result = response.json()

for page in result['pages']:
    print(f"페이지 {page['id']}:")
    for word in page['words']:
        print(f"  {word['text']} (신뢰도: {word['confidence']:.2f})")
```

---

이어서 나머지 카테고리들을 작성하겠습니다. 문서가 너무 길어서 분할하여 작성하겠습니다.

이 문서는 계속 업데이트됩니다...

---

**다음 파트:** 교통, 의료, 쇼핑, 게임, 소셜 API 등

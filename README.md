# <img src="./assets/public-api-icon.png" width="50" height="50"/> Public API - kr

[![Link Health Check](https://github.com/yybmion/public-apis-4Kr/actions/workflows/link_health_check.yml/badge.svg)](https://github.com/yybmion/public-apis-4Kr/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Korean APIs](https://img.shields.io/badge/Korean%20APIs-260+-blue.svg)](https://github.com/yybmion/public-apis-4Kr)
[![Global APIs](https://img.shields.io/badge/Global%20APIs-780+-blue.svg)](https://github.com/yybmion/public-apis-4Kr/blob/main/GLOBAL_PUBLIC_APIS_KR.md)

🇺🇸 [English](./README_EN.md) | 🇰🇷 [한국어](./README.md) | 🌏 [글로벌 public API](./GLOBAL_PUBLIC_APIS_KR.md)


이 프로젝트는 한국에서 개발자들이 활용할 수 있는 모든 **공개 API**를 체계적으로 정리한 목록입니다.


2026년 최신 정보로 업데이트되었으며, 앞으로도 주기적으로 업데이트 할 예정입니다.

> ### 🌍 글로벌 API 리소스
>
> 한국 API 외에도 전세계의 다양한 Public API를 찾고 계신가요?
>
> 👉 [Global Public APIs 문서](./GLOBAL_PUBLIC_APIS_KR.md)를 참고해주세요!

## 목차

- [🏛 정부 & 공공기관](#정부--공공기관)
- [🗺 지도 & 위치](#지도--위치)
- [📍 지역별 공공데이터](#지역별-공공데이터)
- [💵 금융 & 결제](#금융--결제)
- [📱 통신사](#통신사)
- [🚗 교통](#교통)
- [☀️ 날씨 & 환경](#날씨--환경)
- [🏥 의료 & 보건](#의료--보건)
- [🎓 교육](#교육)
- [🏘 부동산](#부동산)
- [🎭 문화 & 관광](#문화--관광)
- [📊 통계 & 데이터](#통계--데이터)
- [🤖 AI & 머신러닝](#ai--머신러닝)
- [🛍 쇼핑 & 이커머스](#쇼핑--이커머스)
- [📦 배송 & 물류](#배송--물류)
- [🍔 음식 & 음료](#음식--음료)
- [🎮 게임 & 엔터테인먼트](#게임--엔터테인먼트)
- [📺 미디어 & 콘텐츠](#미디어--콘텐츠)
- [💬 소셜 & 커뮤니케이션](#소셜--커뮤니케이션)
- [⚡ 에너지 & 전력](#에너지--전력)
- [🔬 과학 & 연구](#과학--연구)
- [💼 비즈니스 & 기업](#비즈니스--기업)
- [☁️ 클라우드 서비스](#클라우드-서비스)
- [🔗 블록체인](#블록체인)
- [🏠 IoT & 스마트홈](#iot--스마트홈)
- [💰 암호화폐 거래소](#암호화폐-거래소)
- [⚖️ 법률](#️법률)
- [🔒 보안](#보안)
- [🚨 공공안전](#공공안전)
- [✈️ 항공](#항공)
- [🚛 물류 인프라 & 통관](#물류-인프라--통관)
- [🌾 농수산](#농수산)
- [📈 생활경제](#생활경제)
- [🏦 재정 & 예산](#재정--예산)
- [<img src="./assets/logo-naver.png" width="16" height="16"/> 네이버](#네이버)
- [<img src="./assets/logo-kakao.png" width="16" height="16"/> 카카오](#카카오)

### 정부 & 공공기관

| API                                                                                                              | 설명                                                               | 인증       |
|------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|----------|
| [공공데이터포털](https://www.data.go.kr/)                                                                               | 정부 및 공공기관의 모든 데이터를 통합 제공하는 중앙 플랫폼 (10만개 이상 데이터셋)                 | `apiKey` |
| [국가기록원 검색 API](https://www.archives.go.kr/next/newsearch/openAPI01.do)                                           | 나라기록물 검색서비스, RSS 형식 제공 (일 1000건 제한)                              | `apiKey` |
| [국가지표통합 공유서비스](https://www.index.go.kr/unity/openApi/openApiIntro.do)                                            | 국가 통계포털 ‘지표누리’가 각종 공공 통계지표 제공                                    | `apiKey` |
| [국토교통부 실거래가](https://www.data.go.kr/dataset/3050988/openapi.do)                                                  | 아파트, 오피스텔, 단독다가구 등 실거래가 정보                                       | `apiKey` |
| [기상청 단기예보](https://www.data.go.kr/data/15084084/openapi.do)                                                      | 초단기실황, 초단기예보, 단기예보 정보 제공                                         | `apiKey` |
| [기상청 생활기상지수](https://data.kma.go.kr/api/selectApiList.do?pgmNo=42)                                               | 자외선지수, 대기정체지수, 체감온도 등 생활기상정보                                     | `apiKey` |
| [기상청 중기예보](https://www.data.go.kr/data/15059468/openapi.do)                                                      | 중기 기상예보 정보 조회 서비스                                                | `apiKey` |
| [농림축산식품부](https://data.mafra.go.kr/main.do)                                                                      | 농촌, 농업, 축산, 유통소비 등 데이터 제공                                        | `apiKey` |
| [마이데이터 통합지원 API](https://www.kdata.or.kr/mydata)                                                                 | 한국데이터산업진흥원 마이데이터 표준 API 서비스                                      | `OAuth`  |
| [문화체육관광부 문화정보](https://www.culture.go.kr/data/openapi/openapiInfo.do)                                            | 공연, 전시, 문화재, 도서관 등 문화정보                                          | `apiKey` |
| [보건복지부](https://www.mohw.go.kr/menu.es?mid=a10104010100)                                                         | 보건복지부의 정책, 법령, 재정, 감사, 연구정보 등 제공                                 | `OAuth`  |
| [소상공인 365 API](https://bigdata.sbiz.or.kr/#/apiMain/dataApi/intro)                                               | 전국 상가업소 조회                                                       | `apiKey` |
| [열린국회정보 확장 API](https://open.assembly.go.kr/portal/openapi/main.do)                                              | 국회의원 표결정보, 발의법률안, 의안 상세정보, 연구보고서                                 | `apiKey` |
| [예금보험공사](https://www.data.go.kr/tcs/dss/selectDataSetList.do?org=예금보험공사)                                         | 금융기관 예금자보호 및 영업정지저축은행 정보                                         | `apiKey` |
| [지방행정 인허가 데이터 개방](https://www.localdata.go.kr/main.do)                                                           | 전국 자치단체 인허가 데이터셋 (동물, 의료, 문화, 생활 등) 26.4.15부로 폐쇄 (공공데이터 포털에서 제공) | `apiKey` |
| [정부24 공공서비스 API](https://www.gov.kr/openapi/info)                                                                | 정부 공공서비스 정보 오픈API, 실시간 행정정보 제공                                   | `apiKey` |
| [정책정보포털 POINT](https://policy.nl.go.kr/pages/point/api.jsp)                                                      | 최신정책동향, 온라인 정부간행물, 정책정보종합목록 제공                                   | `apiKey` |
| [초록누리 Open API](https://ecolife.me.go.kr/ecolife/infoCenter/openApi)                                             | 환경부 환경정보 및 친환경 생활정보 제공                                           | `apiKey` |
| [키프리스 플러스 API](https://plus.kipris.or.kr/portal/data/service/List.do?subTab=SC001&amp;entYn=N&amp;menuNo=200100) | 특허·상표·디자인 등 지식재산권 정보 검색                                          | `apiKey` |
| [통계청 KOSIS](https://kosis.kr/serviceInfo/openAPIGuide.do)                                                        | 국가통계포털의 134,586종 통계자료                                            | `apiKey` |
| [한국관광공사 TourAPI](https://api.visitkorea.or.kr/)                                                                  | 관광지, 숙박, 음식점, 축제 등 관광정보                                          | `apiKey` |
| [한국도로공사 교통정보](https://www.data.go.kr/data/15076872/openapi.do)                                                   | 실시간 고속도로 교통량 및 교통정보                                              | `apiKey` |
| [한국산업인력공단 HRD](https://openapi.hrdkorea.or.kr/main)                                                              | 국가자격, 과정평가형자격, 일학습병행자격 정보 제공                                     | `apiKey` |
| [한국철도공사 열차운행정보](https://www.data.go.kr/data/15125762/openapi.do)                                                 | KTX, 새마을호 등 열차 운행정보                                              | `apiKey` |
| [한국토지주택공사(LH)](https://www.data.go.kr/tcs/dss/selectDataSetList.do?org=한국토지주택공사)                                 | 분양임대공고, 사전청약, 임대주택 정보                                            | `apiKey` |
| [한국환경공단 에어코리아](https://www.data.go.kr/data/15073861/openapi.do)                                                  | 실시간 대기오염정보 및 미세먼지 데이터                                            | `apiKey` |
| [행정안전부 행정표준코드](https://www.data.go.kr/data/15077871/openapi.do)                                                  | 법정동코드, 행정구역코드 등 표준코드 정보                                          | `apiKey` |
| [환경공간정보서비스 지도 API](https://egis.me.go.kr/api/intro.do)                                                           | 환경부 토지피복지도, 환경주제도, 생태자연도 공간정보                                    | `apiKey` |
| [NTIS 국가과학기술정보](https://www.ntis.go.kr/rndopen/api/mng/apiMain.do)                                               | 국가R&D 과제정보, 성과정보 메타데이터 검색                                        | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 지도 & 위치

| API                                                              | 설명                                   | 인증     |
|------------------------------------------------------------------|--------------------------------------| -------- |
| [국토정보플랫폼](https://map.ngii.go.kr/mi/openKey/openKeyInfo.do)      | 수치지도, 항공사진, 정사영상, DEM, 국가관심지점(POI)   | `apiKey` |
| [네이버 지도](https://www.ncloud.com/product/applicationService/maps) | 지도 API, Geocoding, Directions, 파노라마  | `apiKey` |
| [브이월드](https://www.vworld.kr/v4po_openapi_s001.do)               | 국토지리정보원의 3D 지도 및 공간정보                | `apiKey` |
| [주소기반산업지원서비스](https://business.juso.go.kr)                       | 도로명주소 API / DB 제공 및 국가지점정보 등 제공      | `apiKey` |
| [카카오맵](https://apis.map.kakao.com/web/guide/)                    | 지도 표시, 장소 검색, 좌표 변환, 경로 탐색           | `apiKey` |
| [T맵 API](https://openapi.sk.com/)                                | SK텔레콤의 내비게이션 및 경로 탐색 API             | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 지역별 공공데이터

| API                                                                              | 설명                      | 인증       |
|----------------------------------------------------------------------------------|-------------------------|----------|
| [경기 데이터드림](https://data.gg.go.kr)                                                | 경기도 및 시·군 공공데이터         | `apiKey` |
| [경남 빅데이터허브](https://bigdata.gyeongnam.go.kr)                                     | 경상남도 공공데이터              | `apiKey` |
| [경북 공공데이터 포털](https://www.gb.go.kr/Main/open_contents/section/data/index.html)   | 경상북도 공공데이터              | `apiKey` |
| [광주 공공데이터포털](https://www.gjcity.go.kr/bigdata/)                                  | 광주광역시 공공데이터             | `apiKey` |
| [대구 공공데이터 포털](https://data.daegu.go.kr)                                          | 대구광역시 생활, 교통, 관광 등      | `apiKey` |
| [대전 데이터포털](https://bigdata.daejeon.go.kr/)                                       | 대전광역시 도시, 교통, 환경 등      | `apiKey` |
| [부산 공공데이터 포털](https://data.busan.go.kr)                                          | 부산광역시 버스, 지하철, 문화, 안전 등 | `apiKey` |
| [서울 열린데이터광장](https://data.seoul.go.kr)                                           | 서울특별시 교통, 환경, 시설, 복지 등  | `apiKey` |
| [세종 데이터포털](https://www.sejong.go.kr/stat/index.do)                               | 세종특별자치시 행정, 생활 데이터      | `apiKey` |
| [울산 데이터포털](https://data.ulsan.go.kr)                                             | 울산광역시 산업, 환경 등          | `apiKey` |
| [인천 데이터포털](https://data.incheon.go.kr)                                           | 인천광역시 공공데이터             | `apiKey` |
| [전남 공공데이터포털](https://data.jeonnam.go.kr)                                         | 전라남도 공공데이터              | `apiKey` |
| [전북 공공데이터 포털](https://www.bigdatahub.go.kr/index.jeonbuk)                        | 전북특별자치도 공공데이터           | `apiKey` |
| [제주 공공데이터포털](https://www.jejudatahub.net/)                                       | 제주특별자치도 공공데이터           | `apiKey` |
| [충남 데이터포털 올담](https://alldam.chungnam.go.kr)                                     | 충청남도 공공데이터              | `apiKey` |
| [충북 공공데이터 포털](https://data.chungbuk.go.kr)                                       | 충청북도 공공데이터              | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 금융 & 결제

| API                                                                   | 설명                                     | 인증          |
| --------------------------------------------------------------------- |----------------------------------------| ------------- |
| [금융결제원 오픈뱅킹](https://openapi.kftc.or.kr/service/openBanking) | 19개+ 은행 통합 계좌조회, 이체, 결제 서비스            | `OAuth`       |
| [네이버페이 API](https://developers.pay.naver.com/)                   | 네이버페이 결제, 정기결제, 자동결제 API               | `OAuth`       |
| [부트페이 API](https://docs.bootpay.co.kr/)                           | 통합 PG 연동 서비스, 이니시스·KCP·다날 등 다중 PG사 지원  | `apiKey`      |
| [삼성페이 API](https://developer.samsung.com/pay)                     | 모바일 결제 및 디지털 지갑 서비스                    | `Partnership` |
| [신한은행 Open API](https://openapi.shinhan.com/)                     | 신한금융그룹 통합 API 서비스                      | `OAuth`       |
| [우리은행 Open API](https://developer.wooribank.com/apiservice)       | 핀테크 개발자 원스탑 지원 서비스                     | `OAuth`       |
| [카카오페이](https://developers.kakaopay.com/)                        | 온라인 결제, 정기결제, 송금 등 종합 결제 솔루션           | `OAuth`       |
| [토스페이 API](https://docs-pay.toss.im/reference)                    | 토스를 통한 결제 서비스 API (TLS 1.2+ 필수)        | `apiKey`      |
| [토스페이먼츠](https://docs.tosspayments.com/reference)               | 통합 결제 API (카드, 가상계좌, 간편결제)             | `apiKey`      |
| [페이코(PAYCO)](https://developers.payco.com/guide)                   | NHN 통합 ID 및 멤버십 연동 서비스                 | `OAuth`       |
| [페이플 API](https://developer.payple.kr/)                            | 간편결제, 정기결제, 링크결제 서비스                   | `apiKey`      |
| [하나금융그룹 Open API](https://www.hanafnapimarket.com/)             | 하나금융그룹 API 마켓플레이스                      | `OAuth`       |
| [하이픈 API 마켓플레이스](https://hyphen.im/)                         | 케이에스넷 자회사 데이터 API 마켓플레이스 (500개 이상 API) | `apiKey`      |
| [한국수출입은행 Open API](https://www.koreaexim.go.kr/ir/HPHKIR019M01) | 현재환율, 대출금리, 국제금리 정보                    | `apiKey` |
| [한국은행 Open API](https://ecos.bok.or.kr/api/)                      | 경제통계정보 제공 API                          | `apiKey`      |
| [한국투자증권 KIS API](https://apiportal.koreainvestment.com/intro)   | 국내외 주식 시세 및 주문 API                     | `OAuth`       |
| [CODEF API](https://developer.codef.io/)                              | 금융, 보험, 통신 데이터 통합 연동                   | `OAuth`       |
| [KB API 포탈](https://apiportal.kbfg.com/)                            | KB금융그룹 종합 금융 API 서비스 (800+ API 제공)     | `OAuth`       |
| [KB국민은행 Open API](https://obizapi.kbstar.com/quics?page=C108082)  | KB 종합 금융서비스 및 BaaS 플랫폼                 | `OAuth`       |
| [NH농협은행 Open API](https://developers.nonghyup.com/center/CE_1020) | 농협 금융 API 개발자센터                        | `OAuth`       |

**[⬆ 목차로 돌아가기](#목차)**

### 통신사

| API                                                         | 설명                                        | 인증     |
| ----------------------------------------------------------- | ------------------------------------------- | -------- |
| [KT API Link](https://apilink.kt.co.kr/)                    | Geo Master, Cloud API, GiGA Genie AI        | `apiKey` |
| [SK텔레콤 Open API](https://openapi.sk.com/)                | T맵, NUGU, AI/IoT 플랫폼 46개 API           | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 교통

| API                                                                                           | 설명                                              | 인증     |
| --------------------------------------------------------------------------------------------- | ------------------------------------------------- | -------- |
| [경기도 버스정보](https://www.data.go.kr/data/15058012/openapi.do)                             | 경기도 시내/시외버스 실시간 정보                  | `apiKey` |
| [국토교통부 교통소통정보](https://www.data.go.kr/data/15040463/openapi.do?recommendDataYn=Y)   | 고속도로 및 국도 실시간 속도정보                  | `apiKey` |
| [기아자동차 Developers](https://developers.kia.com/)                                          | KIA Connect 차량 데이터 및 운행정보               | `OAuth`  |
| [따릉이(서울자전거)](https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do)            | 서울시 공공자전거 실시간 대여정보                 | `apiKey` |
| [레일포털(KRIC)](https://data.kric.go.kr/rips/serviceInfo/openapi/introduce.do)               | 철도산업정보센터 전국 철도 정보                   | `apiKey` |
| [서울 TOPIS 교통정보](https://topis.seoul.go.kr/refRoom/openRefRoom_4.do)                      | 서울시 다양한 교통정보, 비영리 목적 활용          | `apiKey` |
| [서울교통공사 역간거리](https://www.data.go.kr/data/15057802/openapi.do)                       | 지하철 역간거리 및 소요시간 정보                  | `apiKey` |
| [서울시 버스 도착정보](http://api.bus.go.kr/contents/sub01/wisOpenApi.html)                    | 서울시 시내버스 실시간 도착정보                   | `apiKey` |
| [서울시 지하철 실시간 도착정보](https://data.seoul.go.kr/dataList/OA-12764/A/1/datasetView.do) | 서울 지하철 2~8호선 실시간 도착정보               | `apiKey` |
| [카카오T 비즈니스](https://kakaotbusinessapiinfo.oopy.io/)                                     | 업무용 카카오T 이용내역 연동 서비스               | `apiKey` |
| [카카오모빌리티 길찾기](https://developers.kakaomobility.com/product/api)                      | 모빌리티 서비스 개발용 기술제품                   | `apiKey` |
| [한국도로공사 실시간 교통량](https://www.data.go.kr/data/15076872/openapi.do)                  | 고속도로 실시간 영업소별 교통량 정보              | `apiKey` |
| [현대자동차 Developers](https://developers.hyundai.com/)                                      | 차량 제원, 운행정보, 주행거리, 차량상태, 운전습관 | `OAuth`  |
| [ODsay 대중교통 API](https://lab.odsay.com/guide/guide)                                       | 전국 대중교통, 고속버스, 항공편 통합 정보         | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 날씨 & 환경

| API                                                                               | 설명                           | 인증        |
|-----------------------------------------------------------------------------------|------------------------------|-----------|
| [기상청 API허브](https://apihub.kma.go.kr/)                                            | 관측·예보·위성·레이더 등 12개 분야 기상데이터  | `apiKey` |
| [기상청 동네예보](https://www.data.go.kr/dataset/15000099/openapi.do)                    | 읍면동 단위 동네예보 3시간 간격 제공        | `apiKey`  |
| [기상청 중기예보](https://www.data.go.kr/data/15059468/openapi.do)                       | 단기예보 이후 향후 11일까지의 기상전망 제공    | `apiKey`  |
| [대기질정보 서비스](https://www.data.go.kr/data/15028236/openapi.do)                      | 연돌기준, 대기질분야 조사·예측 정보 및 공간정보 제공 | `apiKey`  |
| [동식물상정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_11.html)     | 동식물상 조사 정보 및 생태계 보전 관련 정보    | `apiKey`  |
| [사업구역정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_15.html)     | 환경영향평가 사업구역 정보 제공            | `apiKey`  |
| [소음진동정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_13.html)     | 소음·진동 조사·예측 정보 제공            | `apiKey`  |
| [수리수문정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_06.html)     | 수리수문분야 조사·예측 정보 제공           | `apiKey`  |
| [수질정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_05.html)       | 수질조사 개요·조사·예측 정보 및 조사지점 공간정보 | `apiKey`  |
| [악취정보 서비스](https://www.data.go.kr/data/15083164/fileData.do)                      | 악취분야 조사·예측 속성정보 및 조사지점 공간정보 제공 | `apiKey`  |
| [에어코리아 대기오염 예보정보](https://www.data.go.kr/data/15109350/openapi.do)                | 미세먼지, 초미세먼지, 오존 예보           | `apiKey`  |
| [에어코리아 실시간 대기오염정보](https://www.data.go.kr/data/15073861/openapi.do)               | 시도별 실시간 대기질 측정정보             | `apiKey`  |
| [온실가스정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_02.html)     | 환경영향평가 사업의 온실가스 조사·예측 정보 제공  | `apiKey`  |
| [위생공중보건정보 서비스](https://www.data.go.kr/data/15028239/openapi.do)                   | 위생공중보건분야 조사 속성정보(스타이렌, 염화수소 등) | `apiKey`  |
| [인구주거정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_14.html)     | 인구 및 주거 관련 정보 제공             | `apiKey`  |
| [전국전기차충전소표준데이터](https://www.data.go.kr/data/15013115/standard.do)                 | 충전소 구분, 위치, 운영시간, 충전기 상태 등   | `apiKey`  |
| [전기차충전기정보](https://chargeinfo.ksga.org/front/cs/api/infomation)                   | 충전 사업자 충전소 위치 및 충전기 상태       | `apiKey`  |
| [지형지질정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_10.html)     | 개요·조사·광산·지질도·능선축·표고·경사 정보 제공 | `apiKey`  |
| [친환경적자원순환정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_12.html) | 친환경적 자원순환 관련 정보 제공           | `apiKey`  |
| [토양정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_09.html)       | 토양 기본정보 및 조사 정보 제공           | `apiKey`  |
| [토지이용정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_08.html)     | 토지이용 현황 및 계획 정보 제공           | `apiKey`  |
| [한국환경공단 전기차충전소](https://www.data.go.kr/data/15076352/openapi.do)                  | 전국 전기차 충전소 정보, 충전기 상태정보      | `apiKey`  |
| [환경위성센터 API](https://nesc.nier.go.kr/ko/html/svc/openapi/explain.do)              | 환경위성(GEMS) Data, Image 자료 제공 | `apiKey` |
| [해양환경정보 서비스](https://www.eiass.go.kr/openapiguide/kei_html/chapter04_07.html)     | 해양환경분야 조사·예측 정보 제공           | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 의료 & 보건

| API                                                                            | 설명                                                    | 인증            |
|--------------------------------------------------------------------------------|-------------------------------------------------------|---------------|
| [국민건강보험공단](https://www.nhis.or.kr/nhis/together/wbhaec10800m01.do)             | 장기요양 시설 정보와 건강검진 기관 정보, 예약 및 검진 일정 정보                                       | `apiKey`      |
| [보건의료빅데이터 확장 API](https://opendata.hira.or.kr/op/opc/selectOpenApiInfoView.do) | 건강보험심사평가원 의료빅데이터 활용 Open API                          | `apiKey`      |
| [삼성헬스 SDK](https://developer.samsung.com/health)                               | 건강 데이터 읽기/쓰기 (심박수, 산소포화도, 혈당, 혈압 등)                   | `Partnership` |
| [식품의약품 데이터](https://data.mfds.go.kr/OPCAA01F01)                                | 식품·의약품·의료기기 등 국민 보건 및 안전 관련 분야의 다양한 데이터               | `apiKey`      |
| [중앙응급의료센터](https://www.e-gen.or.kr/nemc/open_api.do)                           | 병의원/약국 위치, AED 설치정보 등                                 | `apiKey`      |

**[⬆ 목차로 돌아가기](#목차)**

### 교육

| API                                                                                | 설명                           | 인증             |
|------------------------------------------------------------------------------------|------------------------------|----------------|
| [교육부 나이스 학교기본정보](https://www.data.go.kr/data/15122275/openapi.do)                  | 전국 초중고 학교 기본정보               | `apiKey`       |
| [국립국어원 우리말샘](https://opendict.korean.go.kr/service/openApiInfo)                    | 표준국어대사전, 방언, 외래어 정보          | `apiKey`       |
| [대학알리미](https://www.data.go.kr/data/15037507/openapi.do#tab_layer_detail_function) | 대학 기본정보                      | `apiKey`       |
| [커리어넷](https://www.career.go.kr/cnet/front/openapi/openApiUseGuideCenter.do)       | 진로교육 자료 및 직업정보               | `apiKey`       |
| [클래스101 Business API](https://docs.class101.net/)                                  | 클래스 관리, 수강신청, 진도율 조회, SSO 연동 | `Bearer Token` |
| [학교알리미](https://www.schoolinfo.go.kr/ng/go/pnnggo_a01_l0.do)                       | 전국 초중고 학교 기본정보               | `apiKey`       |
| [한국교육학술정보원 RISS 종합목록](https://www.data.go.kr/data/15071949/fileData.do)            | 대학 도서관 통합 학술자료 목록            | `apiKey`       |
| [한국교육학술정보원 학술연구정보](https://www.data.go.kr/data/3046254/openapi.do)                 | KERIS 학술논문, 연구정보 검색 서비스      | `apiKey`       |

**[⬆ 목차로 돌아가기](#목차)**

### 부동산

| API                                                                                       | 설명                                     | 인증     |
| ----------------------------------------------------------------------------------------- | ---------------------------------------- | -------- |
| [아파트 매매 실거래가](https://www.data.go.kr/data/15126469/openapi.do)                   | 국토교통부 아파트 매매 실거래 자료       | `apiKey` |
| [아파트 전월세 실거래가](https://www.data.go.kr/data/15126474/openapi.do)                 | 아파트 전세/월세 실거래 자료             | `apiKey` |
| [한국부동산원 부동산통계](https://www.reb.or.kr/r-one/portal/openapi/openApiIntroPage.do) | 부동산 시장동향 및 통계정보              | `apiKey` |
| [Airbnb API](https://www.airbnb.com/help/article/3418)                                    | 숙소 관리, 예약 관리 (B2B 파트너십 필수) | `OAuth`  |

**[⬆ 목차로 돌아가기](#목차)**

### 문화 & 관광

| API                                                                      | 설명                               | 인증     |
|--------------------------------------------------------------------------|----------------------------------| -------- |
| [국립중앙박물관 e뮤지엄](https://www.emuseum.go.kr/openApi)                   | 전국 박물관 소장품(유물) 정보 조회 | `apiKey` |
| [도서관 정보나루](https://www.data4library.kr/apiUtilization)                   | 전국 공공도서관에서 수집한 회원·장서·대출 데이터 등을 제공 | `apiKey` |
| [문화공공데이터광장](https://www.culture.go.kr/data/main/main.do)                 | 박물관, 미술관, 공연, 문화재 정보             | `apiKey` |
| [한국관광공사 TourAPI 4.0](https://api.visitkorea.or.kr/)                      | 관광지, 숙박, 음식점, 축제 등 관광정보          | `apiKey` |
| [한국문화정보원](https://www.kcisa.kr/kr/contents/open_openData/view.do)        | 문화콘텐츠 오픈 API                     | `apiKey` |
| [KOPIS 공연예술통합전산망](https://www.kopis.or.kr/por/cs/openapi/openApiInfo.do) | 공연정보, 공연장정보, 예매정보                | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 통계 & 데이터

| API                                                               | 설명                           | 인증        |
|-------------------------------------------------------------------|------------------------------|-----------|
| [빅카인즈(BIG KINDS)](https://www.bigkinds.or.kr/)                    | 한국언론진흥재단 뉴스 빅데이터 분석 (로그인 필요) |  `apiKey` |
| [통계청 KOSIS 통계자료](https://kosis.kr/openapi/?sso=ok)                | 국가통계 데이터 조회 서비스              | `apiKey`  |
| [한국은행 경제통계](https://ecos.bok.or.kr/api/#/)                        | 금리, 환율, 물가지수 등 경제통계          | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### AI & 머신러닝

| API                                                                                        | 설명                                   | 인증     |
|--------------------------------------------------------------------------------------------|--------------------------------------| -------- |
| [네이버 CLOVA Face Recognition](https://developers.naver.com/docs/clova/api/CFR/API_Guide.md) | 얼굴 인식 및 감정 분석                        | `apiKey` |
| [네이버 CLOVA Speech](https://www.ncloud.com/product/aiService/clovaSpeech)                   | 음성 인식 및 STT 서비스                      | `apiKey` |
| [네이버 클라우드 CLOVA Studio](https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary)     | 한국어 특화 생성형 AI 플랫폼                    | `apiKey` |
| [삼성 빅스비 API](https://developer.samsung.com/bixby)                                          | 음성 인식 및 AI 어시스턴트 통합                  | `apiKey` |
| [삼성SDS FabriX](https://www.samsungsds.com/us/ai-fabrix/fabrix.html)                        | 멀티 LLM 기업용 생성형 AI 플랫폼                | `apiKey` |
| [AI Hub](https://aihub.or.kr)                                                              | AI 학습용 데이터셋                              | `apiKey` |
| [ETRI AI Open API](https://epretx.etri.re.kr/)                                             | ETRI에서 개발된 최첨단 인공지능 기술 제공                 | `apiKey` |
| [SKT A.X 4.0](https://github.com/SKT-AI/A.X-4.0)                                           | 한국어 특화 대규모 언어모델                      | `apiKey` |
| [Upstage Document AI](https://developers.upstage.ai/)                                      | 문서 파싱, 레이아웃 분석, 정보 추출                | `apiKey` |
| [Upstage Solar LLM](https://developers.upstage.ai/)                                        | 대화형 LLM, Document AI, OCR, Embedding | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 쇼핑 & 이커머스

| API                                                                                                  | 설명                                    | 인증     |
| ---------------------------------------------------------------------------------------------------- | --------------------------------------- | -------- |
| [네이버 쇼핑 검색 API](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md)     | 네이버 쇼핑 상품 검색 서비스            | `apiKey` |
| [네이버 쇼핑인사이트 API](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) | 쇼핑 분야별 검색 트렌드 데이터          | `apiKey` |
| [네이버 커머스 API](https://apicenter.commerce.naver.com/ko/basic/commerce-api)                      | 스마트스토어 판매자 전용 상품/주문 관리 | `OAuth`  |
| [위메프 로그인](https://developer.login.wonders.work/)                                               | 위메프 로그인 OAuth 2.0 (제휴사 전용)   | `OAuth`  |
| [쿠팡 Open API](https://developers.coupangcorp.com/hc/ko)                                            | 쿠팡 파트너스 및 셀러 API               | `apiKey` |
| [11번가 Open API](https://openapi.11st.co.kr/)                                                       | 11번가 상품정보 및 주문관리 API         | `apiKey` |
| [G마켓 Open API](https://etapi.gmarket.com/pages/API-%EA%B0%80%EC%9D%B4%EB%93%9C)                    | G마켓 상품검색 및 카테고리 API          | `apiKey` |
| [G마켓/옥션 ESM Trading API](https://etapi.gmarket.com/category/%EA%B3%B5%EC%A7%80)                  | 이베이코리아 통합 판매자 도구           | `JWT`    |
| [NHN커머스 개발자센터](https://devcenter.nhn-commerce.com/)                                          | 고도몰 API 연동 및 샘플 코드 제공       | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 배송 & 물류

| API                                                                                                                                                                                                                                                  | 설명                             | 인증     |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | -------- |
| [실시간 택배조회 서비스](http://apiservice.co.kr/)                                                                                                                                                                                                   | 택배사별 실시간 배송정보 조회    | `apiKey` |
| [한진택배 배송조회](https://developers.hanjin.com/guides)                                                                                                                                                                                            | 한진택배 배송추적 서비스         | ✕        |
| [CJ대한통운 택배조회](https://development-pro.tistory.com/entry/%ED%83%9D%EB%B0%B0%EC%82%AC%EC%A1%B0%ED%9A%8C%EA%B0%81-%ED%83%9D%EB%B0%B0%EC%82%AC-%EB%B0%8F-%EB%8C%80%ED%95%9C%ED%86%B5%EC%9A%B4-API-%EC%9D%B8%ED%84%B0%ED%8E%98%EC%9D%B4%EC%8A%A4) | CJ대한통운 배송추적 API          | ✕        |
| [Delivery Tracker API](https://tracker.delivery/)                                                                                                                                                                                                    | 오픈소스 배송조회 서비스         | `apiKey` |
| [SweetTracker 스마트택배](https://tracking.sweettracker.co.kr/)                                                                                                                                                                                      | 24개 택배사 통합 배송조회 서비스 | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 음식 & 음료

| API                                                                                      | 설명                                   | 인증     |
|------------------------------------------------------------------------------------------|--------------------------------------| -------- |
| [배달의민족 배달대행 API](https://www.newtrack.co.kr/news/29)                                     | 배달대행 주문정보 연동 시스템 (파트너사 전용)           | `apiKey` |
| [식품영양성분 데이터베이스](https://various.foodsafetykorea.go.kr/nutrient/industry/openApi/info.do) | 가공식품·원재료·음식별 영양성분(칼로리, 영양소 등) 정보를 제공 | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 게임 & 엔터테인먼트

| API                                                                                                                                                                                               | 설명                             | 인증        |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|-----------|
| [게임물관리위원회](https://www.grac.or.kr/OpenBook/OpenAPI.aspx)                                                                                                                                          | 게임물 등급분류 정보                    | `apiKey` |
| [넥슨 Open API](https://openapi.nexon.com/)                                                                                                                                                         | 메이플스토리, 던파, FC온라인 등 13종 게임 데이터 | `apiKey`  |
| [엔씨소프트 PLAYNC](https://developers.plaync.com/)                                                                                                                                                    | 리니지2M 아이템 정보, 시세, 검색 데이터       | `apiKey`  |
| [컴투스 HIVE 플랫폼](https://developers.hiveplatform.ai/ko/latest/api/hive-sdk-api/?_gl=1*1aw8yqt*_ga*NTEzOTU0MjkyLjE3NTU2MDQ1OTM.*_ga_4J643QJWFZ*czE3NTU2MDQ1OTIkbzEkZzEkdDE3NTU2MDQ2MDQkajQ4JGwwJGgw) | GBaaS 플랫폼 (연 1억명 접속)           | `apiKey`  |
| [크래프톤 배틀그라운드 API](https://developer.pubg.com/)                                                                                                                                                    | 배틀그라운드 게임 데이터, 플레이어 통계, 매치 분석  | `apiKey`  |
| [펄어비스 Black Desert API](https://documenter.getpostman.com/view/4028519/2s9Y5YRhp4)                                                                                                                | 검은사막 게임 정보 및 캐릭터 데이터           | `apiKey`  |
| [Neople API](https://developers.neople.co.kr/)                                                                                                                                                    | 던전앤파이터 게임 데이터                  | `apiKey`  |
| [Riot Games API](https://developer.riotgames.com/apis)                                                                                                                                            | 롤, 발로란트 등 라이엇 게임 데이터           | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 미디어 & 콘텐츠

| API                                                                      | 설명                                           | 인증     |
|--------------------------------------------------------------------------|----------------------------------------------| -------- |
| [네이버 치지직 API](https://chzzk.gitbook.io/chzzk)                            | 네이버 라이브 스트리밍 플랫폼                             | `apiKey` |
| [딥서치 뉴스 API](https://news.deepsearch.com)                              | 국내 150개, 해외 50개 언론사의 뉴스를 수집                  | `apiKey` |
| [만화규장각](https://www.kmas.or.kr/guide/openapi)                            | 최신의 만화/웹툰/작가 정보 제공                           | `apiKey` |
| [영화진흥위원회 KOBIS](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do) | 박스오피스, 영화정보, 영화사정보, 영화인정보                    | `apiKey` |
| [KMDb 시네마테크KOFA 상영일정](https://www.kmdb.or.kr/info/api/apiDetail/3)       | 한국영상자료원 상암본원 시네마테크 상영일정 (2002년~현재)           | `apiKey` |
| [KMDb 영화상세정보](https://www.kmdb.or.kr/info/api/apiDetail/6)               | 한국영화 제명, 제작년도, 제작사, 크레딧, 줄거리, 장르, 키워드 등 상세정보 | `apiKey` |
| [SOOP](https://developers.afreecatv.com/?szWork=openapi)                 | SOOP 방송 리스트, 카테고리 정보                         | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 소셜 & 커뮤니케이션

| API                                                                                     | 설명                                                | 인증      |
| --------------------------------------------------------------------------------------- | --------------------------------------------------- | --------- |
| [가비아 문자/알림톡 API](https://message.gabia.com/api/documentation/)                  | SMS, LMS, MMS, 카카오 알림톡 통합 (8개 언어 지원)   | `OAuth`   |
| [네이버 블로그 API](https://developers.naver.com/docs/serviceapi/search/blog/blog.md)   | 네이버 블로그 포스팅 API                            | `OAuth`   |
| [네이버 카페 API](https://developers.naver.com/docs/login/cafe-api/cafe-api.md)         | 네이버 카페 글 작성 및 관리                         | `OAuth`   |
| [라인 API](https://developers.line.biz/)                                                | LINE Login, Messaging API, LINE Pay, LIFF, MINI App | `OAuth`   |
| [센드버드 채팅 플랫폼 API](https://sendbird.com/docs)             | 실시간 채팅, 음성/영상 통화, AI 챗봇 기능 | `apiKey` |
| [잔디(JANDI) 웹훅](https://support.jandi.com/)                                          | 외부 서비스 실시간 연동 인커밍 웹훅                 | `webhook` |
| [카카오톡 공유하기](https://developers.kakao.com/docs/latest/ko/kakaotalk-share/common) | 웹/앱에서 카카오톡으로 콘텐츠 공유                  | `apiKey`  |
| [카카오톡 메시지](https://developers.kakao.com/docs/latest/ko/kakaotalk-message/common) | 카카오톡 텍스트/이미지 메시지 전송                  | `OAuth`   |
| [카카오톡 채널](https://developers.kakao.com/docs/latest/ko/kakaotalk-channel/common)   | 메시지 발송, 채널 관리                              | `OAuth`   |
| [하이웍스 API](https://developers.hiworks.com/)                                         | 전자결재, 푸시 알림 기업용 협업 도구                | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 에너지 & 전력

| API                                                                               | 설명                   | 인증        |
|-----------------------------------------------------------------------------------|----------------------|-----------|
| [전기차 충전소 정보](https://www.data.go.kr/data/15076352/openapi.do)                     | 전국 전기차 충전소 위치 및 상태정보 | `apiKey`  |
| [한국전력 전기요금](https://www.kepco.co.kr/home/disclosure/pbdata/pbdatasystem/conts.do) | 전기 사용량 및 요금 정보       | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 과학 & 연구

| API                                                                              | 설명                            | 인증     |
|----------------------------------------------------------------------------------|-------------------------------| -------- |
| [국가기록원 기록정보](https://www.archives.go.kr/next/newsearch/openAPI01.do)             | 국가기록 및 역사정보 검색                | `apiKey` |
| [국립중앙도서관 OpenAPI](https://www.nl.go.kr/NL/contents/N31101030700.do)              | 소장자료, 디지털컬렉션 검색               | `apiKey` |
| [근현대사 아카이브](https://archive.much.go.kr/cnts/cont01/page03.do)       | 박물관 소장품, 역사문화경관, 기록영상 등 근현대사 자료 | `apiKey` |
| [서울연구원 OpenAPI](https://www.si.re.kr/content.do?key=2411210021)                  | 연구보고서, 정기간행물, 정책리포트 등 연구성과 정보 | `apiKey` |
| [한국과학기술정보연구원 KISTI](https://scienceon.kisti.re.kr/apigateway/api/main/mainForm.do) | 과학기술 정보 및 연구데이터               | `apiKey` |
| [DBpia API](https://api.dbpia.co.kr/openApi/index.do)                            | 학술논문 검색 (기관 라이선스)             | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 비즈니스 & 기업

| API                                                               | 설명                                           | 인증          |
|-------------------------------------------------------------------|----------------------------------------------| ------------- |
| [네이버웍스 API](https://developers.worksmobile.com/kr)                | Bot 사용, 조직 및 그룹 관리, 파일 업로드/다운로드 외 다양한 기능과 리소스 | `OAuth`       |
| [비즈노 API](https://bizno.net/openapi)                              | 사업자등록번호, 상호명으로 사업자정보 조회                     | `apiKey` |
| [삼성 녹스 API](https://developer.samsung.com/knox)                   | 기업용 모바일 보안 및 관리 솔루션                          | `Partnership` |
| [에어브릿지 API](https://help.airbridge.io/ko/references/introduction) | 모바일 앱 마케팅 어트리뷰션 (다중 플랫폼 SDK)                 | `apiKey`      |
| [중소벤처기업부 기업정보](https://www.smes.go.kr/main/dbCnrs)                | 중소기업 지원정책 및 사업정보                             | `apiKey`      |
| [한국산업인력공단 HRD](https://openapi.hrdkorea.or.kr/main)               | 직업훈련, 자격증, 취업정보                              | `apiKey`      |
| [CODEF 오픈API](https://codef.io/)                                  | 금융, 보험, 통신, 공공기관 스크래핑 API                    | `OAuth`       |

**[⬆ 목차로 돌아가기](#목차)**

### 클라우드 서비스

| API                                                                      | 설명                                                 | 인증     |
| ------------------------------------------------------------------------ | ---------------------------------------------------- | -------- |
| [가비아 g클라우드](https://cloud.gabia.com/)                             | CSAP 인증 중소기업 친화적 클라우드                   | `apiKey` |
| [네이버 클라우드 플랫폼](https://api.ncloud-docs.com/docs/common-ncpapi) | 종합 클라우드 서비스 (AI, Maps, SMS, Object Storage) | `apiKey` |
| [KT Cloud API](https://cloud.kt.com/)                                    | 공공/금융/제조업 특화 클라우드 (NPU 지원)            | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 블록체인

| API                                         | 설명                                             | 인증     |
| ------------------------------------------- | ------------------------------------------------ | -------- |
| [두나무 노딧 API](https://docs.nodit.io/)   | 블록체인 개발 플랫폼 및 인프라 서비스            | `apiKey` |
| [카이아(KAIA) API](https://docs.kaia.io/)   | 클레이튼+핀시아 통합 블록체인 (라인 메신저 연동) | `apiKey` |
| [클레이튼 KAS](https://docs.klaytnapi.com/) | 노드 운영 없는 블록체인 개발 서비스              | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### IoT & 스마트홈

| API                                                                                                | 설명                                      | 인증    |
| -------------------------------------------------------------------------------------------------- |-----------------------------------------| ------- |
| [삼성 SmartThings API](https://developer.smartthings.com/docs/api/public)                          | 스마트홈 기기 제어, 자동화(룰), 장소 관리, 사용자·기기 정보 조회 | `OAuth` |
| [LG ThinQ API](https://smartsolution.developer.lge.com/ko/apiManage/thinq_connect?s=1755605653897) | AI 가전 제어 및 상업용 설비 관리                    | `OAuth` |

**[⬆ 목차로 돌아가기](#목차)**

### 암호화폐 거래소

| API                                         | 설명                          | 인증        |
|---------------------------------------------|-----------------------------|-----------|
| [빗썸 프로 API](https://apidocs.bithumb.com/)   | 전문 거래자용 암호화폐 거래 API         | `apiKey`  |
| [업비트 Open API](https://docs.upbit.com/kr)   | 국내 최대 암호화폐 거래소 API (JWT 인증) | `JWT`     |
| [코인원 Open API](https://docs.coinone.co.kr/) | 가상자산 거래 및 시세정보 API          | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 법률

| API                                                                                               | 설명                                     | 인증     |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------- | -------- |
| [국가법령정보 Open API](https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsNwListGuide) | 대한민국 현행 법령 목록과 조문 정보 조회 | `apiKey` |
| [국가법령정보 판례 API](https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precInfoGuide) | 대한민국 법원 판례 전문 정보 조회        | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 보안

| API                                                                         | 설명                                 | 인증     |
| --------------------------------------------------------------------------- | ------------------------------------ | -------- |
| [WHOIS 도메인/IP 정보 API](https://www.data.go.kr/data/15094277/openapi.do) | .kr 도메인과 IP 주소 WHOIS 정보 조회 | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 공공안전

| API                                                                  | 설명                              | 인증       |
|----------------------------------------------------------------------|---------------------------------| -------- |
| [생활안전정보](https://safemap.go.kr/opna/data/dataListRenew.do)                | 범죄발생현황, 교통사고, 화재, 생활안전시설 위치정보   | `apiKey` |
| [소방청 공공데이터](https://www.nfa.go.kr/nfa/releaseinformation/0011/0001/) | 화재정보, 구급출동, 소방시설 위치 등 소방안전정보    | `apiKey` |
| [안전드림 실종/안전 API](https://www.safe182.go.kr/home/api/guideMain.do)    | 실종자 정보 및 생활안전 정보 제공 (경찰청)       | `apiKey` |
| [재난안전데이터 공유플랫폼](https://www.safetydata.go.kr/disaster-data/list2)    | 재난 발생 현황, 피해 통계, 안전 관련 등 재난안전정보 | `apiKey` |
 
**[⬆ 목차로 돌아가기](#목차)**

### 항공

| API                                                                                       | 설명                                  | 인증     |
| ----------------------------------------------------------------------------------------- | ------------------------------------- | -------- |
| [국내항공운항정보 API](https://www.data.go.kr/data/15098526/openapi.do?recommendDataYn=Y) | 국내선 항공편 운항 일정 조회 (국토부) | `apiKey` |
| [인천공항 여객운항 현황 API](https://www.data.go.kr/data/15095074/openapi.do)             | 인천공항 항공편 출도착 현황 조회      | `apiKey` |
| [항공기 운항정보 API](https://www.data.go.kr/data/15000126/openapi.do)                    | 국내 공항 항공편 실시간 운항정보 조회 | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 물류 인프라 & 통관

| API                                                                                                                                                         | 설명                                         | 인증     |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------- | -------- |
| [관세청 화물통관정보 API](https://www.data.go.kr/data/15126268/openapi.do)                                                                                           | 수출입 화물 통관 진행 상황 조회              | `apiKey` |
| [로지스팟 물류 Open API](https://logi-spot.com/%EB%A1%9C%EC%A7%80%EC%8A%A4%ED%8C%9F-open-api-%EC%86%8C%EA%B0%9C-%EB%B0%8F-%ED%99%9C%EC%9A%A9-%EB%B0%A9%EB%B2%95/) | 통합 물류관리 API (운송배차, 차량정보, 정산) | `apiKey` |
| [물류창고업 등록정보 API](https://www.data.go.kr/data/3048029/openapi.do)                                                                                            | 전국 물류창고 업체 현황 정보 조회            | `apiKey` |
| [KOMSA MTIS Open API](https://mtisopenapi.komsa.or.kr/)                                                                                                     | 연안여객선 운항 일정·통계·제원 및 안전 정보 제공 | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 농수산

| API                                                                                              | 설명                                              | 인증     |
|--------------------------------------------------------------------------------------------------|-------------------------------------------------| -------- |
| [국립농업과학원 토양환경정보 Open API](https://www.naas.go.kr/01_commu/Commu_Minwon.do?menu_code=0&tg=5&mmode=21) | 지번 코드(PNU) 또는 법정동 코드를 통해 지역별 토양 화학성 등 상세 토양특성 정보 | `apiKey` |
| [국립수산과학원](https://www.nifs.go.kr/openApi/actionOpenapiInfoList.do)                               | 해양환경 및 수산정보                                     | `apiKey` |
| [농식품올바로](https://koreanfood.rda.go.kr/kfi/openapi/useNewGuidance)                                | 농산물성분, 농산물효능 등 다양한 농산물 정보                       | `apiKey` |
| [농촌진흥청 농사로 Open API](https://www.nongsaro.go.kr/portal/ps/psz/psza/contentMain.ps?menuId=PS00191) | 작목별 농업기술, 주간농사정보, 병해충 방제정보 등 다양한 농업 기술정보        | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 생활경제
| API                                                                                                                       | 설명                    | 인증        |
|---------------------------------------------------------------------------------------------------------------------------|-----------------------|-----------|
| [주유소 가격 정보](https://www.opinet.co.kr/user/custapi/custApiInfo.do)                                                         | 전국 주유소 휘발유/경유 가격      | `apiKey`  |
| [지역화폐 가맹점 현황](https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId=3NPA52LBMO36CQEQ1GMY28894927&infSeq=1) | 경기도 각 시군의 지역화폐 가맹점 현황 | `apiKey`  |
| [한국소비자원 참가격](https://www.data.go.kr/dataset/3043385/openapi.do)                                                           | 생필품 가격 정보 실시간 조회      | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 재정 & 예산

| API                                                                       | 설명                               | 인증        |
|---------------------------------------------------------------------------|----------------------------------|-----------|
| [열린재정 재정정보공개시스템](https://www.openfiscaldata.go.kr/op/ko/ds/UOPKODSA06)    | 국가 및 지방재정 예산/결산, 보조금, 국고보조사업 정보  | `apiKey`  |

**[⬆ 목차로 돌아가기](#목차)**

### 네이버

| API                                                                                                | 설명                                       | 인증     |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------- |
| [공유하기](https://developers.naver.com/docs/share/navershare/)                                    | 네이버 블로그, 카페 공유하기               | `apiKey` |
| [네이버 검색](https://developers.naver.com/products/service-api/search/search.md)                  | 블로그, 이미지, 웹, 뉴스, 백과사전 등 검색 | `apiKey` |
| [네이버 로그인](https://developers.naver.com/products/login/api/)                                  | 네이버 아이디로 로그인 및 프로필 조회      | `OAuth`  |
| [네이버 블로그](https://developers.naver.com/docs/serviceapi/search/blog/blog.md)                  | 블로그 포스팅 API                          | `OAuth`  |
| [네이버 지도](https://www.ncloud.com/product/applicationService/maps)                              | 지도 표시 및 주소 좌표 변환                | `apiKey` |
| [네이버 카페](https://developers.naver.com/docs/login/cafe-api/cafe-api.md)                        | 카페 가입 및 글 작성                       | `OAuth`  |
| [네이버 캘린더](https://developers.naver.com/docs/login/calendar-api/calendar-api.md)              | 사용자 캘린더 일정 추가                    | `OAuth`  |
| [단축URL](https://developers.naver.com/docs/utils/shortenurl/)                                     | URL을 me2.do 형태로 단축                   | `apiKey` |
| [데이터랩 검색어트렌드](https://developers.naver.com/docs/serviceapi/datalab/search/search.md)     | 통합검색어 트렌드 조회                     | `apiKey` |
| [데이터랩 쇼핑인사이트](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) | 쇼핑인사이트 분야별 트렌드 조회            | `apiKey` |
| [음성 캡차](https://developers.naver.com/docs/utils/scaptcha/overview/)                            | 자동 입력 방지용 음성 보안                 | `apiKey` |
| [캡차 이미지](https://developers.naver.com/docs/utils/captcha/overview/)                           | 자동 입력 방지용 보안 이미지 생성          | `apiKey` |
| [파파고 번역](https://developers.naver.com/docs/papago/README.md)                                  | 인공신경망 기반 기계 번역                  | `apiKey` |
| [CLOVA 얼굴인식](https://developers.naver.com/products/clova/face/)                                | 얼굴윤곽/부위/표정/유명인 닮음도 분석      | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

### 카카오

| API                                                                                       | 설명                                  | 인증     |
| ----------------------------------------------------------------------------------------- | ------------------------------------- | -------- |
| [카카오 검색](https://developers.kakao.com/docs/latest/ko/daum-search/common)             | 웹, 이미지, 동영상, 블로그 검색       | `apiKey` |
| [카카오 로그인](https://developers.kakao.com/docs/latest/ko/kakaologin/common)            | 카카오 계정으로 로그인 및 사용자 관리 | `OAuth`  |
| [카카오내비](https://developers.kakao.com/docs/latest/ko/kakaonavi/common)                | 카카오내비 길찾기 연동                | `apiKey` |
| [카카오링크](https://developers.kakao.com/docs/latest/ko/message/common)                  | 앱/웹에서 카카오톡으로 메시지 전송    | `apiKey` |
| [카카오맵](https://developers.kakao.com/docs/latest/ko/local/common)                      | 지도 표시, 장소 검색, 좌표 변환       | `apiKey` |
| [카카오모먼트](https://developers.kakao.com/docs/latest/ko/kakaomoment/reference)         | 모바일 광고 플랫폼                    | `apiKey` |
| [카카오톡 메시지](https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api) | 나에게 보내기, 친구에게 보내기        | `OAuth`  |
| [카카오톡 채널](https://developers.kakao.com/docs/latest/ko/kakaotalk-channel/common)     | 카카오톡 채널 관리                    | `OAuth`  |
| [카카오톡 친구](https://developers.kakao.com/docs/latest/ko/kakaotalk-social/common)      | 카카오톡 친구 목록 및 소셜 기능       | `OAuth`  |
| [카카오페이](http://developers.kakaopay.com/docs/payment/online/common)                   | 간편결제 및 정기결제                  | `apiKey` |
| [푸시 알림](https://developers.kakao.com/docs/latest/ko/push/common)                      | 앱 푸시 알림 발송                     | `apiKey` |

**[⬆ 목차로 돌아가기](#목차)**

---

## 기여하기

이 목록에 새로운 API를 추가하거나 정보를 수정하고 싶으시다면 Pull Request를 보내주세요. 자세한 내용은 [기여 가이드](./CONTRIBUTING.md)를 참고해주세요.

---

**마지막 업데이트**: 2026년 2월 03일

**총 API 수**: 260+α(데이터셋)

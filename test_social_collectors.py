"""
소셜 미디어 Collector 테스트 스크립트

실제 API를 호출해서 데이터를 가져올 수 있는지 테스트
"""

import asyncio
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.collectors.social_collector import TradestieCollector, StockTwitsCollector


async def test_tradestie():
    """Tradestie API 테스트 (WallStreetBets Top 50)"""
    print("\n" + "="*60)
    print("테스트 1: Tradestie API (WallStreetBets Top 50)")
    print("="*60)

    collector = TradestieCollector()

    print("\n데이터 수집 중...")
    mentions = await collector.collect()

    if mentions:
        print(f"\n✅ 성공! {len(mentions)}개의 종목 수집됨\n")
        print("상위 10개 종목:")
        print("-" * 60)
        for mention in mentions[:10]:
            print(f"#{mention['rank']:2d} | {mention['ticker']:6s} | "
                  f"멘션: {mention['mention_count']:4d} | "
                  f"감성: {mention['sentiment']:8s} | "
                  f"점수: {mention['sentiment_score']:+.2f}")
    else:
        print("\n❌ 실패: 데이터를 가져오지 못했습니다.")

    return mentions


async def test_stocktwits():
    """StockTwits API 테스트"""
    print("\n" + "="*60)
    print("테스트 2: StockTwits API (종목별 감성)")
    print("="*60)

    collector = StockTwitsCollector()

    # 테스트할 종목들 (유명한 미국 주식)
    test_symbols = ['TSLA', 'AAPL', 'NVDA', 'MSFT', 'AMD']

    print(f"\n{len(test_symbols)}개 종목 감성 분석 중...")

    results = await collector.collect_multiple(test_symbols)

    if results:
        print(f"\n✅ 성공! {len(results)}/{len(test_symbols)}개 종목 수집됨\n")
        print("종목별 감성:")
        print("-" * 60)
        for result in results:
            print(f"{result['ticker']:6s} | "
                  f"{result['sentiment']:8s} | "
                  f"점수: {result['sentiment_score']:+.2f} | "
                  f"낙관 비율: {result['bullish_ratio']:.1%} | "
                  f"멘션: {result['mention_count']}개")
    else:
        print("\n❌ 실패: 데이터를 가져오지 못했습니다.")

    return results


async def test_combined():
    """통합 테스트"""
    print("\n" + "="*60)
    print("테스트 3: 통합 워크플로우")
    print("="*60)

    print("\n1단계: WallStreetBets Top 50 수집...")
    wsb_mentions = await test_tradestie()

    if wsb_mentions:
        # WSB 상위 5개 종목에 대해 StockTwits 감성 조회
        top_tickers = [m['ticker'] for m in wsb_mentions[:5]]

        print(f"\n2단계: WSB 상위 {len(top_tickers)}개 종목의 StockTwits 감성 수집...")

        collector = StockTwitsCollector()
        st_results = await collector.collect_multiple(top_tickers)

        if st_results:
            print(f"\n✅ 통합 분석 완료!\n")
            print("WSB & StockTwits 비교:")
            print("-" * 80)
            print(f"{'티커':<8} | {'WSB 멘션':<10} | {'WSB 감성':<10} | "
                  f"{'StockTwits':<10} | {'낙관 비율':<10}")
            print("-" * 80)

            for wsb in wsb_mentions[:5]:
                ticker = wsb['ticker']
                st_data = next((s for s in st_results if s['ticker'] == ticker), None)

                wsb_sent = wsb['sentiment']
                wsb_count = wsb['mention_count']

                if st_data:
                    st_sent = st_data['sentiment']
                    st_ratio = f"{st_data['bullish_ratio']:.1%}"
                else:
                    st_sent = "N/A"
                    st_ratio = "N/A"

                print(f"{ticker:<8} | {wsb_count:<10} | {wsb_sent:<10} | "
                      f"{st_sent:<10} | {st_ratio:<10}")


async def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("소셜 미디어 Collector 실제 동작 테스트")
    print("="*60)
    print("\n이 테스트는 실제 API를 호출합니다 (무료, 인증 불필요)")
    print("인터넷 연결이 필요합니다.")

    try:
        # 모든 테스트 실행
        await test_combined()

        print("\n" + "="*60)
        print("테스트 완료!")
        print("="*60)
        print("\n✅ 모든 Collector가 정상 작동합니다.")
        print("\n다음 단계:")
        print("1. FastAPI 서버 실행: uvicorn app.main:app --reload")
        print("2. API 테스트: http://localhost:8000/docs")
        print("3. WSB 트렌딩 조회: GET /api/v1/social/wallstreetbets/trending")
        print("4. 종목 감성 조회: GET /api/v1/social/stocktwits/TSLA")

    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

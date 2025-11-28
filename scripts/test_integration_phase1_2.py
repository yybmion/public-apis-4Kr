#!/usr/bin/env python3
"""
Phase 1 + Phase 2 통합 테스트 스크립트

통합 테스트 대상:
- Phase 1: FRED API, ECOS API, Fear & Greed Index
- Phase 2: SEC EDGAR API

검증 항목:
1. 모든 수집기가 정상 작동하는지
2. 데이터 품질 검증
3. 수집기 간 데이터 연관성 분석
4. 전체 시스템 통합 동작 확인

Usage:
    python scripts/test_integration_phase1_2.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.collectors.fred_collector import FredCollector
from app.collectors.ecos_collector import EcosCollector
from app.collectors.fear_greed_collector import FearGreedCollector
from app.collectors.sec_edgar_collector import SECEdgarCollector
from app.config import Settings


# ============================================================================
# Utility Functions
# ============================================================================

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")


def print_data(label: str, value, indent: int = 1):
    """Print data in a formatted way"""
    indent_str = "   " * indent
    print(f"{indent_str}{label}: {value}")


# ============================================================================
# Individual Collector Tests
# ============================================================================

async def test_fear_greed_collector() -> Dict[str, Any]:
    """Test Fear & Greed Index Collector"""
    print_section("TEST 1: Fear & Greed Index Collector")

    try:
        collector = FearGreedCollector()
        print_info("Fear & Greed Index Collector 초기화 완료")

        # Collect data
        print("\n📊 Fear & Greed Index 수집 중...")
        result = await collector.collect()

        if result.get('success'):
            data = result['data']
            print_success(f"데이터 수집 성공!")
            print_data("Score", f"{data['score']:.2f} / 100")
            print_data("Rating", data['rating'])
            print_data("Signal", data['signal']['signal'])

            return {
                'success': True,
                'collector': 'FearGreed',
                'data': data,
                'score': data['score']
            }
        else:
            print_error(f"수집 실패: {result.get('error')}")
            return {'success': False, 'collector': 'FearGreed'}

    except Exception as e:
        print_error(f"예외 발생: {str(e)}")
        return {'success': False, 'collector': 'FearGreed', 'error': str(e)}


async def test_fred_collector(api_key: str) -> Dict[str, Any]:
    """Test FRED API Collector"""
    print_section("TEST 2: FRED API Collector")

    if not api_key or api_key == "your_fred_api_key_here":
        print_warning("FRED API 키가 설정되지 않았습니다. 테스트를 건너뜁니다.")
        return {'success': False, 'collector': 'FRED', 'skipped': True}

    try:
        collector = FredCollector(api_key=api_key)
        print_info("FRED Collector 초기화 완료")

        # Test Federal Funds Rate
        print("\n📊 Federal Funds Rate 수집 중...")
        result = await collector.collect(indicator='federal_funds_rate')

        if result.get('success'):
            data = result['data']
            print_success(f"데이터 수집 성공!")
            print_data("Indicator", data['indicator_name'])
            print_data("Latest Value", f"{data['latest_value']:.2f}%")
            print_data("Latest Date", data['latest_date'])

            # Get yield curve
            print("\n📈 Yield Curve 계산 중...")
            yc_result = await collector.get_yield_curve()

            if yc_result.get('success'):
                yc_data = yc_result['data']
                print_success("Yield Curve 계산 완료!")
                print_data("10Y-2Y Spread", f"{yc_data['spreads'].get('10y_2y', 0):.3f}%")
                print_data("Recession Signal", yc_data['recession_signal'])

                return {
                    'success': True,
                    'collector': 'FRED',
                    'data': data,
                    'yield_curve': yc_data,
                    'fed_rate': data['latest_value']
                }
            else:
                return {'success': False, 'collector': 'FRED'}
        else:
            print_error(f"수집 실패: {result.get('error')}")
            return {'success': False, 'collector': 'FRED'}

    except Exception as e:
        print_error(f"예외 발생: {str(e)}")
        return {'success': False, 'collector': 'FRED', 'error': str(e)}


async def test_ecos_collector(api_key: str) -> Dict[str, Any]:
    """Test ECOS API Collector"""
    print_section("TEST 3: ECOS API Collector")

    if not api_key or api_key == "your_ecos_api_key_here":
        print_warning("ECOS API 키가 설정되지 않았습니다. 테스트를 건너뜁니다.")
        return {'success': False, 'collector': 'ECOS', 'skipped': True}

    try:
        collector = EcosCollector(api_key=api_key)
        print_info("ECOS Collector 초기화 완료")

        # Test Base Rate
        print("\n📊 한국 기준금리 수집 중...")
        result = await collector.collect(indicator='base_rate')

        if result.get('success'):
            data = result['data']
            print_success(f"데이터 수집 성공!")
            print_data("Indicator", data['indicator_name'])
            print_data("Latest Value", f"{data['latest_value']:.2f}%")
            print_data("Latest Date", data['latest_date'])

            # Get economic snapshot
            print("\n📈 Economic Snapshot 생성 중...")
            snapshot = await collector.get_economic_snapshot()

            if snapshot.get('success'):
                snap_data = snapshot['data']
                print_success("Economic Snapshot 생성 완료!")
                print_data("Base Rate", f"{snap_data.get('base_rate', {}).get('value', 0):.2f}%")
                print_data("USD/KRW", f"{snap_data.get('usd_krw', {}).get('value', 0):.2f}")

                return {
                    'success': True,
                    'collector': 'ECOS',
                    'data': data,
                    'snapshot': snap_data,
                    'base_rate': data['latest_value']
                }
            else:
                return {'success': False, 'collector': 'ECOS'}
        else:
            print_error(f"수집 실패: {result.get('error')}")
            return {'success': False, 'collector': 'ECOS'}

    except Exception as e:
        print_error(f"예외 발생: {str(e)}")
        return {'success': False, 'collector': 'ECOS', 'error': str(e)}


async def test_sec_edgar_collector() -> Dict[str, Any]:
    """Test SEC EDGAR API Collector"""
    print_section("TEST 4: SEC EDGAR API Collector")

    try:
        collector = SECEdgarCollector()
        print_info("SEC EDGAR Collector 초기화 완료 (API 키 불필요)")

        # Test ticker to CIK
        print("\n📊 Apple 티커 → CIK 변환 중...")
        cik = await collector.ticker_to_cik("AAPL")

        if cik:
            print_success(f"AAPL → CIK: {cik}")

            # Get latest 10-K
            print("\n📄 Apple 최신 10-K 조회 중...")
            result = await collector.get_latest_10k("AAPL")

            if result.get('success'):
                data = result['data']
                print_success("10-K 데이터 수집 성공!")
                print_data("Company", data.get('company_name'))

                if 'latest_filing' in data:
                    filing = data['latest_filing']
                    print_data("Filing Date", filing.get('filing_date'))
                    print_data("Accession Number", filing.get('accession_number'))

                return {
                    'success': True,
                    'collector': 'SEC_EDGAR',
                    'cik': cik,
                    'data': data
                }
            else:
                return {'success': False, 'collector': 'SEC_EDGAR'}
        else:
            print_error("CIK 변환 실패")
            return {'success': False, 'collector': 'SEC_EDGAR'}

    except Exception as e:
        print_error(f"예외 발생: {str(e)}")
        return {'success': False, 'collector': 'SEC_EDGAR', 'error': str(e)}


# ============================================================================
# Integration Tests
# ============================================================================

async def test_data_correlation(results: List[Dict[str, Any]]):
    """Test data correlation between collectors"""
    print_section("TEST 5: 데이터 상관성 분석")

    # Extract data from results
    fear_greed = next((r for r in results if r['collector'] == 'FearGreed' and r['success']), None)
    fred = next((r for r in results if r['collector'] == 'FRED' and r['success']), None)
    ecos = next((r for r in results if r['collector'] == 'ECOS' and r['success']), None)

    if not fear_greed:
        print_warning("Fear & Greed 데이터 없음 - 상관성 분석 제한적")
        return

    print_info("수집된 데이터 간 상관성 분석 중...\n")

    # Analysis 1: Fear & Greed vs Interest Rates
    if fred and 'fed_rate' in fred:
        fed_rate = fred['fed_rate']
        fear_score = fear_greed['score']

        print("📊 분석 1: 시장 심리 vs 미국 금리")
        print_data("Fear & Greed Score", f"{fear_score:.2f}")
        print_data("Fed Funds Rate", f"{fed_rate:.2f}%")

        # Simple correlation logic
        if fear_score < 30 and fed_rate > 4.5:
            print_data("관찰", "높은 금리 + 극단적 공포 → 매수 기회 가능성")
        elif fear_score > 70 and fed_rate < 2.0:
            print_data("관찰", "낮은 금리 + 극단적 탐욕 → 과열 신호")
        else:
            print_data("관찰", "정상 범위")
        print()

    # Analysis 2: US vs Korea Interest Rates
    if fred and ecos and 'fed_rate' in fred and 'base_rate' in ecos:
        fed_rate = fred['fed_rate']
        base_rate = ecos['base_rate']
        spread = fed_rate - base_rate

        print("📊 분석 2: 미국-한국 금리 차이")
        print_data("US Fed Rate", f"{fed_rate:.2f}%")
        print_data("KR Base Rate", f"{base_rate:.2f}%")
        print_data("Spread", f"{spread:.2f}%p")

        if spread > 2.0:
            print_data("관찰", "미국 금리 높음 → 원화 약세 압력")
        elif spread < -0.5:
            print_data("관찰", "한국 금리 상대적 높음 → 원화 강세 가능성")
        else:
            print_data("관찰", "적정 범위")
        print()

    # Analysis 3: Overall Market Condition
    print("📊 분석 3: 종합 시장 상황")

    conditions = []
    if fear_greed:
        score = fear_greed['score']
        if score < 25:
            conditions.append("극단적 공포 (역발상 매수 기회)")
        elif score > 75:
            conditions.append("극단적 탐욕 (경계 필요)")
        else:
            conditions.append(f"시장 심리 {fear_greed['data']['rating']}")

    if fred and 'yield_curve' in fred:
        yc = fred['yield_curve']
        if yc.get('recession_signal'):
            conditions.append("⚠️  수익률 곡선 역전 (경기 침체 신호)")
        else:
            conditions.append("수익률 곡선 정상")

    for i, condition in enumerate(conditions, 1):
        print_data(f"조건 {i}", condition)

    print()


async def test_system_health(results: List[Dict[str, Any]]):
    """Test overall system health"""
    print_section("TEST 6: 시스템 전체 상태 점검")

    total = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = sum(1 for r in results if not r['success'] and not r.get('skipped'))
    skipped = sum(1 for r in results if r.get('skipped'))

    print(f"📊 수집기 상태:")
    print_data("전체", f"{total}개")
    print_data("성공", f"{successful}개")
    print_data("실패", f"{failed}개")
    print_data("건너뜀", f"{skipped}개 (API 키 미설정)")
    print()

    success_rate = (successful / (total - skipped)) * 100 if (total - skipped) > 0 else 0

    if success_rate == 100:
        print_success(f"시스템 상태: 완벽 ({success_rate:.0f}%)")
    elif success_rate >= 75:
        print_success(f"시스템 상태: 양호 ({success_rate:.0f}%)")
    elif success_rate >= 50:
        print_warning(f"시스템 상태: 보통 ({success_rate:.0f}%)")
    else:
        print_error(f"시스템 상태: 불량 ({success_rate:.0f}%)")

    # Recommendations
    print("\n💡 권장사항:")

    if skipped > 0:
        print_info("API 키를 설정하면 더 많은 데이터를 수집할 수 있습니다:")
        for r in results:
            if r.get('skipped'):
                if r['collector'] == 'FRED':
                    print("   - FRED API: https://fredaccount.stlouisfed.org/apikeys")
                elif r['collector'] == 'ECOS':
                    print("   - ECOS API: https://ecos.bok.or.kr/api/")

    if successful >= 2:
        print_success("최소 2개 이상의 데이터 소스가 작동 중입니다!")
        print_info("분석 모듈을 활성화할 수 있습니다.")

    if successful == total:
        print_success("모든 수집기가 정상 작동합니다!")
        print_info("프로덕션 환경으로 배포 가능합니다.")


# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """Main integration test runner"""
    print_section("Phase 1 + Phase 2 통합 테스트")
    print("데이터 수집기 통합 테스트를 시작합니다.\n")
    print("테스트 대상:")
    print("  - Phase 1: FRED API, ECOS API, Fear & Greed Index")
    print("  - Phase 2: SEC EDGAR API")
    print()

    # Load configuration
    try:
        settings = Settings()
        fred_api_key = settings.FRED_API_KEY
        ecos_api_key = settings.ECOS_API_KEY
    except Exception as e:
        print_warning(f"설정 로드 실패: {str(e)}")
        print_warning(".env 파일이 없거나 API 키가 설정되지 않았습니다.")
        fred_api_key = ""
        ecos_api_key = ""

    # Run individual collector tests
    results = []

    # Test 1: Fear & Greed (always runs - no API key needed)
    fear_greed_result = await test_fear_greed_collector()
    results.append(fear_greed_result)

    # Test 2: FRED
    fred_result = await test_fred_collector(fred_api_key)
    results.append(fred_result)

    # Test 3: ECOS
    ecos_result = await test_ecos_collector(ecos_api_key)
    results.append(ecos_result)

    # Test 4: SEC EDGAR (always runs - no API key needed)
    sec_result = await test_sec_edgar_collector()
    results.append(sec_result)

    # Integration tests
    await test_data_correlation(results)
    await test_system_health(results)

    # Final summary
    print_section("최종 결과")

    successful = sum(1 for r in results if r['success'])
    total_runnable = sum(1 for r in results if not r.get('skipped'))

    if successful == total_runnable:
        print_success(f"✨ 모든 테스트 통과! ({successful}/{total_runnable})")
        print()
        print("🎉 축하합니다! Phase 1 + Phase 2 통합이 완료되었습니다!")
        print()
        print("다음 단계:")
        print("  1. 데이터베이스 마이그레이션 실행")
        print("  2. 분석 모듈 구현")
        print("  3. 대시보드 구축")
        print()
        return True
    else:
        print_warning(f"일부 테스트 통과 ({successful}/{total_runnable})")
        print()
        print("문제 해결:")
        for r in results:
            if not r['success'] and not r.get('skipped'):
                print(f"  ❌ {r['collector']}: {r.get('error', '알 수 없는 오류')}")
        print()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Scheduler Test Script

자동화 스케줄러 테스트

Usage:
    python scripts/test_scheduler.py [--mode MODE]

Modes:
    instant: 즉시 실행 테스트 (기본값)
    schedule: 스케줄 모드 테스트 (10초 간격)
    daemon: 데몬 모드 (계속 실행)
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scheduler.scheduler import StockDataScheduler
from app.config import Settings


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"✅ {msg}")


def print_info(msg: str):
    """Print info message"""
    print(f"ℹ️  {msg}")


def print_warning(msg: str):
    """Print warning message"""
    print(f"⚠️  {msg}")


async def test_instant_mode():
    """Test scheduler in instant mode (즉시 실행)"""
    print_section("Scheduler Test: Instant Mode")
    print_info("스케줄러를 즉시 실행 모드로 테스트합니다.\n")

    # Initialize scheduler in test mode
    scheduler = StockDataScheduler(test_mode=True)

    # Test 1: Run collection now
    print_section("TEST 1: 데이터 수집 즉시 실행")
    collection_result = await scheduler.run_now_collection()

    if collection_result.get('success'):
        summary = collection_result['summary']
        print_success(
            f"데이터 수집 완료: {summary['successful']}/{summary['total']} 성공 "
            f"(소요시간: {summary['duration_seconds']:.1f}초)"
        )

        # Show collected data
        results = collection_result['results']
        print("\n수집된 데이터:")

        if results.get('fear_greed', {}).get('success'):
            fg = results['fear_greed']['data']
            print(f"  • Fear & Greed: {fg['score']:.1f} ({fg['rating']})")

        if results.get('fred', {}).get('success'):
            fred = results['fred']
            rate = fred['fed_rate']['latest_value']
            print(f"  • Fed Rate: {rate:.2f}%")

        if results.get('ecos', {}).get('success'):
            ecos = results['ecos']
            rate = ecos['base_rate']['latest_value']
            print(f"  • KR Base Rate: {rate:.2f}%")
    else:
        print_warning("데이터 수집 실패 또는 일부만 성공")

    # Test 2: Run analysis now
    print_section("TEST 2: 분석 즉시 실행")
    analysis_result = await scheduler.run_now_analysis()

    if analysis_result.get('success'):
        summary = analysis_result['summary']
        print_success(
            f"분석 완료: {summary['successful']}/{summary['total']} 성공 "
            f"(소요시간: {summary['duration_seconds']:.1f}초)"
        )

        # Show analysis results
        results = analysis_result['results']

        if results.get('investment_signal', {}).get('success'):
            signal = results['investment_signal']['signal']
            print(f"\n📊 투자 신호: {signal['signal']}")
            print(f"   신뢰도: {signal['confidence']:.0f}%")
            print(f"   액션: {signal['action_plan']['action']}")

        # Show briefing
        if results.get('daily_briefing', {}).get('success'):
            print("\n" + results['daily_briefing']['briefing'])
    else:
        print_warning("분석 실패")

    # Test 3: Check status
    print_section("TEST 3: 스케줄러 상태 확인")
    status = scheduler.get_status()

    print(f"Running: {status['running']}")
    print(f"Jobs: {status['jobs']}")
    print(f"Latest Collection: {status['latest_collection']}")
    print(f"Latest Analysis: {status['latest_analysis']}")

    print_section("테스트 완료")
    print_success("✨ 즉시 실행 모드 테스트 성공!")


async def test_schedule_mode():
    """Test scheduler in schedule mode (짧은 간격)"""
    print_section("Scheduler Test: Schedule Mode")
    print_info("스케줄러를 짧은 간격으로 테스트합니다 (10초마다).\n")
    print_warning("Ctrl+C를 눌러 종료하세요.\n")

    # Initialize scheduler
    scheduler = StockDataScheduler()

    # Override schedules for testing (every 10 seconds)
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler.scheduler.remove_all_jobs()

    # Add test jobs
    scheduler.scheduler.add_job(
        scheduler.job_collect_fear_greed,
        IntervalTrigger(seconds=10),
        id='test_fear_greed',
        name='Test: Fear & Greed (10초마다)'
    )

    scheduler.scheduler.add_job(
        scheduler.job_generate_signal,
        IntervalTrigger(seconds=30),
        id='test_signal',
        name='Test: 투자 신호 (30초마다)'
    )

    print_info("스케줄 목록:")
    scheduler.list_jobs()

    # Start scheduler
    scheduler.start()

    print_success("스케줄러 시작됨. 작업이 자동으로 실행됩니다...\n")

    try:
        # Run first collection immediately
        await scheduler.run_now_collection()

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  사용자 중단")
        scheduler.stop()

    print_section("테스트 종료")


async def test_daemon_mode():
    """Test scheduler in daemon mode (실제 스케줄대로)"""
    print_section("Scheduler Test: Daemon Mode")
    print_info("스케줄러를 실제 스케줄대로 실행합니다.\n")
    print_warning("Ctrl+C를 눌러 종료하세요.\n")

    # Initialize scheduler
    scheduler = StockDataScheduler()

    # Show schedule
    print_info("스케줄 목록:")
    scheduler.list_jobs()

    # Start scheduler
    scheduler.start()

    print_success("스케줄러 시작됨. 예정된 시간에 작업이 실행됩니다...\n")

    try:
        # Keep running
        while True:
            await asyncio.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n\n⏹️  사용자 중단")
        scheduler.stop()

    print_section("테스트 종료")


async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='스케줄러 테스트')
    parser.add_argument(
        '--mode',
        choices=['instant', 'schedule', 'daemon'],
        default='instant',
        help='테스트 모드 (기본값: instant)'
    )

    args = parser.parse_args()

    print_section("자동화 스케줄러 테스트")
    print(f"테스트 모드: {args.mode}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        if args.mode == 'instant':
            await test_instant_mode()
        elif args.mode == 'schedule':
            await test_schedule_mode()
        elif args.mode == 'daemon':
            await test_daemon_mode()

        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Run Scheduler (Production)

프로덕션 환경에서 스케줄러 실행

Usage:
    python scripts/run_scheduler.py
    python scripts/run_scheduler.py --init  # 첫 실행 시 즉시 데이터 수집

Features:
- 자동 데이터 수집 (Fear & Greed, FRED, ECOS, SEC EDGAR)
- 자동 분석 및 투자 신호 생성
- 일일 브리핑 (개장 전/마감 후)
- 오류 발생 시 자동 재시도
- 안전한 종료 (Ctrl+C)

Schedule:
- 06:00: Fear & Greed Index
- 07:00: FRED 경제 지표
- 08:30: 투자 신호 생성
- 09:00: ECOS + 개장 전 브리핑
- 09:30: 전체 분석
- 15:40: 마감 후 브리핑
- 월요일 08:00: SEC EDGAR 주간 업데이트

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
import sys
import argparse
import signal
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scheduler.scheduler import StockDataScheduler
from app.config import Settings


class SchedulerRunner:
    """Scheduler Runner with graceful shutdown"""

    def __init__(self, scheduler: StockDataScheduler):
        """
        Initialize Runner

        Args:
            scheduler: Stock Data Scheduler instance
        """
        self.scheduler = scheduler
        self.running = False

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n\n🛑 종료 신호 수신...")
        self.running = False

    async def run(self, init: bool = False):
        """
        Run scheduler

        Args:
            init: 첫 실행 시 즉시 데이터 수집
        """
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("=" * 80)
        print("  📊 Stock Intelligence System - 자동화 스케줄러")
        print("=" * 80)
        print()
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Initial run
        if init:
            print("🚀 초기 데이터 수집 시작...")
            try:
                await self.scheduler.run_now_full()
                print("✅ 초기 데이터 수집 완료\n")
            except Exception as e:
                print(f"⚠️  초기 수집 실패: {str(e)}\n")

        # Start scheduler
        print("=" * 80)
        print("  ⏰ 스케줄러 시작")
        print("=" * 80)
        self.scheduler.start()

        # Show schedule
        self.scheduler.list_jobs()

        print("\n✅ 스케줄러가 실행 중입니다...")
        print("   Ctrl+C를 눌러 종료하세요.\n")

        self.running = True

        try:
            while self.running:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass

        finally:
            print("\n🛑 스케줄러 종료 중...")
            self.scheduler.stop()
            print("✅ 스케줄러 종료 완료")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Stock Intelligence System - 자동화 스케줄러',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_scheduler.py              # 스케줄러 시작
  python scripts/run_scheduler.py --init       # 초기 데이터 수집 후 시작

Schedule:
  06:00 - Fear & Greed Index 수집
  07:00 - FRED 경제 지표 수집
  08:30 - 투자 신호 생성
  09:00 - ECOS 경제 지표 수집 + 개장 전 브리핑
  09:30 - 전체 분석 실행
  15:40 - 마감 후 브리핑
  월 08:00 - SEC EDGAR 주간 업데이트

Ctrl+C to stop.
        """
    )

    parser.add_argument(
        '--init',
        action='store_true',
        help='첫 실행 시 즉시 데이터 수집'
    )

    args = parser.parse_args()

    try:
        # Load settings
        settings = Settings()

        # Initialize scheduler
        scheduler = StockDataScheduler(settings=settings)

        # Run
        runner = SchedulerRunner(scheduler)
        await runner.run(init=args.init)

        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

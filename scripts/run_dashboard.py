#!/usr/bin/env python3
"""
Run Dashboard

Streamlit 대시보드 실행 스크립트

Usage:
    python scripts/run_dashboard.py
    python scripts/run_dashboard.py --port 8501
    python scripts/run_dashboard.py --host 0.0.0.0

Author: AI Assistant
Created: 2025-11-22
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Stock Intelligence System - Streamlit Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_dashboard.py              # 기본 실행 (localhost:8501)
  python scripts/run_dashboard.py --port 8080  # 포트 변경
  python scripts/run_dashboard.py --host 0.0.0.0  # 외부 접속 허용

Features:
  - 실시간 시장 현황
  - 투자 신호 및 액션 플랜
  - 경제 지표 모니터링
  - 분석 차트 (개발 중)
  - 스케줄러 제어 (개발 중)
        """
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='포트 번호 (기본값: 8501)'
    )

    parser.add_argument(
        '--host',
        default='localhost',
        help='호스트 (기본값: localhost, 외부 접속: 0.0.0.0)'
    )

    args = parser.parse_args()

    # Dashboard path
    dashboard_path = project_root / 'app' / 'dashboard' / 'main.py'

    if not dashboard_path.exists():
        print(f"❌ 대시보드 파일을 찾을 수 없습니다: {dashboard_path}")
        return False

    print("=" * 80)
    print("  📊 Stock Intelligence System - Dashboard")
    print("=" * 80)
    print()
    print(f"대시보드 URL: http://{args.host}:{args.port}")
    print()
    print("Ctrl+C를 눌러 종료하세요.")
    print("=" * 80)
    print()

    # Run streamlit
    try:
        cmd = [
            'streamlit',
            'run',
            str(dashboard_path),
            '--server.port', str(args.port),
            '--server.address', args.host,
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]

        subprocess.run(cmd, check=True)

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 대시보드 실행 실패: {e}")
        return False

    except KeyboardInterrupt:
        print("\n\n🛑 대시보드 종료")
        return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Logs Page - 로그 및 모니터링

실시간 로그 확인 및 시스템 모니터링

Author: AI Assistant
Created: 2025-11-22
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import json


LOG_DIR = Path(os.getenv('LOG_DIR', 'logs'))


def read_log_file(file_path: Path, lines: int = 100) -> list:
    """
    Read last N lines from log file

    Args:
        file_path: Path to log file
        lines: Number of lines to read

    Returns:
        List of log lines
    """
    if not file_path.exists():
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    except Exception as e:
        st.error(f"로그 파일 읽기 실패: {str(e)}")
        return []


def parse_log_line(line: str) -> dict:
    """
    Parse log line

    Args:
        line: Log line

    Returns:
        Parsed log dict
    """
    try:
        # Try JSON format first
        return json.loads(line)
    except:
        # Fall back to text parsing
        parts = line.split(' - ', 3)
        if len(parts) >= 4:
            return {
                'timestamp': parts[0],
                'logger': parts[1],
                'level': parts[2],
                'message': parts[3].strip()
            }
        else:
            return {
                'timestamp': '',
                'logger': '',
                'level': 'UNKNOWN',
                'message': line.strip()
            }


def get_log_stats(lines: list) -> dict:
    """
    Get log statistics

    Args:
        lines: Log lines

    Returns:
        Statistics dict
    """
    levels = []
    loggers = []
    timestamps = []

    for line in lines:
        parsed = parse_log_line(line)
        levels.append(parsed.get('level', 'UNKNOWN'))
        loggers.append(parsed.get('logger', 'unknown'))

        ts = parsed.get('timestamp', '')
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
            except:
                pass

    level_counts = Counter(levels)
    logger_counts = Counter(loggers)

    return {
        'total_logs': len(lines),
        'level_counts': dict(level_counts),
        'logger_counts': dict(logger_counts),
        'timestamps': timestamps
    }


def show_log_viewer(log_file: Path, title: str, lines: int = 100):
    """
    Show log viewer

    Args:
        log_file: Path to log file
        title: Viewer title
        lines: Number of lines to show
    """
    st.markdown(f"### {title}")

    if not log_file.exists():
        st.info(f"📝 로그 파일이 아직 생성되지 않았습니다: {log_file.name}")
        return

    # File info
    file_size = log_file.stat().st_size
    file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("파일 크기", f"{file_size / 1024:.1f} KB")
    with col2:
        st.metric("마지막 수정", file_modified.strftime('%H:%M:%S'))
    with col3:
        if st.button(f"🔄 새로고침", key=f"refresh_{log_file.name}"):
            st.rerun()

    # Read logs
    log_lines = read_log_file(log_file, lines)

    if not log_lines:
        st.info("로그가 비어있습니다.")
        return

    # Statistics
    stats = get_log_stats(log_lines)

    # Level distribution
    if stats['level_counts']:
        st.markdown("#### 로그 레벨 분포")

        level_colors = {
            'DEBUG': '#17a2b8',
            'INFO': '#28a745',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#6f42c1'
        }

        fig = go.Figure(data=[
            go.Bar(
                x=list(stats['level_counts'].keys()),
                y=list(stats['level_counts'].values()),
                marker_color=[level_colors.get(level, '#6c757d') for level in stats['level_counts'].keys()]
            )
        ])

        fig.update_layout(
            title=f"총 {stats['total_logs']}개 로그",
            xaxis_title="로그 레벨",
            yaxis_title="개수",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    # Filter options
    st.markdown("#### 필터")

    col1, col2 = st.columns(2)

    with col1:
        level_filter = st.multiselect(
            "로그 레벨",
            options=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default=['ERROR', 'WARNING', 'INFO'],
            key=f"level_filter_{log_file.name}"
        )

    with col2:
        search_text = st.text_input(
            "검색어",
            key=f"search_{log_file.name}"
        )

    # Display logs
    st.markdown("#### 로그 내용")

    filtered_logs = []
    for line in log_lines:
        parsed = parse_log_line(line)
        level = parsed.get('level', 'UNKNOWN')
        message = parsed.get('message', line)

        # Apply filters
        if level not in level_filter:
            continue

        if search_text and search_text.lower() not in message.lower():
            continue

        filtered_logs.append(line)

    if not filtered_logs:
        st.info("필터 조건에 맞는 로그가 없습니다.")
        return

    # Show in text area (most recent first)
    log_text = ''.join(reversed(filtered_logs))

    st.text_area(
        f"{len(filtered_logs)}개 로그 (최신순)",
        log_text,
        height=400,
        key=f"logs_{log_file.name}"
    )

    # Download button
    st.download_button(
        label="📥 로그 다운로드",
        data=log_text,
        file_name=f"{log_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        key=f"download_{log_file.name}"
    )


def show_system_status():
    """Show system status"""
    st.markdown("### 시스템 상태")

    col1, col2, col3, col4 = st.columns(4)

    # Log directory status
    with col1:
        log_files = list(LOG_DIR.glob('*.log'))
        st.metric("로그 파일", f"{len(log_files)}개")

    # Total log size
    with col2:
        total_size = sum(f.stat().st_size for f in log_files if f.exists())
        st.metric("총 로그 크기", f"{total_size / (1024 * 1024):.1f} MB")

    # Latest log time
    with col3:
        if log_files:
            latest_time = max(f.stat().st_mtime for f in log_files if f.exists())
            latest_dt = datetime.fromtimestamp(latest_time)
            time_ago = (datetime.now() - latest_dt).total_seconds()

            if time_ago < 60:
                time_str = f"{int(time_ago)}초 전"
            elif time_ago < 3600:
                time_str = f"{int(time_ago / 60)}분 전"
            else:
                time_str = f"{int(time_ago / 3600)}시간 전"

            st.metric("마지막 로그", time_str)
        else:
            st.metric("마지막 로그", "N/A")

    # Log directory path
    with col4:
        st.metric("로그 디렉토리", str(LOG_DIR))

    # Log files list
    if log_files:
        st.markdown("#### 로그 파일 목록")

        file_data = []
        for log_file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True):
            file_stat = log_file.stat()
            file_data.append({
                '파일명': log_file.name,
                '크기 (KB)': f"{file_stat.st_size / 1024:.1f}",
                '마지막 수정': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })

        df = pd.DataFrame(file_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def show_error_summary():
    """Show error summary from error.log"""
    st.markdown("### 오류 요약")

    error_log = LOG_DIR / 'errors.log'

    if not error_log.exists():
        st.info("📝 오류 로그가 아직 생성되지 않았습니다.")
        return

    # Read recent errors
    error_lines = read_log_file(error_log, lines=50)

    if not error_lines:
        st.success("✅ 최근 오류 없음")
        return

    # Parse errors
    errors = []
    for line in error_lines:
        parsed = parse_log_line(line)
        if parsed.get('level') in ['ERROR', 'CRITICAL']:
            errors.append(parsed)

    if not errors:
        st.success("✅ 최근 오류 없음")
        return

    # Error count
    st.error(f"⚠️ 최근 {len(errors)}개 오류 발견")

    # Recent errors
    st.markdown("#### 최근 오류 (최대 10개)")

    for error in errors[-10:]:
        with st.expander(
            f"🔴 {error.get('timestamp', 'N/A')} - {error.get('message', 'Unknown error')[:100]}",
            expanded=False
        ):
            st.code(error.get('message', 'Unknown error'), language='text')

            if 'exception' in error:
                st.markdown("**Stack Trace:**")
                st.code(error['exception'], language='python')


def show():
    """Show logs page"""
    st.title("📋 로그 및 모니터링")

    st.markdown("""
    시스템 로그를 실시간으로 확인하고 오류를 추적합니다.
    """)

    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("자동 새로고침 (30초)", value=False)

    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 시스템 상태", "📝 전체 로그", "🔴 오류 로그", "⚙️ 설정"])

    with tab1:
        show_system_status()
        st.markdown("---")
        show_error_summary()

    with tab2:
        log_file = LOG_DIR / 'stock_intelligence.log'

        # Number of lines to show
        lines = st.slider("표시할 로그 개수", 50, 500, 100, 50)

        show_log_viewer(log_file, "전체 시스템 로그", lines)

    with tab3:
        error_log = LOG_DIR / 'errors.log'

        # Number of lines to show
        lines = st.slider("표시할 오류 개수", 20, 200, 50, 10, key="error_lines")

        show_log_viewer(error_log, "오류 로그", lines)

    with tab4:
        st.markdown("### 로그 설정")

        st.markdown("#### 현재 설정")

        col1, col2 = st.columns(2)

        with col1:
            st.code(f"""
LOG_DIR: {LOG_DIR}
LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}
            """.strip())

        with col2:
            st.markdown("""
            **로그 레벨 설명:**
            - DEBUG: 디버그 정보
            - INFO: 일반 정보
            - WARNING: 경고
            - ERROR: 오류
            - CRITICAL: 치명적 오류
            """)

        st.markdown("---")

        st.markdown("#### 로그 관리")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ 오래된 로그 삭제 (30일 이상)", type="secondary"):
                cutoff_date = datetime.now() - timedelta(days=30)
                deleted_count = 0

                for log_file in LOG_DIR.glob('*.log.*'):  # Rotated logs
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        deleted_count += 1

                st.success(f"✅ {deleted_count}개 파일 삭제됨")

        with col2:
            if st.button("📦 로그 압축 및 백업"):
                st.info("압축 기능은 구현 예정입니다.")

        st.markdown("---")

        st.markdown("#### 로그 로테이션 정보")

        st.markdown("""
        - **파일 크기 제한**: 10 MB
        - **백업 개수**: 10개 (전체 로그), 5개 (오류 로그)
        - **인코딩**: UTF-8
        - **로테이션 방식**: 크기 기반
        """)

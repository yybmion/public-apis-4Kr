"""
Automated Scheduler

데이터 수집 및 분석 자동화 스케줄러

Schedule:
- 06:00: Fear & Greed Index 수집
- 07:00: FRED 경제 지표 수집
- 08:30: 투자 신호 생성
- 09:00: ECOS 경제 지표 수집 + 일일 브리핑 (개장 전)
- 15:40: 일일 브리핑 (마감 후)
- 월요일 08:00: SEC EDGAR 주간 업데이트

Author: AI Assistant
Created: 2025-11-22
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app.scheduler.collection_jobs import CollectionJobs
from app.scheduler.analysis_jobs import AnalysisJobs
from app.config import Settings

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class StockDataScheduler:
    """
    주식 데이터 수집 및 분석 스케줄러

    Features:
    - 자동 데이터 수집
    - 자동 분석 및 신호 생성
    - 일일 브리핑
    - 작업 실패 시 자동 재시도
    """

    def __init__(self, settings: Optional[Settings] = None, test_mode: bool = False):
        """
        Initialize Scheduler

        Args:
            settings: Application settings
            test_mode: 테스트 모드 (즉시 실행)
        """
        self.settings = settings or Settings()
        self.test_mode = test_mode

        # Initialize jobs
        self.collection_jobs = CollectionJobs(self.settings)
        self.analysis_jobs = AnalysisJobs()

        # Initialize scheduler
        self.scheduler = AsyncIOScheduler()

        # Job results storage
        self.latest_collection_results = None
        self.latest_analysis_results = None

        # Configure scheduler
        self._configure_scheduler()

    def _configure_scheduler(self):
        """Configure scheduler with all jobs"""

        if self.test_mode:
            logger.info("🧪 테스트 모드: 스케줄 무시, 즉시 실행")
            return

        # Job 1: Fear & Greed Index (매일 06:00)
        self.scheduler.add_job(
            self.job_collect_fear_greed,
            CronTrigger(hour=6, minute=0),
            id='fear_greed_collection',
            name='Fear & Greed Index 수집',
            replace_existing=True
        )

        # Job 2: FRED Data (매일 07:00)
        self.scheduler.add_job(
            self.job_collect_fred,
            CronTrigger(hour=7, minute=0),
            id='fred_collection',
            name='FRED 경제 지표 수집',
            replace_existing=True
        )

        # Job 3: Investment Signal (매일 08:30 - 개장 30분 전)
        self.scheduler.add_job(
            self.job_generate_signal,
            CronTrigger(hour=8, minute=30),
            id='signal_generation',
            name='투자 신호 생성',
            replace_existing=True
        )

        # Job 4: ECOS Data + Morning Briefing (매일 09:00 - 개장 직전)
        self.scheduler.add_job(
            self.job_morning_routine,
            CronTrigger(hour=9, minute=0),
            id='morning_routine',
            name='ECOS 수집 + 개장 전 브리핑',
            replace_existing=True
        )

        # Job 5: Afternoon Briefing (매일 15:40 - 마감 후)
        self.scheduler.add_job(
            self.job_afternoon_briefing,
            CronTrigger(hour=15, minute=40),
            id='afternoon_briefing',
            name='마감 후 브리핑',
            replace_existing=True
        )

        # Job 6: SEC EDGAR Weekly Update (매주 월요일 08:00)
        self.scheduler.add_job(
            self.job_collect_sec_edgar,
            CronTrigger(day_of_week='mon', hour=8, minute=0),
            id='sec_edgar_collection',
            name='SEC EDGAR 주간 업데이트',
            replace_existing=True
        )

        # Job 7: Full Daily Analysis (매일 09:30 - 장 시작 후)
        self.scheduler.add_job(
            self.job_full_analysis,
            CronTrigger(hour=9, minute=30),
            id='full_analysis',
            name='전체 분석 실행',
            replace_existing=True
        )

        # Event listeners
        self.scheduler.add_listener(self._job_success_handler, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error_handler, EVENT_JOB_ERROR)

        logger.info("✅ 스케줄러 설정 완료")
        self._print_schedule()

    def _print_schedule(self):
        """Print scheduled jobs"""
        logger.info("\n" + "=" * 80)
        logger.info("📅 스케줄 목록")
        logger.info("=" * 80)

        jobs = self.scheduler.get_jobs()
        for job in sorted(jobs, key=lambda j: str(j.next_run_time)):
            logger.info(f"  {job.next_run_time.strftime('%H:%M')} - {job.name}")

        logger.info("=" * 80 + "\n")

    def _job_success_handler(self, event):
        """Handle successful job execution"""
        job = self.scheduler.get_job(event.job_id)
        if job:
            logger.info(f"✅ 작업 완료: {job.name}")

    def _job_error_handler(self, event):
        """Handle job execution errors"""
        job = self.scheduler.get_job(event.job_id)
        if job:
            logger.error(f"❌ 작업 실패: {job.name} - {event.exception}")

    # ========================================================================
    # Scheduled Jobs
    # ========================================================================

    async def job_collect_fear_greed(self):
        """Job: Fear & Greed Index 수집"""
        logger.info("🎯 [JOB] Fear & Greed Index 수집 시작")
        result = await self.collection_jobs.collect_fear_greed()

        if result.get('success'):
            # Store result
            if not self.latest_collection_results:
                self.latest_collection_results = {}
            self.latest_collection_results['fear_greed'] = result

        return result

    async def job_collect_fred(self):
        """Job: FRED 경제 지표 수집"""
        logger.info("📊 [JOB] FRED 경제 지표 수집 시작")
        result = await self.collection_jobs.collect_fred_data()

        if result.get('success'):
            if not self.latest_collection_results:
                self.latest_collection_results = {}
            self.latest_collection_results['fred'] = result

        return result

    async def job_collect_ecos(self):
        """Job: ECOS 경제 지표 수집"""
        logger.info("🇰🇷 [JOB] ECOS 경제 지표 수집 시작")
        result = await self.collection_jobs.collect_ecos_data()

        if result.get('success'):
            if not self.latest_collection_results:
                self.latest_collection_results = {}
            self.latest_collection_results['ecos'] = result

        return result

    async def job_collect_sec_edgar(self):
        """Job: SEC EDGAR 주간 업데이트"""
        logger.info("🏢 [JOB] SEC EDGAR 주간 업데이트 시작")
        result = await self.collection_jobs.collect_sec_edgar_data()

        if result.get('success'):
            if not self.latest_collection_results:
                self.latest_collection_results = {}
            self.latest_collection_results['sec_edgar'] = result

        return result

    async def job_generate_signal(self):
        """Job: 투자 신호 생성"""
        logger.info("🎯 [JOB] 투자 신호 생성 시작")

        if not self.latest_collection_results:
            logger.warning("⚠️  수집된 데이터 없음 - 신호 생성 불가")
            return {'success': False, 'error': 'No collection data'}

        result = await self.analysis_jobs.generate_investment_signal(
            self.latest_collection_results
        )

        if result.get('success'):
            self.latest_analysis_results = result

        return result

    async def job_morning_routine(self):
        """Job: 아침 루틴 (ECOS 수집 + 브리핑)"""
        logger.info("🌅 [JOB] 아침 루틴 시작 (ECOS + 브리핑)")

        # Collect ECOS data
        await self.job_collect_ecos()

        # Generate briefing
        briefing = await self.analysis_jobs.generate_daily_briefing(
            self.latest_collection_results or {},
            self.latest_analysis_results
        )

        if briefing.get('success'):
            logger.info("\n" + briefing['briefing'])

        return briefing

    async def job_afternoon_briefing(self):
        """Job: 오후 브리핑 (마감 후)"""
        logger.info("🌆 [JOB] 오후 브리핑 시작")

        briefing = await self.analysis_jobs.generate_daily_briefing(
            self.latest_collection_results or {},
            self.latest_analysis_results
        )

        if briefing.get('success'):
            logger.info("\n" + briefing['briefing'])

        return briefing

    async def job_full_analysis(self):
        """Job: 전체 분석 실행"""
        logger.info("🔍 [JOB] 전체 분석 시작")

        if not self.latest_collection_results:
            logger.warning("⚠️  수집된 데이터 없음 - 분석 불가")
            return {'success': False, 'error': 'No collection data'}

        result = await self.analysis_jobs.run_full_analysis(
            self.latest_collection_results
        )

        return result

    # ========================================================================
    # Manual Execution Methods
    # ========================================================================

    async def run_now_collection(self):
        """수집 작업 즉시 실행"""
        logger.info("🚀 수집 작업 즉시 실행")
        result = await self.collection_jobs.collect_all_daily()
        self.latest_collection_results = result.get('results', {})
        return result

    async def run_now_analysis(self):
        """분석 작업 즉시 실행"""
        logger.info("🚀 분석 작업 즉시 실행")

        if not self.latest_collection_results:
            logger.warning("⚠️  먼저 수집 작업을 실행하세요")
            return {'success': False, 'error': 'No collection data'}

        result = await self.analysis_jobs.run_full_analysis(
            self.latest_collection_results
        )
        return result

    async def run_now_full(self):
        """전체 작업 즉시 실행 (수집 + 분석)"""
        logger.info("🚀 전체 작업 즉시 실행")

        # Collection
        collection_result = await self.run_now_collection()

        # Analysis
        analysis_result = await self.run_now_analysis()

        return {
            'collection': collection_result,
            'analysis': analysis_result
        }

    # ========================================================================
    # Scheduler Control
    # ========================================================================

    def start(self):
        """Start scheduler"""
        if not self.test_mode:
            self.scheduler.start()
            logger.info("✅ 스케줄러 시작됨")
        else:
            logger.info("🧪 테스트 모드: 스케줄러 시작 안 함")

    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 스케줄러 종료됨")

    def pause(self):
        """Pause scheduler"""
        if self.scheduler.running:
            self.scheduler.pause()
            logger.info("⏸️  스케줄러 일시정지됨")

    def resume(self):
        """Resume scheduler"""
        if not self.scheduler.running:
            self.scheduler.resume()
            logger.info("▶️  스케줄러 재시작됨")

    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            'running': self.scheduler.running,
            'jobs': len(self.scheduler.get_jobs()),
            'latest_collection': self.latest_collection_results is not None,
            'latest_analysis': self.latest_analysis_results is not None
        }

    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        for job in sorted(jobs, key=lambda j: str(j.next_run_time)):
            print(f"{job.next_run_time} - {job.name}")

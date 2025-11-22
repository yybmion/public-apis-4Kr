"""
LLM Orchestrator
Coordinates multiple LLM agents and aggregates results
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.llm.agents.claude_agent import ClaudeAgent
from app.llm.agents.gpt4_agent import GPT4Agent
from app.llm.agents.gemini_agent import GeminiAgent
from app.llm.agents.grok_agent import GrokAgent
from app.models.llm_analysis import LLMAnalysis, LLMConsensus, LLMPerformance, DataCollectionLog
from app.database.session import get_db
from app.utils.logger import LoggerMixin


class LLMOrchestrator(LoggerMixin):
    """
    LLM Orchestrator

    Coordinates multiple LLM agents in parallel and aggregates results
    """

    def __init__(self, db: Session):
        """
        Initialize orchestrator with database session

        Args:
            db: SQLAlchemy database session
        """
        super().__init__()
        self.db = db

        # Initialize all agents
        self.claude = ClaudeAgent()
        self.gpt4 = GPT4Agent()
        self.gemini = GeminiAgent()
        self.grok = GrokAgent()

        self.agents = {
            'claude': self.claude,
            'gpt4': self.gpt4,
            'gemini': self.gemini,
            'grok': self.grok
        }

        self.logger.info("LLM Orchestrator initialized with 4 agents")

    async def analyze_multi_agent(
        self,
        stock_code: str,
        stock_name: str,
        technical_data: Optional[Dict] = None,
        fundamental_data: Optional[Dict] = None,
        us_market_data: Optional[Dict] = None,
        news_data: Optional[Dict] = None,
        analysis_type: str = "combined_signal"
    ) -> Dict[str, Any]:
        """
        Run analysis with all 4 LLM agents in parallel

        Args:
            stock_code: Stock code
            stock_name: Stock name
            technical_data: Technical analysis data
            fundamental_data: Fundamental data
            us_market_data: US market data
            news_data: News data
            analysis_type: Type of analysis ('news_risk', 'combined_signal', 'explanation')

        Returns:
            Aggregated analysis results with consensus
        """
        self.logger.info(f"Starting multi-agent analysis for {stock_code} - {analysis_type}")

        start_time = datetime.now()

        # Run all agents in parallel
        if analysis_type == "news_risk":
            results = await self._run_news_risk_analysis(news_data or {})
        elif analysis_type == "combined_signal":
            results = await self._run_combined_signal_analysis(
                stock_code, stock_name,
                technical_data, fundamental_data, us_market_data, news_data
            )
        elif analysis_type == "explanation":
            results = await self._run_explanation_analysis(
                stock_code, stock_name,
                {"technical": technical_data, "fundamental": fundamental_data}
            )
        else:
            raise ValueError(f"Invalid analysis_type: {analysis_type}")

        # Log individual analyses to database
        analysis_ids = {}
        for model_name, result in results.items():
            if result.get('success'):
                analysis_id = self._save_llm_analysis(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    analysis_type=analysis_type,
                    llm_model=model_name,
                    result=result
                )
                analysis_ids[f"{model_name}_analysis_id"] = analysis_id

        # Calculate consensus
        consensus = self._calculate_consensus(results, analysis_type)

        # Save consensus to database
        consensus_id = self._save_consensus(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_type=analysis_type,
            analysis_ids=analysis_ids,
            consensus=consensus
        )

        # Update performance metrics
        for model_name, result in results.items():
            if result.get('success'):
                self._update_performance(model_name, result)

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds() * 1000

        self.logger.info(
            f"Multi-agent analysis completed in {total_duration:.0f}ms - "
            f"Consensus: {consensus['decision']} ({consensus['confidence']:.1f}%)"
        )

        return {
            'consensus_id': consensus_id,
            'stock_code': stock_code,
            'stock_name': stock_name,
            'analysis_type': analysis_type,
            'individual_results': results,
            'consensus': consensus,
            'total_duration_ms': int(total_duration),
            'timestamp': end_time.isoformat()
        }

    async def _run_news_risk_analysis(self, news_data: Dict) -> Dict[str, Dict]:
        """Run news risk analysis with all agents"""
        tasks = {
            'claude': self.claude.analyze_news_risk(news_data),
            'gpt4': self.gpt4.analyze_news_risk(news_data),
            'gemini': self.gemini.analyze_news_risk(news_data),
            'grok': self.grok.analyze_news_risk(news_data)
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        return {
            model: result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for model, result in zip(tasks.keys(), results)
        }

    async def _run_combined_signal_analysis(
        self,
        stock_code: str,
        stock_name: str,
        technical_data: Optional[Dict],
        fundamental_data: Optional[Dict],
        us_market_data: Optional[Dict],
        news_data: Optional[Dict]
    ) -> Dict[str, Dict]:
        """Run combined signal analysis with all agents"""
        tasks = {
            'claude': self.claude.generate_combined_signal(
                technical_data, fundamental_data, us_market_data, news_data
            ),
            'gpt4': self.gpt4.generate_combined_signal(
                technical_data, fundamental_data, us_market_data, news_data
            ),
            'gemini': self.gemini.generate_combined_signal(
                technical_data, fundamental_data, us_market_data, news_data
            ),
            'grok': self.grok.generate_combined_signal(
                technical_data, fundamental_data, us_market_data, news_data
            )
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        return {
            model: result if not isinstance(result, Exception) else {'success': False, 'error': str(result)}
            for model, result in zip(tasks.keys(), results)
        }

    async def _run_explanation_analysis(
        self,
        stock_code: str,
        stock_name: str,
        analysis_data: Dict
    ) -> Dict[str, Dict]:
        """Run beginner explanation with all agents"""
        tasks = {
            'claude': self.claude.explain_for_beginner(stock_code, stock_name, analysis_data),
            'gpt4': self.gpt4.explain_for_beginner(stock_code, stock_name, analysis_data),
            'gemini': self.gemini.explain_for_beginner(stock_code, stock_name, analysis_data),
            'grok': self.grok.explain_for_beginner(stock_code, stock_name, analysis_data)
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        # Convert string results to dict format
        formatted_results = {}
        for model, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                formatted_results[model] = {'success': False, 'error': str(result)}
            elif isinstance(result, str):
                formatted_results[model] = {
                    'success': True,
                    'explanation': result,
                    'decision': None,
                    'confidence': None
                }
            else:
                formatted_results[model] = result

        return formatted_results

    def _calculate_consensus(self, results: Dict[str, Dict], analysis_type: str) -> Dict[str, Any]:
        """
        Calculate consensus from multiple LLM results

        Args:
            results: Dictionary of results from each model
            analysis_type: Type of analysis

        Returns:
            Consensus decision and metadata
        """
        # Count votes for each decision
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        confidences = []
        successful_models = []

        for model_name, result in results.items():
            if result.get('success') and result.get('decision'):
                decision = result['decision'].upper()
                if decision in votes:
                    votes[decision] += 1
                    confidences.append(result.get('confidence', 0))
                    successful_models.append(model_name)

        total_models = len(successful_models)

        if total_models == 0:
            return {
                'decision': 'NO_CONSENSUS',
                'confidence': 0.0,
                'agreement_level': 0.0,
                'votes': votes,
                'successful_models': 0,
                'total_models': 4
            }

        # Determine consensus decision
        max_votes = max(votes.values())
        consensus_decision = [k for k, v in votes.items() if v == max_votes][0]

        # Calculate agreement level (what % of models agreed)
        agreement_level = max_votes / total_models if total_models > 0 else 0

        # Calculate consensus confidence
        if agreement_level >= 0.75:  # 3/4 or 4/4 agree
            consensus_confidence = sum(confidences) / len(confidences) if confidences else 0
            consensus_strength = "STRONG"
        elif agreement_level >= 0.5:  # 2/4 agree
            consensus_confidence = (sum(confidences) / len(confidences)) * 0.7 if confidences else 0
            consensus_strength = "MODERATE"
        else:
            consensus_decision = 'NO_CONSENSUS'
            consensus_confidence = 0.0
            consensus_strength = "WEAK"

        return {
            'decision': consensus_decision,
            'confidence': round(consensus_confidence, 2),
            'agreement_level': round(agreement_level, 2),
            'strength': consensus_strength,
            'votes': votes,
            'successful_models': total_models,
            'total_models': 4,
            'avg_confidence': round(sum(confidences) / len(confidences), 2) if confidences else 0
        }

    def _save_llm_analysis(
        self,
        stock_code: str,
        stock_name: str,
        analysis_type: str,
        llm_model: str,
        result: Dict
    ) -> int:
        """
        Save individual LLM analysis to database

        Returns:
            Analysis ID
        """
        try:
            analysis = LLMAnalysis(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_type=analysis_type,
                llm_model=llm_model,
                model_version=result.get('model_version'),
                input_data=result.get('input_data', {}),
                llm_response=result.get('raw_response', ''),
                parsed_result=result.get('parsed_result', {}),
                decision=result.get('decision'),
                confidence=result.get('confidence'),
                tokens_used=result.get('tokens_used'),
                cost=result.get('cost'),
                latency_ms=result.get('latency_ms'),
                success=result.get('success', True),
                error_message=result.get('error')
            )

            self.db.add(analysis)
            self.db.commit()
            self.db.refresh(analysis)

            return analysis.id
        except Exception as e:
            self.logger.error(f"Error saving LLM analysis: {e}")
            self.db.rollback()
            return -1

    def _save_consensus(
        self,
        stock_code: str,
        stock_name: str,
        analysis_type: str,
        analysis_ids: Dict[str, int],
        consensus: Dict
    ) -> int:
        """
        Save consensus result to database

        Returns:
            Consensus ID
        """
        try:
            consensus_record = LLMConsensus(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_type=analysis_type,
                claude_analysis_id=analysis_ids.get('claude_analysis_id'),
                gpt4_analysis_id=analysis_ids.get('gpt4_analysis_id'),
                gemini_analysis_id=analysis_ids.get('gemini_analysis_id'),
                grok_analysis_id=analysis_ids.get('grok_analysis_id'),
                buy_votes=consensus['votes']['BUY'],
                sell_votes=consensus['votes']['SELL'],
                hold_votes=consensus['votes']['HOLD'],
                consensus_decision=consensus['decision'],
                consensus_confidence=consensus['confidence'],
                agreement_level=consensus['agreement_level'],
                avg_confidence=consensus['avg_confidence'],
                recommendation=f"{consensus['strength']} consensus: {consensus['decision']} "
                              f"({consensus['successful_models']}/{consensus['total_models']} models agree)"
            )

            self.db.add(consensus_record)
            self.db.commit()
            self.db.refresh(consensus_record)

            return consensus_record.id
        except Exception as e:
            self.logger.error(f"Error saving consensus: {e}")
            self.db.rollback()
            return -1

    def _update_performance(self, model_name: str, result: Dict):
        """Update aggregated performance metrics for a model"""
        try:
            # Get or create performance record
            perf = self.db.query(LLMPerformance).filter(
                LLMPerformance.llm_model == model_name
            ).first()

            if not perf:
                perf = LLMPerformance(llm_model=model_name)
                self.db.add(perf)

            # Update counters
            perf.total_requests = (perf.total_requests or 0) + 1
            perf.total_tokens = (perf.total_tokens or 0) + result.get('tokens_used', 0)
            perf.total_cost = (perf.total_cost or 0.0) + result.get('cost', 0.0)

            # Update latency (moving average)
            current_latency = result.get('latency_ms', 0)
            if perf.avg_latency_ms:
                perf.avg_latency_ms = (perf.avg_latency_ms * (perf.total_requests - 1) + current_latency) / perf.total_requests
            else:
                perf.avg_latency_ms = current_latency

            # Update decision counts
            decision = result.get('decision', '').upper()
            if decision == 'BUY':
                perf.buy_count = (perf.buy_count or 0) + 1
            elif decision == 'SELL':
                perf.sell_count = (perf.sell_count or 0) + 1
            elif decision == 'HOLD':
                perf.hold_count = (perf.hold_count or 0) + 1

            # Update success rate
            success = 1 if result.get('success') else 0
            if perf.success_rate is not None:
                perf.success_rate = (perf.success_rate * (perf.total_requests - 1) + success) / perf.total_requests
            else:
                perf.success_rate = success

            perf.last_used_at = datetime.now()

            self.db.commit()

        except Exception as e:
            self.logger.error(f"Error updating performance for {model_name}: {e}")
            self.db.rollback()

    def get_model_performance(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for one or all models

        Args:
            model_name: Specific model name, or None for all models

        Returns:
            Performance metrics
        """
        try:
            if model_name:
                perf = self.db.query(LLMPerformance).filter(
                    LLMPerformance.llm_model == model_name
                ).first()

                if not perf:
                    return {'error': f'No performance data for {model_name}'}

                return self._format_performance(perf)
            else:
                all_perf = self.db.query(LLMPerformance).all()
                return {
                    'models': [self._format_performance(p) for p in all_perf],
                    'total_models': len(all_perf)
                }
        except Exception as e:
            self.logger.error(f"Error getting performance: {e}")
            return {'error': str(e)}

    def _format_performance(self, perf: LLMPerformance) -> Dict:
        """Format performance record as dictionary"""
        return {
            'model': perf.llm_model,
            'total_requests': perf.total_requests,
            'total_tokens': perf.total_tokens,
            'total_cost': round(perf.total_cost, 4) if perf.total_cost else 0,
            'avg_latency_ms': round(perf.avg_latency_ms, 2) if perf.avg_latency_ms else 0,
            'success_rate': round(perf.success_rate * 100, 2) if perf.success_rate else 0,
            'accuracy': round(perf.accuracy * 100, 2) if perf.accuracy else None,
            'decisions': {
                'buy': perf.buy_count or 0,
                'sell': perf.sell_count or 0,
                'hold': perf.hold_count or 0
            },
            'last_used': perf.last_used_at.isoformat() if perf.last_used_at else None
        }

    def log_data_collection(
        self,
        collector_type: str,
        action: str,
        target_code: str,
        success: bool,
        records_collected: int = 0,
        duration_ms: int = 0,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log data collection activity

        Args:
            collector_type: Type of collector ('kis', 'yahoo', 'dart', 'news')
            action: Action performed
            target_code: Target stock/index code
            success: Whether collection succeeded
            records_collected: Number of records collected
            duration_ms: Duration in milliseconds
            error_message: Error message if failed
            metadata: Additional metadata
        """
        try:
            log = DataCollectionLog(
                collector_type=collector_type,
                action=action,
                target_code=target_code,
                success=success,
                records_collected=records_collected,
                duration_ms=duration_ms,
                error_message=error_message,
                metadata=metadata or {}
            )

            self.db.add(log)
            self.db.commit()

            self.logger.info(
                f"Data collection logged: {collector_type}/{action} for {target_code} - "
                f"{'Success' if success else 'Failed'} ({records_collected} records)"
            )
        except Exception as e:
            self.logger.error(f"Error logging data collection: {e}")
            self.db.rollback()

"""
Base LLM Agent
Abstract base class for all LLM sub-agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time

from app.utils.logger import LoggerMixin


class BaseLLMAgent(ABC, LoggerMixin):
    """
    Abstract base class for LLM agents
    
    All LLM sub-agents (Claude, GPT-4, Gemini, Grok) inherit from this class
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "unknown"):
        """
        Initialize LLM agent
        
        Args:
            api_key: API key for the LLM service
            model_name: Name of the LLM model
        """
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
    @abstractmethod
    async def analyze_news_risk(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news and assess risks
        
        Args:
            news_data: News articles and sentiment data
            
        Returns:
            Risk assessment results
        """
        pass
    
    @abstractmethod
    async def generate_combined_signal(
        self, 
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        us_market_data: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate combined trading signal from all data sources
        
        Args:
            technical_data: Technical indicators
            fundamental_data: Financial metrics
            us_market_data: US market signals
            news_data: News and sentiment
            
        Returns:
            Combined trading signal (BUY/SELL/HOLD)
        """
        pass
    
    @abstractmethod
    async def explain_for_beginner(
        self,
        stock_code: str,
        stock_name: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Generate beginner-friendly explanation
        
        Args:
            stock_code: Stock code
            stock_name: Stock name
            analysis_data: All analysis results
            
        Returns:
            Easy-to-understand explanation in Korean
        """
        pass
    
    async def call_llm(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call the LLM API (to be implemented by subclasses)
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            LLM response with metadata
        """
        start_time = time.time()
        
        try:
            # Subclasses will implement actual API call
            response = await self._make_api_call(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            elapsed = time.time() - start_time
            
            # Update statistics
            self.request_count += 1
            self.total_tokens += response.get('tokens_used', 0)
            self.total_cost += response.get('cost', 0.0)
            
            self.logger.info(
                f"{self.model_name} API call completed in {elapsed:.2f}s, "
                f"tokens: {response.get('tokens_used', 0)}"
            )
            
            return {
                'success': True,
                'content': response.get('content', ''),
                'tokens_used': response.get('tokens_used', 0),
                'cost': response.get('cost', 0.0),
                'elapsed_time': elapsed,
                'model': self.model_name
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"{self.model_name} API call failed: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': elapsed,
                'model': self.model_name
            }
    
    @abstractmethod
    async def _make_api_call(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Make actual API call to LLM service
        
        To be implemented by each subclass with their specific API
        """
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get agent statistics
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            'model_name': self.model_name,
            'request_count': self.request_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'avg_tokens_per_request': (
                self.total_tokens / self.request_count 
                if self.request_count > 0 else 0
            )
        }
    
    def format_stock_data_prompt(
        self,
        stock_code: str,
        stock_name: str,
        technical: Dict,
        fundamental: Dict,
        us_market: Dict,
        news: Dict
    ) -> str:
        """
        Format all stock data into a structured prompt
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""
주식 종합 분석 요청

종목 정보:
- 코드: {stock_code}
- 이름: {stock_name}

기술적 분석:
- RSI: {technical.get('rsi', 'N/A')}
- MACD: {technical.get('macd', 'N/A')}
- 이동평균 추세: {technical.get('ma_trend', 'N/A')}
- 패턴: {technical.get('pattern', 'N/A')}
- 추세 강도: {technical.get('trend_strength', 'N/A')}/100

재무 분석:
- ROE: {fundamental.get('roe', 'N/A')}%
- PER: {fundamental.get('per', 'N/A')}
- 배당수익률: {fundamental.get('dividend_yield', 'N/A')}%
- 시가총액: {fundamental.get('market_cap', 'N/A')}원
- 점수: {fundamental.get('score', 'N/A')}/100

미국 시장:
- S&P 500 신호: {us_market.get('signal', 'N/A')}
- 신뢰도: {us_market.get('confidence', 'N/A')}%
- S&P 500 종가: ${us_market.get('sp500_close', 'N/A')}
- MA(20): ${us_market.get('sp500_ma20', 'N/A')}

뉴스 및 감성:
- 전체 감성: {news.get('overall', 'N/A')}
- 평균 점수: {news.get('average_score', 'N/A')}
- 긍정 기사: {news.get('positive_count', 'N/A')}개
- 부정 기사: {news.get('negative_count', 'N/A')}개
"""
        return prompt.strip()

"""
Claude LLM Agent
Anthropic Claude API integration
"""

from typing import Dict, Any, Optional
import os

from app.llm.agents.base_agent import BaseLLMAgent


class ClaudeAgent(BaseLLMAgent):
    """
    Claude (Anthropic) sub-agent
    
    Strengths:
    - Long context understanding
    - Detailed reasoning
    - News analysis and risk assessment
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude agent
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        super().__init__(api_key=api_key, model_name='claude-sonnet-4')
        
        # Claude-specific settings
        self.max_tokens = 4000
        self.model_id = 'claude-sonnet-4-20250514'
    
    async def _make_api_call(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Make API call to Claude
        """
        try:
            # Import here to make it optional
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a professional stock market analyst.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            
            # Approximate cost (Claude Sonnet pricing)
            cost = (message.usage.input_tokens * 0.003 / 1000) + \
                   (message.usage.output_tokens * 0.015 / 1000)
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'cost': cost
            }
            
        except ImportError:
            self.logger.warning("anthropic library not installed, using mock response")
            return self._mock_response(prompt)
        except Exception as e:
            self.logger.error(f"Claude API error: {str(e)}")
            raise
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response for testing without API key"""
        return {
            'content': f"[MOCK] Claude 분석 결과: {prompt[:100]}...",
            'tokens_used': 500,
            'cost': 0.01
        }
    
    async def analyze_news_risk(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news and assess risks using Claude
        """
        prompt = f"""
다음 뉴스 데이터를 분석하여 투자 리스크를 평가해주세요.

뉴스 데이터:
{news_data}

다음 형식으로 답변해주세요:
1. 주요 리스크 요인 (3개)
2. 긍정적 요인 (3개)
3. 종합 리스크 점수 (0-100, 높을수록 위험)
4. 투자 권장 사항

답변은 JSON 형식으로 해주세요.
"""
        
        system_prompt = """당신은 한국 주식 시장 전문가입니다. 
뉴스 기사를 깊이 있게 분석하여 숨겨진 리스크를 발견하는 것이 특기입니다."""
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        return response
    
    async def generate_combined_signal(
        self,
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        us_market_data: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate combined trading signal
        """
        stock_code = technical_data.get('stock_code', 'UNKNOWN')
        stock_name = technical_data.get('stock_name', 'UNKNOWN')
        
        prompt = self.format_stock_data_prompt(
            stock_code=stock_code,
            stock_name=stock_name,
            technical=technical_data,
            fundamental=fundamental_data,
            us_market=us_market_data,
            news=news_data
        )
        
        prompt += """

위 데이터를 종합하여 다음을 JSON 형식으로 제공해주세요:

{
  "decision": "BUY" | "SELL" | "HOLD",
  "confidence": 0-100,
  "reasoning": "상세한 이유 (3-5문장)",
  "target_price_change": "+15%" 형식,
  "risks": ["리스크1", "리스크2"],
  "opportunities": ["기회1", "기회2"],
  "holding_period": "1-3개월" 형식
}
"""
        
        system_prompt = "당신은 모든 데이터를 종합하여 최적의 투자 결정을 내리는 전문가입니다."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.5
        )
        
        return response
    
    async def explain_for_beginner(
        self,
        stock_code: str,
        stock_name: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Generate beginner-friendly explanation
        """
        prompt = f"""
종목: {stock_name} ({stock_code})

분석 결과:
{analysis_data}

위 분석 결과를 완전 초보 투자자도 이해할 수 있게 쉽게 설명해주세요.

다음 내용을 포함해주세요:
1. 이 주식이 왜 좋은지 (또는 나쁜지)를 은행 예금, 부동산 같은 친숙한 것에 비유
2. 구체적인 금액 예시 (100만원 투자 시)
3. 언제, 얼마나 사야 하는지
4. 주의사항
5. 초보자 팁

반말로, 친근하게 작성해주세요.
"""
        
        system_prompt = "당신은 초보자에게 주식을 쉽게 설명하는 친절한 선생님입니다."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2500,
            temperature=0.7
        )
        
        if response['success']:
            return response['content']
        else:
            return "설명 생성 중 오류가 발생했습니다."

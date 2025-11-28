"""
Gemini LLM Agent
Google Gemini API integration
"""

from typing import Dict, Any, Optional
import os

from app.llm.agents.base_agent import BaseLLMAgent


class GeminiAgent(BaseLLMAgent):
    """
    Gemini (Google) sub-agent
    
    Strengths:
    - Multilingual understanding
    - Visual and textual analysis
    - Beginner-friendly explanations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini agent
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        super().__init__(api_key=api_key, model_name='gemini-pro')
        
        # Gemini-specific settings
        self.max_tokens = 4000
        self.model_id = 'gemini-pro'
    
    async def _make_api_call(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Make API call to Gemini
        """
        try:
            # Import here to make it optional
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_id)
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': max_tokens,
                }
            )
            
            content = response.text
            # Gemini doesn't provide token count easily, approximate
            tokens_used = len(content.split()) * 1.3
            
            # Approximate cost (Gemini Pro pricing)
            cost = (tokens_used * 0.00025 / 1000)
            
            return {
                'content': content,
                'tokens_used': int(tokens_used),
                'cost': cost
            }
            
        except ImportError:
            self.logger.warning("google-generativeai library not installed, using mock response")
            return self._mock_response(prompt)
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response for testing without API key"""
        return {
            'content': f"[MOCK] Gemini 분석 결과: {prompt[:100]}...",
            'tokens_used': 450,
            'cost': 0.005
        }
    
    async def analyze_news_risk(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news and assess risks using Gemini
        """
        prompt = f"""
다음 뉴스 데이터를 분석하여 투자 리스크를 평가해주세요.

뉴스 데이터:
{news_data}

JSON 형식으로 답변:
{{
  "key_risks": ["리스크1", "리스크2", "리스크3"],
  "positive_factors": ["긍정요인1", "긍정요인2", "긍정요인3"],
  "risk_score": 0-100,
  "recommendation": "투자 권장 사항"
}}
"""
        
        system_prompt = "당신은 한국 주식 시장 뉴스 분석 전문가입니다."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.4
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

위 데이터를 종합하여 매매 신호를 JSON 형식으로 제공:

{
  "decision": "BUY/SELL/HOLD",
  "confidence": 0-100,
  "reasoning": "종합 분석 이유",
  "target_price_change": "+X%",
  "risks": ["리스크들"],
  "opportunities": ["기회들"],
  "holding_period": "기간"
}
"""
        
        system_prompt = "당신은 여러 데이터를 균형있게 판단하는 전문가입니다."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2500,
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
        Generate beginner-friendly explanation (Gemini's strength)
        """
        prompt = f"""
종목: {stock_name} ({stock_code})

분석 결과:
{analysis_data}

완전 초보자도 이해할 수 있게 아주 쉽게 설명해주세요.

포함 내용:
1. 이 주식이 좋은/나쁜 이유 (친숙한 비유 사용)
2. 100만원 투자 시 구체적 예시
3. 매수/매도 타이밍
4. 주의사항
5. 초보자 팁

친근한 반말로 작성.
"""
        
        system_prompt = "당신은 주식을 처음 접하는 사람에게 쉽게 설명하는 전문가입니다."
        
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

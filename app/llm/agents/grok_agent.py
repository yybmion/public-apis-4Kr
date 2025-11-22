"""
Grok LLM Agent
xAI Grok API integration
"""

from typing import Dict, Any, Optional
import os

from app.llm.agents.base_agent import BaseLLMAgent


class GrokAgent(BaseLLMAgent):
    """
    Grok (xAI) sub-agent
    
    Strengths:
    - Real-time data integration
    - Twitter/X sentiment analysis
    - Scenario planning and prediction
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Grok agent
        
        Args:
            api_key: xAI API key (defaults to XAI_API_KEY env var)
        """
        api_key = api_key or os.getenv('XAI_API_KEY')
        super().__init__(api_key=api_key, model_name='grok-2')
        
        # Grok-specific settings
        self.max_tokens = 4000
        self.model_id = 'grok-2'
    
    async def _make_api_call(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Make API call to Grok
        
        Note: Grok API is similar to OpenAI API
        """
        try:
            # Grok uses OpenAI-compatible API
            import openai
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1"
            )
            
            messages = [
                {"role": "system", "content": system_prompt or "You are a stock market analyst."},
                {"role": "user", "content": prompt}
            ]
            
            response = client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Approximate cost (Grok pricing)
            cost = (tokens_used * 0.005 / 1000)
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'cost': cost
            }
            
        except ImportError:
            self.logger.warning("openai library not installed for Grok, using mock response")
            return self._mock_response(prompt)
        except Exception as e:
            self.logger.error(f"Grok API error: {str(e)}")
            # Fallback to mock if API fails
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response for testing without API key"""
        return {
            'content': f"[MOCK] Grok 분석 결과: {prompt[:100]}...",
            'tokens_used': 550,
            'cost': 0.0075
        }
    
    async def analyze_news_risk(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news and assess risks using Grok
        
        Grok can leverage real-time Twitter/X data for sentiment
        """
        prompt = f"""
Analyze the following news data and assess investment risks.
Consider real-time market sentiment and social media trends.

News Data:
{news_data}

Provide analysis in JSON format:
{{
  "key_risks": ["risk1", "risk2", "risk3"],
  "positive_factors": ["factor1", "factor2", "factor3"],
  "risk_score": 0-100,
  "recommendation": "recommendation",
  "social_sentiment": "Twitter/X sentiment if available"
}}

Answer in Korean.
"""
        
        system_prompt = """You are a real-time market analyst with access to social media trends.
You excel at predicting market movements based on sentiment shifts."""
        
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
        Generate combined trading signal with scenario planning
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

Based on the data, provide trading signal with scenario analysis in JSON:

{
  "decision": "BUY/SELL/HOLD",
  "confidence": 0-100,
  "reasoning": "detailed reasoning",
  "scenarios": {
    "best_case": {"probability": "30%", "outcome": "+X%"},
    "base_case": {"probability": "50%", "outcome": "+Y%"},
    "worst_case": {"probability": "20%", "outcome": "-Z%"}
  },
  "target_price_change": "+X%",
  "risks": ["risks"],
  "opportunities": ["opportunities"],
  "holding_period": "period"
}

Answer in Korean.
"""
        
        system_prompt = "You are an expert at scenario planning and probabilistic thinking."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.6
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
Stock: {stock_name} ({stock_code})

Analysis:
{analysis_data}

Explain this to a complete beginner in an engaging, friendly way.

Include:
1. Why this stock matters (use trending topics/memes if relevant)
2. Concrete money examples
3. When and how to buy
4. Risks in simple terms
5. Pro tips

Write in Korean, casual tone (반말).
"""
        
        system_prompt = "You explain complex topics in a fun, relatable way."
        
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

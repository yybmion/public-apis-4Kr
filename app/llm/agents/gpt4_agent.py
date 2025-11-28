"""
GPT-4 LLM Agent
OpenAI GPT-4 API integration
"""

from typing import Dict, Any, Optional
import os

from app.llm.agents.base_agent import BaseLLMAgent


class GPT4Agent(BaseLLMAgent):
    """
    GPT-4 (OpenAI) sub-agent
    
    Strengths:
    - Strong reasoning ability
    - Complex signal prioritization
    - Mathematical analysis
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GPT-4 agent
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        super().__init__(api_key=api_key, model_name='gpt-4-turbo')
        
        # GPT-4 specific settings
        self.max_tokens = 4000
        self.model_id = 'gpt-4-turbo-2024-04-09'
    
    async def _make_api_call(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Make API call to GPT-4
        """
        try:
            # Import here to make it optional
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            messages = [
                {"role": "system", "content": system_prompt or "You are a professional stock analyst."},
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
            
            # Approximate cost (GPT-4 Turbo pricing)
            cost = (response.usage.prompt_tokens * 0.01 / 1000) + \
                   (response.usage.completion_tokens * 0.03 / 1000)
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'cost': cost
            }
            
        except ImportError:
            self.logger.warning("openai library not installed, using mock response")
            return self._mock_response(prompt)
        except Exception as e:
            self.logger.error(f"GPT-4 API error: {str(e)}")
            raise
    
    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response for testing without API key"""
        return {
            'content': f"[MOCK] GPT-4 분석 결과: {prompt[:100]}...",
            'tokens_used': 600,
            'cost': 0.015
        }
    
    async def analyze_news_risk(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze news and assess risks using GPT-4
        """
        prompt = f"""
Analyze the following news data and assess investment risks.

News Data:
{news_data}

Provide your analysis in JSON format with:
1. key_risks: Array of 3 main risk factors
2. positive_factors: Array of 3 positive factors
3. risk_score: 0-100 (higher = more risky)
4. recommendation: Investment recommendation

Answer in Korean.
"""
        
        system_prompt = """You are a Korean stock market expert specializing in quantitative analysis.
You excel at identifying patterns and statistical correlations."""
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.2
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

Based on the above data, provide a comprehensive trading signal in JSON format:

{
  "decision": "BUY" | "SELL" | "HOLD",
  "confidence": 0-100,
  "reasoning": "Detailed reasoning with statistical evidence",
  "target_price_change": e.g., "+15%",
  "stop_loss": e.g., "-8%",
  "risks": ["risk1", "risk2"],
  "opportunities": ["opportunity1", "opportunity2"],
  "holding_period": e.g., "1-3 months",
  "probability_analysis": "Win probability based on historical patterns"
}

Answer in Korean.
"""
        
        system_prompt = """You are an expert at synthesizing multiple data sources.
You prioritize quantitative evidence over qualitative opinions."""
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.4
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

Analysis Results:
{analysis_data}

Explain the above analysis in a way that a complete beginner can understand.

Include:
1. Why this stock is good/bad, using familiar analogies
2. Concrete examples with specific amounts (e.g., "If you invest 1 million won...")
3. When and how much to buy
4. Warnings and risks
5. Beginner tips

Write in Korean, in a friendly tone (반말).
"""
        
        system_prompt = "You are a friendly teacher explaining stocks to beginners."
        
        response = await self.call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2500,
            temperature=0.6
        )
        
        if response['success']:
            return response['content']
        else:
            return "설명 생성 중 오류가 발생했습니다."

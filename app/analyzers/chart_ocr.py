"""
Chart OCR Analyzer - Analyze Stock Charts with Upstage AI
Stock Intelligence System
"""

import requests
import base64
from typing import Dict, Optional
from pathlib import Path
import io
from PIL import Image

from app.config import settings
from app.utils.logger import LoggerMixin


class ChartOCRAnalyzer(LoggerMixin):
    """
    Analyze stock chart images using Upstage Document AI OCR

    Features:
    - Extract price data from chart images
    - Extract technical indicators from screenshots
    - Pattern recognition
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or settings.UPSTAGE_API_KEY
        self.base_url = settings.UPSTAGE_BASE_URL

        if not self.api_key:
            self.log_warning("Upstage API key not configured")

    def analyze_chart(
        self,
        image_path: str,
        extract_indicators: bool = True
    ) -> Dict[str, any]:
        """
        Analyze chart image and extract data

        Args:
            image_path: Path to chart image
            extract_indicators: Whether to extract technical indicators

        Returns:
            Extracted data dictionary
        """
        if not self.api_key:
            self.log_error("Cannot analyze without API key")
            return {'error': 'API key not configured'}

        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Call Upstage OCR API
            ocr_result = self._call_ocr_api(image_base64)

            if not ocr_result:
                return {'error': 'OCR failed'}

            # Parse OCR result
            parsed_data = self._parse_ocr_result(ocr_result)

            # Extract technical indicators if requested
            if extract_indicators:
                indicators = self._extract_indicators(parsed_data)
                parsed_data['indicators'] = indicators

            self.log_info(f"Chart analysis complete: {image_path}")

            return {
                'success': True,
                'image_path': image_path,
                'data': parsed_data,
                'raw_ocr': ocr_result
            }

        except FileNotFoundError:
            self.log_error(f"Image file not found: {image_path}")
            return {'error': 'Image file not found'}
        except Exception as e:
            self.log_error(f"Chart analysis failed: {str(e)}")
            return {'error': str(e)}

    def _call_ocr_api(self, image_base64: str) -> Optional[Dict]:
        """Call Upstage Document AI OCR API"""
        try:
            url = f"{self.base_url}/document-ai/ocr"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "document": image_base64,
                "output_format": "json"
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                self.log_error(f"OCR API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self.log_error(f"OCR API call failed: {str(e)}")
            return None

    def _parse_ocr_result(self, ocr_result: Dict) -> Dict:
        """
        Parse OCR result and extract relevant data

        Expected data from chart:
        - Current price
        - Moving averages (MA5, MA20, MA60)
        - RSI
        - MACD
        - Volume
        """
        parsed = {
            'current_price': None,
            'ma_5': None,
            'ma_20': None,
            'ma_60': None,
            'rsi': None,
            'macd': None,
            'volume': None,
            'confidence': 0.0
        }

        # Extract text from OCR result
        text = self._extract_text_from_ocr(ocr_result)

        # Parse numbers from text
        numbers = self._extract_numbers(text)

        # Try to identify each value
        # This is a simplified version - real implementation would be more sophisticated

        if numbers:
            # Assume the largest number is the current price
            prices = [n for n in numbers if 1000 < n < 1000000]
            if prices:
                parsed['current_price'] = max(prices)
                parsed['confidence'] = 0.7

            # Look for RSI (typically 0-100)
            rsi_candidates = [n for n in numbers if 0 <= n <= 100]
            if rsi_candidates:
                parsed['rsi'] = rsi_candidates[0]

        self.log_info(f"Parsed OCR data: {parsed}")

        return parsed

    def _extract_text_from_ocr(self, ocr_result: Dict) -> str:
        """Extract all text from OCR result"""
        if not ocr_result:
            return ""

        # Upstage API returns text in 'text' or 'pages' field
        if 'text' in ocr_result:
            return ocr_result['text']
        elif 'pages' in ocr_result:
            texts = []
            for page in ocr_result['pages']:
                if 'text' in page:
                    texts.append(page['text'])
            return ' '.join(texts)

        return str(ocr_result)

    def _extract_numbers(self, text: str) -> list:
        """Extract all numbers from text"""
        import re

        # Find all numbers (including decimals and commas)
        pattern = r'[\d,]+\.?\d*'
        matches = re.findall(pattern, text)

        numbers = []
        for match in matches:
            try:
                # Remove commas and convert to float
                num = float(match.replace(',', ''))
                numbers.append(num)
            except ValueError:
                continue

        return numbers

    def _extract_indicators(self, parsed_data: Dict) -> Dict:
        """Extract technical indicators from parsed data"""
        indicators = {}

        # If we have current price and MAs, calculate relationships
        if parsed_data['current_price'] and parsed_data['ma_20']:
            above_ma = parsed_data['current_price'] > parsed_data['ma_20']
            indicators['above_ma_20'] = above_ma
            indicators['signal'] = 'BULLISH' if above_ma else 'BEARISH'

        # RSI signal
        if parsed_data['rsi']:
            if parsed_data['rsi'] < 30:
                indicators['rsi_signal'] = 'OVERSOLD'
            elif parsed_data['rsi'] > 70:
                indicators['rsi_signal'] = 'OVERBOUGHT'
            else:
                indicators['rsi_signal'] = 'NEUTRAL'

        return indicators

    def analyze_with_ai(
        self,
        image_path: str,
        question: str = "이 차트에서 현재 추세는 무엇인가요?"
    ) -> Dict[str, any]:
        """
        Analyze chart with AI model (CLOVA or GPT)

        This is a placeholder for AI-based chart analysis
        In production, this would call CLOVA Studio or similar API
        """
        self.log_info(f"AI analysis requested for: {image_path}")
        self.log_warning("AI chart analysis not fully implemented (requires CLOVA API)")

        # Mock response
        return {
            'question': question,
            'answer': '차트 분석 기능은 CLOVA Studio API 설정이 필요합니다.',
            'confidence': 0.0,
            'recommendations': [
                '실제 구현을 위해서는 CLOVA Studio API 키가 필요합니다.',
                '또는 OpenAI GPT-4 Vision API를 사용할 수 있습니다.'
            ]
        }

    def validate_chart_image(self, image_path: str) -> bool:
        """
        Validate that image is a valid chart

        Args:
            image_path: Path to image

        Returns:
            True if valid chart image
        """
        try:
            with Image.open(image_path) as img:
                # Check image size
                width, height = img.size

                # Charts are typically wider than tall
                if width < 400 or height < 300:
                    self.log_warning(f"Image too small: {width}x{height}")
                    return False

                # Check aspect ratio
                aspect_ratio = width / height
                if aspect_ratio < 1.0:
                    self.log_warning(f"Unusual aspect ratio for chart: {aspect_ratio}")
                    return False

                self.log_info(f"Valid chart image: {width}x{height}")
                return True

        except Exception as e:
            self.log_error(f"Image validation failed: {str(e)}")
            return False

    def generate_chart_report(self, analysis_result: Dict) -> str:
        """Generate human-readable report from analysis"""
        if not analysis_result.get('success'):
            return f"분석 실패: {analysis_result.get('error', 'Unknown error')}"

        data = analysis_result.get('data', {})
        indicators = data.get('indicators', {})

        report = "📊 차트 분석 결과\n"
        report += "=" * 50 + "\n\n"

        # Price data
        if data.get('current_price'):
            report += f"현재가: {data['current_price']:,.0f}원\n"

        # Moving averages
        if data.get('ma_5'):
            report += f"MA(5):  {data['ma_5']:,.0f}원\n"
        if data.get('ma_20'):
            report += f"MA(20): {data['ma_20']:,.0f}원\n"
        if data.get('ma_60'):
            report += f"MA(60): {data['ma_60']:,.0f}원\n"

        report += "\n"

        # Technical indicators
        if data.get('rsi'):
            report += f"RSI: {data['rsi']:.2f}\n"

        if data.get('macd'):
            report += f"MACD: {data['macd']:.2f}\n"

        report += "\n"

        # Signals
        if indicators:
            report += "신호:\n"
            if 'signal' in indicators:
                emoji = "🟢" if indicators['signal'] == 'BULLISH' else "🔴"
                report += f"{emoji} {indicators['signal']}\n"

            if 'rsi_signal' in indicators:
                report += f"RSI: {indicators['rsi_signal']}\n"

        # Confidence
        report += f"\n신뢰도: {data.get('confidence', 0) * 100:.1f}%\n"

        return report


class MockChartAnalyzer(LoggerMixin):
    """Mock analyzer for testing without API key"""

    def analyze_chart(self, image_path: str, extract_indicators: bool = True) -> Dict:
        self.log_info(f"[MOCK] Analyzing chart: {image_path}")

        return {
            'success': True,
            'image_path': image_path,
            'data': {
                'current_price': 75000,
                'ma_5': 74800,
                'ma_20': 73500,
                'ma_60': 71000,
                'rsi': 65,
                'macd': 120,
                'volume': 15234567,
                'confidence': 0.85,
                'indicators': {
                    'above_ma_20': True,
                    'signal': 'BULLISH',
                    'rsi_signal': 'NEUTRAL'
                }
            }
        }

    def validate_chart_image(self, image_path: str) -> bool:
        return True

    def generate_chart_report(self, analysis_result: Dict) -> str:
        return "[MOCK] Chart analysis report"

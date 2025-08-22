# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import re
import sys
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class LinkResult:
  url: str
  api_name: str
  category: str
  status_code: int
  is_working: bool
  error_type: str
  error_message: str
  response_time: float
  redirect_url: Optional[str] = None

class KoreanAPILinkChecker:
  def __init__(self, max_concurrent: int = 30, timeout: int = 15):
    self.max_concurrent = max_concurrent
    self.timeout = timeout
    self.semaphore = asyncio.Semaphore(max_concurrent)
    self.user_agents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

  def extract_api_links(self, filename: str) -> List[Tuple[str, str, str]]:
    with open(filename, 'r', encoding='utf-8') as file:
      content = file.read()

    links = []
    current_category = ""
    lines = content.split('\n')

    for line in lines:
      if line.startswith('### '):
        current_category = line.replace('### ', '').strip()
        continue

      if line.startswith('|') and not line.startswith('|---'):
        cells = [cell.strip() for cell in line.split('|')[1:-1]]

        if len(cells) >= 3:
          api_cell = cells[0]
          link_match = re.search(r'\[([^\]]+)\]\((https?://[^\)]+)\)', api_cell)
          if link_match:
            api_name = link_match.group(1)
            url = link_match.group(2)
            links.append((url, api_name, current_category))

    return links

  async def check_single_link(self, session: aiohttp.ClientSession,
      url: str, api_name: str, category: str) -> LinkResult:
    async with self.semaphore:
      start_time = time.time()

      try:
        import random
        headers = {
          'User-Agent': random.choice(self.user_agents),
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
          'Accept-Encoding': 'gzip, deflate',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
        }

        async with session.get(
            url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            allow_redirects=True,
            ssl=False
        ) as response:
          response_time = time.time() - start_time
          redirect_url = str(response.url) if str(response.url) != url else None
          is_working = response.status < 400
          error_type = ""
          error_message = ""

          if not is_working:
            if response.status == 403:
              error_type = "FORBIDDEN"
              error_message = "접근 거부 (IP 차단 또는 지역 제한 가능)"
            elif response.status == 404:
              error_type = "NOT_FOUND"
              error_message = "페이지를 찾을 수 없음"
            elif response.status == 500:
              error_type = "SERVER_ERROR"
              error_message = "서버 내부 오류"
            else:
              error_type = "HTTP_ERROR"
              error_message = f"HTTP {response.status}"

          return LinkResult(
              url=url,
              api_name=api_name,
              category=category,
              status_code=response.status,
              is_working=is_working,
              error_type=error_type,
              error_message=error_message,
              response_time=response_time,
              redirect_url=redirect_url
          )

      except asyncio.TimeoutError:
        return LinkResult(
            url=url,
            api_name=api_name,
            category=category,
            status_code=0,
            is_working=False,
            error_type="TIMEOUT",
            error_message=f"{self.timeout}초 시간 초과",
            response_time=self.timeout
        )
      except aiohttp.ClientConnectorError:
        return LinkResult(
            url=url,
            api_name=api_name,
            category=category,
            status_code=0,
            is_working=False,
            error_type="CONNECTION_ERROR",
            error_message="연결 실패 (도메인 오류 또는 네트워크 문제)",
            response_time=0
        )
      except aiohttp.ClientSSLError:
        return LinkResult(
            url=url,
            api_name=api_name,
            category=category,
            status_code=0,
            is_working=False,
            error_type="SSL_ERROR",
            error_message="SSL 인증서 문제",
            response_time=0
        )
      except Exception as e:
        return LinkResult(
            url=url,
            api_name=api_name,
            category=category,
            status_code=0,
            is_working=False,
            error_type="UNKNOWN_ERROR",
            error_message=str(e)[:100],
            response_time=0
        )

  async def check_all_links(self, links: List[Tuple[str, str, str]]) -> List[LinkResult]:
    connector = aiohttp.TCPConnector(
        limit=self.max_concurrent,
        limit_per_host=10,
        ttl_dns_cache=300,
        use_dns_cache=True,
    )

    async with aiohttp.ClientSession(connector=connector) as session:
      tasks = [
        self.check_single_link(session, url, api_name, category)
        for url, api_name, category in links
      ]

      results = []
      batch_size = 20

      for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)

        for j, result in enumerate(batch_results):
          if isinstance(result, Exception):
            url, api_name, category = links[i + j]
            results.append(LinkResult(
                url=url,
                api_name=api_name,
                category=category,
                status_code=0,
                is_working=False,
                error_type="EXCEPTION",
                error_message=str(result)[:100],
                response_time=0
            ))
          else:
            results.append(result)

        print(f"진행률: {min(i + batch_size, len(tasks))}/{len(tasks)} 완료")

      return results

  def generate_report(self, results: List[LinkResult]) -> str:
    total = len(results)
    working = sum(1 for r in results if r.is_working)
    broken = total - working

    category_stats = {}
    for result in results:
      cat = result.category
      if cat not in category_stats:
        category_stats[cat] = {'total': 0, 'working': 0, 'broken': 0}

      category_stats[cat]['total'] += 1
      if result.is_working:
        category_stats[cat]['working'] += 1
      else:
        category_stats[cat]['broken'] += 1

    report = f"""
🔗 한국 Public API 링크 상태 리포트
================================
검사 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
총 API 수: {total}개
정상 링크: {working}개 ({working/total*100:.1f}%)
깨진 링크: {broken}개 ({broken/total*100:.1f}%)

📊 카테고리별 상태:
"""

    for category, stats in category_stats.items():
      working_pct = (stats['working'] / stats['total']) * 100 if stats['total'] > 0 else 0
      status_emoji = "✅" if stats['broken'] == 0 else "⚠️" if stats['broken'] <= 2 else "❌"
      report += f"{status_emoji} {category}: {stats['working']}/{stats['total']} ({working_pct:.1f}%)\n"

    if broken > 0:
      report += f"\n🚨 깨진 링크 상세 목록 ({broken}개):\n"
      report += "=" * 60 + "\n"

      error_groups = {}
      for result in results:
        if not result.is_working:
          error_type = result.error_type
          if error_type not in error_groups:
            error_groups[error_type] = []
          error_groups[error_type].append(result)

      for error_type, error_results in error_groups.items():
        report += f"\n📋 {error_type} ({len(error_results)}개):\n"
        for result in error_results:
          report += f"   ❌ [{result.api_name}]({result.url})\n"
          report += f"      카테고리: {result.category}\n"
          report += f"      상태: {result.status_code} - {result.error_message}\n"
          if result.redirect_url:
            report += f"      리다이렉트: {result.redirect_url}\n"
          report += "\n"

    return report

  def save_results(self, results: List[LinkResult], filename: str = 'link_health_report.json'):
    data = {
      'generated_at': datetime.now().isoformat(),
      'total_links': len(results),
      'working_links': sum(1 for r in results if r.is_working),
      'broken_links': sum(1 for r in results if not r.is_working),
      'results': [asdict(result) for result in results]
    }

    with open(filename, 'w', encoding='utf-8') as f:
      json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"📄 상세 결과가 {filename}에 저장되었습니다.")


async def main():
  if len(sys.argv) < 2:
    print("사용법: python link_health_check.py <README파일> [--save-json] [--concurrent N]")
    print("예시: python link_health_check.py README.md --save-json --concurrent 20")
    sys.exit(1)

  filename = sys.argv[1]
  save_json = '--save-json' in sys.argv

  concurrent = 30
  if '--concurrent' in sys.argv:
    try:
      idx = sys.argv.index('--concurrent')
      concurrent = int(sys.argv[idx + 1])
    except (IndexError, ValueError):
      print("⚠️ concurrent 값이 잘못되었습니다. 기본값 30을 사용합니다.")

  print(f"🚀 한국 Public API 링크 상태 검사 시작")
  print(f"📄 파일: {filename}")
  print(f"⚡ 동시 요청 수: {concurrent}")
  print("-" * 50)

  checker = KoreanAPILinkChecker(max_concurrent=concurrent)

  try:
    print("🔍 README에서 API 링크 추출 중...")
    links = checker.extract_api_links(filename)
    print(f"📊 총 {len(links)}개 API 링크 발견")

    if not links:
      print("❌ 링크를 찾을 수 없습니다. 파일 형식을 확인해주세요.")
      sys.exit(1)

    print("\n🌐 링크 상태 검사 시작...")
    start_time = time.time()
    results = await checker.check_all_links(links)
    elapsed_time = time.time() - start_time

    print(f"⏱️ 검사 완료 (소요시간: {elapsed_time:.1f}초)")

    broken_count = sum(1 for r in results if not r.is_working)

    report = checker.generate_report(results)
    print(report)

    if save_json:
      checker.save_results(results)

    if broken_count > 0:
      print(f"\n💥 {broken_count}개의 깨진 링크가 발견되었습니다!")
      print("🔧 위의 링크들을 수정하거나 제거해주세요.")
      sys.exit(1)
    else:
      print("\n🎉 모든 링크가 정상적으로 작동합니다!")
      sys.exit(0)

  except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {filename}")
    sys.exit(1)
  except KeyboardInterrupt:
    print("\n⏹️ 사용자에 의해 중단되었습니다.")
    sys.exit(1)
  except Exception as e:
    print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
    sys.exit(1)


if __name__ == '__main__':
  if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

  asyncio.run(main())

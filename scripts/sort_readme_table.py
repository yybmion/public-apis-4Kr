#!/usr/bin/env python3

"""
README 파일의 각 섹션 내 API 목록을 정렬하는 스크립트

- README.md: 한글 ㄱ,ㄴ,ㄷ 순
- README_EN.md: 알파벳 A-Z 순

사용법: python scripts/sort_readme_table.py
"""

import re
from pathlib import Path


def extract_api_name(row):
    """테이블 행에서 API 이름 추출"""
    match = re.search(r'\|\s*\[([^\]]+)\]', row)
    if match:
        return match.group(1)
    match = re.search(r'\[([^\]]+)\]\([^)]+\)', row)
    if match:
        return match.group(1)
    return row


def get_korean_sort_key(name):
    """한글 정렬을 위한 키 생성 (한글 먼저, 영문/숫자는 뒤로)"""
    first_char = name[0] if name else ''
    if '\uAC00' <= first_char <= '\uD7A3':
        return (0, name.lower())
    elif '\u3131' <= first_char <= '\u3163':
        return (0, name.lower())
    else:
        return (1, name.lower())


def sort_section_tables(content, sort_key_func):
    """섹션 내의 테이블 행들을 정렬"""
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        result.append(line)

        if re.match(r'\|\s*(API|API\s+)\s*\|', line, re.IGNORECASE):
            i += 1
            if i < len(lines):
                result.append(lines[i])
                i += 1

                table_rows = []
                while i < len(lines) and lines[i].strip().startswith('|') and not lines[i].strip().startswith('|--'):
                    if '**[⬆' in lines[i] or lines[i].strip() == '|':
                        break
                    table_rows.append(lines[i])
                    i += 1

                if table_rows:
                    table_rows.sort(key=lambda row: sort_key_func(extract_api_name(row)))
                    result.extend(table_rows)

                continue

        i += 1

    return '\n'.join(result)


def main():
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    readme_path = project_root / "README.md"
    readme_en_path = project_root / "README_EN.md"

    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        sorted_content = sort_section_tables(content, get_korean_sort_key)
        readme_path.write_text(sorted_content, encoding="utf-8")
        print(f"✓ {readme_path.name} 정렬 완료 (한글 ㄱ,ㄴ,ㄷ 순)")
    else:
        print(f"✗ {readme_path} 파일을 찾을 수 없습니다.")

    if readme_en_path.exists():
        content_en = readme_en_path.read_text(encoding="utf-8")
        sorted_content_en = sort_section_tables(content_en, lambda name: name.lower())
        readme_en_path.write_text(sorted_content_en, encoding="utf-8")
        print(f"✓ {readme_en_path.name} 정렬 완료 (알파벳 A-Z 순)")
    else:
        print(f"✗ {readme_en_path} 파일을 찾을 수 없습니다.")


if __name__ == "__main__":
    main()


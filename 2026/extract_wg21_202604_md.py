#!/usr/bin/env python3
import re
from pathlib import Path
p = Path('2026/wg21_2026_04.txt')
text = p.read_text(encoding='utf-8')
rows = re.findall(r'<tr\b[^>]*>(.*?)</tr>', text, re.S|re.I)
lines = []
for row in rows:
    tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S|re.I)
    if not tds:
        continue
    m = re.search(r'<a\s+href="([^"]+)">([^<]+)</a>', tds[0], re.I)
    if not m:
        continue
    href = m.group(1).strip()
    id_ = m.group(2).strip()
    title = ''
    if len(tds) >= 2:
        title = re.sub(r'<[^>]+>', '', tds[1]).strip()
    if href.startswith('../'):
        href2 = href[3:]
    else:
        href2 = href.lstrip('./')
    abs_url = 'https://www.open-std.org/jtc1/sc22/wg21/docs/papers/' + href2
    lines.append(f"### [{id_} {title}]({abs_url})")
out = Path('2026/wg21_papers_202604.md')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('wrote', len(lines), 'entries to', out)

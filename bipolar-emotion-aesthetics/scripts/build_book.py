#!/usr/bin/env python3
"""由 references/*.md 生成 docs/theory-book.html（单一事实源）。

理论正文只维护 bipolar-emotion-aesthetics/references/ 下的 Markdown；
本脚本负责渲染为带目录的单页在线著作。仅用标准库，离线可用。

用法（在仓库根目录执行）：
  python3 bipolar-emotion-aesthetics/scripts/build_book.py
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
REPO = os.path.dirname(SKILL)
OUT = os.path.join(REPO, "docs", "theory-book.html")

# (章节标题, 相对技能目录的文件)
CHAPTERS = [
    ("第一编 · 本体与机制", "references/theory.md"),
    ("第二编 · 范式连续谱", "references/paradigms.md"),
    ("第三编 · 方法论", "references/method.md"),
    ("第四编 · 领域配方与诊断", "references/playbooks.md"),
    ("第五编 · 审计模板", "references/audit-templates.md"),
    ("第六编 · 提示词语法", "references/bea-prompts.md"),
]


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def render_md(md: str) -> str:
    """极简 Markdown 渲染：标题/表格/列表/引用/分隔线/段落。"""
    out, in_table, in_list, in_code = [], False, False, False
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.strip().startswith("```"):
            if not in_code:
                out.append("<pre><code>")
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            i += 1
            continue
        if in_code:
            out.append(html.escape(line) + "\n")
            i += 1
            continue
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.endswith("|")
        if is_table_row:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if re.fullmatch(r"[:\-\s|]+", stripped):
                i += 1
                continue  # 分隔行
            if not in_table:
                out.append("<table>")
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
                in_table = True
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            i += 1
            continue
        elif in_table:
            out.append("</table>")
            in_table = False
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(stripped[2:])}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if not stripped:
                pass
            elif stripped.startswith("#### "):
                out.append(f"<h4>{inline(stripped[5:])}</h4>")
            elif stripped.startswith("### "):
                out.append(f"<h3>{inline(stripped[4:])}</h3>")
            elif stripped.startswith("## "):
                out.append(f"<h3>{inline(stripped[3:])}</h3>")
            elif stripped.startswith("# "):
                out.append(f"<h3>{inline(stripped[2:])}</h3>")
            elif stripped.startswith("> "):
                out.append(f"<blockquote>{inline(stripped[2:])}</blockquote>")
            elif stripped in ("---", "***"):
                out.append("<hr>")
            else:
                out.append(f"<p>{inline(stripped)}</p>")
        i += 1
    if in_table:
        out.append("</table>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


CSS = """
  :root{--bg:#faf9f7;--card:#fff;--ink:#2b2a28;--sub:#6f6c66;--line:#e8e5e0;--accent:#b5442c;--accent-soft:#f6ebe7;--qing:#7a9e9f}
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:"Noto Serif SC",-apple-system,"PingFang SC",serif;background:var(--bg);color:var(--ink);line-height:1.9}
  .wrap{max-width:820px;margin:0 auto;padding:48px 24px 80px}
  header{text-align:center;margin-bottom:48px}
  header h1{font-size:30px;font-weight:900;letter-spacing:2px}
  header h1 span{color:var(--accent)}
  header p{color:var(--sub);font-size:14px;margin-top:10px}
  .src{display:inline-block;margin-top:14px;font-size:12px;color:var(--qing);border:1px solid var(--qing);border-radius:999px;padding:4px 14px}
  nav{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 26px;margin-bottom:40px}
  nav b{font-size:14px;color:var(--accent)}
  nav ol{margin:10px 0 0 20px;font-size:14px}
  nav a{color:var(--ink);text-decoration:none}
  nav a:hover{color:var(--accent)}
  section{margin-bottom:56px}
  section>h2{font-size:22px;font-weight:800;border-left:5px solid var(--accent);padding-left:14px;margin-bottom:18px}
  h3{font-size:17px;margin:26px 0 10px;color:var(--ink)}
  h4{font-size:15px;margin:20px 0 8px}
  p{font-size:14.5px;margin-bottom:10px}
  table{width:100%;border-collapse:collapse;font-size:13px;margin:14px 0;background:var(--card)}
  th,td{padding:8px 10px;border:1px solid var(--line);text-align:left}
  th{background:var(--accent-soft);color:var(--accent);font-weight:600}
  blockquote{border-left:4px solid var(--qing);background:#eef4f3;padding:10px 16px;border-radius:0 8px 8px 0;font-size:13.5px;margin:12px 0}
  code{background:#f0ede8;border-radius:4px;padding:1px 5px;font-size:12.5px;font-family:Menlo,monospace}
  pre{background:#f0ede8;border-radius:10px;padding:14px;overflow-x:auto;font-size:12.5px;margin:12px 0}
  ul{margin:8px 0 12px 22px;font-size:14px}
  hr{border:none;border-top:1px solid var(--line);margin:24px 0}
  footer{text-align:center;font-size:12px;color:var(--sub);margin-top:48px}
  footer a{color:var(--qing);text-decoration:none}
"""


def main():
    toc, body = [], []
    for idx, (title, rel) in enumerate(CHAPTERS, 1):
        path = os.path.join(SKILL, rel)
        if not os.path.exists(path):
            raise SystemExit(f"缺少章节文件：{path}")
        md = open(path, encoding="utf-8").read()
        toc.append(f'<li><a href="#c{idx}">{html.escape(title)}</a></li>')
        body.append(f'<section id="c{idx}"><h2>{html.escape(title)}</h2>\n{render_md(md)}</section>')

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>双极情绪美学 BEA · 完整理论著作</title>
<meta name="description" content="美感 = 可控张力下的情绪奖赏。BEA 完整理论：本体与机制、范式连续谱、方法论、领域配方、审计模板与提示词语法。">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;800;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>双极情绪美学 <span>BEA</span></h1>
    <p>美感 = 可控张力下的情绪奖赏 · 一套可计算的形式美学</p>
    <div class="src">本页由 build_book.py 从 references/*.md 自动生成 · 理论正文以技能内 Markdown 为准（单一事实源）</div>
  </header>
  <nav><b>目录</b><ol>{''.join(toc)}</ol>
    <p style="margin-top:12px;font-size:13px">配套：<a href="guide.html">🌿 10 分钟读懂 BEA</a> · <a href="index.html">🧮 W(T) 交互计算器</a></p>
  </nav>
  {''.join(body)}
  <footer>
    双极情绪美学 BEA v1.4.0 · 作者 星空本空 · <a href="https://github.com/Maxing0000/bipolar-emotion-aesthetics">GitHub</a> · CC BY 4.0<br>
    0–10 刻度与 W(T) 为协作参照，非心理物理常数
  </footer>
</div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"已生成 {OUT}（{len(page)} 字符，{len(CHAPTERS)} 编）")


if __name__ == "__main__":
    main()

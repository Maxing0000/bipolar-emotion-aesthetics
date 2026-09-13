#!/usr/bin/env python3
"""BEA 案例 Markdown 转 HTML 脚本：把 cases/*.md 转换为 docs/cases/*.html，套用 BEA 样式。"""
import markdown
import os
import re

CASES_DIR = "docs/cases"

# BEA 样式模板
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · BEA 双极情绪美学案例</title>
<meta name="description" content="{title} - BEA双极情绪美学深度分析案例">
<meta name="keywords" content="BEA,双极情绪美学,设计分析,{title}">
<meta name="author" content="星空本空">
<meta name="theme-color" content="#E8A87C">
<meta property="og:title" content="{title} · BEA案例">
<meta property="og:description" content="BEA双极情绪美学深度分析案例">
<meta property="og:type" content="article">
<link rel="canonical" href="https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/{filename}">
<style>
:root{{
  --plus:#E8A87C;--plus-dark:#D4956A;--minus:#4A90A4;--minus-dark:#3A7A8C;
  --bg:#FAF8F5;--bg2:#F0EDE8;--card:#FFFFFF;--text:#2C2C2C;--text2:#666;
  --border:#E5E0D8;--radius:12px;--shadow:0 2px 12px rgba(0,0,0,.06);
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);line-height:1.8;min-height:100vh}}
.bea-nav{{position:sticky;top:0;z-index:100;background:rgba(250,248,245,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 24px}}
.bea-nav-inner{{max-width:900px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:56px}}
.bea-nav-brand{{font-weight:700;font-size:16px;color:var(--text);text-decoration:none;display:flex;align-items:center;gap:8px}}
.bea-nav-brand .logo{{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--plus),var(--minus));display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:14px}}
.bea-nav-links{{display:flex;gap:20px;list-style:none}}
.bea-nav-links a{{color:var(--text2);text-decoration:none;font-size:14px;font-weight:500;transition:color .2s}}
.bea-nav-links a:hover{{color:var(--minus)}}
.bea-nav-links a.active{{color:var(--minus);font-weight:600}}
.bea-nav-mobile-toggle{{display:none;background:none;border:none;font-size:20px;cursor:pointer;color:var(--text)}}
.container{{max-width:860px;margin:0 auto;padding:40px 24px 60px}}
.case-header{{margin-bottom:32px;padding-bottom:24px;border-bottom:2px solid var(--border)}}
.case-header h1{{font-size:28px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,var(--plus-dark),var(--minus-dark));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.case-meta{{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;color:var(--text2)}}
.case-meta span{{background:var(--bg2);padding:4px 12px;border-radius:20px}}
.case-meta .paradigm{{background:linear-gradient(135deg,var(--plus),var(--minus));color:#fff}}
.content h2{{font-size:22px;font-weight:700;margin:32px 0 16px;padding-left:12px;border-left:4px solid var(--plus)}}
.content h3{{font-size:18px;font-weight:600;margin:24px 0 12px;color:var(--minus-dark)}}
.content p{{margin-bottom:16px;color:var(--text)}}
.content strong{{color:var(--plus-dark);font-weight:600}}
.content ul,.content ol{{margin:0 0 16px 24px}}
.content li{{margin-bottom:8px}}
.content table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}}
.content th{{background:linear-gradient(135deg,var(--plus),var(--minus));color:#fff;padding:10px 12px;text-align:left;font-weight:600}}
.content td{{padding:10px 12px;border-bottom:1px solid var(--border)}}
.content tr:nth-child(even){{background:var(--bg2)}}
.content tr:hover{{background:rgba(232,168,124,.08)}}
.content blockquote{{border-left:4px solid var(--minus);background:rgba(74,144,164,.06);padding:12px 20px;margin:16px 0;border-radius:0 8px 8px 0;color:var(--text2)}}
.content code{{background:var(--bg2);padding:2px 6px;border-radius:4px;font-size:13px;font-family:Menlo,monospace}}
.content pre{{background:#2C2C2C;color:#E8E8E8;padding:16px;border-radius:8px;overflow-x:auto;margin:16px 0}}
.content pre code{{background:none;color:inherit;padding:0}}
.content hr{{border:none;border-top:1px solid var(--border);margin:32px 0}}
.back-link{{display:inline-flex;align-items:center;gap:6px;color:var(--minus);text-decoration:none;font-weight:500;margin-bottom:24px;font-size:14px}}
.back-link:hover{{text-decoration:underline}}
.footer{{text-align:center;padding:32px 24px;border-top:1px solid var(--border);color:var(--text2);font-size:13px}}
.footer a{{color:var(--minus);text-decoration:none}}
@media(max-width:768px){{
  .bea-nav-links{{display:none;position:absolute;top:56px;left:0;right:0;background:var(--card);flex-direction:column;padding:16px 24px;gap:12px;border-bottom:1px solid var(--border);box-shadow:var(--shadow)}}
  .bea-nav-links.open{{display:flex}}
  .bea-nav-mobile-toggle{{display:block}}
  .container{{padding:24px 16px 40px}}
  .case-header h1{{font-size:22px}}
  .content h2{{font-size:18px}}
  .content table{{font-size:12px}}
  .content th,.content td{{padding:8px}}
}}
</style>
</head>
<body>
<nav class="bea-nav">
  <div class="bea-nav-inner">
    <a href="../index.html" class="bea-nav-brand"><span class="logo">B</span>BEA 双极情绪美学</a>
    <button class="bea-nav-mobile-toggle" onclick="document.getElementById('beaNavLinks').classList.toggle('open')" aria-label="菜单">☰</button>
    <ul class="bea-nav-links" id="beaNavLinks">
      <li><a href="../index.html">🧮 计算器</a></li>
      <li><a href="../image-analysis.html">🖼️ 图片分析</a></li>
      <li><a href="../quick-diagnosis.html">⚡ 快速诊断</a></li>
      <li><a href="../workbench.html">🔧 工作台</a></li>
      <li><a href="../cases.html" class="active">📚 案例库</a></li>
      <li><a href="../theory-book.html">📖 理论著作</a></li>
    </ul>
  </div>
</nav>
<div class="container">
  <a href="../cases.html" class="back-link">← 返回案例库</a>
  <div class="case-header">
    <h1>{title}</h1>
    <div class="case-meta">
      <span class="paradigm">BEA 双极情绪美学案例</span>
      <span>作者：星空本空</span>
      <span>CC BY 4.0</span>
    </div>
  </div>
  <div class="content">
{body}
  </div>
</div>
<div class="footer">
  <p>BEA 双极情绪美学 · 作者：星空本空 · <a href="https://github.com/Maxing0000/bipolar-emotion-aesthetics" target="_blank">GitHub</a> · CC BY 4.0</p>
</div>
</body>
</html>"""

def convert_md_to_html(md_path, html_path):
    """把单个 Markdown 文件转换为 HTML"""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(md_path).replace('.md', '')

    # 转换 Markdown 为 HTML
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])

    # 生成完整 HTML
    filename = os.path.basename(html_path)
    full_html = HTML_TEMPLATE.format(title=title, body=html_body, filename=filename)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    return title

def main():
    # 转换所有 .md 文件
    converted = []
    for md_file in sorted(os.listdir(CASES_DIR)):
        if not md_file.endswith('.md'):
            continue
        md_path = os.path.join(CASES_DIR, md_file)
        html_file = md_file.replace('.md', '.html')
        html_path = os.path.join(CASES_DIR, html_file)
        title = convert_md_to_html(md_path, html_path)
        converted.append((md_file, html_file, title))
        print(f"✅ {md_file} -> {html_file} ({title})")

    print(f"\n共转换 {len(converted)} 个案例")
    return converted

if __name__ == '__main__':
    main()

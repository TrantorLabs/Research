#!/usr/bin/env python3
"""Build English PDFs 02–05 in the style of Kun Yuan's PDF 01."""
from __future__ import annotations
import re, subprocess
from pathlib import Path
from html import escape
from weasyprint import HTML, CSS

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"civilization-strategy"/"en"
OUT=ROOT/"civilization-strategy"/"pdf"
SOURCES=[
 ("02","01-second-age-of-intelligence.md","02_Second_Age_of_Intelligence_EN.pdf","SECOND AGE OF INTELLIGENCE"),
 ("03","02-ai-safety-a.md","03_AI_Safety_Research_EN.pdf","AI SAFETY"),
 ("04","03-mindos-b.md","04_MindOS_Research_and_Development_EN.pdf","MINDOS"),
 ("05","04-human-agency-c.md","05_Human_Subjecthood_and_Existential_Risk_EN.pdf","HUMAN SUBJECTHOOD")
]
STYLE=r"""
@page {
 size:A4;
 margin:22mm 24mm 21mm 25mm;
 @bottom-center {content:string(series) " | " counter(page);font-family:'Lato',sans-serif;font-size:7.2pt;color:#66798b;}
}
body {font-family:'Noto Serif','Liberation Serif',serif;font-size:9.45pt;line-height:1.42;font-weight:400;color:#23303b;margin:0;orphans:2;widows:2;text-align:left;}
.running {string-set:series content();font-size:0;margin:0;padding:0;}
h1,h2,h3,h4 {color:#15374f;break-after:avoid;page-break-after:avoid;}
h1 {font-family:'Lato',sans-serif;font-weight:800;font-size:17.6pt;line-height:1.16;margin:0 0 5pt;letter-spacing:-0.25px;}
h1:before {content:attr(data-number) " | ";}
h2 {font-family:'Lato',sans-serif;font-size:11pt;font-weight:800;line-height:1.22;margin:15pt 0 5pt;break-after:avoid;}
h3 {font-family:'Lato',sans-serif;font-size:9.8pt;font-weight:800;line-height:1.28;margin:10pt 0 4pt;break-after:avoid;}
h4 {font-family:'Lato',sans-serif;font-size:9.4pt;font-weight:700;line-height:1.25;margin:8pt 0 3pt;}
p {margin:0 0 7.8pt;hyphens:auto;}
strong {font-weight:700;} em {font-style:italic;}
a {color:#235a81;text-decoration:none;overflow-wrap:anywhere;}
hr {border:0;border-top:.7pt solid #7c8790;margin:16pt 0 18pt;}
ul,ol {margin:5pt 0 9pt;padding-left:19pt;}li {padding-left:1pt;margin:0 0 4pt;}li p {margin:0;}
blockquote {margin:7pt 0 10pt 14pt;padding-left:10pt;border-left:2pt solid #b9cbd9;}
code {font-family:'DejaVu Sans Mono',monospace;font-size:.86em;}
table {width:100%;border-collapse:collapse;font:8pt/1.3 'Lato',sans-serif;}
th,td {border-bottom:.4pt solid #c2c8cb;text-align:left;padding:4pt;}
pre {white-space:pre-wrap;overflow-wrap:anywhere;}
h1+p {margin-top:6pt;}
"""

def html_from_markdown(path):
 return subprocess.run(["pandoc","--from=gfm","--to=html5","--wrap=none",str(path)],check=True,capture_output=True,text=True,encoding="utf-8").stdout

def build():
 OUT.mkdir(parents=True,exist_ok=True)
 for number,source,outname,short in SOURCES:
  src=INPUT/source
  md=src.read_text(encoding="utf-8")
  if not md.startswith("# ") or len(md)<12000:raise ValueError("Incomplete source: "+str(src))
  body=html_from_markdown(src)
  body,n=re.subn(r"<h1(\s|>)",rf'<h1 data-number="{number}"\1',body,count=1)
  if n!=1:raise RuntimeError("Missing h1: "+str(src))
  html=f"<!doctype html><html lang='en'><head><meta charset='utf-8'></head><body><div class='running'>{number} · Kun Yuan — {escape(short)}</div>{body}</body></html>"
  doc=HTML(string=html,base_url=str(INPUT),media_type="print").render(stylesheets=[CSS(string=STYLE)])
  dest=OUT/outname
  doc.write_pdf(target=dest)
  if len(doc.pages)<3 or dest.stat().st_size<10000:raise ValueError("Suspicious PDF: "+str(dest))
  print(outname, "pages",len(doc.pages),"bytes",dest.stat().st_size,"source-chars",len(md),flush=True)

if __name__=="__main__":build()

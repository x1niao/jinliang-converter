# -*- coding: utf-8 -*-
"""把演化资料 Markdown 转成 APP 内嵌的离线 HTML（仅用标准库）。"""
import html
import os
import re

BASE = r"C:/Users/Administrator/WorkBuddy/2026-11-25-13-01-49"
SRC = os.path.join(BASE, "古代重量单位两与现代重量单位两演化资料.md")
DST = os.path.join(BASE, "android-build/app/src/main/assets/reference.html")


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    return text


def cells(line):
    return [inline(c.strip()) for c in line.strip().strip("|").split("|")]


def render(lines):
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped == "---":
            out.append("<hr/>")
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            out.append("<h%d>%s</h%d>" % (level, inline(line[level:].strip()), level))
            i += 1
            continue
        if (line.startswith("|") and i + 1 < len(lines)
                and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip())):
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            table = ['<div class="tw"><table><thead><tr>']
            table += ["<th>%s</th>" % c for c in head]
            table.append("</tr></thead><tbody>")
            for row in rows:
                table.append("<tr>" + "".join("<td>%s</td>" % c for c in row) + "</tr>")
            table.append("</tbody></table></div>")
            out.append("".join(table))
            continue
        if line.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(inline(lines[i][2:].strip()))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br/>".join(quote))
            continue
        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ol>")
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ul>")
            continue
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt == "---" or nxt.startswith("#") or nxt.startswith("|")
                    or nxt.startswith("> ") or nxt.startswith("- ")
                    or re.match(r"^\d+\.\s", nxt)):
                break
            para.append(nxt)
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
    return "\n".join(out)


CSS = """
body{font-family:-apple-system,'Noto Sans CJK SC','Microsoft YaHei',sans-serif;
 font-size:15px;line-height:1.75;color:#26313d;background:#f7f8fa;margin:0;padding:14px 16px 40px}
h1{font-size:20px;color:#b03a2e;margin:6px 0 12px;line-height:1.45}
h2{font-size:18px;color:#145a8a;margin:24px 0 10px;padding-bottom:6px;border-bottom:2px solid #d9e6f0}
h3{font-size:16px;color:#2c3e50;margin:18px 0 8px}
p{margin:9px 0}
strong{color:#b03a2e}
blockquote{margin:12px 0;padding:9px 12px;background:#fff6f3;border-left:4px solid #d98880;color:#4a5560}
.tw{overflow-x:auto;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff}
th,td{border:1px solid #dcdfe3;padding:7px 9px;text-align:left;vertical-align:top;white-space:nowrap}
th{background:#eaf2f8;color:#1f4e79}
ul,ol{margin:8px 0;padding-left:22px}
li{margin:5px 0}
code{background:#eceff1;padding:1px 4px;border-radius:3px;font-size:14px}
hr{border:0;border-top:1px solid #dfe3e8;margin:20px 0}
em{color:#7f8c8d}
"""

with open(SRC, encoding="utf-8") as f:
    body = render(f.read().splitlines())

os.makedirs(os.path.dirname(DST), exist_ok=True)
page = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>参考资料及文献</title><style>%s</style></head><body>%s</body></html>"
        % (CSS, body))
with open(DST, "w", encoding="utf-8") as f:
    f.write(page)

print("HTML generated:", DST)
print("bytes:", os.path.getsize(DST))
print("sections:", page.count("<h2>"), "tables:", page.count("<table>"), "refs:", page.count("<li>"))

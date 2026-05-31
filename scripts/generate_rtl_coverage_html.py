#!/usr/bin/env python3
"""Generate an RTL-level coverage HTML report from code_coverage.json.

Reads the toffee-generated code_coverage.json (Verilator .dat filtered
to RTL module-level constructs) and renders an interactive HTML page
with per-module Branch / Line / Toggle / Expr coverage breakdown.

When an RTL source file is provided (--rtl), uncovered-line detail boxes
include the actual Verilog source code for quick cross-referencing.

Usage:
    python scripts/generate_rtl_coverage_html.py                              # defaults
    python scripts/generate_rtl_coverage_html.py --rtl rtl/dut/Cache.v        # with RTL source
    python scripts/generate_rtl_coverage_html.py -i in.json -o out.html
    python scripts/generate_rtl_coverage_html.py -i in.json -o out.html --rtl build/picker_cache/Cache.v

Author: WorkBuddy (AI) — human-AI collaborative development
Date:   2026-05-30 / updated 2026-05-31 (RTL source embedding)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Optional

# ── Default paths ────────────────────────────────────────────────────
_SCRIPT_DIR    = Path(__file__).resolve().parent
_WORKSPACE     = _SCRIPT_DIR.parent
_DEFAULT_INPUT = _WORKSPACE / "build" / "reports" / "line_dat" / "code_coverage.json"
_DEFAULT_OUTPUT = _WORKSPACE / "build" / "reports" / "rtl_coverage.html"
_DEFAULT_RTL   = _WORKSPACE / "build" / "picker_cache" / "Cache.v"

# ── CSS ──────────────────────────────────────────────────────────────
_CSS = r"""
:root {
  --bg:#fafafa;--card-bg:#fff;--border:#e0e0e0;--text:#333;--text-secondary:#666;
  --green:#2e7d32;--green-bg:#e8f5e9;--yellow:#f57f17;--yellow-bg:#fff8e1;
  --red:#c62828;--red-bg:#ffebee;--accent:#1565c0;--radius:10px;
  --shadow:0 1px 3px rgba(0,0,0,0.08);
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.6;padding:24px}
.container{max-width:1200px;margin:0 auto}
h1{font-size:1.6rem;margin-bottom:4px}
.subtitle{color:var(--text-secondary);font-size:.85rem;margin-bottom:24px}
.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.summary-card{background:var(--card-bg);border:1px solid var(--border);
  border-radius:var(--radius);padding:16px 20px;box-shadow:var(--shadow)}
.summary-card .label{font-size:.75rem;color:var(--text-secondary);
  text-transform:uppercase;letter-spacing:.5px}
.summary-card .pct{font-size:2rem;font-weight:700;margin:4px 0}
.summary-card .detail{font-size:.8rem;color:var(--text-secondary)}
.summary-card .bar-bg{height:6px;border-radius:3px;background:#eee;
  margin-top:8px;overflow:hidden}
.summary-card .bar-fill{height:100%;border-radius:3px;transition:width .6s}
.section-title{font-size:1.1rem;font-weight:600;margin:28px 0 12px;
  padding-bottom:6px;border-bottom:2px solid var(--accent)}
table{width:100%;border-collapse:collapse;background:var(--card-bg);
  border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow)}
th{background:#f5f5f5;font-size:.78rem;text-transform:uppercase;
  letter-spacing:.3px;color:var(--text-secondary);padding:10px 12px;text-align:center}
th:first-child{text-align:left;padding-left:16px}
td{padding:9px 12px;border-top:1px solid var(--border);font-size:.88rem;text-align:center}
td:first-child{text-align:left;padding-left:16px;font-weight:500}
.module-name{font-weight:600;color:var(--accent)}
.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}
.bg-green{background:var(--green-bg)}.bg-yellow{background:var(--yellow-bg)}
.bg-red{background:var(--red-bg)}
.detail-row{display:none}
.detail-row.open{display:table-row}
.detail-row td{padding:0 12px 12px 16px;border-top:none}
.detail-box{background:#f9f9f9;border:1px solid var(--border);
  border-radius:8px;padding:14px 16px;font-size:.82rem}
.detail-box h4{font-size:.8rem;color:var(--text-secondary);margin:8px 0 4px}
.chip{display:inline-block;background:var(--red-bg);color:var(--red);
  padding:2px 8px;border-radius:4px;margin:2px 4px 2px 0;
  font-family:monospace;font-size:.78rem;cursor:pointer}
.chip:hover{opacity:.8}
.chip-toggle{background:#fff3e0;color:#e65100}
.chip-expr{background:#e8eaf6;color:#283593}
.chip-selected{outline:2px solid var(--accent);outline-offset:1px}
.rtl-preview{display:none;margin:8px 0 0 0;background:#1e1e1e;color:#dcdcaa;
  border-radius:6px;overflow:hidden;font-family:"SF Mono","Fira Code",monospace;
  font-size:.78rem;line-height:1.45}
.rtl-preview.open{display:block}
.rtl-preview .header{background:#333;color:#ccc;padding:4px 12px;
  font-size:.72rem;display:flex;justify-content:space-between}
.rtl-preview pre{margin:0;padding:8px 0;overflow-x:auto}
.rtl-preview code{display:block;padding:0 12px;white-space:pre}
.rtl-preview .lineno{display:inline-block;width:42px;text-align:right;
  color:#858585;margin-right:12px;user-select:none}
.rtl-preview .rline{color:#dcdcaa}
.rtl-preview .rline.highlight{background:#3a3a1a}
.clickable{cursor:pointer;user-select:none}
.clickable:hover{background:#f5f5f5}
.expand-icon{display:inline-block;width:16px;margin-right:4px;
  transition:transform .2s;font-size:.7rem}
.expand-icon.open{transform:rotate(90deg)}
.tabs{display:flex;gap:4px;margin-bottom:16px}
.tab{padding:6px 18px;border-radius:6px;font-size:.82rem;cursor:pointer;
  border:1px solid var(--border);background:var(--card-bg);
  color:var(--text-secondary);transition:all .15s}
.tab:hover{background:#f0f0f0}
.tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
@media(max-width:700px){.summary-grid{grid-template-columns:repeat(2,1fr)}}
"""

# ── RTL source loading ────────────────────────────────────────────────

def _load_rtl_source(rtl_path: Optional[str]) -> Dict[int, str]:
    """Read a Verilog file and return {line_number: source_line}."""
    source: Dict[int, str] = {}
    if not rtl_path or not os.path.exists(rtl_path):
        return source
    with open(rtl_path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            stripped = line.rstrip("\n")
            source[i] = stripped
    return source


def _expand_range(range_str: str) -> list[int]:
    """Expand '202-207' → [202,203,204,205,206,207]; '558-558' → [558]."""
    m = re.match(r"^(\d+)-(\d+)$", range_str)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    return [int(range_str)] if range_str.isdigit() else []


def _build_rtl_source_js(source: Dict[int, str]) -> str:
    """Build a JS object literal: {lineNum: "source code", ...}"""
    if not source:
        return "{}"
    entries = []
    for ln, text in sorted(source.items()):
        # Escape backticks, backslashes, and other JS-unfriendly chars
        safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        entries.append(f"{ln}:`{safe}`")
    return "{" + ",".join(entries) + "}"


# ── Coverage data extraction ──────────────────────────────────────────

def _extract_modules(data: dict) -> list[dict]:
    """Parse code_coverage.json into a list of per-module dicts."""
    uncovered = data.get("uncovered", {})
    udata = uncovered.get("data", {})
    if not udata:
        return []

    file_path, file_cov = next(iter(udata.items()))
    modules_raw = file_cov.get("modules", {})

    result = []
    for mod_name in sorted(modules_raw.keys()):
        m = modules_raw[mod_name]
        t = m.get("total", {})
        mi = m.get("miss", {})

        result.append({
            "name": mod_name,
            "line_total": t.get("line", 0),
            "line_hit":   t.get("line", 0) - mi.get("line", 0),
            "line_miss":  mi.get("line", 0),
            "branch_total": t.get("branch", 0),
            "branch_hit":   t.get("branch", 0) - mi.get("branch", 0),
            "branch_miss":  mi.get("branch", 0),
            "toggle_total": t.get("toggle", 0),
            "toggle_hit":   t.get("toggle", 0) - mi.get("toggle", 0),
            "toggle_miss":  mi.get("toggle", 0),
            "expr_total": t.get("expr", 0),
            "expr_hit":   t.get("expr", 0) - mi.get("expr", 0),
            "expr_miss":  mi.get("expr", 0),
            "uncovered_lines":     [r for r in m.get("line", []) if r],
            "uncovered_branches":  [r for r in m.get("branch", []) if r],
            "uncovered_toggles":   m.get("toggle", []),
            "uncovered_exprs":     m.get("expr", []),
        })
    return result


def _build_js_modules(modules: list[dict]) -> str:
    """Build a JavaScript array literal from the module list."""
    entries = []
    for m in modules:
        entries.append(
            f'{{name:"{m["name"]}",'
            f'line:[{m["line_total"]},{m["line_hit"]},{m["line_miss"]}],'
            f'branch:[{m["branch_total"]},{m["branch_hit"]},{m["branch_miss"]}],'
            f'toggle:[{m["toggle_total"]},{m["toggle_hit"]},{m["toggle_miss"]}],'
            f'expr:[{m["expr_total"]},{m["expr_hit"]},{m["expr_miss"]}],'
            f'branchUnc:{json.dumps(m["uncovered_branches"])},'
            f'lineUnc:{json.dumps(m["uncovered_lines"])},'
            f'toggleUnc:{json.dumps(m["uncovered_toggles"])},'
            f'exprUnc:{json.dumps(m["uncovered_exprs"])}}}'
        )
    return "[" + ",".join(entries) + "]"


# ── JavaScript template ───────────────────────────────────────────────

_JS_TEMPLATE = r"""
// === Data injected by Python ===
const MODULES = __MODULES_JSON__;
const RTL_SRC = __RTL_SOURCE_JSON__;

let currentMetric = 'branch';
const metricLabels = { line:'Line', branch:'Branch', toggle:'Toggle', expr:'Expr' };

function getPct(total, hit) {
  return total > 0 ? (hit / total * 100) : 100;
}
function pctClass(pct) {
  if (pct >= 100 || pct >= 85) return 'green';
  if (pct >= 60) return 'yellow';
  return 'red';
}
function pctBg(pct) {
  if (pct >= 100 || pct >= 85) return 'bg-green';
  if (pct >= 60) return 'bg-yellow';
  return 'bg-red';
}
function barColor(pct) {
  if (pct >= 85) return 'var(--green)';
  if (pct >= 60) return 'var(--yellow)';
  return 'var(--red)';
}

// Expand a range string like "202-207" into individual line numbers
function expandRange(r) {
  var m = r.match(/^(\d+)-(\d+)$/);
  if (m) {
    var lines = [];
    for (var i = parseInt(m[1]); i <= parseInt(m[2]); i++) lines.push(i);
    return lines;
  }
  var n = parseInt(r);
  return isNaN(n) ? [] : [n];
}

// Get RTL source lines for a list of range strings
function getRtlSourceLines(rangeStrs) {
  var result = [];
  rangeStrs.forEach(function(r) {
    expandRange(r).forEach(function(ln) {
      if (RTL_SRC[ln] !== undefined) {
        result.push({line: ln, code: RTL_SRC[ln]});
      }
    });
  });
  return result;
}

// Toggle RTL preview for a chip element
window.showRtlPreview = function(chipId) {
  var preview = document.getElementById('rtlpreview-' + chipId);
  var chip = document.getElementById('chip-' + chipId);
  if (!preview) return;
  var isOpen = preview.classList.contains('open');
  // Close all other previews first
  document.querySelectorAll('.rtl-preview.open').forEach(function(p) {
    if (p !== preview) p.classList.remove('open');
  });
  document.querySelectorAll('.chip-selected').forEach(function(c) {
    if (c !== chip) c.classList.remove('chip-selected');
  });
  preview.classList.toggle('open', !isOpen);
  if (chip) chip.classList.toggle('chip-selected', !isOpen);
};

function renderRow(m, i) {
  var d = m[currentMetric];
  var pct = getPct(d[0], d[1]);
  var hasUnc = d[2] > 0;
  var uncMap = { branch: m.branchUnc, line: m.lineUnc, toggle: m.toggleUnc, expr: m.exprUnc };
  var unc = hasUnc ? uncMap[currentMetric] : [];

  var html = '<tr class="' + (hasUnc ? 'clickable' : '') + '" ' +
    (hasUnc ? 'onclick="toggleDetail(' + i + ')"' : '') + '>';
  html += '<td>' + (hasUnc ? '<span class="expand-icon" id="icon-' + i + '">\u25b6</span>'
    : '<span style="display:inline-block;width:20px"></span>');
  html += '<span class="module-name">' + m.name + '</span></td>';
  html += '<td class="' + pctClass(pct) + '">' + pct.toFixed(1) + '%</td>';
  html += '<td class="' + pctBg(pct) + '">' + d[1] + ' / ' + d[0] + '</td>';
  html += '<td style="color:' + (d[2] > 0 ? 'var(--red)' : 'var(--green)') + ';">' + d[2] + '</td>';
  html += '</tr>';

  if (hasUnc && unc.length > 0) {
    html += '<tr class="detail-row" id="detail-' + i + '"><td colspan="4"><div class="detail-box">';
    html += '<h4>\u274c \u672a\u8986\u76d6\u7684 ' + metricLabels[currentMetric] + ' (' + unc.length + ' \u9879)</h4>';

    var cls = currentMetric === 'toggle' ? 'chip-toggle' : currentMetric === 'expr' ? 'chip-expr' : '';
    unc.forEach(function(item, idx) {
      var chipId = 'u' + i + '-' + idx;
      var hasRtl = getRtlSourceLines([item]).length > 0;
      html += '<span class="chip ' + cls + '" id="chip-' + chipId + '"';
      if (hasRtl) {
        html += ' onclick="event.stopPropagation();showRtlPreview(\'' + chipId + '\')"';
        html += ' title="\u70b9\u51fb\u67e5\u770b RTL \u6e90\u7801"';
      }
      html += '>Line ' + item + '</span>';

      // RTL source preview (hidden by default)
      if (hasRtl) {
        var srcLines = getRtlSourceLines([item]);
        html += '<div class="rtl-preview" id="rtlpreview-' + chipId + '">';
        html += '<div class="header"><span>Cache.v</span><span style="cursor:pointer" onclick="event.stopPropagation();document.getElementById(\'rtlpreview-' + chipId + '\').classList.remove(\'open\');document.getElementById(\'chip-' + chipId + '\').classList.remove(\'chip-selected\')">\u2715</span></div>';
        html += '<pre>';
        srcLines.forEach(function(sl) {
          html += '<code><span class="lineno">' + sl.line + '</span><span class="rline">' +
            sl.code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</span></code>';
        });
        html += '</pre></div>';
      }
    });
    html += '</div></td></tr>';
  }
  return html;
}

function renderTotals() {
  var t = 0, h = 0, m = 0;
  MODULES.forEach(function(mod) {
    var d = mod[currentMetric];
    t += d[0]; h += d[1]; m += d[2];
  });
  var pct = getPct(t, h);
  return '<tr style="font-weight:700;border-top:2px solid var(--accent);">' +
    '<td>TOTAL</td><td class="' + pctClass(pct) + '">' + pct.toFixed(1) + '%</td>' +
    '<td>' + h + ' / ' + t + '</td>' +
    '<td style="color:' + (m > 0 ? 'var(--red)' : 'var(--green)') + ';">' + m + '</td></tr>';
}

function renderTable() {
  var html = '<table><thead><tr>' +
    '<th>\u6a21\u5757</th><th>\u8986\u76d6\u7387</th><th>Hit / Total</th><th>Miss</th>' +
    '</tr></thead><tbody>';
  MODULES.forEach(function(m, i) { html += renderRow(m, i); });
  html += renderTotals();
  html += '</tbody></table>';
  document.getElementById('table-container').innerHTML = html;
}

window.toggleDetail = function(i) {
  var row = document.getElementById('detail-' + i);
  var icon = document.getElementById('icon-' + i);
  if (!row || !icon) return;
  var open = row.classList.contains('open');
  row.classList.toggle('open', !open);
  icon.classList.toggle('open', !open);
};

// Render summary cards
(function() {
  var totals = { line:[0,0], branch:[0,0], toggle:[0,0], expr:[0,0] };
  MODULES.forEach(function(m) {
    ['line','branch','toggle','expr'].forEach(function(k) {
      totals[k][0] += m[k][0];
      totals[k][1] += m[k][1];
    });
  });
  ['line','branch','toggle','expr'].forEach(function(k) {
    var pct = getPct(totals[k][0], totals[k][1]);
    document.getElementById('card-' + k + '-pct').textContent = pct.toFixed(1) + '%';
    document.getElementById('card-' + k + '-pct').style.color = barColor(pct);
    document.getElementById('card-' + k + '-detail').textContent =
      totals[k][1] + ' / ' + totals[k][0];
    document.getElementById('card-' + k + '-bar').style.width = pct.toFixed(1) + '%';
    document.getElementById('card-' + k + '-bar').style.background = barColor(pct);
  });
})();

// Tab switching
document.querySelectorAll('.tab').forEach(function(tab) {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
    this.classList.add('active');
    currentMetric = this.dataset.metric;
    renderTable();
  });
});

renderTable();
"""


def _build_html(modules: list[dict], source_path: str,
                rtl_source: Dict[int, str], rtl_path: str) -> str:
    """Assemble the complete HTML document."""
    js = _JS_TEMPLATE
    js = js.replace("__MODULES_JSON__", _build_js_modules(modules))
    js = js.replace("__RTL_SOURCE_JSON__", _build_rtl_source_js(rtl_source))

    rtl_note = ""
    if rtl_source:
        total_lines = len(rtl_source)
        rtl_note = (f'<br>RTL source: <code>{rtl_path}</code> '
                    f'({total_lines} lines loaded — click uncovered-line chips to view source)')

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Cache.v — RTL Coverage Report</title>
<style>{_CSS}</style>
</head>
<body>
<div class="container">

<h1>Cache.v — RTL Coverage Report</h1>
<p class="subtitle">
  Data source: <code>{source_path}</code>{rtl_note}<br>
  Generated by <code>scripts/generate_rtl_coverage_html.py</code> (WorkBuddy)
</p>

<div class="summary-grid">
  <div class="summary-card">
    <div class="label">📏 Line</div>
    <div class="pct" id="card-line-pct">--</div>
    <div class="detail" id="card-line-detail">--</div>
    <div class="bar-bg"><div class="bar-fill" id="card-line-bar"></div></div>
  </div>
  <div class="summary-card">
    <div class="label">🌿 Branch</div>
    <div class="pct" id="card-branch-pct">--</div>
    <div class="detail" id="card-branch-detail">--</div>
    <div class="bar-bg"><div class="bar-fill" id="card-branch-bar"></div></div>
  </div>
  <div class="summary-card">
    <div class="label">🔄 Toggle</div>
    <div class="pct" id="card-toggle-pct">--</div>
    <div class="detail" id="card-toggle-detail">--</div>
    <div class="bar-bg"><div class="bar-fill" id="card-toggle-bar"></div></div>
  </div>
  <div class="summary-card">
    <div class="label">🔢 Expr</div>
    <div class="pct" id="card-expr-pct">--</div>
    <div class="detail" id="card-expr-detail">--</div>
    <div class="bar-bg"><div class="bar-fill" id="card-expr-bar"></div></div>
  </div>
</div>

<h2 class="section-title">📊 Per-Module Coverage</h2>

<div class="tabs">
  <div class="tab active" data-metric="branch">Branch</div>
  <div class="tab" data-metric="line">Line</div>
  <div class="tab" data-metric="toggle">Toggle</div>
  <div class="tab" data-metric="expr">Expr</div>
</div>

<div id="table-container"></div>

<div style="margin-top:32px;font-size:.78rem;color:var(--text-secondary);">
  <p><strong>Note:</strong> Data sourced from <code>code_coverage.json</code> (toffee/picker RTL-level extraction).
  Branch coverage shown is at the RTL module level, not the Verilator C++ level.</p>
  <p>Click uncovered-line chips to expand the RTL source code for that line.</p>
</div>

</div>
<script>{js}</script>
</body>
</html>"""


# ── Main API ──────────────────────────────────────────────────────────

def generate(input_path: str, output_path: str, rtl_path: Optional[str] = None) -> None:
    """Read code_coverage.json and write the RTL coverage HTML report.

    Args:
        input_path:  Path to code_coverage.json.
        output_path: Path for the output HTML.
        rtl_path:    Optional path to Cache.v for embedding RTL source in uncovered details.
    """
    if not os.path.exists(input_path):
        print(f"ERROR: {input_path} not found. Run collect_coverage.sh first.", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    modules = _extract_modules(data)
    if not modules:
        print("ERROR: No module coverage data found in JSON.", file=sys.stderr)
        sys.exit(1)

    rtl_source = _load_rtl_source(rtl_path)
    if rtl_source:
        print(f"RTL source loaded: {len(rtl_source)} lines from {rtl_path}")
    elif rtl_path:
        print(f"WARNING: RTL file not found at {rtl_path} — source preview disabled.", file=sys.stderr)

    # Show a quick summary on stdout
    total = {"line": [0, 0], "branch": [0, 0], "toggle": [0, 0], "expr": [0, 0]}
    for m in modules:
        for k in total:
            total[k][0] += m[f"{k}_total"]
            total[k][1] += m[f"{k}_hit"]
    print(f"Modules: {len(modules)}")
    for k, label in [("line", "Line"), ("branch", "Branch"), ("toggle", "Toggle"), ("expr", "Expr")]:
        t, h = total[k]
        pct = (h / t * 100) if t > 0 else 100.0
        print(f"  {label:>8s}: {h}/{t} = {pct:.1f}%")

    html = _build_html(modules, input_path, rtl_source, rtl_path or "")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML report written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate RTL coverage HTML from code_coverage.json"
    )
    parser.add_argument(
        "-i", "--input", default=str(_DEFAULT_INPUT),
        help=f"Path to code_coverage.json (default: {_DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o", "--output", default=str(_DEFAULT_OUTPUT),
        help=f"Output HTML path (default: {_DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--rtl", default=str(_DEFAULT_RTL),
        help=f"Path to Cache.v for RTL source embedding (default: {_DEFAULT_RTL}). "
             "Set to empty string to disable.",
    )
    args = parser.parse_args()

    rtl = args.rtl if args.rtl else None
    generate(args.input, args.output, rtl)


if __name__ == "__main__":
    main()

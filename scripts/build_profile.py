#!/usr/bin/env python3
"""Build the generated parts of my GitHub profile README. Standard library only.

  assets/trace-{dark,light}.svg    my career drawn as a distributed trace
                                   (source: data/career.json)
  assets/latency-{dark,light}.svg  shared-memory vs TCP latency measured by
                                   Market-Data-System-HFT/scripts/bench.sh
                                   (source: data/latency.txt, written by CI)
  README.md                        the block between the upstream markers,
                                   rebuilt from the GitHub search API

    python scripts/build_profile.py            # normal run (uses GITHUB_TOKEN if set)
    python scripts/build_profile.py --offline  # use data/prs_cache.json, no network
"""
import argparse
import json
import math
import os
import re
import urllib.request
from datetime import date
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNTS = ["harshpanchal04", "harshkumar-raga"]  # personal + RagaAI work account
# Merged PRs left off the list: content additions, not code.
EXCLUDE_REPOS = {"lingdojo/kana-dojo"}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "border": "#30363d", "grid": "#21262d",
        "text": "#e6edf3", "dim": "#8b949e", "event": "#d29922",
        "svc": {"edu": "#8b949e", "urban-company": "#bc8cff", "piramal": "#ffa657",
                "ragaai": "#58a6ff", "builds": "#56d4dd", "fam": "#3fb950"},
        "shm": "#3fb950", "tcp": "#58a6ff",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "border": "#d0d7de", "grid": "#eaeef2",
        "text": "#1f2328", "dim": "#59636e", "event": "#9a6700",
        "svc": {"edu": "#6e7781", "urban-company": "#8250df", "piramal": "#bc4c00",
                "ragaai": "#0969da", "builds": "#1b7c83", "fam": "#1a7f37"},
        "shm": "#1a7f37", "tcp": "#0969da",
    },
}


# ------------------------------------------------------------------ helpers

def path(*parts):
    return os.path.join(ROOT, *parts)


def write(rel, text):
    with open(path(rel), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", rel)


def months(ym):
    """'2024-07' -> fractional years (2024.5)."""
    y, m = ym.split("-")
    return int(y) + (int(m) - 1) / 12.0


def today_ym():
    t = date.today()
    return "{:04d}-{:02d}".format(t.year, t.month)


def fmt_duration(start, end):
    n = round((months(end) - months(start)) * 12)
    if n >= 24:
        return "{:.1f} y".format(n / 12).replace(".0 y", " y")
    return "{} mo".format(max(n, 1))


def text_w(s, size):
    """Rough rendered width of a string, for layout only."""
    return len(s) * size * 0.56


def grow(attr, final, delay, dur=0.55):
    """SMIL animation from 0 to `final` after `delay`. Static renderers ignore it
    and show the base value, so the base value is always the final state."""
    total = delay + dur
    k = delay / total
    return ('<animate attributeName="{a}" values="0;0;{f}" keyTimes="0;{k:.3f};1" '
            'dur="{t:.2f}s" fill="freeze" calcMode="spline" keySplines="0 0 1 1;0.2 0.8 0.2 1"/>'
            ).format(a=attr, f=final, k=k, t=total)


def fade(delay, dur=0.4):
    total = delay + dur
    return ('<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" '
            'dur="{t:.2f}s" fill="freeze"/>').format(k=delay / total, t=total)


def frame(w, h, th, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            'role="img" font-family="{sans}">\n'
            '<rect x="0.5" y="0.5" width="{w1}" height="{h1}" rx="10" fill="{bg}" stroke="{border}"/>\n'
            '{body}\n</svg>\n').format(w=w, h=h, w1=w - 1, h1=h - 1, sans=SANS,
                                       bg=th["bg"], border=th["border"], body=body)


# ------------------------------------------------------------------ trace card

def render_trace(career, th):
    W, LEFT, X0, X1 = 880, 24, 268, 852
    ROW, TOP = 44, 92
    spans, events = career["spans"], career.get("events", [])
    now = today_ym()
    t0, t1 = months(career["start"]), months(career["end"])

    def x(ym):
        return X0 + (months(ym) - t0) / (t1 - t0) * (X1 - X0)

    H = TOP + ROW * len(spans) + 64
    out = []

    # header, like a trace viewer
    out.append('<text x="{}" y="34" font-family="{}" font-size="15" fill="{}" font-weight="600">'
               'trace <tspan fill="{}">{}</tspan></text>'.format(
                   LEFT, MONO, th["text"], th["svc"]["fam"], escape(career["trace_id"])))
    out.append('<text x="{}" y="34" text-anchor="end" font-family="{}" font-size="12" fill="{}">'
               '{} spans · {} events · started {} · still running</text>'.format(
                   X1, MONO, th["dim"], len(spans), len(events), career["start"]))

    # time axis
    axis_y = TOP - 22
    out.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}"/>'.format(
        LEFT, axis_y + 8, X1, axis_y + 8, th["border"]))
    for year in range(int(math.ceil(t0)), int(t1) + 1):
        xx = x("{}-01".format(year))
        out.append('<line x1="{0:.1f}" y1="{1}" x2="{0:.1f}" y2="{2}" stroke="{3}" stroke-dasharray="2 4"/>'
                   .format(xx, axis_y + 8, H - 40, th["grid"]))
        out.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-family="{}" font-size="11" fill="{}">{}</text>'
                   .format(xx, axis_y, MONO, th["dim"], year))
    out.append('<text x="{}" y="{}" font-family="{}" font-size="11" fill="{}">service · operation</text>'
               .format(LEFT, axis_y, MONO, th["dim"]))

    # "now" marker
    xn = x(now)
    out.append('<line x1="{0:.1f}" y1="{1}" x2="{0:.1f}" y2="{2}" stroke="{3}" stroke-width="1.5" stroke-dasharray="4 3"/>'
               .format(xn, axis_y + 8, H - 40, th["svc"]["fam"]))
    out.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-family="{}" font-size="10" fill="{}">now</text>'
               .format(xn, H - 28, MONO, th["svc"]["fam"]))

    # spans
    for i, s in enumerate(spans):
        y = TOP + i * ROW
        color = th["svc"].get(s["service"], th["dim"])
        end = s["end"] or now
        ongoing = s["end"] is None or months(s["end"]) > months(now)
        bx, bw = x(s["start"]), max(x(min(end, now, key=months)) - x(s["start"]), 3)
        delay = 0.15 + i * 0.12
        indent = LEFT + s.get("depth", 0) * 14

        if s.get("depth", 0):
            out.append('<path d="M{} {} v{} h8" fill="none" stroke="{}"/>'.format(
                indent - 9, y - 18, 18 + 4, th["border"]))
        out.append('<rect x="{}" y="{}" width="4" height="16" rx="1" fill="{}"/>'.format(indent, y - 8, color))
        out.append('<text x="{}" y="{}" font-family="{}" font-size="12.5" fill="{}">{}'
                   '<tspan fill="{}"> {}</tspan></text>'.format(
                       indent + 10, y + 4, MONO, th["text"], escape(s["service"]), th["dim"], escape(s["op"])))

        # bar and duration
        dur_txt = "ongoing" if ongoing and s["end"] is None else fmt_duration(s["start"], end)
        if ongoing and s["end"] is not None:
            dur_txt = fmt_duration(s["start"], now) + " / " + fmt_duration(s["start"], s["end"])
        out.append('<rect x="{:.1f}" y="{}" width="{:.1f}" height="14" rx="3" fill="{}" opacity="{}">{}</rect>'
                   .format(bx, y - 9, bw, color, 0.35 if s["service"] == "edu" else 0.95,
                           grow("width", "{:.1f}".format(bw), delay)))
        dx = bx + bw + 7
        anchor = "start"
        if dx + text_w(dur_txt, 11) > X1:
            dx, anchor = bx - 7, "end"
        out.append('<text x="{:.1f}" y="{}" text-anchor="{}" font-family="{}" font-size="11" fill="{}" stroke="{}" '
                   'stroke-width="4" paint-order="stroke" stroke-linejoin="round" opacity="1">{}{}</text>'
                   .format(dx, y + 2, anchor, MONO, th["dim"], th["bg"], escape(dur_txt), fade(delay + 0.4)))
        if s["end"] is None:  # live span: pulsing head
            out.append('<circle cx="{:.1f}" cy="{}" r="4" fill="{}"><animate attributeName="opacity" '
                       'values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'.format(bx + bw, y - 2, color))

        # detail line under the bar, kept inside the card
        detail = s.get("detail", "")
        tx = min(bx, X1 - text_w(detail, 11))
        out.append('<text x="{:.1f}" y="{}" font-size="11" fill="{}" stroke="{}" stroke-width="4" '
                   'paint-order="stroke" stroke-linejoin="round" opacity="1">{}{}</text>'
                   .format(max(tx, X0), y + 19, th["dim"], th["bg"], escape(detail), fade(delay + 0.3)))

    # events (logs on the trace)
    ey = TOP + len(spans) * ROW - 6
    for j, e in enumerate(events):
        ex = x(e["at"])
        out.append('<path d="M{0:.1f} {1} l5 5 l-5 5 l-5 -5 z" fill="{2}" opacity="1">{3}</path>'
                   .format(ex, ey - 5, th["event"], fade(0.9 + j * 0.15)))
        right = ex + 9 + text_w(e["label"], 11) * 1.08 > X1
        out.append('<text x="{:.1f}" y="{}" text-anchor="{}" font-family="{}" font-size="11" fill="{}" stroke="{}" '
                   'stroke-width="4" paint-order="stroke" stroke-linejoin="round" opacity="1">{}{}</text>'
                   .format(ex - 9 if right else ex + 9, ey + 4, "end" if right else "start", MONO,
                           th["event"], th["bg"], escape(e["label"]), fade(0.9 + j * 0.15)))

    return frame(W, H, th, "\n".join(out))


# ------------------------------------------------------------------ latency card

def load_latency():
    p = path("data", "latency.txt")
    if not os.path.exists(p):
        return None
    meta, rows = {}, {}
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line.startswith("# ") and ":" in line:
            k, v = line[2:].split(":", 1)
            meta[k.strip()] = v.strip()
        elif line.startswith("RESULT"):
            kv = dict(tok.split("=", 1) for tok in line.split()[1:])
            rows[kv["path"]] = {k: float(v) for k, v in kv.items() if k != "path"}
    return (meta, rows) if {"shm", "tcp"} <= rows.keys() else None


def fmt_ns(ns):
    if ns < 1000:
        return "{:.0f} ns".format(ns)
    if ns < 10000:
        return "{:.1f} µs".format(ns / 1000)
    if ns < 1e6:
        return "{:.0f} µs".format(ns / 1000)
    return "{:.1f} ms".format(ns / 1e6)


def render_latency(meta, rows, th):
    W, H = 880, 262
    LEFT, X0, X1 = 24, 250, 852
    lo = 10 ** math.floor(math.log10(min(r["min_ns"] for r in rows.values())))
    hi = 10 ** math.ceil(math.log10(max(r["p999_ns"] for r in rows.values())))
    lo, hi = max(lo, 10), max(hi, lo * 1000)

    def x(ns):
        ns = min(max(ns, lo), hi)
        return X0 + (math.log10(ns) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (X1 - X0)

    shm, tcp = rows["shm"], rows["tcp"]
    ratio = tcp["p50_ns"] / shm["p50_ns"] if shm["p50_ns"] else 0
    out = []
    out.append('<text x="{}" y="34" font-size="15" font-weight="600" fill="{}">One tick, two paths: '
               '<tspan font-family="{}" fill="{}">p50 {}</tspan> vs <tspan font-family="{}" fill="{}">{}</tspan>'
               '<tspan fill="{}" font-weight="400"> ({:.0f}× faster over shared memory)</tspan></text>'.format(
                   LEFT, th["text"], MONO, th["shm"], fmt_ns(shm["p50_ns"]), MONO, th["tcp"],
                   fmt_ns(tcp["p50_ns"]), th["dim"], ratio))
    out.append('<text x="{}" y="54" font-size="11.5" fill="{}">Lock-free SPSC ring in POSIX shared memory vs the same tick '
               'as JSON over TCP. Latency = receive − send, both on CLOCK_MONOTONIC.</text>'.format(LEFT, th["dim"]))

    # decade grid
    gy0, gy1 = 76, 196
    d = lo
    while d <= hi:
        xx = x(d)
        out.append('<line x1="{0:.1f}" y1="{1}" x2="{0:.1f}" y2="{2}" stroke="{3}"/>'.format(xx, gy0, gy1, th["grid"]))
        out.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-family="{}" font-size="10.5" fill="{}">{}</text>'
                   .format(xx, gy1 + 16, MONO, th["dim"], fmt_ns(d).replace(".0", "")))
        d *= 10

    lanes = [("shm", "shared memory", "lock-free SPSC, busy-poll", 112),
             ("tcp", "TCP + JSON", "kernel socket, blocking read", 168)]
    for i, (key, name, sub, y) in enumerate(lanes):
        r, c = rows[key], th[key]
        delay = 0.2 + i * 0.35
        out.append('<text x="{}" y="{}" font-size="13" font-weight="600" fill="{}">{}</text>'.format(LEFT, y - 4, th["text"], name))
        out.append('<text x="{}" y="{}" font-size="11" fill="{}">{}</text>'.format(LEFT, y + 11, th["dim"], sub))
        # whisker min..p99.9, box p50..p99
        out.append('<line x1="{:.1f}" y1="{}" x2="{:.1f}" y2="{}" stroke="{}" stroke-width="1.5" opacity="1">{}</line>'
                   .format(x(r["min_ns"]), y, x(r["p999_ns"]), y, c, fade(delay)))
        bx, bw = x(r["p50_ns"]), max(x(r["p99_ns"]) - x(r["p50_ns"]), 2)
        out.append('<rect x="{:.1f}" y="{}" width="{:.1f}" height="14" rx="3" fill="{}" opacity="0.9">{}</rect>'
                   .format(bx, y - 7, bw, c, grow("width", "{:.1f}".format(bw), delay)))
        out.append('<circle cx="{:.1f}" cy="{}" r="5" fill="{}" stroke="{}" stroke-width="2"/>'.format(bx, y, th["bg"], c))
        # labels above the bar; move one below if it would overlap its neighbour
        edge = {-14: -1e9, 24: -1e9}
        for lab, v in (("p50", r["p50_ns"]), ("p99", r["p99_ns"]), ("p99.9", r["p999_ns"])):
            txt = "{} {}".format(lab, fmt_ns(v))
            lx, half = x(v), len(txt) * 6.3 / 2
            for dy in (-14, 24):
                if lx - half > edge[dy] + 8:
                    edge[dy] = lx + half
                    out.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-family="{}" font-size="10.5" '
                               'fill="{}" opacity="1">{}{}</text>'.format(lx, y + dy, MONO, c, txt, fade(delay + 0.5)))
                    break

    m = re.search(r"(\d+) ticks, one every (\d+)us", meta.get("workload", ""))
    work = "{:,} ticks, one every {} µs".format(int(m.group(1)), m.group(2)) if m else meta.get("workload", "")
    foot = "{} · {:,} samples per path after warm-up · {}".format(work, int(shm["n"]), meta.get("host", ""))
    out.append('<text x="{}" y="{}" font-size="11" fill="{}">{}</text>'.format(LEFT, H - 18, th["dim"], escape(foot)))
    return frame(W, H, th, "\n".join(out))


# ------------------------------------------------------------------ upstream PRs

def search_prs(token):
    items = []
    for acct in ACCOUNTS:
        url = ("https://api.github.com/search/issues?per_page=100&q="
               "author:{}+type:pr+is:merged".format(acct))
        req = urllib.request.Request(url, headers={"User-Agent": "harshpanchal04-profile-builder",
                                                   "Accept": "application/vnd.github+json"})
        if token:
            req.add_header("Authorization", "Bearer " + token)
        with urllib.request.urlopen(req, timeout=30) as resp:
            items += json.load(resp).get("items", [])
    return items


def upstream_markdown(items):
    seen, rows = set(), []
    for it in items:
        repo = it["repository_url"].split("/repos/")[1]
        owner = repo.split("/")[0]
        merged = (it.get("pull_request") or {}).get("merged_at")
        if not merged or owner in ACCOUNTS or repo in EXCLUDE_REPOS or it["html_url"] in seen:
            continue
        seen.add(it["html_url"])
        rows.append((merged[:10], repo, it["title"], it["html_url"], it["number"]))
    rows.sort(reverse=True)
    lines = ["| merged | repo | pull request |", "|---|---|---|"]
    for d, repo, title, url, num in rows:
        lines.append("| {} | `{}` | [#{} {}]({}) |".format(d, repo, num, title.replace("|", "\\|"), url))
    return "\n".join(lines)


def update_readme(md):
    p = path("README.md")
    s = open(p, encoding="utf-8").read()
    new = re.sub(r"(<!-- upstream:start -->).*?(<!-- upstream:end -->)",
                 lambda m: m.group(1) + "\n" + md + "\n" + m.group(2), s, flags=re.S)
    if new != s:
        open(p, "w", encoding="utf-8").write(new)
        print("updated README upstream block")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    career = json.load(open(path("data", "career.json"), encoding="utf-8"))
    lat = load_latency()
    for name, th in THEMES.items():
        write("assets/trace-{}.svg".format(name), render_trace(career, th))
        if lat:
            write("assets/latency-{}.svg".format(name), render_latency(lat[0], lat[1], th))
    if not lat:
        print("no data/latency.txt with shm+tcp RESULT lines; kept the existing latency cards")

    items = None
    if not args.offline:
        try:
            items = search_prs(os.environ.get("GITHUB_TOKEN"))
            json.dump({"items": items}, open(path("data", "prs_cache.json"), "w"), indent=1)
        except Exception as e:  # rate limit or network: fall back to the cache
            print("GitHub API failed ({}); using cache".format(e))
    if items is None:
        items = json.load(open(path("data", "prs_cache.json"), encoding="utf-8")).get("items", [])
    update_readme(upstream_markdown(items))


if __name__ == "__main__":
    main()

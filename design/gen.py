"""Profile README v3 — designed SVG components.

Each component is a self-contained SVG: subset fonts embedded as base64 WOFF2,
light and dark palettes (<file>.svg and <file>-dark.svg), CSS keyframe motion with
reduced-motion fallback. GitHub renders SVGs as <img>, so no JS and no remote
assets are allowed inside them.

Run from this folder: pip install fonttools brotli && python3 gen.py  ->  ../assets/*.svg
Fonts: Instrument Serif, Geist, Geist Mono (SIL Open Font License), subset at build time.
"""
import base64, io, re, html
from fontTools.ttLib import TTFont
from fontTools import subset

FONTS = {
    'serif':   ('fonts/InstrumentSerif-Regular.ttf', 'KY Serif', 'normal', 400),
    'serifi':  ('fonts/InstrumentSerif-Italic.ttf', 'KY Serif', 'italic', 400),
    'sans':    ('fonts/Geist-400.ttf', 'KY Sans', 'normal', 400),
    'sansm':   ('fonts/Geist-500.ttf', 'KY Sans', 'normal', 500),
    'sansb':   ('fonts/Geist-600.ttf', 'KY Sans', 'normal', 600),
    'mono':    ('fonts/GeistMono-400.ttf', 'KY Mono', 'normal', 400),
    'monom':   ('fonts/GeistMono-500.ttf', 'KY Mono', 'normal', 500),
}

# Palette: bone paper + ink, vermilion signal (Indian post-box red), pine secondary.
MODE = "light"
TOKENS = {"light": """:root{--bg:#F3EEE5;--card:#FBF8F2;--ink:#17140F;--sub:#4A443B;--mute:#8A8275;--line:#DDD5C7;--hair:#E8E1D4;
--acc:#E4472B;--acc-soft:#F6D3C8;--pine:#2F5D50;--pine-soft:#D5E3DC;--amber:#C98A1B;--amber-soft:#F2E2BF;--grain:.05}""",
          "dark": """:root{--bg:#121722;--card:#181E2A;--ink:#EDE7DA;--sub:#B9B3A6;--mute:#7F8796;--line:#2A3242;--hair:#1F2633;--acc:#D9B26F;--acc-soft:#3A3122;--pine:#93C2A6;--pine-soft:#1C2E28;--amber:#A9B6EA;--amber-soft:#232A45;--grain:.06}"""}
SHARED = """

.bg{fill:var(--bg)}.card{fill:var(--card)}.ink{fill:var(--ink)}.sub{fill:var(--sub)}.mute{fill:var(--mute)}
.acc{fill:var(--acc)}.pine{fill:var(--pine)}.amber{fill:var(--amber)}
.line{stroke:var(--line)}.hair{stroke:var(--hair)}.s-acc{stroke:var(--acc)}.s-ink{stroke:var(--ink)}.s-pine{stroke:var(--pine)}.s-mute{stroke:var(--mute)}
.f-serif{font-family:'KY Serif',Georgia,serif;font-weight:400}.f-serifi{font-family:'KY Serif',Georgia,serif;font-style:italic;font-weight:400}
.f-sans{font-family:'KY Sans',system-ui,sans-serif;font-weight:400}.f-sansm{font-family:'KY Sans',system-ui,sans-serif;font-weight:500}.f-sansb{font-family:'KY Sans',system-ui,sans-serif;font-weight:600}
.f-mono{font-family:'KY Mono',ui-monospace,monospace;font-weight:400}.f-monom{font-family:'KY Mono',ui-monospace,monospace;font-weight:500}
.ease{animation-timing-function:cubic-bezier(.65,0,.35,1)}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""


def font_face(key, chars):
    path, fam, style, weight = FONTS[key]
    f = TTFont(path)
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['kern', 'liga', 'calt']
    opts.name_IDs = []; opts.notdef_outline = True
    s = subset.Subsetter(opts); s.populate(text=chars + ' '); s.subset(f)
    buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"

def text_by_class(body):
    """Collect characters used by each font class (text/tspan with class f-xxx)."""
    used = {}
    for m in re.finditer(r'<(text|tspan)[^>]*class="[^"]*\bf-(\w+)\b[^"]*"[^>]*>(.*?)</\1>', body, re.S):
        k, inner = m.group(2), m.group(3)
        inner = re.sub(r'<tspan[^>]*class="[^"]*\bf-\w+[^"]*"[^>]*>.*?</tspan>', '', inner, flags=re.S)
        inner = html.unescape(re.sub(r'<[^>]+>', '', inner))
        used[k] = used.get(k, '') + inner
    return used

GRAIN = """<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0"/></filter>"""

def svg(w, h, body, title, extra_css='', grain=True, radius=26, frame=True):
    used = text_by_class(body)
    faces = ''.join(font_face(k, ''.join(sorted(set(v)))) for k, v in used.items() if k in FONTS)
    bgrect = f'<rect width="{w}" height="{h}" rx="{radius}" class="bg"/>' if frame else ''
    g = f'<rect width="{w}" height="{h}" rx="{radius}" filter="url(#grain)" style="opacity:var(--grain)"/>' if grain else ''
    border = f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{radius-.75}" fill="none" class="line" stroke-width="1.5"/>' if frame else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">'
            f'<title>{html.escape(title)}</title><defs>{GRAIN}<clipPath id="clip"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath></defs>'
            f'<style>{faces}{TOKENS[MODE]}{SHARED}{extra_css}</style>'
            f'<g clip-path="url(#clip)">{bgrect}{body}{g}</g>{border}</svg>')

def esc(s): return html.escape(s, quote=False)

def write(name, content):
    open(f'../assets/{name}{"-dark" if MODE == "dark" else ""}.svg', 'w').write(content)
    print(f'{name}.svg  {len(content)//1024} KB')

# ---------------------------------------------------------------- hero
def hero():
    W, H = 1200, 460
    # Route: intent -> agents -> review -> ship. A parcel travels it; each stop lights as it passes.
    path = "M 690 330 C 760 330 760 190 850 190 S 940 300 1010 300 S 1070 150 1120 130"
    stops = [(690, 330, 'intent'), (850, 190, 'agents'), (1010, 300, 'review'), (1120, 130, 'ship')]
    T = 7  # seconds per loop
    # parcel reaches stops at roughly these fractions of the loop
    at = [0.04, 0.30, 0.56, 0.80]
    css = []
    stop_svg = ''
    for i, ((x, y, label), t) in enumerate(zip(stops, at)):
        p = round(t * 100)
        css.append(f"@keyframes lit{i}{{0%,{max(p-3,0)}%{{opacity:.28}}{p}%,{min(p+40,94)}%{{opacity:1}}100%{{opacity:.28}}}}"
                   f".lit{i}{{animation:lit{i} {T}s infinite cubic-bezier(.65,0,.35,1)}}"
                   f"@keyframes ring{i}{{0%,{max(p-1,0)}%{{transform:scale(.6);opacity:0}}{p+1}%{{opacity:.9}}{min(p+14,99)}%{{transform:scale(2.6);opacity:0}}100%{{opacity:0}}}}"
                   f".ring{i}{{transform-box:fill-box;transform-origin:center;animation:ring{i} {T}s infinite ease-out}}")
        ly = y + 34 if y < 250 else y - 22
        if label == 'ship': ly = y - 22
        is_end = label == 'ship'
        stop_svg += (f'<circle cx="{x}" cy="{y}" r="9" fill="none" class="s-acc ring{i}" stroke-width="1.5"/>'
                     f'<g class="lit{i}"><circle cx="{x}" cy="{y}" r="{7 if is_end else 5.5}" class="{"acc" if is_end else "ink"}"/>'
                     f'<text x="{x}" y="{ly}" text-anchor="middle" class="f-mono sub" font-size="13" letter-spacing="1.5">{label.upper()}</text></g>')
    css.append(f"@keyframes draw{{0%{{stroke-dashoffset:900}}80%,100%{{stroke-dashoffset:0}}}}"
               f".trail{{stroke-dasharray:900;animation:draw {T}s infinite cubic-bezier(.65,0,.35,1)}}"
               "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 2.4s infinite ease-in-out}"
               "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
               ".rise1{animation:rise 1.1s .1s both cubic-bezier(.2,.8,.2,1)}.rise2{animation:rise 1.1s .25s both cubic-bezier(.2,.8,.2,1)}.rise3{animation:rise 1.1s .45s both cubic-bezier(.2,.8,.2,1)}")
    body = f'''
<g class="hair" stroke-width="1">{''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(600, 1200, 60))}{''.join(f'<line x1="600" y1="{y}" x2="1200" y2="{y}"/>' for y in range(40, H, 60))}</g>
<text x="64" y="70" class="f-monom acc" font-size="14" letter-spacing="3">KY / 2026</text>
<g transform="translate(1136 64)"><circle cx="-6" cy="-5" r="5" class="pine pulse"/><text x="-20" y="0" text-anchor="end" class="f-mono sub" font-size="14" letter-spacing="1.5">OPEN TO WORK · PUNJAB, IN</text></g>
<g class="rise1"><text x="58" y="208" class="f-serif ink" font-size="132" letter-spacing="-3">Karthik</text></g>
<g class="rise2"><text x="58" y="318" class="f-serifi ink" font-size="132" letter-spacing="-3">Yernana<tspan class="f-serif acc">.</tspan></text></g>
<g class="rise3">
<text x="64" y="374" class="f-sans sub" font-size="21">Full-stack developer and AI engineer,</text>
<text x="64" y="402" class="f-sans sub" font-size="21">building with a founder’s mindset.</text>
</g>
<path d="{path}" fill="none" class="line" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>
<path d="{path}" fill="none" class="s-acc trail" stroke-width="2" stroke-linecap="round"/>
{stop_svg}
<g><rect x="-9" y="-9" width="18" height="18" rx="4" class="acc"/><rect x="-4" y="-4" width="8" height="8" rx="1.5" class="card"/>
<animateMotion dur="{T}s" repeatCount="indefinite" path="{path}" rotate="0" keyPoints="0;0;1;1" keyTimes="0;.04;.80;1" calcMode="spline" keySplines="0 0 1 1;.65 0 .35 1;0 0 1 1"/></g>
<text x="690" y="420" class="f-mono mute" font-size="11.5" letter-spacing="1.2">SET THE INTENT · GUIDE THE AGENTS · REVIEW EVERYTHING</text>
'''
    write('hero', svg(W, H, body, 'Karthik Yernana — full-stack developer and AI engineer, building with a founder’s mindset', ''.join(css)))

# ---------------------------------------------------------------- connect pills
ICONS = {
    'linkedin': '<path d="M3 4.5h3.2V15H3zM4.6 0a1.85 1.85 0 1 1 0 3.7 1.85 1.85 0 0 1 0-3.7zM8.2 4.5h3.06v1.44h.04c.43-.81 1.47-1.66 3.03-1.66 3.24 0 3.84 2.13 3.84 4.9V15h-3.2V9.84c0-1.23-.02-2.82-1.72-2.82-1.72 0-1.98 1.34-1.98 2.73V15H8.2z"/>',
    'x': '<path d="M13.7 0h2.67l-5.83 6.66L17.4 15.8h-5.37l-4.2-5.5-4.8 5.5H.35l6.24-7.13L0 0h5.5l3.8 5.03zm-.94 14.18h1.48L4.7 1.52H3.11z"/>',
    'portfolio': '<path d="M8.5 0a8 8 0 1 0 0 16A8 8 0 0 0 8.5 0zm5.6 7.2h-2.6a12.6 12.6 0 0 0-1.1-4.9 6.4 6.4 0 0 1 3.7 4.9zM8.5 1.7c.7.9 1.4 2.8 1.6 5.5H6.9c.2-2.7.9-4.6 1.6-5.5zM6.6 2.3a12.6 12.6 0 0 0-1.1 4.9H2.9a6.4 6.4 0 0 1 3.7-4.9zM2.9 8.8h2.6c.1 1.9.5 3.6 1.1 4.9a6.4 6.4 0 0 1-3.7-4.9zm5.6 5.5c-.7-.9-1.4-2.8-1.6-5.5h3.2c-.2 2.7-.9 4.6-1.6 5.5zm1.9-.6c.6-1.3 1-3 1.1-4.9h2.6a6.4 6.4 0 0 1-3.7 4.9z"/>',
    'leetcode': '<path d="M11.1 12.4 8.3 15.2a2.4 2.4 0 0 1-3.4 0L1.5 11.8a2.4 2.4 0 0 1 0-3.4l3.4-3.5L9.4.4a1 1 0 0 1 1.4 1.4L7.7 5a4.1 4.1 0 0 1 3.4 1.1l1.4 1.4a1 1 0 0 1-1.4 1.4L9.7 7.5a2.4 2.4 0 0 0-3.4 0L2.9 10.9a.7.7 0 0 0 0 1l3.4 3.4a.7.7 0 0 0 1 0l2.8-2.8a1 1 0 0 1 1.4 1.4zM8 10h7a1 1 0 0 1 0 2H8a1 1 0 0 1 0-2z"/>',
    'mail': '<path d="M1.6 2h13.8c.9 0 1.6.7 1.6 1.6v8.8c0 .9-.7 1.6-1.6 1.6H1.6C.7 14 0 13.3 0 12.4V3.6C0 2.7.7 2 1.6 2zm.4 2v.3l6.5 4.2L15 4.3V4zm13 2.6-6.5 4.1L2 6.6v5.4h13z"/>',
}
def pill(name, icon, label, handle, i):
    W, H = 232, 64
    css = (f"@keyframes nudge{{0%,70%,100%{{transform:translate(0,0)}}80%{{transform:translate(3px,-3px)}}90%{{transform:translate(0,0)}}}}"
           f".arrow{{animation:nudge 5s {i*0.35:.2f}s infinite cubic-bezier(.65,0,.35,1)}}")
    body = f'''
<rect width="{W}" height="{H}" class="card"/>
<g transform="translate(22 24)" class="ink">{ICONS[icon]}</g>
<text x="52" y="29" class="f-sansm ink" font-size="15">{esc(label)}</text>
<text x="52" y="47" class="f-mono mute" font-size="11.5">{esc(handle)}</text>
<g class="arrow"><path d="M200 39 L211 28 M203 28 H211 V36" fill="none" class="s-acc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>'''
    write(f'link-{name}', svg(W, H, body, f'{label}: {handle}', css, grain=False, radius=16))

# ---------------------------------------------------------------- section label
def label(name, num, text, note=''):
    W, H = 1200, 72
    body = f'''
<text x="32" y="44" class="f-monom acc" font-size="14" letter-spacing="2.5">{num}</text>
<text x="74" y="46" class="f-serif ink" font-size="34">{esc(text)}</text>
<line x1="{90 + len(text)*15.5:.0f}" y1="36" x2="{1168 - (len(note)*8.6 + 20 if note else 0):.0f}" y2="36" class="line" stroke-width="1"/>
{f'<text x="1168" y="41" text-anchor="end" class="f-mono mute" font-size="12" letter-spacing="1.5">{esc(note)}</text>' if note else ''}'''
    write(f'label-{name}', svg(W, H, body, f'{num} {text}', grain=False, radius=18))

# ---------------------------------------------------------------- featured: PreCourier
def featured():
    W, H = 1200, 440
    orders = [('#4821', '₹1,240', 'Pune', .18, 'SHIP', 'pine'), ('#4822', '₹3,890', 'Patna', .71, 'VERIFY', 'amber'),
              ('#4823', '₹649', 'Kochi', .12, 'SHIP', 'pine'), ('#4824', '₹5,420', 'Agra', .88, 'HOLD', 'acc'),
              ('#4825', '₹1,099', 'Surat', .34, 'SHIP', 'pine'), ('#4826', '₹2,750', 'Ranchi', .63, 'VERIFY', 'amber')]
    rowh = 58
    def rows(off):
        out = ''
        for i, (oid, amt, city, risk, verdict, col) in enumerate(orders):
            y = off + i * rowh
            bw = 120
            out += (f'<g transform="translate(0 {y})"><rect x="0" y="0" width="476" height="{rowh-10}" rx="12" class="card"/>'
                    f'<rect x=".5" y=".5" width="475" height="{rowh-11}" rx="11.5" fill="none" class="line"/>'
                    f'<text x="18" y="30" class="f-mono mute" font-size="12.5">{oid}</text>'
                    f'<text x="78" y="30" class="f-sansm ink" font-size="15">{amt}</text>'
                    f'<text x="150" y="30" class="f-sans sub" font-size="13">COD · {city}</text>'
                    f'<rect x="262" y="21" width="{bw}" height="6" rx="3" class="hair" fill="none" stroke-width="6"/>'
                    f'<rect x="262" y="21" width="{bw*risk:.0f}" height="6" rx="3" class="{col}"/>'
                    f'<rect x="{396}" y="12" width="66" height="24" rx="12" style="fill:var(--{ "pine" if col=="pine" else ("amber" if col=="amber" else "acc")}-soft)"/>'
                    f'<text x="429" y="28.5" text-anchor="middle" class="f-monom {col}" font-size="11" letter-spacing="1">{verdict}</text></g>')
        return out
    loop = len(orders) * rowh
    css = (f"@keyframes feed{{0%{{transform:translateY(0)}}100%{{transform:translateY(-{loop}px)}}}}"
           f".feed{{animation:feed 18s infinite linear}}"
           "@keyframes scan{0%,100%{transform:translateY(0)}50%{transform:translateY(270px)}}.scan{animation:scan 6s infinite cubic-bezier(.65,0,.35,1)}")
    body = f'''
<text x="56" y="76" class="f-monom acc" font-size="13" letter-spacing="2.5">FEATURED · RAZORPAY BUILDATHON · TRACK 03</text>
<text x="52" y="160" class="f-serif ink" font-size="86" letter-spacing="-1.5">PreCourier</text>
<text x="56" y="204" class="f-serifi sub" font-size="30">Decide before the courier does.</text>
<text x="56" y="256" class="f-sans sub" font-size="17">An India-first decision API for D2C brands. It checks every</text>
<text x="56" y="281" class="f-sans sub" font-size="17">cash-on-delivery order between checkout and the shipping</text>
<text x="56" y="306" class="f-sans sub" font-size="17">label, explains the risk, and acts only when the rupee maths</text>
<text x="56" y="331" class="f-sans sub" font-size="17">says it’s worth it.</text>
<g transform="translate(56 362)">
  {''.join(f'<g transform="translate({x} 0)"><rect width="{w}" height="30" rx="15" fill="none" class="line" stroke-width="1.2"/><text x="{w/2}" y="20" text-anchor="middle" class="f-mono sub" font-size="12.5">{t}</text></g>' for x, w, t in [(0, 82, 'Python'), (92, 92, 'FastAPI'), (194, 112, '200+ tests'), (316, 146, 'explainable AI')])}
</g>
<text x="1144" y="402" text-anchor="end" class="f-sansm acc" font-size="15">View repository ↗</text>
<g transform="translate(668 40)">
  <rect x="-24" y="0" width="524" height="340" rx="20" style="fill:var(--hair)"/>
  <text x="0" y="26" class="f-mono mute" font-size="11.5" letter-spacing="1.5">LIVE DECISIONS · BEFORE THE LABEL PRINTS</text>
  <svg x="0" y="44" width="476" height="282" overflow="hidden"><g class="feed">{rows(0)}{rows(loop)}</g></svg>
  <g class="scan"><rect x="0" y="44" width="476" height="2" class="acc" opacity=".5"/></g>
</g>'''
    write('featured-precourier', svg(W, H, body, 'PreCourier — decide before the courier does. India-first COD decision API. View repository.', css))

# ---------------------------------------------------------------- project cards
def project(name, num, title, lines, tags, glyph, css, alt):
    W, H = 590, 300
    tx = 36
    tagx, tags_svg = 0, ''
    for t in tags:
        w = len(t) * 7.6 + 26
        tags_svg += f'<g transform="translate({tagx:.0f} 0)"><rect width="{w:.0f}" height="26" rx="13" fill="none" class="line" stroke-width="1.2"/><text x="{w/2:.0f}" y="17.5" text-anchor="middle" class="f-mono sub" font-size="11.5">{esc(t)}</text></g>'
        tagx += w + 8
    body = f'''
<text x="{tx}" y="54" class="f-monom acc" font-size="13" letter-spacing="2.5">{num}</text>
<g transform="translate(330 32)">{glyph}</g>
<text x="{tx-2}" y="170" class="f-serif ink" font-size="46" letter-spacing="-.5">{esc(title)}</text>
{''.join(f'<text x="{tx}" y="{204 + i*22}" class="f-sans sub" font-size="15.5">{esc(l)}</text>' for i, l in enumerate(lines))}
<g transform="translate({tx} 248)">{tags_svg}</g>
<path d="M538 268 L549 257 M541 257 H549 V265" fill="none" class="s-acc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'''
    write(f'project-{name}', svg(W, H, body, alt, css))

def glyph_mila():
    items = [('Atta 5 kg', '₹245'), ('Toor dal', '₹168'), ('Milk ×2', '₹64')]
    rows = ''.join(f'<g class="li li{i}"><text x="18" y="{36+i*22}" class="f-mono sub" font-size="11.5">{a}</text><text x="206" y="{36+i*22}" text-anchor="end" class="f-mono ink" font-size="11.5">{b}</text></g>' for i, (a, b) in enumerate(items))
    css = ("@keyframes li{0%,8%{opacity:0;transform:translateX(-8px)}16%,88%{opacity:1;transform:none}100%{opacity:0}}"
           + ''.join(f".li{i}{{animation:li 6s {i*0.45:.2f}s infinite cubic-bezier(.2,.8,.2,1)}}" for i in range(3))
           + "@keyframes stamp{0%,45%{opacity:0;transform:scale(1.6) rotate(-12deg)}53%,88%{opacity:1;transform:scale(1) rotate(-8deg)}100%{opacity:0}}"
           ".stamp{transform-box:fill-box;transform-origin:center;animation:stamp 6s infinite cubic-bezier(.2,.8,.2,1)}")
    g = f'''<rect width="224" height="128" rx="14" class="card"/><rect x=".5" y=".5" width="223" height="127" rx="13.5" fill="none" class="line"/>{rows}
<line x1="18" y1="92" x2="206" y2="92" class="line" stroke-dasharray="3 4"/>
<text x="18" y="114" class="f-monom ink" font-size="12">TOTAL</text><text x="206" y="114" text-anchor="end" class="f-monom ink" font-size="12">₹477</text>
<g class="stamp"><rect x="118" y="44" width="80" height="30" rx="5" fill="none" class="s-pine" stroke-width="2"/><text x="158" y="64" text-anchor="middle" class="f-monom pine" font-size="13" letter-spacing="2">PAID</text></g>'''
    return g, css

def glyph_planguard():
    css = ("@keyframes ghost{0%,20%{opacity:0}35%,85%{opacity:1}100%{opacity:0}}.ghost{animation:ghost 6s infinite cubic-bezier(.65,0,.35,1)}"
           "@keyframes cost{0%,30%{width:180px}50%,85%{width:46px}100%{width:180px}}.cost{animation:cost 6s infinite cubic-bezier(.65,0,.35,1)}"
           "@keyframes lbl1{0%,38%{opacity:1}46%,88%{opacity:0}100%{opacity:1}}.l1{animation:lbl1 6s infinite}"
           "@keyframes lbl2{0%,40%{opacity:0}50%,85%{opacity:1}100%{opacity:0}}.l2{animation:lbl2 6s infinite}")
    g = '''<rect width="224" height="128" rx="14" class="card"/><rect x=".5" y=".5" width="223" height="127" rx="13.5" fill="none" class="line"/>
<rect x="74" y="14" width="76" height="22" rx="6" fill="none" class="s-ink" stroke-width="1.3"/><text x="112" y="29" text-anchor="middle" class="f-mono ink" font-size="10.5">SELECT</text>
<path d="M112 36 V48 M60 48 H164 M60 48 V56 M164 48 V56" fill="none" class="s-mute" stroke-width="1.2"/>
<rect x="22" y="56" width="76" height="22" rx="6" fill="none" class="s-ink" stroke-width="1.3"/><text x="60" y="71" text-anchor="middle" class="f-mono ink" font-size="10.5">orders</text>
<g class="ghost"><rect x="126" y="56" width="76" height="22" rx="6" fill="none" class="s-acc" stroke-width="1.4" stroke-dasharray="4 3"/><text x="164" y="71" text-anchor="middle" class="f-mono acc" font-size="10.5">idx?</text></g>
<text x="22" y="100" class="f-mono mute" font-size="10">COST</text>
<rect x="22" y="106" width="180" height="8" rx="4" class="hair" fill="none" stroke-width="8"/>
<rect x="22" y="106" width="180" height="8" rx="4" class="acc cost"/>
<text x="202" y="100" text-anchor="end" class="f-mono sub l1" font-size="10">seq scan</text>
<text x="202" y="100" text-anchor="end" class="f-mono pine l2" font-size="10">−74% with index</text>'''
    return g, css

def glyph_funds():
    css = ("@keyframes stock{0%,15%{width:150px}30%,50%{width:112px}65%,90%{width:76px}100%{width:150px}}.stock{animation:stock 7s infinite cubic-bezier(.65,0,.35,1)}"
           "@keyframes log{0%{opacity:0;transform:translateY(6px)}10%,90%{opacity:1;transform:none}100%{opacity:0}}"
           ".lg1{animation:log 7s 1s infinite both cubic-bezier(.2,.8,.2,1)}.lg2{animation:log 7s 3s infinite both cubic-bezier(.2,.8,.2,1)}")
    g = '''<rect width="224" height="128" rx="14" class="card"/><rect x=".5" y=".5" width="223" height="127" rx="13.5" fill="none" class="line"/>
<text x="18" y="28" class="f-mono mute" font-size="10.5">SKU-118 · STOCK</text>
<rect x="18" y="38" width="150" height="10" rx="5" class="hair" fill="none" stroke-width="10"/><rect x="18" y="38" width="150" height="10" rx="5" class="pine stock"/>
<path d="M186 34 h14 v-4 a7 7 0 0 0 -14 0 v4 z M184 34 h18 v14 h-18 z" fill="none" class="s-ink" stroke-width="1.4"/>
<line x1="18" y1="62" x2="206" y2="62" class="line"/>
<g class="lg1"><text x="18" y="84" class="f-mono sub" font-size="10.5">10:42  −12  order #219</text></g>
<g class="lg2"><text x="18" y="106" class="f-mono sub" font-size="10.5">10:44  −12  order #220</text></g>'''
    return g, css

def glyph_rpm():
    ecg = "M10 70 H40 L50 70 L56 52 L62 86 L70 26 L78 98 L86 62 L92 70 H130 L140 70 L146 52 L152 86 L160 26 L168 98 L176 62 L182 70 H214"
    css = ("@keyframes ecg{0%{stroke-dashoffset:520}70%,100%{stroke-dashoffset:0}}.ecg{stroke-dasharray:520;animation:ecg 3.2s infinite linear}"
           "@keyframes blink{0%,60%{opacity:0}65%,95%{opacity:1}100%{opacity:0}}.alert{animation:blink 3.2s infinite}")
    g = f'''<rect width="224" height="128" rx="14" class="card"/><rect x=".5" y=".5" width="223" height="127" rx="13.5" fill="none" class="line"/>
<path d="{ecg}" fill="none" class="line" stroke-width="1.5"/>
<path d="{ecg}" fill="none" class="s-acc ecg" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
<text x="16" y="24" class="f-monom ink" font-size="12">HR 118</text>
<g class="alert"><circle cx="190" cy="20" r="4" class="acc"/><text x="182" y="24" text-anchor="end" class="f-mono acc" font-size="10.5">ALERT</text></g>
<text x="16" y="116" class="f-mono mute" font-size="10">LIVE · SERVER-SENT EVENTS</text>'''
    return g, css

# ---------------------------------------------------------------- toolkit
def toolkit():
    W, H = 1200, 250
    groups = [('INTERFACE', ['React', 'Next.js', 'TypeScript', 'Tailwind CSS']),
              ('SERVER', ['Node.js', 'Express', 'Python', 'FastAPI']),
              ('DATA', ['PostgreSQL', 'MongoDB', 'Prisma', 'Supabase']),
              ('AI & AUTOMATION', ['AI agents', 'n8n', 'LLM APIs', 'Prompt design']),
              ('SHIP & PRACTICE', ['Docker', 'Vercel', 'Git', 'C++ · DSA'])]
    colw = (W - 112) / 5
    out = ''
    for i, (g, items) in enumerate(groups):
        x = 56 + i * colw
        out += f'<text x="{x:.0f}" y="64" class="f-monom acc" font-size="12" letter-spacing="2">{esc(g)}</text>'
        out += f'<line x1="{x:.0f}" y1="80" x2="{x+colw-28:.0f}" y2="80" class="line"/>'
        for j, it in enumerate(items):
            out += f'<text x="{x:.0f}" y="{116 + j*30}" class="f-sans ink" font-size="17">{esc(it)}</text>'
    write('toolkit', svg(W, H, out, 'Toolkit: React, Next.js, TypeScript, Tailwind CSS, Node.js, Express, Python, FastAPI, PostgreSQL, MongoDB, Prisma, Supabase, AI agents, n8n, LLM APIs, Docker, Vercel, Git, C++'))

# ---------------------------------------------------------------- now + about
def about():
    W, H = 1200, 300
    body = '''
<text x="56" y="82" class="f-serif ink" font-size="40" letter-spacing="-.5">I came to code from the launch side.</text>
<text x="56" y="132" class="f-sans sub" font-size="18">I ran marketing at Gravity and kept wanting to build the product, not just sell it. So I learned.</text>
<text x="56" y="160" class="f-sans sub" font-size="18">Now I build full-stack products with AI in the loop: I set the intent, guide the agents, and review</text>
<text x="56" y="188" class="f-sans sub" font-size="18">every line before it ships. I like problems with money and trust under the interface.</text>
<g transform="translate(56 226)">
  <text x="0" y="22" class="f-mono mute" font-size="12" letter-spacing="1.5">B.TECH CSE · LOVELY PROFESSIONAL UNIVERSITY · 2027</text>
  <text x="1088" y="22" text-anchor="end" class="f-mono mute" font-size="12" letter-spacing="1.5">EX-HEAD OF MARKETING, GRAVITY</text>
</g>'''
    write('about', svg(W, H, body, 'About: I came to code from the launch side. Ran marketing at Gravity, now build full-stack products with AI in the loop. B.Tech CSE, LPU, 2027.'))

def now():
    W, H = 1200, 210
    items = [('Building', ['PreCourier into a decision engine', 'a real brand could run.']),
             ('Practising', ['DSA in C++ every week,', 'synced to GitHub from LeetCode.']),
             ('Open to', ['full-time roles, freelance work', 'and good collaborations.'])]
    colw = (W - 112) / 3
    css = "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 2.4s infinite ease-in-out}"
    out = ''
    for i, (k, ls) in enumerate(items):
        x = 56 + i * colw
        dot = f'<circle cx="{x+5:.0f}" cy="58" r="5" class="{"pine pulse" if i == 2 else "acc"}"/>'
        out += dot + f'<text x="{x+20:.0f}" y="63" class="f-monom ink" font-size="13" letter-spacing="2">{k.upper()}</text>'
        out += ''.join(f'<text x="{x:.0f}" y="{112 + j*28}" class="f-serif ink" font-size="24">{esc(l)}</text>' for j, l in enumerate(ls))
        if i: out += f'<line x1="{x-28:.0f}" y1="44" x2="{x-28:.0f}" y2="170" class="line"/>'
    write('now', svg(W, H, out, 'Now: building PreCourier, practising DSA in C++, open to full-time, freelance and collaborations.', css))

def footer():
    W, H = 1200, 150
    path = "M 760 96 C 840 96 860 54 940 54 S 1060 96 1140 76"
    css = ("@keyframes draw{0%{stroke-dashoffset:420}70%,100%{stroke-dashoffset:0}}.trail{stroke-dasharray:420;animation:draw 5s infinite cubic-bezier(.65,0,.35,1)}")
    body = f'''
<text x="56" y="90" class="f-serifi ink" font-size="44">Let’s build something that holds up.</text>
<path d="{path}" fill="none" class="line" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>
<path d="{path}" fill="none" class="s-acc trail" stroke-width="2" stroke-linecap="round"/>
<circle cx="1140" cy="76" r="6" class="acc"/>
<text x="56" y="124" class="f-mono mute" font-size="12" letter-spacing="1.5">KARTHIKYERNANA@GMAIL.COM</text>'''
    write('footer', svg(W, H, body, 'Let’s build something that holds up. karthikyernana@gmail.com', css, frame=True))

def build():
    hero()
    for i, (n, ic, lb, hd) in enumerate([('linkedin', 'linkedin', 'LinkedIn', 'in/yernana'), ('x', 'x', 'X', '@karthikbuildss'),
                                         ('portfolio', 'portfolio', 'Portfolio', 'karthikyernana.dev'), ('leetcode', 'leetcode', 'LeetCode', 'karthik_yernana'),
                                         ('github', 'mail', 'Email', 'say hello')]):
        pill(n if n != 'github' else 'email', ic, lb, hd, i)
    about()
    label('work', '01', 'Selected work', 'EVERY CARD OPENS THE REPO')
    featured()
    for args in [
        ('milastores', '02', 'MilaStores', ['Grocery storefront with Razorpay', 'and cash-on-delivery checkout.'], ['Next.js', 'Supabase', 'Razorpay'], glyph_mila, 'MilaStores — grocery storefront with Razorpay and COD checkout'),
        ('planguard', '03', 'PlanGuard', ['Test a Postgres index before you', 'create it, with HypoPG.'], ['FastAPI', 'React', 'PostgreSQL'], glyph_planguard, 'PlanGuard — test Postgres indexes hypothetically with HypoPG'),
        ('fundsroom', '04', 'FundsRoom', ['Mini ERP + CRM with atomic stock', 'deduction and a strict audit trail.'], ['React', 'PostgreSQL', 'Audit log'], glyph_funds, 'FundsRoom — mini ERP and CRM with atomic stock deduction and audit trail'),
        ('manual-rpm', '05', 'Manual-RPM', ['Remote patient monitoring with', 'rule-based live alerts.'], ['MERN', 'SSE', 'Alerts'], glyph_rpm, 'Manual-RPM — remote patient monitoring with rule-based live alerts'),
    ]:
        name, num, title, lines, tags, gf, alt = args
        g, css = gf()
        project(name, num, title, lines, tags, g, css, alt)
    label('toolkit', '02', 'Toolkit')
    toolkit()
    label('now', '03', 'Right now')
    now()
    footer()


if __name__ == '__main__':
    for MODE in ('light', 'dark'):
        build()

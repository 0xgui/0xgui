#!/usr/bin/env python3
"""Generate the mood SVGs in assets/. Run after editing the art: python3 scripts/draw_robots.py"""

import math
import os

BODY, SHADE, LINE = "#7B9CFF", "#5A78E6", "#2E3A6E"
SCREEN, EYE, GOLD, PINK, PANEL = "#1D2440", "#7CF5FF", "#FFC857", "#FF8FB1", "#A8BCFF"
S = f'stroke="{LINE}" stroke-width="3" stroke-linejoin="round"'


def antenna(ball=GOLD):
    return (f'<g class="ant"><path d="M120 46V28" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle class="ball" cx="120" cy="22" r="8" fill="{ball}" {S}/></g>'
            f'<rect x="108" y="42" width="24" height="12" rx="5" fill="{SHADE}" {S}/>')


def head(face, screen=SCREEN):
    return (f'<circle cx="46" cy="104" r="10" fill="{SHADE}" {S}/><circle cx="194" cy="104" r="10" fill="{SHADE}" {S}/>'
            f'<rect x="50" y="52" width="140" height="104" rx="34" fill="{BODY}" {S}/>'
            f'<rect x="62" y="60" width="44" height="10" rx="5" fill="#fff" opacity=".35"/>'
            f'<rect x="66" y="72" width="108" height="68" rx="20" fill="{screen}"/>'
            f'<g class="face">{face}</g>')


def arm(side, cls="arm"):
    x = 54 if side == "l" else 168
    return (f'<g class="{cls} {side}"><rect x="{x}" y="166" width="18" height="44" rx="9" fill="{SHADE}" {S}/>'
            f'<circle cx="{x + 9}" cy="212" r="10" fill="{BODY}" {S}/></g>')


def body(chest=""):
    return (f'<rect x="110" y="150" width="20" height="14" fill="{SHADE}" {S}/>'
            f'<rect x="90" y="218" width="20" height="18" rx="6" fill="{SHADE}" {S}/>'
            f'<rect x="130" y="218" width="20" height="18" rx="6" fill="{SHADE}" {S}/>'
            f'<rect x="82" y="230" width="32" height="14" rx="7" fill="{BODY}" {S}/>'
            f'<rect x="126" y="230" width="32" height="14" rx="7" fill="{BODY}" {S}/>'
            f'<rect x="72" y="160" width="96" height="64" rx="24" fill="{BODY}" {S}/>'
            f'<rect x="94" y="176" width="52" height="30" rx="10" fill="{PANEL}" {S}/>'
            f'{chest or chest_lights()}')


def chest_lights(colors=(EYE, GOLD, PINK)):
    return "".join(f'<circle class="led" cx="{106 + 14 * i}" cy="191" r="4.5" fill="{c}"/>' for i, c in enumerate(colors))


def eyes_open():
    return ('<g class="eyes">'
            f'<rect x="88" y="91" width="20" height="26" rx="10" fill="{EYE}"/><rect x="132" y="91" width="20" height="26" rx="10" fill="{EYE}"/>'
            '<circle cx="102" cy="98" r="3.5" fill="#fff"/><circle cx="146" cy="98" r="3.5" fill="#fff"/></g>')


def cheeks(op=".55"):
    return f'<ellipse cx="80" cy="124" rx="7" ry="4" fill="{PINK}" opacity="{op}"/><ellipse cx="160" cy="124" rx="7" ry="4" fill="{PINK}" opacity="{op}"/>'


def smile(d="M110 124Q120 132 130 124", color=EYE):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round"/>'


def shadow(rx=64, cx=120):
    return f'<ellipse cx="{cx}" cy="250" rx="{rx}" ry="7" fill="{BODY}" opacity=".25"/>'


def svg(name, css, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 260" width="240" height="260" role="img">'
            f'<title>Robot is {name}</title><style>{css}</style>{inner}</svg>\n')


def robot(face, chest="", arms=None, ball=GOLD, screen=SCREEN):
    return (antenna(ball) + (arms or arm("l") + arm("r")).split("|")[0] + body(chest)
            + head(face, screen) + ((arms or "").split("|")[1] if arms and "|" in arms else ""))


ARMS_REST = 'g.arm.l{transform:rotate(12deg);transform-origin:63px 170px}g.arm.r{transform:rotate(-12deg);transform-origin:177px 170px}'

MOODS = {}

MOODS["idle"] = svg("idle",
    ARMS_REST +
    '.ant{animation:bob 2.4s ease-in-out infinite;transform-origin:120px 46px}'
    '@keyframes bob{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}'
    '.eyes{animation:blink 4.5s infinite;transform-origin:120px 104px}'
    '@keyframes blink{0%,90%,96%,100%{transform:scaleY(1)}93%{transform:scaleY(.1)}}'
    '.bot{animation:float 3s ease-in-out infinite}'
    '@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}',
    shadow() + '<g class="bot">' + robot(eyes_open() + cheeks() + smile()) + '</g>')

laptop = (f'<rect x="78" y="176" width="84" height="44" rx="6" fill="#E6EAF5" {S}/>'
          f'<circle cx="120" cy="198" r="6" fill="{BODY}"/>'
          f'<rect x="66" y="218" width="108" height="9" rx="4.5" fill="#C7CFE3" {S}/>')
code = ''.join(
    f'<g class="code c{i}"><path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
    for i, (d, c) in enumerate([("M24 70l-8 8 8 8M38 70l8 8-8 8", EYE), ("M206 54l-6 18", GOLD), ("M208 92h14M215 85v14", PINK)]))
MOODS["busy"] = svg("busy",
    'g.arm{transform-origin:63px 170px}g.arm.r{transform-origin:177px 170px}'
    'g.arm.l{animation:tapl .32s ease-in-out infinite alternate}'
    'g.arm.r{animation:tapr .32s ease-in-out infinite alternate-reverse}'
    '@keyframes tapl{from{transform:rotate(-38deg)}to{transform:rotate(-26deg)}}'
    '@keyframes tapr{from{transform:rotate(38deg)}to{transform:rotate(26deg)}}'
    '.eyes{animation:scan 1.6s ease-in-out infinite}'
    '@keyframes scan{0%,100%{transform:translateX(-4px)}50%{transform:translateX(4px)}}'
    '.ant{animation:bob 1s ease-in-out infinite;transform-origin:120px 46px}'
    '@keyframes bob{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}'
    '.code{opacity:0;animation:pop 2.4s ease-out infinite}.c1{animation-delay:.8s}.c2{animation-delay:1.6s}'
    '@keyframes pop{0%{opacity:0;transform:translateY(6px)}20%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translateY(-12px)}}',
    shadow() + robot(
        f'<g class="eyes"><rect x="88" y="100" width="20" height="16" rx="8" fill="{EYE}"/><rect x="132" y="100" width="20" height="16" rx="8" fill="{EYE}"/>'
        f'<path d="M89 93l17 2M151 93l-17 2" stroke="{EYE}" stroke-width="3" stroke-linecap="round"/></g>'
        + smile("M112 126h16"),
        arms=arm("l") + arm("r") + "|" + laptop + arm("l").replace('class="arm', 'class="arm hand') + arm("r").replace('class="arm', 'class="arm hand'))
    .replace('g class="arm l"', 'g class="arm l" opacity="0"', 1).replace('g class="arm r"', 'g class="arm r" opacity="0"', 1) + code)


def tongue(w, h):
    """One flame tongue, base at 0 0 and tip pointing up; leans a little so it reads as fire."""
    return (f"M{-w} 0C{-w} {-h * .45:.0f} {w * .2:.0f} {-h * .55:.0f} {w * .5:.0f} {-h}"
            f"C{w * .1:.0f} {-h * .6:.0f} {w} {-h * .45:.0f} {w} 0Q0 {w * .9:.0f} {-w} 0z")


bolt = "M0 0l9 14h-6l7 14-15-17h6z"
bolts = ''.join(f'<path class="bolt b{i}" transform="translate({x} {y}) rotate({r}) scale(1.5)" d="{bolt}" fill="#FFF3B0" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>'
                for i, (x, y, r) in enumerate([(16, 62, -10), (206, 150, 14), (198, 50, 12), (20, 160, -8)]))
rocks = ''.join(f'<path class="rock r{i}" d="M{x} 246l6-6 8 2 3 7-7 4-8-1z" fill="#8C96B4" stroke="{LINE}" stroke-width="1.5" stroke-linejoin="round"/>'
                for i, x in enumerate([22, 200]))
# x, y, angle, scale of each flame tongue around the robot (left side is mirrored so flames lean outward)
TONGUES = [(52, 212, -24, .9), (40, 160, -16, 1), (46, 106, -10, 1), (72, 72, -8, .85), (102, 62, -3, .85), (120, 64, 0, .9)]
INNER = [(64, 196, -18, .7), (58, 134, -10, .8), (92, 80, -4, .75), (120, 74, 0, .8)]


def flames(spots, fill=""):
    """Each left-side spot plus its mirror on the right; the middle one is drawn once."""
    out = ""
    for x, y, r, k in spots:
        for sx, sr, sk in ((x, r, -k), (240 - x, -r, k))[(x == 120):]:
            out += f'<g transform="translate({sx} {y}) rotate({sr}) scale({sk} {k})"><use class="t" href="#f"{fill}/></g>'
    return out


sparkle = "M0-7Q1-1 7 0Q1 1 0 7Q-1 1-7 0Q-1-1 0-7z"
motes = (f'<g fill="#FFF3B0" stroke="{LINE}" stroke-width="1.3" stroke-linejoin="round">'
         + ''.join(f'<g transform="translate({x} 228) scale({k})"><path class="mote" d="{sparkle}"/></g>'
                   for x, k in ([(30, 1), (210, .9), (62, .7), (180, .8), (14, .6), (228, .6)])) + '</g>')
MOODS["ascending"] = svg("ascending",
    'g.arm.l{transform:rotate(24deg);transform-origin:63px 170px}g.arm.r{transform:rotate(-24deg);transform-origin:177px 170px}'
    '.bot{animation:lift 2.4s ease-in-out infinite}'
    '@keyframes lift{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}'
    '.t{transform-origin:0 0;animation:fl .42s ease-in-out infinite alternate}g:nth-child(odd)>.t{animation-delay:-.21s}g:nth-child(3n)>.t{animation-duration:.33s}'
    '@keyframes fl{from{transform:scale(.92,.82) skewX(-4deg)}to{transform:scale(1.04,1.08) skewX(4deg)}}'
    '.core{animation:pulse 1.2s ease-in-out infinite}@keyframes pulse{50%{opacity:.85}}'
    '.bolt{opacity:0;animation:zap 1.6s steps(1) infinite}.b1,.b3{animation-delay:.8s}'
    '@keyframes zap{0%{opacity:1}12%{opacity:0}18%{opacity:1}26%{opacity:0}}'
    '.mote{opacity:0;animation:rise 1.8s ease-in infinite}g:nth-child(2n)>.mote{animation-delay:-.9s}g:nth-child(3n)>.mote{animation-delay:-.45s}g:nth-child(5)>.mote{animation-delay:-1.35s}'
    '@keyframes rise{0%{opacity:0;transform:translateY(0)}20%{opacity:1}100%{opacity:0;transform:translateY(-260px)}}'
    '.rock{animation:hover 2.4s ease-in-out infinite}.r1{animation-delay:-1.2s}'
    '@keyframes hover{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}',
    f'<defs><path id="f" d="{tongue(22, 62)}"/><radialGradient id="g" cy=".6"><stop offset="0" stop-color="#FFF8DC"/>'
    '<stop offset=".6" stop-color="#FFD166"/><stop offset="1" stop-color="#FFB13B"/></radialGradient></defs>'
    f'<ellipse cx="120" cy="250" rx="40" ry="5" fill="#FF9F1C" opacity=".3"/>{rocks}'
    f'<g fill="#FFB13B" stroke="#F08A00" stroke-width="2" stroke-linejoin="round">{flames(TONGUES)}</g>'
    '<ellipse class="core" cx="120" cy="134" rx="84" ry="92" fill="url(#g)"/>'
    f'<g>{flames(INNER, chr(32) + "fill=\"#FFF3B0\"")}</g>'
    '<g class="bot"><g transform="translate(17 2) scale(.86)">' + robot(
        f'<rect x="88" y="92" width="22" height="26" rx="10" fill="#FFFBEA" stroke="{GOLD}" stroke-width="3"/>'
        f'<rect x="130" y="92" width="22" height="26" rx="10" fill="#FFFBEA" stroke="{GOLD}" stroke-width="3"/>'
        f'<path d="M84 84l26 8M156 84l-26 8" stroke="{GOLD}" stroke-width="4.5" stroke-linecap="round"/>'
        f'<path d="M106 124q14 10 28 0z" fill="{GOLD}" stroke="{GOLD}" stroke-width="3" stroke-linejoin="round"/>',
        chest=chest_lights((GOLD, "#FFFBEA", GOLD)), ball="#FFFBEA") + '</g></g>' + bolts + motes)

zs = ''.join(f'<path class="z z{i}" d="M{x} {y}h{w}l-{w} {w}h{w}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
             for i, (x, y, w, sw, c) in enumerate([(168, 58, 11, 3.5, EYE), (184, 40, 14, 4, PANEL), (201, 20, 17, 4.5, EYE)]))
MOODS["sleeping"] = svg("sleeping",
    ARMS_REST.replace("12deg", "4deg") +
    '.bot{animation:breathe 4s ease-in-out infinite;transform-origin:120px 244px}'
    '@keyframes breathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.975)}}'
    '.z{opacity:0;animation:zz 4.2s ease-in-out infinite}.z1{animation-delay:1.4s}.z2{animation-delay:2.8s}'
    '@keyframes zz{0%{opacity:0;transform:translate(-6px,8px)}30%{opacity:1}100%{opacity:0;transform:translate(6px,-10px)}}',
    shadow() + '<g class="bot">' + robot(
        f'<path d="M88 106q10 9 20 0M132 106q10 9 20 0" fill="none" stroke="{EYE}" stroke-width="4.5" stroke-linecap="round"/>'
        + cheeks(".4") + f'<ellipse cx="120" cy="125" rx="4" ry="3" fill="{EYE}" opacity=".8"/>',
        chest=chest_lights(("#4A5A8A", "#4A5A8A", EYE)), ball="#8C7B4E", screen="#161B30") + '</g>' + zs)

star = "M0-9l2.6 5.6 6.1.7-4.5 4.2 1.2 6L0 14.5l-5.4 3 1.2-6-4.5-4.2 6.1-.7z"
stars = ''.join(f'<path class="st t{i}" d="{star}" fill="{GOLD}" stroke="{LINE}" stroke-width="1.5" stroke-linejoin="round"/>' for i in range(3))
MOODS["fell-over"] = svg("fell over",
    ARMS_REST +
    '.st{offset-path:path("M54 62a40 12 0 1 0 80 0a40 12 0 1 0-80 0");offset-rotate:0deg;animation:orbit 2.4s linear infinite}'
    '.t1{animation-delay:-.8s}.t2{animation-delay:-1.6s}'
    '@keyframes orbit{from{offset-distance:0%}to{offset-distance:100%}}'
    '.ant{animation:wob 1.6s ease-in-out infinite;transform-origin:120px 46px}'
    '@keyframes wob{0%,100%{transform:rotate(-10deg)}50%{transform:rotate(14deg)}}'
    '.dust{animation:puff 2.4s ease-out infinite;transform-origin:200px 244px}'
    '@keyframes puff{0%{opacity:.7;transform:scale(.6)}100%{opacity:0;transform:scale(1.4)}}',
    shadow(104, 112) +
    '<g transform="translate(10 22) rotate(-90 120 140)">' + robot(
        f'<path d="M90 96l16 16M106 96l-16 16M134 96l16 16M150 96l-16 16" stroke="{EYE}" stroke-width="5" stroke-linecap="round"/>'
        + smile("M110 130q10-8 20 0") + cheeks(".4")) + '</g>'
    f'<g class="dust"><circle cx="212" cy="240" r="6" fill="#AFB9D1"/><circle cx="224" cy="232" r="4" fill="#AFB9D1"/></g>' + stars)

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out, exist_ok=True)
    for name, data in MOODS.items():
        with open(os.path.join(out, f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(data)
        print(f"{name}.svg {len(data.encode())} bytes")

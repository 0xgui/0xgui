#!/usr/bin/env python3
"""Draw the profile robot as one composed SVG.

robot.py calls compose(mood, level, tier, streak) and writes assets/robot.svg.
Run this file directly to write every mood, power level and gear tier to preview/ for a look:
python3 scripts/draw_robots.py
"""

import math
import os

BODY, SHADE, LINE = "#7B9CFF", "#5A78E6", "#2E3A6E"
SCREEN, EYE, GOLD, PINK, PANEL = "#1D2440", "#7CF5FF", "#FFC857", "#FF8FB1", "#A8BCFF"
S = 'class="o"'  # the dark outline every part shares, styled once in svg()


def antenna(ball=GOLD, extra=""):
    return (f'<g class="ant"><path d="M120 46V28" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>'
            f'<circle class="ball o" cx="120" cy="22" r="8" fill="{ball}"/>{extra}</g>'
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


FONT = "font-family=\"-apple-system,Segoe UI,Helvetica,Arial,sans-serif\""
# CSS for gear tiers 1 to 4, then the streak badge flame
GEAR_CSS = ('.sig{animation:sig 1.6s ease-out infinite}.sig+.sig{animation-delay:.8s}@keyframes sig{0%{opacity:0}30%{opacity:1}100%{opacity:0}}',
            '.tail{animation:flap .5s ease-in-out infinite alternate;transform-origin:142px 160px}@keyframes flap{to{transform:rotate(-9deg)}}',
            '.jet{animation:jet .18s ease-in-out infinite alternate;transform-origin:center top;transform-box:fill-box}@keyframes jet{to{transform:scaleY(.7)}}',
            '',
            '.bf{animation:bf .4s ease-in-out infinite alternate;transform-origin:center bottom;transform-box:fill-box}@keyframes bf{to{transform:scale(.8,.65)}}')


def svg(name, css, inner, streak=None, tier=0):
    """The robot plus, when streak is given, a streak badge under it. Badge rows add 28px of height."""
    gear_css = "".join(GEAR_CSS[:tier]) + (GEAR_CSS[4] if streak else "")
    h = 260 if streak is None else 288
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 {h}" width="240" height="{h}" role="img">'
            f'<title>Robot is {name}</title><style>.o{{stroke:{LINE};stroke-width:3px;stroke-linejoin:round}}{css}{gear_css}</style>{inner}{badge(streak)}</svg>\n')


def badge(streak):
    if streak is None:
        return ""
    text = f"{streak}-day streak" if streak else "No streak yet"
    w = 38 + 7 * len(text)
    x = 120 - w / 2
    hot = streak > 0
    return (f'<rect x="{x:.0f}" y="261" width="{w}" height="24" rx="12" fill="{LINE}" stroke="{BODY}" stroke-width="2"/>'
            f'<g transform="translate({x + 17:.0f} 279)"><path class="bf" d="M-6 0c-3-5 1-8 3-12 0 3 2 4 3 2 1-2 0-5-1-7 5 2 8 8 7 12-1 4-3 5-6 5h-2c-3 0-4-0-4 0z" '
            f'fill="{GOLD if hot else "#8C96B4"}" stroke="{"#FF8A3D" if hot else "#5A6488"}" stroke-width="1.5" stroke-linejoin="round"/></g>'
            f'<text x="{x + 29:.0f}" y="277.5" {FONT} font-size="12.5" font-weight="700" fill="#fff">{text}</text>')


# Evolution gear names by tier (thresholds live in robot.py). Each tier keeps the gear before it.
GEAR = ("Bare", "Antenna", "Scarf", "Jetpack", "Crown")


def gear(tier, jet_flame=True, crown_up=0):
    """SVG pieces for the gear of a tier: (behind the robot, on the antenna, in front of the robot)."""
    back = ant = front = ""
    if tier >= 1:  # beacon: an orbit ring and signal waves on the antenna ball
        ant = (f'<ellipse cx="120" cy="22" rx="14" ry="4.5" fill="none" stroke="{GOLD}" stroke-width="2.5" transform="rotate(-14 120 22)"/>'
               f'<g fill="none" stroke="#2BB8D9" stroke-width="3" stroke-linecap="round"><path class="sig" d="M100 14q-5 8 0 16M140 14q5 8 0 16"/>'
               '<path class="sig" d="M92 9q-8 13 0 26M148 9q8 13 0 26"/></g>')
    if tier >= 3:  # jetpack tanks behind the body, with flame when awake
        for x in (50, 166):
            back += (f'<rect x="{x}" y="146" width="24" height="60" rx="11" fill="#FF7A59" {S}/>'
                     f'<rect x="{x}" y="164" width="24" height="9" fill="#FFE9A0" {S}/>'
                     f'<path d="M{x + 5} 206h14l3 9h-20z" fill="{SHADE}" {S}/>')
            if jet_flame:
                back += f'<path class="jet" d="M{x + 3} 216h18l-9 26z" fill="{GOLD}" stroke="#FF8A3D" stroke-width="2" stroke-linejoin="round"/>'
    if tier >= 2:  # scarf around the neck, tail flapping
        front += (f'<g class="tail"><path d="M140 158l26 26-6 8-26-22zM140 160l12 34-8 3-10-30z" fill="#FF5C7A" {S}/></g>'
                  f'<rect x="84" y="148" width="72" height="16" rx="8" fill="#FF5C7A" {S}/>'
                  f'<path d="M98 150v12M112 150v12M126 150v12" stroke="#FFB3C2" stroke-width="3" stroke-linecap="round"/>'
                  f'<circle cx="142" cy="160" r="7" fill="#E84463" {S}/>')
    if tier >= 4:  # crown with the antenna ball as its top jewel
        front += (f'<g transform="translate(0 -{crown_up})">' if crown_up else '') + (f'<path d="M84 56l-4-26 18 12 10-16 12 10 12-10 10 16 18-12-4 26z" fill="{GOLD}" {S}/>'
                  f'<rect x="82" y="50" width="76" height="10" rx="4" fill="#FFB13B" {S}/>'
                  f'<circle cx="100" cy="55" r="3" fill="{PINK}"/><circle cx="120" cy="55" r="3" fill="{EYE}"/><circle cx="140" cy="55" r="3" fill="{PINK}"/>') + ('</g>' if crown_up else '')
    return back, ant, front


def robot(face, chest="", arms=None, ball=GOLD, screen=SCREEN, kit=("", "", ""), hair=""):
    back, ant, front = kit
    arms_back, _, arms_front = (arms or arm("l") + arm("r")).partition("|")
    return (back + antenna(ball, ant) + arms_back + body(chest)
            + head(face, screen) + hair + front + arms_front)


ARMS_REST = 'g.arm.l{transform:rotate(12deg);transform-origin:63px 170px}g.arm.r{transform:rotate(-12deg);transform-origin:177px 170px}'


def idle(tier, level):
    return "idle", (
        ARMS_REST +
        '.ant{animation:bob 2.4s ease-in-out infinite;transform-origin:120px 46px}'
        '@keyframes bob{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}'
        '.eyes{animation:blink 4.5s infinite;transform-origin:120px 104px}'
        '@keyframes blink{0%,90%,96%,100%{transform:scaleY(1)}93%{transform:scaleY(.1)}}'
        '.bot{animation:float 3s ease-in-out infinite}'
        '@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}'), (
        shadow() + '<g class="bot">' + robot(eyes_open() + cheeks() + smile(), kit=gear(tier)) + '</g>')


laptop = (f'<rect x="78" y="176" width="84" height="44" rx="6" fill="#E6EAF5" {S}/>'
          f'<circle cx="120" cy="198" r="6" fill="{BODY}"/>'
          f'<rect x="66" y="218" width="108" height="9" rx="4.5" fill="#C7CFE3" {S}/>')
code = ''.join(
    f'<g class="code c{i}"><path d="{d}" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
    for i, (d, c) in enumerate([("M24 70l-8 8 8 8M38 70l8 8-8 8", EYE), ("M206 54l-6 18", GOLD), ("M208 92h14M215 85v14", PINK)]))


def busy(tier, level):
    return "busy", (
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
        '@keyframes pop{0%{opacity:0;transform:translateY(6px)}20%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translateY(-12px)}}'), (
        shadow() + robot(
            f'<g class="eyes"><rect x="88" y="100" width="20" height="16" rx="8" fill="{EYE}"/><rect x="132" y="100" width="20" height="16" rx="8" fill="{EYE}"/>'
            f'<path d="M89 93l17 2M151 93l-17 2" stroke="{EYE}" stroke-width="3" stroke-linecap="round"/></g>'
            + smile("M112 126h16"),
            arms=arm("l") + arm("r") + "|" + laptop + arm("l").replace('class="arm', 'class="arm hand') + arm("r").replace('class="arm', 'class="arm hand'),
            kit=gear(tier))
        .replace('g class="arm l"', 'g class="arm l" opacity="0"', 1).replace('g class="arm r"', 'g class="arm r" opacity="0"', 1) + code)


def tongue(w, h):
    """One flame tongue, base at 0 0 and tip pointing up; leans a little so it reads as fire."""
    return (f"M{-w} 0C{-w} {-h * .45:.0f} {w * .2:.0f} {-h * .55:.0f} {w * .5:.0f} {-h}"
            f"C{w * .1:.0f} {-h * .6:.0f} {w} {-h * .45:.0f} {w} 0Q0 {w * .9:.0f} {-w} 0z")


def num(v):
    """Short number for SVG attributes: .9 instead of 0.9, -.9 instead of -0.9."""
    return f"{v:g}".replace("0.", ".")


def flames(spots, fill=""):
    """Each left-side spot plus its mirror on the right; the middle one is drawn once."""
    out, n = "", 0
    for x, y, r, k in spots:
        for sx, sr, sk in ((x, r, -k), (240 - x, -r, k))[(x == 120):]:
            out += f'<use transform="translate({sx} {y}) rotate({sr}) scale({num(sk)} {num(k)})" href="#{"fh"[n % 2]}"{fill}/>'
            n += 1
    return out


BOLT = "M0 0l13 21h-9l11 21-23-26h9z"
BOLT_SPOTS = [(16, 62, -10), (206, 150, 14), (198, 50, 12), (20, 160, -8), (2, 108, -4), (224, 96, 8), (44, 14, -16), (180, 204, 10)]
ROCKS = ''.join(f'<path class="rock r{i}" d="M{x} 246l6-6 8 2 3 7-7 4-8-1z" fill="#8C96B4" stroke="{LINE}" stroke-width="1.5" stroke-linejoin="round"/>'
                for i, x in enumerate([22, 200]))
# x, y, angle, scale of each flame tongue around the robot (left side is mirrored so flames lean outward)
TONGUES = [(52, 212, -24, .9), (40, 160, -16, 1), (46, 106, -10, 1), (72, 72, -8, .85), (102, 62, -3, .85), (120, 64, 0, .9)]
OUTER = [(36, 222, -30, .8), (28, 168, -22, .9), (30, 114, -16, .9), (50, 66, -12, .85), (84, 46, -6, .8)]
INNER = [(64, 196, -18, .7), (58, 134, -10, .8), (92, 80, -4, .75), (120, 74, 0, .8)]
SPARKLE = "M0-7Q1-1 7 0Q1 1 0 7Q-1 1-7 0Q-1-1 0-7z"
MOTES = (f'<g fill="#FFF3B0" stroke="{LINE}" stroke-width="1.3" stroke-linejoin="round">'
         + ''.join(f'<g transform="translate({x} 228) scale({k})"><path class="mote" d="{SPARKLE}"/></g>'
                   for x, k in ([(30, 1), (210, .9), (62, .7), (180, .8), (14, .6), (228, .6)])) + '</g>')
HAIR = ('<g class="hair"><path d="M50 100L28 70l26 0-12-38 38 20 2-42 26 34 12-8 12 8 26-34 2 42 38-20-12 38 26 0-22 30'
        f'l-8-26-14-6-12 14-10-14-18 18-18-18-10 14-12-14-14 6z" fill="{GOLD}" {S}/>'
        '<path d="M48 66l-8-24 26 14M192 66l8-24-26 14M86 46l2-24 16 22M154 46l-2-24-16 22" fill="none" stroke="#FFF3B0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>')


def zigzag(n=26, cx=120, cy=196, rx=104, ry=18):
    """A jagged ellipse, like an electric arc, as a back half (top) and a front half (bottom)."""
    halves = []
    for start in (math.pi, 0):
        pts = []
        for i in range(n + 1):
            t = start + math.pi * i / n
            k = 1 + (.05 if i % 2 else -.05) * (0 < i < n)
            pts.append(f"{cx + rx * k * math.cos(t):.0f} {cy + ry * k * math.sin(t):.0f}")
        halves.append("M" + "L".join(pts))
    return halves


def ring(front):
    """Half of the electric ring around the hips; the back half is drawn behind the robot."""
    i = int(front)
    return (f'<use href="#z{i}" stroke="{LINE}" stroke-width="6"/><use class="zz" href="#z{i}" stroke="{EYE}" stroke-width="2.5"/>')


def ascending(tier, level):
    aura, core, edge = (("#FFD23F", "#FFFFFF", "#F59E0B") if level >= 3 else ("#FFB13B", "#FFF8DC", "#F08A00"))
    n_bolts, beat = {1: (4, 1.6), 2: (6, 1.2), 3: (8, .8)}[level]
    bolts = ''.join(f'<path class="bolt b{i % 2}" transform="translate({x} {y}) rotate({r})" d="{BOLT}"/>'
                    for i, (x, y, r) in enumerate(BOLT_SPOTS[:n_bolts]))
    css = ('g.arm.l{transform:rotate(24deg);transform-origin:63px 170px}g.arm.r{transform:rotate(-24deg);transform-origin:177px 170px}'
           '.bot{animation:lift 2.4s ease-in-out infinite}'
           '@keyframes lift{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}'
           '#f,#h{transform-origin:0 0;animation:fl .42s ease-in-out infinite alternate}#h{animation:fl .33s ease-in-out -.2s infinite alternate}'
           '@keyframes fl{from{transform:scale(.92,.82) skewX(-4deg)}to{transform:scale(1.04,1.08) skewX(4deg)}}'
           '.core{animation:pulse 1.2s ease-in-out infinite}@keyframes pulse{50%{opacity:.85}}'
           f'.bolt{{opacity:0;animation:zap {beat}s steps(1) infinite}}.b1{{animation-delay:{beat / 2}s}}'
           '@keyframes zap{0%{opacity:1}12%{opacity:0}18%{opacity:1}26%{opacity:0}}'
           '.mote{opacity:0;animation:rise 1.8s ease-in infinite}g:nth-child(2n)>.mote{animation-delay:-.9s}g:nth-child(3n)>.mote{animation-delay:-.45s}g:nth-child(5)>.mote{animation-delay:-1.35s}'
           '@keyframes rise{0%{opacity:0;transform:translateY(0)}20%{opacity:1}100%{opacity:0;transform:translateY(-260px)}}'
           '.rock{animation:hover 2.4s ease-in-out infinite}.r1{animation-delay:-1.2s}'
           '@keyframes hover{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}')
    if level >= 2:
        css += '.zz{animation:zap2 .5s steps(1) infinite}@keyframes zap2{70%{stroke:#fff}}'
    if level >= 3:
        css += ('.all{animation:quake 1.6s infinite}@keyframes quake{0%,20%,100%{transform:translate(0,0)}4%{transform:translate(-3px,1px)}'
                '8%{transform:translate(3px,-1px)}12%{transform:translate(-2px,-1px)}16%{transform:translate(2px,1px)}}'
                '.hair{animation:hair .3s ease-in-out infinite alternate;transform-origin:120px 96px}@keyframes hair{to{transform:scaleY(1.05)}}')
    inner = (f'<defs><path id="f" d="{tongue(22, 62)}"/><path id="h" d="{tongue(22, 62)}"/>'
             + (''.join(f'<path id="z{i}" d="{d}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>' for i, d in enumerate(zigzag())) if level >= 2 else '')
             + f'<radialGradient id="g" cy=".6"><stop offset="0" stop-color="{core}"/>'
             f'<stop offset=".6" stop-color="#FFD166"/><stop offset="1" stop-color="{aura}"/></radialGradient></defs>'
             f'<g class="all"><ellipse cx="120" cy="250" rx="40" ry="5" fill="#FF9F1C" opacity=".3"/>{ROCKS}'
             + (f'<g fill="#FFE08A" stroke="{edge}" stroke-width="2" stroke-linejoin="round">{flames(OUTER)}</g>' if level >= 2 else '')
             + f'<g fill="{aura}" stroke="{edge}" stroke-width="2" stroke-linejoin="round">{flames(TONGUES)}</g>'
             '<ellipse class="core" cx="120" cy="134" rx="84" ry="92" fill="url(#g)"/>'
             f'<g>{flames(INNER, " fill=" + chr(34) + "#FFF3B0" + chr(34))}</g>'
             '<g class="bot"><g transform="translate(17 2) scale(.86)">' + (ring(False) if level >= 2 else '') + robot(
                 f'<rect x="88" y="92" width="22" height="26" rx="10" fill="#FFFBEA" stroke="{GOLD}" stroke-width="3"/>'
                 f'<rect x="130" y="92" width="22" height="26" rx="10" fill="#FFFBEA" stroke="{GOLD}" stroke-width="3"/>'
                 f'<path d="M84 84l26 8M156 84l-26 8" stroke="{GOLD}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<path d="M106 124q14 10 28 0z" fill="{GOLD}" stroke="{GOLD}" stroke-width="3" stroke-linejoin="round"/>',
                 chest=chest_lights((GOLD, "#FFFBEA", GOLD)), ball="#FFFBEA", kit=gear(tier, crown_up=12 if level >= 3 else 0), hair=HAIR if level >= 3 else "")
             + (ring(True) if level >= 2 else '') + '</g></g>'
             f'<g fill="#FFF3B0" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round">{bolts}</g>' + MOTES + '</g>')
    title = "ascending" if level == 1 else f"ascending at power level {level}"
    return title, css, inner


ZS = ''.join(f'<path class="z z{i}" d="M{x} {y}h{w}l-{w} {w}h{w}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
             for i, (x, y, w, sw, c) in enumerate([(168, 58, 11, 3.5, EYE), (184, 40, 14, 4, PANEL), (201, 20, 17, 4.5, EYE)]))


def sleeping(tier, level):
    return "sleeping", (
        ARMS_REST.replace("12deg", "4deg") +
        '.bot{animation:breathe 4s ease-in-out infinite;transform-origin:120px 244px}'
        '@keyframes breathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.975)}}'
        '.z{opacity:0;animation:zz 4.2s ease-in-out infinite}.z1{animation-delay:1.4s}.z2{animation-delay:2.8s}'
        '@keyframes zz{0%{opacity:0;transform:translate(-6px,8px)}30%{opacity:1}100%{opacity:0;transform:translate(6px,-10px)}}'), (
        shadow() + '<g class="bot">' + robot(
            f'<path d="M88 106q10 9 20 0M132 106q10 9 20 0" fill="none" stroke="{EYE}" stroke-width="4.5" stroke-linecap="round"/>'
            + cheeks(".4") + f'<ellipse cx="120" cy="125" rx="4" ry="3" fill="{EYE}" opacity=".8"/>',
            chest=chest_lights(("#4A5A8A", "#4A5A8A", EYE)), ball="#8C7B4E", screen="#161B30", kit=gear(tier, jet_flame=False)) + '</g>' + ZS)


STAR = "M0-9l2.6 5.6 6.1.7-4.5 4.2 1.2 6L0 14.5l-5.4 3 1.2-6-4.5-4.2 6.1-.7z"
STARS = ''.join(f'<path class="st t{i}" d="{STAR}" fill="{GOLD}" stroke="{LINE}" stroke-width="1.5" stroke-linejoin="round"/>' for i in range(3))


def fell_over(tier, level):
    return "fell over", (
        ARMS_REST +
        '.st{offset-path:path("M54 62a40 12 0 1 0 80 0a40 12 0 1 0-80 0");offset-rotate:0deg;animation:orbit 2.4s linear infinite}'
        '.t1{animation-delay:-.8s}.t2{animation-delay:-1.6s}'
        '@keyframes orbit{from{offset-distance:0%}to{offset-distance:100%}}'
        '.ant{animation:wob 1.6s ease-in-out infinite;transform-origin:120px 46px}'
        '@keyframes wob{0%,100%{transform:rotate(-10deg)}50%{transform:rotate(14deg)}}'
        '.dust{animation:puff 2.4s ease-out infinite;transform-origin:200px 244px}'
        '@keyframes puff{0%{opacity:.7;transform:scale(.6)}100%{opacity:0;transform:scale(1.4)}}'), (
        shadow(104, 112) +
        '<g transform="translate(10 22) rotate(-90 120 140)">' + robot(
            f'<path d="M90 96l16 16M106 96l-16 16M134 96l16 16M150 96l-16 16" stroke="{EYE}" stroke-width="5" stroke-linecap="round"/>'
            + smile("M110 130q10-8 20 0") + cheeks(".4"), kit=gear(tier, jet_flame=False)) + '</g>'
        f'<g class="dust"><circle cx="212" cy="240" r="6" fill="#AFB9D1"/><circle cx="224" cy="232" r="4" fill="#AFB9D1"/></g>' + STARS)


MOODS = {"sleeping": sleeping, "idle": idle, "busy": busy, "ascending": ascending, "fell-over": fell_over}


def compose(mood, level=1, tier=0, streak=None):
    """One SVG: the mood's robot wearing the gear of its evolution tier, with an optional streak badge."""
    title, css, inner = MOODS[mood](tier, level)
    return svg(title, css, inner, streak, tier)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "preview", "parts")
    os.makedirs(out, exist_ok=True)
    variants = [(m, 1, 0) for m in MOODS] + [("ascending", lv, 0) for lv in (2, 3)]
    variants += [(m, 1, t) for m in MOODS for t in range(1, len(GEAR))] + [("ascending", 3, 4)]
    for mood, level, tier in variants:
        name = f"{mood}-p{level}-g{tier}.svg"
        data = compose(mood, level, tier, streak=12)
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(data)
        print(f"{name} {len(data.encode())} bytes")

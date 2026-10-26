"""Generate a script-free animated SVG from the public GitHub contribution calendar."""
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import argparse
import urllib.request


def parse_calendar(text):
    class CalendarParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.days = {}

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'data-date' in attrs and 'data-level' in attrs:
                day = date.fromisoformat(attrs['data-date'])
                level = int(attrs['data-level'])
                if not 0 <= level <= 4:
                    raise ValueError('Invalid contribution level')
                self.days[day] = level

    parser = CalendarParser()
    parser.feed(text)
    days = sorted(parser.days.items())
    if len(days) < 350 or len(days) > 371:
        raise ValueError('GitHub calendar missing or incomplete; keep the previous SVG')
    if (days[-1][0] - days[0][0]).days + 1 != len(days):
        raise ValueError('GitHub calendar contains missing days')
    return days


def render(days):
    colors = ['#1D2738', '#263D78', '#4664B9', '#7B7BEA', '#B8A2FF']
    first = days[0][0]
    offset = (first.weekday() + 1) % 7
    weeks = ((days[-1][0] - first).days + offset) // 7 + 1
    left, top, step, duration = 78, 100, 15, 22
    right = left + (weeks - 1) * step
    rows = []
    for row in range(7):
        y = top + row * step + 5.5
        start, end = (left - 30, right + 30) if row % 2 == 0 else (right + 30, left - 30)
        rows.append(f'{"M" if row == 0 else "L"}{start},{y} L{end},{y}')
    path = ' '.join(rows) + f' L{left - 30},{top + 5.5}'
    styles = []
    cells, effects = [], []
    for index, (day, level) in enumerate(days):
        elapsed = (day - first).days + offset
        col, row = divmod(elapsed, 7)
        x, y = left + col * step, top + row * step
        # Each horizontal pass lasts 2.8 seconds, with 0.15s to turn.
        progress = (col + 2) / (weeks + 3) if row % 2 == 0 else (weeks + 1 - col) / (weeks + 3)
        hit = row * 3 + progress * 2.8
        pct = hit / duration * 100
        style = ''
        if level:
            styles.append(f'@keyframes hit{index}{{0%,{pct:.3f}%{{opacity:1}}{pct + .3:.3f}%,99.5%{{opacity:0}}100%{{opacity:1}}}}')
            style = f' style="animation:hit{index} {duration}s linear infinite"'
            burst_start = max(0, (hit - .17) / duration)
            burst_end = min(.99, (hit + .22) / duration)
            times = f'0;{burst_start:.5f};{hit / duration:.5f};{burst_end:.5f};1'
            direction = 1 if row % 2 == 0 else -1
            effects.append(f'''<g class="impact" opacity="0">
              <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="{times}" dur="{duration}s" repeatCount="indefinite"/>
              <path d="M{x + 5.5},{y - 3}v-5 m0,27v-5 M{x - 3},{y + 5.5}h-5 m27,0h-5 M{x - 2},{y - 2}l-4,-4 m19,19l4,4 M{x - 2},{y + 13}l-4,4 m19,-19l4,-4" stroke="#FBBF24" stroke-width="1.6"/>
              <circle cx="{x + 5.5}" cy="{y + 5.5}" r="7" fill="#FDE68A" opacity=".65"/>
            </g>
            <line class="shot" x1="{x + 5.5 - direction * 32}" x2="{x + 5.5 - direction * 22}" y1="{y + 5.5}" y2="{y + 5.5}" stroke="#67E8F9" stroke-width="2" opacity="0">
              <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="{times}" dur="{duration}s" repeatCount="indefinite"/>
              <animateTransform attributeName="transform" type="translate" values="0 0;0 0;{direction * 25} 0;{direction * 25} 0;0 0" keyTimes="{times}" dur="{duration}s" repeatCount="indefinite"/>
            </line>''')
        cells.append(f'<rect class="day" x="{x}" y="{y}" width="11" height="11" rx="2.5" fill="{colors[level]}"{style}><title>{escape(day.isoformat())}: nível de atividade {level}/4</title></rect>')
    # Explicit timing keeps the airplane aligned with the per-day impacts.
    motion_values, motion_times = [], []
    for row in range(7):
        y = top + row * step + 5.5
        start, end = (left - 30, right + 30) if row % 2 == 0 else (right + 30, left - 30)
        motion_values.extend([f'{start} {y}', f'{end} {y}'])
        motion_times.extend([row * 3 / duration, (row * 3 + 2.8) / duration])
    motion_values.append(motion_values[0])
    motion_times.append(1)
    # animateMotion with keyPoints matches horizontal passes and turns exactly.
    segments = []
    coords = [tuple(map(float, value.split())) for value in motion_values]
    for a, b in zip(coords, coords[1:]):
        segments.append(((a[0]-b[0])**2 + (a[1]-b[1])**2)**.5)
    total = sum(segments)
    lengths = [0]
    for length in segments:
        lengths.append(lengths[-1] + length / total)
    points = ';'.join(f'{v:.7f}' for v in lengths)
    times = ';'.join(f'{v:.7f}' for v in motion_times)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="title description">
    <title id="title">Avião no calendário de contribuições de FabricioSantossa</title>
    <desc id="description">Um avião percorre os sete dias da semana e dispara nos quadradinhos com contribuições. Calendário público de {days[0][0]} a {days[-1][0]}. A animação reinicia a cada 22 segundos.</desc>
    <style>{''.join(styles)} @media(prefers-reduced-motion:reduce){{.day{{animation:none!important}}.aircraft,.impact,.shot{{display:none}}}}</style>
    <defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0D1117"/><stop offset="1" stop-color="#151C33"/></linearGradient></defs>
    <rect x="1" y="1" width="958" height="298" rx="20" fill="url(#bg)" stroke="#30363D"/>
    <text x="38" y="41" fill="#A78BFA" font-family="Segoe UI,Arial,sans-serif" font-size="12" letter-spacing="3">FLIGHT LOG / GITHUB</text>
    <text x="38" y="71" fill="#F0F6FC" font-family="Segoe UI,Arial,sans-serif" font-size="23" font-weight="700">Cada contribuição, um novo destino.</text>
    <text x="920" y="43" text-anchor="end" fill="#8B9AB4" font-family="Segoe UI,Arial,sans-serif" font-size="12">@FabricioSantossa</text>
    {''.join(cells)}{''.join(effects)}
    <g class="aircraft">
      <animateMotion path="{path}" dur="{duration}s" rotate="auto" calcMode="linear" keyPoints="{points}" keyTimes="{times}" repeatCount="indefinite"/>
      <path d="M-15,-3 L-26,0 L-15,3Z" fill="#FBBF24" opacity=".8"/>
      <path d="M17,0 L3,-4 L-8,-17 L-13,-17 L-8,-3 L-16,-4 L-19,-10 L-23,-10 L-20,0 L-23,10 L-19,10 L-16,4 L-8,3 L-13,17 L-8,17 L3,4Z" fill="#60A5FA" stroke="#BAE6FD" stroke-width=".7"/>
      <path d="M3,-2 L10,0 L3,2 L-3,0Z" fill="#E0F2FE"/>
    </g>
    <text x="38" y="260" fill="#8B9AB4" font-family="Segoe UI,Arial,sans-serif" font-size="12">CONTRIBUIÇÕES / ÚLTIMOS 12 MESES</text>
    <text x="38" y="281" fill="#64748B" font-family="Segoe UI,Arial,sans-serif" font-size="11">{days[0][0]} — {days[-1][0]} · animação em loop</text>
    <text x="792" y="269" fill="#8B9AB4" font-family="Segoe UI,Arial,sans-serif" font-size="11">Menos</text>
    {''.join(f'<rect x="{834+i*15}" y="259" width="11" height="11" rx="2" fill="{color}"/>' for i,color in enumerate(colors))}
    <text x="916" y="269" fill="#8B9AB4" font-family="Segoe UI,Arial,sans-serif" font-size="11">Mais</text>
    </svg>'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', type=Path)
    parser.add_argument('--output', type=Path, default=Path('profile/flight.svg'))
    args = parser.parse_args()
    if args.html:
        source = args.html.read_text(encoding='utf-8')
    else:
        request = urllib.request.Request('https://github.com/users/FabricioSantossa/contributions', headers={'User-Agent': 'FabricioSantossa-profile-flight', 'Accept': 'text/html'})
        with urllib.request.urlopen(request, timeout=30) as response:
            source = response.read().decode('utf-8')
    days = parse_calendar(source)
    svg = render(days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding='utf-8')
    print(f'Generated {args.output}: {len(days)} days, {sum(level > 0 for _, level in days)} active days')

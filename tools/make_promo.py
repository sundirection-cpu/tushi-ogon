"""Промо-материалы для Яндекс Игр: иконка, обложки (RU/EN) и скриншоты.
Рисуются кодом самой игры в безголовом Chrome (Flatpak), складываются в ../yandex/promo/.
Сначала запусти tools/build_yandex.py. Запуск: python3 tools/make_promo.py
Размеры поменять легко: см. ICON/COVER/SHOTS ниже."""
import os, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'yandex', 'build', 'index.html')
OUT = os.path.join(ROOT, 'yandex', 'promo')
TMP = os.path.join(subprocess.check_output(['xdg-user-dir', 'DOWNLOAD'], text=True).strip(), 'tushi-promo-tmp')
HOOK = "show('menu');\n  requestAnimationFrame(frame);"

SCENE = r"""
function bgNight(g, W, H, ground){
  g.imageSmoothingEnabled = false;
  g.fillStyle = '#1e1833'; g.fillRect(0, 0, W, H);
  ['#0d0a17','#120e20','#181329','#1e1833'].forEach((col, i) => { g.fillStyle = col; g.fillRect(0, i * ground / 4, W, ground / 4 + 1); });
  for (const [x, y, tw] of STARS) { g.fillStyle = tw > .7 ? '#fff6c2' : '#9a8fb0'; g.fillRect(x * W / 160 | 0, y * ground / 60 | 0, 1, 1); }
  for (let i = 0; i * 19 < W + 20; i++) pine(g, 6 + i * 19 + (i % 2) * 5, ground + 2, 22 + (i * 7 % 11), '#161d22', null);
  g.fillStyle = '#22301f'; g.fillRect(0, ground, W, H - ground);
  const R = rnd(5); for (let i = 0; i < W * 2; i++) { g.fillStyle = R() < .5 ? '#2b3c28' : '#1a2418'; g.fillRect(R() * W | 0, ground + (R() * (H - ground) | 0), 1, 1); }
}
function puff(g, x, y, r){ [[0,0,r],[r*.8,-r*.3,r*.75],[-r*.8,-r*.2,r*.7],[r*.2,-r*.9,r*.7]].forEach(([dx,dy,rr],i) => {
  g.fillStyle = i % 2 ? '#c9d3db' : '#eef5f8'; g.beginPath(); g.arc(Math.round(x+dx), Math.round(y+dy), Math.round(rr), 0, 7); g.fill(); }); }
function drops(g, x, y){ g.fillStyle = '#7fd6ff'; [[-6,2],[7,0],[-9,-4],[10,-5],[-3,-7],[4,-9]].forEach(([dx,dy]) => g.fillRect(x+dx, y+dy, 1, 2)); }
function big(g, spr, x, y, s){ g.drawImage(spr, x, y, 16 * s, 16 * s); }
function stage(W, H, scale){
  document.body.innerHTML = ''; document.body.style.cssText = 'margin:0;padding:0;background:#120e1a;overflow:hidden';
  screen = 'promo';
  const box = document.createElement('div'); box.style.cssText = 'position:relative;width:' + W*scale + 'px;height:' + H*scale + 'px';
  const c = document.createElement('canvas'); c.width = W; c.height = H; c.style.cssText = 'width:100%;height:100%;image-rendering:pixelated';
  box.appendChild(c); document.body.appendChild(box); return [c.getContext('2d'), box];
}
"""

ICON = SCENE + r"""
const [g] = stage(128, 128, 4); const now = 1000;
bgNight(g, 128, 128, 86);
glow(g, 46, 92, now, 1, 2.6);
big(g, SPR.fireA, 14, 50, 3);
big(g, SPR.barrel, 66, 58, 3);
puff(g, 62, 50, 9); puff(g, 50, 36, 7); puff(g, 68, 28, 5);
drops(g, 62, 66);
"""

def cover(lang):
    title = {'ru': 'Туши огонь', 'en': 'Put Out<br>the Fire'}[lang]
    size = {'ru': 56, 'en': 48}[lang]
    return SCENE + r"""
const [g, box] = stage(160, 94, 5); const now = 1000;
bgNight(g, 160, 94, 66);
g.fillStyle = '#e8e2c8'; g.beginPath(); g.arc(146, 12, 5, 0, 7); g.fill(); g.fillStyle = '#0d0a17'; g.beginPath(); g.arc(149, 10, 5, 0, 7); g.fill();
glow(g, 118, 75, now, 1, 1.4);
g.drawImage(SPR.fireOut, 136, 66); puff(g, 144, 62, 5); puff(g, 140, 52, 4); drops(g, 144, 72);
g.drawImage(fireSpr(now, 0), 110, 66);
shadow(g, 70, 68); g.drawImage(SPR.hero.right1, 70, 64);
shadow(g, 86, 68); g.drawImage(SPR.barrel, 86, 66);
g.drawImage(SPR.fireOut, 22, 70); puff(g, 30, 64, 3);
const h = document.createElement('div');
h.innerHTML = '""" + title + r"""';
h.style.cssText = 'position:absolute;left:44px;top:34px;font:""" + str(size) + r"""px/1.25 "Press Start 2P";color:#ff8f1f;text-shadow:5px 5px 0 #000,0 0 30px rgba(255,120,30,.45)';
box.appendChild(h);
"""

def shot_level(lang, lvl, moves):
    # ходы задаются строкой направлений; последний толчок гасит костёр — на снимке виден пар
    seq = ','.join({'u': '[0,-1]', 'd': '[0,1]', 'l': '[-1,0]', 'r': '[1,0]'}[m] for m in moves)
    return f"applyLang('{lang}'); startLevel({lvl}); [{seq}].forEach((d, i) => setTimeout(() => tryMove(...d), 150 + i * 140));"

ICON_SIZE = (512, 512)
COVER_SIZE = (800, 470)
SHOTS = [  # имя, ширина, высота, масштаб (dpr), код
    ('desktop-1', 1280, 720, 1.5, shot_level('ru', 0, 'drrr')),
    ('desktop-2', 1280, 720, 1.5, shot_level('ru', 14, '')),
    ('desktop-3', 1280, 720, 1.5, "applyLang('ru'); for(let i=0;i<9;i++)prog.best[i]=9+i%4; show('levels');"),
    ('mobile-1', 360, 640, 3, shot_level('ru', 2, 'u')),
    ('mobile-2', 360, 640, 3, shot_level('ru', 29, '')),
    ('mobile-3', 360, 640, 3, "applyLang('ru'); show('menu');"),
    ('en-desktop-1', 1280, 720, 1.5, shot_level('en', 0, 'drrr')),
    ('en-mobile-1', 360, 640, 3, shot_level('en', 9, '')),
]

def render(name, code, w, h, dpr=1, budget=1600):
    src = open(BUILD, encoding='utf-8').read()
    assert HOOK in src
    html = src.replace(HOOK, code + "\n  requestAnimationFrame(frame);")
    p = os.path.join(TMP, name + '.html'); png = os.path.join(TMP, name + '.png')
    open(p, 'w', encoding='utf-8').write(html)
    subprocess.run(['flatpak', 'run', 'com.google.Chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    f'--window-size={w},{h}', f'--force-device-scale-factor={dpr}', f'--virtual-time-budget={budget}',
                    f'--screenshot={png}', 'file://' + p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    shutil.move(png, os.path.join(OUT, name + '.png'))
    print('  ', name + '.png', f'{int(w*dpr)}x{int(h*dpr)}')

if __name__ == '__main__':
    shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
    shutil.copytree(os.path.join(ROOT, 'yandex', 'build', 'fonts'), os.path.join(TMP, 'fonts'))
    os.makedirs(OUT, exist_ok=True)
    render('icon-512', ICON, *ICON_SIZE)
    render('cover-ru-800x470', cover('ru'), *COVER_SIZE)
    render('cover-en-800x470', cover('en'), *COVER_SIZE)
    for name, w, h, dpr, code in SHOTS: render('screenshot-' + name, code, w, h, dpr)
    shutil.rmtree(TMP, ignore_errors=True)
    print('Готово:', OUT)

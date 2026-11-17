"""Сборка архива для Яндекс Игр.

Берёт ../index.html (та же игра, что в артефакте), убирает Google Fonts,
кладёт шрифт рядом, добавляет полноценный HTML-каркас и SDK Яндекс Игр (/sdk.js),
и упаковывает всё в ../yandex/tushi-ogon.zip.

Запуск: python3 tools/build_yandex.py
"""
import os, re, shutil, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'yandex')
BUILD = os.path.join(OUT, 'build')
FONTS = os.path.join(OUT, 'fonts')
ZIP = os.path.join(OUT, 'tushi-ogon.zip')

src = open(SRC, encoding='utf-8').read()

# 1. шрифт — из архива, без внешних запросов
font_css = ('<style>@font-face{font-family:"Press Start 2P";'
            'src:url("fonts/PressStart2P-Regular.ttf") format("truetype");font-display:block}</style>')
src, n = re.subn(r'<!--FONTS-->.*?<!--/FONTS-->', font_css, src, flags=re.S)
assert n == 1, 'не найден блок шрифтов'

# 2. служебная метка артефакта не нужна
src = src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')

# 3. заголовок отдельно, остальное — в body
m = re.match(r'\s*(<title>.*?</title>)\s*', src, flags=re.S)
title = m.group(1); body = src[m.end():]
head_end = body.index('</style>') + len('</style>')
head, body = body[:head_end], body[head_end:]

html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
{title}
<script src="/sdk.js"></script>
{head}
</head>
<body>
{body.strip()}
</body>
</html>
"""
assert 'http://' not in html and 'https://' not in html, 'в сборке остались внешние ссылки'

shutil.rmtree(BUILD, ignore_errors=True)
os.makedirs(os.path.join(BUILD, 'fonts'))
open(os.path.join(BUILD, 'index.html'), 'w', encoding='utf-8').write(html)
for f in ('PressStart2P-Regular.ttf', 'OFL.txt'):
    shutil.copy(os.path.join(FONTS, f), os.path.join(BUILD, 'fonts', f))

if os.path.exists(ZIP): os.remove(ZIP)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for dp, _, files in os.walk(BUILD):
        for f in files:
            p = os.path.join(dp, f); arc = os.path.relpath(p, BUILD)
            assert re.fullmatch(r'[A-Za-z0-9._/-]+', arc), 'недопустимое имя файла: ' + arc
            z.write(p, arc)
print('Готово:', ZIP, os.path.getsize(ZIP) // 1024, 'КБ')
for n in zipfile.ZipFile(ZIP).namelist(): print('  ', n)

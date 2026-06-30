"""
Generate all product HTML pages from products.json
All paths are now ASCII-only.
"""
import sys, json, os, re
sys.stdout.reconfigure(encoding='utf-8')

with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

sub_labels = {
    'commercial': '商用系列',
    'gaming': '电竞系列',
    'design': '设计系列',
    'professional': '专业系列',
    'vr': 'VR设备',
    'sockets': '插座/转换器',
    'laptops': '笔记本电脑',
}

def make_product_page(p, category, sub_category, index_depth):
    all_imgs = [img.replace('\\', '/') for img in p.get('images', [])]
    detail_imgs = [img.replace('\\', '/') for img in p.get('detail_images', [])]
    thumb = all_imgs[0] if all_imgs else p.get('thumb', '')
    thumb = thumb.replace('\\', '/')

    sub_label = sub_labels.get(sub_category, sub_category) if sub_category else ''

    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = 'active' if i == 0 else ''
        thumbs_html += f'      <div class="product-thumb {active}"><img src="{img}" alt="{esc(p["name"])}"></div>\n'

    detail_html = ''
    for img in detail_imgs:
        detail_html += f'    <img src="{img}" alt="{esc(p["name"])}" loading="lazy">\n'

    nav_html = f'''
<nav class="nav">
  <div class="nav-inner">
    <a href="{index_depth}index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="{index_depth}index.html">首页</a></li>
      <li><a href="{index_depth}monitors/index.html">显示器</a></li>
      <li><a href="{index_depth}aios/index.html">一体机</a></li>
      <li><a href="{index_depth}others/index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle">&#9776;</button>
  </div>
</nav>'''

    body = f'''
<div class="product-detail">
  <div class="product-hero">
    <h1 class="product-hero-title">{esc(p["name"])}</h1>
    <p class="product-hero-tag">{esc(sub_label)}</p>
    <div class="product-hero-image">
      <img src="{thumb}" alt="{esc(p["name"])}">
    </div>
  </div>
'''

    if len(all_imgs) > 1:
        body += f'''
  <div class="product-gallery">
    <div class="product-gallery-main">
      <img src="{thumb}" alt="{esc(p["name"])}">
    </div>
    <div class="product-thumbnails">
{thumbs_html}    </div>
  </div>
'''

    if detail_imgs:
        body += f'''
  <div class="product-detail-images">
{detail_html}  </div>
'''

    body += '\n</div>\n'

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(p["name"])} - MAYA 玛雅</title>
  <link rel="stylesheet" href="{index_depth}css/style.css">
</head>
<body>
{nav_html}
{body}
<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>
<script src="{index_depth}js/app.js"></script>
</body>
</html>
'''

count = 0

# Generate Monitor Pages
for sub, prods in data.get('monitors', {}).items():
    dir_path = f'monitors/{sub}' if sub else 'monitors'
    os.makedirs(dir_path, exist_ok=True)
    for p in prods:
        slug = p.get('name', 'product')
        filename = f'{dir_path}/{slug}.html'
        depth = '../' if sub else ''
        html = make_product_page(p, 'monitors', sub, depth)
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1

# Generate AIO Pages
os.makedirs('aios', exist_ok=True)
for p in data.get('aios', []):
    slug = p.get('name', 'product')
    filename = f'aios/{slug}.html'
    html = make_product_page(p, 'aios', '', '../')
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(html)
    count += 1

# Generate Other Products Pages
for sub, prods in data.get('others', {}).items():
    dir_path = f'others/{sub}'
    os.makedirs(dir_path, exist_ok=True)
    for p in prods:
        slug = p.get('name', 'product')
        filename = f'{dir_path}/{slug}.html'
        html = make_product_page(p, 'others', sub, '../../')
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1

print(f'Generated {count} product pages')

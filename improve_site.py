"""
Apply 4 improvements:
1. Split sockets into 玛雅品牌/骐麟品牌 subdirectories
2. Uppercase all English text
3. Remove dark hero from product detail pages
4. (Homepage carousel done in HTML/CSS separately)
"""
import sys, json, os, re, shutil, urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ===== 1. Split sockets into brand subdirectories =====
print("=== 1. Splitting sockets into brand subdirs ===")

# Create brand subdirectories
os.makedirs('其他产品/插座类目/玛雅品牌', exist_ok=True)
os.makedirs('其他产品/插座类目/骐麟品牌', exist_ok=True)

# Move socket product pages by brand
sock_dir = '其他产品/插座类目'
moved = 0
for p in data['others']['sockets']:
    brand = p.get('brand', '').upper()
    if brand == 'KILIN':
        dst = f'{sock_dir}/骐麟品牌'
    else:
        dst = f'{sock_dir}/玛雅品牌'
    src_file = f'{sock_dir}/{p["name"]}.html'
    dst_file = f'{dst}/{p["name"]}.html'
    if os.path.exists(src_file):
        shutil.move(src_file, dst_file)
        moved += 1

print(f"  Moved {moved} socket pages into brand subdirs")

# Update socket page_urls in products.json
for p in data['others']['sockets']:
    brand = p.get('brand', '').upper()
    subdir = '骐麟品牌' if brand == 'KILIN' else '玛雅品牌'
    p['page_url'] = f'其他产品/插座类目/{subdir}/{p["name"]}.html'
    # Add brand subcategory
    p['sub_brand'] = subdir

# Remove leftover empty socket html files
for f in os.listdir(sock_dir):
    if f.endswith('.html'):
        os.remove(os.path.join(sock_dir, f))

# ===== 2. Fix socket product page paths (3 levels deep now: 其他产品/插座类目/品牌) =====
print("\n=== 2. Fixing socket page image paths (3 levels deep) ===")

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

for p in data['others']['sockets']:
    brand = p.get('brand', '').upper()
    subdir = '骐麟品牌' if brand == 'KILIN' else '玛雅品牌'
    slug = p['name']
    filename = f'其他产品/插座类目/{subdir}/{slug}.html'

    all_imgs_clean = [img.replace('\\','/') for img in p.get('images', [])]
    detail_imgs_clean = [img.replace('\\','/') for img in p.get('detail_images', [])]
    thumb_clean = all_imgs_clean[0] if all_imgs_clean else ''

    # 3 levels deep: 其他产品/插座类目/品牌/  -> ../../../
    all_imgs = ['../../../' + img for img in all_imgs_clean]
    detail_imgs = ['../../../' + img for img in detail_imgs_clean]
    thumb = all_imgs[0] if all_imgs else '../../../' + thumb_clean

    display_name = p.get('display_name', p['name'])

    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = 'active' if i == 0 else ''
        thumbs_html += f'      <div class="product-thumb {active}"><img src="{img}" alt="{esc(display_name)}"></div>\n'

    detail_html = ''
    for img in detail_imgs:
        detail_html += f'    <img src="{img}" alt="{esc(display_name)}" loading="lazy">\n'

    depth = '../../../'
    nav_html = f'''
<nav class="nav">
  <div class="nav-inner">
    <a href="{depth}index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="{depth}index.html">首页</a></li>
      <li><a href="{depth}%E7%8E%9B%E9%9B%85%E6%98%BE%E7%A4%BA%E5%99%A8/index.html">显示器</a></li>
      <li><a href="{depth}%E7%8E%9B%E9%9B%85%E4%B8%80%E4%BD%93%E6%9C%BA/index.html">一体机</a></li>
      <li><a href="../../index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle">&#9776;</button>
  </div>
</nav>'''

    # NO dark hero - start directly with breadcrumb + gallery
    desc_lines = p.get('description', [])
    desc_html = ''
    if desc_lines:
        desc_html = '<div class="product-desc"><div class="product-desc-title">产品介绍</div><ul>'
        for line in desc_lines:
            desc_html += f'<li>{esc(line)}</li>'
        desc_html += '</ul></div>'

    body = f'''
<div class="breadcrumb">
  <a href="{depth}index.html">首页</a> <span>›</span>
  <a href="../../index.html">其他产品</a> <span>›</span>
  <a href="../index.html">{esc(subdir)}</a> <span>›</span>
  {esc(display_name)}
</div>
<div class="product-detail">
  <div class="product-header">
    <h1 class="product-title">{esc(display_name)}</h1>
    <p class="product-brand">{esc(brand)}</p>
  </div>
  {desc_html}
'''
    if all_imgs:
        body += f'''
  <div class="product-gallery">
    <div class="product-gallery-main">
      <img src="{thumb}" alt="{esc(display_name)}">
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

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(display_name)} - MAYA 玛雅</title>
  <link rel="stylesheet" href="{depth}css/style.css">
</head>
<body>
{nav_html}
{body}
<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>
<script src="{depth}js/app.js"></script>
</body>
</html>
'''
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(html)

print(f"  Regenerated {len(data['others']['sockets'])} socket pages (no dark hero)")

# ===== 3. Regenerate monitor/aio/vr/laptop pages without dark hero =====
print("\n=== 3. Regenerating other product pages (no dark hero) ===")

MONITOR_CATEGORIES = {
    'commercial': '商用系列',
    'gaming': '电竞系列',
    'design': '设计系列',
    'professional': '专业系列',
}

OTHER_CATEGORIES = {
    'vr': 'VR类目',
    'laptops': '笔记本电脑类目',
}

def make_product_html_v2(p, category, sub_label, depth):
    all_imgs = [img.replace('\\', '/') for img in p.get('images', [])]
    detail_imgs = [img.replace('\\', '/') for img in p.get('detail_images', [])]
    thumb = all_imgs[0] if all_imgs else p.get('thumb', '')
    thumb = thumb.replace('\\', '/')
    display_name = p.get('display_name', p['name'])

    all_imgs = [depth + img for img in all_imgs]
    detail_imgs = [depth + img for img in detail_imgs]
    thumb = depth + thumb

    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = 'active' if i == 0 else ''
        thumbs_html += f'      <div class="product-thumb {active}"><img src="{img}" alt="{esc(display_name)}"></div>\n'

    detail_html = ''
    for img in detail_imgs:
        detail_html += f'    <img src="{img}" alt="{esc(display_name)}" loading="lazy">\n'

    enc_mon = urllib.parse.quote('玛雅显示器')
    enc_aio = urllib.parse.quote('玛雅一体机')

    nav_html = f'''
<nav class="nav">
  <div class="nav-inner">
    <a href="{depth}index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="{depth}index.html">首页</a></li>
      <li><a href="{depth}{enc_mon}/index.html">显示器</a></li>
      <li><a href="{depth}{enc_aio}/index.html">一体机</a></li>
      <li><a href="{depth}%E5%85%B6%E4%BB%96%E4%BA%A7%E5%93%81/index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle">&#9776;</button>
  </div>
</nav>'''

    # Determine breadcrumb parent
    if category == 'monitors':
        crumb = f'<a href="{depth}{enc_mon}/index.html">显示器</a> <span>›</span> <a href="../index.html">{esc(sub_label)}</a> <span>›</span> {esc(display_name)}'
    elif category == 'aios':
        crumb = f'<a href="{depth}{enc_aio}/index.html">一体机</a> <span>›</span> {esc(display_name)}'
    else:
        crumb = f'<a href="{depth}%E5%85%B6%E4%BB%96%E4%BA%A7%E5%93%81/index.html">其他产品</a> <span>›</span> <a href="../index.html">{esc(sub_label)}</a> <span>›</span> {esc(display_name)}'

    # Build description HTML
    desc_lines = p.get('description', [])
    desc_html = ''
    if desc_lines:
        desc_html = '<div class="product-desc"><div class="product-desc-title">产品介绍</div><ul>'
        for line in desc_lines:
            desc_html += f'<li>{esc(line)}</li>'
        desc_html += '</ul></div>'

    body = f'''
<div class="breadcrumb">
  <a href="{depth}index.html">首页</a> <span>›</span> {crumb}
</div>
<div class="product-detail">
  <div class="product-header">
    <h1 class="product-title">{esc(display_name)}</h1>
    <p class="product-brand">{esc(sub_label)}</p>
  </div>
  {desc_html}
'''
    if all_imgs:
        body += f'''
  <div class="product-gallery">
    <div class="product-gallery-main">
      <img src="{thumb}" alt="{esc(display_name)}">
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
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(display_name)} - MAYA 玛雅</title>
  <link rel="stylesheet" href="{depth}css/style.css">
</head>
<body>
{nav_html}
{body}
<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>
<script src="{depth}js/app.js"></script>
</body>
</html>
'''

# Monitors
count = 0
for sub_en, sub_cn in MONITOR_CATEGORIES.items():
    dir_path = f'玛雅显示器/{sub_cn}'
    for p in data['monitors'][sub_en]:
        slug = p['name']
        html = make_product_html_v2(p, 'monitors', sub_cn, '../../')
        with open(f'{dir_path}/{slug}.html', 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1

# AIOs
for p in data['aios']:
    slug = p['name']
    html = make_product_html_v2(p, 'aios', '一体机', '../')
    with open(f'玛雅一体机/{slug}.html', 'w', encoding='utf-8') as out:
        out.write(html)
    count += 1

# VR + Laptops
for sub_en, sub_cn in OTHER_CATEGORIES.items():
    dir_path = f'其他产品/{sub_cn}'
    for p in data['others'][sub_en]:
        slug = p['name']
        html = make_product_html_v2(p, 'others', sub_cn, '../../')
        with open(f'{dir_path}/{slug}.html', 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1

print(f"  Regenerated {count} monitor/aio/vr/laptop pages (no dark hero)")

# ===== Save products.json =====
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nAll 4 improvements applied to product pages!")
print("\nSocket structure:")
print("  其他产品/插座类目/玛雅品牌/  (MAYA sockets)")
print("  其他产品/插座类目/骐麟品牌/  (KILIN sockets)")

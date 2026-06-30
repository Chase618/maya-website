"""
Rebuild products.json properly:
1. Fix sockets - scan actual products (4 levels deep)
2. Fix product URL slugs - store the correct URL for each product
3. Fix display names for kilin/maya brands
"""
import sys, json, os, re, glob

sys.stdout.reconfigure(encoding='utf-8')

with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ===== Fix sockets: rebuild with actual products =====
print("Rebuilding sockets products...")

sockets_products = []
sockets_base = 'images/others/sockets'

# Scan all product directories (4 levels deep: sockets/brand/category/product/)
for brand in sorted(os.listdir(sockets_base)):
    brand_path = os.path.join(sockets_base, brand)
    if not os.path.isdir(brand_path):
        continue
    brand_display = brand.upper()  # KILIN or MAYA
    for category in sorted(os.listdir(brand_path)):
        cat_path = os.path.join(brand_path, category)
        if not os.path.isdir(cat_path):
            continue
        for product in sorted(os.listdir(cat_path)):
            prod_path = os.path.join(cat_path, product)
            if not os.path.isdir(prod_path):
                continue
            # Find images
            imgs = []
            detail_imgs = []
            for f in sorted(os.listdir(prod_path)):
                fp = os.path.join(prod_path, f)
                if os.path.isfile(fp) and f.lower().endswith('.jpg'):
                    if 'detail' in f.lower():
                        detail_imgs.append(fp)
                    else:
                        imgs.append(fp)
            # Check for detail subdirectory
            for dd in sorted(os.listdir(prod_path)):
                ddp = os.path.join(prod_path, dd)
                if os.path.isdir(ddp) and 'detail' in dd.lower():
                    for f in sorted(os.listdir(ddp)):
                        fp = os.path.join(ddp, f)
                        if os.path.isfile(fp) and f.lower().endswith('.jpg'):
                            detail_imgs.append(fp)

            # Normalize paths
            imgs = [p.replace('\\', '/') for p in imgs]
            detail_imgs = [p.replace('\\', '/') for p in detail_imgs]
            thumb = imgs[0] if imgs else ''

            # Build display name from product dir
            display_name = product.replace('-', ' ').title()

            sockets_products.append({
                'name': product,
                'dir': product,
                'display_name': display_name,
                'brand': brand_display,
                'images': imgs,
                'detail_images': detail_imgs,
                'thumb': thumb,
            })

print(f"  Found {len(sockets_products)} socket products")
for p in sockets_products[:5]:
    print(f"    {p['brand']}: {p['display_name']} ({len(p['images'])} images)")

data['others']['sockets'] = sockets_products

# ===== Fix product URLs: store the correct HTML filename =====
# The HTML files use the directory name as the filename slug.
# We need to store the correct URL in products.json.

def set_product_url(p, category, sub):
    """Store the correct product detail page URL"""
    # The HTML file is at: {category}/{sub}/{name}.html
    # where name = p['name'] (the directory slug)
    p['page_url'] = f"{category}/{sub}/{p['name']}.html" if sub else f"{category}/{p['name']}.html"

for sub, prods in data.get('monitors', {}).items():
    for p in prods:
        set_product_url(p, 'monitors', sub)

for p in data.get('aios', []):
    set_product_url(p, 'aios', '')

for sub, prods in data.get('others', {}).items():
    for p in prods:
        if sub == 'sockets':
            # Socket products are at others/sockets/{name}.html
            p['page_url'] = f"others/sockets/{p['name']}.html"
        else:
            set_product_url(p, f'others/{sub}', '')

# ===== Generate socket product HTML pages =====
print("\nGenerating socket product pages...")
os.makedirs('others/sockets', exist_ok=True)

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

for p in sockets_products:
    slug = p['name']
    filename = f'others/sockets/{slug}.html'
    all_imgs = p.get('images', [])
    detail_imgs = p.get('detail_images', [])
    thumb = all_imgs[0] if all_imgs else ''

    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = 'active' if i == 0 else ''
        thumbs_html += f'      <div class="product-thumb {active}"><img src="{img}" alt="{esc(p["display_name"])}"></div>\n'

    detail_html = ''
    for img in detail_imgs:
        detail_html += f'    <img src="{img}" alt="{esc(p["display_name"])}" loading="lazy">\n'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(p["display_name"])} - MAYA 玛雅</title>
  <link rel="stylesheet" href="../../css/style.css">
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a href="../../index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="../../index.html">首页</a></li>
      <li><a href="../../monitors/index.html">显示器</a></li>
      <li><a href="../../aios/index.html">一体机</a></li>
      <li><a href="../index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle">&#9776;</button>
  </div>
</nav>
<div class="product-detail">
  <div class="product-hero">
    <h1 class="product-hero-title">{esc(p["display_name"])}</h1>
    <p class="product-hero-tag">{esc(p["brand"])}</p>
    <div class="product-hero-image">
      <img src="{thumb}" alt="{esc(p["display_name"])}">
    </div>
  </div>
'''
    if len(all_imgs) > 1:
        html += f'''
  <div class="product-gallery">
    <div class="product-gallery-main">
      <img src="{thumb}" alt="{esc(p["display_name"])}">
    </div>
    <div class="product-thumbnails">
{thumbs_html}    </div>
  </div>
'''
    if detail_imgs:
        html += f'''
  <div class="product-detail-images">
{detail_html}  </div>
'''
    html += f'''
</div>
<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>
<script src="../../js/app.js"></script>
</body>
</html>
'''
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(html)

print(f"  Generated {len(sockets_products)} socket product pages")

# ===== Save fixed products.json =====
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nDone! Summary:")
print(f"  Monitors: {sum(len(v) for v in data['monitors'].values())}")
print(f"  AIOs: {len(data['aios'])}")
print(f"  VR: {len(data['others']['vr'])}")
print(f"  Sockets: {len(data['others']['sockets'])}")
print(f"  Laptops: {len(data['others']['laptops'])}")
print(f"  Total: {sum(len(v) for v in data['monitors'].values()) + len(data['aios']) + sum(len(v) for v in data['others'].values())}")

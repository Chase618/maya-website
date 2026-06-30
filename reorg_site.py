"""
Reorganize the entire website to match the original folder structure:

www.maya.com.cn/
├── index.html
├── css/style.css
├── js/app.js
├── products.json
├── 玛雅显示器/
│   ├── index.html          (category listing with tabs)
│   ├── 商用系列/
│   │   ├── air-20.html
│   │   └── ...
│   ├── 电竞系列/
│   ├── 设计系列/
│   └── 专业系列/
├── 玛雅一体机/
│   ├── index.html
│   ├── maya-baijing-gs22.html
│   └── ...
├── 其他产品/
│   ├── index.html
│   ├── VR类目/
│   │   ├── maya-vr.html
│   │   └── ...
│   ├── 插座类目/
│   │   ├── f8-a.html
│   │   └── ...
│   └── 笔记本电脑类目/
│       └── ...
└── images/
    ├── 玛雅显示器/
    ├── 玛雅一体机/
    └── 其他产品/
"""
import sys, json, os, re, shutil

sys.stdout.reconfigure(encoding='utf-8')

# Load products data
with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ===== Directory mapping =====
# We keep Chinese directory names for the site structure
# Product slugs use English for URL compatibility

MONITOR_CATEGORIES = {
    'commercial': '商用系列',
    'gaming': '电竞系列',
    'design': '设计系列',
    'professional': '专业系列',
}

OTHER_CATEGORIES = {
    'vr': 'VR类目',
    'sockets': '插座类目',
    'laptops': '笔记本电脑类目',
}

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def make_product_html(p, category, sub_category, css_depth, sub_label):
    """Generate a product detail page"""
    all_imgs = [img.replace('\\', '/') for img in p.get('images', [])]
    detail_imgs = [img.replace('\\', '/') for img in p.get('detail_images', [])]
    thumb = all_imgs[0] if all_imgs else p.get('thumb', '')
    thumb = thumb.replace('\\', '/')
    display_name = p.get('display_name', p['name'])

    # Image paths relative to product page depth
    all_imgs = [css_depth + img for img in all_imgs]
    detail_imgs = [css_depth + img for img in detail_imgs]
    thumb = css_depth + thumb

    thumbs_html = ''
    for i, img in enumerate(all_imgs):
        active = 'active' if i == 0 else ''
        thumbs_html += f'      <div class="product-thumb {active}"><img src="{img}" alt="{esc(display_name)}"></div>\n'

    detail_html = ''
    for img in detail_imgs:
        detail_html += f'    <img src="{img}" alt="{esc(display_name)}" loading="lazy">\n'

    # Nav links
    nav_html = f'''
<nav class="nav">
  <div class="nav-inner">
    <a href="{css_depth}index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="{css_depth}index.html">首页</a></li>
      <li><a href="{css_depth}玛雅显示器/index.html">显示器</a></li>
      <li><a href="{css_depth}玛雅一体机/index.html">一体机</a></li>
      <li><a href="{css_depth}其他产品/index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle">&#9776;</button>
  </div>
</nav>'''

    body = f'''
<div class="product-detail">
  <div class="product-hero">
    <h1 class="product-hero-title">{esc(display_name)}</h1>
    <p class="product-hero-tag">{esc(sub_label)}</p>
    <div class="product-hero-image">
      <img src="{thumb}" alt="{esc(display_name)}">
    </div>
  </div>
'''

    if len(all_imgs) > 1:
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
  <link rel="stylesheet" href="{css_depth}css/style.css">
</head>
<body>
{nav_html}
{body}
<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>
<script src="{css_depth}js/app.js"></script>
</body>
</html>
'''

# ===== Step 1: Remove old directory structure =====
print("Step 1: Cleaning old structure...")
old_dirs = ['monitors', 'aios', 'others']
for d in old_dirs:
    if os.path.isdir(d):
        shutil.rmtree(d)
        print(f"  Removed {d}/")

# ===== Step 2: Reorganize images =====
print("\nStep 2: Reorganizing images...")

# Create new image directories
os.makedirs('images/玛雅显示器', exist_ok=True)
os.makedirs('images/玛雅一体机', exist_ok=True)
os.makedirs('images/其他产品', exist_ok=True)

# Move monitor images: images/monitors/{sub} -> images/玛雅显示器/{sub_chinese}
for sub_en, sub_cn in MONITOR_CATEGORIES.items():
    src = f'images/monitors/{sub_en}'
    dst = f'images/玛雅显示器/{sub_cn}'
    if os.path.isdir(src):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.move(src, dst)
        print(f"  {src} -> {dst}")

# Move AIO images: images/aios/* -> images/玛雅一体机/
for item in os.listdir('images/aios'):
    src = f'images/aios/{item}'
    dst = f'images/玛雅一体机/{item}'
    if os.path.isdir(src):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.move(src, dst)
        print(f"  {src} -> {dst}")

# Move other product images
for sub_en, sub_cn in OTHER_CATEGORIES.items():
    src = f'images/others/{sub_en}'
    dst = f'images/其他产品/{sub_cn}'
    if os.path.isdir(src):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.move(src, dst)
        print(f"  {src} -> {dst}")

# Clean up old image dirs
for d in ['monitors', 'aios', 'others']:
    img_dir = f'images/{d}'
    if os.path.isdir(img_dir):
        shutil.rmtree(img_dir)

# ===== Step 3: Update products.json paths =====
print("\nStep 3: Updating products.json paths...")

def update_image_path(path):
    """Convert old paths to new structure"""
    path = path.replace('\\', '/')

    # Monitors
    for sub_en, sub_cn in MONITOR_CATEGORIES.items():
        old = f'images/monitors/{sub_en}/'
        new = f'images/玛雅显示器/{sub_cn}/'
        path = path.replace(old, new)

    # AIOs
    path = path.replace('images/aios/', 'images/玛雅一体机/')

    # Others
    for sub_en, sub_cn in OTHER_CATEGORIES.items():
        old = f'images/others/{sub_en}/'
        new = f'images/其他产品/{sub_cn}/'
        path = path.replace(old, new)

    return path

def update_obj(obj):
    if isinstance(obj, str):
        return update_image_path(obj)
    elif isinstance(obj, list):
        return [update_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: update_obj(v) for k, v in obj.items()}
    return obj

data = update_obj(data)

# ===== Step 4: Generate product pages =====
print("\nStep 4: Generating product pages...")

# Create category index pages with proper structure
# Monitor index page
monitor_index = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>玛雅显示器 - MAYA 官方网站</title>
  <meta name="description" content="浏览MAYA玛雅全系列显示器产品，涵盖商用、电竞、设计、专业四大系列。">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="../index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="../index.html">首页</a></li>
      <li><a href="index.html" style="color:#fff;">显示器</a></li>
      <li><a href="../玛雅一体机/index.html">一体机</a></li>
      <li><a href="../其他产品/index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle" aria-label="菜单">&#9776;</button>
  </div>
</nav>

<div class="page-hero">
  <h1 class="page-hero-title">玛雅显示器</h1>
  <p class="page-hero-desc">商用 · 电竞 · 设计 · 专业四大系列，满足不同场景需求</p>
</div>

<div class="breadcrumb">
  <a href="../index.html">首页</a> <span>›</span> 显示器
</div>

<div class="sub-tabs" id="subTabs">
  <button class="sub-tab active" data-tab="all">全部</button>
  <button class="sub-tab" data-tab="商用系列">商用系列</button>
  <button class="sub-tab" data-tab="电竞系列">电竞系列</button>
  <button class="sub-tab" data-tab="设计系列">设计系列</button>
  <button class="sub-tab" data-tab="专业系列">专业系列</button>
</div>

<div class="product-grid" id="productGrid"></div>

<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>

<script src="../js/app.js"></script>
<script>
(async function() {
  try {
    const data = await loadProducts();
    const grid = document.getElementById('productGrid');
    const tabs = document.getElementById('subTabs');
    const monitors = data.monitors || {};

    function getProducts(filter) {
      let all = [];
      const subMap = {
        '商用系列': 'commercial',
        '电竞系列': 'gaming',
        '设计系列': 'design',
        '专业系列': 'professional'
      };
      for (const [sub, prods] of Object.entries(monitors)) {
        const cnName = {'commercial':'商用系列','gaming':'电竞系列','design':'设计系列','professional':'专业系列'}[sub];
        if (filter === 'all' || filter === cnName) {
          all = all.concat(prods.map(p => ({...p, category: 'monitors', subCategory: cnName})));
        }
      }
      return all;
    }

    function render(filter) {
      renderProductGrid(grid, getProducts(filter));
    }

    render('all');

    tabs.addEventListener('click', (e) => {
      if (!e.target.classList.contains('sub-tab')) return;
      tabs.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      render(e.target.dataset.tab);
    });
  } catch (err) {
    console.error('Failed to load products:', err);
    document.getElementById('productGrid').innerHTML = '<p style="padding:40px;text-align:center;color:red;">加载失败: ' + err.message + '</p>';
  }
})();
</script>
</body>
</html>
'''

# AIO index page
aio_index = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>玛雅一体机 - MAYA 官方网站</title>
  <meta name="description" content="浏览MAYA玛雅全系列一体机产品，简约设计，高效性能。">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="../index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="../index.html">首页</a></li>
      <li><a href="../玛雅显示器/index.html">显示器</a></li>
      <li><a href="index.html" style="color:#fff;">一体机</a></li>
      <li><a href="../其他产品/index.html">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle" aria-label="菜单">&#9776;</button>
  </div>
</nav>

<div class="page-hero">
  <h1 class="page-hero-title">玛雅一体机</h1>
  <p class="page-hero-desc">简约设计，高效性能，一体化办公新体验</p>
</div>

<div class="breadcrumb">
  <a href="../index.html">首页</a> <span>›</span> 一体机
</div>

<div class="product-grid" id="productGrid"></div>

<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>

<script src="../js/app.js"></script>
<script>
(async function() {
  try {
    const data = await loadProducts();
    const grid = document.getElementById('productGrid');
    const aios = (data.aios || []).map(p => ({...p, category: 'aios', subCategory: ''}));
    renderProductGrid(grid, aios);
  } catch (err) {
    console.error('Failed to load AIO products:', err);
    document.getElementById('productGrid').innerHTML = '<p style="padding:40px;text-align:center;color:red;">加载失败: ' + err.message + '</p>';
  }
})();
</script>
</body>
</html>
'''

# Others index page
others_index = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>其他产品 - MAYA 官方网站</title>
  <meta name="description" content="浏览MAYA玛雅VR设备、插座转换器、笔记本电脑等更多产品。">
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="../index.html" class="nav-logo">MAYA</a>
    <ul class="nav-links">
      <li><a href="../index.html">首页</a></li>
      <li><a href="../玛雅显示器/index.html">显示器</a></li>
      <li><a href="../玛雅一体机/index.html">一体机</a></li>
      <li><a href="index.html" style="color:#fff;">其他产品</a></li>
    </ul>
    <button class="nav-mobile-toggle" aria-label="菜单">&#9776;</button>
  </div>
</nav>

<div class="page-hero">
  <h1 class="page-hero-title">其他产品</h1>
  <p class="page-hero-desc">VR设备 · 插座转换器 · 笔记本电脑，更多精彩等你发现</p>
</div>

<div class="breadcrumb">
  <a href="../index.html">首页</a> <span>›</span> 其他产品
</div>

<div class="sub-tabs" id="subTabs">
  <button class="sub-tab active" data-tab="all">全部</button>
  <button class="sub-tab" data-tab="VR类目">VR设备</button>
  <button class="sub-tab" data-tab="插座类目">插座/转换器</button>
  <button class="sub-tab" data-tab="笔记本电脑类目">笔记本电脑</button>
</div>

<div class="product-grid" id="productGrid"></div>

<footer class="footer">
  <div class="footer-inner">
    <p>&copy; 2026 MAYA 玛雅. All rights reserved.</p>
  </div>
</footer>

<script src="../js/app.js"></script>
<script>
(async function() {
  try {
    const data = await loadProducts();
    const grid = document.getElementById('productGrid');
    const tabs = document.getElementById('subTabs');
    const others = data.others || {};

    const subMap = {
      'VR类目': 'vr',
      '插座类目': 'sockets',
      '笔记本电脑类目': 'laptops'
    };

    function getProducts(filter) {
      let all = [];
      for (const [sub, prods] of Object.entries(others)) {
        const cnName = {'vr':'VR类目','sockets':'插座类目','laptops':'笔记本电脑类目'}[sub];
        if (filter === 'all' || filter === cnName) {
          all = all.concat(prods.map(p => ({...p, category: 'others', subCategory: cnName})));
        }
      }
      return all;
    }

    function render(filter) {
      renderProductGrid(grid, getProducts(filter));
    }

    render('all');

    tabs.addEventListener('click', (e) => {
      if (!e.target.classList.contains('sub-tab')) return;
      tabs.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      render(e.target.dataset.tab);
    });
  } catch (err) {
    console.error('Failed to load products:', err);
    document.getElementById('productGrid').innerHTML = '<p style="padding:40px;text-align:center;color:red;">加载失败: ' + err.message + '</p>';
  }
})();
</script>
</body>
</html>
'''

count = 0

# === Monitor product pages ===
for sub_en, sub_cn in MONITOR_CATEGORIES.items():
    dir_path = f'玛雅显示器/{sub_cn}'
    os.makedirs(dir_path, exist_ok=True)
    prods = data.get('monitors', {}).get(sub_en, [])
    for p in prods:
        slug = p.get('name', 'product')
        filename = f'{dir_path}/{slug}.html'
        html = make_product_html(p, 'monitors', sub_cn, '../../', sub_cn)
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1
        # Update page_url
        p['page_url'] = f'玛雅显示器/{sub_cn}/{slug}.html'

# Write monitor index
with open('玛雅显示器/index.html', 'w', encoding='utf-8') as f:
    f.write(monitor_index)

# === AIO product pages ===
os.makedirs('玛雅一体机', exist_ok=True)
for p in data.get('aios', []):
    slug = p.get('name', 'product')
    filename = f'玛雅一体机/{slug}.html'
    html = make_product_html(p, 'aios', '', '../', '一体机')
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(html)
    count += 1
    p['page_url'] = f'玛雅一体机/{slug}.html'

with open('玛雅一体机/index.html', 'w', encoding='utf-8') as f:
    f.write(aio_index)

# === Other product pages ===
for sub_en, sub_cn in OTHER_CATEGORIES.items():
    dir_path = f'其他产品/{sub_cn}'
    os.makedirs(dir_path, exist_ok=True)
    prods = data.get('others', {}).get(sub_en, [])
    for p in prods:
        slug = p.get('name', 'product')
        filename = f'{dir_path}/{slug}.html'
        html = make_product_html(p, 'others', sub_cn, '../../', sub_cn)
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(html)
        count += 1
        p['page_url'] = f'其他产品/{sub_cn}/{slug}.html'

with open('其他产品/index.html', 'w', encoding='utf-8') as f:
    f.write(others_index)

# === Update homepage nav links ===
with open('index.html', 'r', encoding='utf-8') as f:
    homepage = f.read()

homepage = homepage.replace('monitors/index.html', '玛雅显示器/index.html')
homepage = homepage.replace('aios/index.html', '玛雅一体机/index.html')
homepage = homepage.replace('others/index.html', '其他产品/index.html')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(homepage)

# Save updated products.json
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nGenerated {count} product pages")
print("\nNew directory structure:")
for root, dirs, files in os.walk('.'):
    # Skip images and .git
    if '.git' in root or 'node_modules' in root:
        continue
    if root == './images' or root.startswith('./images/'):
        continue
    level = root.count(os.sep)
    indent = '  ' * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = '  ' * (level + 1)
    for file in sorted(files):
        if file.endswith('.html'):
            print(f'{subindent}{file}')

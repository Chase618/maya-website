"""
Rename all directories and files under images/ to ASCII-only names.
Then update products.json paths to match.
"""
import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

# Full directory name mapping (including intermediate dirs)
DIR_RENAMES = {
    # Monitor top-level subdirs
    '商用系列': 'commercial',
    '电竞系列': 'gaming',
    '设计系列': 'design',
    '专业系列': 'professional',
    # Others top-level
    'VR类目': 'vr',
    '插座类目': 'sockets',
    '笔记本电脑类目': 'laptops',
    # AIO product dirs
    'KILIN 骐麟 GS24pro': 'kilin-gs24pro',
    'KILIN 骐麟 XPS24M': 'kilin-xps24m',
    'MAYA 白鲸 GS22': 'maya-white-whale-gs22',
    'MAYA 白鲸 GS24': 'maya-white-whale-gs24',
    'MAYA 银龙 GS22': 'maya-silver-dragon-gs22',
    'MAYA 银龙 GS24': 'maya-silver-dragon-gs24',
    # VR subdirs
    '头盔手柄': 'vr-controller',
    '武器大师(VR支架)': 'weapon-master-vr-stand',
    '玛雅VR头盔': 'maya-vr-headset',
    # Socket subdirs
    'maya品牌': 'maya',
    '骐麟品牌': 'kilin',
    '玛雅出国转换': 'maya-travel-adapter',
    '玛雅大功率转换': 'maya-high-power',
    '玛雅居家一转多': 'maya-home-multi-plug',
    '玛雅接线板': 'maya-power-strip',
    '大功率系列': 'high-power-series',
    '家用办公系列': 'home-office-series',
    # Laptop subdirs
    'KILIN 骐麟 FZ-YH5722': 'kilin-fz-yh5722',
    'KILIN 骐麟 FZ-YH5731': 'kilin-fz-yh5731',
    # Detail page dirs
    '详情页': 'detail',
}

def has_chinese(name):
    return any(ord(c) > 127 for c in name)

def ascii_name(name):
    """Convert name to ASCII-safe"""
    if name in DIR_RENAMES:
        return DIR_RENAMES[name]
    # Remove all non-ASCII, slugify
    s = ''.join(c for c in name.lower() if ord(c) < 128)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    if not s:
        s = 'item'
    return s

def rename_files_in_dir(dirpath):
    """Rename all .jpg files in a directory to ASCII names"""
    for fname in os.listdir(dirpath):
        old_path = os.path.join(dirpath, fname)
        if not os.path.isfile(old_path):
            continue
        if has_chinese(fname) or ' ' in fname:
            name_part, ext = os.path.splitext(fname)
            new_name = ascii_name(name_part) + ext.lower()
            # Avoid collisions
            new_path = os.path.join(dirpath, new_name)
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{ascii_name(name_part)}-{counter}{ext.lower()}"
                new_path = os.path.join(dirpath, new_name)
                counter += 1
            try:
                os.rename(old_path, new_path)
                print(f"  file: {fname} -> {new_name}")
            except Exception as e:
                print(f"  ERROR renaming file {fname}: {e}")

def rename_dirs_recursive(base):
    """Rename directories breadth-first to avoid path issues"""
    # First pass: collect all directories at each level
    changed = True
    while changed:
        changed = False
        for item in sorted(os.listdir(base)):
            full = os.path.join(base, item)
            if not os.path.isdir(full):
                continue
            if has_chinese(item) or ' ' in item or '(' in item:
                new_name = ascii_name(item)
                new_path = os.path.join(base, new_name)
                if new_path != full:
                    # Avoid collision
                    counter = 1
                    while os.path.exists(new_path):
                        new_name = f"{ascii_name(item)}-{counter}"
                        new_path = os.path.join(base, new_name)
                        counter += 1
                    try:
                        os.rename(full, new_path)
                        print(f"  dir: {item} -> {new_name}")
                        changed = True
                    except Exception as e:
                        print(f"  ERROR renaming dir {item}: {e}")
            # Recurse into subdirectories
            actual_path = os.path.join(base, ascii_name(item) if (has_chinese(item) or ' ' in item or '(' in item) else item)
            if os.path.isdir(actual_path):
                rename_dirs_recursive(actual_path)
            # Rename files in this directory
            rename_files_in_dir(actual_path if os.path.isdir(actual_path) else full)

print("Step 1: Renaming directories and files under images/...")
base = 'images'

# Process each top-level category
for category in ['monitors', 'aios', 'others']:
    cat_path = os.path.join(base, category)
    if os.path.isdir(cat_path):
        print(f"\n  Processing images/{category}/...")
        rename_dirs_recursive(cat_path)

print("\nStep 2: Building path mapping from disk...")

# Now scan the actual disk to build the old->new path mapping
# We need to know what the original products.json paths were and map them to new paths
import json

with open('_path_map.json', 'r', encoding='utf-8') as f:
    path_map = json.load(f)

# Build disk mapping: scan new directory structure and figure out which product each dir belongs to
# Actually, let's just rebuild products.json from the new directory structure

print("\nStep 3: Rebuilding products.json from new directory structure...")

products = {'monitors': {}, 'aios': [], 'others': {}}

# Monitors
for sub in ['commercial', 'gaming', 'design', 'professional']:
    sub_path = os.path.join(base, 'monitors', sub)
    if not os.path.isdir(sub_path):
        continue
    products['monitors'][sub] = []
    for d in sorted(os.listdir(sub_path)):
        dp = os.path.join(sub_path, d)
        if not os.path.isdir(dp):
            continue
        imgs = []
        detail_imgs = []
        for f in sorted(os.listdir(dp)):
            fp = os.path.join(dp, f)
            if not os.path.isfile(fp) or not f.lower().endswith('.jpg'):
                continue
            if 'detail' in f.lower():
                detail_imgs.append(fp)
            else:
                imgs.append(fp)
        for dd in sorted(os.listdir(dp)):
            ddp = os.path.join(dp, dd)
            if os.path.isdir(ddp) and 'detail' in dd.lower():
                for f in sorted(os.listdir(ddp)):
                    fp = os.path.join(ddp, f)
                    if os.path.isfile(fp) and f.lower().endswith('.jpg'):
                        detail_imgs.append(fp)
        products['monitors'][sub].append({
            'name': d,
            'dir': d,
            'images': imgs,
            'detail_images': detail_imgs,
            'thumb': imgs[0] if imgs else ''
        })

# AIOs
aio_path = os.path.join(base, 'aios')
for d in sorted(os.listdir(aio_path)):
    dp = os.path.join(aio_path, d)
    if not os.path.isdir(dp):
        continue
    imgs = []
    detail_imgs = []
    for f in sorted(os.listdir(dp)):
        fp = os.path.join(dp, f)
        if not os.path.isfile(fp) or not f.lower().endswith('.jpg'):
            continue
        if 'detail' in f.lower():
            detail_imgs.append(fp)
        else:
            imgs.append(fp)
    for dd in sorted(os.listdir(dp)):
        ddp = os.path.join(dp, dd)
        if os.path.isdir(ddp) and 'detail' in dd.lower():
            for f in sorted(os.listdir(ddp)):
                fp = os.path.join(ddp, f)
                if os.path.isfile(fp) and f.lower().endswith('.jpg'):
                    detail_imgs.append(fp)
    products['aios'].append({
        'name': d,
        'dir': d,
        'images': imgs,
        'detail_images': detail_imgs,
        'thumb': imgs[0] if imgs else ''
    })

# Others
for sub in ['vr', 'sockets', 'laptops']:
    sp = os.path.join(base, 'others', sub)
    if not os.path.isdir(sp):
        continue
    products['others'][sub] = []
    for d in sorted(os.listdir(sp)):
        dp = os.path.join(sp, d)
        if not os.path.isdir(dp):
            continue
        imgs = []
        detail_imgs = []
        for f in sorted(os.listdir(dp)):
            fp = os.path.join(dp, f)
            if not os.path.isfile(fp) or not f.lower().endswith('.jpg'):
                continue
            imgs.append(fp)
        for dd in sorted(os.listdir(dp)):
            ddp = os.path.join(dp, dd)
            if os.path.isdir(ddp):
                for f in sorted(os.listdir(ddp)):
                    fp = os.path.join(ddp, f)
                    if os.path.isfile(fp) and f.lower().endswith('.jpg'):
                        detail_imgs.append(fp)
        products['others'][sub].append({
            'name': d,
            'dir': d,
            'images': imgs,
            'detail_images': detail_imgs,
            'thumb': imgs[0] if imgs else ''
        })

with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Rebuilt products.json from new directory structure")

# Count
total = sum(len(v) for v in products['monitors'].values()) + len(products['aios']) + sum(len(v) for v in products['others'].values())
print(f"Total products: {total}")

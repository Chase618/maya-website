"""
Rename all image directories and files to ASCII-safe paths,
update products.json, and output a rename mapping.
"""
import sys, json, os, re, shutil

sys.stdout.reconfigure(encoding='utf-8')

# Load existing products data
with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Chinese -> ASCII mapping for category/subcategory dirs
DIR_MAP = {
    # Monitor subcategories
    '商用系列': 'commercial',
    '电竞系列': 'gaming',
    '设计系列': 'design',
    '专业系列': 'professional',
    # Others categories
    'VR类目': 'vr',
    '插座类目': 'sockets',
    '笔记本电脑类目': 'laptops',
    # AIO dirs (brand names)
    'KILIN 骐麟 GS24pro': 'kilin-gs24pro',
    'KILIN 骐麟 XPS24M': 'kilin-xps24m',
    'MAYA 白鲸 GS22': 'maya-white-whale-gs22',
    'MAYA 白鲸 GS24': 'maya-white-whale-gs24',
    'MAYA 银龙 GS22': 'maya-silver-dragon-gs22',
    'MAYA 银龙 GS24': 'maya-silver-dragon-gs24',
    # VR products
    '头盔手柄': 'vr-controller',
    '武器大师(VR支架)': 'weapon-master-vr-stand',
    '玛雅VR头盔': 'maya-vr-headset',
    # Socket brand subdirs
    'maya品牌': 'maya',
    '骐麟品牌': 'kilin',
    # Socket product categories
    '玛雅出国转换': 'maya-travel-adapter',
    '玛雅大功率转换': 'maya-high-power',
    '玛雅居家一转多': 'maya-home-multi-plug',
    '玛雅接线板': 'maya-power-strip',
    '大功率系列': 'high-power-series',
    '家用办公系列': 'home-office-series',
    # Laptop products
    'KILIN 骐麟 FZ-YH5722': 'kilin-fz-yh5722',
    'KILIN 骐麟 FZ-YH5731': 'kilin-fz-yh5731',
}

def make_ascii_dirname(name):
    """Convert a display name to an ASCII-safe directory name"""
    if name in DIR_MAP:
        return DIR_MAP[name]
    # Fallback: remove Chinese chars, slugify
    s = ''.join(c for c in name.lower() if ord(c) < 128)
    s = re.sub(r'[^\w]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-') or 'product'

# Build mapping: old relative path -> new relative path
# We need to rename all directories under images/
# The structure is:
# images/monitors/{sub}/{product_name}/{files}
# images/aios/{product_name}/{files}
# images/others/{category}/{brand_or_sub}/{product_name}/{files}

renames = []  # list of (old_path, new_path)

def collect_renames(base_path, parts_func):
    """Walk directory tree and build rename mapping"""
    results = []
    if not os.path.isdir(base_path):
        return results
    for item in sorted(os.listdir(base_path)):
        old_full = os.path.join(base_path, item)
        if os.path.isdir(old_full):
            new_name = parts_func(old_full, item)
            new_full = os.path.join(os.path.dirname(old_full), new_name)
            if new_full != old_full:
                results.append((old_full, new_full))
            results.extend(collect_renames(new_full if new_full != old_full else old_full, parts_func))
    return results

# We'll do this differently: directly build a path mapping for products.json
# and rename files on disk

print("Step 1: Building path mappings...")

# Process monitors
path_map = {}  # old_path_prefix -> new_path_prefix

for sub_key, prods in data.get('monitors', {}).items():
    sub_label = {'commercial':'商用系列','gaming':'电竞系列','design':'设计系列','professional':'专业系列'}.get(sub_key, sub_key)
    for p in prods:
        # Old path starts with: images/monitors/{sub_label}/{product_display_name}/
        # New path: images/monitors/{sub_key}/{ascii_product_name}/
        old_prefix = f"images/monitors/{sub_label}/{p['name']}"
        new_prefix = f"images/monitors/{sub_key}/{make_ascii_dirname(p['name'])}"
        path_map[old_prefix] = new_prefix
        print(f"  {old_prefix} -> {new_prefix}")

# Process AIOs
for p in data.get('aios', []):
    old_prefix = f"images/aios/{p['name']}"
    new_prefix = f"images/aios/{make_ascii_dirname(p['name'])}"
    path_map[old_prefix] = new_prefix
    print(f"  {old_prefix} -> {new_prefix}")

# Process Others
for sub_key, prods in data.get('others', {}).items():
    sub_label_map = {'VR类目':'VR类目','插座类目':'插座类目','笔记本电脑类目':'笔记本电脑类目'}
    sub_label = sub_label_map.get(sub_key, sub_key)
    for p in prods:
        old_prefix = f"images/others/{sub_label}/{p['name']}"
        new_prefix = f"images/others/{make_ascii_dirname(sub_key)}/{make_ascii_dirname(p['name'])}"
        path_map[old_prefix] = new_prefix
        print(f"  {old_prefix} -> {new_prefix}")

print(f"\nTotal mappings: {len(path_map)}")

# Save mapping for rename script
with open('_path_map.json', 'w', encoding='utf-8') as f:
    json.dump(path_map, f, ensure_ascii=False, indent=2)

# Also update products.json paths
def update_path(path):
    for old, new in path_map.items():
        if path.startswith(old):
            return new + path[len(old):]
    return path

def update_obj(obj):
    if isinstance(obj, str):
        return update_path(obj)
    elif isinstance(obj, list):
        return [update_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: update_obj(v) for k, v in obj.items()}
    return obj

data = update_obj(data)
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nUpdated products.json with new paths")

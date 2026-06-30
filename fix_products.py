"""
Fix products.json:
1. Convert all backslash paths to forward slashes
2. Restore readable product display names from directory names
"""
import sys, json, re

sys.stdout.reconfigure(encoding='utf-8')

with open('products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Human-readable display names mapping
DISPLAY_NAMES = {
    # Monitors - Commercial
    'air-20-air19-53': 'Air 20 (Air系列19.53英寸显示器)',
    'air-22-air21-5': 'Air 22 (Air系列21.5英寸显示器)',
    'air-22-plus-air21-5': 'Air 22 Plus (Air系列21.5英寸显示器)',
    'air-24-air24': 'Air 24 (Air系列24英寸显示器)',
    'air-24-plus-air23-8': 'Air 24 Plus (Air系列23.8英寸显示器)',
    'air-24-pro-23-8': 'Air 24 Pro (商用23.8英寸显示器)',
    'air-240c-23-6': 'Air 240C (商用23.6英寸显示器)',
    'air-27-pro-27': 'Air 27 Pro (商用27英寸显示器)',
    # Monitors - Gaming
    '7g27q-27-144hz': '7G27Q (27英寸-144Hz电竞显示器)',
    '7g32-31-5': '7G32 (31.5英寸-吃鸡电竞显示器)',
    '7g32s-31-5-165hz': '7G32S (31.5英寸-165Hz曲面电竞显示器)',
    '7g33q-31-5-144hz': '7G33Q (31.5英寸-144Hz曲面电竞显示器)',
    '7g33s-31-5-165hz': '7G33S (31.5英寸-165Hz曲面电竞显示器)',
    '7g40-38-5-144hz': '7G40 (38.5英寸-144Hz吃鸡电竞显示器)',
    '7g40g-38-5-144hz': '7G40G (38.5英寸-144Hz曲面电竞显示器)',
    'air-27q-27-ips': 'Air 27Q (27英寸-IPS镜面电竞显示器)',
    'air-32b-31-5': 'Air 32B (31.5英寸-纤薄电竞显示器)',
    'air-32qb-31-5': 'Air 32QB (31.5英寸-超薄电竞显示器)',
    'air-32s-31-5-1800r': 'Air 32S (31.5英寸-1800R曲率电竞显示器)',
    'air-40g-38-5-3000r': 'Air 40G (38.5英寸-3000R曲率电竞显示器)',
    'air-40r-38-5': 'Air 40R (38.5英寸-超大屏率电竞显示器)',
    'air-40rb-38-5': 'Air 40RB (38.5英寸-超大屏电竞显示器)',
    # Monitors - Design
    'q32': 'Q32 (色彩狂魔 量子点显示器)',
    'u2717h-99-srgb': 'U2717H (全面屏 99%sRGB色域)',
    # Monitors - Professional
    'maya-4613-46': 'MAYA 4613 (46英寸液晶拼接屏)',
    # AIOs
    'kilin-gs24pro': 'KILIN 骐麟 GS24pro',
    'kilin-xps24m': 'KILIN 骐麟 XPS24M',
    'maya-white-whale-gs22': 'MAYA 白鲸 GS22',
    'maya-white-whale-gs24': 'MAYA 白鲸 GS24',
    'maya-silver-dragon-gs22': 'MAYA 银龙 GS22',
    'maya-silver-dragon-gs24': 'MAYA 银龙 GS24',
    # VR
    'maya-vr-headset': '玛雅VR头盔',
    'vr-controller': 'VR头盔手柄',
    'weapon-master-vr-stand': '武器大师 (VR支架)',
    # Laptops
    'kilin-fz-yh5722': 'KILIN 骐麟 FZ-YH5722',
    'kilin-fz-yh5731': 'KILIN 骐麟 FZ-YH5731',
    # Sockets - Maya Travel Adapter
    'f8-a': 'F8-A (出国转换插头)',
    'f8-au': 'F8-AU (澳洲版)',
    'f8-e': 'F8-E (欧洲版)',
    'f8-g': 'F8-G (英版)',
    'm1-ce': 'M1-CE',
    'm8': 'M8',
    'm8-a': 'M8-A',
    'm8-e': 'M8-E',
    'm8-eu': 'M8-EU',
    'u8-a': 'U8-A',
    'u8-au': 'U8-AU',
    'u8-e': 'U8-E',
    'u8-g': 'U8-G',
    # Sockets - Maya High Power
    'sy16-11': 'SY16-11 (大功率转换器)',
    'sy16-2': 'SY16-2 (大功率转换器)',
    'sy-222d': 'SY-222D (大功率转换器)',
    # Sockets - Maya Home Multi Plug
    'f102': 'F102 (居家一转多)',
    'f102-f103': 'F102+F103 套装',
    'f103': 'F103 (居家一转多)',
    'f105': 'F105 (居家一转多)',
    'f105usb': 'F105USB (居家一转多)',
    'f108': 'F108 (居家一转多)',
    'sy1-4n': 'SY1-4N (居家一转多)',
    # Sockets - Maya Power Strip
    'f106usb': 'F106USB (接线板)',
    'f106usb-f102': 'F106USB+F102 套装',
    'f208': 'F208 (接线板)',
    'f208-usb': 'F208-USB (接线板)',
    'f602ud': 'F602UD 粉色 (接线板)',
    'f602ud-1': 'F602UD 蓝色 (接线板)',
    'f603ud': 'F603UD 粉色 (接线板)',
    'f603ud-1': 'F603UD 蓝色 (接线板)',
    'h112': 'H112 (接线板)',
    'h112-4-8m': 'H112 4.8m (接线板)',
    'p102u': 'P102U (接线板)',
    'sy-t122': 'SY-T122 (接线板)',
    'sy-t208': 'SY-T208 (接线板)',
    'sy-t233': 'SY-T233 (接线板)',
    # Sockets - Kilin High Power
    'sy-16-10': 'SY 16-10 (大功率)',
    # Sockets - Kilin Home Office
    'sy1-2n': 'SY1-2N (家用办公)',
    'sy1-4mf': 'SY1-4MF (家用办公)',
}

def fix_path(p):
    """Convert backslash to forward slash"""
    if isinstance(p, str):
        return p.replace('\\', '/')
    return p

def fix_obj(obj):
    """Recursively fix all string values"""
    if isinstance(obj, str):
        return fix_path(obj)
    elif isinstance(obj, list):
        return [fix_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: fix_obj(v) for k, v in obj.items()}
    return obj

# Fix all paths
data = fix_obj(data)

# Restore display names
def restore_names(prods_list):
    for p in prods_list:
        slug = p.get('name', '')
        if slug in DISPLAY_NAMES:
            p['display_name'] = DISPLAY_NAMES[slug]

for sub, prods in data.get('monitors', {}).items():
    restore_names(prods)

restore_names(data.get('aios', []))

for sub, prods in data.get('others', {}).items():
    restore_names(prods)

with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Fixed products.json:")
print("- Converted all paths to forward slashes")
print("- Added display_name for readable product names")

# Verify
count = 0
for sub, prods in data.get('monitors', {}).items():
    for p in prods:
        count += 1
        assert '\\' not in p.get('thumb', ''), f"Backslash found in {p['thumb']}"
for p in data.get('aios', []):
    count += 1
    assert '\\' not in p.get('thumb', ''), f"Backslash found in {p['thumb']}"
for sub, prods in data.get('others', {}).items():
    for p in prods:
        count += 1
        assert '\\' not in p.get('thumb', ''), f"Backslash found in {p['thumb']}"
print(f"\nVerified: all {count} products have forward-slash paths")

# Show a sample
p = data['monitors']['commercial'][0]
print(f"\nSample product:")
print(f"  name (slug): {p['name']}")
print(f"  display_name: {p.get('display_name', 'N/A')}")
print(f"  thumb: {p['thumb']}")

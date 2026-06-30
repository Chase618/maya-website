"""
Fix all navigation links to use URL-encoded Chinese directory names.
GitHub Pages serves files with Chinese paths, but links need to be URL-encoded.
"""
import sys, os, urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

# URL-encoded paths
ENC = {
    '显示器': urllib.parse.quote('玛雅显示器'),
    '一体机': urllib.parse.quote('玛雅一体机'),
    '其他产品': urllib.parse.quote('其他产品'),
}

def fix_html(filepath):
    """Fix navigation links in an HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix nav links
    content = content.replace('href="玛雅显示器/index.html"', f'href="{ENC["显示器"]}/index.html"')
    content = content.replace('href="玛雅一体机/index.html"', f'href="{ENC["一体机"]}/index.html"')
    content = content.replace('href="其他产品/index.html"', f'href="{ENC["其他产品"]}/index.html"')

    # Fix relative links going up
    content = content.replace(f'href="{ENC["显示器"]}/../index.html"', f'href="../index.html"')
    content = content.replace(f'href="{ENC["一体机"]}/../index.html"', f'href="../index.html"')
    content = content.replace(f'href="{ENC["其他产品"]}/../index.html"', f'href="../index.html"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Fix all HTML files
for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.html'):
            fix_html(os.path.join(root, f))

print("Fixed all HTML navigation links")
print(f"显示器 -> {ENC['显示器']}")
print(f"一体机 -> {ENC['一体机']}")
print(f"其他产品 -> {ENC['其他产品']}")

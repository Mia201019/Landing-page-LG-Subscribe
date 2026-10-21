#!/usr/bin/env python3
"""
Ghép ảnh sản phẩm cho trang LG Subscribe (Stanbyme landingpage).

Mỗi sản phẩm có MỘT file ảnh riêng, đặt tên theo mã model:
    img/<mã model>.webp      ví dụ: 'AS10GDWH0.ABAE' -> img/AS10GDWH0.webp

Cách dùng (chạy trong thư mục chứa index.html, category-details.html và img/):
    python3 map_images.py          # xem kết quả ghép, chưa ghi file
    python3 map_images.py --write  # ghi lại bảng IMG_MAP vào cả 2 file HTML

Sản phẩm nào chưa có file img/<mã model>.webp thì để trống (cập nhật sau).
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, 'img')
HTML_FILES = ['index.html', 'category-details.html']


def load_products():
    """Lấy danh sách (model, category) từ mảng PRODUCTS trong category-details.html."""
    html = open(os.path.join(HERE, 'category-details.html'), encoding='utf-8').read()
    arr = re.search(r'const PRODUCTS = (\[.*?\]);', html, re.S).group(1)
    return [(p['model'], p['cat']) for p in json.loads(arr)]


def img_for(model, available):
    base = model.split('.')[0]          # 'AS10GDWH0.ABAE' -> 'AS10GDWH0'
    return available.get(base)          # None -> để trống


def main():
    available = {os.path.splitext(f)[0]: f for f in os.listdir(IMG_DIR) if f.endswith('.webp')}
    mapping, missing = {}, []
    for model, cat in load_products():
        f = img_for(model, available)
        if f: mapping[model] = 'img/' + f
        else: missing.append(model)

    print(f'Đã ghép {len(mapping)} sản phẩm, chưa có ảnh {len(missing)}:')
    for m in missing: print('  -', m)

    if '--write' in sys.argv:
        new = 'const IMG_MAP = ' + json.dumps(mapping, ensure_ascii=False, separators=(',', ':')) + ';'
        for name in HTML_FILES:
            p = os.path.join(HERE, name)
            h = open(p, encoding='utf-8').read()
            h2, n = re.subn(r'const IMG_MAP = \{.*?\};', lambda _: new, h, count=1, flags=re.S)
            if n != 1: sys.exit(f'Không tìm thấy IMG_MAP trong {name}')
            open(p, 'w', encoding='utf-8').write(h2)
            print('Đã cập nhật', name)


if __name__ == '__main__':
    main()

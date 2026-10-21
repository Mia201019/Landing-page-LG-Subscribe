#!/usr/bin/env python3
"""
Ghép ảnh sản phẩm cho trang LG Subscribe (Stanbyme landingpage).

Cách dùng (chạy trong thư mục chứa index.html, category-details.html và img/):
    python3 map_images.py          # xem kết quả ghép, chưa ghi file
    python3 map_images.py --write  # ghi lại bảng IMG_MAP vào cả 2 file HTML

Quy tắc ghép (ưu tiên từ trên xuống):
  1. Có file img/<mã model>.webp trùng mã model  -> dùng ảnh riêng.
  2. Điều hòa IDC / IDH                          -> dùng chung img/ac-idc-idh.webp.
  3. TV / Monitor theo ký hiệu dòng trong tên    -> dùng ảnh chung của dòng:
        MRGB86 -> tv-MRG | OLED -> tv-OLED | QNED -> tv-QNED | NU855 -> tv-NU
  4. Không khớp quy tắc nào                      -> để trống (cập nhật sau).
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


def img_for(model, cat, available):
    base = model.split('.')[0]                      # 'AS10GDWH0.ABAE' -> 'AS10GDWH0'

    # 1) Ảnh riêng trùng mã model
    if base in available and not base.startswith('tv-'):
        return available[base]

    # 2) Điều hòa IDC / IDH dùng chung ảnh dàn lạnh (từ catalogue)
    if cat == 'Air Conditioners' and base[:3] in ('IDC', 'IDH'):
        return available.get('ac-idc-idh')

    # 3) TV / Monitor: ghép theo ký hiệu dòng
    if cat in ('TVs', 'Monitors'):
        if 'MRGB86' in base: return available.get('tv-MRG')
        if 'OLED' in base:   return available.get('tv-OLED')
        if 'QNED' in base:   return available.get('tv-QNED')
        if 'NU855' in base:  return available.get('tv-NU')

    return None                                     # 4) để trống


def main():
    available = {os.path.splitext(f)[0]: f for f in os.listdir(IMG_DIR) if f.endswith('.webp')}
    mapping, missing = {}, []
    for model, cat in load_products():
        f = img_for(model, cat, available)
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

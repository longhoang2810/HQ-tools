#!/usr/bin/env python3
"""Tra cứu hóa chất theo mã CAS: hóa chất thuộc Phụ lục nào của Nghị định
24/2026/NĐ-CP, và yêu cầu khi nhập khẩu theo Nghị định 26/2026/NĐ-CP.

Usage:
    python3 lookup.py <CAS>          # ví dụ: python3 lookup.py 107-13-1

Để tra nhiều CAS cùng lúc từ mô tả hàng hóa của doanh nghiệp, dùng scan.py.
"""
import sys

from core import format_report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    print(format_report(sys.argv[1].strip()))

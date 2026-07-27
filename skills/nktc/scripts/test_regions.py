#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "nktc_process.py"
REGIONS = ROOT / "regions.txt"


class RegionConfigTest(unittest.TestCase):
    def test_default_config_has_hcm_and_creates_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.xlsx"
            output = Path(tmp) / "out.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append([
                "So_to_khai", "Ma_LH", "Ma_DN_XNK", "Ten_DN_XNK",
                "Ma_dia_chi_DN_XNK", "So_quan_ly_cua_noi_bo_doanh_nghiep",
                "Tong_tri_gia_tinh_thue",
            ])
            ws.append([123456789, "E21", "0312345678", "DN HCM", "TP.HCM", "12345678XK01", 100])
            wb.save(source)
            subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "-o", str(output), "--regions", str(REGIONS)],
                check=True, capture_output=True, text=True,
            )
            result = load_workbook(output, data_only=True)
            self.assertIn("HCM", result.sheetnames)
            self.assertEqual(result["HCM"]["B5"].value, "DN HCM")


if __name__ == "__main__":
    unittest.main()

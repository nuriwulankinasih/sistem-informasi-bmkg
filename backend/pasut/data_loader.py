from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / 'data' / 'raw' / 'data_pasut_2025.xlsx'
MONTH_SHEETS = ['JAN','PEB','MRT','APR','MEI','JUN','JUL','AGT','SEP','OKT','NOP','DES']


def load_month(sheet_name: str) -> pd.DataFrame:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f'File tidak ditemukan: {RAW_FILE}')
    if sheet_name not in MONTH_SHEETS:
        raise ValueError(f"Sheet '{sheet_name}' tidak tersedia. Pilih: {MONTH_SHEETS}")
    return pd.read_excel(RAW_FILE, sheet_name=sheet_name, header=None)


def load_all_months() -> dict[str, pd.DataFrame]:
    return {month: load_month(month) for month in MONTH_SHEETS}


def get_data_sheet_names() -> list[str]:
    xls = pd.ExcelFile(RAW_FILE)
    return [s for s in xls.sheet_names if s in MONTH_SHEETS]

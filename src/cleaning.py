"""Fungsi pembersihan data pasang-surut dari workbook Excel BMKG.

File ini hanya menangani pembersihan/normalisasi tabel bulanan.
Data Excel asli TIDAK pernah ditimpa oleh script.
"""

import pandas as pd

# Nama kolom jam yang akan dibuat dari JAM 1 sampai JAM 24 pada Excel.
JAM_COLUMNS = [f"jam_{i}" for i in range(1, 25)]


def extract_tide_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Mengambil tabel TGL + JAM 1..24 dari satu sheet bulanan.

    Struktur workbook yang dipakai:
    - baris Excel ke-7 (index 6) berisi header TGL/JAM 1..24
    - baris Excel berikutnya berisi tanggal 1..akhir bulan
    - kolom setelah JAM 24 dapat berisi tabel bantu/formula dan sengaja diabaikan
    """
    df = df_raw.copy()

    if len(df) < 8 or df.shape[1] < 25:
        raise ValueError(
            "Struktur sheet tidak sesuai: minimal 25 kolom dan 8 baris."
        )

    # Ambil hanya kolom TGL dan 24 jam pertama.
    data = df.iloc[7:, :25].copy()
    data.columns = ["tanggal"] + JAM_COLUMNS

    # Ubah tanggal dan tinggi muka air menjadi numerik.
    data["tanggal"] = pd.to_numeric(data["tanggal"], errors="coerce")
    data = data.dropna(subset=["tanggal"]).copy()
    data["tanggal"] = data["tanggal"].astype(int)

    for col in JAM_COLUMNS:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    return data.reset_index(drop=True)


def remove_empty_days(df: pd.DataFrame) -> pd.DataFrame:
    """Menghapus baris tanggal yang seluruh 24 jamnya kosong."""
    df = df.copy()
    empty = df[JAM_COLUMNS].isna().all(axis=1)

    if empty.any():
        print(
            "Hari tanpa data yang dihapus:",
            df.loc[empty, "tanggal"].astype(int).tolist(),
        )

    return df.loc[~empty].reset_index(drop=True)


def clean_month(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Pipeline pembersihan satu sheet bulanan."""
    return remove_empty_days(extract_tide_table(df_raw))


def month_to_long(df_clean: pd.DataFrame, month: str) -> pd.DataFrame:
    """Mengubah format lebar (24 kolom jam) menjadi format panjang."""
    df = df_clean.melt(
        id_vars=["tanggal"],
        value_vars=JAM_COLUMNS,
        var_name="jam",
        value_name="tinggi_m",
    )

    df["jam"] = (
        df["jam"].str.replace("jam_", "", regex=False).astype(int)
    )
    df["tinggi_m"] = pd.to_numeric(df["tinggi_m"], errors="coerce")
    df["bulan"] = month
    df["sumber_sheet"] = month

    return df[["bulan", "tanggal", "jam", "tinggi_m", "sumber_sheet"]].sort_values(
        ["tanggal", "jam"]
    ).reset_index(drop=True)

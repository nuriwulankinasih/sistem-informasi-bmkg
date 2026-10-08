"""Transformasi data pasut dari format bulanan menjadi dataset tahunan."""

import pandas as pd

# Kode bulan pada workbook -> angka bulan kalender.
MONTH_MAP = {
    "JAN": 1, "PEB": 2, "MRT": 3, "APR": 4,
    "MEI": 5, "JUN": 6, "JUL": 7, "AGT": 8,
    "SEP": 9, "OKT": 10, "NOP": 11, "DES": 12,
}


def wide_to_long(df: pd.DataFrame) -> pd.DataFrame:
    """Mengubah satu tabel bulanan dari wide menjadi long."""
    jam_columns = [f"jam_{i}" for i in range(1, 25)]
    out = df.melt(
        id_vars=["tanggal"],
        value_vars=jam_columns,
        var_name="jam",
        value_name="tinggi_m",
    )
    out["jam"] = out["jam"].str.replace("jam_", "", regex=False).astype(int)
    out["tinggi_m"] = pd.to_numeric(out["tinggi_m"], errors="coerce")
    return out.sort_values(["tanggal", "jam"]).reset_index(drop=True)


def create_timestamp(df: pd.DataFrame, year: int = 2025) -> pd.DataFrame:
    """Membuat timestamp WIB berdasarkan tanggal + label JAM pada workbook.

    Konvensi sumber:
    JAM 1..23 = 01:00..23:00 pada tanggal tersebut.
    JAM 24 = 00:00 pada hari berikutnya.
    """
    out = df.copy()

    if "bulan" not in out.columns:
        raise ValueError("Kolom 'bulan' diperlukan untuk membuat timestamp.")

    out["bulan_num"] = out["bulan"].map(MONTH_MAP)
    if out["bulan_num"].isna().any():
        raise ValueError("Ada kode bulan yang tidak dikenali.")

    # Membuat tanggal dasar tanpa jam.
    base = pd.to_datetime(
        {
            "year": year,
            "month": out["bulan_num"],
            "day": out["tanggal"],
        },
        errors="coerce",
    )

    if base.isna().any():
        bad = out.loc[base.isna(), ["bulan", "tanggal"]].drop_duplicates()
        raise ValueError(f"Tanggal tidak valid ditemukan:\n{bad}")

    # JAM 24 otomatis menjadi 00:00 hari berikutnya.
    out["timestamp"] = (
        base + pd.to_timedelta(out["jam"], unit="h")
    ).dt.tz_localize("Asia/Jakarta")

    return out.drop(columns=["bulan_num"]).sort_values("timestamp").reset_index(drop=True)


def build_annual_dataset(monthly_clean: dict[str, pd.DataFrame], year: int = 2025) -> pd.DataFrame:
    """Menggabungkan 12 sheet bulanan menjadi satu dataset tahunan."""
    parts = []

    for month, df in monthly_clean.items():
        x = wide_to_long(df)
        x["bulan"] = month
        x["sumber_sheet"] = month
        parts.append(x)

    out = pd.concat(parts, ignore_index=True)
    out = create_timestamp(out, year=year)

    # Tahun observasi mengikuti tanggal sumber; JAM 24 tanggal 31 Desember
    # memang menjadi 00:00 pada 1 Januari tahun berikutnya secara timestamp.
    out["tahun_data"] = year

    return out[
        ["timestamp", "tahun_data", "bulan", "tanggal", "jam", "tinggi_m", "sumber_sheet"]
    ].sort_values("timestamp").reset_index(drop=True)

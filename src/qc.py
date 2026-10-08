"""Quality Control (QC) untuk dataset pasang-surut.

QC menjawab pertanyaan dasar sebelum data dimasukkan ke database:
1. Apakah semua bulan terbaca?
2. Berapa hari dan observasi per bulan?
3. Apakah ada nilai kosong?
4. Apakah ada timestamp duplikat?
5. Apakah interval waktu benar-benar 1 jam?
6. Apakah jumlah observasi tahunan sesuai 365 x 24 = 8760?
"""

import pandas as pd

from .cleaning import clean_month, JAM_COLUMNS
from .data_loader import MONTH_SHEETS
from .preprocessing import build_annual_dataset


def monthly_qc(load_month_func) -> pd.DataFrame:
    """Membuat tabel QC untuk setiap sheet bulan."""
    rows = []

    for month in MONTH_SHEETS:
        raw = load_month_func(month)
        clean = clean_month(raw)

        rows.append(
            {
                "bulan": month,
                "jumlah_hari": len(clean),
                "tanggal_min": clean["tanggal"].min(),
                "tanggal_max": clean["tanggal"].max(),
                "jumlah_observasi": int(clean[JAM_COLUMNS].notna().sum().sum()),
                "missing_observasi": int(clean[JAM_COLUMNS].isna().sum().sum()),
                "hari_missing_sebagian": int(
                    clean[JAM_COLUMNS].isna().any(axis=1).sum()
                ),
                "hari_lengkap": int(
                    clean[JAM_COLUMNS].notna().all(axis=1).sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def annual_qc(df: pd.DataFrame) -> dict:
    """Menghasilkan ringkasan QC dataset tahunan."""
    x = df.sort_values("timestamp").copy()

    actual = pd.DatetimeIndex(x["timestamp"])
    duplicate_timestamp = int(actual.duplicated().sum())

    # Karena timestamp pertama pada sumber adalah 01:00 tanggal 1 Januari,
    # expected dibuat dari timestamp aktual pertama sampai terakhir.
    expected = pd.date_range(
        start=actual.min(),
        end=actual.max(),
        freq="h",
        tz="Asia/Jakarta",
    )
    missing_timestamps = expected.difference(actual)

    interval_hours = actual.to_series().diff().dt.total_seconds().div(3600).dropna()

    return {
        "rows": len(x),
        "expected_rows_2025": 365 * 24,
        "missing_height": int(x["tinggi_m"].isna().sum()),
        "duplicate_timestamp": duplicate_timestamp,
        "timestamp_min": actual.min(),
        "timestamp_max": actual.max(),
        "expected_hourly_rows": len(expected),
        "missing_timestamps": len(missing_timestamps),
        "interval_min_hours": float(interval_hours.min()) if len(interval_hours) else None,
        "interval_max_hours": float(interval_hours.max()) if len(interval_hours) else None,
        "height_min_m": float(x["tinggi_m"].min()),
        "height_max_m": float(x["tinggi_m"].max()),
        "height_mean_m": float(x["tinggi_m"].mean()),
    }


def validate_annual_dataset(df: pd.DataFrame, strict: bool = True) -> None:
    """Memastikan dataset memenuhi syarat minimal untuk database.

    strict=True akan menghentikan proses ekspor jika ada masalah struktural.
    """
    required = {
        "timestamp", "tahun_data", "bulan", "tanggal",
        "jam", "tinggi_m", "sumber_sheet",
    }
    missing_columns = required.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Kolom wajib belum tersedia: {sorted(missing_columns)}")

    qc = annual_qc(df)
    errors = []

    if qc["rows"] != qc["expected_rows_2025"]:
        errors.append(
            f"Jumlah baris {qc['rows']} bukan {qc['expected_rows_2025']} observasi."
        )
    if qc["missing_height"] != 0:
        errors.append(f"Masih ada {qc['missing_height']} nilai tinggi muka air kosong.")
    if qc["duplicate_timestamp"] != 0:
        errors.append(f"Ada {qc['duplicate_timestamp']} timestamp duplikat.")
    if qc["missing_timestamps"] != 0:
        errors.append(f"Ada {qc['missing_timestamps']} timestamp per jam yang hilang.")
    if qc["interval_min_hours"] != 1.0 or qc["interval_max_hours"] != 1.0:
        errors.append("Interval timestamp tidak konsisten 1 jam.")

    if errors and strict:
        raise ValueError("QC GAGAL:\n- " + "\n- ".join(errors))

    if errors:
        print("PERINGATAN QC:\n- " + "\n- ".join(errors))

"""
===========================================================
IMPORT DATA PASUT 2025 KE MYSQL
===========================================================

File input:
    data/processed/pasut_2025_long.csv

Database:
    bmkg_pasut

Tabel:
    pasut

Tujuan:
    1. Membaca CSV hasil preprocessing
    2. Memvalidasi struktur data
    3. Mengubah tipe data yang diperlukan
    4. Memasukkan 8.760 data observasi ke MySQL
    5. Mengecek hasil import

Catatan:
    Kolom 'bulan' berupa teks seperti JAN, FEB, MAR, dst.
    sehingga TIDAK dikonversi menjadi angka.
===========================================================
"""

import sys
from pathlib import Path

import pandas as pd
import mysql.connector


# =========================================================
# 1. MENENTUKAN LOKASI PROJECT
# =========================================================

# Folder utama project_pasut
BASE_DIR = Path(__file__).resolve().parent.parent

# Lokasi file CSV
CSV_PATH = BASE_DIR / "data" / "processed" / "pasut_2025_long.csv"


# =========================================================
# 2. KONFIGURASI DATABASE MYSQL
# =========================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "bmkg_pasut",
}


# =========================================================
# 3. KOLOM YANG WAJIB ADA
# =========================================================

REQUIRED_COLUMNS = [
    "timestamp",
    "tahun_data",
    "bulan",
    "tanggal",
    "jam",
    "tinggi_m",
    "sumber_sheet",
]


# =========================================================
# 4. MEMBACA CSV
# =========================================================

def load_csv():
    """
    Membaca file CSV pasut hasil preprocessing.
    """

    print("=" * 60)
    print("MEMBACA FILE CSV")
    print("=" * 60)

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"File CSV tidak ditemukan:\n{CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(f"File CSV berhasil dibaca.")
    print(f"Lokasi       : {CSV_PATH}")
    print(f"Jumlah baris : {len(df):,}")
    print(f"Jumlah kolom : {len(df.columns)}")

    print("\nKolom yang ditemukan:")

    for column in df.columns:
        print(f" - {column}")

    return df


# =========================================================
# 5. VALIDASI KOLOM
# =========================================================

def validate_columns(df):
    """
    Memastikan semua kolom yang diperlukan tersedia.
    """

    print("\n" + "=" * 60)
    print("VALIDASI KOLOM")
    print("=" * 60)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Kolom berikut tidak ditemukan:\n"
            + "\n".join(f"- {column}" for column in missing_columns)
        )

    print("Semua kolom yang diperlukan tersedia.")


# =========================================================
# 6. MENYIAPKAN DATA
# =========================================================

def prepare_data(df):
    """
    Membersihkan dan memastikan tipe data sesuai
    dengan struktur tabel MySQL.
    """

    print("\n" + "=" * 60)
    print("PERSIAPAN DATA")
    print("=" * 60)

    df = df.copy()

    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------
    #
    # Contoh:
    # 2025-01-01 01:00:00+07:00
    #
    # MySQL DATETIME tidak menyimpan timezone.
    # Karena data merupakan data lokal WIB, timezone
    # +07:00 kita lepaskan dan simpan sebagai waktu lokal.
    # -----------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    if df["timestamp"].isna().any():
        jumlah = df["timestamp"].isna().sum()

        raise ValueError(
            f"Terdapat {jumlah} timestamp yang tidak valid."
        )

    # Jika timestamp terbaca sebagai timezone-aware,
    # kita hilangkan timezone tanpa mengubah jam lokal.
    if hasattr(df["timestamp"].dt, "tz") and df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(None)

    # -----------------------------------------------------
    # TAHUN DATA
    # -----------------------------------------------------

    df["tahun_data"] = pd.to_numeric(
        df["tahun_data"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # BULAN
    # -----------------------------------------------------
    #
    # PENTING:
    # bulan memang berupa teks:
    #
    # JAN
    # FEB
    # MAR
    # ...
    #
    # Jadi jangan menggunakan pd.to_numeric().
    # -----------------------------------------------------

    df["bulan"] = (
        df["bulan"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # -----------------------------------------------------
    # TANGGAL
    # -----------------------------------------------------

    df["tanggal"] = pd.to_numeric(
        df["tanggal"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # JAM
    # -----------------------------------------------------

    df["jam"] = pd.to_numeric(
        df["jam"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # TINGGI MUKA AIR
    # -----------------------------------------------------

    df["tinggi_m"] = pd.to_numeric(
        df["tinggi_m"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # SUMBER SHEET
    # -----------------------------------------------------

    df["sumber_sheet"] = (
        df["sumber_sheet"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # -----------------------------------------------------
    # CEK NILAI NULL
    # -----------------------------------------------------

    null_counts = df[REQUIRED_COLUMNS].isna().sum()

    print("\nJumlah nilai kosong:")

    print(null_counts)

    if null_counts.sum() > 0:
        raise ValueError(
            "Terdapat nilai kosong pada kolom yang diperlukan."
        )

    # -----------------------------------------------------
    # KONVERSI KE INTEGER
    # -----------------------------------------------------

    df["tahun_data"] = df["tahun_data"].astype(int)
    df["tanggal"] = df["tanggal"].astype(int)
    df["jam"] = df["jam"].astype(int)

    # -----------------------------------------------------
    # VALIDASI JAM
    # -----------------------------------------------------

    invalid_jam = df[
        (df["jam"] < 1) |
        (df["jam"] > 24)
    ]

    if len(invalid_jam) > 0:
        raise ValueError(
            f"Ditemukan {len(invalid_jam)} data dengan jam "
            "di luar rentang 1-24."
        )

    # -----------------------------------------------------
    # VALIDASI TANGGAL
    # -----------------------------------------------------

    invalid_tanggal = df[
        (df["tanggal"] < 1) |
        (df["tanggal"] > 31)
    ]

    if len(invalid_tanggal) > 0:
        raise ValueError(
            f"Ditemukan {len(invalid_tanggal)} data dengan "
            "tanggal di luar rentang 1-31."
        )

    # -----------------------------------------------------
    # CEK DUPLIKAT TIMESTAMP
    # -----------------------------------------------------

    duplicate_count = df["timestamp"].duplicated().sum()

    print(f"\nDuplikat timestamp : {duplicate_count}")

    if duplicate_count > 0:
        raise ValueError(
            f"Ditemukan {duplicate_count} timestamp duplikat."
        )

    # -----------------------------------------------------
    # URUTKAN BERDASARKAN TIMESTAMP
    # -----------------------------------------------------

    df = df.sort_values("timestamp").reset_index(drop=True)

    print("\nData berhasil dipersiapkan.")

    print("\nTipe data setelah preprocessing:")

    print(df[REQUIRED_COLUMNS].dtypes)

    return df


# =========================================================
# 7. KONEKSI MYSQL
# =========================================================

def get_connection():
    """
    Membuat koneksi ke database MySQL.
    """

    print("\n" + "=" * 60)
    print("KONEKSI MYSQL")
    print("=" * 60)

    connection = mysql.connector.connect(**DB_CONFIG)

    print("Koneksi MySQL berhasil.")

    return connection


# =========================================================
# 8. IMPORT DATA KE MYSQL
# =========================================================

def import_to_mysql(df):
    """
    Memasukkan seluruh data ke tabel pasut.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # SQL INSERT
        # -------------------------------------------------

        sql = """
        INSERT INTO pasut
        (
            `timestamp`,
            tahun_data,
            bulan,
            tanggal,
            jam,
            tinggi_m,
            sumber_sheet
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON DUPLICATE KEY UPDATE
            tahun_data = VALUES(tahun_data),
            bulan = VALUES(bulan),
            tanggal = VALUES(tanggal),
            jam = VALUES(jam),
            tinggi_m = VALUES(tinggi_m),
            sumber_sheet = VALUES(sumber_sheet)
        """

        # -------------------------------------------------
        # MENYIAPKAN DATA UNTUK MYSQL
        # -------------------------------------------------

        rows = []

        for _, row in df.iterrows():

            rows.append(
                (
                    row["timestamp"].to_pydatetime(),
                    int(row["tahun_data"]),
                    row["bulan"],
                    int(row["tanggal"]),
                    int(row["jam"]),
                    float(row["tinggi_m"]),
                    row["sumber_sheet"],
                )
            )

        # -------------------------------------------------
        # IMPORT DALAM BATCH
        # -------------------------------------------------

        batch_size = 500

        total_rows = len(rows)

        print("\n" + "=" * 60)
        print("IMPORT DATA KE MYSQL")
        print("=" * 60)

        for start in range(0, total_rows, batch_size):

            end = min(
                start + batch_size,
                total_rows
            )

            batch = rows[start:end]

            cursor.executemany(
                sql,
                batch
            )

            connection.commit()

            print(
                f"Progress: {end:,} / {total_rows:,}"
            )

        print("\nIMPORT BERHASIL.")

    except Exception:

        if connection:
            connection.rollback()

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# 9. VERIFIKASI HASIL IMPORT
# =========================================================

def verify_database():
    """
    Mengecek jumlah data yang sudah masuk ke MySQL.
    """

    print("\n" + "=" * 60)
    print("VERIFIKASI DATABASE")
    print("=" * 60)

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # JUMLAH DATA
        # -------------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM pasut"
        )

        total = cursor.fetchone()[0]

        print(f"Jumlah data dalam database : {total:,}")

        # -------------------------------------------------
        # RENTANG WAKTU
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                MIN(`timestamp`),
                MAX(`timestamp`)
            FROM pasut
            """
        )

        min_timestamp, max_timestamp = cursor.fetchone()

        print(
            f"Timestamp paling awal      : {min_timestamp}"
        )

        print(
            f"Timestamp paling akhir     : {max_timestamp}"
        )

        # -------------------------------------------------
        # CONTOH DATA
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                `timestamp`,
                tahun_data,
                bulan,
                tanggal,
                jam,
                tinggi_m,
                sumber_sheet
            FROM pasut
            ORDER BY `timestamp`
            LIMIT 5
            """
        )

        rows = cursor.fetchall()

        print("\n5 data pertama:")

        for row in rows:
            print(row)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# 10. PROGRAM UTAMA
# =========================================================

def main():

    try:

        # Membaca CSV
        df = load_csv()

        # Validasi struktur kolom
        validate_columns(df)

        # Menyiapkan data
        df = prepare_data(df)

        # Import ke MySQL
        import_to_mysql(df)

        # Verifikasi
        verify_database()

        print("\n" + "=" * 60)
        print("SEMUA PROSES SELESAI.")
        print("=" * 60)

    except Exception as error:

        print("\n" + "=" * 60)
        print("IMPORT GAGAL")
        print("=" * 60)

        print(
            f"Jenis error : {type(error).__name__}"
        )

        print(
            f"Pesan error : {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
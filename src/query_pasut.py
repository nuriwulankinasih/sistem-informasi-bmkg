"""
===========================================================
QUERY DATA PASUT DARI MYSQL
===========================================================

File:
    src/query_pasut.py

Database:
    bmkg_pasut

Tabel:
    pasut

Tujuan:
    File ini berisi fungsi-fungsi untuk mengambil data
    pasang surut dari database MySQL.

Fungsi utama:

    get_all_pasut()
    get_pasut_by_year()
    get_pasut_by_month()
    get_pasut_by_date()
    get_pasut_between_dates()

Fungsi-fungsi ini nantinya akan digunakan oleh:
    - dashboard
    - analisis Admiralty
    - analisis Least Square
    - grafik
    - laporan
===========================================================
"""

import pandas as pd

from database import get_connection


# =========================================================
# 1. MENGAMBIL SEMUA DATA PASUT
# =========================================================

def get_all_pasut():
    """
    Mengambil seluruh data pasut dari MySQL.

    Hasil:
        pandas.DataFrame
    """

    sql = """
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
    """

    connection = get_connection()

    try:

        df = pd.read_sql(
            sql,
            connection
        )

        return df

    finally:

        connection.close()


# =========================================================
# 2. MENGAMBIL DATA BERDASARKAN TAHUN
# =========================================================

def get_pasut_by_year(tahun):
    """
    Mengambil data pasut berdasarkan tahun.

    Contoh:
        get_pasut_by_year(2025)
    """

    sql = """
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
    WHERE tahun_data = %s
    ORDER BY `timestamp`
    """

    connection = get_connection()

    try:

        df = pd.read_sql(
            sql,
            connection,
            params=(tahun,)
        )

        return df

    finally:

        connection.close()


# =========================================================
# 3. MENGAMBIL DATA BERDASARKAN BULAN
# =========================================================

def get_pasut_by_month(tahun, bulan):
    """
    Mengambil data pasut berdasarkan tahun dan bulan.

    Contoh:
        get_pasut_by_month(2025, "JAN")
    """

    sql = """
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
    WHERE tahun_data = %s
      AND bulan = %s
    ORDER BY `timestamp`
    """

    connection = get_connection()

    try:

        df = pd.read_sql(
            sql,
            connection,
            params=(tahun, bulan.upper())
        )

        return df

    finally:

        connection.close()


# =========================================================
# 4. MENGAMBIL DATA BERDASARKAN TANGGAL
# =========================================================

def get_pasut_by_date(tanggal):
    """
    Mengambil data pasut pada satu tanggal.

    Parameter:
        tanggal = string dengan format YYYY-MM-DD

    Contoh:
        get_pasut_by_date("2025-08-01")
    """

    sql = """
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
    WHERE DATE(`timestamp`) = %s
    ORDER BY `timestamp`
    """

    connection = get_connection()

    try:

        df = pd.read_sql(
            sql,
            connection,
            params=(tanggal,)
        )

        return df

    finally:

        connection.close()


# =========================================================
# 5. MENGAMBIL DATA BERDASARKAN RENTANG TANGGAL
# =========================================================

def get_pasut_between_dates(tanggal_awal, tanggal_akhir):
    """
    Mengambil data pasut berdasarkan rentang tanggal.

    Parameter:
        tanggal_awal
            format YYYY-MM-DD

        tanggal_akhir
            format YYYY-MM-DD

    Contoh:
        get_pasut_between_dates(
            "2025-08-01",
            "2025-08-29"
        )

    Fungsi ini sangat penting untuk analisis Admiralty
    dan Least Square karena kita dapat mengambil
    window data tertentu tanpa mengubah data master.
    """

    sql = """
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
    WHERE `timestamp` >= %s
      AND `timestamp` < DATE_ADD(%s, INTERVAL 1 DAY)
    ORDER BY `timestamp`
    """

    connection = get_connection()

    try:

        df = pd.read_sql(
            sql,
            connection,
            params=(tanggal_awal, tanggal_akhir)
        )

        return df

    finally:

        connection.close()


# =========================================================
# 6. TEST PROGRAM
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TEST QUERY DATA PASUT")
    print("=" * 60)


    # -----------------------------------------------------
    # TEST 1
    # Semua data
    # -----------------------------------------------------

    print("\n[1] Semua data")

    df_all = get_all_pasut()

    print(f"Jumlah data : {len(df_all):,}")

    print(df_all.head())


    # -----------------------------------------------------
    # TEST 2
    # Data tahun 2025
    # -----------------------------------------------------

    print("\n[2] Data tahun 2025")

    df_year = get_pasut_by_year(2025)

    print(f"Jumlah data : {len(df_year):,}")


    # -----------------------------------------------------
    # TEST 3
    # Data Januari 2025
    # -----------------------------------------------------

    print("\n[3] Data Januari 2025")

    df_month = get_pasut_by_month(
        2025,
        "JAN"
    )

    print(f"Jumlah data : {len(df_month):,}")

    print(df_month.head())


    # -----------------------------------------------------
    # TEST 4
    # Data tanggal 1 Agustus 2025
    # -----------------------------------------------------

    print("\n[4] Data 1 Agustus 2025")

    df_date = get_pasut_by_date(
        "2025-08-01"
    )

    print(f"Jumlah data : {len(df_date):,}")

    print(df_date.head())


    # -----------------------------------------------------
    # TEST 5
    # Data 1-29 Agustus 2025
    # -----------------------------------------------------

    print("\n[5] Data 1-29 Agustus 2025")

    df_range = get_pasut_between_dates(
        "2025-08-01",
        "2025-08-29"
    )

    print(f"Jumlah data : {len(df_range):,}")

    print(df_range.head())

    print("\n" + "=" * 60)
    print("SEMUA TEST QUERY SELESAI")
    print("=" * 60)
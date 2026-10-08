"""
database.py

=========================================================
FUNGSI FILE
=========================================================

File ini digunakan untuk membuat koneksi dari Python
ke database MySQL.

Alur project:

    Python
       |
       v
    MySQL
       |
       v
    database: bmkg_pasut
       |
       v
    tabel: pasut

File ini BELUM digunakan untuk memasukkan data 8.760 baris.

Fokus file ini hanya:
1. Membuat koneksi ke MySQL
2. Mengecek apakah koneksi berhasil
3. Menutup koneksi dengan benar
=========================================================
"""

# =========================================================
# 1. IMPORT LIBRARY
# =========================================================

# Library ini digunakan agar Python dapat berkomunikasi
# dengan database MySQL.
import mysql.connector

# Error digunakan untuk menangkap kesalahan koneksi MySQL.
from mysql.connector import Error


# =========================================================
# 2. KONFIGURASI DATABASE
# =========================================================

# Host MySQL.
# Karena MySQL dijalankan di komputer sendiri melalui XAMPP,
# kita menggunakan localhost.
DB_HOST = "localhost"

# Username MySQL.
# Pada konfigurasi XAMPP standar biasanya adalah root.
DB_USER = "root"

# Password MySQL.
# Pada konfigurasi XAMPP standar biasanya kosong.
DB_PASSWORD = ""

# Nama database yang tadi kita buat.
DB_NAME = "bmkg_pasut"

# Port default MySQL.
DB_PORT = 3306


# =========================================================
# 3. FUNGSI MEMBUAT KONEKSI
# =========================================================

def get_connection():
    """
    Fungsi ini digunakan untuk membuat koneksi
    Python ke database MySQL.

    Jika berhasil:
        mengembalikan objek connection.

    Jika gagal:
        mengembalikan None.
    """

    try:

        # Membuat koneksi ke MySQL
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )

        # Mengecek apakah koneksi benar-benar aktif
        if connection.is_connected():

            print("========================================")
            print("Koneksi MySQL berhasil.")
            print("========================================")
            print(f"Host     : {DB_HOST}")
            print(f"Database : {DB_NAME}")
            print(f"User     : {DB_USER}")
            print(f"Port     : {DB_PORT}")
            print("========================================")

            return connection

        else:

            print("Koneksi MySQL gagal.")

            return None

    except Error as error:

        # Bagian ini dijalankan jika terjadi error
        # ketika Python mencoba terhubung ke MySQL.
        print("========================================")
        print("Koneksi MySQL gagal.")
        print("========================================")
        print("Detail error:")
        print(error)

        return None


# =========================================================
# 4. TEST KONEKSI
# =========================================================

# Bagian ini hanya dijalankan apabila file
# database.py dijalankan secara langsung.

if __name__ == "__main__":

    # Memanggil fungsi koneksi
    connection = get_connection()

    # Jika koneksi berhasil
    if connection is not None:

        # Menutup koneksi setelah selesai melakukan test
        connection.close()

        print("Koneksi MySQL ditutup.")
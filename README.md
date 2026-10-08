@"
# Sistem Informasi BMKG

Project sistem informasi dan dashboard pengolahan data BMKG.

## Modul
- Pasut
- F-KLIM

## Modul Pasut
Modul pasut digunakan untuk pengolahan dan analisis data pasang surut.

Metode analisis yang akan dikembangkan:
- Admiralty
- Least Square

## Struktur Project

- `backend/pasut/` - backend pengolahan data pasut
- `backend/fklim/` - backend pengolahan data F-KLIM
- `frontend/pasut/` - frontend modul pasut
- `frontend/fklim/` - frontend modul F-KLIM
- `database/` - struktur database
- `docs/` - dokumentasi project
- `data/` - dokumentasi dan pengelolaan data
"@ | Set-Content .\README.md
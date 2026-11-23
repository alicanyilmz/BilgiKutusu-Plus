# BilgiKutusu Plus 1.0.0 — Test notları / Validation notes

**Tarih / Date:** 23 Kasım / November 2026

| Kontrol / Check | Sonuç / Result |
| --- | --- |
| Mevcut uygulama testleri / Existing application tests | 22 test geçti / 22 tests passed |
| Bash betikleri / Bash scripts | Sözdizimi kontrolü geçti / Syntax checks passed |
| Yapılandırma / Configuration | `app.py --check` başarılı / Passed |
| Tarayıcı JavaScript'i / Browser JavaScript | `node --check` başarılı / Passed |

`python3 -B -m unittest discover -s testler -v` gerçek yerel HTTP istekleriyle dosya listeleme, indirme, byte aralıkları, Türkçe adlar, gizli dosyalar, sembolik bağlantılar, klasör dışına erişim ve yapılandırma davranışlarını kontrol etti. Süre: 11,103 saniye.

The existing tests exercised local HTTP behavior: listing, downloads, byte ranges, Turkish names, hidden files, symbolic links, directory traversal and configuration. Duration: 11.103 seconds.

## Kapsam / Scope

Kontroller geliştirme ortamında çalıştırıldı. Fiziksel Raspberry Pi 4, 4 GB RAM altında performans, gerçek SSD, Wi-Fi erişim noktası ve systemd kurulumu bu çalışmada test edilmedi. Testlerin geçmesi donanım kurulumu veya her koşulda hatasız çalışma garantisi değildir.

Checks ran in a development environment. Physical Raspberry Pi 4 operation, performance with 4 GB RAM, real SSD storage, Wi-Fi access point operation and systemd installation were not tested here. Passing tests does not establish hardware readiness or defect-free operation under all conditions.

Uygulama kodu ve paket içindeki lisans metinleri özgün ZIP ile aynıdır. Yayın hazırlığında Türkçe/İngilizce README, bu test notları, `.gitignore` ve boş klasörleri koruyan `.gitkeep` dosyaları eklendi veya düzenlendi.

Application code and bundled license texts match the original ZIP. Publication preparation added or updated Turkish/English READMEs, these notes, `.gitignore`, and `.gitkeep` placeholders for empty folders.

<div align="center">

# 📚 BilgiKutusu Plus
### İnternet olmasa da bilgi yanında.
**Raspberry Pi 4 için taşınabilir, çevrimdışı bilgi deposu.**

![Sürüm](https://img.shields.io/badge/sürüm-1.0.0-2563eb?style=for-the-badge)
![Hedef donanım](https://img.shields.io/badge/Raspberry_Pi_4-4_GB_RAM-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Çevrimdışı](https://img.shields.io/badge/kullanım-çevrimdışı-15803d?style=for-the-badge)

**Türkçe** · [English](README.en.md)

[Geliştirici: alicanyilmz](https://github.com/alicanyilmz) · [Organizasyon: Bilikon-Project](https://github.com/Bilikon-Project)

</div>

---

> **Geliştirme sürümü · 1.0.0**  
> Bu depo uygulamayı, kurulum dosyalarını ve küçük örnek içerikleri içerir. **Kitap arşivi dahil değildir.** Harita ve video deneme amaçlı örneklerdir. Raspberry Pi üzerinde gerçek donanım ve yük testi henüz doğrulanmamıştır.

## 🌿 BilgiKutusu Plus nedir?

Telefon, tablet ve bilgisayardan aynı yerel ağa bağlanarak dosyalara ulaşmanı sağlayan bir bilgi deposudur. İnternet bağlantısı olmadan klasörleri gezebilir, açık klasörde dosya adına göre arama yapabilir, uyumlu videoları tarayıcıda açabilir ve içerikleri indirebilirsin.

**Plus, BilgiKutusu ailesinin orta seviyesidir:** Go temelinin üzerine seçili özellikler ve örnek içerikler ekler; hedef donanımı **Raspberry Pi 4 Model B, 4 GB RAM**'dir. Yapay zekâ içermez. Python standart kütüphanesini kullanır; ek Python paketi veya bulut hesabı istemez.

## ✨ Özellikler

| Özellik | Bu sürümdeki davranış |
| :--- | :--- |
| 📂 Dosya gezgini | İçerik klasörlerini tarayıcıdan görüntüler. |
| 🔎 Arama ve filtreleme | Açık klasörde dosya adına ve içerik türüne göre süzer. |
| 🎬 Medya erişimi | Tarayıcının desteklediği ses/video dosyalarını açar; HTTP aralık isteklerini destekler. |
| ⬇️ İndirme | Dosyaları telefona veya bilgisayara indirir. |
| 💾 SSD desteği | İçerik klasörü SSD üzerindeki bir klasöre yönlendirilebilir. |
| ⚙️ Otomatik başlatma | systemd kullanan Linux sistemlerde hizmet olarak çalışır. |
| 🧭 Yerel kullanım | Portalın çalışması için internet veya harici web kaynağı gerekmez. |

## 📦 Pakette ne var?

| Bölüm | Dahil olan içerik | Açıklama |
| :--- | :--- | :--- |
| Haritalar | Türkiye şehir konumları görseli | Dokuz şehir merkezinin yaklaşık konumlarını gösteren **örnek koordinat haritası**; ayrıntılı Türkiye haritası değildir. |
| Eğitim videoları | Haritada yönler | Yön, enlem ve boylam okumaya yönelik **24 saniyelik, yazılı anlatımlı örnek video**. |
| Tarım | Ekim takibi CSV çizelgesi | İndirip kendi cihazında doldurabileceğin şablon. |
| Balıkçılık | Gözlem defteri CSV çizelgesi | İndirip kendi cihazında doldurabileceğin şablon. |
| Belgeler | Başlangıç metni | Kısa kullanım bilgisi. |
| Kitaplar | Boş içerik alanı | **Kitap veya e-kitap arşivi bulunmaz.** |
| Görseller | Boş içerik alanı | Kendi görsellerin için ayrılmış klasör. |

Wikipedia/ZIM arşivleri, Kiwix, film/dizi arşivleri ve büyük eğitim kütüphaneleri bu pakete dahil değildir. Yeni içerik otomatik indirilmez. Yalnızca paylaşma hakkına sahip olduğun içerikleri kendin eklersin.

## 🧰 Gereksinimler

| Bileşen | Gereksinim / hedef |
| :--- | :--- |
| Cihaz | Raspberry Pi 4 Model B; 4 GB RAM hedefi |
| İşletim sistemi | Raspberry Pi OS veya Debian gibi Linux dağıtımları |
| Python | 3.9 veya üzeri |
| Otomatik başlatma | systemd |
| Depolama | İçerik boyutuna uygun SD kart veya SSD; sabit 1 TB zorunluluğu yok |
| Ağ | Pi ve istemci cihazların erişebildiği mevcut yerel ağ |

**Wi-Fi notu:** Kurulum erişim noktası oluşturmaz. Önceden yapılandırılmış BilgiKutusu Wi-Fi ağını veya mevcut yerel ağını kullanır. Mevcut nginx, Kiwix ve depolama ayarlarını değiştirmez.

## 🚀 Hızlı başlangıç

Depoyu ZIP olarak indirip çıkar. Proje klasöründe terminal aç:

```bash
bash baslat.sh
```

Pi'nin kendi tarayıcısında **http://127.0.0.1:8091** adresini aç. Durdurmak için **Ctrl+C** kullan. Bu deneme varsayılan olarak yalnızca Pi'nin kendisinden erişilebilir.

## 🔧 Raspberry Pi'de kurulum

Proje klasöründe:

```bash
sudo bash kurulum/kur.sh
```

Uygulama `/opt/bilgikutusu-plus`, içerikler `/srv/bilgikutusu-plus/icerik`, ayarlar `/etc/bilgikutusu-plus/config.json` altına yerleştirilir; `bilgikutusu-plus` hizmeti başlatılır.

1. Telefonunu Pi ile aynı yerel ağa bağla.
2. Pi'de `hostname -I` komutuyla bu ağa ait IP adresini öğren.
3. Tarayıcıda `http://PI_ADRESI:8091` aç; `PI_ADRESI` yerine cihazının adresini yaz.

Kurulum mevcut Plus kurulumu veya kullanılan 8091 portu bulursa durur. Betik güncelleme aracı değildir; mevcut kurulum için önce içerik ve ayarlarını yedekle.

## 💾 SSD üzerindeki içeriği kullanma

`/etc/bilgikutusu-plus/config.json` içindeki `content_dir` değerini paylaşılacak klasörün tam yoluyla değiştir. Örnek değer: `/mnt/BilgiKutusu`.

Kısayollar `Haritalar`, `EgitimVideolari`, `Tarim` ve `Balikcilik` klasör adlarını kullanır. SSD'de örnekleri de görmek istersen ilgili örnek dosyaları bu klasörlere kendin kopyala. Hizmet kullanıcısına okuma ve klasörlere erişim izni ver. SSD bağlıyken:

```bash
sudo systemctl restart bilgikutusu-plus
```

**Paylaşım kapsamı:** Seçilen klasördeki erişilebilir dosyalar yerel ağdaki kullanıcılara sunulur. Kullanıcı girişi yoktur; güvenilen yerel ağ içindir. Kişisel dosyalarını paylaşım klasörüne koyma ve portu internete açma. Web arayüzü dosya yükleme, silme veya düzenleme yapmaz.

## 🗂️ Proje yapısı

| Yol | İçerik |
| :--- | :--- |
| `uygulama/` | Python uygulaması ve yerel web arayüzü |
| `kurulum/` | Kurulum, durum, kaldırma betikleri ve hizmet tanımı |
| `ayarlar/` | Varsayılan yapılandırma |
| `icerik/` | Örnek içerikler ve boş içerik klasörleri |
| `belgeler/` | Kaynak lisans bildirimi ve test notları |
| `testler/` | Otomatik uygulama testleri |
| `baslat.sh` | Yerel deneme başlatıcısı |

## ✅ Durum ve testler

```bash
bash kurulum/durum.sh
python3 -B -m unittest discover -s testler -v
```

Testler dosya erişimi, indirme, medya aralıkları, Türkçe dosya adları, yapılandırma, gizli dosyalar ve klasör dışına erişim kontrollerini kapsar. Doğrulama kapsamı için [test notlarına](belgeler/Test-Notlari.md) bak.

## 🤝 Katkıda bulunma

Hata ve öneriler için bu deponun **Issues** bölümünü kullanabilirsin. Kod katkıları pull request ile gönderilebilir. İçerik katkılarında kaynağı ve paylaşım lisansını belirt; kişisel bilgi, parola veya API anahtarı ekleme.

[Geliştirici](https://github.com/alicanyilmz) · [Bilikon-Project](https://github.com/Bilikon-Project)

## ⚖️ Lisans

Plus paketi **Ücretsiz ve Ticari Olmayan Kullanım Lisansı 1.0** ile sunulur. Kaynak kodu incelenebilir; kullanım ve yeniden dağıtım koşulları [LICENSE](LICENSE) dosyasındadır. Ticari kullanım yazılı izin gerektirir. Bu lisans OSI tanımına uygun bir açık kaynak lisansı değildir.

Temel alınan Go arşivinin özgün lisans bildirimi [belgeler/Go-Kaynak-Lisansi.txt](belgeler/Go-Kaynak-Lisansi.txt) dosyasında korunur. Üçüncü taraf içerikleri kendi lisanslarına tabidir.

---

<div align="center">

**BilgiKutusu Plus · Bilgiye çevrimdışı erişim**  
[Türkçe](README.md) · [English](README.en.md) · [Bilikon-Project](https://github.com/Bilikon-Project)

</div>

<div align="center">

# 📚 BilgiKutusu Plus
### Keep knowledge close, even offline.
**A portable offline knowledge depot for Raspberry Pi 4.**

![Version](https://img.shields.io/badge/version-1.0.0-2563eb?style=for-the-badge)
![Target hardware](https://img.shields.io/badge/Raspberry_Pi_4-4_GB_RAM-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Offline](https://img.shields.io/badge/usage-offline-15803d?style=for-the-badge)

[Türkçe](README.md) · **English**

[Developer: alicanyilmz](https://github.com/alicanyilmz) · [Organization: Bilikon-Project](https://github.com/Bilikon-Project)

</div>

---

> **Development version · 1.0.0**  
> This repository contains the application, installation scripts and small sample resources. **No book collection is included.** The map and video are demonstration content. Operation and load performance on physical Raspberry Pi hardware have not yet been verified.

## 🌿 About

BilgiKutusu Plus lets phones, tablets and computers on the same local network browse and download files without internet access. It is the middle tier of the BilgiKutusu family, extending the Go foundation with selected features and sample content. Its target is **Raspberry Pi 4 Model B with 4 GB RAM**.

The application contains no AI. It uses the Python standard library, with no additional Python packages or cloud account required. Its web interface uses local assets and works offline. The external badges on this GitHub README are separate from the offline portal.

## ✨ Features

| Feature | Current behavior |
| :--- | :--- |
| File browser | Browse folders in a configured local content directory. |
| Search and filters | Filter the current folder by filename and content type. |
| Media | Open browser-supported audio/video files; HTTP byte ranges support seeking. |
| Downloads | Download files to your phone or computer. |
| SSD storage | Point the content directory to a folder on an SSD. |
| Automatic startup | Run as a service on Linux systems using systemd. |

## 📦 Included content

| Section | Included | Scope |
| :--- | :--- | :--- |
| Maps | Türkiye city-location image | **Sample coordinate map** showing approximate locations of nine city centers; not a detailed map of Türkiye. |
| Educational videos | Map directions | **24-second sample video** with written explanations of directions, latitude and longitude. |
| Agriculture | Planting log CSV | Downloadable template to edit on your own device. |
| Fishing | Observation log CSV | Downloadable template to edit on your own device. |
| Documents | Getting-started text | Short usage notes. |
| Books | Empty content directory | **No books or e-book archive are included.** |
| Images | Empty content directory | Space for your own images. |

Wikipedia/ZIM archives, Kiwix, films, TV series and large educational collections are not bundled. No new content is downloaded automatically. Add only resources you have permission to share.

## 🧰 Requirements

| Component | Requirement / target |
| :--- | :--- |
| Hardware | Raspberry Pi 4 Model B; 4 GB RAM target |
| Operating system | Linux, such as Raspberry Pi OS or Debian |
| Python | 3.9 or newer |
| Service installation | systemd |
| Storage | SD card or SSD sized for your content; no fixed 1 TB requirement |
| Network | An existing local network reachable by the Pi and client devices |

The installer **does not create a Wi-Fi access point**. It uses your existing BilgiKutusu Wi-Fi network or another configured local network. Existing nginx, Kiwix and storage settings are left unchanged.

## 🚀 Quick start

Download and extract the repository ZIP, then open a terminal in the project directory:

```bash
bash baslat.sh
```

Open **http://127.0.0.1:8091** in the Pi's own browser. Press **Ctrl+C** to stop. This configuration listens only on localhost by default.

## 🔧 Install on Raspberry Pi

From the project directory:

```bash
sudo bash kurulum/kur.sh
```

The installer places the application in `/opt/bilgikutusu-plus`, content in `/srv/bilgikutusu-plus/icerik`, and configuration in `/etc/bilgikutusu-plus/config.json`. It starts the `bilgikutusu-plus` service.

1. Connect your phone to the same local network as the Pi.
2. Run `hostname -I` on the Pi and choose its address on that network.
3. Open `http://PI_ADDRESS:8091`, replacing `PI_ADDRESS` with the device's address.

Installation stops if it finds an existing Plus installation or port 8091 is in use. The installer is not an upgrade tool; back up your content and configuration before changing an existing installation.

## 💾 Use an SSD

Change `content_dir` in `/etc/bilgikutusu-plus/config.json` to the absolute path of the folder you want to share, for example `/mnt/BilgiKutusu`.

Interface shortcuts use the folder names `Haritalar`, `EgitimVideolari`, `Tarim` and `Balikcilik`. Copy the bundled samples into the corresponding SSD folders yourself if needed. The service user needs read and directory traversal permissions. With the SSD mounted:

```bash
sudo systemctl restart bilgikutusu-plus
```

**Sharing scope:** Accessible files in the configured directory are shared with local network users. The portal has no user login and is intended for a trusted local network. Keep personal files outside the shared directory and do not expose the port to the internet. The interface does not upload, delete or edit files.

## 🗂️ Project layout

| Path | Purpose |
| :--- | :--- |
| `uygulama/` | Python application and local web interface |
| `kurulum/` | Install, status, uninstall scripts and service definition |
| `ayarlar/` | Default configuration |
| `icerik/` | Sample resources and empty content folders |
| `belgeler/` | Source license notice and validation notes |
| `testler/` | Automated application tests |
| `baslat.sh` | Local quick-start script |

## ✅ Status and validation

```bash
bash kurulum/durum.sh
python3 -B -m unittest discover -s testler -v
```

Tests cover file access, downloads, media byte ranges, Turkish filenames, configuration, hidden files and directory traversal controls. See [validation notes](belgeler/Test-Notlari.md) for scope and hardware limitations.

## 🤝 Contributing

Use this repository's **Issues** tab for bug reports and suggestions. Submit code contributions through pull requests. Include the source and redistribution license for content contributions. Do not commit personal information, passwords or API keys.

[Developer](https://github.com/alicanyilmz) · [Bilikon-Project](https://github.com/Bilikon-Project)

## ⚖️ License

The package uses **BilgiKutusu Plus Free and Non-Commercial Use License 1.0**. The source is available to inspect; usage and redistribution conditions are defined in [LICENSE](LICENSE). Commercial use requires written permission. This is not an OSI-compliant open-source license.

The original license notice from the source Go archive is retained in [belgeler/Go-Kaynak-Lisansi.txt](belgeler/Go-Kaynak-Lisansi.txt). Third-party content remains subject to its own licenses.

---

<div align="center">

**BilgiKutusu Plus · Offline access to knowledge**  
[Türkçe](README.md) · [English](README.en.md) · [Bilikon-Project](https://github.com/Bilikon-Project)

</div>

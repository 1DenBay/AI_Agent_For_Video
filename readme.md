### **Markdown**# 🚀 AI Video Agent (v1.0)

**Tek bir komutla fikirlerinizi viral videolara dönüştüren otonom içerik üretim ve dağıtım fabrikası.**

***TÜM SİSTEM SIFIRDAN ŞAHSIMA AİTTİR***

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Stable-green)
![AI](https://img.shields.io/badge/AI-Powered-purple)

### 📖  Hakkında (Information)

Bu proje, uçtan uca otonom video üretimi sağlayan bir yapay zeka ajanıdır. Kullanıcıdan sadece bir **konu başlığı** alır ve geriye kalan her şeyi (senaryo, seslendirme, stok video bulma, montaj, altyazı ve sosyal medya paylaşımı) kendisi halleder.

YouTube Shorts ve TikTok için optimize edilmiştir. İçerisinde, TikTok'un bot korumalarını aşabilen özel geliştirilmiş **Browser Automation Engine** bulunmaktadır.✨ Özellikler

### 🧠 Üretim Hattı (Production)

* **Akıllı Senaryo (Brain Agent):** Google Gemini 2.5 Flash modeli ile viral potansiyeli yüksek senaryolar ve görsel arama terimleri üretir.
* **Profesyonel Ses (Voice Agent):** Google TTS teknolojisi ile akıcı ve doğal seslendirme yapar.
* **Otomatik Medya (Media Agent):** Pexels API üzerinden senaryoya en uygun stok videoları bulur ve indirir.
* **Dinamik Montaj (Editor Agent):** MoviePy ve FFmpeg kullanarak ses ve görüntüyü senkronize eder, 3.5 saniyelik dinamik kesimler yapar.
* **Yapay Zeka Altyazı (Subtitler Agent):** OpenAI Whisper modeli ile sesi analiz eder ve saniyesi saniyesine "hard-coded" altyazı ekler.

### 📡 Dağıtım Hattı (Distribution)

* **YouTube Uploader:** Resmi YouTube Data API (OAuth2) kullanarak videoları otomatik olarak başlık, açıklama ve etiketlerle yükler.
* **TikTok Auto-Publisher:**
  * `undetected-chromedriver` ile bot korumalarını aşar.
  * Çerez yönetimi (`pickle`) ile oturumu hatırlar.
  * **Dedektif Modu:** Sayfa yapısı değişse bile butonları tarayarak doğru etkileşimi bulur.
  * **JS Event Dispatcher:** Görünmez katmanları (overlay) aşarak tıklama işlemini garantiye alır.

---

## 🛠️ Kurulum

Projeyi yerel makinenizde çalıştırmak için adımları takip edin.

### 1. Projeyi Klonlayın

```bash
git clone [https://github.com/KULLANICI_ADINIZ/ai-video-agent.git](https://github.com/KULLANICI_ADINIZ/ai-video-agent.git)
cd ai-video-agent
```

### 2. Sanal Ortamı Oluşturun

**Bash**

```
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin

**Bash**

```
pip install -r requirements.txt
```

*(Gerekli kütüphaneler: `google-genai`, `moviepy`, `openai-whisper`, `selenium`, `undetected-chromedriver`, `google-auth-oauthlib` vb.)*

### 4. Çevre Değişkenlerini Ayarlayın (.env)

Proje ana dizininde `.env` dosyası oluşturun ve API anahtarlarınızı girin:

**Kod snippet'i**

```
GEMINI_API_KEY=senin_gemini_keyin
PEXELS_API_KEY=senin_pexels_keyin
```

*> Not: YouTube yüklemesi için `client_secret.json` dosyasını proje ana dizinine eklemelisiniz.*

---

## 🚀 Kullanım

Fabrikayı çalıştırmak için tek komut yeterlidir:

**Bash**

```
python main.py
```

Program başladığında sizden bir konu isteyecektir:

**Plaintext**

```
--- YENİ GÖREV ---
Video Konusu Nedir? (Çıkış için 'q'): Ör. Kara delikler nasıl oluşur
```

Arkanıza yaslanın! ☕ Sistem sırasıyla senaryoyu yazacak, videoyu hazırlayacak, YouTube'a yükleyecek ve TikTok için tarayıcıyı açıp paylaşımı yapacaktır.

---

## 📂 Proje Mimarisi

**Plaintext**

```
ai-video-agent/
├── agents/                 # İçerik Üretim Ajanları
│   ├── agent_brain.py      # Senaryo (Gemini)
│   ├── agent_voice.py      # Ses (TTS)
│   ├── agent_media.py      # Görsel (Pexels)
│   ├── agent_editor.py     # Montaj (MoviePy)
│   └── agent_subtitler.py  # Altyazı (Whisper)
├── distributors/           # Dağıtım Ajanları
│   ├── agent_youtube.py    # YouTube API
│   └── agent_tiktok.py     # TikTok Otomasyonu (V12)
├── media_files/            # İndirilen stok videolar (Geçici)
├── final_videos/           # Hazır videolar
├── main.py                 # Ana Yönetici (Orkestra Şefi)
├── requirements.txt        # Kütüphaneler
└── README.md               # Dokümantasyon
```

---

## ⚠️ Önemli Notlar

* **TikTok Otomasyonu:** TikTok dağıtımı sırasında otomatik bir Chrome penceresi açılacaktır. İşlem bitene kadar bu pencereye  **müdahale etmeyiniz** . Bot, "Paylaş" butonunu bulup tıklayacaktır.
* **API Kotaları:** Pexels ve Gemini ücretsiz katmanlarının limitlerine dikkat ediniz.
* **FFmpeg:** Sisteminizde FFmpeg kurulu olmalıdır (MoviePy genellikle otomatik kurar).

## 🗺️ Yol Haritası (v1.1)

* [X] Medya Ajanı için "Akıllı Yedekleme" (Video bulunamazsa alternatif kelime arama).
* [ ] Farklı ses seçenekleri (ElevenLabs entegrasyonu).
* [ ] Instagram Reels desteği.

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için önce tartışma başlatınız.

## 👤 İletişim

Bu proje **Deniz BAYAT** tarafından geliştirilmiştir. *-Teşekkürler, Saygılar*

* **LinkedIn**: linkedin.com/in/denizbayat1/
* **GitHub**: github.com/1DenBay
* **Medium**: medium.com/@denizbyat
* **Email**: [denizbyat@gmail.com](mailto:denizbyat@gmail.com)

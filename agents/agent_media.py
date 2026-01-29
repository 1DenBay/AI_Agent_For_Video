import os
import requests
from dotenv import load_dotenv
import random

load_dotenv()

# video aramalarında son çare olarak kullanılacak genel yedek kelimeler
GLOBAL_BACKUPS = [
    "Abstract background", "Blue particles", "Technology connection", 
    "Time lapse city", "Nature landscape", "Galaxy stars", 
    "Cinematic lighting", "Slow motion water"
]

# pexels api anahtarı .env dosyasından alınır
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if not PEXELS_API_KEY:
    raise ValueError("HATA: PEXELS_API_KEY .env dosyasında bulunamadı!")

# Videoları indireceğimiz klasörü oluşturur
MEDIA_DIR = "media_files"
if not os.path.exists(MEDIA_DIR): 
    os.makedirs(MEDIA_DIR)


"""
    Pexels API'sinde verilen kelimeye göre DİKEY (Portrait) video arar.
    İlk sonucun indirme linkini döner.
"""
def search_video(query):
    
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": 1,           # Sadece en iyi 1 videoyu getir
        "orientation": "portrait", # TikTok/Reels formatı (Dikey)
        "size": "medium"         # Çok büyük dosyalarla uğraşmayalım (HD yeterli)
    }

    print(f"🔍 Pexels'de aranıyor: '{query}'...")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                # Videonun indirme linkini al
                video_url = data['videos'][0]['video_files'][0]['link']
                return video_url
            else:
                print(f"⚠️ '{query}' için video bulunamadı.")
                return None
        else:
            print(f"❌ API Hatası: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"❌ Bağlantı Hatası: {e}")
        return None


"""
    V1.1 - Akıllı Arama Yöneticisi:
    Tam kelimeyi arar.- Bulamazsa kelimeleri parçalayıp (sondan başa) arar.
    Yine bulamazsa GLOBAL_BACKUPS listesinden rastgele bir video seçer. (boş kalmasın diye)
"""
def smart_search_manager(query):
    # 1- önce normal arama yapılır 
    url = search_video(query)
    if url: return url

    # 2- Kelime Parçalama (Bulunuş anahtar kelimeleri parçalar)
    # "Dark Forest Scary" -> Önce "Scary", sonra "Forest", sonra "Dark"
    words = query.split() # boşluklardan parçala
    if len(words) > 1: # birden fazla kelime varsa parçalayarak dene
        print(f"   ⚠️ Tam eşleşme yok. Kelimeler parçalanarak deneniyor...")
        for word in reversed(words): # sondan başa doğru dene
            if len(word) > 2: # "at", "in" gibi kısa kelimeleri, bağlaçları filan geç
                print(f"   🔄 Alternatif aranıyor: '{word}'")
                url = search_video(word) # parçalanmış kelime ile ara
                if url:
                    print(f"   ✅ Alternatif bulundu: '{word}'")
                    return url

    # 3- global Yedek (Son Çare)
    print(f"   ❌ Kritik: '{query}' için hiçbir görsel bulunamadı.")
    backup = random.choice(GLOBAL_BACKUPS) # rastgele yedek kelime seç (en başlta liste içinde tanımlandı)
    print(f"   🆘 Acil durum yedeği devreye giriyor: '{backup}'")
    return search_video(backup) # rastgele seçilen yedek kelime ile ara


"""
    Linkteki videoyu bilgisayara (media_files klasörüne) indirir.
"""
def download_video(url, filename):
    
    filepath = os.path.join(MEDIA_DIR, filename)

    print(f"⬇️ İndiriliyor: {filename}...")
    
    try:
        # stream=True ile büyük dosyaları parça parça indiririz. normalde direkt rame indirir. (RAMe indirme hemen işliycez demek)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f: # Write Binary (wb) modunda aç. yani bu metin değil ikili dosya demek bozuk açmasın
                for chunk in r.iter_content(chunk_size=8192): # 8KB parça parça indir. bi anda indirmesin diye.
                    f.write(chunk) # dosyayı diske yaz
        
        print(f"✅ İndirme Tamamlandı: {filepath}")
        return filepath

    except Exception as e:
        print(f"❌ İndirme Hatası: {e}")
        return None


"""
    Dışarıdan çağrılan ana fonksiyon.
    Kelime listesini alır, hepsini indirir ve dosya yollarını döner.
"""
def get_media_files(keywords): # beyinden gelen kelimleri alacak
    
    # Eski videoları temizler.
    print("🧹 Eski videolar temizleniyor (Sahne hazırlanıyor)...")
    for f in os.listdir(MEDIA_DIR):
        if f.endswith(".mp4"):
            try:
                os.remove(os.path.join(MEDIA_DIR, f))
            except Exception as e:
                print(f"⚠️ Silinemedi: {f} - {e}")

    downloaded_paths = []
    
    for i, keyword in enumerate(keywords):
        video_url = smart_search_manager(keyword) # v1.1 yeni akıllı arama yöneticisi
        
        if video_url:
            # Dosya ismini temizle ve numaralandır (video_0.mp4, video_1.mp4)
            safe_name = f"video_{i}.mp4"
            path = download_video(video_url, safe_name)
            if path:
                downloaded_paths.append(path)
    
    return downloaded_paths


# --- BİRİM TEST ---
if __name__ == "__main__":
    # Test kelimeleri (Brain'den gelmiş gibi)
    test_keywords = ["dark forest", "clock ticking", "stormy sky"]
    
    paths = get_media_files(test_keywords)
    
    print("\n--- SONUÇ RAPORU ---")
    print(f"İndirilen Dosyalar: {paths}")
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv() # .env dosyasını yükler

api_key = os.getenv("GEMINI_API_KEY") # .env dosyasından API anahtarını alır
if not api_key:
    raise ValueError("HATA: GEMINI_API_KEY .env dosyasında bulunamadı!")

try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"⚠️ Yapılandırma hatası: {e}")


"""
    Bu fonksiyon Google hesabındaki tüm modelleri tarar.
    En ucuz ve hızlı (Flash) modeli otomatik seçer.
    Gelecekte yeni model çıkarsa onu bulur. - Sabit model kullanım dışı kaldığında hataların önüne geçer sürdürülebilir kod için.
"""
def select_dynamic_model():
    
    print("ℹ️ En uygun ücretsiz/hızlı model aranıyor...")
    
    # modelleri kategorik olarak ayırmak için listeler ileride duruma göre istenen kategori seçilebilir
    flash_models = []
    pro_models = []
    other_models = []

    try:
        # Tüm modelleri listeler
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name
                # Kategorilere ayırır
                if "flash" in name.lower():
                    flash_models.append(name)
                elif "pro" in name.lower():
                    pro_models.append(name)
                else:
                    other_models.append(name)
        
        # Öncelik: Flash modellerin (genelde ücretsiz,ucuz ve hızlı)
        if flash_models:
            # Listeyi ters çevirip (genelde yeniler sonda olur) veya en güncel görüneni alabiliriz.
            # Şimdilik "latest" içeren varsa onu, yoksa 2.5, yoksa 1.5 diye bakarız.
            # Ama en basiti Bulduğun ilk Flash iş görür.
            
            # Küçük bir zeka: 'exp' (deneysel) olmayanları tercih et
            stable_flash = [m for m in flash_models if "exp" not in m and "preview" not in m]
            if stable_flash:
                selected = stable_flash[0] # İlk stabil Flash
            else:
                selected = flash_models[0] # Yoksa herhangi bir Flash
                
            print(f"✅ OTO-PİLOT: Flash modeli seçildi -> {selected}")
            return selected

        # Pro modelleri (Daha zeki ama kotalı olabilir, fazla maliyete gerek yok. üst seviye videoalr istenirse keyfi olarak açılabilir.)
        if pro_models:
            selected = pro_models[0]
            print(f"⚠️ Pro seçildi -> {selected}")
            return selected
            
        # Ne varsa (alternatiftir son çare)
        if other_models:
            selected = other_models[0]
            print(f"⚠️ Özel model seçildi -> {selected}")
            return selected
            
    except Exception as e:
        print(f"❌ Model tarama hatası: {e}")
    
    # Her şey patlarsa kör atış yap (Son çare - genelde bu çalışsın garanti olsun)
    return "models/gemini-2.5-flash"

# Modeli bir kez seç ve hafızaya kaydet (Her fonksiyonda tekrar taramasın, sisteme zaman-maliyet kaybı yaşatmasın)
CURRENT_MODEL_NAME = select_dynamic_model()


"""
    Verilen konuyu alır, Gemini'ye İngilizce viral bir senaryo ve görsel arama terimleri hazırlatır. yani Prompt (İstem) Mühendisliği yapar.
    Geminiye çıktıyı "JSON" formatında verecek.
"""
def generate_video_plan(topic_tr): # Türkçe konu alır
    
    prompt = f"""
    You are a viral content creator for TikTok and YouTube Shorts.
    Topic: '{topic_tr}'
    
    Create a highly engaging, 30-50 second script about this topic in English.
    The script must be captivating (e.g., "Did you know that...", "Here is a dark fact...").
    
    Also, provide 3 specific, simple search keywords (English) to find background stock videos for this script (e.g., "dark forest", "clock", "man thinking").
    
    Strictly output ONLY a valid JSON object in this format (no markdown, no extra text):
    {{
        "title": "A catchy short title",
        "script": "The full spoken text of the video...",
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
    """
    
    print(f"🧠 Beyin çalışıyor: '{topic_tr}' konusu işleniyor...")
    
   
    try:
        # listendeki mevcut model kullanılıyor
        model = genai.GenerativeModel(CURRENT_MODEL_NAME)
        
        # İçerik üret
        response = model.generate_content(prompt)
        
        # Yanıtı temizle ve JSON'a çevir
        # Bazen model ```json ile başlar, bazen başlamaz. Hepsini temizliyoruz.
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Olası tırnak hatalarına karşı basit bir önlem
        try:
            data = json.loads(clean_text)
            return data
        except json.JSONDecodeError:
            # Eğer temizlemesine rağmen bozuksa, ham metni gösterelim
            print("HATA: JSON ayrıştırılamadı. Gelen veri:")
            print(clean_text)
            return None

    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
        return None

# --- TEST BLOĞU ---
if __name__ == "__main__":
    test_konu = "The Infinite Hotel Paradox (Sonsuz Otel Paradoksu)"
    sonuc = generate_video_plan(test_konu)
    
    if sonuc:
        print("\n✅ BAŞARILI! İşte üretilen plan:")
        print(json.dumps(sonuc, indent=4, ensure_ascii=False))
    else:
        print("\n❌ Başarısız oldu.")
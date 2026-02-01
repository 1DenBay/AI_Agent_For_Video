import os
import json
import re
import random
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
    
    Create a valid JSON output based on these rules:
    
    1. "script": A 30-50 sec engaging, conversational ENGLISH script.
        IMPORTANT: The script must be a SINGLE LINE string. Do NOT use real line breaks (newlines). Use spaces only.
    2. "title": A viral, clickbait ENGLISH title.
    3. "description": A short, engaging ENGLISH description.
    4. "hashtags": 5-7 popular hashtags (comma separated string).
    5. "keywords": Exactly 8 specific ENGLISH keywords for stock video search (List of strings).

    OUTPUT FORMAT (Strictly JSON):
    {{
        "script": "Did you know that... Then imagine this... Finally...",
        "title": "You won't believe this!",
        "description": "Watch this mind-blowing fact...",
        "hashtags": "#facts, #mystery",
        "keywords": ["word1", "word2", "word3", "word4", "word5", "word6", "word7", "word8"]
    }}
    """
    
    print(f"🧠 Beyin çalışıyor: ({CURRENT_MODEL_NAME})... Konu: {topic_tr}")
    
   
    try:
        # listendeki mevcut model kullanılıyor
        model = genai.GenerativeModel(CURRENT_MODEL_NAME)
        
        # İçerik üret
        response = model.generate_content(prompt)
        
        # Temizlik (v1.1 artık temizlik fonksiyonu ile yapılıyor)
        cleaned_json = clean_json_text(response.text)
        #Eğer Gemini yine de satır atladıysa, JSON patlamasın diye strict=False yapıyoruz
        # ve olası kontrol karakterlerini temizliyoruz.
        try:
            data = json.loads(cleaned_json, strict=False)
        except json.JSONDecodeError:
            # Hata verirse son çare: Python tarafında satır sonlarını temizle
            print("⚠️ JSON formatı bozuk geldi, onarılmaya çalışılıyor...")
            # Bu biraz riskli ama basit tırnak içi enterları yakalamaya çalışır
            fixed_json = cleaned_json.replace("\n", " ") 
            data = json.loads(fixed_json, strict=False)
        
        # Metadata'yı dosyaya kaydet
        with open("video_metadata.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print("✅ İçerik Paketi Hazırlandı ve 'video_metadata.json' dosyasına kaydedildi.")
        return data

    except json.JSONDecodeError:
        print(f"❌ JSON Hatası: Gelen veri bozuk. \n{response.text}")
        return None
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def clean_json_text(text):
    """Gemini'den gelen yanıtı temizler ve saf JSON metni yapar."""
    text = text.strip()
    # Markdown kod bloklarını temizle
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    return text.strip()


"""
    Sadece aşağıdaki listeden rastgele bir konu seçer ve döndürür.
"""
def pick_random_topic_from_list():
    
    
    # Buraya istediğin konuları ekleyebilirsiniz
    topic_pool = [
        "Unsolved Space Mysteries",   # Uzay Gizemleri
        "Dark History Facts",         # Karanlık Tarih
        "Psychological Paradoxes",    # Psikolojik Paradokslar
        "Future Technology Scary",    # Ürkütücü Gelecek Teknolojileri
        "Deep Ocean Creatures",       # Okyanus Canlıları
        "Simulation Theory Evidence", # Simülasyon Teorisi
        "Human Body Weird Facts",     # İnsan Vücudu
        "Ancient Civilizations"       # Antik Uygarlıklar
    ]
    
    # Listeden rastgele bir tane seç
    selected_topic = random.choice(topic_pool)
    
    print(f"\n🎲 Havuzdan Rastgele Seçilen Konu: {selected_topic}")
    return selected_topic


# --- birim test ---
if __name__ == "__main__":
    
    # 1. Adım: Listeden rastgele konuyu seç (AI YOK)
    secilen_konu = pick_random_topic_from_list()
    
    # 2. Adım: Seçilen konuyu senaryo üretmesi için AI'ya ver
    if secilen_konu:
        sonuc = generate_video_plan(secilen_konu)
        
        if sonuc:
            print("\n--- SONUÇ ---")
            print(f"Başlık: {sonuc.get('title')}")
            print(f"Senaryo (Kısaca): {sonuc.get('script')[:50]}...")
            print(f"Anahtar Kelimeler: {sonuc.get('keywords')}")
        else:
            print("❌ Video planı oluşturulamadı.")
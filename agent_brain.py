import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() # .env dosyasını yükler

api_key = os.getenv("GEMINI_API_KEY") # .env dosyasından API anahtarını alır
if not api_key:
    raise ValueError("HATA: GEMINI_API_KEY .env dosyasında bulunamadı!")

client = genai.Client(api_key=api_key) # Gemini API istemcisi oluşturur. Localden googla tünel.


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
        # GÜNCELLEME: Senin listendeki mevcut model kullanılıyor
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7 # Yaratıcılık seviyesi (0.0 robotik - 1.0 çılgınca)
            )
        )
        
        # Yanıtı temizle ve JSON'a çevir
        # Bazen model ```json ile başlar, bazen başlamaz. Hepsini temizliyoruz.
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Olası tırnak hatalarına karşı basit bir önlem (opsiyonel ama güvenli)
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
import asyncio
# asyncio kütüphanesi, asenkron işlemler için gereklidir. Pythonda Dosyalar senkron yani satır satır okunarak çalışır
# ancak bu ses dosyası gibi veri indirmeli dosyalarda bekleme süreleri olabilir. Bu yüzden asenkron programlama kullanılır. Yani dosya inerken sen bekleme demektir.
import edge_tts # azure tabanlı metin-okuma kütüphanesi. API siz ve ücretsizdir.

# KULLANILACAK SES:
# "en-US-ChristopherNeural" -> Belgesel, Ciddi, Derin Erkek Sesi
VOICE = "en-US-ChristopherNeural"


"""
    Arka planda çalışan asenkron işçi.
"""
async def _create_voice_file(text, output_file): # fonksiyon başına async anahtar kelimesi ile asenkron fonksiyon tanımlanır.
    # Ayrıca ek bilgi: fonksiyon ismi "_" ile başlıyorsa bu fonksiyonun modül dışından çağrılmaması gerektiği anlamına gelir.
    
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_file) # sihirli kelime await, bu satırda işlem tamamlanana kadar bekle demektir. yoksa fonksiyon hemen devam eder ve aşağıda dosya inmediğinden hata verir.


"""
    Dış dünyadan çağrılan yönetici fonksiyon. İleride main.py dosyası direkt burayı çağıracak. Asenkron fonksiyonu çağıramaz dili uymaz çünkü main normal olarak senkron çalışacak
    Asenkron işlemi başlatır, bitmesini bekler ve sonucu döner.
"""
def generate_audio_file(text, filename="final_audio.mp3"):
    
    print(f"🎙️ Seslendirmen Sahneye Çıktı: '{filename}' hazırlanıyor...")
    
    try:
        # Yeni bir olay döngüsü (Event Loop) yaratılir. Asenkron işlemler bu döngüde çalışır.
        # Böyle bir kontrol altında döngü yaratılıyor çünkü asenkron için sistemi bekletmek gerekir.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # İşin bitmesi için sistemi bekletir.
        loop.run_until_complete(_create_voice_file(text, filename))
        
        # Temizlik
        loop.close()
        
        print(f"✅ Ses Kaydı Başarılı: {filename}")
        return True

    except Exception as e:
        print(f"❌ Seslendirme Hatası: {e}")
        return False


# --- TEST BLOĞU ---
# Sadece bu dosya çalıştırıldığında devreye girer.
if __name__ == "__main__":
    test_metni = "This is a test. The Infinite Hotel Paradox is one of the most fascinating concepts in mathematics." # ses dosyasının ne söyleyeceği metin
    
    basari = generate_audio_file(test_metni, "test_voice.mp3")
    
    if basari:
        print("Test tamamlandı. Lütfen klasördeki 'test_voice.mp3' dosyasını dinleyin.")
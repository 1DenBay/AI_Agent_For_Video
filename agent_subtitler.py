import whisper
import os
import platform
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip # video düzenleme kütüphanesi
from moviepy.config import change_settings


# İşletim sistemine göre font seçimi. aşağıda kullanılacak
def get_font():
    system_name = platform.system()
    if system_name == "Darwin": # Mac
        return "Helvetica-Bold"
    elif system_name == "Windows":
        return "Arial-Bold"
    else: # Linux vs
        return "DejaVu-Sans-Bold"
    

def add_subtitles(video_path, audio_path, output_path): # video , ses dosya yollarını alır
    print("📝 Altyazı Ajanı Devrede: Ses dinleniyor...")
    
    try:
        # 1. WHISPER MODELİNİ YÜKLE (İlk çalışmada, tek seferlik 150MB modeli indirir)
        # 'base' modeli hız/performans için idealdir. tiny var çok hızlı ama aptal, large var çok iyi ama yavaş.
        model = whisper.load_model("base")
        
        # 2. TRANSKRİPSİYON (Sesi metne dök)
        print("   👂 Ses analiz ediliyor (Whisper AI)...")
        result = model.transcribe(audio_path) # videodaki sesi metne döker
        segments = result['segments'] # videoda o an ne denildiğini ve zamanlamasını alır hangi zamanda ne denildiği bilgisini tutar.
        
        # 3. VİDEOYU YÜKLE
        video = VideoFileClip(video_path)
        
        subtitle_clips = []
        
        # 4. ALTYAZILARI OLUŞTUR
        print(f"   ✍️ {len(segments)} parça altyazı oluşturuluyor...")
        
        for segment in segments: # her altyazının ekranda kalacağı süreyi belirler
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip() # bazen gereksiz alt boşluklar olur, onları temizler
            
            # TikTok Tarzı Altyazı Ayarları (sarı, kalın ve siyah kenarlıklı)
            txt_clip = TextClip(
                text, 
                fontsize=70, 
                color='yellow', 
                font=get_font(),
                stroke_color='black', 
                stroke_width=3, # kenarlık kalınlığı
                method='caption', # Metni ekrana sığdırır, gerekirse alt satıra geçer. metin ekrandan taşmasın diye
                size=(video.w * 0.8, None) # Genişlik ekranın %80'i olsun, yükseklik otomatik olsun, caption metodun sınırları içinde
            )
            
            # Zamanlama ve Pozisyon. yazılar ile videoları eşleştirir
            txt_clip = txt_clip.set_start(start_time).set_end(end_time)
            txt_clip = txt_clip.set_position(('center', 'center')) # Tam ortada (İstersen ('center', 1400) yapıp aşağı alabiliriz)
            
            subtitle_clips.append(txt_clip)
            
        # 5. BİRLEŞTİRME (Video + Altyazılar)
        final_video = CompositeVideoClip([video] + subtitle_clips)
        
        # 6. KAYDET
        print(f"   💾 Altyazılı video kaydediliyor: {output_path}")
        final_video.write_videofile(
            output_path, 
            fps=video.fps,
            codec='libx264', 
            audio_codec='aac',
            threads=4,
            logger='bar'
        )
        
        return output_path

    except Exception as e:
        print(f"❌ Altyazı Hatası: {e}")
        return None

# --- TEST ---
if __name__ == "__main__":
    test_video = "final_videos/shorts_1769255684.mp4" 
    test_audio = "voice_1769253271.mp3"  # Bu dosya ana dizinde olmalı
    output_test = "test_altyazili_sonuc.mp4"
    
    print("🧪 Test Başlıyor...")
    
    if os.path.exists(test_video) and os.path.exists(test_audio):
        add_subtitles(test_video, test_audio, output_test)
        print("\n✅ Test Bitti! 'test_altyazili_sonuc.mp4' dosyasını kontrol et.")
    else:
        print(f"❌ Dosyalar bulunamadı!\nVideo: {test_video}\nSes: {test_audio}")
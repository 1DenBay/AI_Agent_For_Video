import whisper
import os
import platform
import subprocess
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip # video düzenleme kütüphanesi



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

    video_path = os.path.abspath(video_path)
    audio_path = os.path.abspath(audio_path)
    output_path = os.path.abspath(output_path)

    # Geçici sessiz video dosyası ismi (Ana dosyadan ayrı, yoksa altyazı ve ses beraber olunca sesi atıyor)
    temp_silent_video = output_path.replace(".mp4", "_temp_sessiz.mp4")

    # Temizlik: Eğer eskiden kalma temp dosyası varsa sil
    if os.path.exists(temp_silent_video):
        os.remove(temp_silent_video)
    
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
        final_video_silent = CompositeVideoClip([video] + subtitle_clips)

        print(f"   💾 Görüntü işleniyor (Ses daha sonra eklenecek)...")
        final_video_silent.write_videofile(
            temp_silent_video,
            fps=video.fps,
            codec='libx264', 
            audio=False, #  Sesi kapattık, hatayı önledik yoksa altyazı gelince sesi atıyor
            threads=4,
            logger='bar'
        )


        # 4. FFMPEG İLE SESİ DIŞARIDAN ÇAK (Kalite Kaybı Yok)
        # Sesi Python değil, FFmpeg birleştiriyor. python birlşetirince sesi atıyordu.
        print("   🔨 FFmpeg ile ses videoya kayıpsız ekleniyor...")
        
        command = [
            "ffmpeg", "-y",
            "-i", temp_silent_video, # Görüntü
            "-i", audio_path,        # Ses
            "-c:v", "copy",          # Görüntüyü elleme
            "-c:a", "libmp3lame",    # AAC yerine MP3 (Daha uyumlu)
            "-b:a", "192k",          # Ses kalitesi
            "-map", "0:v:0",         # Görüntü akışı
            "-map", "1:a:0",         # Ses akışı
            output_path
        ]
        
        # Komutu çalıştır
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path) / (1024*1024)
            print(f"   ✅ Dosya oluşturuldu: {size:.2f} MB")
            
        # TEMİZLİK
        if os.path.exists(temp_silent_video):
            os.remove(temp_silent_video)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Hatası:\n{e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"❌ Genel Hata: {e}")
        return None

# --- TEST ---
if __name__ == "__main__":
    pass
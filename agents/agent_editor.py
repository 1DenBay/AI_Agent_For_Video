import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips # video düzenleme kütüphanesi

OUTPUT_DIR = "final_videos"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# pexels den aldığımız videolar farklı çözünürlükte olabilir. Biz hepsini TikTok/Reels formatına (1080x1920) getireceğiz. Birleştirmede de hata verir standardizasyon yapmazsak.
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


def create_final_video(audio_path, video_paths, output_filename="shorts_final.mp4"): # ses ve görüntü yollarını alır
    print("🎬 Kurgu Masası çalışıyor...")

    final_clip = None
    audio_clip = None

    try:
        # SES YÜKLEME
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Ses dosyası yok: {audio_path}")
            
        audio_clip = AudioFileClip(audio_path)      # ses dosyalarını yükler
        total_duration = audio_clip.duration        # saniye cinsinden toplam ses süresi. Bu ses dosyasına göre olacak. ses dosyası kaç saniye ise görüntü o kadar olacak.
        print(f"🔊 Ses Süresi: {total_duration:.2f} saniye")


        # VİDEO PLANLAMASI
        CLIP_DURATION = 3.5  # Her klip maksimum 3.5 saniye
        print(f"✂️ Hızlandırma Modu: Her sahne {CLIP_DURATION} saniye olacak.")


        # VİDEOLARI HAZIRLA
        processed_clips = [] # işlenmiş klipleri tutacak liste
        current_duration = 0
        # Videoları karıştıracak hep aynı sırayla gitmesin
        random.shuffle(video_paths)
        
        # Böylece süre dolana kadar sıradakini çekeriz - Elimizdeki videoları sonsuz döngüye alalım (Iterator)
        video_pool = video_paths * 10

        for v_path in video_pool:
            # Hedef süreye ulaştıysak döngüyü kır
            if current_duration >= total_duration:
                break

            try:
                clip = VideoFileClip(v_path) # görüntüleri yüklüyoruz 
                clip = clip.without_audio() # sonrasında bizim dublajı bastırmaması için görüntü seslerini atıyoruz
                
                # Resize ile görüntüyü en üstte belirledğimiz çözünürlüğe getiriyoruz
                if clip.w != TARGET_WIDTH or clip.h != TARGET_HEIGHT:
                    clip = clip.resize(newsize=(TARGET_WIDTH, TARGET_HEIGHT))
                
                # RASTGELE KESİM
                # Videonun hep başını değil, ortasını vs. alalım.
                if clip.duration > CLIP_DURATION:
                    # Videonun sonundan pay bırakarak rastgele başlangıç seç
                    max_start = clip.duration - CLIP_DURATION
                    start_t = random.uniform(0, max_start)
                    clip = clip.subclip(start_t, start_t + CLIP_DURATION)
                else:
                    # Video kısaysa olduğu gibi al (loop yaparsak bozulabilir, kısa kalsın)
                    pass
                
                processed_clips.append(clip)
                current_duration += clip.duration
                print(f"   ✅ Eklendi: {os.path.basename(v_path)} (Süre: {clip.duration:.2f}s)")

            except Exception as e:
                print(f"   ❌ Hata ({os.path.basename(v_path)}): {e}")

        if not processed_clips:
            raise ValueError("Video listesi boş!")


        # BİRLEŞTİRME
        print("🔗 Klipler birleştiriliyor...")
        video_track = concatenate_videoclips(processed_clips, method="compose") # görüntüleri tek video gibi birleştirir


        # KESME VE MONTAJ
        final_clip = video_track.subclip(0, total_duration) # görüntüyü ses süresine göre kesiyoruz
        # Sesi videoya ata
        final_clip = final_clip.set_audio(audio_clip)

        # RENDER
        output_path = os.path.join(OUTPUT_DIR, output_filename) # çıkış dosya yolu
        print(f"⏳ Render başladı...")
        
        # 'ffmpeg_params=["-ac", "2"]' -> Sesi zorla 2 kanal (Stereo) yapar. Çünkü oluşturduğumuz MP3 dosyaları mono oluyor moviepy kütüphanesi streo çalıştığından hata verir.
        # 'audio_codec="libmp3lame"' -> En uyumlu MP3 kodeğini kullan
        final_clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264',  # tüm dünyadaki telefon formatı
            audio_codec='libmp3lame',  # AAC yerine MP3 kullanıyoruz (daha güvenli)
            ffmpeg_params=["-ac", "2"], # Zorla Stereo (Mono sesleri zorla iki kanal bölerek streo yapar)
            preset='ultrafast', # hızlı render için şimdilik demo aşamasında kalsın bu şekil
            threads=4,
            logger='bar'
        )
        
        print(f"✅ VİDEO HAZIR: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Montaj Hatası: {e}")
        return None
        
    finally:
        try:
            if final_clip: final_clip.close()
            if audio_clip: audio_clip.close()
        except: pass


if __name__ == "__main__":
    # Test verileri
    test_audio = "test_voice.mp3" 
    media_dir = "media_files"
    
    test_videos = []
    if os.path.exists(media_dir):
        test_videos = [os.path.join(media_dir, f) for f in os.listdir(media_dir) if f.endswith(".mp4")]
        test_videos.sort()
    
    if test_audio and test_videos:
        create_final_video(test_audio, test_videos, "test_render_final.mp4")
    else:
        print("❌ Test dosyaları eksik!")
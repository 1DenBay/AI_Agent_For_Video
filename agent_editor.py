import os
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
        num_videos = len(video_paths) # toplam görüntü sayısı
        clip_duration = total_duration / num_videos # her bir görüntünün ne kadar süreceği. ses süresini baz alarak ona göre bölüyoruz.
        if clip_duration < 2.0: clip_duration = 2.0 # fazla görüntü olunca görüntü başına süre düşerse bişey anlaşılmaz diye en az 2 saniye yapıyoruz.


        # VİDEOLARI HAZIRLA
        processed_clips = []
        for v_path in video_paths:
            try:
                clip = VideoFileClip(v_path) # görüntüleri yüklüyoruz 
                clip = clip.without_audio() # sonrasında bizim dublajı bastırmaması için görüntü seslerini atıyoruz
                
                # Resize ile görüntüyü en üstte belirledğimiz çözünürlüğe getiriyoruz
                if clip.w != TARGET_WIDTH or clip.h != TARGET_HEIGHT:
                    clip = clip.resize(newsize=(TARGET_WIDTH, TARGET_HEIGHT))
                
                # Görüntüyü belirlediğimiz görüntü başına düşen süre kadar alıyoruz
                if clip.duration > clip_duration:
                    clip = clip.subclip(0, clip_duration)
                
                processed_clips.append(clip) # işlenmiş görüntüyü döngü başında oluşturduğumuz boş listeye ekliyoruz
            except Exception as e:
                print(f"   ❌ Hata ({os.path.basename(v_path)}): {e}")

        if not processed_clips:
            raise ValueError("Video listesi boş!")


        # BİRLEŞTİRME
        video_track = concatenate_videoclips(processed_clips, method="compose") # görüntüleri tek video gibi birleştirir
        
        # Loop ile görüntüyü ses süresine yetiştirme (Ekran siyaha düşmesin diye)
        if video_track.duration < total_duration: # eğer görüntü süresi sesten az ise
            n_loops = int(total_duration / video_track.duration) + 2 # kaç kere döneceğini hesapla
            video_track = video_track.loop(n=n_loops) # görüntü bitip siyah ekrana düşmez
            

        # KESME VE MONTAJ
        final_clip = video_track.subclip(0, total_duration) # görüntüyü ses süresine göre kesiyoruz
        # Sesi videoya ata
        final_clip = final_clip.set_audio(audio_clip)

        # RENDER
        output_path = os.path.join(OUTPUT_DIR, output_filename) # çıkış dosya yolu
        print(f"⏳ Render başladı... Hedef: {output_path}")
        
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
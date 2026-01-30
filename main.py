import os
import time
# üreticiler
from agents.agent_brain import generate_video_plan
from agents.agent_voice import generate_audio_file
from agents.agent_media import get_media_files
from agents.agent_editor import create_final_video
from agents.agent_subtitler import add_subtitles
# dağıtıcı
from distributors.agent_youtube import upload_to_youtube
from distributors.agent_tiktok import upload_tiktok

"""
    Tüm ajanları sırayla çalıştıran ana orkestra şefi.
"""
def main_pipeline(topic): # parametre olarak video konusu alır

    print(f"\n🚀 AI Video Fabrikası Çalışıyor... Konu: {topic}")
    

    # --- ADIM 1: BEYİN (Senaryo) ---
    print("\n🧠 ADIM 1: Senaryo ve Görsel İstemi Hazırlanıyor...")
    plan = generate_video_plan(topic) # agent_brain senaryo planı oluşturur
    
    if not plan:
        print("❌ HATA: Brain ajanı senaryo üretemedi.")
        return

    script_text = plan['script']
    search_keywords = plan['keywords']
    video_title = plan['title']
    
    print(f"   📝 Başlık: {video_title}")
    print(f"   🔑 Anahtar Kelimeler: {search_keywords}")


    # --- ADIM 2: SES (Dublaj) ---
    print("\n🎙️ ADIM 2: Christopher Stüdyoya Girdi (Seslendirme)...")
    # Benzersiz isim verelim ki dosyalar karışmasın
    audio_filename = f"voice_{int(time.time())}.mp3"
    audio_path = generate_audio_file(script_text, audio_filename)
    
    if not audio_path:
        print("❌ HATA: Voice ajanı sesi kaydedemedi.")
        return


    # --- ADIM 3: MEDYA (Stok Video) ---
    print("\n🔍 ADIM 3: Görsel Materyaller Toplanıyor...")
    video_paths = get_media_files(search_keywords)
    
    if not video_paths:
        print("❌ HATA: Media ajanı video bulamadı.")
        return


    # --- ADIM 4: MONTAJ (Editor) ---
    print("\n🎬 ADIM 4: Final Montaj ve Render...")
    raw_video_filename = f"raw{int(time.time())}.mp4"
    raw_video_path = create_final_video(audio_filename, video_paths, raw_video_filename)
    
    if not raw_video_path:
        print("❌ HATA: Editor videoyu oluşturamadı.")
        return 
        
    print(f"✅ Ham montaj tamamlandı: {raw_video_path}")


    # --- ADIM 5: ALTYAZI (FİNAL) ---
    print("\n📝 ADIM 5: Altyazı ve Makyaj Yapılıyor...")
    final_filename = f"SHORTS_FINAL_{int(time.time())}.mp4"
    final_output_path = os.path.join("final_videos", final_filename)
    
    subtitle_result = add_subtitles(raw_video_path, audio_filename, final_output_path)
    
    if not subtitle_result:
        print("❌ HATA: Altyazı eklenemedi.")
        return
    
    print(f"\n✨✨✨ İŞLEM BAŞARILI! ✨✨✨")
    print(f"📂 VİDEONUZ HAZIR: {subtitle_result}")
    print(f"------------------------------------------------")
    
    # İstenirse ham videoyu silenebilir, şimdilik kalsın. bazen hata oluyor geri dönüp bakmak için.
    # os.remove(raw_video_path)


    # --- UPLOAD ---
    print(f"------------------------------------------------")
    print("\n🚀 ADIM 6: YouTube - Tiktok Dağıtımı Başlıyor...")
    
    # [v1.1 GÜNCELLEME] Brain Ajanının ürettiği profesyonel verileri çekiyoruz
    # Eskiden burada kelimeleri birleştirip biz uyduruyorduk, şimdi yapay zeka yazdı.
    ai_description = plan.get('description', '') # Brain'den gelen açıklama
    ai_hashtags = plan.get('hashtags', '')       # Brain'den gelen hashtagler (#fact #wow vs.)
    
    # YouTube İçin Açıklama Metni
    # Başlık + AI Açıklaması + AI Hashtagleri + Standart Etiketler
    yt_desc = f"{video_title}\n\n{ai_description}\n\n{ai_hashtags}\n\n#shorts #ai #generated"
    
    # YouTube Etiketleri (Keywords listesini kullanmaya devam edebiliriz, teknik etiket için iyidir)
    yt_tags = [k.replace(" ", "") for k in search_keywords]

    # TikTok Metni (TikTok kısa sever: Başlık + Hashtagler)
    tt_desc = f"{video_title}\n\n{ai_hashtags} #shorts #ai"
    

    # Youtube Dağıtımı
    print("\n📺 YouTube Kanalına Yükleniyor...")
    try:
        upload_to_youtube(
            subtitle_result, # en son üretilen altyazılı videoyu alır
            video_title,  # brainden gelen başlık
            yt_desc, # açıklama metni
            tags=yt_tags, # etiketler
            privacy_status="private" # TEST İÇİN 'PRIVATE' (GİZLİ). Sıkıntı yoksa 'public' yapabilirsin.
        )
    except Exception as e:
        print(f"⚠️ YouTube Hatası (Pas geçiliyor): {e}")


    # Tiktok Dağıtımı
    print("\n🎵 TikTok Yükleniyor...")
    print("   👉 Tarayıcı açılacak, lütfen müdahale etme.")
    
    upload_tiktok(
        subtitle_result,
        tt_desc
    )
    
    print("\n" + "="*60)
    print("🎉 FABRİKA PAYDOS! TÜM GÖREVLER BAŞARIYLA TAMAMLANDI.")
    print("="*60 + "\n")



# BİRİM TEST
if __name__ == "__main__":
    # konu iste gir 
    try:
        while True:
            print("\n--- YENİ GÖREV ---")
            user_topic = input("Video Konusu Nedir? (Çıkış için 'q'): ")
            if user_topic.lower() == 'q':
                break
            if user_topic.strip():
                main_pipeline(user_topic)
    except KeyboardInterrupt:
        print("\n👋 Sistem kapatılıyor.")
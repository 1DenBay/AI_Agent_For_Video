import os
import time
from agent_brain import generate_video_plan
from agent_voice import generate_audio_file
from agent_media import get_media_files
from agent_editor import create_final_video

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
    final_filename = f"shorts_{int(time.time())}.mp4"
    final_path = create_final_video(audio_filename, video_paths, final_filename)
    
    if final_path:
        print(f"\n✨ İŞLEM BAŞARILI! ✨")
        print(f"📂 Videoeq Hazır: {final_path}")
        print("------------------------------------------------")
    else:
        print("❌ HATA: Editor videoyu oluşturamadı.")


if __name__ == "__main__":
    # Kullanıcıdan konu iste
    try:
        user_topic = input("\nVideo Konusu Nedir? (Örn: 'Simülasyon Teorisi', 'Kara Delikler'): ")
        if user_topic.strip():
            main_pipeline(user_topic)
        else:
            print("❌ Konu girmediniz, işlem iptal edildi.")
    except KeyboardInterrupt:
        print("\n👋 İşlem kullanıcı tarafından durduruldu.")
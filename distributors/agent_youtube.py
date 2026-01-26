import os
import pickle # verileri dondurup saklamak için genelde token dosyasını tutarız
# google kütüphaneleri ve youtube api için
from google_auth_oauthlib.flow import InstalledAppFlow # sunucuda (canlıda) değilde masaüstünde çalıştığımızdan onay penceresi açar
from google.auth.transport.requests import Request # istek göndermek için (süresi geçen tokeni yeniliycez)
from googleapiclient.discovery import build # youtube api bağlantısı komutları
from googleapiclient.http import MediaFileUpload # youtube uygun formatta video yükleme için

# YouTube'a video yükleme izni istiyoruz. google api bağlantısı. sadece video yükleme izni içindir.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


"""
    YouTube hesabına giriş yapar ve yetki token'ını 'token.pickle' dosyasına kaydeder.
    İlk çalıştırmada tarayıcı açar izin ister, sonraki seferlerde kaydettiği token'ı kullanır.
"""
def authenticate_youtube():
    credentials = None
    
    # Ana dizindeki token dosyasını kontrol edip. anahatarı yükler
    token_path = "token.pickle"
    client_secret_path = "client_secret.json"

    # Eski oturum (token) var mı. ilk giriş sonrası her seferinde sormasın diye
    if os.path.exists(token_path):
        print("🔑 Eski oturum anahtarı (token.pickle) bulundu...")
        with open(token_path, "rb") as token:
            credentials = pickle.load(token)

    # Token yoksa veya süresi dolmuşsa yeni giriş yap.
    if not credentials or not credentials.valid: # eğer token var ama süresi dolmuşsa  (genelde 1 saat süreli olur) onu yeniler tekrar izin istememek için
        if credentials and credentials.expired and credentials.refresh_token:
            print("🔄 Token süresi dolmuş, yenileniyor...")
            credentials.refresh(Request()) # süresi dolmuş token'ı yeniler (ana token yanında yedek tokenda verir bu yenileme doğrulaması için yedek olanı kullanır burada)

        # daha önce token oluşturulmamışsa yeni token oluşturur    
        else: 
            print("🌍 Tarayıcı açılıyor, lütfen KANAL HESABIYLA giriş yap...")
            
            if not os.path.exists(client_secret_path):
                print(f"❌ HATA: '{client_secret_path}' dosyası bulunamadı! Ana dizine koyduğundan emin ol.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES
            )
            # Yerel bir sunucu açıp Google'dan cevabı bekler
            credentials = flow.run_local_server(port=0) # 0 port hangisi boşsa işte onu kullanacak)

        # Yeni token'ı kaydet (Bir daha şifre sormasın diye saklama yaparız)
        with open(token_path, "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


"""
    Videoyu YouTube'a yükler.
    privacy_status seçenekleri: 'public', 'private', 'unlisted' şuan geliştirme aşamasından dolayı default olarak private kullanıyorum.
"""
def upload_to_youtube(video_path, title, description, tags=[], privacy_status="private"):
    
    try:
        print("🚀 YouTube Ajanı Devrede: Yükleme Başlıyor...")
        
        # hesap ve api bilgileri için önceki fonksiyonu çağırıyoruz
        youtube = authenticate_youtube()
        if not youtube:
            return None

        # yüklenen video kimliği (youtubeye girerken video için gerekli bilgiler)
        body = {
            "snippet": { 
                "title": title[:100], # YouTube max 100 karakter kabul eder
                "description": description,
                "tags": tags,
                "categoryId": "22" # 22 = People ve Blogs (Genel kategori yani. her kategorinin numarsı var videoya göre seçim yapılır)
            },
            "status": {
                "privacyStatus": privacy_status, # public / private / unlisted (geliştirme aşamasında private kullanıyorum)
                "selfDeclaredMadeForKids": False # Çocuklara özel DEĞİL yoksa default çocuklar için oluyo yorumlar falan kapalı olur
            }
        }

        # Dosya yükleme ayarları (Resumable=True, bağlantı koparsa kaldığı yerden devam eder)
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True) # chunksize=-1 tek parça halinde yükle demek
        
        print(f"   📤 Yükleniyor: {title}")
        request = youtube.videos().insert(  # yükleme emri
            part="snippet,status",
            body=body,
            media_body=media
        )

        # yükleme sırasında consoldan takip edebilmek için ilerleme durumu
        response = None # video bitene kadar boş dönecek
        while response is None: # cevap gelene kadar döngü sürsün (googleden video ID içeren cevap döner)
            status, response = request.next_chunk() # süreç ilerlemesini google ile iletişim halinde yapar. (her aldığı parçayı bildirir. bunu aldım sıraki gibisinden.)
            if status:
                print(f"   📊 İlerleme: %{int(status.progress() * 100)}") # yüzdesel ilerleme durumu

        print(f"✅ Yükleme Başarılı!")
        video_id = response['id'] # google status değilde response gönderince işlem biter ve video id döner
        print(f"🔗 Video Linki: https://www.youtube.com/watch?v={video_id}") # yükleme sonrası videonun canlı linkini verecek
        return video_id

    except Exception as e:
        print(f"❌ YouTube Hatası: {e}")
        return None


# --- TEST BLOĞUDUR DİREKT OLUŞTURUP YÜKLEMEK İÇİN SADECE MAIN.PY ÇALIŞTIRMAK YETERLİ ---
if __name__ == "__main__":
    # Test ederken elindeki GERÇEK bir videonun yolunu yazmalısın.
    # Örn: "final_videos/SHORTS_FINAL_123456.mp4"
    
    # Otomatik olarak final_videos klasöründeki son videoyu bulacak onu yüklecek
    final_dir = "final_videos"
    if os.path.exists(final_dir):
        files = [os.path.join(final_dir, f) for f in os.listdir(final_dir) if f.endswith(".mp4")]
        if files:
            latest_video = max(files, key=os.path.getctime) # En son oluşturulan videoyu al
            print(f"🧪 Test için bulunan son video: {latest_video}")
            
            upload_to_youtube(
                latest_video, 
                "Test Video - Python Upload", 
                "Bu video otomatik yüklenmiştir.",
                ["test", "ai"],
                privacy_status="private" # Test olduğu için Gizli yükle
            )
        else:
            print("❌ Test edecek video bulunamadı. Önce video üret!")
    else:
        print("❌ final_videos klasörü yok.")
import os
import time
import pickle
import undetected_chromedriver as uc # robot engelleri için (sadece selenium kullanırsak anlaşılır)
from selenium.webdriver.common.by import By # html elementlerini bulmak için (hangi buton nerede filan)
from selenium.webdriver.common.keys import Keys # klavye tuşları simülasyonu için (escape,enter vs)

COOKIE_FILE = "tiktok_cookies.pickle" # Çerez dosyası (sürekli tekrar tekrar giriş yapmamak için)


"""
    Tarayıcıyı başlatır ve gerekli ayarları yapar.
"""
def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized") # Tam ekran başlat
    options.add_argument("--disable-popup-blocking") # Pop-up engelleyiciyi kapat (çünkü bazı tiktok pencereleri pop-up olarak açılıyor orada direkt anlamasın)
    driver = uc.Chrome(options=options) # undetected chromedriver ile başlat (tespit edilmemesi için)
    return driver


"""
    Giriş kontrolü yapar ve çerezleri yükler/kaydeder.
"""
def check_login_and_load_cookies(driver): # üstten açılan pencereyi parametre olarak alacak
    if os.path.exists(COOKIE_FILE): # çerez dosyası var mı kontrol et
        print("🍪 TikTok: Çerezler yükleniyor...")
        driver.get("https://www.tiktok.com") # önce ana sayfaya git (çerezler orada geçerli olacak)
        with open(COOKIE_FILE, "rb") as f: # çerez dosyasını oku
            cookies = pickle.load(f) # çerezleri yükle
            for cookie in cookies:
                try: driver.add_cookie(cookie)
                except: pass
        driver.refresh() # sayfayı yenile (çerezler yüklendi)
        time.sleep(5)
    # çerez dosyası yoksa yani ilk girişte normal giriş yapılacak
    else:
        print("⚠️ TikTok: Giriş yapman bekleniyor.")
        driver.get("https://www.tiktok.com/login")
        input("Giriş yapınca ENTER'a bas...") # kullanıcıdan giriş yapmasını bekledikten sonra kullanıcı entere basar ve işlemler tekrar oto devma edecek
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, "wb") as f:
            pickle.dump(cookies, f) # giriş sonrası çerezleri kaydet


"""
    Güçlendirilmiş js Tıklama (Event dispatcher)
    Normal tıklamada tiktok algılamayabiliyor, ignore ediyor yada önüne şeffaf katman geçebiliryordu (bilgilendirme ekranları gibi overlay durumlar)
    bu yüzden JS ile mouse event gönderiyoruz yani beyne girip buraya tıklandı sinyali gibi birşey.
"""
def js_click(driver, element):

    driver.execute_script("""
        var element = arguments[0];
        var mouseEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(mouseEvent); // Tıklama olayını tetikler
    """, element)


"""
    Yükleme fonksiyonu
"""
def upload_tiktok(video_path, description):
    print("🚀 TikTok Ajanı Devrede")
    video_path = os.path.abspath(video_path) # direkt yolu alıp verecek. mp4 verirsek çalışmıyor
    driver = get_driver()
    
    try:
        check_login_and_load_cookies(driver) # giriş kontrolü ve çerez yüklemesi ile upload sayfasına gitmek için
        print("🌍 Yükleme sayfasına gidiliyor...")
        driver.get("https://www.tiktok.com/creator-center/upload?from=upload") # yükleme sayfası linki
        time.sleep(8) # Sayfanın tam yüklenmesi için bekletiyoruz. Bazı elementler geç yükleniyor.
        
        # Pop-up temizliği (bazı durumlarda açılıyor, tıklamamızı engellmemesi için normal esc tuşu gönderiyoruz)
        try: driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except: pass

        # Dosyayı yükleme (video seç butonuna basarsak bu sefer locelde dosya dizinleri ile de uğraşmamız gerekecek onun yerine direkt dosya inputuna yolu gönderiyoruz)
        print(f"📤 Video yükleniyor: {os.path.basename(video_path)}")
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if file_inputs:
            file_inputs[0].send_keys(video_path)
        else:
            print("❌ Dosya yükleme alanı bulunamadı.")
            return

        # Bekleme (video telif kontrolü ve işleme süresi için)
        print("⏳ Video işleniyor... (30 saniye)")
        time.sleep(30)

        # Açıklama
        print("✍️ Açıklama yazılıyor...")
        try:
            driver.execute_script("window.scrollBy(0, 300);") # açıklama yazma kutusu bazen altta kalıyor, biraz yukarı kaydırıyoruz ne olur olmaz diye 
            time.sleep(1)
            caption_box = driver.find_element(By.CSS_SELECTOR, ".public-DraftEditor-content") # açıklama kutusu seçimi
            js_click(driver, caption_box) # JS ile odaklan yani kutuya tıkla
            caption_box.send_keys(description) # açıklamayı yaz
        except:
            print("⚠️ Açıklama yazılamadı (Pas geçiliyor).")

        # BUTON TARAMASI BAŞLIYOR (tiktok her zaman sabit nesneler kullanmıyor bazen buton bazen div yapıyor, bu yüzden ikisini de tarıyoruz)
        print("\n🦅 Sayfadaki tüm butonlar taranıyor...")
        
        # En alta in
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Butonları ve buton görünümlü divleri topla (normalde xpath ile tek seferde de alabiliriz ama çalışmıyor robot engelleyiciler yüzünden)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        divs = driver.find_elements(By.XPATH, "//div[@role='button']")
        all_elements = buttons + divs # toplanan hepsini bir araya getirir
        
        target_found = False # hedef buton bulunma durumuna kadar döngü sürecek
        target_words = ["Paylaş", "Yayınla", "Post", "Upload"] # Aranan buton metinleri (Türkçe ve İngilizce karışık)

        for i, btn in enumerate(all_elements): # tüm butonlarda dön
            try:
                # Metni al (HTML içindeki gizli text dahil)
                txt = btn.get_attribute("innerText").strip()
                
                # Boşsa atla
                if not txt: continue
                
                print(f"   🔹 Element {i}: '{txt}'") # bulanan her objeyi konsoldan takip edebiliyorz
                
                # Hedef kelime var mı kontrol et ve kısa mı (yanlış tıklamaları engellemek için)
                if any(target in txt for target in target_words) and len(txt) < 30:
                    print(f"   🎯 HEDEF BULUNDU! ({txt})")
                    
                    # Kırmızı yap (Görmen için çünkü ilk başlarda tıklayamıyordu manuel yapınca oluyordu sonra dan da tıkladığı gözüksün diye silmedim kırmızılığı)
                    driver.execute_script("arguments[0].style.border='4px solid red';", btn)
                    time.sleep(1)
                    
                    # JS Sinyali Gönder (normal tıklama bazen algılanmıyor uzun uğraşlar sonunda bunu bulduk)
                    js_click(driver, btn)
                    print("✅ Tıklama sinyali gönderildi.")
                    
                    target_found = True
                    break # Bulununca çık
            except: # herhangi bir butonda hata olursa atlayacak pencere süresi dolup kapanana kadar bekler
                continue

        if target_found:
            print("🎉 İşlem tamamlandı (veya denendi). Sonuca bak.")
            time.sleep(10)
        else:
            print("❌ Hedef buton ismiyle bulunamadı. Listeyi kontrol et.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        print("👋 Tarayıcı 60sn açık kalacak.")
        time.sleep(60)
        driver.quit()


# BİRİM TESTİ
if __name__ == "__main__":
    sample_video = "/Users/denbay/ai_video_agent/final_videos/SHORTS_FINAL_1769422813.mp4"
    if os.path.exists(sample_video):
        upload_tiktok(sample_video, "Test videosu #ai #python")
    else:
        print("Video yolu hatalı.")
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- AMBIL DATA DARI GITHUB SECRETS ---
USERNAME = os.getenv('FEBSPOT_USER')
PASSWORD = os.getenv('FEBSPOT_PASS')
# Folder tempat video disimpan di repo GitHub kamu
VIDEO_FOLDER = "videos" 

def setup_browser():
    options = Options()
    options.add_argument("--headless")  # Wajib untuk GitHub Actions
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def bot_febspot():
    driver = setup_browser()
    wait = WebDriverWait(driver, 20)

    try:
        # 1. LOGIN
        print("Membuka halaman login...")
        driver.get("https://www.febspot.com/login.html")
        
        print(f"Mencoba login sebagai: {USERNAME}")
        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Cek apakah login berhasil (menunggu dashboard muncul)
        time.sleep(5)
        print("Login Berhasil!")

        # 2. PROSES UPLOAD DARI FOLDER
        if not os.path.exists(VIDEO_FOLDER):
            print(f"Folder '{VIDEO_FOLDER}' tidak ditemukan!")
            return

        videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.mkv', '.mov'))]
        
        if not videos:
            print("Tidak ada file video di folder.")
            return

        for video_file in videos:
            video_path = os.path.abspath(os.path.join(VIDEO_FOLDER, video_file))
            print(f"Sedang mengunggah: {video_file}")

            driver.get("https://www.febspot.com/upload.html")
            
            # Cari input file
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(video_path)

            # Tunggu proses upload selesai (sesuaikan waktu jika video besar)
            print("Menunggu proses upload (30 detik)...")
            time.sleep(30) 

            # Mengisi Judul (opsional, FebSpot biasanya otomatis ambil nama file)
            # Simpan/Publish
            try:
                save_btn = driver.find_element(By.ID, "save_button") # Ganti ID jika salah
                save_btn.click()
                print(f"Berhasil mempublikasikan: {video_file}")
            except:
                print(f"Gagal klik tombol save untuk {video_file}, mungkin sudah otomatis.")

            time.sleep(5) # Jeda antar upload

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        driver.quit()
        print("Bot selesai bekerja.")

if __name__ == "__main__":
    bot_febspot()

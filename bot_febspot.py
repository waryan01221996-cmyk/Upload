import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- KONFIGURASI ---
USERNAME = os.getenv('FEBSPOT_USER')
PASSWORD = os.getenv('FEBSPOT_PASS')
VIDEO_FOLDER = "temp_videos"
# List link video yang ingin di-reupload (bisa dari YouTube, TikTok, dll)
LINKS_TO_DOWNLOAD = [
    "https://www.youtube.com/shorts/contoh1",
    "https://www.youtube.com/shorts/contoh2"
]

def setup_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def download_video(url):
    if not os.path.exists(VIDEO_FOLDER):
        os.makedirs(VIDEO_FOLDER)
    
    print(f"--- Mendownload: {url} ---")
    filename = f"{VIDEO_FOLDER}/video_{int(time.time())}.mp4"
    try:
        # Menjalankan yt-dlp via terminal
        subprocess.run(['yt-dlp', '-f', 'mp4', '-o', filename, url], check=True)
        return filename
    except Exception as e:
        print(f"Gagal download {url}: {e}")
        return None

def upload_to_febspot(driver, file_path):
    wait = WebDriverWait(driver, 30)
    try:
        print(f"--- Mengunggah ke FebSpot: {file_path} ---")
        driver.get("https://www.febspot.com/upload.html")
        
        # Input file
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        file_input.send_keys(os.path.abspath(file_path))
        
        # Tunggu proses upload (bisa ditambah jika video besar)
        print("Sedang mengunggah... tunggu 40 detik.")
        time.sleep(40)
        
        # Klik Simpan/Publish
        save_btn = driver.find_element(By.ID, "save_button")
        save_btn.click()
        print("Upload Berhasil!")
        return True
    except Exception as e:
        print(f"Gagal upload: {e}")
        return False

def main():
    if not USERNAME or not PASSWORD:
        print("Error: Username/Password belum diatur di Secrets!")
        return

    driver = setup_browser()
    
    try:
        # LOGIN
        driver.get("https://www.febspot.com/login.html")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        
        # PROSES SETIAP LINK
        for link in LINKS_TO_DOWNLOAD:
            video_file = download_video(link)
            if video_file and os.path.exists(video_file):
                success = upload_to_febspot(driver, video_file)
                # Hapus file setelah upload agar storage GitHub tidak penuh
                os.remove(video_file)
                print(f"File {video_file} dihapus.")
                time.sleep(10) # Jeda antar upload

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

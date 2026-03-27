import pandas as pd
from playwright.sync_api import sync_playwright
import os
import subprocess # 🚀 FFMPEG İÇİN EKLENDİ

EXCEL_DOSYASI = "fikstur.xlsx"
HTML_DOSYASI = "pinballsim.html"
VIDEO_KLASORU = "Render_Edilen_Maclar"

os.makedirs(VIDEO_KLASORU, exist_ok=True)

def main():
    print("📊 Excel dosyası okunuyor...")
    try:
        df = pd.read_excel(EXCEL_DOSYASI)
    except Exception as e:
        print(f"❌ Excel okuma hatası: {e}")
        return

    with sync_playwright() as p:
        # 🚀 headless=False VE GPU HIZLANDIRMASI EKLENDİ (Fizikler kasmasın diye)
        browser = p.chromium.launch(
            headless=False, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--use-gl=egl"]
        )
        
        for index, row in df.iterrows():
            mac_adi = f"{row['Takim_A_Ad']}_vs_{row['Takim_B_Ad']}".replace(" ", "_")
            print(f"\n🎬 Render Başlıyor [{index+1}/{len(df)}]: {mac_adi}")
            
            context = browser.new_context(
                viewport={"width": 540, "height": 960},
                accept_downloads=True 
            )
            page = context.new_page()
            
            html_path = f"file://{os.path.abspath(HTML_DOSYASI)}"
            page.goto(html_path)
            
            # Excel verilerini HTML'e basma
            page.fill("#leagueName", str(row["Turnuva_Adi"]))
            page.fill("#leagueLogo", str(row["Turnuva_Logo"]))
            page.fill("#history", str(row["Gecmis_Maclar"]))
            page.fill("#teamAName", str(row["Takim_A_Ad"]))
            page.fill("#teamALogo", str(row["Takim_A_Logo"]))
            page.fill("#teamAColor1", str(row["A_Renk1"]))
            page.fill("#teamAColor2", str(row["A_Renk2"]))
            page.fill("#teamBName", str(row["Takim_B_Ad"]))
            page.fill("#teamBLogo", str(row["Takim_B_Logo"]))
            page.fill("#teamBColor1", str(row["B_Renk1"]))
            page.fill("#teamBColor2", str(row["B_Renk2"]))
            
            print("   ⏳ Maç oynanıyor ve kaydediliyor...")
            
            with page.expect_download(timeout=90000) as download_info:
                page.click("#start-btn")
                page.evaluate("document.getElementById('control-panel').style.display = 'none'")

            # 1. Ham webm videosunu indir
            download = download_info.value
            ham_video_yolu = os.path.join(VIDEO_KLASORU, f"{mac_adi}_RAW.webm")
            download.save_as(ham_video_yolu)
            
            page.close()
            context.close()
            
            # =========================================================================
            # 💥 2. FFMPEG İLE GÖRÜNTÜYÜ 1080P YAP VE SESİ SABİTLE (SIFIR KAYMA) 💥
            # =========================================================================
            final_mp4_yolu = os.path.join(VIDEO_KLASORU, f"{mac_adi}_1080p.mp4")
            print(f"   ⚙️ FFmpeg işliyor: Görüntü HD yapılıyor ve Ses senkronize ediliyor...")
            
            ffmpeg_cmd = [
                "ffmpeg", "-y", 
                "-i", ham_video_yolu, 
                # 1. HAMLE: Çözünürlük 2K Shorts (1440x2560) yapıldı. Algoritma için yeterli, PC için hafif.
                "-vf", "scale=1440:2560:flags=lanczos", 
                "-r", "60", # Sabit 60 FPS (Senkron garantisi devam ediyor)
                # 2. HAMLE: CRF 17 (1080p'nin 18'i ile 4K'nın 16'sı arası kusursuz denge)
                "-c:v", "libx264", "-crf", "17", 
                # 3. HAMLE: 'slow' yerine 'medium' yapıldı. İşlemci çok daha az yorulur, render hızlanır.
                "-preset", "medium", 
                "-c:a", "aac", "-b:a", "192k", 
                "-af", "aresample=async=1", 
                final_mp4_yolu
            ]
            
            try:
                subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                print(f"   ✅ HD Video Hazır: {mac_adi}_1080p.mp4")
                # Çöplük olmaması için işi biten ham webm dosyasını siliyoruz
                os.remove(ham_video_yolu) 
            except Exception as e:
                print(f"   ❌ FFmpeg Hatası: {e}")
            
        browser.close()
        print("\n🎉 Fikstürdeki tüm maçlar HD olarak klasöre dizildi!")

if __name__ == "__main__":
    main()
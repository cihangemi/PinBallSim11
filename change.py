import os
import subprocess

def convert_to_shorts_safe_mp4(input_folder, output_folder):
    # Çıktı klasörü yoksa oluştur
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".webm"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".webm", ".mp4"))
            
            print(f"İşleniyor: {filename}...")

            # FFmpeg Komutu: Mühendislik dokunuşları burada
            command = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',        # Video kodeği: H.264 (En uyumlu)
                '-preset', 'fast',
                '-crf', '18',             # Kalite (18-23 arası iyidir)
                '-r', '30',               # FPS: Tam 30'a sabitle (CFR)
                '-vsync', 'cfr',          # SES KAYMASININ İLACI: Constant Frame Rate zorlaması
                '-c:a', 'aac',            # Ses kodeği: AAC
                '-b:a', '192k',
                '-ar', '44100',           # Ses frekansı: 44.1kHz (Standart)
                '-pix_fmt', 'yuv420p',    # Mobil cihaz uyumluluğu için şart
                output_path
            ]

            try:
                subprocess.run(command, check=True)
                print(f"Başarılı: {filename} -> MP4")
            except subprocess.CalledProcessError as e:
                print(f"Hata oluştu ({filename}): {e}")

# Klasör yollarını kendine göre ayarla
input_dir = r"C:\Users\PC\Desktop\PinBallSim\Render_Edilen_Maclar"
output_dir = r"C:\Users\PC\Desktop\simmp4"

convert_to_shorts_safe_mp4(input_dir, output_dir)
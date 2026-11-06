"""
eminakkurt-mcp Sunucusu
Model Context Protocol (MCP) standartlarına uygun araçlar ve kaynaklar içerir.
"""

import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Veritabanı modülünü içe aktarabilmek için path ayarı
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db.database import save_contact_message, get_site_statistics

# Emin Akkurt Hakkında Bilgi Deposu (Knowledge Base)
EMIN_PROFILE = {
    "name": "Emin Akkurt",
    "title": "Software Developer / Engineer",
    "bio": "Modern web teknolojileri, yapay zeka, sistem mimarileri ve bulut altyapıları ile ilgilenen yazılım geliştirici.",
    "website": "https://eminakkurt.com",
    "github": "https://github.com/eminakkurtt",
    "email": "iletisim@eminakkurt.com",
    "skills": [
        "Python", "JavaScript / TypeScript", "Docker", "Kubernetes",
        "FastAPI", "Node.js", "Git & GitHub", "Cloudflare Pages", "SQL / Databases",
        "Model Context Protocol (MCP)", "Yapay Zeka & LLM Entegrasyonları"
    ],
    "projects": [
        {
            "name": "eminakkurt.com",
            "desc": "Kişisel web sitesi ve portfolyo. Cloudflare Pages ve yapay zeka tabanlı MCP chatbot asistanı barındırır.",
            "tech": "HTML/CSS/JS, Python, SQLite, MCP, Cloudflare"
        },
        {
            "name": "DevOps & Cloud Simülatörleri",
            "desc": "Kubernetes, Docker ve mikroservis mimarileri üzerine çalışmalar ve denemeler.",
            "tech": "Docker, Kubernetes, Linux"
        }
    ]
}

# --- MCP Tool Fonksiyonları ---

def tool_get_profile() -> dict:
    """Emin Akkurt hakkında genel biyografi, yetenekler ve iletişim bilgilerini döndürür."""
    return {
        "name": EMIN_PROFILE["name"],
        "title": EMIN_PROFILE["title"],
        "bio": EMIN_PROFILE["bio"],
        "skills": EMIN_PROFILE["skills"],
        "contact": {
            "email": EMIN_PROFILE["email"],
            "github": EMIN_PROFILE["github"],
            "website": EMIN_PROFILE["website"]
        }
    }

def tool_get_projects() -> list:
    """Emin Akkurt'un geliştirdiği veya üzerinde çalıştığı projelerin listesini döndürür."""
    return EMIN_PROFILE["projects"]

def tool_leave_contact_message(name: str, email: str, message: str, session_id: str = None) -> dict:
    """
    Ziyaretçinin Emin Akkurt'a iletmek istediği mesajı veya iş teklifini doğrudan veritabanına kaydeder.
    """
    if not name or not email or not message:
        return {"status": "error", "error": "İsim, e-posta ve mesaj alanları zorunludur."}

    msg_id = save_contact_message(name=name, email=email, message=message, session_id=session_id)
    return {
        "status": "success",
        "message_id": msg_id,
        "detail": f"Mesajınız başarıyla veritabanına kaydedildi. Emin Akkurt en kısa sürede {email} adresinizden size geri dönüş sağlayacaktır."
    }

def tool_get_site_stats() -> dict:
    """Web sitesi ziyaretçi ve etkileşim istatistiklerini veritabanından sorgular."""
    return get_site_statistics()

# --- Resmi MCP Sunucusu Tanımı (FastMCP) ---
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("eminakkurt-assistant-mcp")

    @mcp.tool()
    def get_profile() -> dict:
        """Emin Akkurt'un yetenekleri, unvanı ve hakkında bilgilerini getirir."""
        return tool_get_profile()

    @mcp.tool()
    def get_projects() -> list:
        """Emin Akkurt'un projelerini getirir."""
        return tool_get_projects()

    @mcp.tool()
    def leave_message(name: str, email: str, message: str) -> dict:
        """Ziyaretçinin Emin'e iletmek istediği iletişim veya iş teklifi mesajını veritabanına kaydeder."""
        return tool_leave_contact_message(name, email, message)

    @mcp.tool()
    def get_stats() -> dict:
        """Sitenin ziyaret ve mesaj istatistiklerini getirir."""
        return tool_get_site_stats()

except ImportError:
    # mcp kütüphanesi henüz yüklenmediğinde doğrudan Python fonksiyonları kullanılır
    mcp = None

if __name__ == "__main__":
    if mcp:
        print("MCP Sunucusu başlatılıyor...")
        mcp.run()
    else:
        print("MCP kütüphanesi bulunamadı. Standart modda test ediliyor:")
        print("Profil:", tool_get_profile())

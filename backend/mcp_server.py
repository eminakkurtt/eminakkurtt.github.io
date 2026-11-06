"""
eminakkurt-mcp Sunucusu
Model Context Protocol (MCP) standartlarına uygun araçlar ve kaynaklar içerir.
Muhammet Emin Akkurt'un gerçek CV verileri ile güçlendirilmiştir.
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

# Muhammet Emin Akkurt Hakkında Bilgi Deposu (Knowledge Base)
EMIN_PROFILE = {
    "name": "Muhammet Emin Akkurt",
    "title": "Cloud, DevOps & Systems/Network Engineer",
    "location": "Pendik / İstanbul, Türkiye",
    "email": "eminakkurtt@icloud.com",
    "website": "https://eminakkurt.com",
    "github": "https://github.com/eminakkurtt",
    "linkedin": "https://www.linkedin.com/in/muhammeteminakkurt",
    "bio": (
        "Cloud, DevOps ve sistem/ağ yönetimi alanlarında kendini sürekli geliştiren, "
        "uygulamalı proje deneyimiyle desteklenen bir teknik altyapıya sahip mühendis. "
        "Azure ve Huawei Cloud gibi bulut platformlarında, Docker ve Kubernetes ile container yönetiminde, "
        "Jenkins ile CI/CD süreçlerinde ve Grafana ile Prometheus kullanılarak yapılan sistem izleme çalışmalarında deneyimli."
    ),
    "education": [
        {
            "school": "Sakarya Üniversitesi",
            "degree": "Bilişim Sistemleri Mühendisliği (Lisans)",
            "dates": "Eylül 2021 – Şubat 2026"
        },
        {
            "school": "Darıca Fen Lisesi",
            "degree": "Fen Bilimleri",
            "dates": "2015 – 2019"
        }
    ],
    "skills": {
        "cloud_virtualization": ["Microsoft Azure (IaaS, PaaS)", "Huawei Cloud", "Cloudflare", "VMware"],
        "containers_cicd": ["Docker", "Kubernetes", "Jenkins", "Git", "GitHub Actions"],
        "networking_infrastructure": ["TCP/IP", "Subnetting", "DNS", "DHCP", "NAT", "SSL/TLS", "Switch/Router"],
        "systems_directory": ["Linux (Ubuntu, CentOS)", "Windows Server", "Active Directory", "Domain Controller"],
        "scripting_automation": ["Python (Otomasyon betikleri)", "Bash"],
        "monitoring_messaging": ["Grafana", "Prometheus", "Log Analizi", "RabbitMQ"]
    },
    "experiences": [
        {
            "role": "Cloud & DevOps Stajyeri",
            "company": "Vanora Ventures",
            "type": "Ofisten",
            "dates": "Temmuz 2026 – Günümüz",
            "points": [
                "Azure ve Huawei Cloud ortamlarında temel sanal makine ve kaynak işlemlerinde ekibe destek verdi.",
                "Docker container oluşturma ve temel Kubernetes komutlarını kullanarak deneyim kazandı.",
                "Jenkins üzerinde basit CI/CD pipeline adımlarının takibi ve test edilmesine yardımcı oldu.",
                "Grafana ve Prometheus panellerini takip ederek temel sistem izleme görevlerine katıldı.",
                "Linux sunucularda temel komut satırı işlemleri ve otomasyon betikleri üzerinde çalıştı."
            ]
        },
        {
            "role": "Yazılım Stajyeri",
            "company": "Megacode Yazılım ve Ticaret A.Ş.",
            "type": "Esenyurt, İstanbul",
            "dates": "Eylül 2025 – Ekim 2025",
            "points": [
                "Python ve C# kullanarak yazılım geliştirme süreçlerine destek sağladı.",
                "Postman ile REST API testleri gerçekleştirerek sistem hatalarını tespit edip raporladı.",
                "Git tabanlı versiyon kontrol süreçlerine aktif katıldı."
            ]
        },
        {
            "role": "Yapay Zeka Mühendisi",
            "company": "Horiar",
            "type": "Uzaktan",
            "dates": "Haziran 2024 – Eylül 2024",
            "points": [
                "Şirketin iş akışlarını ve sistem süreçlerini tasarlayarak operasyonların düzene girmesine katkı sağladı.",
                "Kullanıcı ihtiyaçlarını analiz ederek platform yapısını teknik gereksinimler doğrultusunda şekillendirdi."
            ]
        }
    ],
    "certifications": [
        "MCSE Eğitimi (Windows Server, AD & Network) – Udemy",
        "Kubernetes – BTK Akademi",
        "Microsoft Azure ile Bulut Bilişim – BTK Akademi",
        "DevOps Çözümleri (Jenkins) – BTK Akademi",
        "Temel Network Eğitimi – Turkcell Geleceği Yazanlar",
        "Temel Linux (101, 201, 301, 401) – Turkcell Geleceği Yazanlar"
    ],
    "languages": "İngilizce: B2 | Türkçe: Anadil"
}

# --- MCP Tool Fonksiyonları ---

def tool_get_profile() -> dict:
    """Muhammet Emin Akkurt hakkında kapsamlı mühendislik özeti ve iletişim bilgilerini döndürür."""
    return EMIN_PROFILE

def tool_get_experience() -> list:
    """Emin Akkurt'un staj ve çalışma geçmişini döndürür."""
    return EMIN_PROFILE["experiences"]

def tool_get_skills() -> dict:
    """Emin Akkurt'un teknik yetenek matrisini (Cloud, DevOps, Network, Linux) döndürür."""
    return EMIN_PROFILE["skills"]

def tool_get_education_and_certs() -> dict:
    """Emin Akkurt'un üniversite eğitimi ve sertifikasyonlarını döndürür."""
    return {
        "education": EMIN_PROFILE["education"],
        "certifications": EMIN_PROFILE["certifications"],
        "languages": EMIN_PROFILE["languages"]
    }

def tool_leave_contact_message(name: str, email: str, message: str, session_id: str = None) -> dict:
    """Ziyaretçinin Emin'e ilettiği mesajı veya teklifi doğrudan veritabanına kaydeder."""
    if not name or not email or not message:
        return {"status": "error", "error": "İsim, e-posta ve mesaj alanları zorunludur."}

    msg_id = save_contact_message(name=name, email=email, message=message, session_id=session_id)
    return {
        "status": "success",
        "message_id": msg_id,
        "detail": f"Mesajınız başarıyla veritabanına kaydedildi. Emin Akkurt en kısa sürede {email} adresiniz üzerinden sizinle iletişime geçecektir."
    }

def tool_get_site_stats() -> dict:
    """Web sitesi ziyaretçi ve mesaj istatistiklerini sorgular."""
    return get_site_statistics()

# --- FastMCP Sunucu Tanımı ---
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("eminakkurt-engineer-mcp")

    @mcp.tool()
    def get_profile() -> dict:
        """Emin Akkurt'un genel profilini getirir."""
        return tool_get_profile()

    @mcp.tool()
    def get_skills() -> dict:
        """Emin'in Cloud, DevOps, Network ve Yazılım yeteneklerini getirir."""
        return tool_get_skills()

    @mcp.tool()
    def get_experience() -> list:
        """Emin'in iş ve staj deneyimlerini getirir."""
        return tool_get_experience()

    @mcp.tool()
    def leave_message(name: str, email: str, message: str) -> dict:
        """Emin'e veritabanına kayıtlı mesaj bırakır."""
        return tool_leave_contact_message(name, email, message)

except ImportError:
    mcp = None

if __name__ == "__main__":
    if mcp:
        mcp.run()
    else:
        print("MCP Hazır. Profil:", tool_get_profile()["name"])

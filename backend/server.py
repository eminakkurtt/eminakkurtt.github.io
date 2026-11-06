import os
import sys
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from db.database import (
    init_db, log_visitor, save_chat_message, get_chat_history,
    get_all_contact_messages, get_site_statistics
)
from mcp_server import (
    tool_get_profile, tool_get_experience, tool_get_skills,
    tool_get_education_and_certs, tool_leave_contact_message, tool_get_site_stats
)

init_db()

app = FastAPI(title="Muhammet Emin Akkurt Portfolio & MCP Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    tool_called: Optional[str] = None

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Muhammet Emin Akkurt Portfolio AI Agent & MCP Server",
        "profile": "Cloud, DevOps & Systems/Network Engineer"
    }

@app.get("/api/stats")
def get_stats():
    return get_site_statistics()

@app.get("/api/messages")
def get_messages():
    return get_all_contact_messages()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    log_visitor(session_id=payload.session_id, ip_address=client_ip, user_agent=user_agent)
    save_chat_message(session_id=payload.session_id, role="user", message=payload.message)

    user_text = payload.message.strip().lower()
    tool_called = None
    bot_reply = ""

    # Gemini API Entegrasyonu (varsa)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = (
                f"Sen Muhammet Emin Akkurt'un (Cloud, DevOps & Systems Engineer) portfolyo sitesindeki Chatbot'sun. "
                f"Emin hakkında bilgiler:\n{tool_get_profile()}\n\n"
                f"Ziyaretçinin mesajı: {payload.message}\n"
                f"Lütfen profesyonel, samimi ve teknik yetenekleri öne çıkaran bir dille yanıt ver."
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            bot_reply = response.text
        except Exception:
            pass

    # Deterministic MCP Router (API Key yokken veya hızlı yanıt için)
    if not bot_reply:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', payload.message)
        
        # 1. Mesaj / İletişim Bırakma
        if email_match:
            email = email_match.group(0)
            name_match = re.search(r'(?:adım|adim|ben|ismim)\s+([A-Za-zÇçĞğİıÖöŞşÜü]+)', payload.message, re.IGNORECASE)
            name = name_match.group(1) if name_match else "Ziyaretçi"
            
            result = tool_leave_contact_message(name=name, email=email, message=payload.message, session_id=payload.session_id)
            tool_called = "tool_leave_contact_message"
            bot_reply = f"Harika {name}! Mesajınızı veritabanımıza kaydettim (Kayıt No: #{result.get('message_id')}). Emin en kısa sürede {email} adresiniz üzerinden sizinle iletişime geçecektir. 📬"

        # 2. Deneyimler & Stajlar
        elif any(k in user_text for k in ["deneyim", "staj", "nerede", "şirket", "çalıştı", "tecrübe", "vanora", "megacode", "horiar"]):
            exps = tool_get_experience()
            tool_called = "tool_get_experience"
            lines = []
            for exp in exps:
                lines.append(f"• **{exp['role']}** @ {exp['company']} ({exp['dates']})\n  - {exp['points'][0]}")
            bot_reply = "💼 **Emin'in Deneyim ve Staj Geçmişi:**\n\n" + "\n\n".join(lines)

        # 3. Yetenekler & Stack
        elif any(k in user_text for k in ["yetenek", "skill", "teknoloji", "devops", "cloud", "bulut", "docker", "kubernetes", "network", "linux", "jenkins"]):
            skills = tool_get_skills()
            tool_called = "tool_get_skills"
            bot_reply = (
                "⚡ **Muhammet Emin'in Temel Teknik Yetenekleri:**\n\n"
                f"☁️ **Bulut:** {', '.join(skills['cloud_virtualization'])}\n"
                f"🐳 **Konteyner & CI/CD:** {', '.join(skills['containers_cicd'])}\n"
                f"🌐 **Ağ & Altyapı:** {', '.join(skills['networking_infrastructure'])}\n"
                f"🖥️ **Sistem:** {', '.join(skills['systems_directory'])}\n"
                f"📜 **Betik & İzleme:** {', '.join(skills['scripting_automation'])}, {', '.join(skills['monitoring_messaging'])}"
            )

        # 4. Eğitim & Sertifikalar
        elif any(k in user_text for k in ["eğitim", "okul", "üniversite", "sakarya", "lise", "sertifika", "kurs", "btk"]):
            edu_certs = tool_get_education_and_certs()
            tool_called = "tool_get_education_and_certs"
            certs = "\n".join([f"• {c}" for c in edu_certs["certifications"][:4]])
            bot_reply = (
                f"🎓 **Eğitim:**\n"
                f"• {edu_certs['education'][0]['degree']} - {edu_certs['education'][0]['school']} ({edu_certs['education'][0]['dates']})\n"
                f"• {edu_certs['education'][1]['degree']} - {edu_certs['education'][1]['school']}\n\n"
                f"📜 **Öne Çıkan Sertifikalar:**\n{certs}\n*(ve daha fazlası)*\n\n"
                f"🗣️ **Diller:** {edu_certs['languages']}"
            )

        # 5. Kimdir / Genel Profil
        elif any(k in user_text for k in ["kim", "tanıt", "hakkında", "biyografi", "özet"]):
            profile = tool_get_profile()
            tool_called = "tool_get_profile"
            bot_reply = (
                f"👤 **{profile['name']}**\n"
                f"*{profile['title']}* • {profile['location']}\n\n"
                f"{profile['bio']}\n\n"
                f"🔗 **LinkedIn:** {profile['linkedin']}\n"
                f"🐙 **GitHub:** {profile['github']}\n"
                f"✉️ **E-posta:** {profile['email']}"
            )

        # 6. İletişim / Mesaj isteği
        elif any(k in user_text for k in ["iletişim", "ulaş", "mail", "mesaj", "teklif", "görüşme"]):
            bot_reply = (
                "Emin'e iletmek istediğiniz bir proje veya iş teklifi varsa lütfen mesajınızda **adınızı ve e-posta adresinizi** yazın.\n\n"
                "Örnek: *\"Adım Zeynep, e-postam zeynep@firma.com, Cloud pozisyonu için görüşmek isteriz.\"*\n\n"
                "Bilgiler doğrudan veritabanına kaydedilip Emin'e ulaştırılacaktır! ✍️"
            )

        else:
            bot_reply = (
                "Merhaba! Ben Muhammet Emin'in web sitesindeki **Chatbot**'uyum. 🚀 "
                "Emin'in bulut/altyapı tecrübelerini, stajlarını (Vanora Ventures vb.), yeteneklerini ve eğitimini sorabilir "
                "veya ona iletmek üzere bir mesaj bırakabilirsiniz. Size nasıl yardımcı olabilirim?"
            )

    save_chat_message(session_id=payload.session_id, role="bot", message=bot_reply)
    return ChatResponse(reply=bot_reply, tool_called=tool_called)

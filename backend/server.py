import os
import re
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from db.database import (
    init_db, log_visitor, save_chat_message, get_chat_history,
    get_all_contact_messages, get_site_statistics
)
from mcp_server import (
    tool_get_profile, tool_get_projects,
    tool_leave_contact_message, tool_get_site_stats
)

# Veritabanını başlat
init_db()

app = FastAPI(title="eminakkurt.com AI Backend & MCP Bridge")

# Cloudflare Pages veya yerel tarayıcıdan gelen isteklere izin ver (CORS)
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
        "service": "eminakkurt.com AI Agent & MCP Server",
        "db": "connected"
    }

@app.get("/api/stats")
def get_stats():
    """Site istatistiklerini döndürür (Ziyaretçiler, mesajlar)."""
    return get_site_statistics()

@app.get("/api/messages")
def get_messages():
    """Ziyaretçilerin bıraktığı tüm mesajları listeler."""
    return get_all_contact_messages()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # 1. Ziyaretçiyi veritabanına kaydet
    log_visitor(session_id=payload.session_id, ip_address=client_ip, user_agent=user_agent)

    # 2. Kullanıcı mesajını sohbet geçmişine kaydet
    save_chat_message(session_id=payload.session_id, role="user", message=payload.message)

    user_text = payload.message.strip().lower()
    tool_called = None
    bot_reply = ""

    # 3. LLM API Anahtarı kontrolü (GEMINI_API_KEY varsa Google Gemini ile tool calling)
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        # Gemini API entegrasyonu
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            # Sistem promptu ve MCP araçları tanımlanabilir
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Sen Emin Akkurt'un web sitesindeki akıllı yapay zeka asistanısın. Ziyaretçinin mesajı: {payload.message}\nEmin hakkında bilgi:\n{tool_get_profile()}"
            )
            bot_reply = response.text
        except Exception as e:
            bot_reply = f"Yapay zeka modeli yanıt verirken bir sorun oluştu: {str(e)}"
    
    # API Key girilmediyse, yerel MCP Araç Yönlendiricisi (Deterministic Intent Router)
    if not bot_reply:
        # İletişim / Mesaj Bırakma tespiti (E-posta adresi içeriyorsa otomatik tetikle)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', payload.message)
        
        if email_match:
            email = email_match.group(0)
            name_match = re.search(r'(?:adım|adim|ben|ismim)\s+([A-Za-zÇçĞğİıÖöŞşÜü]+)', payload.message, re.IGNORECASE)
            name = name_match.group(1) if name_match else "Ziyaretçi"
            
            # MCP Tool Çalıştırma: leave_message
            result = tool_leave_contact_message(name=name, email=email, message=payload.message, session_id=payload.session_id)
            tool_called = "tool_leave_contact_message"
            bot_reply = f"Harika {name}! Mesajınızı veritabanımıza kaydettim (Kayıt No: #{result.get('message_id')}). Emin en kısa sürede {email} adresiniz üzerinden sizinle iletişime geçecektir. 📬"

        elif "kim" in user_text or "hakkında" in user_text or "biyografi" in user_text or "tanıt" in user_text:
            profile = tool_get_profile()
            tool_called = "tool_get_profile"
            skills_str = ", ".join(profile["skills"][:6])
            bot_reply = (
                f"👤 **{profile['name']}**\n"
                f"{profile['title']}\n\n"
                f"{profile['bio']}\n\n"
                f"🛠️ **Temel Yetenekler:** {skills_str} ve daha fazlası.\n"
                f"🔗 **GitHub:** {profile['contact']['github']}\n"
                f"✉️ **E-posta:** {profile['contact']['email']}"
            )

        elif "proje" in user_text or "portfolyo" in user_text or "ne yaptın" in user_text or "çalışma" in user_text:
            projects = tool_get_projects()
            tool_called = "tool_get_projects"
            proj_lines = [f"• **{p['name']}**: {p['desc']} *(Teknolojiler: {p['tech']})*" for p in projects]
            bot_reply = "🚀 **Emin'in Öne Çıkan Projeleri:**\n\n" + "\n\n".join(proj_lines)

        elif "yetenek" in user_text or "teknoloji" in user_text or "stack" in user_text or "dil" in user_text:
            profile = tool_get_profile()
            tool_called = "tool_get_profile"
            skills_list = "\n".join([f"• {s}" for s in profile["skills"]])
            bot_reply = f"💻 **Emin'in Kullandığı Teknolojiler & Yetenekler:**\n\n{skills_list}"

        elif "istatistik" in user_text or "kaç kişi" in user_text or "sayaç" in user_text:
            stats = tool_get_site_stats()
            tool_called = "tool_get_site_stats"
            bot_reply = (
                f"📊 **Site & Etkileşim İstatistikleri:**\n"
                f"• Toplam Ziyaretçi: {stats['total_visitors']}\n"
                f"• Bırakılan Mesajlar: {stats['total_messages']}\n"
                f"• Sorulan Sorular: {stats['total_user_questions']}"
            )

        elif "mesaj" in user_text or "iletişim" in user_text or "ulaşmak" in user_text:
            bot_reply = (
                "Emin'e iletmek istediğiniz bir mesaj veya iş teklifi varsa lütfen cümlenizde **isminizi** ve **e-posta adresinizi** belirtin.\n\n"
                "Örnek:\n*\"Adım Mehmet, e-postam mehmet@example.com, yeni bir proje geliştirmek istiyoruz.\"*\n\n"
                "Ben bu bilgiyi doğrudan veritabanına kaydedip Emin'e bildireceğim! ✍️"
            )

        else:
            bot_reply = (
                "Merhaba! Emin hakkında bilgi alabilir (kimdir, yetenekleri, projeleri) "
                "veya ona iletmek istediğiniz bir mesajı (adınızı ve e-postanızı ekleyerek) yazabilirsiniz. Size nasıl yardımcı olabilirim?"
            )

    # 4. Bot yanıtını da veritabanına kaydet
    save_chat_message(session_id=payload.session_id, role="bot", message=bot_reply)

    return ChatResponse(reply=bot_reply, tool_called=tool_called)

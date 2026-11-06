import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db.database import get_all_contact_messages, get_site_statistics, get_connection

def display():
    print("=" * 60)
    print("        eminakkurt.com VERİTABANI ÖZET RAPORU")
    print("=" * 60)

    stats = get_site_statistics()
    print(f"👥 Toplam Ziyaretçi : {stats['total_visitors']}")
    print(f"💬 Toplam Soru       : {stats['total_user_questions']}")
    print(f"📬 Bırakılan Mesajlar: {stats['total_messages']}")
    print("-" * 60)

    messages = get_all_contact_messages()
    print(f"\n📩 GELEN İLETİŞİM & İŞ TEKLİFİ MESAJLARI ({len(messages)}):")
    if not messages:
        print("  Henüz mesaj bırakılmamış.")
    for m in messages:
        print(f"  [ID #{m['id']}] {m['created_at']}")
        print(f"  Gönderen : {m['name']} ({m['email']})")
        print(f"  Mesaj    : {m['message']}")
        print(f"  Durum    : {m['status']}")
        print("  " + "-" * 50)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visitors ORDER BY last_seen DESC LIMIT 5")
        visitors = cursor.fetchall()
        print(f"\n🌐 SON ZİYARETÇİLER (Son 5):")
        for v in visitors:
            print(f"  Session: {v['session_id']} | Ziyaret Sayısı: {v['visit_count']} | Son Görülme: {v['last_seen']}")

    print("=" * 60)

if __name__ == "__main__":
    display()

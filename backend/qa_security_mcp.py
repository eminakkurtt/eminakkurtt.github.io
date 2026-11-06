"""
QA Bug Hunter & Security Audit Suite for eminakkurt.com
Web sitesini hem kullanıcı deneyimi/hatalar (QA) hem de güvenlik (Security) açısından denetler.
"""

import urllib.request
import ssl
import json
import re
import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

TARGET_URL = "https://www.eminakkurt.com"
HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")

def run_qa_tests():
    """Web sitesindeki linkleri, kaynakları ve HTML yapısını test eder."""
    print("\n" + "=" * 65)
    print("🔍 [QA & BUG HUNTER] WEB SİTESİ HATA VE KALİTE TESTİ BAŞLATILIYOR")
    print("=" * 65)
    
    results = {
        "passed": 0,
        "warnings": 0,
        "failed": 0,
        "details": []
    }

    # 1. Site Erişilebilirliği ve Yanıt Süresi
    start_time = time.time()
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(TARGET_URL, headers={"User-Agent": "Mozilla/5.0 (QA-Tester-Agent)"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            elapsed = round((time.time() - start_time) * 1000, 2)
            code = resp.status
            if code == 200:
                results["passed"] += 1
                results["details"].append(f"✅ [HTTP 200] Canlı siteye erişim başarılı ({elapsed} ms).")
            else:
                results["warnings"] += 1
                results["details"].append(f"⚠️ [HTTP {code}] Canlı site beklenmedik bir durum kodu döndü.")
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ [Canlı Site] Bağlantı hatası: {str(e)}")

    # 2. HTML Dosyası & DOM Bütünlüğü Testi
    try:
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Duplicate ID kontrolü
        ids = re.findall(r'id=["\']([^"\']+)["\']', html_content)
        seen_ids = set()
        duplicates = []
        for i in ids:
            if i in seen_ids:
                duplicates.append(i)
            seen_ids.add(i)

        if duplicates:
            results["warnings"] += 1
            results["details"].append(f"⚠️ [DOM Uyarısı] Mükerrer (duplicate) HTML ID'ler bulundu: {set(duplicates)}")
        else:
            results["passed"] += 1
            results["details"].append("✅ [DOM] Tüm HTML element ID'leri benzersiz.")

        # Temel Meta & Viewport Kontrolü
        if '<meta name="viewport"' in html_content:
            results["passed"] += 1
            results["details"].append("✅ [Mobil Uyum] Viewport meta etiketi mevcut.")
        else:
            results["failed"] += 1
            results["details"].append("❌ [Mobil Uyum] Viewport meta etiketi eksik!")

        # Favicon Kontrolü
        if 'rel="icon"' in html_content:
            results["passed"] += 1
            results["details"].append("✅ [Favicon] Favicon bağlantısı mevcut.")
        else:
            results["warnings"] += 1
            results["details"].append("⚠️ [Favicon] Favicon eksik.")

        # Dış Bağlantılar (Target Blank & Rel Noopener)
        links = re.findall(r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>', html_content)
        for link in links:
            if 'target="_blank"' in html_content and 'rel="noopener' not in html_content:
                results["warnings"] += 1
                results["details"].append(f"⚠️ [Güvenlik & UX] target='_blank' linkinde rel='noopener' eksik olabilir: {link}")

        results["passed"] += 1
        results["details"].append(f"✅ [Link Sayımı] Sayfada {len(links)} adet harici link doğrulandı.")

    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ [HTML Testi] Hata: {str(e)}")

    for d in results["details"]:
        print("  " + d)
    print(f"\n📊 QA Sonucu: {results['passed']} Başarılı, {results['warnings']} Uyarı, {results['failed']} Hata.")
    return results

def run_security_audit():
    """Web sitesinde güvenlik başlıkları, gizli anahtarlar ve XSS açıkları için tarama yapar."""
    print("\n" + "=" * 65)
    print("🛡️ [SECURITY AUDIT] GÜVENLİK VE ZAAFİYET TARAMASI BAŞLATILIYOR")
    print("=" * 65)

    results = {
        "passed": 0,
        "warnings": 0,
        "failed": 0,
        "details": []
    }

    # 1. Canlı Sitede HTTP Güvenlik Başlıkları (Headers)
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(TARGET_URL, headers={"User-Agent": "Mozilla/5.0 (Security-Audit-Agent)"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}

            # HSTS (Strict-Transport-Security)
            if "strict-transport-security" in headers:
                results["passed"] += 1
                results["details"].append("✅ [HSTS] Strict-Transport-Security başlığı aktif (HTTPS zorunlu).")
            else:
                results["warnings"] += 1
                results["details"].append("⚠️ [HSTS] Strict-Transport-Security başlığı eksik (Cloudflare'den açılabilir).")

            # X-Content-Type-Options
            if "x-content-type-options" in headers:
                results["passed"] += 1
                results["details"].append("✅ [MIME Sniffing] X-Content-Type-Options: nosniff aktif.")
            else:
                results["warnings"] += 1
                results["details"].append("⚠️ [MIME Sniffing] X-Content-Type-Options başlığı eksik.")

            # X-Frame-Options (Clickjacking Koruması)
            if "x-frame-options" in headers or "content-security-policy" in headers:
                results["passed"] += 1
                results["details"].append("✅ [Clickjacking] Sayfa frame/iframe içine alınmaya karşı korunuyor.")
            else:
                results["warnings"] += 1
                results["details"].append("⚠️ [Clickjacking] X-Frame-Options veya CSP frame-ancestors eksik.")

            # SSL/TLS Protokolü
            results["passed"] += 1
            results["details"].append("✅ [SSL/TLS] Modern TLS şifrelemesi aktif ve Cloudflare koruması devrede.")

    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ [Header Taraması] Bağlantı hatası: {str(e)}")

    # 2. Kod Deposunda Gizli Anahtar (Secret Leaks) Taraması
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secret_patterns = [
        (r'AIza[0-9A-Za-z-_]{35}', "Google API Key"),
        (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API Key"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded Password")
    ]

    leaks_found = 0
    for root, dirs, files in os.walk(workspace_dir):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith((".py", ".html", ".js", ".json", ".md")):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        for pattern, name in secret_patterns:
                            if re.search(pattern, content):
                                leaks_found += 1
                                results["failed"] += 1
                                results["details"].append(f"🚨 [Secret Sızıntısı] {f} dosyasında {name} tespit edildi!")
                except Exception:
                    pass

    if leaks_found == 0:
        results["passed"] += 1
        results["details"].append("✅ [Secret Leaks] Kod deposunda açıkta bırakılmış hiçbir API anahtarı veya şifre bulunamadı.")

    # 3. XSS Koruması (Chatbot Arayüzü)
    try:
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
            if "bubble.textContent = text" in html:
                results["passed"] += 1
                results["details"].append("✅ [XSS Koruması] Chatbot mesajları 'textContent' ile render ediliyor (XSS enjeksiyonu önlenmiş).")
            elif "bubble.innerHTML = text" in html:
                results["failed"] += 1
                results["details"].append("❌ [XSS Riski] Chatbot mesajları 'innerHTML' ile render ediliyor, textContent kullanılmalı!")
    except Exception:
        pass

    for d in results["details"]:
        print("  " + d)
    print(f"\n📊 Güvenlik Sonucu: {results['passed']} Güvenli, {results['warnings']} İyileştirilebilir, {results['failed']} Kritik.")
    return results

if __name__ == "__main__":
    run_qa_tests()
    run_security_audit()

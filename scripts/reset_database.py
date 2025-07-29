#!/usr/bin/env python3
"""
Veritabanını sıfırlama scripti
"""

import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from db.database import init_db
from services.auth_service import AuthService
import config

# .env dosyasını yükle
load_dotenv()

def reset_database():
    """Veritabanını tamamen sıfırlar ve yeniden oluşturur"""
    print("🗂️  Veritabanı sıfırlanıyor...")
    
    # Veritabanı dosyasının yolunu al
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    
    try:
        # Mevcut veritabanı dosyasını sil
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Eski veritabanı silindi: {db_path}")
        
        # Yeni veritabanını oluştur
        init_db()
        print("✅ Yeni veritabanı tablolarıyla oluşturuldu!")
        
        # Admin kullanıcısı oluştur
        print("\n👤 Admin kullanıcısı oluşturuluyor...")
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        success = AuthService.register(
            username=admin_username,
            email=admin_email, 
            password=admin_password,
            role="admin"
        )
        
        if success:
            print("✅ Admin kullanıcısı başarıyla oluşturuldu!")
            print(f"📧 E-posta: {admin_email}")
            print(f"👤 Kullanıcı Adı: {admin_username}")
            print(f"🔑 Şifre: {admin_password}")
        else:
            print("❌ Admin kullanıcısı oluşturulamadı!")
        
        print("\n🎉 Veritabanı sıfırlama tamamlandı!")
        print("🚀 Artık temiz bir veritabanıyla başlayabilirsin!")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

def confirm_reset():
    """Kullanıcıdan onay al"""
    print("⚠️  UYARI: Bu işlem mevcut tüm verileri silecek!")
    print("   - Tüm kullanıcılar")
    print("   - Tüm eğitimler") 
    print("   - Tüm öğrenciler")
    print("   - Tüm sertifikalar")
    print()
    
    confirm = input("Devam etmek istediğinizden emin misiniz? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', 'evet']:
        return True
    else:
        print("❌ İşlem iptal edildi.")
        return False

if __name__ == "__main__":
    if confirm_reset():
        reset_database() 
#!/usr/bin/env python3
"""
Admin kullanıcısı oluşturma scripti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from db.database import init_db
from services.auth_service import AuthService

# .env dosyasını yükle
load_dotenv()

def create_admin_user():
    """İlk admin kullanıcısını oluşturur"""
    print("Admin kullanıcısı oluşturuluyor...")
    
    # Veritabanını başlat
    init_db()
    
    # .env dosyasından admin bilgilerini al
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Admin kullanıcısı oluştur
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
        print("🔑 Şifre: .env dosyasında tanımlı")
        print("⚠️  Güvenlik için şifreyi düzenli olarak değiştirmeyi unutmayın!")
    else:
        print("❌ Admin kullanıcısı oluşturulamadı!")
        print("💡 Kullanıcı zaten mevcut olabilir.")

if __name__ == "__main__":
    create_admin_user() 
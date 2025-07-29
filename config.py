import os
from dotenv import load_dotenv
import streamlit as st

# .env dosyasını yükle (yerel geliştirme için)
load_dotenv()

# Streamlit secrets'a erişim için yardımcı fonksiyon
def get_secret(key, default_value=""):
    """Streamlit secrets veya environment variable'dan değer al"""
    try:
        # Önce Streamlit secrets'tan dene
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Sonra environment variable'dan dene
    return os.getenv(key, default_value)

# Uygulama ayarları
APP_TITLE = "Sertifika Yönetim Sistemi"
APP_ICON = "📜"

# Veritabanı ayarları - Streamlit.io için SQLite kullan
default_db = "sqlite:///certificate_app.db"
DATABASE_URL = get_secret("DATABASE_URL", default_db)

# JWT ayarları
JWT_SECRET = get_secret("JWT_SECRET", "PXn7KDollarMEqualsph8CaretPA-NhCsDotPercentCHAe52DSlashSlashYZq0XFSlashP3rxm9JfA6i9y7T-g")
JWT_ISSUER = get_secret("JWT_ISSUER", "https://genczeka.streamlit.app")
JWT_AUDIENCE = get_secret("JWT_AUDIENCE", "https://genczeka.streamlit.app")
JWT_EXPIRY_HOURS = int(get_secret("JWT_EXPIRY_HOURS", "60"))

# Dosya depolama ayarları - Streamlit.io için "local" kullan
STORAGE_TYPE = get_secret("STORAGE_TYPE", "local")  # 'local' veya 's3'
STORAGE_PATH = get_secret("STORAGE_PATH", "./storage")

# S3 ayarları (opsiyonel)
S3_BUCKET = get_secret("S3_BUCKET", "certificate-files") 
S3_ACCESS_KEY = get_secret("S3_ACCESS_KEY", "")
S3_SECRET_KEY = get_secret("S3_SECRET_KEY", "")
S3_REGION = get_secret("S3_REGION", "")

# E-posta ayarları - Gmail (Artık secrets'tan alınıyor!)
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "587"))
SMTP_USERNAME = get_secret("SMTP_USERNAME", "")  # Secrets'tan alınacak
SMTP_PASSWORD = get_secret("SMTP_PASSWORD", "")  # Secrets'tan alınacak - GÜVENLİ!
SMTP_SENDER_EMAIL = get_secret("SMTP_SENDER_EMAIL", "")  # Secrets'tan alınacak
SMTP_SENDER_NAME = get_secret("SMTP_SENDER_NAME", "Certificate System")

# Uygulama URL'i - Streamlit.io için güncellendi
BASE_URL = get_secret("BASE_URL", "https://genczeka.streamlit.app")

# Sayfa ayarları
PAGES = {
    "login": "Giriş",
    "dashboard": "Ana Sayfa",
    "courses": "Eğitimler",
    "students": "Öğrenciler",
    "certificates": "Sertifikalar",
    "users": "Kullanıcı Yönetimi",
    "profile": "Profil"
}
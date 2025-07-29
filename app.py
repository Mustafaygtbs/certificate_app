import os
import streamlit as st
from datetime import datetime
from db.database import init_db
from utils.auth_helpers import init_session_state
from services.auth_service import AuthService
import config
import login, dashboard, courses, students, certificates, certificate_viewer, users, profile

# CSS ile sidebar navigasyonunu gizle
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Uygulama başlığı ve favicon
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Session state değişkenlerini başlat
init_session_state()

# Veritabanını başlat
init_db()

# Admin kullanıcısını otomatik oluştur (Deploy için kritik!)
def ensure_admin_user():
    """Admin kullanıcısının var olduğundan emin ol, yoksa oluştur"""
    try:
        # Mevcut admin kullanıcısını kontrol et
        from db.database import get_session
        from db.models import User
        
        session = get_session()
        admin_user = session.query(User).filter_by(role="admin").first()
        
        if not admin_user:
            # Admin kullanıcısı yok, oluştur
            admin_username = config.get_secret("ADMIN_USERNAME", "admin")
            admin_email = config.get_secret("ADMIN_EMAIL", "admin@example.com")
            admin_password = config.get_secret("ADMIN_PASSWORD", "admin123")
            
            success = AuthService.register(
                username=admin_username,
                email=admin_email, 
                password=admin_password,
                role="admin"
            )
            
            if success:
                st.success(f"✅ Admin kullanıcısı oluşturuldu: {admin_email}")
        
        session.close()
    except Exception as e:
        # Sessizce geç, deployment'ı bozmasın
        pass

# Admin kullanıcısını kontrol et/oluştur
ensure_admin_user()

# Storage klasörlerini oluştur
os.makedirs("storage/certificate-templates", exist_ok=True)
os.makedirs("storage/certificates", exist_ok=True)

# URL parametrelerini kontrol et (güncellenmiş API)
try:
    params = st.query_params
    certificate_token = params.get("token", None)
except:
    # Eski API için fallback
    try:
        params = st.experimental_get_query_params()
        certificate_token = params.get("token", [None])[0]
    except:
        certificate_token = None

# Sertifika görüntüleme sayfası için özel kontrol
if certificate_token:
    st.session_state["current_page"] = "certificate_viewer"
    st.session_state["certificate_token"] = certificate_token

# Sayfa yönlendirmesi
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"

# Sayfa gösterimi
if st.session_state["current_page"] == "login":
    login.show()
elif st.session_state["current_page"] == "dashboard":
    dashboard.show()
elif st.session_state["current_page"] == "courses":
    courses.show()
elif st.session_state["current_page"] == "students":
    students.show()
elif st.session_state["current_page"] == "certificates":
    certificates.show()
elif st.session_state["current_page"] == "users":
    users.show()
elif st.session_state["current_page"] == "profile":
    profile.show()
elif st.session_state["current_page"] == "certificate_viewer":
    certificate_viewer.show()
else:
    st.session_state["current_page"] = "login"
    login.show()

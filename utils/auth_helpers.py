import jwt
import streamlit as st
import datetime
import config

def check_jwt():
    """
    Kullanıcı oturumunu kontrol eder
    
    Returns:
        True: Giriş yapmış kullanıcı
        False: Giriş yapmamış kullanıcı
    """
    if "token" not in st.session_state or not st.session_state["token"]:
        return False
        
    token = st.session_state["token"]
    
    try:
        # Token doğrulama
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        
        # Kullanıcı bilgilerini session state'e kaydet
        st.session_state["user_id"] = int(payload["sub"])
        st.session_state["email"] = payload["email"]
        st.session_state["username"] = payload["username"]
        st.session_state["role"] = payload["role"]
        
        # Token süresi kontrolü
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.datetime.utcnow().timestamp()
        
        # Süresi dolmuşsa False döndür
        if now_timestamp > exp_timestamp:
            return False
        
        return True
        
    except jwt.ExpiredSignatureError:
        # Token süresi dolmuş
        st.session_state.pop("token", None)
        return False
    except jwt.InvalidTokenError:
        # Geçersiz token
        st.session_state.pop("token", None)
        return False
    except Exception:
        # Beklenmeyen hata
        return False

def auth_required(func):
    """
    Yetkilendirme gerektiren sayfalar için decorator
    
    Args:
        func: Çağrılacak fonksiyon
    
    Returns:
        Wrapper fonksiyon
    """
    def wrapper(*args, **kwargs):
        if not check_jwt():
            st.warning("Bu sayfayı görüntülemek için giriş yapmalısınız!")
            
            # Login sayfasına yönlendir
            st.session_state["current_page"] = "login"
            import login
            return login.show()
        
        # Yetkilendirme başarılı, orijinal fonksiyonu çağır
        return func(*args, **kwargs)
    
    return wrapper

def admin_required(func):
    """
    Yönetici yetkisi gerektiren sayfalar için decorator
    
    Args:
        func: Çağrılacak fonksiyon
    
    Returns:
        Wrapper fonksiyon
    """
    def wrapper(*args, **kwargs):
        if not check_jwt():
            st.warning("Bu sayfayı görüntülemek için giriş yapmalısınız!")
            
            # Login sayfasına yönlendir
            st.session_state["current_page"] = "login"
            import login
            return login.show()
            
        # Admin yetkisi kontrol et
        if st.session_state.get("role") != "admin":
            st.error("Bu sayfayı görüntülemek için yönetici yetkisine sahip olmalısınız!")
            
            # Dashboard sayfasına yönlendir
            st.session_state["current_page"] = "dashboard"
            import dashboard
            return dashboard.show()
        
        # Yetkilendirme başarılı, orijinal fonksiyonu çağır
        return func(*args, **kwargs)
    
    return wrapper

def init_session_state():
    """
    Uygulama başlatıldığında session state değişkenlerini ayarlar
    """
    # Sayfa yönlendirme
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"
        
    # Kullanıcı bilgileri
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
        
    if "username" not in st.session_state:
        st.session_state["username"] = None
        
    if "email" not in st.session_state:
        st.session_state["email"] = None
        
    if "role" not in st.session_state:
        st.session_state["role"] = None
        
    if "token" not in st.session_state:
        st.session_state["token"] = None

def logout():
    """
    Kullanıcı oturumunu sonlandırır
    """
    # Kullanıcı bilgilerini temizle
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["email"] = None
    st.session_state["role"] = None
    st.session_state["token"] = None
    
    # Login sayfasına yönlendir
    st.session_state["current_page"] = "login"

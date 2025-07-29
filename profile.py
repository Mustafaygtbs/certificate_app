import streamlit as st
from utils.auth_helpers import auth_required
from services.auth_service import AuthService

@auth_required
def show():
    """Kullanıcı profil sayfasını gösterir"""
    
    # Sol üst köşeye ana sayfa butonu
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    
    st.title("👤 Profil")
    
    # Kullanıcı bilgileri
    st.sidebar.success(f"Hoş geldiniz, {st.session_state['username']}!")
    
    # Mevcut kullanıcı bilgilerini al
    user_id = st.session_state.get('user_id')
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        st.error("Kullanıcı bilgileri bulunamadı!")
        return
    
    # Tab'lar
    tab1, tab2 = st.tabs(["📋 Bilgilerim", "🔐 Şifre Değiştir"])
    
    with tab1:
        st.header("Kullanıcı Bilgileri")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Kullanıcı Adı:** {user['username']}")
            st.info(f"**E-posta:** {user['email']}")
        
        with col2:
            st.info(f"**Rol:** {'🔑 Yönetici' if user['role'] == 'admin' else '👤 Kullanıcı'}")
            st.info(f"**Kayıt Tarihi:** {user['created_at'].strftime('%d.%m.%Y %H:%M')}")
    
    with tab2:
        st.header("Şifre Değiştir")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Mevcut Şifre", type="password", key="current_password")
            new_password = st.text_input("Yeni Şifre", type="password", key="new_password")
            confirm_password = st.text_input("Yeni Şifre (Tekrar)", type="password", key="confirm_password")
            
            # Şifre gereksinimleri
            st.write("**Şifre Gereksinimleri:**")
            st.write("- En az 8 karakter")
            st.write("- En az 1 büyük harf")
            st.write("- En az 1 küçük harf")
            st.write("- En az 1 rakam")
            
            submitted = st.form_submit_button("🔐 Şifre Değiştir")
            
            if submitted:
                # Validasyonlar
                if not current_password or not new_password or not confirm_password:
                    st.error("Tüm alanları doldurunuz!")
                elif new_password != confirm_password:
                    st.error("Yeni şifreler eşleşmiyor!")
                elif len(new_password) < 8:
                    st.error("Yeni şifre en az 8 karakter olmalıdır!")
                elif not any(c.isupper() for c in new_password):
                    st.error("Yeni şifre en az 1 büyük harf içermelidir!")
                elif not any(c.islower() for c in new_password):
                    st.error("Yeni şifre en az 1 küçük harf içermelidir!")
                elif not any(c.isdigit() for c in new_password):
                    st.error("Yeni şifre en az 1 rakam içermelidir!")
                else:
                    # Şifre değiştir
                    if AuthService.change_password(user_id, current_password, new_password):
                        st.success("Şifreniz başarıyla değiştirildi!")
                        st.balloons()
                    else:
                        st.error("Şifre değiştirilemedi! Mevcut şifrenizi kontrol edin.")

def validate_password_strength(password):
    """
    Şifre gücünü kontrol eder
    
    Args:
        password: Kontrol edilecek şifre
        
    Returns:
        (bool, str): (Geçerli mi?, Hata mesajı)
    """
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır!"
    
    if not any(c.isupper() for c in password):
        return False, "Şifre en az 1 büyük harf içermelidir!"
    
    if not any(c.islower() for c in password):
        return False, "Şifre en az 1 küçük harf içermelidir!"
    
    if not any(c.isdigit() for c in password):
        return False, "Şifre en az 1 rakam içermelidir!"
    
    return True, "Şifre geçerli!" 
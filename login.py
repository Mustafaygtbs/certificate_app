import streamlit as st
from services.auth_service import AuthService

def show():
    """Login sayfasını gösterir"""
    
    st.title("Sertifika Yönetim Sistemi")
    
    # Oturum durumunu kontrol et
    if "token" in st.session_state and st.session_state["token"]:
        from utils.auth_helpers import check_jwt
        jwt_valid = check_jwt()
        if jwt_valid:
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        else:
            st.session_state.pop("token", None)
    
    # Login formu
    with st.form("login_form"):
        st.subheader("Giriş Yap")
        
        email = st.text_input("E-posta", key="login_email")
        password = st.text_input("Şifre", type="password", key="login_password")
        
        submitted = st.form_submit_button("Giriş Yap")
        
        if submitted:
            if not email or not password:
                st.error("Lütfen e-posta ve şifre girin!")
                return
                
            # Login işlemi
            auth_service = AuthService()
            result = auth_service.login(email, password)
            
            if result:
                # Başarılı giriş
                st.session_state["token"] = result["token"]
                st.session_state["user_id"] = result["user_id"]
                st.session_state["username"] = result["username"]
                st.session_state["email"] = result["email"]
                st.session_state["role"] = result["role"]
                
                st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                st.session_state["current_page"] = "dashboard"
                st.rerun()
            else:
                # Başarısız giriş
                st.error("Geçersiz e-posta veya şifre!")

import streamlit as st
from utils.auth_helpers import auth_required, admin_required
from services.auth_service import AuthService
from services.email_service import EmailService
import secrets
import string

@admin_required
def show():
    """Kullanıcı yönetimi sayfasını gösterir (sadece admin)"""
    
    # Sol üst köşeye ana sayfa butonu
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    
    st.title("👥 Kullanıcı Yönetimi")
    
    # Kullanıcı bilgileri
    st.sidebar.success(f"Hoş geldiniz, {st.session_state['username']}!")
    
    # Tab'lar
    tab1, tab2 = st.tabs(["📋 Kullanıcı Listesi", "➕ Yeni Kullanıcı Ekle"])
    
    with tab1:
        st.header("Mevcut Kullanıcılar")
        
        # Kullanıcıları listele
        users = AuthService.get_all_users()
        
        if users:
            for user in users:
                with st.expander(f"👤 {user['username']} ({user['email']})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**E-posta:** {user['email']}")
                        st.write(f"**Rol:** {'🔑 Admin' if user['role'] == 'admin' else '👤 Kullanıcı'}")
                        st.write(f"**Kayıt Tarihi:** {user['created_at']}")
                    
                    with col2:
                        # Rol değiştirme
                        new_role = st.selectbox(
                            "Rol", 
                            ["user", "admin"], 
                            index=0 if user['role'] == 'user' else 1,
                            key=f"role_{user['id']}"
                        )
                        
                        if st.button("🔄 Rol Güncelle", key=f"update_role_{user['id']}"):
                            if AuthService.update_user_role(user['id'], new_role):
                                st.success("Rol başarıyla güncellendi!")
                                st.rerun()
                            else:
                                st.error("Rol güncellenirken hata oluştu!")
                    
                    with col3:
                        # Şifre sıfırlama
                        if st.button("🔄 Şifre Sıfırla", key=f"reset_password_{user['id']}"):
                            new_password = generate_random_password()
                            if AuthService.reset_user_password(user['id'], new_password):
                                # E-posta gönder
                                email_service = EmailService()
                                if send_password_email(email_service, user['email'], user['username'], new_password):
                                    st.success("Yeni şifre e-posta ile gönderildi!")
                                else:
                                    st.warning(f"Şifre güncellendi ama e-posta gönderilemedi. Yeni şifre: {new_password}")
                                st.rerun()
                            else:
                                st.error("Şifre sıfırlanırken hata oluştu!")
                        
                        # Kullanıcı silme (kendini silemez)
                        if user['id'] != st.session_state.get('user_id'):
                            if st.button("🗑️ Sil", key=f"delete_user_{user['id']}"):
                                if AuthService.delete_user(user['id']):
                                    st.success("Kullanıcı başarıyla silindi!")
                                    st.rerun()
                                else:
                                    st.error("Kullanıcı silinirken hata oluştu!")
        else:
            st.info("Henüz hiç kullanıcı yok.")
    
    with tab2:
        st.header("Yeni Kullanıcı Ekle")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Kullanıcı Adı", key="new_username")
                email = st.text_input("E-posta", key="new_email")
            
            with col2:
                role = st.selectbox("Rol", ["user", "admin"], key="new_role")
                send_email = st.checkbox("E-posta ile şifre gönder", value=True, key="send_email")
            
            submitted = st.form_submit_button("👤 Kullanıcı Ekle")
            
            if submitted:
                if not username or not email:
                    st.error("Kullanıcı adı ve e-posta alanları zorunludur!")
                else:
                    # Rastgele şifre oluştur
                    password = generate_random_password()
                    
                    # Kullanıcı ekle
                    if AuthService.register(username, email, password, role):
                        st.success(f"Kullanıcı başarıyla eklendi!")
                        
                        # E-posta gönder
                        if send_email:
                            email_service = EmailService()
                            if send_welcome_email(email_service, email, username, password):
                                st.success("Hoş geldin e-postası gönderildi!")
                            else:
                                st.warning(f"Kullanıcı eklendi ama e-posta gönderilemedi. Şifre: {password}")
                        else:
                            st.info(f"Kullanıcı şifresi: {password}")
                        
                        st.rerun()
                    else:
                        st.error("Kullanıcı eklenirken hata oluştu! Bu e-posta adresi zaten kullanımda olabilir.")

def generate_random_password(length=12):
    """Rastgele güvenli şifre oluşturur"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_welcome_email(email_service, to_email, username, password):
    """Hoş geldin e-postası gönderir"""
    subject = "Sertifika Yönetim Sistemi - Hesap Bilgileriniz"
    
    body = f"""
    <html>
    <body>
    <h2>🎉 Hoş Geldiniz!</h2>
    <p>Merhaba <strong>{username}</strong>,</p>
    
    <p>Sertifika Yönetim Sistemi'ne hoş geldiniz! Hesabınız başarıyla oluşturuldu.</p>
    
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>🔐 Giriş Bilgileriniz:</h3>
        <p><strong>Kullanıcı Adı:</strong> {username}</p>
        <p><strong>E-posta:</strong> {to_email}</p>
        <p><strong>Geçici Şifre:</strong> <code style="background-color: #e9ecef; padding: 2px 5px;">{password}</code></p>
    </div>
    
    <p>⚠️ <strong>Önemli:</strong> İlk girişinizden sonra şifrenizi değiştirmenizi önemle tavsiye ederiz.</p>
    
    <p>Sisteme giriş yapmak için aşağıdaki adımları takip edin:</p>
    <ol>
        <li>Giriş sayfasına gidin</li>
        <li>E-posta adresinizi ve geçici şifrenizi girin</li>
        <li>Giriş yaptıktan sonra şifrenizi değiştirin</li>
    </ol>
    
    <p>Herhangi bir sorunuz varsa lütfen bizimle iletişime geçin.</p>
    
    <p>İyi çalışmalar!<br>
    <strong>Sertifika Yönetim Sistemi</strong></p>
    </body>
    </html>
    """
    
    return email_service.send_email(to_email, subject, body)

def send_password_email(email_service, to_email, username, new_password):
    """Şifre sıfırlama e-postası gönderir"""
    subject = "Sertifika Yönetim Sistemi - Şifreniz Sıfırlandı"
    
    body = f"""
    <html>
    <body>
    <h2>🔑 Şifreniz Sıfırlandı</h2>
    <p>Merhaba <strong>{username}</strong>,</p>
    
    <p>Şifreniz sistem yöneticisi tarafından sıfırlandı.</p>
    
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>🔐 Yeni Giriş Bilgileriniz:</h3>
        <p><strong>E-posta:</strong> {to_email}</p>
        <p><strong>Yeni Şifre:</strong> <code style="background-color: #e9ecef; padding: 2px 5px;">{new_password}</code></p>
    </div>
    
    <p>⚠️ <strong>Güvenlik İçin:</strong> İlk girişinizden sonra şifrenizi değiştirmenizi önemle tavsiye ederiz.</p>
    
    <p>Eğer bu işlemi siz talep etmediyseniz, lütfen derhal sistem yöneticisi ile iletişime geçin.</p>
    
    <p>İyi çalışmalar!<br>
    <strong>Sertifika Yönetim Sistemi</strong></p>
    </body>
    </html>
    """
    
    return email_service.send_email(to_email, subject, body) 
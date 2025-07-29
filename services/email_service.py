import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
import datetime

class EmailService:
    """E-posta işlemleri için servis sınıfı"""
    
    def __init__(self):
        """
        E-posta servisi başlatma
        """
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.smtp_username = config.SMTP_USERNAME
        self.smtp_password = config.SMTP_PASSWORD
        self.sender_email = config.SMTP_SENDER_EMAIL
        self.sender_name = config.SMTP_SENDER_NAME
        
        # E-posta ayarlarını logla
        print(f"[EMAIL SERVICE] SMTP Server: {self.smtp_server}")
        print(f"[EMAIL SERVICE] SMTP Port: {self.smtp_port}")
        print(f"[EMAIL SERVICE] SMTP Username: {self.smtp_username}")
        print(f"[EMAIL SERVICE] Sender Email: {self.sender_email}")
        print(f"[EMAIL SERVICE] Sender Name: {self.sender_name}")
    
    def send_email(self, to, subject, body, is_html=True):
        """
        E-posta gönderir
        
        Args:
            to: Alıcı e-posta adresi
            subject: E-posta konusu
            body: E-posta içeriği
            is_html: HTML formatında mı? (varsayılan: True)
            
        Returns:
            Başarılı gönderim durumunda True, başarısız durumda False
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[EMAIL SERVICE] [{timestamp}] E-posta gönderimi başlatılıyor...")
        print(f"[EMAIL SERVICE] [{timestamp}] Alıcı: {to}")
        print(f"[EMAIL SERVICE] [{timestamp}] Konu: {subject}")
        print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - SMTP Username: {self.smtp_username}")
        print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - SMTP Password Length: {len(self.smtp_password) if self.smtp_password else 0}")
        
        try:
            # E-posta ayarları yoksa uyarı ver ve çık
            if not self.smtp_server or not self.smtp_username or not self.smtp_password:
                print(f"[EMAIL SERVICE] [{timestamp}] HATA: E-posta ayarları yapılandırılmamış!")
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP Server: {self.smtp_server}")
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP Username: {self.smtp_username}")
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP Password: {'***' if self.smtp_password else 'None'}")
                return False
                
            print(f"[EMAIL SERVICE] [{timestamp}] SMTP bağlantısı kuruluyor...")
            
            # E-posta oluştur
            message = MIMEMultipart()
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to
            message["Subject"] = subject
            
            # İçerik türünü ayarla
            if is_html:
                message.attach(MIMEText(body, "html"))
                print(f"[EMAIL SERVICE] [{timestamp}] HTML formatında e-posta oluşturuldu")
            else:
                message.attach(MIMEText(body, "plain"))
                print(f"[EMAIL SERVICE] [{timestamp}] Plain text formatında e-posta oluşturuldu")
            
            print(f"[EMAIL SERVICE] [{timestamp}] SMTP sunucusuna bağlanılıyor: {self.smtp_server}:{self.smtp_port}")
            
            # E-posta gönder
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP bağlantısı başarılı")
                print(f"[EMAIL SERVICE] [{timestamp}] TLS başlatılıyor...")
                server.starttls()  # TLS güvenliği
                print(f"[EMAIL SERVICE] [{timestamp}] TLS başarılı")
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP girişi yapılıyor...")
                print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - Giriş denemesi: {self.smtp_username}")
                server.login(self.smtp_username, self.smtp_password)
                print(f"[EMAIL SERVICE] [{timestamp}] SMTP girişi başarılı")
                print(f"[EMAIL SERVICE] [{timestamp}] E-posta gönderiliyor...")
                server.send_message(message)
                print(f"[EMAIL SERVICE] [{timestamp}] ✅ E-posta başarıyla gönderildi!")
                
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ SMTP Kimlik Doğrulama Hatası: {str(e)}")
            print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - Bu hata genellikle şu nedenlerden kaynaklanır:")
            print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - 1. 2 Adımlı Doğrulama açık değil")
            print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - 2. App Password kullanılmıyor")
            print(f"[EMAIL SERVICE] [{timestamp}] DEBUG - 3. 'Daha az güvenli uygulama erişimi' kapalı")
            return False
        except smtplib.SMTPConnectError as e:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ SMTP Bağlantı Hatası: {str(e)}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ Alıcı Reddedildi: {str(e)}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ SMTP Sunucu Bağlantısı Kesildi: {str(e)}")
            return False
        except Exception as e:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ E-posta gönderme hatası: {str(e)}")
            print(f"[EMAIL SERVICE] [{timestamp}] Hata türü: {type(e).__name__}")
            return False
    
    def send_certificate_email(self, to, student_name, certificate_link):
        """
        Sertifika e-postası gönderir
        
        Args:
            to: Alıcı e-posta adresi
            student_name: Öğrenci adı
            certificate_link: Sertifika erişim linki
            
        Returns:
            Başarılı gönderim durumunda True, başarısız durumda False
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[EMAIL SERVICE] [{timestamp}] Sertifika e-postası gönderiliyor...")
        print(f"[EMAIL SERVICE] [{timestamp}] Öğrenci: {student_name}")
        print(f"[EMAIL SERVICE] [{timestamp}] Sertifika Linki: {certificate_link}")
        
        subject = "Eğitim Sertifikanız Hazır!"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="text-align: center; padding: 10px; background-color: #f8f9fa; margin-bottom: 20px;">
                    <h2 style="color: #2c3e50;">Tebrikler, {student_name}!</h2>
                </div>
                
                <p>Eğitimi başarıyla tamamladınız ve sertifikanız hazır.</p>
                
                <p>Sertifikanızı görüntülemek ve indirmek için aşağıdaki bağlantıya tıklayın:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{certificate_link}" style="background-color: #3498db; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">Sertifikanızı Görüntüleyin</a>
                </div>
                
                <p>Bu link size özeldir ve sertifikanızın doğruluğunu ispat etmek için kullanılabilir.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #777; text-align: center;">
                    Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıtlamayınız.
                </p>
            </div>
        </body>
        </html>
        """
        
        result = self.send_email(to, subject, body)
        
        if result:
            print(f"[EMAIL SERVICE] [{timestamp}] ✅ Sertifika e-postası başarıyla gönderildi: {to}")
        else:
            print(f"[EMAIL SERVICE] [{timestamp}] ❌ Sertifika e-postası gönderilemedi: {to}")
        
        return result

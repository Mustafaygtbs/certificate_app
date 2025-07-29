from sqlalchemy.exc import SQLAlchemyError
from db.database import get_session
from db.models import User
import bcrypt
import jwt
import datetime
import config

class AuthService:
    """Kimlik doğrulama işlemleri için servis sınıfı"""
    
    @staticmethod
    def login(email, password):
        """
        Kullanıcı girişi yapar
        
        Args:
            email: Kullanıcı e-posta adresi
            password: Şifre
            
        Returns:
            Başarılı giriş durumunda token ve kullanıcı bilgileri, başarısız durumda None
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.email == email).first()
            
            if not user:
                return None
                
            # Şifre kontrolü
            if not AuthService.verify_password(password, user.password_hash):
                return None
                
            # JWT token oluştur
            token = AuthService.generate_token(user)
            
            return {
                "token": token,
                "user_id": user.id,  # User ID'yi de döndür
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def register(username, email, password, role="user"):
        """
        Yeni kullanıcı kaydı yapar
        
        Args:
            username: Kullanıcı adı
            email: E-posta adresi
            password: Şifre
            role: Kullanıcı rolü (varsayılan: "user")
            
        Returns:
            Başarılı kayıt durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            
            # E-posta adresi kontrol et
            existing_user = session.query(User).filter(User.email == email).first()
            if existing_user:
                return False
                
            # Şifreyi hash'le
            password_hash = AuthService.hash_password(password)
            
            # Yeni kullanıcı oluştur
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role
            )
            
            session.add(new_user)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Kullanıcı şifresini değiştirir
        
        Args:
            user_id: Kullanıcı ID
            current_password: Mevcut şifre
            new_password: Yeni şifre
            
        Returns:
            Başarılı değişiklik durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
                
            # Mevcut şifre kontrolü
            if not AuthService.verify_password(current_password, user.password_hash):
                return False
                
            # Yeni şifreyi hash'le
            user.password_hash = AuthService.hash_password(new_password)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def hash_password(password):
        """
        Şifreyi hash'ler
        
        Args:
            password: Hash'lenecek şifre
            
        Returns:
            Hash'lenmiş şifre
        """
        # Önce string'i byte'a çevir
        password_bytes = password.encode('utf-8')
        # Salt oluştur ve şifreyi hash'le
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Byte'ı string'e çevir
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """
        Şifre doğrulaması yapar
        
        Args:
            password: Kontrol edilecek şifre
            hashed_password: Hash'lenmiş şifre
            
        Returns:
            Şifre doğruysa True, yanlışsa False
        """
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def generate_token(user):
        """
        JWT token oluşturur
        
        Args:
            user: Token oluşturulacak kullanıcı
            
        Returns:
            JWT token (string formatında)
        """
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=config.JWT_EXPIRY_HOURS)
        
        payload = {
            'sub': str(user.id),  # PyJWT için string'e çevir!
            'email': user.email,
            'username': user.username,
            'role': user.role,
            'exp': expiry
        }
        
        # PyJWT modern versiyon için string döndür
        token = jwt.encode(payload, config.JWT_SECRET, algorithm='HS256')
        
        # PyJWT 2.0+ versiyonunda encode string döndürür, bytes değil
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        return token
    
    @staticmethod
    def verify_token(token):
        """
        JWT token doğrular
        
        Args:
            token: Doğrulanacak JWT token
            
        Returns:
            Token geçerliyse payload, geçersizse None
        """
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token süresi dolmuş")
            return None
        except jwt.InvalidTokenError:
            print("Geçersiz token")
            return None
    
    @staticmethod
    def check_admin_exists():
        """
        Admin kullanıcısının var olup olmadığını kontrol eder
        
        Returns:
            Admin kullanıcısı varsa True, yoksa False
        """
        try:
            session = get_session()
            admin_user = session.query(User).filter(User.role == "admin").first()
            return admin_user is not None
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def create_default_admin():
        """
        Varsayılan admin kullanıcısını oluşturur
        
        Returns:
            Başarılı oluşturma durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            
            # Admin kullanıcısı zaten var mı kontrol et
            existing_admin = session.query(User).filter(User.role == "admin").first()
            if existing_admin:
                return True
                
            # Varsayılan admin kullanıcısını oluştur
            success = AuthService.register(
                username="admin",
                email="admin@example.com", 
                password="admin123",
                role="admin"
            )
            
            if success:
                print("✅ Varsayılan admin kullanıcısı oluşturuldu!")
                print("📧 E-posta: admin@example.com")
                print("🔑 Şifre: admin123")
                print("⚠️  Güvenlik için şifreyi değiştirmeyi unutmayın!")
            
            return success
        except SQLAlchemyError as e:
            print(f"Admin oluşturma hatası: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def get_all_users():
        """
        Tüm kullanıcıları listeler
        
        Returns:
            Kullanıcı listesi
        """
        try:
            session = get_session()
            users = session.query(User).all()
            
            user_list = []
            for user in users:
                user_list.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            return user_list
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def update_user_role(user_id, new_role):
        """
        Kullanıcı rolünü günceller
        
        Args:
            user_id: Kullanıcı ID
            new_role: Yeni rol ("user" veya "admin")
            
        Returns:
            Başarılı güncelleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            user.role = new_role
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def reset_user_password(user_id, new_password):
        """
        Kullanıcı şifresini sıfırlar
        
        Args:
            user_id: Kullanıcı ID
            new_password: Yeni şifre
            
        Returns:
            Başarılı güncelleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            # Şifreyi hash'le
            password_hash = AuthService.hash_password(new_password)
            user.password_hash = password_hash
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def delete_user(user_id):
        """
        Kullanıcıyı siler
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Başarılı silme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            session.delete(user)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Kullanıcıyı ID ile getirir
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            Kullanıcı bilgileri, bulunamazsa None
        """
        try:
            session = get_session()
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at
            }
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()

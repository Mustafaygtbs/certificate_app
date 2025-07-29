from sqlalchemy.exc import SQLAlchemyError
from db.database import get_session
from db.models import Student, Course
import uuid
import pandas as pd
import io
import config
from services.file_service import FileService
from services.email_service import EmailService
import datetime

class StudentService:
    """Öğrenci işlemleri için servis sınıfı"""
    
    @staticmethod
    def get_students_by_course(course_id):
        """
        Eğitime kayıtlı öğrencileri listeler
        
        Args:
            course_id: Eğitim ID'si
            
        Returns:
            Öğrenci listesi
        """
        try:
            session = get_session()
            
            # Önce kursun var olduğunu kontrol et
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise KeyError(f"Eğitim bulunamadı: ID {course_id}")
                
            students = session.query(Student).filter(Student.course_id == course_id).all()
            
            result = []
            for student in students:
                result.append({
                    "id": student.id,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "email": student.email,
                    "phone_number": student.phone_number,
                    "has_completed_course": student.has_completed_course,
                    "certificate_url": student.certificate_url,
                    "certificate_access_token": student.certificate_access_token,
                    "course_id": student.course_id,
                    "course_name": course.name
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def get_student_by_id(student_id):
        """
        ID'ye göre öğrenci bilgilerini getirir
        
        Args:
            student_id: Öğrenci ID'si
            
        Returns:
            Öğrenci bilgileri, bulunamazsa None
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return None
                
            course = session.query(Course).filter(Course.id == student.course_id).first()
            
            return {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "phone_number": student.phone_number,
                "has_completed_course": student.has_completed_course,
                "certificate_url": student.certificate_url,
                "certificate_access_token": student.certificate_access_token,
                "course_id": student.course_id,
                "course_name": course.name if course else ""
            }
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_student_by_token(token):
        """
        Sertifika erişim tokeni ile öğrenci bilgilerini getirir
        
        Args:
            token: Sertifika erişim tokeni
            
        Returns:
            Öğrenci bilgileri, bulunamazsa None
        """
        try:
            session = get_session()
            student = session.query(Student).filter(
                Student.certificate_access_token == token
            ).first()
            
            if not student:
                return None
                
            course = session.query(Course).filter(Course.id == student.course_id).first()
            
            return {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "phone_number": student.phone_number,
                "has_completed_course": student.has_completed_course,
                "certificate_url": student.certificate_url,
                "certificate_access_token": student.certificate_access_token,
                "course_id": student.course_id,
                "course_name": course.name if course else ""
            }
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def create_student(student_data):
        """
        Yeni öğrenci oluşturur
        
        Args:
            student_data: Öğrenci bilgileri
            
        Returns:
            Başarılı oluşturma durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            
            # Eğitim kontrol et
            course = session.query(Course).filter(Course.id == student_data["course_id"]).first()
            if not course:
                raise KeyError(f"Eğitim bulunamadı: ID {student_data['course_id']}")
                
            # E-posta+kurs kontrolü (aynı e-posta ile aynı kursa iki kez kaydolamaz)
            existing_student = session.query(Student).filter(
                Student.email == student_data["email"],
                Student.course_id == student_data["course_id"]
            ).first()
            
            if existing_student:
                print(f"Bu e-posta adresi ile aynı kursa daha önce kayıt yapılmış: {student_data['email']}")
                return False
                
            new_student = Student(
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                email=student_data["email"],
                phone_number=student_data.get("phone_number", ""),
                has_completed_course=student_data.get("has_completed_course", False),
                certificate_url=student_data.get("certificate_url", ""),
                course_id=student_data["course_id"],
                certificate_access_token=str(uuid.uuid4())
            )
            
            session.add(new_student)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        except KeyError as e:
            print(str(e))
            return False
        finally:
            session.close()
    
    @staticmethod
    def update_student(student_id, student_data):
        """
        Öğrenci bilgilerini günceller
        
        Args:
            student_id: Güncellenecek öğrenci ID'si
            student_data: Güncellenecek öğrenci bilgileri
            
        Returns:
            Başarılı güncelleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                raise KeyError(f"Öğrenci bulunamadı: ID {student_id}")
                
            student.first_name = student_data.get("first_name", student.first_name)
            student.last_name = student_data.get("last_name", student.last_name)
            student.email = student_data.get("email", student.email)
            student.phone_number = student_data.get("phone_number", student.phone_number)
            student.has_completed_course = student_data.get("has_completed_course", student.has_completed_course)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        except KeyError as e:
            print(str(e))
            return False
        finally:
            session.close()
    
    @staticmethod
    def delete_student(student_id):
        """
        Öğrenciyi siler
        
        Args:
            student_id: Silinecek öğrenci ID'si
            
        Returns:
            Başarılı silme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                raise KeyError(f"Öğrenci bulunamadı: ID {student_id}")
                
            session.delete(student)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        except KeyError as e:
            print(str(e))
            return False
        finally:
            session.close()
    
    @staticmethod
    def import_students_from_excel(course_id, file_content):
        """
        Excel dosyasından öğrenci bilgilerini içe aktarır
        
        Args:
            course_id: Eğitim ID'si
            file_content: Excel dosyası içeriği (BytesIO)
            
        Returns:
            Başarılı içe aktarma durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            
            # Eğitim kontrolü
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise KeyError(f"Eğitim bulunamadı: ID {course_id}")
                
            # Excel'i pandas ile oku
            df = pd.read_excel(file_content)
            
            # Gerekli sütunların var olduğunu kontrol et
            required_columns = ["Ad", "Soyad"]  # E-posta artık zorunlu değil
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Excel dosyasında gerekli sütun bulunamadı: {col}")
            
            # Her satır için öğrenci ekle
            for _, row in df.iterrows():
                first_name = str(row["Ad"]).strip()
                last_name = str(row["Soyad"]).strip()
                
                # E-posta sütunu varsa al
                email = ""
                if "E-posta" in df.columns:
                    email = str(row["E-posta"]).strip()
                
                # Telefon sütunu varsa al
                phone_number = ""
                if "Telefon" in df.columns:
                    phone_number = str(row["Telefon"]).strip()
                
                # Tamamlama durumu sütunu varsa al
                has_completed = False
                if "Eğitimi Tamamladı" in df.columns:
                    has_completed_val = row["Eğitimi Tamamladı"]
                    if isinstance(has_completed_val, bool):
                        has_completed = has_completed_val
                    elif isinstance(has_completed_val, str):
                        has_completed = has_completed_val.lower() in ["true", "evet", "1", "yes"]
                
                # Boş ad alanlarını atla (e-posta artık zorunlu değil)
                if not first_name:
                    continue
                
                # E-posta kontrolü kaldırıldı - artık aynı e-posta ile aynı kursa kayıt yapılabilir
                
                # Yeni öğrenci ekle
                new_student = Student(
                    first_name=first_name,
                    last_name=last_name,
                    email=email if email and email != 'nan' else "",  # E-posta opsiyonel
                    phone_number=phone_number,
                    has_completed_course=has_completed,
                    course_id=course_id,
                    certificate_access_token=str(uuid.uuid4())
                )
                
                session.add(new_student)
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        except (KeyError, ValueError) as e:
            print(str(e))
            return False
        except Exception as e:
            print(f"Excel okuma hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def mark_student_as_completed(student_id):
        """
        Öğrenciyi eğitimi tamamlamış olarak işaretler
        
        Args:
            student_id: Öğrenci ID'si
            
        Returns:
            Başarılı işaretleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return False
                
            student.has_completed_course = True
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def mark_student_as_not_completed(student_id):
        """
        Öğrenciyi eğitimi tamamlamamış olarak işaretler
        
        Args:
            student_id: Öğrenci ID'si
            
        Returns:
            Başarılı işaretleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                return False
                
            student.has_completed_course = False
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def send_certificate_email(student_id):
        """
        Öğrenciye sertifika e-postası gönderir
        
        Args:
            student_id: Öğrenci ID'si
            
        Returns:
            Başarılı gönderim durumunda True, başarısız durumda False
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[STUDENT SERVICE] [{timestamp}] Sertifika e-postası gönderimi başlatılıyor...")
        print(f"[STUDENT SERVICE] [{timestamp}] Öğrenci ID: {student_id}")
        
        try:
            session = get_session()
            student = session.query(Student).filter(Student.id == student_id).first()
            
            if not student:
                print(f"[STUDENT SERVICE] [{timestamp}] ❌ Öğrenci bulunamadı: ID {student_id}")
                return False
                
            print(f"[STUDENT SERVICE] [{timestamp}] Öğrenci bulundu: {student.first_name} {student.last_name}")
            print(f"[STUDENT SERVICE] [{timestamp}] E-posta: {student.email}")
            print(f"[STUDENT SERVICE] [{timestamp}] Eğitimi tamamladı mı: {student.has_completed_course}")
            
            if not student.has_completed_course:
                print(f"[STUDENT SERVICE] [{timestamp}] ❌ Öğrenci eğitimi tamamlamamış!")
                return False
                
            course = session.query(Course).filter(Course.id == student.course_id).first()
            if not course:
                print(f"[STUDENT SERVICE] [{timestamp}] ❌ Eğitim bulunamadı: ID {student.course_id}")
                return False
                
            print(f"[STUDENT SERVICE] [{timestamp}] Eğitim bulundu: {course.name}")
            print(f"[STUDENT SERVICE] [{timestamp}] Sertifika URL: {student.certificate_url}")
            
            # Sertifika yoksa oluştur
            if not student.certificate_url:
                print(f"[STUDENT SERVICE] [{timestamp}] Sertifika oluşturuluyor...")
                file_service = FileService()
                email_service = EmailService()
                
                # Sertifika için değiştirilecek alanlar
                replacements = {
                    "{{ogrenci_adi}}": f"{student.first_name} {student.last_name}",
                    "{{kurs_adi}}": course.name,
                    "{{egitmen_adi}}": course.instructor_name or "Eğitmen Adı",
                    "{{tarih}}": datetime.datetime.now().strftime("%d.%m.%Y"),
                    "{{sertifika_no}}": f"{datetime.datetime.now().strftime('%Y%m%d')}{student.id:04d}"
                }
                
                print(f"[STUDENT SERVICE] [{timestamp}] Sertifika şablonu: {course.certificate_template_url}")
                print(f"[STUDENT SERVICE] [{timestamp}] Değiştirilecek alanlar: {replacements}")
                
                # Sertifika oluştur
                certificate_path = file_service.generate_certificate(
                    course.certificate_template_url,
                    replacements
                )
                
                if certificate_path:
                    print(f"[STUDENT SERVICE] [{timestamp}] ✅ Sertifika oluşturuldu: {certificate_path}")
                    student.certificate_url = certificate_path
                    session.commit()
                else:
                    print(f"[STUDENT SERVICE] [{timestamp}] ❌ Sertifika oluşturulamadı!")
                    return False
                
                # E-posta gönder
                certificate_link = f"{config.BASE_URL}/?token={student.certificate_access_token}"
                print(f"[STUDENT SERVICE] [{timestamp}] Sertifika linki: {certificate_link}")
                
                email_result = email_service.send_certificate_email(
                    student.email,
                    f"{student.first_name} {student.last_name}",
                    certificate_link
                )
                
                if email_result:
                    print(f"[STUDENT SERVICE] [{timestamp}] ✅ Sertifika e-postası başarıyla gönderildi!")
                else:
                    print(f"[STUDENT SERVICE] [{timestamp}] ❌ Sertifika e-postası gönderilemedi!")
                
                return email_result
            else:
                print(f"[STUDENT SERVICE] [{timestamp}] Sertifika zaten mevcut, sadece e-posta gönderiliyor...")
                # Sertifika zaten var, sadece e-posta gönder
                email_service = EmailService()
                certificate_link = f"{config.BASE_URL}/?token={student.certificate_access_token}"
                print(f"[STUDENT SERVICE] [{timestamp}] Sertifika linki: {certificate_link}")
                
                email_result = email_service.send_certificate_email(
                    student.email,
                    f"{student.first_name} {student.last_name}",
                    certificate_link
                )
                
                if email_result:
                    print(f"[STUDENT SERVICE] [{timestamp}] ✅ Sertifika e-postası başarıyla gönderildi!")
                else:
                    print(f"[STUDENT SERVICE] [{timestamp}] ❌ Sertifika e-postası gönderilemedi!")
                
                return email_result
        except SQLAlchemyError as e:
            session.rollback()
            print(f"[STUDENT SERVICE] [{timestamp}] ❌ Veritabanı hatası: {str(e)}")
            return False
        except Exception as e:
            print(f"[STUDENT SERVICE] [{timestamp}] ❌ Genel hata: {str(e)}")
            print(f"[STUDENT SERVICE] [{timestamp}] Hata türü: {type(e).__name__}")
            return False
        finally:
            session.close()

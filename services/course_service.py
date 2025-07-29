from sqlalchemy.exc import SQLAlchemyError
from db.database import get_session
from db.models import Course, Student
import datetime
import os
import config
from services.file_service import FileService

class CourseService:
    """Eğitim işlemleri için servis sınıfı"""
    
    @staticmethod
    def get_all_courses():
        """
        Tüm eğitimleri listeler
        
        Returns:
            Eğitim listesi
        """
        try:
            session = get_session()
            courses = session.query(Course).all()
            
            result = []
            for course in courses:
                student_count = session.query(Student).filter(Student.course_id == course.id).count()
                
                result.append({
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "instructor_name": course.instructor_name,
                    "start_date": course.start_date,
                    "end_date": course.end_date,
                    "is_completed": course.is_completed,
                    "certificate_template_url": course.certificate_template_url,
                    "student_count": student_count,
                    "created_at": course.created_at
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def get_course_by_id(course_id):
        """
        ID'ye göre eğitim bilgilerini getirir
        
        Args:
            course_id: Eğitim ID
            
        Returns:
            Eğitim bilgileri, bulunamazsa None
        """
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return None
                
            student_count = session.query(Student).filter(Student.course_id == course.id).count()
            
            return {
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "instructor_name": course.instructor_name,
                "start_date": course.start_date,
                "end_date": course.end_date,
                "is_completed": course.is_completed,
                "certificate_template_url": course.certificate_template_url,
                "student_count": student_count,
                "created_at": course.created_at
            }
        except SQLAlchemyError as e:
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def create_course(course_data):
        """
        Yeni eğitim oluşturur
        
        Args:
            course_data: Eğitim bilgileri
            
        Returns:
            Oluşturulan eğitim ID'si, başarısız durumda None
        """
        try:
            session = get_session()
            
            new_course = Course(
                name=course_data["name"],
                description=course_data.get("description", ""),
                instructor_name=course_data.get("instructor_name", ""),
                start_date=course_data["start_date"],
                end_date=course_data["end_date"],
                is_completed=course_data.get("is_completed", False),
                certificate_template_url=course_data.get("certificate_template_url", "")
            )
            
            session.add(new_course)
            session.commit()
            
            return new_course.id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def update_course(course_id, course_data):
        """
        Eğitim bilgilerini günceller
        
        Args:
            course_id: Güncellenecek eğitim ID'si
            course_data: Güncellenecek eğitim bilgileri
            
        Returns:
            Başarılı güncelleme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return False
                
            course.name = course_data.get("name", course.name)
            course.description = course_data.get("description", course.description)
            course.start_date = course_data.get("start_date", course.start_date)
            course.end_date = course_data.get("end_date", course.end_date)
            course.is_completed = course_data.get("is_completed", course.is_completed)
            
            # Şablon URL'i değişmişse güncelle
            new_template = course_data.get("certificate_template_url")
            if new_template and new_template != course.certificate_template_url:
                course.certificate_template_url = new_template
                
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def delete_course(course_id):
        """
        Eğitimi siler
        
        Args:
            course_id: Silinecek eğitim ID'si
            
        Returns:
            Başarılı silme durumunda True, başarısız durumda False
        """
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return False
                
            # Öğrencileri ve sertifikaları da sil (cascade delete)
            session.delete(course)
            session.commit()
            
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def upload_certificate_template(course_id, file_data):
        """
        Eğitim için sertifika şablonu yükler
        
        Args:
            course_id: Eğitim ID'si
            file_data: Yüklenecek dosya
            
        Returns:
            Başarılı yükleme durumunda şablon URL'i, başarısız durumda None
        """
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return None
                
            # Dosya servisi ile şablonu yükle
            file_service = FileService()
            template_url = file_service.upload_file(file_data, "certificate-templates")
            
            if template_url:
                course.certificate_template_url = template_url
                session.commit()
                
            return template_url
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return None
        except Exception as e:
            print(f"Dosya yükleme hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def upload_html_certificate_template(course_id, html_content):
        """
        Eğitim için HTML sertifika şablonu yükler
        
        Args:
            course_id: Eğitim ID'si
            html_content: HTML şablon içeriği
            
        Returns:
            Başarılı yükleme durumunda şablon URL'i, başarısız durumda None
        """
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return None
                
            # HTML içeriğini dosya olarak kaydet
            file_service = FileService()
            template_url = file_service.save_html_template(html_content, course_id)
            
            if template_url:
                course.certificate_template_url = template_url
                session.commit()
                
            return template_url
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return None
        except Exception as e:
            print(f"HTML şablon yükleme hatası: {str(e)}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def complete_course(course_id, email_service=None, file_service=None):
        """
        Eğitimi tamamlar ve sertifika oluşturur
        
        Args:
            course_id: Eğitim ID'si
            email_service: E-posta servisi (opsiyonel)
            file_service: Dosya servisi (opsiyonel)
            
        Returns:
            Başarılı tamamlama durumunda True, başarısız durumda False
        """
        if not email_service:
            from services.email_service import EmailService
            email_service = EmailService()
            
        if not file_service:
            from services.file_service import FileService
            file_service = FileService()
            
        try:
            session = get_session()
            course = session.query(Course).filter(Course.id == course_id).first()
            
            if not course:
                return False
                
            # Eğitimi tamamlandı olarak işaretle
            course.is_completed = True
            
            # Eğitimi tamamlamış öğrencileri bul
            completed_students = session.query(Student).filter(
                Student.course_id == course_id,
                Student.has_completed_course == True
            ).all()
            
            # Her öğrenci için sertifika oluştur ve e-posta gönder
            for student in completed_students:
                # Sertifika için değiştirilecek alanlar
                replacements = {
                    "{{ogrenci_adi}}": f"{student.first_name} {student.last_name}",
                    "{{kurs_adi}}": course.name,
                    "{{egitmen_adi}}": course.instructor_name or "Eğitmen Adı",
                    "{{tarih}}": datetime.datetime.now().strftime("%d.%m.%Y"),
                    "{{sertifika_no}}": f"{datetime.datetime.now().strftime('%Y%m%d')}{student.id:04d}"
                }
                
                # Sertifika oluştur
                certificate_path = file_service.generate_certificate(
                    course.certificate_template_url,
                    replacements
                )
                
                # Öğrenci bilgilerini güncelle
                student.certificate_url = certificate_path
                
                # E-posta gönder
                certificate_link = f"{config.BASE_URL}/?token={student.certificate_access_token}"
                email_service.send_certificate_email(
                    student.email,
                    f"{student.first_name} {student.last_name}",
                    certificate_link
                )
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Veritabanı hatası: {str(e)}")
            return False
        except Exception as e:
            print(f"Sertifika oluşturma hatası: {str(e)}")
            return False
        finally:
            session.close()

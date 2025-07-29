import os
import shutil
from datetime import datetime
import uuid
from PIL import Image, ImageDraw, ImageFont
import io
import config
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class FileService:
    """Dosya işlemleri için servis sınıfı"""
    
    def __init__(self):
        """
        Dosya servisi başlatma
        """
        # Yerel depolama için dizin oluştur
        if config.STORAGE_TYPE == "local":
            os.makedirs(config.STORAGE_PATH, exist_ok=True)
            os.makedirs(os.path.join(config.STORAGE_PATH, "certificate-templates"), exist_ok=True)
            os.makedirs(os.path.join(config.STORAGE_PATH, "certificates"), exist_ok=True)
    
    def upload_file(self, file_data, folder_name):
        """
        Dosya yükler
        
        Args:
            file_data: Yüklenecek dosya
            folder_name: Dosyanın yükleneceği klasör adı
            
        Returns:
            Yüklenen dosyanın yolu, başarısız durumda None
        """
        try:
            if config.STORAGE_TYPE == "local":
                return self._upload_file_local(file_data, folder_name)
            elif config.STORAGE_TYPE == "s3":
                return self._upload_file_s3(file_data, folder_name)
            else:
                raise ValueError(f"Geçersiz depolama türü: {config.STORAGE_TYPE}")
        except Exception as e:
            print(f"Dosya yükleme hatası: {str(e)}")
            return None
    
    def _upload_file_local(self, file_data, folder_name):
        """
        Dosyayı yerel depoya yükler
        
        Args:
            file_data: Yüklenecek dosya
            folder_name: Dosyanın yükleneceği klasör adı
            
        Returns:
            Yüklenen dosyanın yolu
        """
        # Klasör yolunu oluştur
        folder_path = os.path.join(config.STORAGE_PATH, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Dosya adını oluştur
        file_ext = os.path.splitext(file_data.name)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(folder_path, file_name)
        
        # Dosyayı kaydet
        with open(file_path, "wb") as f:
            f.write(file_data.read())
        
        # Göreceli yolu döndür
        return os.path.join(folder_name, file_name)
    
    def save_html_template(self, html_content, course_id):
        """
        HTML şablonunu dosya olarak kaydeder
        
        Args:
            html_content: HTML içeriği
            course_id: Eğitim ID'si
            
        Returns:
            Kaydedilen dosyanın yolu
        """
        try:
            # Klasör yolunu oluştur
            folder_path = os.path.join(config.STORAGE_PATH, "certificate-templates")
            os.makedirs(folder_path, exist_ok=True)
            
            # Dosya adını oluştur
            file_name = f"template_course_{course_id}.html"
            file_path = os.path.join(folder_path, file_name)
            
            # HTML içeriğini kaydet
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Göreceli yolu döndür
            return os.path.join("certificate-templates", file_name)
        except Exception as e:
            print(f"HTML şablon kaydetme hatası: {str(e)}")
            return None
    
    def _upload_file_s3(self, file_data, folder_name):
        """
        Dosyayı S3'e yükler
        
        Args:
            file_data: Yüklenecek dosya
            folder_name: Dosyanın yükleneceği klasör adı
            
        Returns:
            Yüklenen dosyanın yolu
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            # S3 istemcisi oluştur
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.S3_ACCESS_KEY,
                aws_secret_access_key=config.S3_SECRET_KEY,
                region_name=config.S3_REGION
            )
            
            # Dosya adını oluştur
            file_ext = os.path.splitext(file_data.name)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            s3_path = f"{folder_name}/{file_name}"
            
            # Dosyayı yükle
            s3_client.upload_fileobj(
                file_data,
                config.S3_BUCKET,
                s3_path
            )
            
            return s3_path
        except NoCredentialsError:
            print("S3 kimlik bilgileri bulunamadı")
            raise
        except Exception as e:
            print(f"S3 yükleme hatası: {str(e)}")
            raise
    
    def get_file(self, file_path):
        """
        Dosyayı getirir
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya içeriği
        """
        try:
            if config.STORAGE_TYPE == "local":
                return self._get_file_local(file_path)
            elif config.STORAGE_TYPE == "s3":
                return self._get_file_s3(file_path)
            else:
                raise ValueError(f"Geçersiz depolama türü: {config.STORAGE_TYPE}")
        except Exception as e:
            print(f"Dosya okuma hatası: {str(e)}")
            raise
    
    def _get_file_local(self, file_path):
        """
        Yerel depodan dosyayı getirir
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya içeriği
        """
        full_path = os.path.join(config.STORAGE_PATH, file_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {full_path}")
        
        with open(full_path, "rb") as f:
            return f.read()
    
    def _get_file_s3(self, file_path):
        """
        S3'ten dosyayı getirir
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya içeriği
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            # S3 istemcisi oluştur
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.S3_ACCESS_KEY,
                aws_secret_access_key=config.S3_SECRET_KEY,
                region_name=config.S3_REGION
            )
            
            # Dosyayı indir
            response = s3_client.get_object(
                Bucket=config.S3_BUCKET,
                Key=file_path
            )
            
            return response['Body'].read()
        except NoCredentialsError:
            print("S3 kimlik bilgileri bulunamadı")
            raise
        except Exception as e:
            print(f"S3 okuma hatası: {str(e)}")
            raise
    
    def delete_file(self, file_path):
        """
        Dosyayı siler
        
        Args:
            file_path: Silinecek dosya yolu
            
        Returns:
            Başarılı silme durumunda True, başarısız durumda False
        """
        try:
            if config.STORAGE_TYPE == "local":
                return self._delete_file_local(file_path)
            elif config.STORAGE_TYPE == "s3":
                return self._delete_file_s3(file_path)
            else:
                raise ValueError(f"Geçersiz depolama türü: {config.STORAGE_TYPE}")
        except Exception as e:
            print(f"Dosya silme hatası: {str(e)}")
            return False
    
    def _delete_file_local(self, file_path):
        """
        Yerel depodan dosyayı siler
        
        Args:
            file_path: Silinecek dosya yolu
            
        Returns:
            Başarılı silme durumunda True
        """
        full_path = os.path.join(config.STORAGE_PATH, file_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
        
        return True
    
    def _delete_file_s3(self, file_path):
        """
        S3'ten dosyayı siler
        
        Args:
            file_path: Silinecek dosya yolu
            
        Returns:
            Başarılı silme durumunda True
        """
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            # S3 istemcisi oluştur
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.S3_ACCESS_KEY,
                aws_secret_access_key=config.S3_SECRET_KEY,
                region_name=config.S3_REGION
            )
            
            # Dosyayı sil
            s3_client.delete_object(
                Bucket=config.S3_BUCKET,
                Key=file_path
            )
            
            return True
        except NoCredentialsError:
            print("S3 kimlik bilgileri bulunamadı")
            return False
        except Exception as e:
            print(f"S3 silme hatası: {str(e)}")
            return False
    
    def generate_certificate(self, template_path, replacements):
        """
        Sertifika oluşturur
        
        Args:
            template_path: Şablon dosyasının yolu
            replacements: Değiştirilecek alanlar
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        try:
            # Şablon dosyasını oku
            template_data = self.get_file(template_path)
            
            # Dosya uzantısını al
            ext = os.path.splitext(template_path)[1].lower()
            
            # HTML şablonu ise HTML olarak oluştur
            if ext == ".html":
                return self._generate_html_certificate(template_data, replacements)
            # PDF şablonu ise PDF olarak oluştur
            elif ext == ".pdf":
                return self._generate_pdf_certificate(template_data, replacements)
            # Resim şablonu ise görüntü olarak oluştur
            elif ext in [".jpg", ".jpeg", ".png"]:
                return self._generate_image_certificate(template_data, replacements, ext)
            else:
                # Desteklenmeyen format
                raise ValueError(f"Desteklenmeyen şablon formatı: {ext}")
        except Exception as e:
            print(f"Sertifika oluşturma hatası: {str(e)}")
            raise
    
    def _generate_html_certificate(self, template_data, replacements):
        """
        HTML sertifikası oluşturur
        
        Args:
            template_data: HTML şablon içeriği
            replacements: Değiştirilecek alanlar
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        try:
            # HTML içeriğini string'e çevir
            if isinstance(template_data, bytes):
                html_content = template_data.decode('utf-8')
            else:
                html_content = str(template_data)
            
            # Placeholder'ları değiştir
            for key, value in replacements.items():
                html_content = html_content.replace(key, str(value))
            
            # Çıktı dosyası için geçici dosya oluştur
            output_filename = f"certificate_{uuid.uuid4()}.html"
            output_path = os.path.join("certificates", output_filename)
            full_output_path = os.path.join(config.STORAGE_PATH, output_path)
            
            # Dizini oluştur
            os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
            
            # HTML dosyasını kaydet
            with open(full_output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            return output_path
        except Exception as e:
            print(f"HTML sertifika oluşturma hatası: {str(e)}")
            raise
    
    def _generate_pdf_certificate(self, template_data, replacements):
        """
        PDF sertifikası oluşturur
        
        Args:
            template_data: Şablon dosyası içeriği
            replacements: Değiştirilecek alanlar
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        # Bu örnekte basit bir PDF oluşturuyoruz
        # Gerçek uygulamada şablonu düzenlemek için PyPDF2 veya benzeri bir kütüphane kullanılabilir
        
        # Çıktı dosyası için geçici dosya oluştur
        output_filename = f"certificate_{uuid.uuid4()}.pdf"
        output_path = os.path.join("certificates", output_filename)
        full_output_path = os.path.join(config.STORAGE_PATH, output_path)
        
        # Dizini oluştur
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        # Yeni PDF oluştur
        c = canvas.Canvas(full_output_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Font kaydet
        try:
            # Varsayılan font
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        except:
            # Font bulunamazsa, yerleşik font kullan
            pass
        
        # Başlık
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-50, "SERTİFİKA")
        
        # Tarih
        c.setFont("Helvetica", 12)
        c.drawRightString(width-50, height-100, f"Tarih: {replacements.get('{{CompletionDate}}', datetime.now().strftime('%d.%m.%Y'))}")
        
        # İçerik
        c.setFont("Helvetica", 12)
        text = f"Bu sertifika, {replacements.get('{{StudentName}}', 'Öğrenci')} isimli katılımcının"
        c.drawCentredString(width/2, height/2 + 50, text)
        
        c.setFont("Helvetica-Bold", 16)
        course_name = replacements.get('{{CourseName}}', 'Eğitim')
        c.drawCentredString(width/2, height/2, f'"{course_name}"')
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height/2 - 50, "eğitimini başarıyla tamamladığını belgelemektedir.")
        
        # İmza
        c.drawString(width-150, height/4, "____________________")
        c.drawString(width-150, height/4 - 20, "Yetkili İmza")
        
        c.save()
        
        return output_path
    
    def _generate_image_certificate(self, template_data, replacements, ext):
        """
        Görüntü sertifikası oluşturur
        
        Args:
            template_data: Şablon dosyası içeriği
            replacements: Değiştirilecek alanlar
            ext: Dosya uzantısı
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        # Şablon görüntüsünü aç
        img = Image.open(io.BytesIO(template_data))
        draw = ImageDraw.Draw(img)
        
        # Font oluştur (varsayılan)
        try:
            font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
            font_medium = ImageFont.truetype("DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("DejaVuSans.ttf", 18)
        except:
            # Varsayılan font ile devam et
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Görüntü boyutları
        width, height = img.size
        
        # Başlık
        draw.text((width/2, 50), "SERTİFİKA", font=font_large, fill=(0, 0, 0), anchor="mt")
        
        # Tarih
        completion_date = replacements.get('{{CompletionDate}}', datetime.now().strftime('%d.%m.%Y'))
        draw.text((width-50, 100), f"Tarih: {completion_date}", font=font_small, fill=(0, 0, 0), anchor="rt")
        
        # İçerik
        student_name = replacements.get('{{StudentName}}', 'Öğrenci')
        text = f"Bu sertifika, {student_name} isimli katılımcının"
        draw.text((width/2, height/2 - 50), text, font=font_medium, fill=(0, 0, 0), anchor="mm")
        
        course_name = replacements.get('{{CourseName}}', 'Eğitim')
        draw.text((width/2, height/2), f'"{course_name}"', font=font_large, fill=(0, 0, 0), anchor="mm")
        
        draw.text((width/2, height/2 + 50), "eğitimini başarıyla tamamladığını belgelemektedir.", 
                 font=font_medium, fill=(0, 0, 0), anchor="mm")
        
        # İmza
        draw.text((width-150, height-100), "____________________", font=font_small, fill=(0, 0, 0))
        draw.text((width-150, height-70), "Yetkili İmza", font=font_small, fill=(0, 0, 0))
        
        # Çıktı dosyası için geçici dosya oluştur
        output_filename = f"certificate_{uuid.uuid4()}{ext}"
        output_path = os.path.join("certificates", output_filename)
        full_output_path = os.path.join(config.STORAGE_PATH, output_path)
        
        # Dizini oluştur
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        
        # Görüntüyü kaydet
        img.save(full_output_path)
        
        return output_path

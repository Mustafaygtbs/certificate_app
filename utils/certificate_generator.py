from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime
import uuid
import config
import base64

class CertificateGenerator:
    """Sertifika oluşturma yardımcı sınıfı"""
    
    @staticmethod
    def generate_pdf_certificate(student_name, course_name, completion_date, output_path=None):
        """
        PDF sertifikası oluşturur
        
        Args:
            student_name: Öğrenci adı
            course_name: Eğitim adı
            completion_date: Tamamlama tarihi
            output_path: Çıktı dosyası yolu (None ise geçici dosya oluşturur)
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        # Çıktı dosyası yolu
        if not output_path:
            output_filename = f"certificate_{uuid.uuid4()}.pdf"
            output_path = os.path.join(config.STORAGE_PATH, "certificates", output_filename)
            
            # Dizin oluştur
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Yeni PDF oluştur
        c = canvas.Canvas(output_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Arka plan rengi
        c.setFillColor(HexColor("#f9f9f9"))
        c.rect(0, 0, width, height, fill=True)
        
        # Kenar çizgisi
        c.setStrokeColor(HexColor("#3498db"))
        c.setLineWidth(10)
        c.rect(20, 20, width-40, height-40, stroke=True, fill=False)
        
        # İç kenar çizgisi
        c.setStrokeColor(HexColor("#2c3e50"))
        c.setLineWidth(2)
        c.rect(30, 30, width-60, height-60, stroke=True, fill=False)
        
        # Font kaydet
        try:
            # Varsayılan font - sistem fontlarını kullan
            title_font = "Helvetica-Bold"
            normal_font = "Helvetica"
        except:
            # Font bulunamazsa, yerleşik font kullan
            title_font = "Helvetica-Bold"
            normal_font = "Helvetica"
        
        # Başlık
        c.setFont(title_font, 36)
        c.setFillColor(HexColor("#2c3e50"))
        c.drawCentredString(width/2, height-100, "SERTİFİKA")
        
        # Tarih
        c.setFont(normal_font, 12)
        c.setFillColor(HexColor("#34495e"))
        c.drawRightString(width-50, height-150, f"Tarih: {completion_date}")
        
        # İçerik
        c.setFont(normal_font, 14)
        text = f"Bu sertifika, "
        c.drawCentredString(width/2, height/2 + 50, text)
        
        c.setFont(title_font, 20)
        c.setFillColor(HexColor("#e74c3c"))
        c.drawCentredString(width/2, height/2 + 20, student_name)
        
        c.setFont(normal_font, 14)
        c.setFillColor(HexColor("#34495e"))
        c.drawCentredString(width/2, height/2 - 10, "isimli katılımcının")
        
        c.setFont(title_font, 18)
        c.setFillColor(HexColor("#3498db"))
        c.drawCentredString(width/2, height/2 - 50, f'"{course_name}"')
        
        c.setFont(normal_font, 14)
        c.setFillColor(HexColor("#34495e"))
        c.drawCentredString(width/2, height/2 - 90, "eğitimini başarıyla tamamladığını belgelemektedir.")
        
        # İmza
        c.setFont(normal_font, 12)
        c.drawString(width-200, height/4 - 20, "____________________")
        c.drawString(width-200, height/4 - 40, "Yetkili İmza")
        
        # QR kod için bir kutu (gerçek uygulamada QR kod kütüphanesi ile oluşturulabilir)
        c.setStrokeColor(HexColor("#34495e"))
        c.setLineWidth(1)
        c.rect(50, 50, 100, 100, stroke=True, fill=False)
        c.setFont(normal_font, 8)
        c.drawCentredString(100, 40, "Doğrulama Kodu")
        c.drawCentredString(100, 30, str(uuid.uuid4())[:8])
        
        c.save()
        
        return output_path
    
    @staticmethod
    def convert_html_to_pdf(html_content, output_path=None):
        """
        HTML içeriğini PDF'e çevirir
        
        Args:
            html_content: HTML içeriği
            output_path: Çıktı dosyası yolu
            
        Returns:
            PDF dosyasının bytes'ı
        """
        try:
            # WeasyPrint veya pdfkit kullanılabilir
            # Şimdilik basit bir PDF oluşturalım
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape
            
            if not output_path:
                output_path = f"temp_certificate_{uuid.uuid4()}.pdf"
            
            # PDF oluştur
            c = canvas.Canvas(output_path, pagesize=landscape(A4))
            width, height = landscape(A4)
            
            # HTML içeriğini basit metin olarak ekle
            c.setFont("Helvetica", 12)
            c.drawString(50, height-50, "HTML Sertifikası")
            c.drawString(50, height-100, "Bu sertifika HTML formatından dönüştürülmüştür.")
            
            c.save()
            
            # PDF'i bytes olarak oku
            with open(output_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Geçici dosyayı sil
            if os.path.exists(output_path):
                os.remove(output_path)
            
            return pdf_bytes
            
        except Exception as e:
            print(f"HTML to PDF dönüştürme hatası: {str(e)}")
            return None
    
    @staticmethod
    def convert_image_to_pdf(image_data, output_path=None):
        """
        Resim dosyasını PDF'e çevirir
        
        Args:
            image_data: Resim dosyasının bytes'ı
            output_path: Çıktı dosyası yolu
            
        Returns:
            PDF dosyasının bytes'ı
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.utils import ImageReader
            
            if not output_path:
                output_path = f"temp_certificate_{uuid.uuid4()}.pdf"
            
            # Resmi PIL ile aç
            img = Image.open(io.BytesIO(image_data))
            
            # PDF oluştur
            c = canvas.Canvas(output_path, pagesize=landscape(A4))
            width, height = landscape(A4)
            
            # Resmi PDF'e ekle
            img_reader = ImageReader(img)
            img_width, img_height = img_reader.getSize()
            
            # Resmi sayfaya sığdır
            scale = min(width/img_width, height/img_height) * 0.8
            new_width = img_width * scale
            new_height = img_height * scale
            
            x = (width - new_width) / 2
            y = (height - new_height) / 2
            
            c.drawImage(img_reader, x, y, width=new_width, height=new_height)
            
            c.save()
            
            # PDF'i bytes olarak oku
            with open(output_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Geçici dosyayı sil
            if os.path.exists(output_path):
                os.remove(output_path)
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Image to PDF dönüştürme hatası: {str(e)}")
            return None
    
    @staticmethod
    def generate_image_certificate(student_name, course_name, completion_date, output_path=None, format="png"):
        """
        Görüntü sertifikası oluşturur
        
        Args:
            student_name: Öğrenci adı
            course_name: Eğitim adı
            completion_date: Tamamlama tarihi
            output_path: Çıktı dosyası yolu (None ise geçici dosya oluşturur)
            format: Görüntü formatı (png, jpg, jpeg)
            
        Returns:
            Oluşturulan sertifika dosyasının yolu
        """
        # Görüntü boyutları (A4 landscape yaklaşık)
        width, height = 842, 595
        
        # Çıktı dosyası yolu
        if not output_path:
            output_filename = f"certificate_{uuid.uuid4()}.{format}"
            output_path = os.path.join(config.STORAGE_PATH, "certificates", output_filename)
            
            # Dizin oluştur
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Yeni görüntü oluştur
        img = Image.new('RGB', (width, height), color="#f9f9f9")
        draw = ImageDraw.Draw(img)
        
        # Font oluştur
        try:
            # Sistem fontlarını kullan
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            # Varsayılan font ile devam et
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Kenar çizgisi - dış
        draw.rectangle([(20, 20), (width-20, height-20)], outline="#3498db", width=10)
        
        # Kenar çizgisi - iç
        draw.rectangle([(30, 30), (width-30, height-30)], outline="#2c3e50", width=2)
        
        # Başlık
        draw.text((width/2, 100), "SERTİFİKA", font=font_title, fill="#2c3e50", anchor="mm")
        
        # Tarih
        draw.text((width-50, 150), f"Tarih: {completion_date}", font=font_normal, fill="#34495e", anchor="rm")
        
        # İçerik
        draw.text((width/2, height/2 - 50), f"Bu sertifika,", font=font_normal, fill="#34495e", anchor="mm")
        draw.text((width/2, height/2 - 20), student_name, font=font_subtitle, fill="#e74c3c", anchor="mm")
        draw.text((width/2, height/2 + 10), "isimli katılımcının", font=font_normal, fill="#34495e", anchor="mm")
        draw.text((width/2, height/2 + 50), f'"{course_name}"', font=font_subtitle, fill="#3498db", anchor="mm")
        draw.text((width/2, height/2 + 90), "eğitimini başarıyla tamamladığını belgelemektedir.", 
                 font=font_normal, fill="#34495e", anchor="mm")
        
        # İmza
        draw.text((width-150, height-120), "____________________", font=font_normal, fill="#34495e")
        draw.text((width-180, height-90), "Yetkili İmza", font=font_normal, fill="#34495e")
        
        # QR kod için bir kutu
        draw.rectangle([(50, height-150), (150, height-50)], outline="#34495e", width=1)
        draw.text((100, height-40), "Doğrulama Kodu", font=font_small, fill="#34495e", anchor="mm")
        draw.text((100, height-25), str(uuid.uuid4())[:8], font=font_small, fill="#34495e", anchor="mm")
        
        # Görüntüyü kaydet
        img.save(output_path)
        
        return output_path

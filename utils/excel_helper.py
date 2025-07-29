import pandas as pd
import io

class ExcelHelper:
    """Excel dosyaları için yardımcı fonksiyonlar"""
    
    @staticmethod
    def export_students_to_excel(students):
        """
        Öğrencileri Excel formatına dönüştürür
        
        Args:
            students: Öğrenci listesi
            
        Returns:
            Excel dosyası içeriği (bytes)
        """
        try:
            # DataFrame oluştur
            df = pd.DataFrame([
                {
                    "Ad": student["first_name"],
                    "Soyad": student["last_name"],
                    "E-posta": student["email"],
                    "Telefon": student["phone_number"],
                    "Eğitimi Tamamladı": student["has_completed_course"],
                    "Eğitim Adı": student["course_name"]
                }
                for student in students
            ])
            
            # Excel'e dönüştür
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Öğrenciler")
                
                # Sütun genişliklerini ayarla
                worksheet = writer.sheets["Öğrenciler"]
                for i, col in enumerate(df.columns):
                    # İçeriğe göre sütun genişliğini ayarla (min 10, max 30 karakter)
                    max_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                    max_len = min(max(max_len, 10), 30)
                    worksheet.column_dimensions[chr(65 + i)].width = max_len
            
            return output.getvalue()
        except Exception as e:
            print(f"Excel dışa aktarma hatası: {str(e)}")
            raise
    
    @staticmethod
    def get_excel_template():
        """
        Öğrenci ekleme için Excel şablonu oluşturur
        
        Returns:
            Excel şablonu içeriği (bytes)
        """
        try:
            # Boş DataFrame oluştur
            df = pd.DataFrame(columns=["Ad", "Soyad", "E-posta", "Telefon", "Eğitimi Tamamladı"])
            
            # Örnek satır ekle
            df.loc[0] = ["Ad", "Soyad", "email@example.com", "05321234567", False]
            
            # Excel'e dönüştür
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Öğrenciler")
                
                # Sütun genişliklerini ayarla
                worksheet = writer.sheets["Öğrenciler"]
                for i, col in enumerate(df.columns):
                    worksheet.column_dimensions[chr(65 + i)].width = max(len(col) + 2, 15)
            
            return output.getvalue()
        except Exception as e:
            print(f"Excel şablonu oluşturma hatası: {str(e)}")
            raise

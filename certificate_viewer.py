import streamlit as st
import base64
from services.student_service import StudentService
from services.file_service import FileService
from utils.certificate_generator import CertificateGenerator
import config

def show():
    """Sertifika görüntüleme sayfası"""
    
    # URL parametrelerini al (güncellenmiş API)
    try:
        params = st.query_params
        token = params.get("token", None)
    except:
        # Eski API için fallback
        try:
            params = st.experimental_get_query_params()
            token = params.get("token", [None])[0]
        except:
            token = None
    
    if not token:
        st.error("Geçersiz sertifika linki!")
        st.write("Sertifika linki eksik veya hatalı.")
        return
    
    # Öğrenciyi token ile bul
    student_service = StudentService()
    student = student_service.get_student_by_token(token)
    
    if not student:
        st.error("Sertifika bulunamadı!")
        st.write("Bu token ile eşleşen bir sertifika bulunamadı.")
        return
    
    if not student["has_completed_course"]:
        st.warning("Bu öğrenci eğitimi henüz tamamlamamış!")
        st.write("Sertifika sadece eğitimi tamamlayan öğrenciler için oluşturulur.")
        return
    
    if not student["certificate_url"]:
        st.warning("Bu öğrenci için henüz sertifika oluşturulmamış!")
        st.write("Sertifika henüz oluşturulmamış. Lütfen daha sonra tekrar deneyin.")
        return
    
    # Sertifika bilgilerini göster
    st.title("🎓 Eğitim Sertifikası")
    
    # Öğrenci bilgileri
    st.subheader("Öğrenci Bilgileri")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Ad Soyad:** {student['first_name']} {student['last_name']}")
        st.write(f"**E-posta:** {student['email']}")
    
    with col2:
        st.write(f"**Eğitim:** {student['course_name']}")
        st.write(f"**Sertifika No:** {student['certificate_access_token']}")
    
    st.divider()
    
    # Sertifika görüntüleme
    st.subheader("Sertifika")
    
    try:
        file_service = FileService()
        certificate_data = file_service.get_file(student['certificate_url'])
        
        if not certificate_data:
            st.error("Sertifika dosyası bulunamadı!")
            return
        
        # Dosya uzantısına göre görüntüleme
        file_ext = student['certificate_url'].split('.')[-1].lower()
        
        if file_ext == "html":
            # HTML sertifikasını gömülü olarak göster
            html_content = certificate_data.decode('utf-8') if isinstance(certificate_data, bytes) else str(certificate_data)
            
            # HTML'i tam ekran göster
            st.components.v1.html(html_content, height=800, scrolling=True)
            
            # İndirme butonları
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 HTML İndir",
                    data=certificate_data,
                    file_name=f"sertifika_{student['first_name']}_{student['last_name']}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                # HTML'i PDF'e çevirme butonu
                if st.button("🔄 PDF'e Çevir", help="HTML sertifikasını PDF formatına çevirir", use_container_width=True):
                    with st.spinner("PDF oluşturuluyor..."):
                        pdf_data = CertificateGenerator.convert_html_to_pdf(html_content)
                        if pdf_data:
                            st.download_button(
                                label="📥 PDF İndir",
                                data=pdf_data,
                                file_name=f"sertifika_{student['first_name']}_{student['last_name']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("PDF başarıyla oluşturuldu!")
                        else:
                            st.error("PDF oluşturulurken bir hata oluştu!")
            
        elif file_ext == "pdf":
            # PDF'i gömülü olarak göster
            base64_pdf = base64.b64encode(certificate_data).decode('utf-8')
            pdf_display = f'''
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" height="600" type="application/pdf"
                    style="border: 1px solid #ddd; border-radius: 5px;">
            </iframe>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # PDF indirme butonu
            st.download_button(
                label="📥 PDF Sertifikayı İndir",
                data=certificate_data,
                file_name=f"sertifika_{student['first_name']}_{student['last_name']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        elif file_ext in ["jpg", "jpeg", "png"]:
            # Resim sertifikasını göster
            st.image(certificate_data, caption=f"{student['first_name']} {student['last_name']} Sertifikası")
            
            # İndirme butonları
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Resim İndir",
                    data=certificate_data,
                    file_name=f"sertifika_{student['first_name']}_{student['last_name']}.{file_ext}",
                    mime=f"image/{file_ext}",
                    use_container_width=True
                )
            
            with col2:
                # Resmi PDF'e çevirme butonu
                if st.button("🔄 PDF'e Çevir", help="Resim sertifikasını PDF formatına çevirir", use_container_width=True):
                    with st.spinner("PDF oluşturuluyor..."):
                        pdf_data = CertificateGenerator.convert_image_to_pdf(certificate_data)
                        if pdf_data:
                            st.download_button(
                                label="📥 PDF İndir",
                                data=pdf_data,
                                file_name=f"sertifika_{student['first_name']}_{student['last_name']}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("PDF başarıyla oluşturuldu!")
                        else:
                            st.error("PDF oluşturulurken bir hata oluştu!")
            
        else:
            st.error(f"Desteklenmeyen dosya formatı: {file_ext}")
            return
            
    except Exception as e:
        st.error(f"Sertifika görüntülenirken bir hata oluştu: {str(e)}")
        return
    
    # Doğrulama bilgileri
    st.divider()
    st.subheader("🔍 Sertifika Doğrulama")
    
    st.info("""
    Bu sertifika aşağıdaki bilgilerle doğrulanabilir:
    - **Sertifika Numarası:** Yukarıda gösterilen numara
    - **Öğrenci Bilgileri:** Ad, soyad ve e-posta adresi
    - **Eğitim Bilgileri:** Tamamlanan eğitimin adı
    """)
    
    # Doğrulama linki (domain uyumlu)
    verification_url = f"{config.BASE_URL}/?token={token}"
    st.write(f"**Doğrulama Linki:** {verification_url}")
    
    # QR kod oluşturma (opsiyonel)
    try:
        import qrcode
        from io import BytesIO
        
        # QR kod oluştur
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # QR kod resmi oluştur
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resmi bytes'a çevir
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # QR kodu göster
        st.subheader("📱 QR Kod")
        st.image(img_buffer, caption="Sertifika doğrulama QR kodu", width=200)
        
        # QR kod indirme butonu
        st.download_button(
            label="📥 QR Kodu İndir",
            data=img_buffer.getvalue(),
            file_name=f"qr_kod_{student['first_name']}_{student['last_name']}.png",
            mime="image/png",
            use_container_width=True
        )
        
    except ImportError:
        st.info("QR kod özelliği için 'qrcode' paketi gerekli.")
    
    # Yazdırma ve paylaşım butonları
    st.divider()
    st.subheader("🖨️ Yazdırma ve Paylaşım")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Yazdırma butonu
        st.markdown("""
        <script>
        function printCertificate() {
            window.print();
        }
        </script>
        <button onclick="printCertificate()" style="
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        ">🖨️ Yazdır</button>
        """, unsafe_allow_html=True)
    
    with col2:
        # E-posta ile paylaşım
        share_email = st.button(
            "📧 E-posta ile Paylaş",
            help="Sertifikayı e-posta ile paylaş",
            use_container_width=True
        )
    
    with col3:
        # Sosyal medya paylaşım
        share_social = st.button(
            "📱 Sosyal Medya",
            help="Sosyal medyada paylaş",
            use_container_width=True
        )
    
    # Ek bilgiler
    st.divider()
    st.subheader("ℹ️ Ek Bilgiler")
    
    st.info(f"""
    **Sertifika Detayları:**
    - **Oluşturulma Tarihi:** {student.get('created_at', 'Bilinmiyor')}
    - **Eğitim Süresi:** {student.get('course_duration', 'Bilinmiyor')}
    - **Sertifika Türü:** {file_ext.upper()}
    - **Doğrulama Durumu:** ✅ Geçerli
    """)
    
    # Alt bilgi
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        Bu sertifika <strong>{config.APP_TITLE}</strong> tarafından oluşturulmuştur.<br>
        Sertifika doğrulama için yukarıdaki linki kullanabilirsiniz.
    </div>
    """, unsafe_allow_html=True)

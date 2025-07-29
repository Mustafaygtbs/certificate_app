import streamlit as st
import pandas as pd
from utils.auth_helpers import auth_required
from services.course_service import CourseService
from services.student_service import StudentService
from services.file_service import FileService
import base64
import io
import config

@auth_required
def show():
    """Sertifikalar sayfasını gösterir"""
    
    # Sol üst köşeye ana sayfa butonu
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    
    st.title("Sertifikalar")
    
    # Kullanıcı bilgileri
    st.sidebar.success(f"Hoş geldiniz, {st.session_state['username']}!")
    
    # Navigasyon
    with st.sidebar:
        st.title("Menü")
        if st.button("Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        
        if st.button("Eğitimler", use_container_width=True):
            st.session_state["current_page"] = "courses"
            st.rerun()
            
        if st.button("Öğrenciler", use_container_width=True):
            st.session_state["current_page"] = "students"
            st.rerun()
            
        if st.button("Sertifikalar", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "certificates"
            st.rerun()
            
        if st.button("Çıkış Yap", use_container_width=True):
            # Oturum bilgilerini temizle
            st.session_state.pop("token", None)
            st.session_state.pop("user_id", None)
            st.session_state.pop("username", None)
            st.session_state.pop("email", None)
            st.session_state.pop("role", None)
            
            st.session_state["current_page"] = "login"
            st.rerun()
    
    # Servis nesnelerini oluştur
    course_service = CourseService()
    student_service = StudentService()
    file_service = FileService()
    
    # Eğitim listesini al
    courses = course_service.get_all_courses()
    
    if not courses:
        st.warning("Sistemde kayıtlı eğitim bulunmamaktadır. Önce eğitim eklemelisiniz.")
        
        if st.button("Eğitim Ekle"):
            st.session_state["current_page"] = "courses"
            st.rerun()
            
        return
    
    # Eğitim seçimi
    course_options = {c["id"]: f"{c['name']} ({c['student_count']} öğrenci)" for c in courses}
    
    # Seçilen kurs varsa onu göster, yoksa ilk kursu seç
    selected_course_id = st.session_state.get("selected_course_id", list(course_options.keys())[0])
    
    selected_course_id = st.selectbox(
        "Eğitim Seçin",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x],
        index=list(course_options.keys()).index(selected_course_id) if selected_course_id in course_options else 0
    )
    
    # Seçilen eğitimi kaydet
    st.session_state["selected_course_id"] = selected_course_id
    
    # Seçilen eğitim için öğrenci listesini al
    students = student_service.get_students_by_course(selected_course_id)
    
    # Sadece eğitimi tamamlayanları filtrele
    completed_students = [s for s in students if s["has_completed_course"]]
    
    # Sertifika şablonu kontrol et
    selected_course = course_service.get_course_by_id(selected_course_id)
    
    if not selected_course:
        st.error("Seçilen eğitim bulunamadı!")
        return
    
    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["Sertifika Şablonu", "Sertifikalar", "Sertifika Doğrulama"])
    
    with tab1:
        st.header("Sertifika Şablonu")
        
        if not selected_course["certificate_template_url"]:
            st.warning("Bu eğitim için henüz sertifika şablonu yüklenmemiş!")
            
            # HTML şablonu girişi
            st.subheader("HTML Sertifika Şablonu")
            st.write("""
            Aşağıdaki alanları HTML şablonunuzda kullanabilirsiniz:
            - `{{ogrenci_adi}}` - Öğrenci adı
            - `{{kurs_adi}}` - Eğitim adı  
            - `{{egitmen_adi}}` - Eğitmen adı
            - `{{tarih}}` - Sertifika tarihi
            - `{{sertifika_no}}` - Sertifika numarası
            """)
            
            html_template = st.text_area(
                "HTML Şablonu",
                value="""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sertifika Şablonu</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Playfair+Display:wght@700&family=Sacramento&display=swap" rel="stylesheet">
    <style>
        /* Genel Sayfa Stili */
        body {
            font-family: 'Montserrat', sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            color: #333;
            min-height: 100vh;
            margin: 0;
            box-sizing: border-box;
        }

        /* Sertifika Konteyneri */
        .sertifika-konteyner {
            width: 100%;
            max-width: 800px;
            aspect-ratio: 1.414 / 1;
            box-sizing: border-box;
        }

        /* Sertifika Ana Yapısı */
        #sertifika {
            background: #ffffff;
            border: 10px solid #003366;
            padding: 2rem 3rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            position: relative;
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
        }

        /* Dekoratif İç Çerçeve */
        #sertifika::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 2px solid #cfa34d;
            z-index: 1;
        }

        .sertifika-icerik {
             position: relative;
             z-index: 2;
        }

        .sertifika-baslik {
            font-family: 'Playfair Display', serif;
            font-size: clamp(2rem, 5vw, 3.5rem);
            color: #003366;
            margin: 0;
        }

        .sertifika-sunum {
            font-size: clamp(0.9rem, 2vw, 1.2rem);
            margin: 1.5rem 0 0.5rem 0;
        }

        /* Doldurulacak Alan: Öğrenci Adı */
        #ogrenci-adi {
            font-family: 'Sacramento', cursive;
            font-size: clamp(2.5rem, 6vw, 4.5rem);
            color: #cfa34d;
            font-weight: normal;
            margin: 0;
            padding-bottom: 1rem;
            border-bottom: 2px solid #eee;
        }

        .sertifika-aciklama {
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            margin: 1.5rem 0;
        }

        /* Doldurulacak Alan: Kurs Adı */
        #kurs-adi {
            font-weight: bold;
            color: #003366;
        }

        .sertifika-alt-bilgi {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 3rem;
            padding: 0 2rem;
        }

        .imza-alani {
            border-top: 1px solid #555;
            padding-top: 0.5rem;
            width: 40%;
            font-size: clamp(0.8rem, 1.5vw, 1rem);
        }
        
        /* Doldurulacak Alan: Tarih */
        .imza-alani #tarih {
            font-weight: bold;
        }
        
        .imza-alani span {
            font-weight: bold;
        }

        /* Doldurulacak Alan: Sertifika Numarası */
        #sertifika-no {
            position: absolute;
            bottom: 1.5rem;
            left: 2rem;
            font-size: 0.75rem;
            color: #999;
            z-index: 2;
        }

        /* Yazdırma için Özel Stiller */
        @media print {
            body {
                padding: 0;
                margin: 0;
                background-color: #fff;
            }
            .sertifika-konteyner {
                margin: 0;
                padding: 0;
                width: 100vw;
                height: 100vh;
                max-width: none;
                box-shadow: none;
                border: none;
            }
            #sertifika {
                box-shadow: none;
                border: 10px solid #003366;
                width: 100%;
                height: 100%;
                box-sizing: border-box;
            }
        }
    </style>
</head>
<body>

    <div class="sertifika-konteyner">
        <div id="sertifika">
            <div class="sertifika-icerik">
                <h1 class="sertifika-baslik">BAŞARI SERTİFİKASI</h1>
                <p class="sertifika-sunum">Bu sertifika</p>
                <h2 id="ogrenci-adi">{{ogrenci_adi}}</h2>
                <p class="sertifika-aciklama">
                    <strong id="kurs-adi">{{kurs_adi}}</strong> eğitimini başarıyla tamamladığı için verilmiştir.
                </p>
                <div class="sertifika-alt-bilgi">
                    <div class="imza-alani">
                        <span id="tarih">{{tarih}}</span><br>
                        Tarih
                    </div>
                    <div class="imza-alani">
                        <span>{{egitmen_adi}}</span><br>
                        Eğitim Koordinatörü
                    </div>
                </div>
            </div>
            <span id="sertifika-no">Sertifika No: {{sertifika_no}}</span>
        </div>
    </div>

</body>
</html>""",
                height=400,
                key="html_template"
            )
            
            # Önizleme bölümü
            st.subheader("Önizleme")
            
            # Test verileri ile önizleme
            test_data = {
                "ogrenci_adi": "Test Öğrenci",
                "kurs_adi": selected_course["name"],
                "egitmen_adi": selected_course.get("instructor_name", "Test Eğitmen"),
                "tarih": "29.07.2025",
                "sertifika_no": "2025072901"
            }
            
            # HTML'de placeholder'ları değiştir
            preview_html = html_template
            for key, value in test_data.items():
                preview_html = preview_html.replace(f"{{{{{key}}}}}", value)
            
            # Önizleme göster
            st.components.v1.html(preview_html, height=600, scrolling=True)
            
            if st.button("Şablonu Yükle"):
                # HTML şablonunu kaydet
                template_url = course_service.upload_html_certificate_template(
                    selected_course_id, 
                    html_template
                )
                
                if template_url:
                    st.success(f"HTML şablonu başarıyla yüklendi!")
                    st.rerun()
                else:
                    st.error("Şablon yüklenirken bir hata oluştu!")
        else:
            st.success("✅ Sertifika şablonu yüklendi!")
            
            # Mevcut şablonu göster
            st.subheader("Mevcut Şablon")
            
            try:
                # Şablon dosyasını oku
                template_data = file_service.get_file(selected_course["certificate_template_url"])
                
                if template_data:
                    # HTML içeriğini göster
                    if isinstance(template_data, bytes):
                        html_content = template_data.decode('utf-8')
                    else:
                        html_content = str(template_data)
                    
                    # Test verileri ile önizleme
                    test_data = {
                        "ogrenci_adi": "Test Öğrenci",
                        "kurs_adi": selected_course["name"],
                        "egitmen_adi": selected_course.get("instructor_name", "Test Eğitmen"),
                        "tarih": "29.07.2025",
                        "sertifika_no": "2025072901"
                    }
                    
                    # HTML'de placeholder'ları değiştir
                    preview_html = html_content
                    for key, value in test_data.items():
                        preview_html = preview_html.replace(f"{{{{{key}}}}}", value)
                    
                    # Önizleme göster
                    st.components.v1.html(preview_html, height=600, scrolling=True)
                else:
                    st.error("Şablon dosyası okunamadı!")
            except Exception as e:
                st.error(f"Şablon yüklenirken bir hata oluştu: {str(e)}")
    
    with tab2:
        st.header("Eğitimi Tamamlayan Öğrenciler")
        
        if not completed_students:
            st.info("Bu eğitimi tamamlayan öğrenci bulunmamaktadır.")
        else:
            # Eğitimi tamamlayan öğrencileri listele
            for student in completed_students:
                with st.expander(f"{student['first_name']} {student['last_name']}"):
                    cols = st.columns([3, 1])
                    
                    with cols[0]:
                        st.write(f"**E-posta:** {student['email']}")
                        st.write(f"**Telefon:** {student['phone_number'] or 'Belirtilmemiş'}")
                        st.write(f"**Sertifika Durumu:** {'✅ Oluşturuldu' if student['certificate_url'] else '❌ Oluşturulmadı'}")
                        st.write(f"**Erişim Tokeni:** {student['certificate_access_token']}")
                        
                        if student['certificate_url']:
                            certificate_link = f"{config.BASE_URL}/?token={student['certificate_access_token']}"
                            st.write(f"**Sertifika Linki:** [Görüntüle]({certificate_link})")
                    
                    with cols[1]:
                        # Sertifika görüntüleme butonu
                        if student['certificate_url']:
                            if st.button("Sertifikayı Görüntüle", key=f"view_cert_{student['id']}"):
                                try:
                                    # Sertifika dosyasını al
                                    certificate_data = file_service.get_file(student['certificate_url'])
                                    
                                    # Dosya uzantısına göre MIME türünü belirle
                                    file_ext = student['certificate_url'].split('.')[-1].lower()
                                    
                                    if file_ext == "html":
                                        # HTML sertifikasını gömülü olarak göster
                                        html_content = certificate_data.decode('utf-8') if isinstance(certificate_data, bytes) else str(certificate_data)
                                        st.components.v1.html(html_content, height=600, scrolling=True)
                                        
                                        # İndirme butonu
                                        st.download_button(
                                            label="Sertifikayı İndir",
                                            data=certificate_data,
                                            file_name=f"sertifika_{student['first_name']}_{student['last_name']}.html",
                                            mime="text/html"
                                        )
                                    elif file_ext == "pdf":
                                        mime_type = "application/pdf"
                                        
                                        # PDF'i gömülü olarak göster
                                        base64_pdf = base64.b64encode(certificate_data).decode('utf-8')
                                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                        st.markdown(pdf_display, unsafe_allow_html=True)
                                        
                                        # İndirme butonu
                                        st.download_button(
                                            label="Sertifikayı İndir",
                                            data=certificate_data,
                                            file_name=f"sertifika_{student['first_name']}_{student['last_name']}.pdf",
                                            mime=mime_type
                                        )
                                    elif file_ext in ["jpg", "jpeg", "png"]:
                                        mime_type = f"image/{file_ext}"
                                        st.image(certificate_data, caption=f"{student['first_name']} {student['last_name']} Sertifikası")
                                        
                                        # İndirme butonu
                                        st.download_button(
                                            label="Sertifikayı İndir",
                                            data=certificate_data,
                                            file_name=f"sertifika_{student['first_name']}_{student['last_name']}.{file_ext}",
                                            mime=mime_type
                                        )
                                    else:
                                        st.error(f"Desteklenmeyen dosya formatı: {file_ext}")
                                except Exception as e:
                                    st.error(f"Sertifika görüntülenirken bir hata oluştu: {str(e)}")
                        
                        # Sertifika oluşturma/gönderme butonu
                        if not student['certificate_url']:
                            if st.button("Sertifika Oluştur", key=f"create_cert_{student['id']}"):
                                if student_service.send_certificate_email(student['id']):
                                    st.success("Sertifika oluşturuldu ve e-posta gönderildi!")
                                    st.rerun()
                                else:
                                    st.error("Sertifika oluşturulurken bir hata oluştu!")
                        else:
                            # Sertifika e-posta gönderme butonu
                            if st.button("E-posta Gönder", key=f"send_email_{student['id']}"):
                                if student_service.send_certificate_email(student['id']):
                                    st.success("Sertifika e-postası başarıyla gönderildi!")
                                else:
                                    st.error("E-posta gönderilirken bir hata oluştu!")
            
            # Toplu işlemler
            st.subheader("Toplu İşlemler")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Tüm Sertifikaları Oluştur", use_container_width=True):
                    success_count = 0
                    for student in completed_students:
                        if not student['certificate_url']:
                            if student_service.send_certificate_email(student['id']):
                                success_count += 1
                    
                    if success_count > 0:
                        st.success(f"{success_count} sertifika başarıyla oluşturuldu!")
                        st.rerun()
                    else:
                        st.info("Oluşturulacak sertifika bulunamadı.")
            
            with col2:
                if st.button("Tüm E-postaları Gönder", use_container_width=True):
                    success_count = 0
                    for student in completed_students:
                        if student['certificate_url']:
                            if student_service.send_certificate_email(student['id']):
                                success_count += 1
                    
                    if success_count > 0:
                        st.success(f"{success_count} e-posta başarıyla gönderildi!")
                    else:
                        st.info("Gönderilecek e-posta bulunamadı.")
    
    with tab3:
        st.header("Sertifika Doğrulama")
        
        st.write("""
        Sertifika erişim tokeni ile sertifika doğrulama yapabilirsiniz.
        Token, öğrenciye gönderilen sertifika linkinde yer alır.
        """)
        
        token = st.text_input("Sertifika Tokeni")
        
        if st.button("Doğrula"):
            if not token:
                st.error("Token girilmedi!")
            else:
                try:
                    # Token formatını kontrol et
                    import uuid
                    try:
                        uuid_obj = uuid.UUID(token)
                    except ValueError:
                        st.error("Geçersiz token formatı!")
                        return
                    
                    # Öğrenciyi bul
                    student = student_service.get_student_by_token(token)
                    
                    if not student:
                        st.error("Bu token ile eşleşen bir sertifika bulunamadı!")
                    elif not student["has_completed_course"]:
                        st.warning("Bu öğrenci eğitimi henüz tamamlamamış!")
                    elif not student["certificate_url"]:
                        st.warning("Bu öğrenci için henüz sertifika oluşturulmamış!")
                    else:
                        st.success("✅ Sertifika doğrulandı!")
                        
                        st.write(f"**Öğrenci:** {student['first_name']} {student['last_name']}")
                        st.write(f"**E-posta:** {student['email']}")
                        st.write(f"**Eğitim:** {student['course_name']}")
                        
                        # Sertifikayı görüntüle
                        try:
                            # Sertifika dosyasını al
                            certificate_data = file_service.get_file(student['certificate_url'])
                            
                            # Dosya uzantısına göre MIME türünü belirle
                            file_ext = student['certificate_url'].split('.')[-1].lower()
                            
                            if file_ext == "html":
                                # HTML sertifikasını gömülü olarak göster
                                html_content = certificate_data.decode('utf-8') if isinstance(certificate_data, bytes) else str(certificate_data)
                                st.components.v1.html(html_content, height=600, scrolling=True)
                                
                                # İndirme butonu
                                st.download_button(
                                    label="Sertifikayı İndir",
                                    data=certificate_data,
                                    file_name=f"sertifika_{student['first_name']}_{student['last_name']}.html",
                                    mime="text/html"
                                )
                            elif file_ext == "pdf":
                                mime_type = "application/pdf"
                                
                                # PDF'i gömülü olarak göster
                                base64_pdf = base64.b64encode(certificate_data).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                                
                                # İndirme butonu
                                st.download_button(
                                    label="Sertifikayı İndir",
                                    data=certificate_data,
                                    file_name=f"sertifika_{student['first_name']}_{student['last_name']}.pdf",
                                    mime=mime_type
                                )
                            elif file_ext in ["jpg", "jpeg", "png"]:
                                mime_type = f"image/{file_ext}"
                                st.image(certificate_data, caption=f"{student['first_name']} {student['last_name']} Sertifikası")
                                
                                # İndirme butonu
                                st.download_button(
                                    label="Sertifikayı İndir",
                                    data=certificate_data,
                                    file_name=f"sertifika_{student['first_name']}_{student['last_name']}.{file_ext}",
                                    mime=mime_type
                                )
                            else:
                                st.error(f"Desteklenmeyen dosya formatı: {file_ext}")
                        except Exception as e:
                            st.error(f"Sertifika görüntülenirken bir hata oluştu: {str(e)}")
                except Exception as e:
                    st.error(f"Doğrulama sırasında bir hata oluştu: {str(e)}")

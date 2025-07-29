import streamlit as st
import pandas as pd
import io
from utils.auth_helpers import auth_required
from services.course_service import CourseService
from services.student_service import StudentService
from utils.excel_helper import ExcelHelper

@auth_required
def show():
    """Öğrenciler sayfasını gösterir"""
    
    # Sol üst köşeye ana sayfa butonu
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    
    st.title("Öğrenciler")
    
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
            
        if st.button("Sertifikalar", use_container_width=True):
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
    
    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["Öğrenci Listesi", "Yeni Öğrenci Ekle", "Excel ile Öğrenci Ekle"])
    
    with tab1:
        st.header("Öğrenci Listesi")
        
        # Filtre ve sıralama seçenekleri
        col1, col2 = st.columns(2)
        
        with col1:
            # Durum filtresi
            status_filter = st.radio(
                "Durum Filtresi",
                ["Tümü", "Tamamlayanlar", "Tamamlamayanlar"],
                horizontal=True,
                index=0
            )
        
        with col2:
            # Sıralama
            sort_option = st.selectbox(
                "Sıralama",
                ["Ad (A-Z)", "Ad (Z-A)", "Soyad (A-Z)", "Soyad (Z-A)"]
            )
        
        # Filtreleme ve sıralama
        if status_filter == "Tamamlayanlar":
            filtered_students = [s for s in students if s["has_completed_course"]]
        elif status_filter == "Tamamlamayanlar":
            filtered_students = [s for s in students if not s["has_completed_course"]]
        else:
            filtered_students = students
        
        # Sıralama
        if sort_option == "Ad (A-Z)":
            sorted_students = sorted(filtered_students, key=lambda x: x["first_name"])
        elif sort_option == "Ad (Z-A)":
            sorted_students = sorted(filtered_students, key=lambda x: x["first_name"], reverse=True)
        elif sort_option == "Soyad (A-Z)":
            sorted_students = sorted(filtered_students, key=lambda x: x["last_name"])
        elif sort_option == "Soyad (Z-A)":
            sorted_students = sorted(filtered_students, key=lambda x: x["last_name"], reverse=True)
        else:
            sorted_students = filtered_students
        
        # Excel'e aktar butonu
        if students:
            excel_data = ExcelHelper.export_students_to_excel(students)
            
            st.download_button(
                label="Excel'e Aktar",
                data=excel_data,
                file_name=f"ogrenciler_{selected_course_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Toplu işlemler
        st.subheader("Toplu İşlemler")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Tümünü Tamamladı İşaretle", use_container_width=True):
                success_count = 0
                for student in students:
                    if not student['has_completed_course']:
                        if student_service.mark_student_as_completed(student['id']):
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"{success_count} öğrenci başarıyla tamamladı olarak işaretlendi!")
                    st.rerun()
                else:
                    st.info("İşaretlenecek öğrenci bulunamadı.")
        
        with col2:
            if st.button("Tümünü Tamamlamadı İşaretle", use_container_width=True):
                success_count = 0
                for student in students:
                    if student['has_completed_course']:
                        if student_service.mark_student_as_not_completed(student['id']):
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"{success_count} öğrenci başarıyla tamamlamadı olarak işaretlendi!")
                    st.rerun()
                else:
                    st.info("İşaretlenecek öğrenci bulunamadı.")
        
        # col3 kaldırıldı - "Tamamlayanlara Mail Gönder" butonu kaldırıldı
        
        # Öğrenci listesi
        if not sorted_students:
            st.info(f"Bu filtreye uygun öğrenci bulunmamaktadır.")
        else:
            # Her öğrenci için kart oluştur
            for student in sorted_students:
                with st.expander(f"{student['first_name']} {student['last_name']}"):
                    cols = st.columns([3, 1])
                    
                    with cols[0]:
                        st.write(f"**E-posta:** {student['email']}")
                        st.write(f"**Telefon:** {student['phone_number'] or 'Belirtilmemiş'}")
                        st.write(f"**Eğitim:** {student['course_name']}")
                        st.write(f"**Durum:** {'✅ Tamamladı' if student['has_completed_course'] else '❌ Tamamlamadı'}")
                        
                        if student['certificate_url']:
                            st.write("✅ Sertifika oluşturuldu")
                        else:
                            st.write("❌ Sertifika oluşturulmadı")
                    
                    with cols[1]:
                        # Durum değiştirme butonu
                        if not student['has_completed_course']:
                            if st.button("Tamamladı İşaretle", key=f"mark_completed_{student['id']}"):
                                if student_service.mark_student_as_completed(student['id']):
                                    st.success("Öğrenci başarıyla tamamladı olarak işaretlendi!")
                                    st.rerun()
                                else:
                                    st.error("İşlem sırasında bir hata oluştu!")
                        
                        # Sertifika gönderme butonu
                        if student['has_completed_course']:
                            if st.button("Sertifika Gönder", key=f"send_cert_{student['id']}"):
                                if student_service.send_certificate_email(student['id']):
                                    st.success("Sertifika e-postası başarıyla gönderildi!")
                                else:
                                    st.error("Sertifika gönderilirken bir hata oluştu!")
                        
                        # Öğrenci düzenleme butonu
                        st.button("Düzenle", key=f"edit_student_{student['id']}", 
                                  on_click=lambda sid=student['id']: set_student_for_edit(sid))
                        
                        # Öğrenci silme butonu
                        if st.button("Sil", key=f"delete_student_{student['id']}"):
                            if student_service.delete_student(student['id']):
                                st.success("Öğrenci başarıyla silindi!")
                                st.rerun()
                            else:
                                st.error("Öğrenci silinirken bir hata oluştu!")
    
    with tab2:
        st.header("Yeni Öğrenci Ekle")
        
        # Öğrenci ekleme formu
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Ad", key="add_first_name")
            
            with col2:
                last_name = st.text_input("Soyad", key="add_last_name")
            
            email = st.text_input("E-posta", key="add_email")
            phone = st.text_input("Telefon", key="add_phone")
            
            completed = st.checkbox("Eğitimi tamamladı", key="add_completed")
            
            # Form gönderme
            submitted = st.form_submit_button("Öğrenciyi Ekle")
            
            if submitted:
                if not first_name or not last_name or not email:
                    st.error("Ad, Soyad ve E-posta alanları zorunludur!")
                else:
                    # Öğrenci ekle
                    student_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone_number": phone,
                        "has_completed_course": completed,
                        "course_id": selected_course_id
                    }
                    
                    if student_service.create_student(student_data):
                        st.success("Öğrenci başarıyla eklendi!")
                        
                        st.rerun()
                    else:
                        st.error("Öğrenci eklenirken bir hata oluştu! Aynı e-posta adresi ile bu eğitime kayıtlı başka bir öğrenci olabilir.")
    
    with tab3:
        st.header("Excel ile Öğrenci Ekle")
        
        st.write("""
        Excel dosyası ile toplu öğrenci ekleyebilirsiniz. 
        Dosyanızda şu sütunlar bulunmalıdır:
        - Ad (zorunlu)
        - Soyad (zorunlu)
        - E-posta (opsiyonel)
        - Telefon (opsiyonel)
        - Eğitimi Tamamladı (opsiyonel, True/False)
        """)
        
        # Örnek şablon indirme
        excel_template = ExcelHelper.get_excel_template()
        
        st.download_button(
            label="Excel Şablonu İndir",
            data=excel_template,
            file_name="ogrenci_sablonu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Excel dosyası yükleme
        uploaded_file = st.file_uploader("Excel Dosyasını Seçin", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            if st.button("Öğrencileri İçe Aktar"):
                try:
                    # Excel dosyasını işle
                    if student_service.import_students_from_excel(selected_course_id, uploaded_file):
                        st.success("Öğrenciler başarıyla içe aktarıldı!")
                        st.rerun()
                    else:
                        st.error("Öğrenciler içe aktarılırken bir hata oluştu!")
                except Exception as e:
                    st.error(f"Excel dosyası işlenirken bir hata oluştu: {str(e)}")
    
    # Öğrenci düzenleme
    if "edit_student" in st.session_state and st.session_state["edit_student"]:
        student_id = st.session_state["selected_student_id"]
        student = student_service.get_student_by_id(student_id)
        
        if student:
            with st.expander("Öğrenciyi Düzenle", expanded=True):
                with st.form("edit_student_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        first_name = st.text_input("Ad", value=student["first_name"], key="edit_first_name")
                    
                    with col2:
                        last_name = st.text_input("Soyad", value=student["last_name"], key="edit_last_name")
                    
                    email = st.text_input("E-posta", value=student["email"], key="edit_email")
                    phone = st.text_input("Telefon", value=student["phone_number"], key="edit_phone")
                    
                    completed = st.checkbox("Eğitimi tamamladı", value=student["has_completed_course"], key="edit_completed")
                    
                    # Form gönderme
                    submitted = st.form_submit_button("Güncelle")
                    
                    if submitted:
                        if not first_name or not last_name or not email:
                            st.error("Ad, Soyad ve E-posta alanları zorunludur!")
                        else:
                            # Öğrenci güncelle
                            student_data = {
                                "id": student_id,
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": email,
                                "phone_number": phone,
                                "has_completed_course": completed,
                                "course_id": student["course_id"]
                            }
                            
                            if student_service.update_student(student_id, student_data):
                                st.success("Öğrenci başarıyla güncellendi!")
                                st.session_state.pop("edit_student", None)
                                st.rerun()
                            else:
                                st.error("Öğrenci güncellenirken bir hata oluştu!")
                
                if st.button("İptal", key="cancel_edit_student"):
                    st.session_state.pop("edit_student", None)
                    st.rerun()

def set_student_for_edit(student_id):
    """Düzenleme için öğrenci seçer"""
    st.session_state["selected_student_id"] = student_id
    st.session_state["edit_student"] = True

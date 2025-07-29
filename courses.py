import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from utils.auth_helpers import auth_required, admin_required
from services.course_service import CourseService
from services.student_service import StudentService

@auth_required
def show():
    """Eğitimler sayfasını gösterir"""
    
    # Sol üst köşeye ana sayfa butonu
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    
    st.title("Eğitimler")
    
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
    
    # Sekmeler
    tab1, tab2 = st.tabs(["Eğitim Listesi", "Yeni Eğitim Ekle"])
    
    with tab1:
        st.header("Eğitim Listesi")
        
        # Eğitim listesini al
        courses = course_service.get_all_courses()
        
        if not courses:
            st.info("Henüz eğitim bulunmamaktadır.")
        else:
            # Durum filtresi
            status_filter = st.radio(
                "Durum Filtresi",
                ["Tümü", "Devam Eden", "Tamamlanan"],
                horizontal=True,
                index=0
            )
            
            # Filtreye göre eğitimleri filtrele
            if status_filter == "Devam Eden":
                filtered_courses = [c for c in courses if not c["is_completed"]]
            elif status_filter == "Tamamlanan":
                filtered_courses = [c for c in courses if c["is_completed"]]
            else:
                filtered_courses = courses
            
            if not filtered_courses:
                st.info(f"{status_filter} eğitim bulunmamaktadır.")
            else:
                # Her eğitim için kart oluştur
                for course in filtered_courses:
                    with st.expander(f"{course['name']} ({course['student_count']} Öğrenci)"):
                        cols = st.columns([3, 1])
                        
                        with cols[0]:
                            st.write(f"**Açıklama:** {course['description']}")
                            st.write(f"**Başlangıç Tarihi:** {course['start_date'].strftime('%d.%m.%Y')}")
                            st.write(f"**Bitiş Tarihi:** {course['end_date'].strftime('%d.%m.%Y')}")
                            st.write(f"**Durum:** {'✅ Tamamlandı' if course['is_completed'] else '🔄 Devam Ediyor'}")
                            
                            if course['certificate_template_url']:
                                st.write("✅ Sertifika şablonu yüklendi")
                            else:
                                st.write("❌ Sertifika şablonu yüklenmedi")
                        
                        with cols[1]:
                            # Eğitim detayları
                            if st.button("Öğrencileri Görüntüle", key=f"view_students_{course['id']}"):
                                st.session_state["selected_course_id"] = course["id"]
                                st.session_state["current_page"] = "students"
                                st.rerun()
                            
                            # Sertifika şablonu yükleme butonu
                            if not course['certificate_template_url']:
                                st.button("Sertifika Şablonu Yükle", key=f"upload_template_{course['id']}", 
                                          on_click=lambda cid=course['id']: set_course_for_template(cid))
                            
                            # Eğitim tamamlama butonu
                            if not course['is_completed'] and course['certificate_template_url']:
                                if st.button("Eğitimi Tamamla", key=f"complete_course_{course['id']}"):
                                    if course_service.complete_course(course['id']):
                                        st.success("Eğitim başarıyla tamamlandı ve sertifikalar gönderildi!")
                                        st.rerun()
                                    else:
                                        st.error("Eğitim tamamlanırken bir hata oluştu!")
                            
                            # Eğitim düzenleme butonu
                            st.button("Eğitimi Düzenle", key=f"edit_course_{course['id']}", 
                                      on_click=lambda cid=course['id']: set_course_for_edit(cid))
                                
                            # Eğitim silme butonu (admin kontrolü)
                            if st.session_state.get("role") == "admin":
                                if st.button("Eğitimi Sil", key=f"delete_course_{course['id']}"):
                                    if course_service.delete_course(course['id']):
                                        st.success("Eğitim başarıyla silindi!")
                                        st.rerun()
                                    else:
                                        st.error("Eğitim silinirken bir hata oluştu!")
    
    with tab2:
        st.header("Yeni Eğitim Ekle")
        
        # Eğitim ekleme formu
        with st.form("add_course_form"):
            course_name = st.text_input("Eğitim Adı", key="course_name")
            course_desc = st.text_area("Eğitim Açıklaması", key="course_desc")
            instructor_name = st.text_input("Eğitmen Adı", key="instructor_name")
            
            col1, col2 = st.columns(2)
            
            with col1:
                today = datetime.now().date()
                start_date = st.date_input("Başlangıç Tarihi", value=today, key="start_date")
            
            with col2:
                end_date = st.date_input("Bitiş Tarihi", value=today + timedelta(days=30), key="end_date")
            
            # Form gönderme
            submitted = st.form_submit_button("Eğitimi Ekle")
            
            if submitted:
                if not course_name:
                    st.error("Eğitim adı zorunludur!")
                elif start_date > end_date:
                    st.error("Başlangıç tarihi bitiş tarihinden sonra olamaz!")
                else:
                    # Eğitim ekle
                    course_data = {
                        "name": course_name,
                        "description": course_desc,
                        "instructor_name": instructor_name,
                        "start_date": datetime.combine(start_date, datetime.min.time()),
                        "end_date": datetime.combine(end_date, datetime.min.time()),
                        "is_completed": False
                    }
                    
                    course_id = course_service.create_course(course_data)
                    
                    if course_id:
                        st.success(f"Eğitim başarıyla eklendi! ID: {course_id}")
                        st.rerun()
                    else:
                        st.error("Eğitim eklenirken bir hata oluştu!")
    
    # Eğitim düzenleme
    if "edit_course" in st.session_state and st.session_state["edit_course"]:
        course_id = st.session_state["selected_course_id"]
        course = course_service.get_course_by_id(course_id)
        
        if course:
            with st.expander("Eğitimi Düzenle", expanded=True):
                with st.form("edit_course_form"):
                    course_name = st.text_input("Eğitim Adı", value=course["name"])
                    course_desc = st.text_area("Eğitim Açıklaması", value=course["description"])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        start_date = st.date_input("Başlangıç Tarihi", value=course["start_date"].date())
                    
                    with col2:
                        end_date = st.date_input("Bitiş Tarihi", value=course["end_date"].date())
                    
                    is_completed = st.checkbox("Tamamlandı", value=course["is_completed"])
                    
                    # Form gönderme
                    submitted = st.form_submit_button("Güncelle")
                    
                    if submitted:
                        if not course_name:
                            st.error("Eğitim adı zorunludur!")
                        elif start_date > end_date:
                            st.error("Başlangıç tarihi bitiş tarihinden sonra olamaz!")
                        else:
                            # Eğitim güncelle
                            course_data = {
                                "id": course_id,
                                "name": course_name,
                                "description": course_desc,
                                "start_date": datetime.combine(start_date, datetime.min.time()),
                                "end_date": datetime.combine(end_date, datetime.min.time()),
                                "is_completed": is_completed
                            }
                            
                            if course_service.update_course(course_id, course_data):
                                st.success("Eğitim başarıyla güncellendi!")
                                st.session_state.pop("edit_course", None)
                                st.rerun()
                            else:
                                st.error("Eğitim güncellenirken bir hata oluştu!")
                
                if st.button("İptal", key="cancel_edit_course"):
                    st.session_state.pop("edit_course", None)
                    st.rerun()

def set_course_for_template(course_id):
    """Şablon yükleme için eğitim seçer"""
    st.session_state["selected_course_id"] = course_id
    st.session_state["show_template_upload"] = True

def set_course_for_edit(course_id):
    """Düzenleme için eğitim seçer"""
    st.session_state["selected_course_id"] = course_id
    st.session_state["edit_course"] = True

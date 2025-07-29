import streamlit as st
import pandas as pd
import numpy as np
import datetime
from utils.auth_helpers import auth_required
from services.course_service import CourseService
from services.student_service import StudentService
import altair as alt

@auth_required
def show():
    """Gösterge paneli sayfasını gösterir"""
    
    st.title("Gösterge Paneli")
    
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
            
        # Admin menüleri
        if st.session_state.get("role") == "admin":
            st.divider()
            st.write("**👑 Admin Paneli**")
            if st.button("👥 Kullanıcı Yönetimi", use_container_width=True):
                st.session_state["current_page"] = "users"
                st.rerun()
        
        st.divider()
        if st.button("👤 Profil", use_container_width=True):
            st.session_state["current_page"] = "profile"
            st.rerun()
            
        if st.button("Çıkış Yap", use_container_width=True, type="primary"):
            # Oturum bilgilerini temizle
            st.session_state.pop("token", None)
            st.session_state.pop("user_id", None)
            st.session_state.pop("username", None)
            st.session_state.pop("email", None)
            st.session_state.pop("role", None)
            
            st.session_state["current_page"] = "login"
            st.rerun()
    
    # Verileri al
    course_service = CourseService()
    student_service = StudentService()
    
    courses = course_service.get_all_courses()
    
    # Temel istatistikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Toplam Eğitim", value=len(courses))
        
    with col2:
        active_courses = sum(1 for course in courses if not course["is_completed"])
        st.metric(label="Aktif Eğitim", value=active_courses)
        
    with col3:
        completed_courses = sum(1 for course in courses if course["is_completed"])
        st.metric(label="Tamamlanan Eğitim", value=completed_courses)
        
    with col4:
        total_students = sum(course["student_count"] for course in courses)
        st.metric(label="Toplam Öğrenci", value=total_students)
    
    # Son eklenen eğitimler
    st.subheader("Son Eklenen Eğitimler")
    
    if courses:
        # Tarihe göre sırala (en yeni başta)
        sorted_courses = sorted(courses, key=lambda x: x["created_at"], reverse=True)[:5]
        
        # Tablo verisi
        table_data = [
            {
                "Eğitim Adı": course["name"],
                "Başlangıç": course["start_date"].strftime("%d.%m.%Y"),
                "Bitiş": course["end_date"].strftime("%d.%m.%Y"),
                "Öğrenci Sayısı": course["student_count"],
                "Durum": "✅ Tamamlandı" if course["is_completed"] else "🔄 Devam Ediyor"
            }
            for course in sorted_courses
        ]
        
        st.table(pd.DataFrame(table_data))
    else:
        st.info("Henüz eğitim bulunmamaktadır.")
    
    # Eğitim durumu daire grafiği
    if courses:
        st.subheader("Eğitim Durumu Dağılımı")
        
        # Daire grafik için veri hazırla
        status_data = {
            "Devam Ediyor": sum(1 for course in courses if not course["is_completed"]),
            "Tamamlandı": sum(1 for course in courses if course["is_completed"])
        }
        
        # Altair daire grafik
        df_pie = pd.DataFrame([
            {"Durum": status, "Sayı": count}
            for status, count in status_data.items()
            if count > 0
        ])
        
        if not df_pie.empty:
            pie_chart = alt.Chart(df_pie).mark_arc().encode(
                theta="Sayı:Q",
                color=alt.Color("Durum:N", scale=alt.Scale(domain=['Devam Ediyor', 'Tamamlandı'], 
                                                         range=['#3498db', '#2ecc71'])),
                tooltip=["Durum", "Sayı"]
            ).properties(
                width=400,
                height=400
            )
            
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("Grafik için veri bulunmamaktadır.")
    else:
        st.info("Henüz eğitim bulunmamaktadır.")

# Sertifika Yönetim Sistemi

Python ve Streamlit ile geliştirilmiş, eğitim tamamlama sertifikalarını yönetmek için bir web uygulaması.

## 🚀 Canlı Demo

**Uygulama:** https://genczeka.streamlit.app

## ✨ Özellikler

- 📚 Eğitim kursları ekleme, düzenleme ve yönetme
- 👥 Öğrencileri manuel veya Excel ile toplu yükleme
- 📄 Sertifika şablonlarını yükleme ve özelleştirme
- 🎓 Eğitimi tamamlayan öğrencilere otomatik sertifika gönderme
- 📧 E-posta ile sertifika dağıtımı
- ✅ Sertifika doğrulama sistemi
- 📊 Dashboard ile istatistikler
- 🔐 JWT tabanlı güvenlik

## 🛠️ Teknolojiler

- **Backend:** Python 3.11+
- **Web Framework:** Streamlit
- **Veritabanı:** SQLite (geliştirme) / PostgreSQL (üretim)
- **ORM:** SQLAlchemy
- **Kimlik Doğrulama:** JWT + bcrypt
- **PDF Oluşturma:** ReportLab
- **E-posta:** SMTP (Gmail)

## 📦 Kurulum

### Yerel Geliştirme

1. **Python 3.11+ yüklü olmalıdır**
2. **Gereksinimleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Çevresel değişkenleri ayarlayın:**
   ```bash
   # .env dosyası örneği
   DATABASE_URL=sqlite:///certificate_app.db
   JWT_SECRET=your-secret-key-here
   JWT_ISSUER=https://genczeka.streamlit.app
   JWT_AUDIENCE=https://genczeka.streamlit.app
   JWT_EXPIRY_HOURS=60
   STORAGE_TYPE=local
   STORAGE_PATH=./storage
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_SENDER_EMAIL=your-email@gmail.com
   SMTP_SENDER_NAME=Certificate System
   BASE_URL=https://genczeka.streamlit.app
   ```

4. **Admin kullanıcısı oluşturun:**
   ```bash
   python scripts/create_admin.py
   ```

5. **Uygulamayı çalıştırın:**
   ```bash
   streamlit run app.py
   ```

### Streamlit.io Dağıtımı

1. **GitHub reposunu oluşturun**
2. **Streamlit hesabı açın:** https://share.streamlit.io
3. **GitHub reposunu Streamlit ile bağlayın**
4. **Streamlit Secrets ile çevresel değişkenleri ayarlayın**

## 🎯 İlk Kullanım

1. Uygulamayı başlattıktan sonra `http://localhost:8501` adresine gidin
2. **Admin kullanıcısı ile giriş yapın:**
   - E-posta: `admin@example.com`
   - Şifre: `admin123`
3. İlk eğitimi oluşturun
4. Öğrenci ekleyin
5. Sertifika şablonu yükleyin
6. Eğitimi tamamlayın

## 🔧 Konfigürasyon

### Streamlit.io Secrets

Streamlit.io'da aşağıdaki secrets'ları ayarlayın:

```toml
# .streamlit/secrets.toml
DATABASE_URL = "sqlite:///certificate_app.db"
JWT_SECRET = "your-secret-key-here"
JWT_ISSUER = "https://genczeka.streamlit.app"
JWT_AUDIENCE = "https://genczeka.streamlit.app"
JWT_EXPIRY_HOURS = "60"
STORAGE_TYPE = "local"
STORAGE_PATH = "./storage"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SENDER_EMAIL = "your-email@gmail.com"
SMTP_SENDER_NAME = "Certificate System"
BASE_URL = "https://genczeka.streamlit.app"
```

## 📁 Proje Yapısı

```
certificate_app/
├── app.py                 # Ana uygulama girişi
├── config.py             # Konfigürasyon ayarları
├── requirements.txt      # Python bağımlılıkları
├── runtime.txt          # Python runtime versiyonu
├── setup.py            # Paket kurulumu
├── .streamlit/         # Streamlit konfigürasyonu
├── db/                 # Veritabanı katmanı
├── services/           # İş mantığı servisleri
├── utils/              # Yardımcı araçlar
├── storage/            # Dosya depolama
└── scripts/            # Yardımcı scriptler
```

## 🔒 Güvenlik

- **JWT Token:** Güvenli oturum yönetimi
- **Şifre Hashleme:** bcrypt ile güvenli şifre saklama
- **Dosya Güvenliği:** Güvenli dosya yükleme ve depolama
- **E-posta Güvenliği:** TLS şifreleme ile güvenli e-posta

## 📊 Özellikler

### Dashboard
- Toplam eğitim sayısı
- Aktif/tamamlanan eğitimler
- Toplam öğrenci sayısı
- Eğitim durumu grafikleri

### Eğitim Yönetimi
- Eğitim ekleme/düzenleme/silme
- Sertifika şablonu yükleme
- Eğitim tamamlama işlemleri

### Öğrenci Yönetimi
- Manuel öğrenci ekleme
- Excel ile toplu öğrenci yükleme
- Öğrenci durumu takibi

### Sertifika Sistemi
- PDF ve HTML sertifika oluşturma
- Otomatik sertifika gönderimi
- Sertifika doğrulama linkleri

## 🚀 Dağıtım

### Yerel Geliştirme
```bash
streamlit run app.py
```

### Streamlit.io
- Otomatik GitHub entegrasyonu
- Otomatik dağıtım
- Secrets yönetimi

## 📝 Notlar

- **SQLite:** Geliştirme ortamında varsayılan veritabanı
- **PostgreSQL:** Üretim ortamında önerilen veritabanı
- **Gmail SMTP:** "Daha az güvenli uygulama erişimi" gerekli
- **Font Dosyaları:** Sistem varsayılan fontları kullanılır

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 📞 İletişim

- **Proje Linki:** https://github.com/yourusername/certificate_app
- **Canlı Demo:** https://genczeka.streamlit.app

# Streamlit.io Dağıtım Rehberi

Bu rehber, Sertifika Yönetim Sistemi'ni Streamlit.io'da canlıya almak için adım adım talimatları içerir.

## 🚀 Hızlı Başlangıç

### 1. GitHub Repository Hazırlığı

1. **Projeyi GitHub'a yükleyin:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/certificate_app.git
   git push -u origin main
   ```

2. **Repository ayarlarını kontrol edin:**
   - `app.py` dosyası ana dizinde olmalı
   - `requirements.txt` dosyası mevcut olmalı
   - `runtime.txt` dosyası Python 3.11 belirtmeli

### 2. Streamlit.io Hesabı

1. **Streamlit hesabı oluşturun:** https://share.streamlit.io
2. **GitHub hesabınızı bağlayın**
3. **"New app" butonuna tıklayın**

### 3. Uygulama Konfigürasyonu

1. **Repository seçin:** `yourusername/certificate_app`
2. **Branch seçin:** `main`
3. **Main file path:** `app.py`
4. **"Deploy!" butonuna tıklayın**

## ⚙️ Secrets Konfigürasyonu

### Streamlit.io Secrets Ayarları

1. **Uygulamanızın ana sayfasına gidin**
2. **"Settings" sekmesine tıklayın**
3. **"Secrets" bölümüne gidin**
4. **Aşağıdaki secrets'ları ekleyin:**

```toml
# Veritabanı ayarları
DATABASE_URL = "sqlite:///certificate_app.db"

# JWT ayarları
JWT_SECRET = "your-super-secret-key-here-make-it-long-and-random"
JWT_ISSUER = "https://genczeka.streamlit.app"
JWT_AUDIENCE = "https://genczeka.streamlit.app"
JWT_EXPIRY_HOURS = "60"

# Dosya depolama ayarları
STORAGE_TYPE = "local"
STORAGE_PATH = "./storage"

# E-posta ayarları (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
SMTP_SENDER_EMAIL = "your-email@gmail.com"
SMTP_SENDER_NAME = "Certificate System"

# Uygulama URL'i
BASE_URL = "https://genczeka.streamlit.app"
```

### Gmail App Password Oluşturma

1. **Google Hesabınıza gidin**
2. **"Güvenlik" sekmesine tıklayın**
3. **"2 Adımlı Doğrulama"yı etkinleştirin**
4. **"Uygulama Şifreleri"ne tıklayın**
5. **"Diğer" seçin ve bir isim verin**
6. **Oluşturulan 16 haneli şifreyi kopyalayın**

## 🔧 Sorun Giderme

### Yaygın Hatalar ve Çözümleri

#### 1. Bağımlılık Hataları
```
Error: pg_config executable not found
```
**Çözüm:** `requirements.txt` dosyasında `psycopg2-binary` satırını yorum satırı yapın.

#### 2. Python Versiyonu Hatası
```
Python 3.13 compatibility issues
```
**Çözüm:** `runtime.txt` dosyasında Python 3.11 kullanın.

#### 3. Import Hataları
```
ModuleNotFoundError: No module named 'streamlit'
```
**Çözüm:** `requirements.txt` dosyasını güncelleyin ve yeniden dağıtın.

#### 4. Veritabanı Hatası
```
Database connection failed
```
**Çözüm:** SQLite kullanın ve `DATABASE_URL` secret'ını kontrol edin.

### Log Kontrolü

1. **Streamlit.io dashboard'da uygulamanıza gidin**
2. **"Logs" sekmesine tıklayın**
3. **Hata mesajlarını kontrol edin**

## 📊 Performans Optimizasyonu

### 1. Dosya Boyutu Optimizasyonu
- Büyük dosyaları `.gitignore`'a ekleyin
- Sadece gerekli dosyaları commit edin

### 2. Bağımlılık Optimizasyonu
- Sadece gerekli paketleri `requirements.txt`'ye ekleyin
- Minimum versiyon numaralarını kullanın

### 3. Veritabanı Optimizasyonu
- SQLite kullanın (Streamlit.io için önerilen)
- Büyük veriler için PostgreSQL düşünün

## 🔒 Güvenlik Kontrol Listesi

### 1. Secrets Güvenliği
- [ ] JWT_SECRET güçlü ve benzersiz
- [ ] SMTP şifreleri güvenli
- [ ] Hassas bilgiler kodda değil secrets'ta

### 2. E-posta Güvenliği
- [ ] Gmail App Password kullanılıyor
- [ ] TLS şifreleme etkin
- [ ] E-posta doğrulama çalışıyor

### 3. Dosya Güvenliği
- [ ] Dosya yükleme güvenli
- [ ] Dosya türü kontrolü var
- [ ] Güvenli dosya depolama

## 📈 Monitoring ve Bakım

### 1. Log Monitoring
- Streamlit.io logs'ları düzenli kontrol edin
- Hata mesajlarını takip edin

### 2. Performans Monitoring
- Uygulama yükleme sürelerini kontrol edin
- Kullanıcı geri bildirimlerini toplayın

### 3. Güvenlik Güncellemeleri
- Bağımlılıkları düzenli güncelleyin
- Güvenlik açıklarını kontrol edin

## 🆘 Destek

### Sorun Yaşarsanız

1. **Streamlit.io Logs'ları kontrol edin**
2. **GitHub Issues'da sorun bildirin**
3. **Stack Overflow'da arama yapın**
4. **Streamlit Community'ye başvurun**

### Faydalı Linkler

- [Streamlit.io Documentation](https://docs.streamlit.io/)
- [Streamlit Community](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

## ✅ Başarı Kontrol Listesi

- [ ] Uygulama başarıyla dağıtıldı
- [ ] Secrets doğru ayarlandı
- [ ] Giriş sayfası çalışıyor
- [ ] Veritabanı bağlantısı çalışıyor
- [ ] E-posta gönderimi çalışıyor
- [ ] Sertifika oluşturma çalışıyor
- [ ] Dosya yükleme çalışıyor
- [ ] Mobil uyumluluk test edildi

## 🎉 Tebrikler!

Uygulamanız başarıyla canlıya alındı! 

**Canlı URL:** https://genczeka.streamlit.app

Artık kullanıcılarınız sertifika yönetim sistemini kullanabilir. 
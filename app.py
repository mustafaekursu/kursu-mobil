import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import re
from datetime import date, timedelta
import cv2
import numpy as np

# =============================================================================
# 🟢 AYARLAR & GÖRÜNÜM
# =============================================================================
st.set_page_config(page_title="KÜRSÜ PRO HİBRİT", page_icon="⚖️", layout="centered")

# CSS: RESMİ ADLİYE TEMASI
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li { color: #000000 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #f8f9fa !important; color: #000000 !important; border: 1px solid #7f8c8d !important;
    }
    div.stButton > button {
        background-color: #c0392b !important; color: white !important; font-weight: bold; border-radius: 6px;
    }
    .sonuc-panel {
        background-color: #2c3e50; color: white !important; padding: 20px; border-radius: 8px; margin-top: 15px; border-left: 6px solid #f1c40f;
    }
    .sonuc-panel * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 🔑 GÜVENLİ ANAHTAR YÖNETİMİ
# =============================================================================
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        AI_AKTIF = True
    else:
        AI_AKTIF = False
except:
    AI_AKTIF = False

st.title("⚖️ KÜRSÜ PRO: v6.0 (HİBRİT)")
st.caption("Hem Yapay Zeka (Online) Hem Dahili Motor (Offline) Bir Arada")

tabs = st.tabs(["📷 HİBRİT OKUYUCU", "⛓️ CEZA HESAPLA", "⏳ ZAMANAŞIMI", "📧 İLETİŞİM"])

# =============================================================================
# MODÜL 1: NİHAİ OFFLINE OCR (OTO-PİLOT MODU)
# =============================================================================
# Gerekli kütüphaneler: cv2, numpy, PIL, pytesseract
with tabs[0]:
    st.header("Dosya Okuma (Tamamen Offline)")
    st.info("Bu modül internete ihtiyaç duymaz. 'Oto-Pilot' algoritması belgeyi kendi düzeltir, temizler ve okur.")

    img_file = st.file_uploader("Belge Fotoğrafı Yükle", type=['png', 'jpg', 'jpeg'])
    
    # --- YARDIMCI FONKSİYON: YAMUKLUK DÜZELTME (DESKEW) ---
    def get_skew_angle(cv_image):
        # Arka planı siyah, yazıları beyaz yap
        new_image = cv_image.copy()
        gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Yazı bloklarını genişlet (Satırları birleştir)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=2)
        
        # Konturları bul ve en büyük dikdörtgenin açısını hesapla
        contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)
        
        if len(contours) > 0:
            rect = cv2.minAreaRect(contours[0])
            angle = rect[-1]
            if angle < -45: angle = -(90 + angle)
            else: angle = -angle
            return angle
        return 0.0

    # --- YARDIMCI FONKSİYON: RESMİ DÖNDÜR ---
    def rotate_image(cv_image, angle):
        (h, w) = cv_image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(cv_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if img_file:
        # Pillow ile açıp göster
        original_pil = Image.open(img_file)
        st.image(original_pil, caption="Yüklenen Ham Belge", use_column_width=True)
        
        # --- KULLANICI KONTROLLERİ (GEREKİRSE MÜDAHALE İÇİN) ---
        with st.expander("⚙️ Manuel Ayarlar (Otomatik Başarısız Olursa)"):
            c1, c2 = st.columns(2)
            with c1: oto_duzelt = st.checkbox("Otomatik Yamukluk Düzeltme (Deskew)", value=True)
            with c2: gultu_filtresi = st.checkbox("Gürültü Temizleme (Bilateral)", value=True)
            
            esik_degeri = st.slider("Mürekkep Hassasiyeti (Threshold)", 50, 200, 127, help="Yazı silikse sola çekin.")

        if st.button("BELGEYİ ANALİZ ET (OFFLINE) 🧠", use_container_width=True):
            try:
                with st.spinner("Algoritma çalışıyor: Geometri düzeltiliyor, doku temizleniyor..."):
                    # 1. OpenCV Formatına Çevir
                    img_cv = np.array(original_pil.convert('RGB')) 
                    img_cv = img_cv[:, :, ::-1].copy() # RGB to BGR
                    
                    # 2. OTOMATİK DÜZELTME (DESKEW)
                    if oto_duzelt:
                        angle = get_skew_angle(img_cv)
                        if abs(angle) > 0.5: # Sadece 0.5 dereceden fazla yamuksa işlem yap
                            img_cv = rotate_image(img_cv, angle)
                            st.caption(f"📐 Sistem belgeyi {angle:.2f} derece düzeltti.")
                    
                    # 3. GRİ TONLAMA
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

                    # 4. AKILLI BÜYÜTME (DPI ARTIRMA)
                    # Tesseract küçük yazıları okuyamaz, resmi 2 kat büyütüyoruz
                    height, width = gray.shape
                    if width < 2000:
                        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

                    # 5. GÜRÜLTÜ TEMİZLEME (BILATERAL FILTER)
                    # Bu filtre harf kenarlarını korur ama kağıt pürüzünü siler (Median'dan daha iyidir)
                    if gultu_filtresi:
                        gray = cv2.bilateralFilter(gray, 9, 75, 75)

                    # 6. EŞİKLEME (THRESHOLD)
                    # Manuel sürgü değeri ile kesin siyah-beyaz ayrımı
                    _, binary = cv2.threshold(gray, esik_degeri, 255, cv2.THRESH_BINARY)
                    
                    # 7. MORFOLOJİK İŞLEM (MÜREKKEP TAMİRİ)
                    # Kopuk harfleri (örn: silik 'ı' harfi) birleştirmek için hafif "Opening"
                    kernel = np.ones((1, 1), np.uint8)
                    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

                    # 8. KENAR BOŞLUĞU EKLE (SAFE AREA)
                    # Tesseract kenara yapışık yazıyı okumaz
                    binary = cv2.copyMakeBorder(binary, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255])

                    # --- SONUCU GÖSTER VE OKU ---
                    final_pil = Image.fromarray(binary)
                    st.image(final_pil, caption="Algoritmanın Gördüğü (İşlenmiş) Veri", use_column_width=True)

                    # Tesseract Konfigürasyonu
                    # --psm 3: Tam otomatik sayfa analizi (En güvenli mod)
                    # --psm 6: Tek blok (Eğer tablo yoksa bu da iyidir)
                    custom_config = r'--oem 3 --psm 3'
                    
                    text = pytesseract.image_to_string(final_pil, lang='tur', config=custom_config)
                    
                    # --- METİN TEMİZLİĞİ ---
                    # OCR hatalarını (gürültü karakterleri) temizle
                    text = text.replace("|", "").replace("~", "").replace("`", "")
                    # Regex ile sayı düzeltmeleri (O -> 0)
                    text = re.sub(r'(?<=\d)[oO](?=\d)', '0', text)
                    text = re.sub(r'(?<=\d)[lI](?=\d)', '1', text)
                    
                    # Paragraf düzeni
                    text = re.sub(r'\n+', '\n', text).strip()

                    st.success("Çeviri Tamamlandı!")
                    st.text_area("Hukuki Metin:", value=text, height=500)

            except Exception as e:
                st.error(f"Hata: {e}")
                st.warning("Lütfen GitHub'da packages.txt ve requirements.txt dosyalarının tam olduğunu kontrol edin.")
# =============================================================================
# MODÜL 2: CEZA İLAMI
# =============================================================================
with tabs[1]:
    st.header("Ceza Hesaplama")
    c1, c2, c3, c4 = st.columns(4)
    with c1: ty = st.number_input("Hapis (Yıl)", 0, 99, 2)
    with c2: ta = st.number_input("Hapis (Ay)", 0, 11, 0)
    with c3: tg = st.number_input("Hapis (Gün)", 0, 29, 0)
    with c4: base_para = st.number_input("Adli Para (Gün)", 0, 99999, 5)
    
    st.divider()
    # Artırım / İndirim
    col_a, col_i = st.columns(2)
    with col_a:
        amod = st.radio("Artırım", ["Liste", "Manuel"], horizontal=True)
        ap, apd = (0,1)
        if amod=="Liste":
            s = st.selectbox("Oran", ["Yok","1/6","1/4","1/3","1/2","1 Kat"])
            if s!="Yok": ap,apd = (int(s.split()[0]),1) if "Kat" in s else map(int, s.split('/'))
        else: ap=st.number_input("Pay",0,10,0,key="ap"); apd=st.number_input("Payda",1,20,1,key="apd")
        
    with col_i:
        imod = st.radio("İndirim", ["Liste", "Manuel"], horizontal=True)
        ip, ipd = (0,1)
        if imod=="Liste":
            si = st.selectbox("Oran ", ["Yok","1/6 (TCK 62)","1/3","1/2","2/3"])
            if si!="Yok": ip,ipd = map(int, si.split(' ')[0].split('/'))
        else: ip=st.number_input("Pay ",0,10,0,key="ip"); ipd=st.number_input("Payda ",1,20,1,key="ipd")

    # Hesap
    total = (ty*360 + ta*30 + tg)
    total_p = base_para
    if ap>0: total += (total*ap)/apd; total_p += (total_p*ap)/apd
    if ip>0: total -= (total*ip)/ipd; total_p -= (total_p*ip)/ipd
    
    y,r = divmod(total, 360); m,d = divmod(r, 30)
    st.markdown(f"<div class='sonuc-panel'><h3>{int(y)} Yıl, {int(m)} Ay, {int(d)} Gün</h3>Adli Para: {int(total_p)} Gün</div>", unsafe_allow_html=True)

# =============================================================================
# MODÜL 3: ZAMANAŞIMI (ÖZET)
# =============================================================================
with tabs[2]:
    st.header("Zamanaşımı")
    tur = st.selectbox("Hesap Türü", ["Ceza", "Hukuk"])
    if tur=="Ceza":
        suc = st.date_input("Suç Tarihi", date(2015,1,1))
        ust = st.selectbox("Üst Sınır", [">20 Yıl", "5-20 Yıl", "<5 Yıl"])
        asli = 20 if ">20" in ust else (15 if "5-20" in ust else 8)
        kes = st.checkbox("Kesilme Var mı?")
        son = asli * 1.5 if kes else asli
        bitis = suc.replace(year=suc.year + int(son))
        kalan = (bitis - date.today()).days
        st.write(f"Bitiş: {bitis.strftime('%d.%m.%Y')} ({'✅ SÜRE VAR' if kalan>0 else '❌ DOLDU'})")
    else:
        bas = st.date_input("Başlangıç", date.today())
        y = st.number_input("Yıl", 10)
        st.write(f"Bitiş: {bas.replace(year=bas.year+y).strftime('%d.%m.%Y')}")

# =============================================================================
# MODÜL 4: İLETİŞİM
# =============================================================================
with tabs[3]:
    st.success("Güvenlik: Secrets kasası korunmaktadır.")
    st.markdown("📧 Geliştirici: mustafa.emin.tr@hotmail.com")

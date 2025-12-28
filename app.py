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
# MODÜL 1: HİBRİT DOSYA OKUMA (AKILLI OFFLINE MOTOR)
# =============================================================================
with tabs[0]:
    st.header("Belge Okuma Merkezi")
    
    # KULLANICIYA MOTOR SEÇTİRİYORUZ
    motor_secimi = st.radio("Kullanılacak Motor:", 
                            ["🚀 Google Yapay Zeka (Online - %100)", 
                             "🧠 Akıllı Dahili Motor (Offline - %90)"])

    img_file = st.file_uploader("Belge Fotoğrafı Yükle", type=['png', 'jpg', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Yüklenen Belge", use_column_width=True)
        
        # --- SEÇENEK A: GOOGLE YAPAY ZEKA (ONLINE) ---
        if "Google" in motor_secimi:
            if st.button("YAPAY ZEKA İLE OKU (ONLINE) 🚀", use_container_width=True):
                if not AI_AKTIF:
                    st.error("⚠️ API Anahtarı (Secrets) tanımlı değil.")
                else:
                    try:
                        with st.spinner("Google Gemini belgeyi inceliyor..."):
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            prompt = "Sen uzman bir katipsin. Bu hukuki belgeyi harf hatası yapmadan, düzgün bir Türkçe ile metne dök. 'GANKARA' -> 'ANKARA', 'ESASNO' -> 'ESAS NO' düzeltmelerini yap."
                            response = model.generate_content([prompt, image])
                            st.success("Online Analiz Tamamlandı!")
                            st.text_area("Sonuç:", value=response.text, height=500)
                    except Exception as e:
                        st.error(f"İnternet Hatası: {e}. Lütfen 'Akıllı Dahili Motor'a geçin.")

        # --- SEÇENEK B: AKILLI DAHİLİ MOTOR (OFFLINE - OPENCV GÜÇLENDİRİLMİŞ) ---
        else:
            st.info("💡 Bu mod internet gerektirmez. 'Bilgisayarlı Görü (OpenCV)' teknolojisi ile belgeyi iyileştirip okur.")
            
            with st.expander("🛠️ Görüntü Laboratuvarı (Otomatik İyileştirme Aktif)"):
                c1, c2 = st.columns(2)
                with c1: golge_modu = st.checkbox("Gölge Temizleyici (Adaptive)", value=True, help="Kağıdın bazı yerleri karanlıksa bunu açın.")
                with c2: kalinlastir = st.checkbox("Mürekkep Artır (Dilation)", value=False, help="Yazılar silikse veya kesikse harfleri birleştirir.")
            
            if st.button("AKILLI MOTOR İLE OKU (OFFLINE) 🧠", use_container_width=True):
                try:
                    with st.spinner("Görüntü işleniyor ve okunuyor..."):
                        # 1. PIL Image -> OpenCV Formatına Çevir (Matematiksel İşlem İçin)
                        open_cv_image = np.array(image) 
                        # RGB'den BGR'ye (OpenCV standardı) ve Griye çevir
                        if len(open_cv_image.shape) == 3:
                            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = open_cv_image

                        # 2. GÖRSEL ZEKA ADIMLARI
                        processed_img = gray
                        
                        # A) Gürültü Temizleme (Noise Reduction)
                        # Kağıttaki kumlanmayı temizler
                        processed_img = cv2.medianBlur(processed_img, 3)

                        # B) Akıllı Eşikleme (Adaptive Threshold) - GÖLGE KATİLİ
                        if golge_modu:
                            # Bu algoritma, resmin her küçük karesi için ayrı ışık ayarı yapar.
                            # Gölgede kalan yazıyı da, ışıkta kalanı da aynı netlikte siyah yapar.
                            processed_img = cv2.adaptiveThreshold(
                                processed_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY, 31, 15 # 31 blok boyutu, 15 sabit (Hassas ayar)
                            )
                        else:
                            # Standart yöntem (Otsu)
                            _, processed_img = cv2.threshold(processed_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                        # C) Morfolojik İşlemler (Mürekkep Tamiri)
                        if kalinlastir:
                            # Harfleri biraz şişirerek kopuklukları birleştirir
                            kernel = np.ones((2,2), np.uint8)
                            processed_img = cv2.dilate(processed_img, kernel, iterations=1)

                        # 3. İşlenmiş Resmi Tekrar Pillow'a Çevir (Tesseract İçin)
                        final_pil_img = Image.fromarray(processed_img)

                        # Kullanıcıya neyi okuduğumuzu gösterelim (Güvenilirlik için)
                        st.image(final_pil_img, caption="Sistemin Gördüğü İyileştirilmiş Belge", use_column_width=True)

                        # 4. OKUMA (Tesseract)
                        custom_config = r'--oem 3 --psm 6'
                        text = pytesseract.image_to_string(final_pil_img, lang='tur', config=custom_config)
                        
                        # 5. TEMİZLİK (Regex)
                        text = text.replace("|", "").replace("~", "")
                        text = re.sub(r'(?<=\d)[oO](?=\d)', '0', text) # Rakam arasındaki o'ları 0 yap
                        
                        st.success("Offline Okuma Tamamlandı!")
                        st.text_area("Sonuç:", value=text, height=500)
                        
                except Exception as e:
                    st.error(f"Sistem Hatası: {e}")
                    st.warning("İPUCU: GitHub'da requirements.txt dosyasına 'opencv-python-headless' ve 'numpy' eklediniz mi?")
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

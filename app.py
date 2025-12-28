import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import re
from datetime import date, timedelta

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
# MODÜL 1: HİBRİT DOSYA OKUMA (SEÇMELİ)
# =============================================================================
with tabs[0]:
    st.header("Belge Okuma Merkezi")
    
    # KULLANICIYA MOTOR SEÇTİRİYORUZ
    motor_secimi = st.radio("Kullanılacak Motor:", 
                            ["🚀 Google Yapay Zeka (İnternet Gerekir - %99 Başarı)", 
                             "🛠️ Dahili Motor (Daha Az İnternet - %80 Başarı)"])

    img_file = st.file_uploader("Belge Fotoğrafı Yükle", type=['png', 'jpg', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Yüklenen Belge", use_column_width=True)
        
        # --- SEÇENEK A: GOOGLE YAPAY ZEKA ---
        if "Google" in motor_secimi:
            if st.button("YAPAY ZEKA İLE OKU 🚀", use_container_width=True):
                if not AI_AKTIF:
                    st.error("⚠️ API Anahtarı (Secrets) bulunamadı. Ayarlarınızı kontrol edin.")
                else:
                    try:
                        with st.spinner("Google Gemini belgeyi inceliyor..."):
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            prompt = "Sen uzman bir katipsin. Bu hukuki belgeyi harf hatası yapmadan, düzgün bir Türkçe ile metne dök. 'GANKARA' gibi hataları 'ANKARA' olarak düzelt."
                            response = model.generate_content([prompt, image])
                            st.success("Yapay Zeka Okuması Tamamlandı!")
                            st.text_area("Sonuç:", value=response.text, height=500)
                    except Exception as e:
                        st.error(f"İnternet Hatası: {e}. Lütfen 'Dahili Motor' seçeneğine geçin.")

        # --- SEÇENEK B: DAHİLİ MOTOR (TESSERACT - ESKİ USÜL) ---
        else:
            st.info("💡 Dahili motor (Tesseract) seçildi. İnternet zayıfsa bu mod idealdir.")
            
            # Eski Görüntü İşleme Ayarları
            with st.expander("Görüntü Ayarları (Okunmazsa Oynayın)"):
                esik = st.slider("Siyah/Beyaz Dengesi", 50, 230, 140)
                dondur = st.slider("Döndür", -5.0, 5.0, 0.0)
            
            if st.button("DAHİLİ MOTOR İLE OKU 🛠️", use_container_width=True):
                try:
                    with st.spinner("Dahili motor çalışıyor..."):
                        # 1. Döndür
                        img = image.rotate(-dondur, expand=True, fillcolor='white')
                        # 2. Griye Çevir & Eşikleme
                        img = img.convert('L').point(lambda x: 0 if x < esik else 255, '1')
                        # 3. Kenar Boşluğu
                        img = ImageOps.expand(img, border=50, fill='white')
                        
                        # Okuma
                        custom_config = r'--oem 3 --psm 6'
                        text = pytesseract.image_to_string(img, lang='tur', config=custom_config)
                        
                        # Temizlik
                        text = text.replace("|", "").replace("~", "")
                        text = text.replace("-\n", "").replace("\n", " ")
                        
                        st.success("Dahili Okuma Tamamlandı!")
                        st.text_area("Sonuç:", value=text, height=500)
                except Exception as e:
                    st.error(f"Motor Hatası: {e}. (GitHub'da packages.txt içinde tesseract-ocr var mı?)")

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

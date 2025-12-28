import streamlit as st
import re
from datetime import date, timedelta
from io import StringIO

# Harici kütüphane kontrolü
try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =============================================================================
# 🟢 AYARLAR
# =============================================================================
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com" 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="KÜRSÜ PRO", page_icon="⚖️", layout="centered")

# --- CSS: AYDINLIK (ADLİYE) TEMASI ---
st.markdown("""
    <style>
    /* 1. GENEL SAYFA (BEYAZ ZEMİN, SİYAH YAZI) */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* 2. TÜM YAZILAR, ETİKETLER, BAŞLIKLAR */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #000000 !important;
    }
    
    /* 3. GİRİŞ KUTULARI (NET ÇERÇEVELİ) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #ced4da !important;
    }
    
    /* 4. SEKMELER (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e9ecef;
        border-radius: 5px;
        padding: 10px 20px;
        color: #495057 !important;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #0d6efd; /* Adalet Mavisi */
        color: white !important;
    }

    /* 5. BUTONLAR */
    div.stButton > button {
        background-color: #d63031 !important; /* Canlı Kırmızı */
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    div.stButton > button:hover {
        background-color: #b71c1c !important;
    }

    /* 6. TUTANAK KAĞIDI GÖRÜNÜMÜ */
    .tutanak-kagidi {
        background-color: #ffffff; 
        color: #000000 !important;
        padding: 40px;
        font-family: 'Times New Roman', serif; 
        font-size: 16px; 
        line-height: 1.6;
        border: 2px solid #333; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        margin-top: 20px;
    }
    
    /* 7. SONUÇ KUTULARI */
    .sonuc-panel { 
        background-color: #2c3e50; 
        color: #ffffff !important; /* Kutu içi yazı beyaz kalsın */
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #f1c40f; 
        margin-top: 15px; 
    }
    /* Sonuç kutusu içindeki başlıkları beyaz yap */
    .sonuc-panel h3, .sonuc-panel span, .sonuc-panel div {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ KÜRSÜ PRO")
st.caption("Aydınlık Tema | Adli Asistan | Tam Kapsamlı")

tabs = st.tabs(["📁 DOSYA & KATİP", "⛓️ CEZA İLAMI", "⏳ ZAMANAŞIMI", "📧 İLETİŞİM"])

# =============================================================================
# FONKSİYON: REGEX (FORMATLAMA MOTORU)
# =============================================================================
def metni_hukuki_formatla(ham_metin):
    metin = ham_metin
    metin = metin.replace("İ", "i").upper() 
    anahtar_kelimeler = ["DAVACI", "DAVALI", "VEKİLİ", "MÜDAFİİ", "SANIK", "SUÇ", "SUÇ TARİHİ", "KONU", "İDDİA MAKAMI", "HÜKÜM", "KARAR", "GEREĞİ DÜŞÜNÜLDÜ"]
    for k in anahtar_kelimeler:
        metin = re.sub(f"(?i)({k}.*?:)", r"\n\n**\1**", metin)
    metin = re.sub(r"(\n\s*[-•1-9]+\.)", r"\n\1", metin)
    metin = re.sub(r"  +", " ", metin)
    metin = re.sub(r"\n\s*\n", "\n\n", metin)
    metin = metin.replace("BERAATİNE", "**BERAATİNE**")
    metin = metin.replace("CEZALANDIRILMASINA", "**CEZALANDIRILMASINA**")
    return metin.strip()

# =============================================================================
# MODÜL 1: DOSYA VE KATİP (Eksiksiz)
# =============================================================================
with tabs[0]:
    st.header("Dosya İşleme")
    
    # Seçenekler
    secim = st.radio("Yöntem Seçiniz:", ["📝 Metin Yapıştır (Önerilen)", "🎙️ Ses Dosyası Yükle", "🖼️ Fotoğraf Yükle"], horizontal=True)
    
    ham_girdi = ""
    
    # A) Metin
    if "Metin" in secim:
        st.info("Kopyaladığınız metni aşağıya yapıştırın.")
        ham_girdi = st.text_area("Metin Alanı:", height=200)

    # B) Ses
    elif "Ses" in secim:
        st.warning("İnternet bağlantısı gerektirir.")
        uploaded_audio = st.file_uploader("Ses Dosyası (.wav)", type=['wav', 'flac'])
        if uploaded_audio and sr:
            if st.button("Sesi Çöz"):
                try:
                    r = sr.Recognizer()
                    with sr.AudioFile(uploaded_audio) as source:
                        audio = r.record(source)
                        ham_girdi = r.recognize_google(audio, language="tr-TR")
                        st.success("Çözüldü!")
                        st.text_area("Sonuç:", value=ham_girdi)
                except Exception as e: st.error(f"Hata: {e}")

    # C) Fotoğraf
    elif "Fotoğraf" in secim:
        st.info("Fotoğrafı görüntüleyip metni telefonunuzla seçerek kopyalayın.")
        uploaded_img = st.file_uploader("Resim Seç", type=['png', 'jpg', 'jpeg'])
        if uploaded_img:
            st.image(uploaded_img, use_column_width=True)
            ham_girdi = st.text_area("Metni Buraya Yapıştırın:", height=150)

    st.markdown("---")
    c1, c2 = st.columns([1,2])
    with c1: belge = st.selectbox("Belge Başlığı", ["DURUŞMA TUTANAĞI", "GEREKÇELİ KARAR", "İFADE"])
    with c2: 
        st.write("")
        st.write("")
        if st.button("Sihirli Formatla ✨", use_container_width=True):
            if ham_girdi: st.session_state['f3'] = metni_hukuki_formatla(ham_girdi)

    if 'f3' in st.session_state:
        st.markdown(f"""<div class="tutanak-kagidi"><center><b>T.C.<br>ANKARA<br>MAHKEMESİ</b><br><u>{belge}</u></center><br>{st.session_state['f3']}</div>""", unsafe_allow_html=True)

# =============================================================================
# MODÜL 2: CEZA İLAMI (Eksiksiz)
# =============================================================================
with tabs[1]:
    st.header("Ceza Hesaplama")
    c1,c2,c3 = st.columns(3)
    with c1: ty=st.number_input("Yıl",0,99,2)
    with c2: ta=st.number_input("Ay",0,11,0)
    with c3: tg=st.number_input("Gün",0,29,0)
    st.divider()
    
    ca, ci = st.columns(2)
    with ca:
        st.subheader("⬆️ Artırım")
        am = st.radio("Tip", ["Liste", "Manuel"], key="ar1", horizontal=True)
        ap, apd = 0,1
        if am=="Liste":
            s=st.selectbox("Oran",["Yok","1/6","1/4","1/3","1/2","1 Kat"],key="as1")
            if s!="Yok": ap,apd=(1,1) if "Kat" in s else map(int,s.split('/'))
        else: ap=st.number_input("Pay",1,10,1,key="amp1"); apd=st.number_input("Payda",1,20,6,key="amd1")

    with ci:
        st.subheader("⬇️ İndirim")
        im = st.radio("Tip", ["Liste", "Manuel"], key="ir1", horizontal=True)
        ip, ipd = 0,1
        if im=="Liste":
            si=st.selectbox("Oran",["Yok","1/6 (TCK 62)","1/3","1/2","2/3"],key="is1")
            if si!="Yok": ip,ipd=map(int,si.split(' ')[0].split('/'))
        else: ip=st.number_input("Pay",1,10,1,key="imp1"); ipd=st.number_input("Payda",1,20,6,key="imd1")

    top = (ty*360)+(ta*30)+tg
    if ap>0: top+=(top*ap)/apd
    if ip>0: top-=(top*ip)/ipd
    sy,rg=divmod(top,360); sa,sg=divmod(rg,30)
    
    st.markdown(f"""
    <div class="sonuc-panel">
        <h3 style="color:white !important; margin:0;">SONUÇ: {int(sy)} Yıl, {int(sa)} Ay, {int(sg)} Gün</h3>
    </div>""", unsafe_allow_html=True)
    
    if st.checkbox("Adli Para Cezasına Çevir"):
        gb = st.number_input("Günlük (TL)", 20, 500, 100)
        st.info(f"💸 {int(top*gb):,} TL")

# =============================================================================
# MODÜL 3: ZAMANAŞIMI (Eksiksiz)
# =============================================================================
with tabs[2]:
    st.header("Süre Hesapları")
    tur = st.selectbox("Tür", ["Ceza (TCK 66/67)", "Hukuk (TBK/HMK)"])
    if "Ceza" in tur:
        st = st # Streamlit alias
        tar = st.date_input("Suç Tarihi", date(2015,1,1))
        sinir = st.selectbox("Üst Sınır", ["Ağırlaştırılmış", "Müebbet", ">20 Yıl", "5-20 Yıl", "<5 Yıl"])
        asli=8
        if "Ağır" in sinir: asli=30
        elif "Müebbet" in sinir: asli=25
        elif ">20" in sinir: asli=20
        elif "5-20" in sinir: asli=15
        
        c1,c2=st.columns(2)
        with c1: kes = st.radio("Zamanaşımı Kesen İşlem?", ["Hayır", "Evet"])
        with c2: dur = st.number_input("Durma (Gün)", 0)
        
        son = asli*1.5 if "Evet" in kes else asli
        bit = tar.replace(year=tar.year+int(son))
        if son%1!=0: bit+=timedelta(days=180)
        bit+=timedelta(days=dur)
        kal = (bit-date.today()).days
        renk, msj = ("green","DOLMADI") if kal>0 else ("red","DOLDU")
        
        st.markdown(f"""<div class="sonuc-panel"><b>HESAP:</b> {son} Yıl (+{dur} gün)<br>Bitiş: {bit.strftime('%d.%m.%Y')}<br><span style='color:{renk}; font-weight:bold; font-size:1.2em'>{msj}</span></div>""", unsafe_allow_html=True)
    else:
        bas = st.date_input("Başlangıç", date.today())
        konu = st.selectbox("Konu", ["Genel (10 Yıl)", "Kira (5 Yıl)", "Haksız Fiil (2 Yıl)", "Çek (10 Gün)"])
        y,g=0,0
        if "10 Yıl" in konu: y=10
        elif "5 Yıl" in konu: y=5
        elif "2 Yıl" in konu: y=2
        elif "10 Gün" in konu: g=10
        bit = bas.replace(year=bas.year+y)+timedelta(days=g)
        k = (bit-date.today()).days
        st.markdown(f"<div class='sonuc-panel'>Bitiş: {bit.strftime('%d.%m.%Y')}<br>{'✅ SÜRE VAR' if k>0 else '❌ DOLDU'}</div>", unsafe_allow_html=True)

# =============================================================================
# MODÜL 4: İLETİŞİM
# =============================================================================
with tabs[3]:
    st.header("İletişim")
    st.markdown(f"<div style='border:1px dashed #333; padding:15px; text-align:center;'><a href='mailto:{HAKIM_MAIL}' style='font-size:1.2em; color:#0d6efd;'>{HAKIM_MAIL}</a></div>", unsafe_allow_html=True)
    st.text_area("Kendinize Not:", placeholder="Notlarınız cihazda saklanır.")
    st.button("Notu Kaydet")

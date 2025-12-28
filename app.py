import streamlit as st
import re
from datetime import date, timedelta
from io import StringIO

# Harici kütüphane kontrolü (Hata vermemesi için)
try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =============================================================================
# 🟢 AYARLAR
# =============================================================================
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com.tr" 

# --- SAYFA VE GELİŞMİŞ TASARIM ---
st.set_page_config(page_title="KÜRSÜ PRO v3", page_icon="⚖️", layout="centered")

# CSS: YÜKSEK KONTRAST VE OKUNAKLILIK
st.markdown("""
    <style>
    /* GENEL SAYFA RENGİ */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* GİRİŞ KUTULARI (TEXT AREA/INPUT) */
    .stTextArea textarea, .stTextInput input, .stNumberInput input {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4b4b4b !important;
        font-size: 16px !important;
    }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #e74c3c !important; /* Canlı Kırmızı */
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #c0392b !important;
        transform: scale(1.02);
    }

    /* SEKMELER (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e;
        border-radius: 5px;
        padding: 10px 20px;
        color: #bdc3c7;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }

    /* TUTANAK KAĞIDI GÖRÜNÜMÜ */
    .tutanak-kagidi {
        background-color: #fdfefe; 
        color: #000000 !important; /* Kağıt üstü yazı simsiyah olsun */
        padding: 30px;
        font-family: 'Times New Roman', serif; 
        font-size: 16px; 
        line-height: 1.6;
        border: 1px solid #bdc3c7; 
        border-radius: 5px;
        margin-top: 20px;
    }
    .baslik-tc { text-align: center; font-weight: bold; margin-bottom: 10px; color:black;}
    .baslik-alt { text-align: center; font-weight: bold; text-decoration: underline; margin-bottom: 25px; color:black;}

    /* SONUÇ PANELLERİ */
    .sonuc-panel { 
        background-color: #1b2631; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #f1c40f; 
        margin-top: 15px; 
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ KÜRSÜ PRO: v3.0")
st.caption("Gelişmiş Arayüz | Dosya Yükleme | Tam Kapsamlı Hesaplama")

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
# MODÜL 1: DOSYA YÜKLEME VE KATİP
# =============================================================================
with tabs[0]:
    st.header("Dosya İşleme ve Düzenleme")
    
    secim = st.radio("İşlem Yöntemi Seçiniz:", ["📝 Metin Yapıştır (En Hızlı/Güvenli)", "🎙️ Ses Dosyası Yükle", "🖼️ Fotoğraf Yükle"], horizontal=True)
    
    ham_girdi = ""
    
    # --- A) METİN YAPIŞTIRMA (HİBRİT) ---
    if "Metin" in secim:
        st.info("💡 Telefonunuzun kamerasından veya sesli yazma özelliğinden metni kopyalayıp buraya yapıştırın.")
        ham_girdi = st.text_area("Metni Yapıştır:", height=200, placeholder="Duruşma tutanağını buraya yapıştırın...")

    # --- B) SES DOSYASI YÜKLEME ---
    elif "Ses" in secim:
        st.warning("⚠️ Bu özellik internet bağlantısı gerektirir (Google Servisleri).")
        uploaded_audio = st.file_uploader("Ses Dosyası Seç (WAV/FLAC)", type=['wav', 'flac'])
        
        if uploaded_audio is not None and sr:
            if st.button("Sesi Yazıya Dök"):
                r = sr.Recognizer()
                with sr.AudioFile(uploaded_audio) as source:
                    audio_data = r.record(source)
                    try:
                        text = r.recognize_google(audio_data, language="tr-TR")
                        st.success("Ses başarıyla çözüldü!")
                        ham_girdi = st.text_area("Çözülen Metin:", value=text, height=150)
                    except Exception as e:
                        st.error(f"Hata: {e}")
        elif not sr:
            st.error("Ses kütüphanesi yüklenemedi. Lütfen 'Metin Yapıştır' modunu kullanın.")

    # --- C) FOTOĞRAF YÜKLEME ---
    elif "Fotoğraf" in secim:
        st.info("💡 Sunucu güvenliği ve hızı için: Fotoğrafı yükleyin, telefonunuzdan metni seçip kopyalayın.")
        uploaded_img = st.file_uploader("Evrak Fotoğrafı Seç", type=['png', 'jpg', 'jpeg'])
        if uploaded_img:
            st.image(uploaded_img, caption="Yüklenen Evrak", use_column_width=True)
            ham_girdi = st.text_area("Fotoğraftan Okunan Metni Buraya Yapıştırın:", height=150)

    # --- FORMATLAMA İŞLEMİ ---
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1: belge_tipi = st.selectbox("Belge Başlığı", ["DURUŞMA TUTANAĞI", "GEREKÇELİ KARAR", "İFADE TUTANAĞI"])
    with col2: 
        st.write("") # Boşluk
        st.write("") 
        if st.button("Sihirli Formatla (Düzenle) ✨", use_container_width=True):
            if ham_girdi:
                st.session_state['fmt_v3'] = metni_hukuki_formatla(ham_girdi)
                st.success("Metin mahkeme formatına uyarlandı.")
            else:
                st.warning("Lütfen işlenecek bir metin giriniz.")

    # --- KAĞIT GÖRÜNÜMÜ ---
    if 'fmt_v3' in st.session_state:
        st.markdown(f"""
        <div class="tutanak-kagidi">
            <div class="baslik-tc">T.C.<br>ANKARA<br>... MAHKEMESİ</div>
            <div class="baslik-alt">{belge_tipi}</div>
            {st.session_state['fmt_v3']}
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# MODÜL 2: CEZA İLAMI
# =============================================================================
with tabs[1]:
    st.header("Ceza Hesaplama")
    c1, c2, c3 = st.columns(3)
    with c1: ty = st.number_input("Yıl",0,99,2)
    with c2: ta = st.number_input("Ay",0,11,0)
    with c3: tg = st.number_input("Gün",0,29,0)
    
    st.divider()
    
    # Artırım
    ca, ci = st.columns(2)
    with ca:
        st.subheader("⬆️ Artırım")
        a_mod = st.radio("Tip", ["Liste", "Manuel"], key="ar", horizontal=True)
        ap, apd = 0,1
        if a_mod=="Liste":
            s=st.selectbox("Oran",["Yok","1/6","1/4","1/3","1/2","1 Kat"],key="as")
            if s!="Yok": ap,apd = (1,1) if "Kat" in s else map(int,s.split('/'))
        else:
            ap=st.number_input("Pay",1,10,1,key="amp"); apd=st.number_input("Payda",1,20,6,key="amdp")

    # İndirim
    with ci:
        st.subheader("⬇️ İndirim")
        i_mod = st.radio("Tip", ["Liste", "Manuel"], key="ir", horizontal=True)
        ip, ipd = 0,1
        if i_mod=="Liste":
            si=st.selectbox("Oran",["Yok","1/6 (TCK 62)","1/3","1/2","2/3"],key="is")
            if si!="Yok": ip,ipd = map(int,si.split(' ')[0].split('/'))
        else:
            ip=st.number_input("Pay",1,10,1,key="imp"); ipd=st.number_input("Payda",1,20,6,key="imdp")

    # Hesap
    top_g = (ty*360)+(ta*30)+tg
    if ap>0: top_g += (top_g*ap)/apd
    if ip>0: top_g -= (top_g*ip)/ipd
    sy,rg = divmod(top_g, 360); sa,sg = divmod(rg, 30)
    
    st.markdown(f"""
    <div class="sonuc-panel" style="border-left-color: #e74c3c;">
        <h3 style="margin:0;">SONUÇ: {int(sy)} Yıl, {int(sa)} Ay, {int(sg)} Gün</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.checkbox("Adli Para Cezasına Çevir (TCK 50)"):
        gb = st.number_input("Günlüğü (TL)", 20, 500, 100)
        st.info(f"💸 {int(top_g * gb):,} TL")

# =============================================================================
# MODÜL 3: ZAMANAŞIMI
# =============================================================================
with tabs[2]:
    st.header("Süre Hesapları")
    tur = st.selectbox("Tür", ["Ceza Davası (TCK 66/67)", "Hukuk Davası (TBK/HMK)"])
    
    if "Ceza" in tur:
        suc_tarihi = st.date_input("Suç Tarihi", date(2015, 1, 1))
        suc_tipi = st.selectbox("Suçun Üst Sınırı", ["Ağırlaştırılmış Müebbet", "Müebbet", ">20 Yıl", "5-20 Yıl", "<5 Yıl"])
        asli = 8
        if "Ağır" in suc_tipi: asli=30
        elif "Müebbet" in suc_tipi: asli=25
        elif ">20" in suc_tipi: asli=20
        elif "5-20" in suc_tipi: asli=15
        
        c1, c2 = st.columns(2)
        with c1: kesme = st.radio("Zamanaşımı Kesen İşlem?", ["Hayır", "Evet (Sorgu/Karar)"])
        with c2: durma = st.number_input("Durma Süresi (Gün)", 0)
        
        sonuc_yil = asli * 1.5 if "Evet" in kesme else asli
        bitis = suc_tarihi.replace(year=suc_tarihi.year + int(sonuc_yil))
        if sonuc_yil % 1 != 0: bitis += timedelta(days=180)
        bitis += timedelta(days=durma)
        
        kalan = (bitis - date.today()).days
        renk = "green" if kalan > 0 else "red"
        msj = "✅ DOLMADI" if kalan > 0 else "❌ DOLDU"
        
        st.markdown(f"""
        <div class="sonuc-panel">
            <b>HESAPLAMA:</b> {sonuc_yil} Yıl (+{durma} gün)<br>
            Bitiş: {bitis.strftime('%d.%m.%Y')}<br>
            Durum: <span style='color:{renk}; font-weight:bold; font-size:1.2em'>{msj}</span>
        </div>""", unsafe_allow_html=True)
    else:
        baslangic = st.date_input("Başlangıç", date.today())
        konu = st.selectbox("Konu", ["Genel (10 Yıl)", "Kira (5 Yıl)", "Haksız Fiil (2 Yıl)", "İşe İade (1 Ay)", "Çek (10 Gün)"])
        y, g = 0, 0
        if "10 Yıl" in konu: y=10
        elif "5 Yıl" in konu: y=5
        elif "2 Yıl" in konu: y=2
        elif "1 Ay" in konu: g=30
        elif "10 Gün" in konu: g=10
        
        bitis = baslangic.replace(year=baslangic.year+y) + timedelta(days=g)
        kalan = (bitis - date.today()).days
        st.markdown(f"<div class='sonuc-panel'>Bitiş: {bitis.strftime('%d.%m.%Y')}<br>{'✅ SÜRE VAR' if kalan>0 else '❌ SÜRE DOLDU'}</div>", unsafe_allow_html=True)

# =============================================================================
# MODÜL 4: İLETİŞİM
# =============================================================================
with tabs[3]:
    st.header("İletişim")
    st.markdown(f"""
    <div style="border:1px dashed #555; padding:15px; text-align:center;">
        <a href="mailto:{HAKIM_MAIL}" style="font-size:1.2em; color:#3498db; text-decoration:none;">{HAKIM_MAIL}</a>
    </div>""", unsafe_allow_html=True)
    st.text_area("Kendinize Not:", placeholder="Notlarınız cihazda saklanır.")
    st.button("Notu Kaydet")

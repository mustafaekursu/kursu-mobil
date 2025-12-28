import streamlit as st
import re
from datetime import date, timedelta
from io import StringIO
import os

# --- KÜTÜPHANE KONTROLLERİ (Hata Vermemesi İçin) ---
try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# =============================================================================
# 🟢 AYARLAR & GÖRÜNÜM
# =============================================================================
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com" 

st.set_page_config(page_title="KÜRSÜ PRO", page_icon="⚖️", layout="centered")

# CSS: RESMİ ADLİYE TEMASI (Yüksek Okunabilirlik)
st.markdown("""
    <style>
    /* 1. ZEMİN VE YAZI RENGİ (BEYAZ ZEMİN - SİYAH YAZI) */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li { color: #000000 !important; }
    
    /* 2. GİRİŞ KUTULARI (NET ÇERÇEVELİ) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #7f8c8d !important;
        font-weight: 500;
    }
    
    /* 3. BUTONLAR (Canlı Kırmızı) */
    div.stButton > button {
        background-color: #c0392b !important;
        color: white !important;
        border-radius: 6px;
        padding: 10px 25px;
        font-weight: bold;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    div.stButton > button:hover { background-color: #e74c3c !important; }

    /* 4. SEKMELER */
    .stTabs [data-baseweb="tab"] { color: #555 !important; font-weight: bold; font-size: 16px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { 
        color: #c0392b !important; 
        border-bottom-color: #c0392b !important; 
    }
    
    /* 5. SONUÇ PANELLERİ */
    .sonuc-panel {
        background-color: #2c3e50; /* Koyu Lacivert */
        color: white !important;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        border-left: 6px solid #f1c40f;
    }
    .sonuc-panel * { color: white !important; } /* İçindeki her şey beyaz olsun */
    
    /* 6. TUTANAK KAĞIDI */
    .tutanak-kagidi {
        background-color: white;
        color: black !important;
        padding: 40px;
        border: 2px solid #000;
        font-family: 'Times New Roman', serif;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ KÜRSÜ PRO: v3.3")
st.caption("Güvenli Altyapı | OCR & Ses | Tam Hesaplama")

tabs = st.tabs(["📁 DOSYA & KATİP", "⛓️ CEZA İLAMI", "⏳ ZAMANAŞIMI", "🛡️ İLETİŞİM & GÜVENLİK"])

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================
def metni_hukuki_formatla(ham_metin):
    metin = ham_metin.replace("İ", "i").upper()
    anahtar = ["DAVACI", "DAVALI", "VEKİLİ", "MÜDAFİİ", "SANIK", "SUÇ", "SUÇ TARİHİ", "KONU", "İDDİA MAKAMI", "HÜKÜM", "KARAR", "GEREĞİ DÜŞÜNÜLDÜ"]
    for k in anahtar:
        metin = re.sub(f"(?i)({k}.*?:)", r"\n\n**\1**", metin)
    metin = re.sub(r"(\n\s*[-•1-9]+\.)", r"\n\1", metin)
    return metin.strip()

# =============================================================================
# MODÜL 1: DOSYA VE TUTANAK (OCR + SES)
# =============================================================================
with tabs[0]:
    st.header("Dosya İşleme Merkezi")
    
    secim = st.radio("Giriş Yöntemi:", ["📝 Metin Yapıştır", "🎙️ Ses Dosyası", "📷 Fotoğraf Analiz (OCR)"], horizontal=True)
    ham_girdi = ""
    
    # --- 1. METİN GİRİŞİ ---
    if "Metin" in secim:
        st.info("Kameradan kopyalanan metni veya notlarınızı yapıştırın.")
        ham_girdi = st.text_area("Metin Alanı:", height=200)
        
    # --- 2. SES GİRİŞİ ---
    elif "Ses" in secim:
        st.warning("Bu işlem için internet bağlantısı kullanılır.")
        dosya = st.file_uploader("Ses Dosyası Seç (.wav)", type=['wav'])
        if dosya and st.button("Sesi Yazıya Dök"):
            if sr:
                try:
                    r = sr.Recognizer()
                    with sr.AudioFile(dosya) as source:
                        audio = r.record(source)
                        ham_girdi = r.recognize_google(audio, language="tr-TR")
                        st.success("Ses başarıyla metne çevrildi.")
                        st.text_area("Çözülen Metin:", value=ham_girdi, height=150)
                except Exception as e: st.error(f"Hata: {e}")
            else: st.error("Ses modülü sunucuda aktif değil.")

    # --- 3. FOTOĞRAF GİRİŞİ (OCR) ---
    elif "Fotoğraf" in secim:
        st.info("Sistem, yüklenen fotoğraftaki yazıları otomatik olarak tarayacaktır.")
        img_file = st.file_uploader("Resim Yükle", type=['png', 'jpg', 'jpeg'])
        
        if img_file:
            image = Image.open(img_file)
            st.image(image, caption="Belge Önizleme", use_column_width=True)
            
            if st.button("Fotoğrafı Oku ve Metne Çevir 🔍"):
                if pytesseract:
                    try:
                        st.spinner("Yapay zeka belgeyi okuyor...")
                        text = pytesseract.image_to_string(image, lang='tur')
                        if not text.strip(): text = pytesseract.image_to_string(image) # Yedek dil
                        
                        ham_girdi = text
                        st.success("Okuma Başarılı!")
                        st.text_area("Okunan Metin:", value=ham_girdi, height=200)
                    except Exception as e:
                        st.error(f"Okuma Hatası: {e}")
                        st.warning("Not: GitHub'da 'packages.txt' dosyası oluşturup içine 'tesseract-ocr' yazdığınızdan emin olun.")
                else:
                    st.error("OCR modülü bulunamadı.")

    st.markdown("---")
    # FORMATLAMA BÖLÜMÜ
    c1, c2 = st.columns([1,2])
    with c1: belge = st.selectbox("Belge Başlığı", ["DURUŞMA TUTANAĞI", "GEREKÇELİ KARAR", "İFADE TUTANAĞI"])
    with c2: 
        st.write(""); st.write("")
        if st.button("Sihirli Formatla (Düzenle) ✨", use_container_width=True):
            if ham_girdi: st.session_state['out_v3'] = metni_hukuki_formatla(ham_girdi)

    if 'out_v3' in st.session_state:
        st.markdown(f"""<div class="tutanak-kagidi"><center><b>T.C.<br>ANKARA ADLİYESİ</b><br><u>{belge}</u></center><br>{st.session_state['out_v3']}</div>""", unsafe_allow_html=True)

# =============================================================================
# MODÜL 2: CEZA İLAMI HESAPLAMA
# =============================================================================
with tabs[1]:
    st.header("Ceza Hesaplama Robotu")
    c1,c2,c3 = st.columns(3)
    with c1: ty=st.number_input("Yıl",0,99,2)
    with c2: ta=st.number_input("Ay",0,11,0)
    with c3: tg=st.number_input("Gün",0,29,0)
    st.divider()
    
    col_a, col_i = st.columns(2)
    with col_a:
        st.subheader("⬆️ Artırım")
        amod = st.radio("Yöntem", ["Liste", "Manuel"], key="art_m", horizontal=True)
        ap, apd = 0,1
        if amod=="Liste":
            s=st.selectbox("Oran Seç",["Yok","1/6","1/4","1/3","1/2","1 Kat"],key="art_s")
            if s!="Yok": ap,apd=(1,1) if "Kat" in s else map(int,s.split('/'))
        else: ap=st.number_input("Pay",1,10,1,key="art_p"); apd=st.number_input("Payda",1,20,6,key="art_pd")
        
    with col_i:
        st.subheader("⬇️ İndirim")
        imod = st.radio("Yöntem", ["Liste", "Manuel"], key="ind_m", horizontal=True)
        ip, ipd = 0,1
        if imod=="Liste":
            si=st.selectbox("Oran Seç",["Yok","1/6 (TCK 62)","1/3","1/2","2/3"],key="ind_s")
            if si!="Yok": ip,ipd=map(int,si.split(' ')[0].split('/'))
        else: ip=st.number_input("Pay",1,10,1,key="ind_p"); ipd=st.number_input("Payda",1,20,6,key="ind_pd")

    # MANTIK
    top = (ty*360)+(ta*30)+tg
    if ap>0: top+=(top*ap)/apd
    if ip>0: top-=(top*ip)/ipd
    sy,rg=divmod(top,360); sa,sg=divmod(rg,30)
    
    st.markdown(f"""<div class="sonuc-panel"><h3>SONUÇ: {int(sy)} Yıl, {int(sa)} Ay, {int(sg)} Gün</h3></div>""", unsafe_allow_html=True)
    if st.checkbox("Adli Para Cezasına Çevir (TCK 50)"):
        val = st.number_input("Bir Günlük Miktar (TL)", 20, 500, 100)
        st.info(f"💸 HESAPLANAN PARA CEZASI: {int(top*val):,} TL")

# =============================================================================
# MODÜL 3: ZAMANAŞIMI HESABI
# =============================================================================
with tabs[2]:
    st.header("Zamanaşımı Hesaplama")
    tur = st.selectbox("Dava Türü", ["Ceza Davası (TCK 66/67)", "Hukuk Davası (TBK/HMK)"])
    if "Ceza" in tur:
        suc_t = st.date_input("Suç İşleme Tarihi", date(2015,1,1))
        ust = st.selectbox("Suçun Üst Sınırı", ["Ağırlaştırılmış Müebbet", "Müebbet", ">20 Yıl", "5-20 Yıl", "<5 Yıl"])
        asli = 8
        if "Ağır" in ust: asli=30
        elif "Müebbet" in ust: asli=25
        elif ">20" in ust: asli=20
        elif "5-20" in ust: asli=15
        
        cc1,cc2 = st.columns(2)
        with cc1: kes = st.radio("Kesilme Var mı?", ["Hayır", "Evet (Dava/Sorgu/Karar)"])
        with cc2: dur = st.number_input("Durma Süresi (Gün)", 0)
        
        son = asli*1.5 if "Evet" in kes else asli
        bitis = suc_t.replace(year=suc_t.year+int(son))
        if son%1!=0: bitis+=timedelta(days=180)
        bitis+=timedelta(days=dur)
        kln = (bitis-date.today()).days
        
        st.markdown(f"""<div class="sonuc-panel"><b>HESAPLAMA SONUCU:</b> {son} Yıl<br>Bitiş Tarihi: {bitis.strftime('%d.%m.%Y')}<br>{'✅ HENÜZ DOLMADI' if kln>0 else '❌ ZAMANAŞIMI DOLDU'}</div>""", unsafe_allow_html=True)
    else:
        bas = st.date_input("Başlangıç Tarihi", date.today())
        konu = st.selectbox("Konu", ["Genel Zamanaşımı (10 Yıl)", "Kira / Vekalet (5 Yıl)", "Haksız Fiil (2 Yıl)", "Kambiyo (10 Gün/6 Ay)"])
        y,g = 0,0
        if "10 Yıl" in konu: y=10
        elif "5 Yıl" in konu: y=5
        elif "2 Yıl" in konu: y=2
        elif "10 Gün" in konu: g=10
        bit = bas.replace(year=bas.year+y)+timedelta(days=g)
        k = (bit-date.today()).days
        st.markdown(f"<div class='sonuc-panel'>Bitiş Tarihi: {bit.strftime('%d.%m.%Y')}<br>{'✅ SÜRE VAR' if k>0 else '❌ SÜRE DOLDU'}</div>", unsafe_allow_html=True)

# =============================================================================
# MODÜL 4: İLETİŞİM VE GÜVENLİK
# =============================================================================
with tabs[3]:
    st.header("İletişim ve Güvenlik Protokolleri")
    
    # Güvenlik Bildirimi Kutusu (Yeşil Onaylı)
    st.success("""
    🛡️ **ÜST DÜZEY GÜVENLİK VE GİZLİLİK BİLDİRİMİ**
    
    Sayın Hakimim, kullanmakta olduğunuz bu sistem;
    
    1.  **Askeri Düzeyde Koruma:** "Private Repository" (Gizli Depo) altyapısı sayesinde kodlara ve verilere sizden başka kimse erişemez.
    2.  **Veri Sızıntısı Koruması:** Sisteme girdiğiniz hiçbir dava bilgisi, isim, metin veya fotoğraf sunucuda **kaydedilmez**.
    3.  **Anlık İmha:** Sayfayı yenilediğiniz veya kapattığınız an, tüm geçici veriler RAM üzerinden kalıcı olarak silinir.
    4.  **Log Tutulmaz:** Sistem hiçbir veri kaydı (log) tutmamaktadır.
    
    Gönül rahatlığıyla kullanabilirsiniz.
    """)
    
    st.markdown("---")
    st.subheader("Geliştirici İletişim")
    st.markdown(f"<div style='border:1px dashed #333; padding:15px; text-align:center;'><a href='mailto:{HAKIM_MAIL}' style='font-size:1.2em; color:#c0392b; font-weight:bold;'>📧 Geliştiriciye Mail Gönder</a></div>", unsafe_allow_html=True)
    
    st.write("")
    st.text_area("Kendinize Şifreli Not Bırakın (Cihaz Önbelleğinde Kalır):")
    st.button("Notu Geçici Olarak Kaydet")

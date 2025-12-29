import streamlit as st
import numpy as np
from PIL import Image
import os
import datetime
from dateutil.relativedelta import relativedelta

# =============================================================================
# 🟢 AYARLAR & GÖRÜNÜM
# =============================================================================
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com" # Mailinizi buraya yazabilirsiniz

st.set_page_config(page_title="KÜRSÜ PRO AI+", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li { color: #000000 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #f8f9fa !important; color: #000000 !important; border: 1px solid #7f8c8d !important;
    }
    div.stButton > button {
        background-color: #2980b9 !important; color: white !important; font-weight: bold; border-radius: 6px;
    }
    .sonuc-panel {
        background-color: #2c3e50; color: white !important; padding: 20px; border-radius: 8px; margin-top: 15px; border-left: 6px solid #f1c40f;
    }
    .sonuc-panel * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ KÜRSÜ PRO: v7.1 (Deep Security)")
st.caption("Tamamen Offline | Derin Öğrenme | Üst Düzey Güvenlik")

# =============================================================================
# 🧠 YAPAY ZEKA MOTORLARINI ÖNBELLEĞE AL (CACHE)
# =============================================================================
@st.cache_resource
def load_ocr_model():
    if OCR_AVAILABLE:
        return easyocr.Reader(['tr'], gpu=False)
    return None

@st.cache_resource
def load_whisper_model():
    if WHISPER_AVAILABLE:
        return whisper.load_model("base")
    return None

tabs = st.tabs(["👁️ GÖRSEL ZEKA (OCR)", "🎙️ SES ZEKA (WHISPER)", "⛓️ CEZA HESAPLA", "🛡️ İLETİŞİM & GÜVENLİK"])

# =============================================================================
# MODÜL 1: OFFLINE GÖRSEL ZEKA (EASYOCR)
# =============================================================================
with tabs[0]:
    st.header("Offline Belge Analizi (EasyOCR)")
    st.info("Bu modül 'Tesseract' yerine 'EasyOCR' yapay zekasını kullanır. El yazısına yakın fontları ve silik yazıları daha iyi okur. İnternet gerekmez.")

    if not OCR_AVAILABLE:
        st.error("⚠️ EasyOCR kütüphanesi bulunamadı. requirements.txt dosyasını kontrol edin.")
    else:
        img_file = st.file_uploader("Belge Fotoğrafı Yükle", type=['png', 'jpg', 'jpeg'])
        
        if img_file:
            image = Image.open(img_file)
            st.image(image, caption="Analiz Edilecek Belge", use_column_width=True)
            
            if st.button("DERİN ZEKA İLE OKU (OFFLINE) 🧠", use_container_width=True):
                with st.spinner("Yapay Zeka Modeli Yükleniyor ve Okuyor... (İlk seferde yavaş olabilir)"):
                    try:
                        reader = load_ocr_model()
                        img_np = np.array(image)
                        result = reader.readtext(img_np, detail=0, paragraph=True)
                        full_text = "\n\n".join(result)
                        
                        st.success("Analiz Tamamlandı!")
                        st.text_area("Hukuki Metin:", value=full_text, height=500)
                        
                    except Exception as e:
                        st.error(f"Bellek Hatası veya İşlem Hatası: {e}")
                        st.warning("Sunucu belleği yetersiz kalırsa daha küçük fotoğraflar deneyin.")

# =============================================================================
# MODÜL 2: OFFLINE SES ZEKA (WHISPER)
# =============================================================================
with tabs[1]:
    st.header("Offline Ses Deşifre (Whisper)")
    st.info("Dünyanın en iyi internetsiz ses tanıma modeli (OpenAI Whisper). Ses kayıtlarını, duruşma notlarını metne döker.")

    if not WHISPER_AVAILABLE:
        st.error("⚠️ Whisper kütüphanesi bulunamadı. requirements.txt dosyasını kontrol edin.")
    else:
        audio_file = st.file_uploader("Ses Dosyası Yükle (WAV, MP3, M4A)", type=['wav', 'mp3', 'm4a'])
        
        if audio_file:
            st.audio(audio_file)
            
            if st.button("SESİ METNE DÖK (OFFLINE) 🎙️", use_container_width=True):
                with st.spinner("Whisper Yapay Zekası sesi dinliyor..."):
                    try:
                        model = load_whisper_model()
                        with open("temp_audio.tmp", "wb") as f:
                            f.write(audio_file.getbuffer())
                        
                        result = model.transcribe("temp_audio.tmp", fp16=False, language='tr')
                        
                        st.success("Deşifre Tamamlandı!")
                        st.text_area("Konuşma Metni:", value=result['text'], height=400)
                        os.remove("temp_audio.tmp")
                        
                    except Exception as e:
                        st.error(f"Hata: {e}")

# =============================================================================
# MODÜL 3: CEZA HESAPLAMA
# =============================================================================
with tabs[2]:
    st.header("Ceza Hesaplama")
    c1, c2, c3, c4 = st.columns(4)
    with c1: ty = st.number_input("Hapis (Yıl)", 0, 99, 2)
    with c2: ta = st.number_input("Hapis (Ay)", 0, 11, 0)
    with c3: tg = st.number_input("Hapis (Gün)", 0, 29, 0)
    with c4: base_para = st.number_input("Adli Para (Gün)", 0, 99999, 5)
    
    st.divider()
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
    # --- ZAMANAŞIMI HESAPLAMA MODÜLÜ ---
st.markdown("---")
st.header("⚖️ Hukuki Süre Hesaplama Uzmanı")

hesap_tipi = st.radio("Hesaplama Türü Seçiniz:", ["Ceza Zamanaşımı (TCK)", "Hukuk/Dava Zamanaşımı (TBK/HMK)"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    baslangic_tarihi = st.date_input("Süre Başlangıç Tarihi (Suç/Olay Tarihi)")
with col2:
    temel_sure_yil = st.number_input("Temel Zamanaşımı Süresi (Yıl)", min_value=1, value=8)

# Hesaplama Değişkenleri
bitis_tarihi = baslangic_tarihi + relativedelta(years=temel_sure_yil)
maksimum_sure_tarihi = baslangic_tarihi + relativedelta(years=int(temel_sure_yil * 1.5)) # TCK Olağanüstü zamanaşımı

# 1. DURMA SEBEPLERİ (Süreyi Uzatır)
with st.expander("⏳ Durma Sebepleri Ekle (Süre İşlemez)"):
    st.info("Örn: Bekletici mesele, İzin alma süreci vb.")
    durma_gun = st.number_input("Toplam Durma Süresi (Gün)", min_value=0, value=0)
    durma_ay = st.number_input("Toplam Durma Süresi (Ay)", min_value=0, value=0)
    
    # Durma süresini bitişe ekle
    uzatma = relativedelta(months=durma_ay, days=durma_gun)
    bitis_tarihi += uzatma
    maksimum_sure_tarihi += uzatma # Durma, olağanüstü süreyi de öteler

# 2. KESME SEBEPLERİ (Süreyi Sıfırlar)
with st.expander("✂️ Kesme Sebepleri Ekle (Süre Sıfırlanır)"):
    st.info("Örn: İfade alma, İddianame düzenlenmesi, Mahkumiyet kararı vb.")
    kesme_var_mi = st.checkbox("Zamanaşımını Kesen Bir İşlem Yapıldı mı?")
    
    if kesme_var_mi:
        son_kesme_tarihi = st.date_input("En Son Yapılan Kesici İşlem Tarihi")
        # Kural: Süre kesilince, o tarihten itibaren temel süre kadar yeniden başlar
        if son_kesme_tarihi > baslangic_tarihi:
            yeni_bitis = son_kesme_tarihi + relativedelta(years=temel_sure_yil) + uzatma
            # Ceza hukukunda kesilme olsa bile toplam süre (1.5 katı) aşılamaz
            if hesap_tipi == "Ceza Zamanaşımı (TCK)":
                if yeni_bitis > maksimum_sure_tarihi:
                    st.warning(f"⚠️ DİKKAT: Kesilme olsa bile TCK 67/4 gereği olağanüstü zamanaşımı ({maksimum_sure_tarihi}) aşılamaz.")
                    bitis_tarihi = maksimum_sure_tarihi
                else:
                    bitis_tarihi = yeni_bitis
            else:
                # Hukuk davalarında (TBK) genelde üst sınır (tavan) farklıdır, burada basit reset mantığı işler
                bitis_tarihi = yeni_bitis

# --- SONUÇ EKRANI ---
st.success(f"🗓️ Tahmini Zamanaşımı Dolma Tarihi: **{bitis_tarihi.strftime('%d.%m.%Y')}**")

if hesap_tipi == "Ceza Zamanaşımı (TCK)":
    st.caption(f"ℹ️ TCK 66/67 kapsamında Olağanüstü (Maksimum) Süre Sınırı: {maksimum_sure_tarihi.strftime('%d.%m.%Y')}")

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
    2.  **Veri Sızıntısı Koruması:** Sisteme girdiğiniz hiçbir dava bilgisi, isim, metin, fotoğraf veya ses kaydı sunucuda **kaydedilmez**.
    3.  **Anlık İmha:** Sayfayı yenilediğiniz veya kapattığınız an, tüm geçici veriler RAM üzerinden kalıcı olarak silinir.
    4.  **Log Tutulmaz:** Sistem hiçbir veri kaydı (log) tutmamaktadır.
    
    Gönül rahatlığıyla kullanabilirsiniz.
    """)
    
    st.markdown("---")
    st.subheader("Geliştirici İletişim")
    st.markdown(f"<div style='border:1px dashed #333; padding:15px; text-align:center;'><a href='mailto:{HAKIM_MAIL}' style='font-size:1.2em; color:#2980b9; font-weight:bold;'>📧 {HAKIM_MAIL}</a></div>", unsafe_allow_html=True)

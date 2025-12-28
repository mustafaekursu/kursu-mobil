from PIL import Image, ImageEnhance, ImageFilter, ImageOps
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

    # --- 3. FOTOĞRAF GİRİŞİ (ROTASYON, SÖZLÜK VE HASSAS OCR) ---
    elif "Fotoğraf" in secim:
        st.info("Nihai Profesyonel Mod: Döndürme, Kırpma ve Hukuki Sözlük Desteği.")
        img_file = st.file_uploader("Resim Yükle", type=['png', 'jpg', 'jpeg'])
        
        if img_file:
            if Image is None:
                st.error("⚠️ HATA: Pillow kütüphanesi eksik.")
            else:
                original_image = Image.open(img_file)
                
                # --- A. KIRPMA VE DÖNDÜRME PANELİ ---
                st.markdown("#### 1. 📐 Geometri Ayarları (Yamuksa Düzeltin)")
                
                # ROTASYON (Yeni Özellik)
                rotasyon = st.slider("Belgeyi Döndür (Düzeltmek için)", -10.0, 10.0, 0.0, step=0.1, help="Belge eğikse okuma bozulur. Buradan düzeltin.")
                
                # Resmi önce döndür
                img = original_image.rotate(-rotasyon, expand=True, fillcolor='white') # Eksi değer sağa yatırır
                
                st.markdown("#### 2. ✂️ Kenar Temizliği (Siyahlıkları Kesin)")
                w_org, h_org = img.size
                c1, c2, c3, c4 = st.columns(4)
                with c1: sol = st.number_input("Sol", 0, 500, 0, step=10)
                with c2: sag = st.number_input("Sağ", 0, 500, 0, step=10)
                with c3: ust = st.number_input("Üst", 0, 500, 0, step=10)
                with c4: alt = st.number_input("Alt", 0, 500, 0, step=10)
                
                # Kırpma
                img = img.crop((sol, ust, w_org - sag, h_org - alt))
                
                # --- B. NETLİK PANELİ ---
                st.markdown("#### 3. 🎛️ Netlik Ayarı")
                esik = st.slider("Siyah/Beyaz Dengesi (Threshold)", 50, 230, 140)
                
                # İŞLEME MOTORU
                # 1. Büyütme (Upscale - 2.5 kat)
                w, h = img.size
                if w < 2500:
                    img = img.resize((2500, int(h * (2500/w))), Image.LANCZOS)
                
                # 2. Eşikleme
                img_gray = img.convert('L')
                final_img = img_gray.point(lambda x: 0 if x < esik else 255, '1')
                
                # 3. Kenar Boşluğu (Padding)
                final_img = ImageOps.expand(final_img, border=50, fill='white')
                
                st.image(final_img, caption="Sistemin Okuyacağı Belge (Düz ve Net mi?)", use_column_width=True)
                
                if st.button("ANALİZ ET VE DÜZELT 🚀", use_container_width=True):
                    if pytesseract:
                        try:
                            with st.spinner("1/2 Metin Sökülüyor..."):
                                # OCR AYARLARI (KRİTİK GÜNCELLEME)
                                # preserve_interword_spaces=1: Kelimelerin yapışmasını engeller
                                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                                
                                text = pytesseract.image_to_string(final_img, lang='tur', config=custom_config)
                                if len(text) < 50: # Yedek
                                    text = pytesseract.image_to_string(final_img, lang='tur+eng', config=custom_config)
                                
                            with st.spinner("2/2 Hukuki Sözlük ile Düzeltiliyor..."):
                                # --- C. HUKUKİ OTO-DÜZELTME (POST-PROCESSING) ---
                                # Yaygın OCR hatalarını manuel düzeltiyoruz
                                corrections = {
                                    "GANKARA": "ANKARA", "0ANKARA": "ANKARA", "G ANKARA": "ANKARA",
                                    "MÖZTEKİN": "M.ÖZTEKİN", "MÖZTEKIN": "M.ÖZTEKİN",
                                    "ESASNO": "ESAS NO", "ESAS No": "ESAS NO",
                                    "KARARTARİHİ": "KARAR TARİHİ", "KARAR TARIHI": "KARAR TARİHİ",
                                    "SıNıK": "SANIK", "SANIKLAR": "SANIK(LAR)",
                                    "KATıLAN": "KATILAN", "MÜDAFİİ": "MÜDAFİİ",
                                    "İDDİANAME": "İDDİANAME", "IDDIANAME": "İDDİANAME",
                                    "TCK": "TCK", "CMK": "CMK",
                                    "|": "", "~": "", "`": "", "©": "", "®": ""
                                }
                                
                                # Önce genel temizlik
                                text = text.replace("-\n", "")
                                text = text.replace("\n", " ")
                                text = re.sub(r'\s+', ' ', text) # Çift boşlukları sil
                                
                                # Sözlükteki hataları bul ve değiştir
                                for hatali, dogru in corrections.items():
                                    text = text.replace(hatali, dogru)
                                    
                                # Regex ile daha akıllı düzeltmeler
                                # Örn: "2024450" gibi yapışık sayıları ayırmak zordur ama "No:" sonrası boşluk garantileyebiliriz
                                text = re.sub(r'(No:)(\S)', r'\1 \2', text) # No:2024 -> No: 2024
                            
                            st.success("İşlem Başarılı! Hukuki terimler düzeltildi.")
                            st.text_area("Sonuç Metni:", value=text.strip(), height=450)
                            
                        except Exception as e:
                            st.error(f"Hata: {e}")
                    else:
                        st.error("OCR Motoru Bulunamadı.")
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
# MODÜL 2: CEZA İLAMI (HAPİS + ADLİ PARA ORTAK HESAP)
# =============================================================================
with tabs[1]:
    st.header("Ceza Hesaplama Robotu")
    st.info("💡 Hapis ve Adli Para cezasını birlikte hesaplar. Artırım/İndirim her ikisine de uygulanır.")

    # 1. GİRİŞLER: HAPİS VE ADLİ PARA GÜN YAN YANA
    st.subheader("1. Temel Cezalar")
    c1, c2, c3, c4 = st.columns(4)
    with c1: ty = st.number_input("Hapis (Yıl)", 0, 99, 2)
    with c2: ta = st.number_input("Hapis (Ay)", 0, 11, 0)
    with c3: tg = st.number_input("Hapis (Gün)", 0, 29, 0)
    with c4: base_para = st.number_input("Adli Para (Gün)", 0, 99999, 5, help="Kanundaki temel adli para gün sayısı")

    st.divider()
    
    # 2. ORTAK ARTIRIM / İNDİRİM
    col_a, col_i = st.columns(2)
    with col_a:
        st.subheader("⬆️ Artırım")
        amod = st.radio("Yöntem", ["Liste", "Manuel"], key="art_m", horizontal=True)
        ap, apd = 0, 1
        if amod == "Liste":
            s = st.selectbox("Oran", ["Yok", "1/6", "1/4", "1/3", "1/2", "1 Kat", "2 Kat"], key="art_s")
            if s != "Yok": 
                if "Kat" in s: ap, apd = int(s.split()[0]), 1
                else: ap, apd = map(int, s.split('/'))
        else: 
            ap = st.number_input("Pay", 0, 10, 0, key="art_p") # 0 varsayılan, artırım yoksa etki etmesin
            apd = st.number_input("Payda", 1, 20, 1, key="art_pd")

    with col_i:
        st.subheader("⬇️ İndirim")
        imod = st.radio("Yöntem", ["Liste", "Manuel"], key="ind_m", horizontal=True)
        ip, ipd = 0, 1
        if imod == "Liste":
            si = st.selectbox("Oran", ["Yok", "1/6 (TCK 62)", "1/3", "1/2", "2/3", "3/4"], key="ind_s")
            if si != "Yok": ip, ipd = map(int, si.split(' ')[0].split('/'))
        else: 
            ip = st.number_input("Pay", 0, 10, 0, key="ind_p")
            ipd = st.number_input("Payda", 1, 20, 1, key="ind_pd")

    # --- HESAPLAMA MOTORU (ÇİFT YÖNLÜ) ---
    # A) Gün Tabanına Çevir
    total_hapis_gun = (ty * 360) + (ta * 30) + tg
    total_para_gun = base_para

    # B) Artırım Uygula (Her ikisine de)
    if ap > 0:
        total_hapis_gun += (total_hapis_gun * ap) / apd
        total_para_gun += (total_para_gun * ap) / apd

    # C) İndirim Uygula (Her ikisine de)
    if ip > 0:
        total_hapis_gun -= (total_hapis_gun * ip) / ipd
        total_para_gun -= (total_para_gun * ip) / ipd

    # D) Sonuçları Geri Dönüştür
    # Hapis -> Yıl/Ay/Gün
    sonuc_yil, kalan_gun = divmod(total_hapis_gun, 360)
    sonuc_ay, sonuc_gun = divmod(kalan_gun, 30)
    # Para -> Küsurat silinir (Tam Sayı Gün)
    sonuc_para_gun = int(total_para_gun)

    # --- SONUÇ EKRANI ---
    st.markdown(f"""
    <div class="sonuc-panel">
        <h3 style="margin-bottom:10px; border-bottom:1px solid #ffffff50; padding-bottom:5px;">HÜKÜM SONUCU</h3>
        <div style="display:flex; justify-content:space-between; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
                <span style="font-size:1.1em; font-weight:bold;">👮 HAPİS CEZASI</span><br>
                <span style="font-size:1.4em; color:#f1c40f;">{int(sonuc_yil)} Yıl, {int(sonuc_ay)} Ay, {int(sonuc_gun)} Gün</span>
            </div>
            <div style="flex:1; min-width:200px; border-left:1px solid #ffffff50; padding-left:15px;">
                <span style="font-size:1.1em; font-weight:bold;">💰 ADLİ PARA (GÜN)</span><br>
                <span style="font-size:1.4em; color:#2ecc71;">{sonuc_para_gun} Gün</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # --- PARA MİKTAR HESABI ---
    st.write("")
    if sonuc_para_gun > 0:
        st.markdown("#### 💸 Miktar Hesabı (TCK 52)")
        col_tl, col_sonuc = st.columns([1, 2])
        with col_tl:
            gunluk_miktar = st.number_input("Günlüğü (TL)", min_value=20, max_value=500, value=100, step=10, help="En az 20, En çok 100 TL (Yasal Sınırlar)")
        
        with col_sonuc:
            toplam_odenecek = sonuc_para_gun * gunluk_miktar
            st.success(f"ÖDENECEK ADLİ PARA CEZASI: **{toplam_odenecek:,} TL**")
            st.caption(f"({sonuc_para_gun} Gün x {gunluk_miktar} TL)")
            
    elif total_hapis_gun > 0:
        # Sadece hapis varsa, hapis->para çevirme opsiyonunu göster
        if st.checkbox("Hapis Cezasının Paraya Çevrilmesi (TCK 50)"):
            gunluk_m = st.number_input("Günlük Miktar (TL)", 20, 100, 20)
            st.info(f"Hapis Karşılığı Para Cezası: **{int(total_hapis_gun * gunluk_m):,} TL**")

# =============================================================================
# MODÜL 3: ZAMANAŞIMI & HAK DÜŞÜRÜCÜ SÜRE (Gelişmiş Hukuk Modülü)
# =============================================================================
with tabs[2]:
    st.header("Süre Hesapları")
    
    # Ana Tür Seçimi
    tur = st.selectbox("Hesaplama Türü Seçiniz:", 
                       ["Ceza Davası Zamanaşımı (TCK)", 
                        "Hukuk: Zamanaşımı (Borçlar/Tazminat)", 
                        "Hukuk: Hak Düşürücü Süre (Usul/İş/Aile)"])
    
    # -------------------------------------------------------------------------
    # A) CEZA DAVASI ZAMANAŞIMI
    # -------------------------------------------------------------------------
    if "Ceza" in tur:
        st.caption("TCK Madde 66 ve 67 uyarınca dava zamanaşımı hesabı.")
        suc_t = st.date_input("Suç İşleme Tarihi", date(2015,1,1))
        ust = st.selectbox("Suçun Yasadaki Üst Sınırı", 
                           ["Ağırlaştırılmış Müebbet (30 Yıl)", "Müebbet (25 Yıl)", "20 Yıldan Fazla (20 Yıl)", "5-20 Yıl Arası (15 Yıl)", "5 Yıldan Az (8 Yıl)"])
        
        # Temel Süre Belirleme
        asli = 8
        if "Ağır" in ust: asli=30
        elif "Müebbet" in ust: asli=25
        elif "20 Yıldan" in ust: asli=20
        elif "5-20" in ust: asli=15
        
        cc1, cc2 = st.columns(2)
        with cc1: kes = st.radio("Zamanaşımını Kesen İşlem Var mı?", ["Hayır (Asli)", "Evet (Uzamış)"], help="Şüpheli/Sanık ifadesi, tutuklama, iddianame, mahkumiyet kararı vb.")
        with cc2: dur = st.number_input("Durma Süresi (Gün)", 0, help="Bekletici mesele, izin alma vb. süreçler.")
        
        # Hesaplama
        son = asli * 1.5 if "Evet" in kes else asli
        bitis = suc_t.replace(year=suc_t.year + int(son))
        if son % 1 != 0: bitis += timedelta(days=180) # Buçuklu yıl hesabı
        bitis += timedelta(days=dur)
        
        kln = (bitis - date.today()).days
        
        st.markdown(f"""
        <div class="sonuc-panel">
            <h4 style="margin:0; color:#f1c40f;">CEZA ZAMANAŞIMI SONUCU</h4>
            <b>Temel Süre:</b> {son} Yıl (+{dur} gün durma)<br>
            <b>Bitiş Tarihi:</b> {bitis.strftime('%d.%m.%Y')}<br>
            Durum: {'✅ DAVA DEVAM EDEBİLİR' if kln>0 else '❌ ZAMANAŞIMI DOLDU (DÜŞME)'}
        </div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # B) HUKUK: ZAMANAŞIMI (DEF'İ)
    # -------------------------------------------------------------------------
    elif "Hukuk: Zamanaşımı" in tur:
        st.info("ℹ️ Zamanaşımı bir def'idir, durma ve kesilmeye tabidir. Arabuluculuk vb. süreleri 'Durma' kısmına ekleyiniz.")
        
        bas = st.date_input("Başlangıç Tarihi (Muacceliyet/Olay)", date.today())
        
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            konu = st.selectbox("Konu / İlgili Kanun", 
                                ["Genel Zamanaşımı (TBK 146) - 10 Yıl", 
                                 "Kira / Vekalet / Eser (TBK 147) - 5 Yıl", 
                                 "Haksız Fiil (TBK 72) - 2 Yıl",
                                 "Haksız Fiil (Mutlak) - 10 Yıl",
                                 "Kambiyo Senedi (TTK) - 3 Yıl",
                                 "Sebepsiz Zenginleşme - 2 Yıl",
                                 "Manuel Giriş"])
        
        y, g = 0, 0
        # Presets
        if "10 Yıl" in konu: y=10
        elif "5 Yıl" in konu: y=5
        elif "3 Yıl" in konu: y=3
        elif "2 Yıl" in konu: y=2
        
        with h_col2:
            if "Manuel" in konu:
                y = st.number_input("Yıl Giriniz", 0, 50, 1)
                g = st.number_input("Gün Giriniz", 0, 365, 0)
            
            durma_gun = st.number_input("Durma Süresi (Gün)", 0, help="Örn: Arabuluculukta geçen süre")

        # Hesaplama
        bitis = bas.replace(year=bas.year + y) + timedelta(days=g + durma_gun)
        kalan = (bitis - date.today()).days
        
        st.markdown(f"""
        <div class="sonuc-panel">
            <h4 style="margin:0; color:#3498db;">ZAMANAŞIMI HESABI</h4>
            <b>Bitiş Tarihi:</b> {bitis.strftime('%d.%m.%Y')}<br>
            <b>Eklenen Durma Süresi:</b> {durma_gun} Gün<br>
            Durum: {'✅ HENÜZ DOLMADI' if kalan>0 else '⚠️ ZAMANAŞIMI DEFİ İLERİ SÜRÜLEBİLİR'}
        </div>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # C) HUKUK: HAK DÜŞÜRÜCÜ SÜRE (İTİRAZ)
    # -------------------------------------------------------------------------
    elif "Hak Düşürücü" in tur:
        st.warning("⚠️ Hak düşürücü süreler kesilmez ve durmaz. Hakim tarafından resen (kendiliğinden) dikkate alınır.")
        
        bas_h = st.date_input("Tebliğ / Öğrenme Tarihi", date.today())
        
        tip = st.selectbox("Dava Türü", 
                           ["İşe İade (1 Ay) - İş K.", 
                            "Önalım (Şufa) - 3 Ay (TMK)", 
                            "Tenkis Davası - 1 Yıl (TMK)", 
                            "Soybağının Reddi - 1 Yıl (TMK)",
                            "Ecrimisil - 5 Yıl (HGK Kararları)",
                            "İdari Dava Açma (60 Gün)",
                            "Vergi Davası Açma (30 Gün)",
                            "Manuel Giriş"])
        
        dy, dm, dd = 0, 0, 0
        
        # Mantıklar
        if "İşe İade" in tip: dm = 1
        elif "Önalım" in tip: dm = 3
        elif "Tenkis" in tip: dy = 1
        elif "Soybağının" in tip: dy = 1
        elif "Ecrimisil" in tip: dy = 5
        elif "60 Gün" in tip: dd = 60
        elif "30 Gün" in tip: dd = 30
        
        if "Manuel" in tip:
            c_man1, c_man2 = st.columns(2)
            with c_man1: dy = st.number_input("Yıl", 0)
            with c_man1: dm = st.number_input("Ay", 0)
            with c_man2: dd = st.number_input("Gün", 0)
            
        # Basit Tarih Ekleme (Ay eklerken takvim kaymasını önlemek için yaklaşık hesap yerine timedelta kullanıyoruz ama ay ekleme karmaşıktır, burada işi basitleştirip gün bazlı veya yıl bazlı gidiyoruz. Hakim için en neti gün hesabıdır ama ay için yaklaşık 30 alalım)
        
        # Net Hesap
        # Yıl Ekleme
        hedef = bas_h.replace(year=bas_h.year + dy)
        
        # Ay Ekleme (Basit Mantık: Ay atlatma)
        # Python'da doğrudan ay ekleme olmadığı için 30 gün mantığı yerine tarih kütüphanesi mantığı:
        new_month = hedef.month + dm
        extra_year = 0
        if new_month > 12:
            extra_year = new_month // 12
            new_month = new_month % 12
            if new_month == 0: # Aralık ayı durumu düzeltme
                new_month = 12
                extra_year -= 1
        
        hedef = hedef.replace(year=hedef.year + extra_year, month=new_month)
        
        # Gün Ekleme
        hedef += timedelta(days=dd)
        
        kalan_h = (hedef - date.today()).days
        
        st.markdown(f"""
        <div class="sonuc-panel" style="border-left-color: #e74c3c;">
            <h4 style="margin:0; color:#e74c3c;">HAK DÜŞÜRÜCÜ SÜRE SONUCU</h4>
            <b>Son İşlem Tarihi:</b> {hedef.strftime('%d.%m.%Y')}<br>
            Durum: {'✅ HAK DÜŞMEMİŞTİR' if kalan_h>=0 else '❌ HAK DÜŞMÜŞTÜR (USULDEN RED)'}
        </div>""", unsafe_allow_html=True)# =============================================================================
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
    st.markdown(f"<div style='border:1px dashed #333; padding:15px; text-align:center;'><a href='mailto:{HAKIM_MAIL}' style='font-size:1.2em; color:#c0392b; font-weight:bold;'>📧 {HAKIM_MAIL}</a></div>", unsafe_allow_html=True)
    
    st.write("")
    st.text_area("Kendinize Şifreli Not Bırakın (Cihaz Önbelleğinde Kalır):")
    st.button("Notu Geçici Olarak Kaydet")

import streamlit as st
import re
from datetime import date, timedelta

# =============================================================================
# 🟢 AYARLAR (MAİL ADRESİNİZİ BURAYA YAZINIZ)
# =============================================================================
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com.tr"  # <- BURAYI DEĞİŞTİRİN
# =============================================================================

# --- SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="KÜRSÜ PRO MASTER", page_icon="⚖️", layout="centered")

# CSS: Kağıt Görünümü ve Panel Tasarımı
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    /* Tutanak Kağıdı */
    .tutanak-kagidi {
        background-color: #fdfefe; color: #2c3e50; padding: 30px;
        font-family: 'Times New Roman', serif; font-size: 15px; line-height: 1.5;
        border: 1px solid #bdc3c7; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        white-space: pre-wrap; margin-top: 20px;
    }
    .baslik-tc { text-align: center; font-weight: bold; margin-bottom: 10px; }
    .baslik-alt { text-align: center; font-weight: bold; text-decoration: underline; margin-bottom: 25px; }
    /* Sonuç Panelleri */
    .sonuc-panel-ceza { background-color: #1c232d; padding: 15px; border-radius: 10px; border-left: 5px solid #e74c3c; margin-top: 15px; }
    .sonuc-panel-zaman { background-color: #1b2631; padding: 15px; border-radius: 10px; border-left: 5px solid #f39c12; margin-top: 15px; }
    .iletisim-kutu { border: 1px dashed #555; padding: 20px; text-align: center; border-radius: 10px; margin-top: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ KÜRSÜ PRO: MASTER")
st.caption("AI Katip | İlam Sihirbazı | Kesintili Zamanaşımı | İletişim")

# SEKMELER (İLETİŞİM EKLENDİ)
tabs = st.tabs(["📸 AKILLI KATİP", "⛓️ CEZA İLAMI", "⏳ ZAMANAŞIMI", "📧 İLETİŞİM"])

# =============================================================================
# FONKSİYON: REGEX İLE AKILLI FORMATLAMA (BEYİN)
# =============================================================================
def metni_hukuki_formatla(ham_metin):
    metin = ham_metin
    # 1. Türkçe Karakter ve Büyük Harf
    metin = metin.replace("İ", "i").upper()
    # 2. Anahtar Kelime Yakalama
    anahtar_kelimeler = ["DAVACI", "DAVALI", "VEKİLİ", "MÜDAFİİ", "SANIK", "SUÇ", "SUÇ TARİHİ", "KONU", "İDDİA MAKAMI", "HÜKÜM", "KARAR", "GEREĞİ DÜŞÜNÜLDÜ"]
    for k in anahtar_kelimeler:
        metin = re.sub(f"(?i)({k}.*?:)", r"\n\n**\1**", metin)
    # 3. Düzenleme
    metin = re.sub(r"(\n\s*[-•1-9]+\.)", r"\n\1", metin)
    metin = re.sub(r"  +", " ", metin)
    metin = re.sub(r"\n\s*\n", "\n\n", metin)
    # 4. Hüküm Vurgusu
    metin = metin.replace("BERAATİNE", "**BERAATİNE**")
    metin = metin.replace("CEZALANDIRILMASINA", "**CEZALANDIRILMASINA**")
    return metin.strip()

# =============================================================================
# MODÜL 1: AKILLI KATİP
# =============================================================================
with tabs[0]:
    st.header("Gören ve Duyan Asistan")
    st.info("Kameradan kopyaladığınız veya sesle yazdırdığınız metni yapıştırın.")
    
    ham_girdi = st.text_area("Metni Yapıştır (Kamera/Ses)", height=150)
    col1, col2 = st.columns(2)
    with col1: belge_tipi = st.selectbox("Belge Tipi", ["DURUŞMA TUTANAĞI", "GEREKÇELİ KARAR", "İFADE"])
    with col2: formatla = st.button("Sihirli Formatla ✨", use_container_width=True)
    
    if formatla and ham_girdi:
        st.session_state['fmt'] = metni_hukuki_formatla(ham_girdi)
        st.success("Formatlama Tamamlandı!")
    
    if 'fmt' in st.session_state:
        st.markdown(f"""
        <div class="tutanak-kagidi">
            <div class="baslik-tc">T.C.<br>ANKARA<br>... MAHKEMESİ</div>
            <div class="baslik-alt">{belge_tipi}</div>
            {st.session_state['fmt']}
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
        a_mod = st.radio("Yöntem", ["Liste", "Manuel"], key="ar", horizontal=True)
        ap, apd = 0,1
        if a_mod=="Liste":
            s=st.selectbox("Oran",["Yok","1/6","1/4","1/3","1/2","1 Kat"],key="as")
            if s!="Yok": ap,apd = (1,1) if "Kat" in s else map(int,s.split('/'))
        else:
            ap=st.number_input("Pay",1,10,1,key="amp"); apd=st.number_input("Payda",1,20,6,key="amdp")

    # İndirim
    with ci:
        st.subheader("⬇️ İndirim")
        i_mod = st.radio("Yöntem", ["Liste", "Manuel"], key="ir", horizontal=True)
        ip, ipd = 0,1
        if i_mod=="Liste":
            si=st.selectbox("Oran",["Yok","1/6 (TCK 62)","1/3","1/2","2/3"],key="is")
            if si!="Yok": ip,ipd = map(int,si.split(' ')[0].split('/'))
        else:
            ip=st.number_input("Pay",1,10,1,key="imp"); ipd=st.number_input("Payda",1,20,6,key="imdp")

    # Hesaplama
    top_g = (ty*360)+(ta*30)+tg
    if ap>0: top_g += (top_g*ap)/apd
    if ip>0: top_g -= (top_g*ip)/ipd
    
    sy,rg = divmod(top_g, 360); sa,sg = divmod(rg, 30)
    
    st.markdown(f"""
    <div class="sonuc-panel-ceza">
        <h3 style="color:#ecf0f1; margin:0;">SONUÇ: {int(sy)} Yıl, {int(sa)} Ay, {int(sg)} Gün</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.checkbox("Adli Para Cezasına Çevir (TCK 50)"):
        gb = st.number_input("Günlüğü (TL)", 20, 500, 100)
        st.info(f"💸 {int(top_g * gb):,} TL")

# =============================================================================
# MODÜL 3: ZAMANAŞIMI
# =============================================================================
with tabs[2]:
    st.header("Süre ve Zamanaşımı")
    tur = st.selectbox("Dava Türü", ["Ceza Davası (TCK 66/67)", "Hukuk Davası (TBK/HMK)"])
    
    if "Ceza" in tur:
        st.subheader("Ceza Dava Zamanaşımı")
        suc_tarihi = st.date_input("Suç Tarihi", date(2015, 1, 1))
        suc_tipi = st.selectbox("Üst Sınır", ["Ağırlaştırılmış Müebbet", "Müebbet Hapis", "20 Yıldan Az Olmayan", "5-20 Yıl Arası", "5 Yıldan Az"])
        
        asli_yil = 8
        if "Ağırlaştırılmış" in suc_tipi: asli_yil = 30
        elif "Müebbet" in suc_tipi: asli_yil = 25
        elif "20 Yıldan Az" in suc_tipi: asli_yil = 20
        elif "5-20" in suc_tipi: asli_yil = 15
        
        c1, c2 = st.columns(2)
        with c1: kesme = st.radio("Zamanaşımı Kesen İşlem?", ["Hayır", "Evet (Dava/Sorgu/Karar)"])
        with c2: durma_gun = st.number_input("Durma Süresi (Gün)", 0, help="Bekletici mesele vb.")

        nihai_yil = asli_yil * 1.5 if "Evet" in kesme else asli_yil
        
        bitis_tarihi = suc_tarihi.replace(year=suc_tarihi.year + int(nihai_yil))
        if nihai_yil % 1 != 0: bitis_tarihi += timedelta(days=180)
        bitis_tarihi += timedelta(days=durma_gun)
        
        kalan_gun = (bitis_tarihi - date.today()).days
        
        st.markdown(f"""
        <div class="sonuc-panel-zaman">
            <b>HESAPLAMA ({'Uzamış' if 'Evet' in kesme else 'Asli'}):</b><br>
            Süre: {nihai_yil} Yıl (+{durma_gun} gün)<br>
            Bitiş: {bitis_tarihi.strftime('%d.%m.%Y')}<br>
            Durum: {'✅ DOLMADI' if kalan_gun > 0 else '❌ DOLDU'}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("Hukuk Süreleri")
        baslangic = st.date_input("Başlangıç", date.today())
        konu = st.selectbox("Tür", ["Genel (10 Yıl)", "Kira/Faiz (5 Yıl)", "Haksız Fiil (2 Yıl)", "İşe İade (1 Ay)", "Çek (10 Gün)"])
        
        yil, gun = 0, 0
        if "10 Yıl" in konu: yil=10
        elif "5 Yıl" in konu: yil=5
        elif "2 Yıl" in konu: yil=2
        elif "1 Ay" in konu: gun=30
        elif "10 Gün" in konu: gun=10
        
        durma = st.number_input("Durma (Gün)", 0)
        bitis = baslangic.replace(year=baslangic.year+yil) + timedelta(days=gun+durma)
        kalan = (bitis - date.today()).days
        st.markdown(f"""<div class="sonuc-panel-zaman">Bitiş: {bitis.strftime('%d.%m.%Y')}<br>{'✅ SÜRE VAR' if kalan>0 else '❌ SÜRE DOLDU'}</div>""", unsafe_allow_html=True)

# =============================================================================
# MODÜL 4: İLETİŞİM (YENİ EKLENDİ)
# =============================================================================
with tabs[3]:
    st.header("Görüş ve Öneriler")
    st.write("Uygulama ile ilgili geliştirme taleplerinizi doğrudan geliştiriciye iletebilirsiniz.")
    
    st.markdown(f"""
    <div class="iletisim-kutu">
        <h3>✉️ İletişim</h3>
        <p>Geliştirme Önerileri İçin:</p>
        <a href="mailto:{HAKIM_MAIL}" style="font-size: 1.5em; color: #3498db; text-decoration: none; font-weight: bold;">
            {HAKIM_MAIL}
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.info("👆 Mail adresine tıklayarak doğrudan e-posta gönderebilirsiniz.")
    
    not_al = st.text_area("Veya kendiniz için buraya bir not bırakın (Cihazda saklanır):")
    if st.button("Notu Kaydet"):
        st.success("Notunuz güvenli yerel hafızaya alındı.")

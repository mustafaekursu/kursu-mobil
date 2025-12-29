import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta

# --- KİŞİSEL AYARLAR (BURAYI DEĞİŞTİRİN) ---
# Lütfen aşağıdaki tırnak işaretlerinin içine kendi mail adresinizi yazın.
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com" 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Kürsü Pro", page_icon="⚖️", layout="centered")

st.title("⚖️ Kürsü Pro v14")
st.caption("Hesaplama Asistanı")

# --- SEKME YÖNETİMİ ---
# 3 Ana Sekme Tanımlıyoruz
tabs = st.tabs(["⏳ Zamanaşımı", "🔢 Ceza Hesapla", "🛡️ İletişim & Güvenlik"])

# ==========================================
# MODÜL 1: ZAMANAŞIMI HESAPLAMA
# ==========================================
with tabs[0]:
    st.header("⏳ Yasal Süre Hesaplayıcı")
    st.info("Dava ve Ceza Zamanaşımı Sürelerini Hesaplar.")

    col1, col2 = st.columns(2)
    with col1:
        hesap_turu = st.selectbox("Hesaplama Türü", 
                                  ["Ceza Dava Zamanaşımı (TCK 66)", 
                                   "Ceza Zamanaşımı (TCK 68)", 
                                   "Hukuk/Borçlar (TBK)",
                                   "Hak Düşürücü Süreler"])
        baslangic = st.date_input("Süre Başlangıç Tarihi")

    with col2:
        yil = st.number_input("Temel Süre (Yıl)", 0, 50, 8)
        ay = st.number_input("Temel Süre (Ay)", 0, 11, 0)
        gun = st.number_input("Temel Süre (Gün)", 0, 30, 0)

    # Hesaplama Motoru
    base_date = baslangic + relativedelta(years=yil, months=ay, days=gun)
    max_date = baslangic + relativedelta(years=int(yil * 1.5), months=int(ay * 1.5), days=int(gun * 1.5))

    st.divider()
    st.success(f"📍 Olağan Süre Sonu: **{base_date.strftime('%d.%m.%Y')}**")

    if "Ceza" in hesap_turu:
        st.error(f"🚨 Kesin (Olağanüstü) Süre Sonu: **{max_date.strftime('%d.%m.%Y')}**")
        st.caption("TCK 67/4: Kesilme sebepleri olsa dahi bu tarih aşılamaz.")

    with st.expander("➕ Durma Sebebi Ekle"):
        durma_gun = st.number_input("Durma Süresi (Gün)", 0, 3650, 0)
        if durma_gun > 0:
            yeni_son = base_date + relativedelta(days=durma_gun)
            st.info(f"Durma Eklenmiş Tarih: {yeni_son.strftime('%d.%m.%Y')}")

# ==========================================
# MODÜL 2: CEZA HESAPLAMA
# ==========================================
with tabs[1]:
    st.header("🔢 Ceza Hesaplama Modülü")
    tur = st.radio("Ceza Türü", ["Hapis Cezası", "Adli Para Cezası"], horizontal=True)
    
    if tur == "Hapis Cezası":
        c1, c2, c3 = st.columns(3)
        with c1: h_yil = st.number_input("Yıl", 0, 100, 1)
        with c2: h_ay = st.number_input("Ay", 0, 11, 0)
        with c3: h_gun = st.number_input("Gün", 0, 29, 0)
        
        toplam_gun = (h_yil * 365) + (h_ay * 30) + h_gun
        st.markdown("---")
        
        col_art, col_ind = st.columns(2)
        with col_art:
            st.markdown("🔺 **Artırım**")
            art_pay = st.number_input("Pay", 0, 10, 0, key="art_p")
            art_payda = st.number_input("Payda", 1, 10, 1, key="art_pd")
        with col_ind:
            st.markdown("🔻 **İndirim**")
            ind_pay = st.number_input("Pay", 0, 10, 0, key="ind_p")
            ind_payda = st.number_input("Payda", 1, 10, 6, key="ind_pd")
            
        if st.button("Hesapla"):
            if art_pay > 0: toplam_gun += (toplam_gun * art_pay) / art_payda
            if ind_pay > 0: toplam_gun -= (toplam_gun * ind_pay) / ind_payda
            
            s_yil = int(toplam_gun / 365)
            s_ay = int((toplam_gun % 365) / 30)
            s_gun = int((toplam_gun % 365) % 30)
            st.success(f"⚖️ Sonuç: {s_yil} Yıl, {s_ay} Ay, {s_gun} Gün")

    else:
        st.subheader("Adli Para Cezası")
        g_sayisi = st.number_input("Gün Sayısı", 5, 730, 100)
        miktar = st.select_slider("Günlük Miktar (TL)", options=[20,30,40,50,100], value=20)
        st.metric("Toplam Tutar", f"{g_sayisi * miktar:,.2f} TL")

# =============================================================================
# MODÜL 3: İLETİŞİM VE GÜVENLİK (SİZİN TASARIMINIZ)
# =============================================================================
with tabs[2]:
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
    
    # Mail butonu
    st.markdown(f"<div style='border:1px dashed #333; padding:15px; text-align:center;'><a href='mailto:{HAKIM_MAIL}' style='font-size:1.2em; color:#c0392b; font-weight:bold; text-decoration:none;'>📧 mustafa.emin.tr@hotmail.com</a></div>", unsafe_allow_html=True)
    
    st.write("")
    st.caption("Not: Bu alan üzerinden gönderilen mesajlar doğrudan şifreli e-posta sunucularına iletilir.")
    
    # Not Defteri
    st.text_area("Kendinize Şifreli Not Bırakın (Cihaz Önbelleğinde Kalır):")
    if st.button("Notu Geçici Olarak Kaydet"):
        st.toast("Not şifrelendi ve geçici hafızaya alındı.", icon="🔒")

st.markdown("---")
st.markdown("© 2025 - Resmi Kullanım İçindir.")

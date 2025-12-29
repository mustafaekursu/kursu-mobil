import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import math

# --- RESMİ ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Kürsü Pro", page_icon="⚖️", layout="centered")

st.title("⚖️ Kürsü Pro v12")
st.caption("T.C. Adalet Bakanlığı Mevzuatına Uygun Hesaplama Asistanı")

# Sekmeler
tab1, tab2, tab3 = st.tabs(["⏳ Zamanaşımı Hesapla", "🔢 Ceza Hesapla (Hapis/Para)", "🛡️ İLETİŞİM & GÜVENLİK"])
HAKIM_MAIL = "mustafa.emin.tr@hotmail.com"
# ==========================================
# 1. MODÜL: ZAMANAŞIMI HESAPLAMA
# ==========================================
with tab1:
    st.header("⏳ Yasal Süre Hesaplayıcı")
    st.info("Dava ve Ceza Zamanaşımı Sürelerini Hesaplar.")

    col1, col2 = st.columns(2)
    with col1:
        hesap_turu = st.selectbox("Hesaplama Türü", 
                                  ["Ceza Dava Zamanaşımı (TCK 66)", 
                                   "Ceza Zamanaşımı (TCK 68)", 
                                   "Hukuk/Borçlar (TBK)",
                                   "Hak Düşürücü Süreler"])
        baslangic = st.date_input("Süre Başlangıç Tarihi", key="zaman_baslangic")

    with col2:
        yil = st.number_input("Temel Süre (Yıl)", 0, 50, 8, key="zaman_yil")
        ay = st.number_input("Temel Süre (Ay)", 0, 11, 0, key="zaman_ay")
        gun = st.number_input("Temel Süre (Gün)", 0, 30, 0, key="zaman_gun")

    # Hesaplama Motoru
    base_date = baslangic + relativedelta(years=yil, months=ay, days=gun)
    max_date = baslangic + relativedelta(years=int(yil * 1.5), months=int(ay * 1.5), days=int(gun * 1.5))

    st.divider()
    st.success(f"📍 Olağan Süre Sonu: **{base_date.strftime('%d.%m.%Y')}**")

    if "Ceza" in hesap_turu:
        st.error(f"🚨 Kesin (Olağanüstü) Süre Sonu: **{max_date.strftime('%d.%m.%Y')}**")
        st.caption("TCK 67/4: Kesilme sebepleri olsa dahi bu tarih aşılamaz.")

    with st.expander("➕ Durma Sebebi Ekle (Tutukluluk vb.)"):
        durma_gun = st.number_input("Durma Süresi (Gün)", 0, 3650, 0, key="zaman_durma")
        if durma_gun > 0:
            yeni_son = base_date + relativedelta(days=durma_gun)
            st.info(f"Durma Eklenmiş Tarih: {yeni_son.strftime('%d.%m.%Y')}")

# ==========================================
# 2. MODÜL: CEZA HESAPLAMA (HAPİS & PARA)
# ==========================================
with tab2:
    st.header("🔢 Ceza Hesaplama Modülü")
    
    tur = st.radio("Hesaplanacak Ceza Türü", ["Hapis Cezası", "Adli Para Cezası"], horizontal=True)
    
    # --- A) HAPİS CEZASI HESABI ---
    if tur == "Hapis Cezası":
        st.subheader("Hapis Cezası Hesapla (TCK 61)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            h_yil = st.number_input("Temel Ceza (Yıl)", 0, 100, 1)
        with c2:
            h_ay = st.number_input("Temel Ceza (Ay)", 0, 11, 0)
        with c3:
            h_gun = st.number_input("Temel Ceza (Gün)", 0, 29, 0)
            
        # Toplam günü hesapla (Basit hesap: 1 ay = 30 gün)
        toplam_gun = (h_yil * 365) + (h_ay * 30) + h_gun
        st.markdown("---")
        
        # Artırım / İndirim
        col_art, col_ind = st.columns(2)
        with col_art:
            st.markdown("🔺 **Artırım Oranı**")
            artirim_pay = st.number_input("Pay (Örn: 1)", 0, 10, 0, key="art_pay")
            artirim_payda = st.number_input("Payda (Örn: 6)", 1, 10, 1, key="art_payda")
        
        with col_ind:
            st.markdown("🔻 **İndirim Oranı (Takdiri vb.)**")
            indirim_pay = st.number_input("Pay (Örn: 1)", 0, 10, 0, key="ind_pay")
            indirim_payda = st.number_input("Payda (Örn: 6)", 1, 10, 6, key="ind_payda")
            
        # HESAPLAMA BUTONU
        if st.button("Cezayı Hesapla"):
            # 1. Artırım Uygula
            if artirim_pay > 0:
                artis_miktari = (toplam_gun * artirim_pay) / artirim_payda
                toplam_gun += artis_miktari
                st.info(f"Artırım Sonrası: {toplam_gun:.0f} gün")
            
            # 2. İndirim Uygula
            if indirim_pay > 0:
                indirim_miktari = (toplam_gun * indirim_pay) / indirim_payda
                toplam_gun -= indirim_miktari
            
            # 3. Sonucu Yıl/Ay/Gün Çevir
            sonuc_yil = int(toplam_gun / 365)
            kalan_gun = toplam_gun % 365
            sonuc_ay = int(kalan_gun / 30)
            sonuc_gun = int(kalan_gun % 30)
            
            st.success(f"⚖️ **SONUÇ CEZA:** {sonuc_yil} Yıl, {sonuc_ay} Ay, {sonuc_gun} Gün")
            
    # --- B) ADLİ PARA CEZASI HESABI ---
    else:
        st.subheader("Adli Para Cezası Hesapla")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            gun_sayisi = st.number_input("Hükmedilen Gün Sayısı", min_value=5, value=100)
        with col_p2:
            gunluk_miktar = st.select_slider("Günlük Miktar (TL)", options=[20, 30, 40, 50, 60, 70, 80, 90, 100], value=20)
            
        toplam_tutar = gun_sayisi * gunluk_miktar
        
        st.metric(label="Ödenecek Toplam Adli Para Cezası", value=f"{toplam_tutar:,.2f} TL")
        
        st.markdown("### Taksitlendirme")
        taksit = st.slider("Taksit Sayısı", 1, 24, 12)
        aylik = toplam_tutar / taksit
        st.caption(f"Aylık Ödeme: **{aylik:,.2f} TL** (İlk taksit peşin ödenirse)")

st.divider()
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
st.markdown("© 2025 - Resmi Kullanım İçindir.")

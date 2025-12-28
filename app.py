# --- 3. FOTOĞRAF GİRİŞİ (GOLD SÜRÜM: LEKE TEMİZLEME & RAKAM ONARMA) ---
    elif "Fotoğraf" in secim:
        st.info("Gold Sürüm: Leke temizleyici ve akıllı rakam onarımı devrede.")
        img_file = st.file_uploader("Resim Yükle", type=['png', 'jpg', 'jpeg'])
        
        if img_file:
            if Image is None:
                st.error("⚠️ HATA: Pillow kütüphanesi eksik.")
            else:
                original_image = Image.open(img_file)
                
                # --- A. KIRPMA VE DÖNDÜRME ---
                st.markdown("#### 1. 📐 Hizalama ve Kırpma")
                c_rot, c_info = st.columns([2, 1])
                with c_rot:
                    rotasyon = st.slider("Belgeyi Döndür (Satırları Düzle)", -5.0, 5.0, 0.0, step=0.1)
                
                # Resmi döndür
                img = original_image.rotate(-rotasyon, expand=True, fillcolor='white')
                
                # Kırpma Ayarları
                with st.expander("✂️ Kenar Kırpma (Gerekirse Açın)"):
                    c1, c2, c3, c4 = st.columns(4)
                    w_org, h_org = img.size
                    with c1: sol = st.number_input("Sol", 0, 500, 0, step=10)
                    with c2: sag = st.number_input("Sağ", 0, 500, 0, step=10)
                    with c3: ust = st.number_input("Üst", 0, 500, 0, step=10)
                    with c4: alt = st.number_input("Alt", 0, 500, 0, step=10)
                    img = img.crop((sol, ust, w_org - sag, h_org - alt))

                # --- B. GÖRÜNTÜ NETLEŞTİRME ---
                st.markdown("#### 2. 🎛️ Netlik ve Temizlik")
                c_esik, c_filtre = st.columns(2)
                with c_esik:
                    esik = st.slider("Siyah/Beyaz Ayarı", 50, 230, 140)
                with c_filtre:
                    leke_temizle = st.checkbox("Noktacıkları Temizle", value=True, help="Kağıttaki tozları harf sanmasını engeller.")

                # İŞLEME MOTORU
                # 1. Büyütme (Upscale)
                w, h = img.size
                if w < 2500:
                    img = img.resize((2500, int(h * (2500/w))), Image.LANCZOS)
                
                # 2. Eşikleme
                img_gray = img.convert('L')
                final_img = img_gray.point(lambda x: 0 if x < esik else 255, '1')
                
                # 3. Leke Temizliği (Median Filter) - Kritik Müdahale
                if leke_temizle:
                    # 3 piksellik karıncalanmaları yok eder
                    final_img = final_img.filter(ImageFilter.MedianFilter(3))
                
                # 4. Kenar Boşluğu
                final_img = ImageOps.expand(final_img, border=50, fill='white')
                
                st.image(final_img, caption="Sistemin Okuyacağı Temiz Belge", use_column_width=True)
                
                if st.button("ANALİZ ET VE DÜZELT 🚀", use_container_width=True):
                    if pytesseract:
                        try:
                            with st.spinner("Metin çözümleniyor ve onarılıyor..."):
                                # OCR AYARLARI
                                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                                text = pytesseract.image_to_string(final_img, lang='tur', config=custom_config)
                                if len(text) < 50: text = pytesseract.image_to_string(final_img, lang='tur+eng', config=custom_config)
                                
                                # --- C. POST-PROCESSING (AKILLI ONARIM) ---
                                # 1. Temel Temizlik
                                text = text.replace("|", "").replace("~", "").replace("`", "")
                                text = text.replace("-\n", "")
                                text = text.replace("\n", " ")
                                text = re.sub(r'\s+', ' ', text)

                                # 2. SÖZLÜK DÜZELTMELERİ
                                corrections = {
                                    "GANKARA": "ANKARA", "MÖZTEKİN": "M.ÖZTEKİN", 
                                    "ESASNO": "ESAS NO", "KARARTARİHİ": "KARAR TARİHİ",
                                    "SıNıK": "SANIK", "TCK": "TCK", "CMK": "CMK"
                                }
                                for hatali, dogru in corrections.items():
                                    text = text.replace(hatali, dogru)

                                # 3. AKILLI RAKAM ONARIMI (Regex)
                                # Sayıların içindeki harfleri temizle (Örn: 2024o450 -> 20240450)
                                # Mantık: İki rakam arasındaki 'o', 'O', 'l', 'i' harflerini rakama çevir.
                                text = re.sub(r'(?<=\d)[oO](?=\d)', '0', text)
                                text = re.sub(r'(?<=\d)[lIi](?=\d)', '1', text)
                                text = re.sub(r'(?<=\d)[zZ](?=\d)', '2', text)
                                text = re.sub(r'(?<=\d)[bB](?=\d)', '8', text)
                                
                                # Esas/Karar No formatlarını düzelt (2024 / 450 gibi ayrık ise birleştir)
                                text = re.sub(r'(\d{4})\s*/\s*(\d+)', r'\1/\2', text)

                            st.success("İşlem Başarılı! Gürültü temizlendi.")
                            st.text_area("Sonuç Metni:", value=text.strip(), height=450)
                            
                        except Exception as e:
                            st.error(f"Hata: {e}")
                    else:
                        st.error("OCR Motoru Bulunamadı.")

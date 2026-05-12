import streamlit as st
from datetime import date, datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import threading

# Sayfa Ayarları
st.set_page_config(page_title="Kösem | İş & Bildirim", page_icon="🌿", layout="wide")

# --- E-POSTA AYARLARI ---
GMAIL_ADRESI = "talipkosem90@gmail.com"
GMAIL_UYGULAMA_SIFRESI = "vlhl tpqd cova kjws" # Senin aldığın kod eklendi
ALICI_POSTA = "talipkosem90@gmail.com"

# --- E-POSTA GÖNDERME FONKSİYONU ---
def eposta_gonder(baslik, icerik):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADRESI
        msg['To'] = ALICI_POSTA
        msg['Subject'] = baslik
        msg.attach(MIMEText(icerik, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADRESI, GMAIL_UYGULAMA_SIFRESI)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# --- GÜNLÜK OTOMATİK KONTROL ---
def gunluk_kontrol():
    while True:
        simdi = datetime.now()
        if simdi.hour == 9 and simdi.minute == 0:
            try:
                df_temp = pd.read_csv("isler.csv", sep="|")
                devam_edenler = df_temp[df_temp["Durum"] == "Devam Ediyor"]
                
                if not devam_edenler.empty:
                    rapor_metni = "🌿 Kösem İş Takip Sistemi - Günlük Hatırlatma\n\n"
                    rapor_metni += "Bugün tamamlanması beklenen veya devam eden işlerin:\n"
                    rapor_metni += "-" * 40 + "\n"
                    for _, row in devam_edenler.iterrows():
                        rapor_metni += f"📌 İş: {row['Başlık']}\n👤 İsteyen: {row['İsteyen']}\n📅 Teslim: {row['Teslim_Tarihi']}\n📝 Not: {row['Notlar']}\n"
                        rapor_metni += "-" * 20 + "\n"
                    
                    eposta_gonder("Kösem - Günlük İş Raporu", rapor_metni)
            except:
                pass
            time.sleep(61) 
        time.sleep(30)

if 'bg_task' not in st.session_state:
    thread = threading.Thread(target=gunluk_kontrol, daemon=True)
    thread.start()
    st.session_state['bg_task'] = True

# --- TASARIM VE VERİ YÖNETİMİ ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%); }
    div[data-testid="stSidebarNav"] {display: none;}
    .stRadio > div { display: flex; flex-direction: column; gap: 12px; }
    .stRadio label {
        background: white; border: 1px solid #e0e0e0; padding: 15px 20px !important;
        border-radius: 12px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.3s ease; cursor: pointer; width: 100%;
    }
    .stRadio label[data-selected="true"] {
        background: linear-gradient(45deg, #4caf50, #2e7d32) !important;
        color: white !important; border: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

def verileri_yukle():
    try: return pd.read_csv("isler.csv", sep="|")
    except: return pd.DataFrame(columns=["ID", "Tarih", "Şirket", "Kategori", "Başlık", "İsteyen", "Teslim_Tarihi", "Notlar", "Durum"])

def veri_kaydet(df): df.to_csv("isler.csv", sep="|", index=False)

df = verileri_yukle()

# --- KENAR ÇUBUĞU ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌿 Kösem</h1>", unsafe_allow_html=True)
    secenek = st.radio("", ["🆕 Yeni İş Oluştur", "⏳ Devam Eden İşler", "✅ Biten İşler", "📧 Bildirim Testi", "📂 Arşiv"], label_visibility="collapsed")

# --- MANTIK ---
if secenek == "🆕 Yeni İş Oluştur":
    st.title("📝 Yeni İş Tanımla")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            kategori = st.selectbox("Kategori", ["Instagram", "Trendyol", "Medya", "Diğer"])
            sirket = "-"
            if kategori == "Medya":
                s_liste = st.multiselect("Şirketler", ["Pelteks Peluş", "Kolunsağ", "Yaje", "Secdem"])
                sirket = ", ".join(s_liste) if s_liste else "-"
            isteyen = st.text_input("İşi Kim İstedi?")
        with c2:
            baslik = st.text_input("İşin Başlığı / Müşteri")
            teslim = st.date_input("Hedef Teslim Tarihi")
        notlar = st.text_area("İş Detayları")
        if st.button("İşi Başlat"):
            if baslik and isteyen:
                yeni_id = int(time.time())
                yeni_is = {"ID": yeni_id, "Tarih": str(date.today()), "Şirket": sirket, "Kategori": kategori, "Başlık": baslik, "İsteyen": isteyen, "Teslim_Tarihi": str(teslim), "Notlar": notlar, "Durum": "Devam Ediyor"}
                df = pd.concat([df, pd.DataFrame([yeni_is])], ignore_index=True)
                veri_kaydet(df)
                st.toast("İş oluşturuldu!", icon="🚀")
            else: st.error("Eksik alanları doldurun.")

elif secenek == "📧 Bildirim Testi":
    st.title("📧 E-posta Test Paneli")
    if st.button("Şimdi Test E-postası Gönder"):
        with st.spinner("Gönderiliyor..."):
            basari = eposta_gonder("Kösem Sistem Testi", "Sistem başarıyla kuruldu, bildirimler aktif!")
            if basari: st.success(f"Harika! {GMAIL_ADRESI} adresine test mesajı gönderildi.")
            else: st.error("Gönderim başarısız. Lütfen internetini ve kodun doğruluğunu kontrol et.")

elif secenek == "⏳ Devam Eden İşler":
    st.title("🏃‍♂️ Devam Eden Süreçler")
    devam_isler = df[df["Durum"] == "Devam Ediyor"]
    if not devam_isler.empty:
        for idx, row in devam_isler.iterrows():
            with st.expander(f"📌 {row['Başlık']} (İsteyen: {row['İsteyen']})"):
                st.write(f"**Şirket:** {row['Şirket']} | **Teslim:** {row['Teslim_Tarihi']}")
                st.write(f"**Detay:** {row['Notlar']}")
                if st.button("✅ İş Bitti", key=f"b_{row['ID']}"):
                    df.loc[idx, "Durum"] = "Bitti"
                    veri_kaydet(df)
                    st.rerun()
    else: st.info("Devam eden iş yok.")

elif secenek == "✅ Biten İşler":
    st.title("🎉 Tamamlananlar")
    bitenler = df[df["Durum"] == "Bitti"]
    if not bitenler.empty:
        st.table(bitenler[["Tarih", "Şirket", "Başlık", "İsteyen"]])
    else: st.info("Henüz biten bir iş yok.")

elif secenek == "📂 Arşiv":
    st.title("📚 Genel Arşiv")
    st.dataframe(df, use_container_width=True)
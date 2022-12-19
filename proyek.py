import streamlit as st

# Custom Tab Title and Icon
from PIL import Image
image = Image.open('logo.png')
st.set_page_config(page_title="Gempa, po?",
                    page_icon=image)

# GEMPA
import tweepy
import config
import pandas as pd

# LOKASI
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim

# BERITA
import datetime as DT
from PIL import Image

# CUACA
import urllib.request, json

# Custom Sidebar
from streamlit_option_menu import option_menu


# Background

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://i.postimg.cc/gj4tgwF2/gempa-po-2-bg.jpg");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
add_bg_from_url()




# === GEMPA ===
st.image('logo.png', width=70)
st.title('Gempa, po?')

selected = option_menu(
            menu_title = None,
            options = ["Deteksi Gempa", "Berita Gempa", "Intensitas Gempa", "Tentang Website"],
            icons = ['activity', 'newspaper', 'bar-chart-line-fill', 'info-circle-fill'],
            menu_icon= 'menu-button-wide-fill',
            default_index = 0,
            orientation = 'horizontal'
        )

loc = get_geolocation()

lat = loc['coords']['latitude']
lon = loc['coords']['longitude']
latlon = f'{lat}, {lon}'
geolocator = Nominatim(user_agent="proyek.py")
locfull = geolocator.reverse(latlon)

loc3 = geolocator.geocode(locfull, addressdetails=True)
locdet = loc3.raw['address']
kec = locdet['municipality']
kab = locdet['county']

    # kab = 'Jayapura'
if selected == 'Deteksi Gempa':

    # === LOKASI ===
    

    st.subheader(f'Lokasi anda:')
    st.write(f'{locfull}')



    # Data Terbuka
    st.markdown("""---""")
    st.subheader('Sumber : Data Terbuka BMKG')
    with urllib.request.urlopen("https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json") as url:
        data = json.load(url)
        status = 'tidak'
        for gempa2 in data['Infogempa']['gempa']:
            if kab in gempa2['Dirasakan']:
                status = 'terjadi'
                st.subheader(f"Terjadi gempa yang dirasakan di wilayah {kab}.")
                st.info(f"{gempa2['Tanggal']}  |  {gempa2['Jam']}")
                st.write(f"Kedalaman: {gempa2['Kedalaman']}")
                st.write(f"Magnitudo: {gempa2['Magnitude']}")
                st.write(f"Pusat: {gempa2['Wilayah']}")

        if status == 'tidak':
            st.success(f'Tidak terjadi gempa yang dirasakan di wilayah {kab}.')




    # TWEET
    st.markdown("""---""")
    st.subheader('Sumber : Twitter BMKG (@infoBMKG)')

    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    result = client.search_recent_tweets(query=(f"from:infoBMKG {kab} #gempa -is:retweet"),
                                                                max_results=10,
                                                                sort_order='recency', 
                                                                tweet_fields=["created_at"])

    tw = []
    tgl = []


    if result.data != None:
        st.warning(f'Terjadi gempa di wilayah {kab} dalam 7 hari terakhir.')
        st.write('')

        for tweet in result.data:
            tw.append(tweet.text)
            tanggal = str(tweet.created_at).replace('T', ' | ')
            tanggal = tanggal.replace('+', ' UTC+')
            tgl.append(tanggal)

        df = pd.DataFrame(list(zip(tw, tgl)), columns = ["Tweet", "Waktu Tweet dikirim"])
                                
        # Menyembunyikan index
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        st.table(df)

    else:
        st.success(f'Tidak ada gempa yang terjadi di wilayah {kab} dalam 7 hari terakhir.')

        


# === BERITA ===
elif selected == 'Berita Gempa':
    st.markdown(f'### Berita tentang Gempa yang Terjadi di Indonesia')
    st.markdown(f'##### (dalam 7 hari terakhir)')

    today = DT.date.today()
    week_ago = today - DT.timedelta(days=7)

    with urllib.request.urlopen(f"https://newsapi.org/v2/everything?q=gempa%20AND%20BMKG&from={week_ago}&to={today}&apiKey=a195b2e8bcb94e0b9a5fe903139dab08") as url:
        data = json.load(url)
        if data['totalResults'] > 1:
            for article in data['articles']:
                st.markdown("""---""")
                st.subheader(article['title'])
                st.caption(f"Sumber : {article['source']['name']}")
                st.image(f"{article['urlToImage']}")
                st.write(article['description'])

                tanggal = article['publishedAt'].replace('T', ' | ')
                tanggal = tanggal.replace('Z', ' ')
                st.write(f"{tanggal} (UTC+00.00)")
                
                st.info(article['url'])
                st.write('')
        else:
            st.info('Tidak ada berita tentang gempa terkini')



elif selected == 'Intensitas Gempa':
    daerah = st.text_input('Masukkan nama Kabupaten/Kota', f'{kab}')
    st.subheader(f'Intensitas gempa dari daerah {daerah.capitalize()} :')
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

    result = client.search_recent_tweets(query=(f"from:infoBMKG #gempa {daerah} -is:retweet"),
                                                                max_results=100,
                                                                sort_order='recency', 
                                                                tweet_fields=["created_at"])
    if result.data != None:
        count = 0
        for tweet in result.data:
            count += 1
        
        st.info(f'Terjadi gempa di wilayah {daerah} sebanyak **{count} kali** dalam 7 hari terakhir.')
    else:
        st.success(f'Tidak ada gempa yang terjadi di wilayah {daerah} dalam 7 hari terakhir.')



else:
    st.subheader('Kita ada untuk Anda')
    st.write('Website ini dibuat untuk mendeteksi apakah terjadi gempa di sekitar Anda.')

    st.markdown("""---""")

    st.markdown(f'##### Cara Kerja Website')    
    st.write('''
            1. Website akan meminta lokasi pengguna
            2. Website mencocokan lokasi pengguna dengan tweet dan data BMKG
            3. Website menampilkan hasil ke pengguna
            ''')

    st.markdown("""---""")
    
    st.write('Website ini mengambil data dengan API Twitter, Data Terbuka BMKG, dan NewsAPI.org')

    st.markdown("""---""")

    st.info('Dibuat oleh Andi Hakim Al-Khawarizmi')
    st.info('Untuk memenuhi tugas akhir mata kuliah Praktik Aplikasi Web Semester 5')
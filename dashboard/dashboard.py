import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_question_1(df):
    quest_1 = df.groupby(["year", "month"]).agg(
        max =('TEMP','max'),
        min = ('TEMP','min'),
         mean = ('TEMP','mean')
    ).reset_index()
    quest_1['month_year'] = quest_1['month'].astype(str).str.zfill(2) + '-' + quest_1['year'].astype(str).str.zfill(2)
    return quest_1

def create_question_2(df):
    dongsi = df[(df["station"] == "Dongsi") & (df["year"] == 2014)]
    quest_2 = dongsi.groupby(["month","year"]).agg(
        max =('TEMP','max'),
        min = ('TEMP','min'),
     mean = ('TEMP','mean'),
    ).reset_index()
    quest_2['month_year'] = quest_2['month'].astype(str).str.zfill(2) + '-' + quest_2['year'].astype(str).str.zfill(2)
    quest_2['nama_bulan'] = pd.to_datetime(quest_2['month_year'])
    quest_2['nama_bulan'] = quest_2['nama_bulan'].dt.strftime('%B')
    return quest_2

def create_question_3(df):
    corr = df.select_dtypes("float64").corr()
    return corr

def create_question_4(df):
    cluster = df.groupby("station").agg({
        "PM2.5":'mean',
        "PM10" : 'mean',
        "SO2" : 'mean',
        "NO2" : 'mean',
        "CO" : 'mean',
        "O3" : 'mean',
    }).reset_index()
    cluster['rank_PM2.5'] = cluster['PM2.5'].rank(ascending=False)
    cluster['rank_PM10'] = cluster['PM10'].rank(ascending=False)
    cluster['rank_SO2'] = cluster['SO2'].rank(ascending=False)
    cluster['rank_NO2'] = cluster['NO2'].rank(ascending=False)
    cluster['rank_CO'] = cluster['CO'].rank(ascending=False)
    cluster['rank_O3'] = cluster['O3'].rank(ascending=True)
    cluster['sum_rank'] = cluster[['PM10','PM2.5','NO2','SO2','CO']].rank(ascending=False).sum(axis=1)
    cluster['sum_rank'] = cluster['sum_rank']+cluster['rank_O3']
    cluster['final_rank'] = cluster['sum_rank'].rank(ascending=True)
    cluster['final_rank'] = pd.to_numeric(cluster['final_rank'])
    for index,data in cluster.iterrows() :
        if   data['final_rank'] < 5 :
             cluster.at[index,'kluster'] = "Rendah"
        elif data['final_rank'] > 8 :
            cluster.at[index,'kluster'] = "Tinggi"
        else : 
            cluster.at[index,'kluster'] = "Menengah"
    return cluster

df_merged = pd.read_csv('df_merged.csv')
df_merged['month_year'] = df_merged['month'].astype(str).str.zfill(2) + '-' + df_merged['day'].astype(str).str.zfill(2) + '-' + df_merged['year'].astype(str).str.zfill(2)
df_merged['month_year'] = pd.to_datetime(df_merged['month_year'])

min_date = df_merged["month_year"].min()
max_date = df_merged["month_year"].max()

with st.sidebar:
    st.title("Laskar AI")
    st.subheader("Penugasan 1 : Analisis Data dengan Python")
    st.markdown("""
        Fathir Maula S  
        L-01  
        [www.linkedin.com/in/fathir-maula-s](https://www.linkedin.com/in/fathir-maula-s)
    """)
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df_merged[(df_merged["month_year"] >= str(start_date)) & 
                (df_merged["month_year"] <= str(end_date))]

quest_1 = create_question_1(main_df)
quest_2 = create_question_2(main_df)
quest_3 = create_question_3(main_df)
quest_4 = create_question_4(main_df)

st.header('Dashboard Analisis Data Air-Quality :sparkle:')

with st.container():
    st.subheader('Question 1: Kapan kondisi rata-rata suhu bulanan ke 12 station mencapai batas maksimum dan minimum dalam kurun 2013-2017 ?')
    
    col1, col2 = st.columns(2)
    
    with col1:
        jumlah_station = quest_4['station'].nunique()
        st.metric("Jumlah Station", value=jumlah_station)

    with col2:
        all_suhu = main_df['TEMP'].mean()
        suhu = "%.2f Celsius" % all_suhu
        st.metric("Rata-Rata Suhu Keseluruhan", value=suhu)

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
    
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    
    sns.barplot(x="month_year", y='max', data=quest_1.sort_values(by='max',ascending=False).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel("Rata-Rata Suhu")
    ax[0].set_xlabel("waktu")
    ax[0].set_title("Nilai Maksimum", loc="center", fontsize=15)
    ax[0].tick_params(axis ='y', labelsize=12)
    
    sns.barplot(x="month_year", y='min', data=quest_1.sort_values(by='min', ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel("Rata-Rata Suhu")
    ax[1].set_xlabel("waktu")
    ax[1].invert_yaxis()
    ax[1].invert_xaxis()
    ax[1].set_title("Nilai Minimum", loc="center", fontsize=15)
    ax[1].tick_params(axis='y', labelsize=12)
    
    plt.suptitle("Nilai Maksimum dan Minimum Rata-Rata Suhu Bulanan (12 Station di RRT)", fontsize=20)

    st.pyplot(fig)

st.subheader('')

with st.container():
    st.subheader('Question 2: Bagaimana perkembangan suhu bulanan di wilayah Dongsi pada bulan tahun 2014 ?')

    fig = plt.figure(figsize=(10, 5)) 

    plt.plot(quest_2['nama_bulan'], quest_2['mean'], marker='o', linewidth=2, color="#72BCD4") 
    plt.title("Perkembangan Rata-rata Suhu Bulanan di Station Dongsi (2014)", loc="center", fontsize=14) 
    plt.xticks(fontsize=10,rotation=45) 
    plt.yticks(fontsize=10)

    st.pyplot(fig)
    st.text("Perkembangan suhu di station dongsi pada tahun 2014 menunjukkan pola yang memiliki puncak suhu Maksimum pada pertengah tahun (Juli) dan suhu minimum pada akhir dan awal tahun (Desemeber dan Januari)")

st.subheader('')

with st.container():
    st.subheader('Question 3: Apakah ada hubungan antara suhu dan kadar O3, NO2, SO2 di udara?')

    col1, col2, col3 = st.columns(3)
    
    with col1:
        cor_temp_o3 = quest_3['TEMP']['O3']
        cor_temp_o3 = round(cor_temp_o3,2)
        st.metric("Korelasi Suhu dengan O3", value="Korelasi Suhu dengan O3")

    with col2:
        cor_temp_no2 = quest_3['TEMP']['NO2']
        cor_temp_no2 = round(cor_temp_no2,2)
        st.metric("Korelasi Suhu dengan NO2", value=cor_temp_no2)

    with col3:
        cor_temp_so2 = quest_3['TEMP']['SO2']
        cor_temp_so2 = round(cor_temp_so2,2)
        st.metric("Korelasi Suhu dengan SO2", value=cor_temp_so2)

    fig = plt.figure(figsize=(8, 6))
    sns.heatmap(quest_3, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1, cbar=True)
    plt.title('Matriks Korelasi Antar Variabel')
    plt.xticks(size=8)
    plt.yticks(size=8,rotation=360)
    plt.show()

    st.pyplot(fig)
    st.text("Suhu memiliki korelasi yang sedang dengan arah positif dengan O3, sedangkan Suhu dengan NO2 dan CO2 memiliki korelasi negatif yang cukup lemah")

st.subheader('')

with st.container():
    st.subheader('Analisis Lanjutan -  Clustering Station Berdasarkan POLUTAN?')

    st.text("""
        Untuk melakukan clustering, saya akan membaginya berdasarkan polutan seperti tabel dibawah, 
    adapun cara saya melakukannya:
            
    - Memberi peringkat wilayah untuk setiap polutan
    - Pemeringkatan secara ascending, dimana berdasarkan informasi di media polutan diatas 
    cenderung bersifat buruk. Kecuali untuk OZON (O3)
    - Hasil perangkingan dijumlahkan, dan di ranking secara descending untuk menentukan kluster
    - Stasion akan dibagi menjadi 3 kluster yakni Tinggi, Menengah, Rendah. Berdasarkan Jumlah peringkat
    - Disclaimer, perangkingan bersifat relatif hanya pada 12 stasion pada tabel

    """)


    high_pollutant = quest_4[quest_4['kluster'] == "Tinggi"]
    high_pollutant = high_pollutant['station']
    stations_as_string = ', '.join(high_pollutant.tolist())
    st.metric("Relative High Pollutant", value=stations_as_string)


    moderate_pollutant = quest_4[quest_4['kluster'] == "Menengah"]
    moderate_pollutant = moderate_pollutant['station']
    stations_as_string = ', '.join(moderate_pollutant.tolist())
    st.metric("Relative Moderate Pollutant", value=stations_as_string)

    low_pollutant = quest_4[quest_4['kluster'] == "Rendah"]
    low_pollutant = low_pollutant['station']
    stations_as_string = ', '.join(low_pollutant.tolist())
    st.metric("Relative Low Pollutant", value=stations_as_string)


    colors = ["#D32F2F", "#D32F2F", "#D32F2F", "#D32F2F", "#FFEB3B", "#FFEB3B", "#FFEB3B", "#FFEB3B", "#81C784", "#81C784", "#81C784", "#81C784"]

    fig = plt.figure(figsize=(10, 6))
    sns.barplot(x="sum_rank", y='station',orient='h' ,data=quest_4.sort_values(by='final_rank',ascending=False), palette=colors)
    plt.title("Klusterisasi Polutan di 13 Stasiun di RRT", loc="center", fontsize=15)
    plt.tick_params(axis ='y', labelsize=12)
    plt.legend(['Tinggi (Buruk)', 'Medium (Agak Buruk)', 'Rendah (Baik)'], loc='lower right')
    plt.show()

    st.pyplot(fig)
    st.text("**Dingling** merupakan wilayah paling banyak polutan di banding 11 station yang lain")

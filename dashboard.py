import streamlit as st
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
sns.set(style='dark')

#BUAT FUNGSI UTK MENGEMBALIKAN TOTAL JUMLAH PENDAPATAN PER HARI
#DATASET PAKE YG DAFTAR_ORDERAN_CLEAN.CSV
def create_daily_revenue_df(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    pendapatan_per_hari = pd.DataFrame(df.groupby(df
                      ['order_purchase_timestamp'].dt.to_period('D'))['payment_value'].sum()).reset_index()
    pendapatan_per_hari.rename(columns={'payment_value': 'income','order_purchase_timestamp':'day'}, inplace=True)
    return pendapatan_per_hari

#BUAT FUNGSI UTK MENGEMBALIKAN SIAPA TOP SPENDER DALAM JANGKA WAKTU TERTENTU
#DATASET PAKE YG TOP_SPENDER.CSV
def create_top_spender_df(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    df = df[
    (df['order_purchase_timestamp'] >= str(start_date)) & 
    (df['order_purchase_timestamp'] <= str(end_date))
    ]
    pelanggan_loyal = df.groupby((['customer_id'])).agg({'payment_value':'sum',
                                                               'order_id':'count'}).reset_index()
    #Tampilkan 5 top spender di aplikasi e-commerce
    pelanggan_loyal= pelanggan_loyal.rename(columns={'order_id':'order_count'})
    pelanggan_loyal=pelanggan_loyal.sort_values('payment_value', ascending=False)
    pelanggan_loyal = pelanggan_loyal.head()
    return pelanggan_loyal

#BUAT FUNGSI UTK MENGEMBALIKAN SIAPA PENJUAL YANG DAPAT PENDAPATAN TERBANYAK DALAM JANGKA WAKTU TERTENTU
#DATASET PAKE YG TOP_SELLER.CSV
def create_top_seller_df(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    df = df[
    (df['order_purchase_timestamp'] >= str(start_date)) & 
    (df['order_purchase_timestamp'] <= str(end_date))
    ]
    top_seller = df[['order_id','seller_id','payment_value']]
    besar_pendapatan = top_seller.groupby('seller_id').agg({'payment_value':'sum',
                                                       'order_id':'count'}).reset_index()
    #Ganti nama kolom order_id jadi order_count
    besar_pendapatan = besar_pendapatan.rename(columns={'order_id':'order_count','payment_value':'income'})
    besar_pendapatan = besar_pendapatan.sort_values(by='income', ascending=False)
    besar_pendapatan = besar_pendapatan.head()
    return besar_pendapatan

#FUNGSI UTK MENGHITUNG RATA-RATA RATING DARI PELANGGAN
def create_average_rating(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    rating_per_bulan = pd.DataFrame(df.groupby(df
                      ['order_purchase_timestamp'].dt.to_period('D'))['review_score'].mean()).reset_index()
    rating_per_bulan.rename(columns={'order_purchase_timestamp': 'day',
                                 'review_score':'average_rating'}, inplace=True)
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    return rating_per_bulan

#FUNGSI UTK MENGHITUNG BERAPA PERSEN PESANAN YANG SAMPAI TEPAT WAKTU
def percentage_on_time_late(df):
    df['order_purchase_timestamp']=df['order_purchase_timestamp'].astype('str')
    df['status_delivery'] = 0  
    for index,row in df.iterrows(): #loop per baris, dimana setiap loop menghasilkan index dan row object
        if row['order_estimated_delivery_date'] >= row['order_delivered_customer_date']:
            df.at[index, 'status_delivery'] = 1
        else:
            df.at[index, 'status_delivery'] = 0
    return df

#FUNGSI UNTUK MENGHITUNG PRODUK YANG PALING LAKU DAN TIDAK LAKU DALAM JANGKA WAKTU TERTENTU
def most_selled_products(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    #FILTER DISINI
    df = df[
    (df['order_purchase_timestamp'] >= str(start_date)) & 
    (df['order_purchase_timestamp'] <= str(end_date))
    ]
    #Hitung jumlah produk yang dibeli di setiap orderan dan kemudian jumlahkan lagi berdasarkan produknya
    jumlah_produk = df.groupby('product_category_name', as_index=False).sum('order_item_id')
    # Rename kolom supaya lebih mudah dipahami
    jumlah_produk.rename(columns={'product_category_name': 'kategori_produk', 'order_item_id': 'jumlah_terjual'}, inplace=True)
    #Tampilkan 5 kategori dengan jumlah penjualan produk terbanyak
    most_selled=jumlah_produk.sort_values(by='jumlah_terjual',ascending=False).head()
    return most_selled

def worst_selled_products(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    #FILTER OUTPUT
    df = df[
    (df['order_purchase_timestamp'] >= str(start_date)) & 
    (df['order_purchase_timestamp'] <= str(end_date))
    ]
    #Hitung jumlah produk yang dibeli di setiap orderan dan kemudian jumlahkan lagi berdasarkan produknya
    jumlah_produk = df.groupby('product_category_name', as_index=False).sum('order_item_id')
    # Rename kolom supaya lebih mudah dipahami
    jumlah_produk.rename(columns={'product_category_name': 'kategori_produk', 'order_item_id': 'jumlah_terjual'}, inplace=True)
    #Tampilkan 5 kategori dengan jumlah penjualan produk tersedikit
    worst_selled=jumlah_produk.sort_values(by='jumlah_terjual',ascending=True).head()
    return worst_selled

def geoloc(df):
    df['order_purchase_timestamp']=pd.to_datetime(df['order_purchase_timestamp'],errors='coerce')
    #FILTER OUTPUT
    df = df[
    (df['order_purchase_timestamp'] >= str(start_date)) & 
    (df['order_purchase_timestamp'] <= str(end_date))
    ]
    return df

#BACA DATA ORDER
orders=pd.read_csv('daftar_orderan_clean.csv')
#TGL UNTUK FILTER
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
min_date = orders["order_purchase_timestamp"].min()
max_date = orders["order_purchase_timestamp"].max()

#DEFAULT BUAT SAAT FORM LOAD
default_start_date = pd.to_datetime('2017-09-05').date()
default_end_date = pd.to_datetime('2017-09-15').date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png") #SESUAI CONTOH DI LAT DASHBOARD
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[default_start_date, default_end_date]
    )

#Baca Semua Data Satu Per Satu
selled_products = pd.read_csv('result_order.csv')
cust_map = pd.read_csv('datacustomer.csv')
user_rating = pd.read_csv('ratings.csv')
top_seller = pd.read_csv('seller_new.csv')
top_spender = pd.read_csv('cust_new.csv')
order_details = pd.read_csv('daftar_orderan_clean.csv') #BUAT HITUNG YG ONTIME/GAK SAMA PENDAPATAN

#PANGGIL FUNGSI DAN FILTERING DISINI!
daily_order_df = create_daily_revenue_df(order_details)
daily_order_df = daily_order_df[(daily_order_df['day'] >= str(start_date)) & 
                                  (daily_order_df['day'] <= str(end_date))]

percentage_on_time_late_df = percentage_on_time_late(order_details)
percentage_on_time_late_df = percentage_on_time_late_df[
    (percentage_on_time_late_df['order_purchase_timestamp'] >= str(start_date)) & 
    (percentage_on_time_late_df['order_purchase_timestamp'] <= str(end_date))
]

st.header('E-Commerce Report from '+ str(start_date)+' to '+str(end_date))
st.subheader('Daily Orders')
col1, col2,col3 = st.columns(3)

with col1:
    total_orders = percentage_on_time_late_df['status_delivery'].count()
    st.metric("Total orders", value=total_orders)
with col3:
    total_revenue = daily_order_df['income'].sum()
    st.metric("Total Revenue", value=f"R$ {total_revenue:.2f}") #atur 2 angka di belakang koma
with col2: #delivery on time
    total_on_time = (percentage_on_time_late_df['status_delivery'].sum())/(percentage_on_time_late_df['status_delivery'].count())*100
    st.metric("Percentage of On Time Delivery", value=f"{total_on_time:.2f}%")
    
# Buat grafik
daily_order_df['day'] = daily_order_df['day'].dt.to_timestamp()
daily_order_df['day'] = daily_order_df['day'].dt.strftime('%d-%m-%Y') 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_order_df["day"],
    daily_order_df["income"],
    marker='o', 
    linewidth=2,
    color="#FD6A02"
)
plt.xticks(rotation=45) #biar lebih readable
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#BACA DATA
best_selling_product_df = most_selled_products(selled_products)
worst_selling_product_df = worst_selled_products(selled_products)
st.subheader('Best and Worst Selling Product Category') 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors_worst = ["#ED2939", "#FA8072", "#FA8072", "#FA8072", "#FA8072"]
colors_best = ["#6A8F5F", "#A0B58A", "#A0B58A", "#A0B58A", "#A0B58A"]
sns.barplot(x="jumlah_terjual", y="kategori_produk", data=best_selling_product_df.head(5), palette=colors_best, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Selling Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="jumlah_terjual", y="kategori_produk", data=worst_selling_product_df.head(5), palette=colors_worst, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Selling Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

#TAMPILIN REVIEW CUSTOMER
st.subheader("Average Rating of Orders based on User's Order Experience")
average_rating = create_average_rating(user_rating)
average_rating = average_rating[
    (average_rating['day'] >= str(start_date)) & 
    (average_rating['day'] <= str(end_date))
]
#Buat Grafiknya
average_rating['day'] = average_rating['day'].dt.to_timestamp()
average_rating['day'] = average_rating['day'].dt.strftime('%d-%m-%Y') 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    average_rating["day"],
    average_rating["average_rating"],
    marker='o', 
    linewidth=2,
    color="#7E481C"
)
plt.xticks(rotation=45) #biar lebih readable
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#TAMPILIN SIAPA TOP SPENDER
pelanggan_loyal = create_top_spender_df(top_spender)
st.subheader("Highest Spending Customers by Payment Value")
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(24, 6))
colors = ["#B399D4", "#D2B0D0", "#D2B0D0", "#D2B0D0", "#D2B0D0"]
sns.barplot(x="payment_value", y="customer_id", data=pelanggan_loyal.sort_values
            ('payment_value', ascending=False).head(5), palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("Payment Value")
ax.tick_params(axis ='y', labelsize=12)
st.pyplot(fig)

#TAMPILIN SIAPA TOP SELLER
st.subheader("Sellers with Highest Revenue")
highest_rank_seller = create_top_seller_df(top_seller)
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(24, 6))
colors = ["#28A99E", "#81CDC6", "#81CDC6", "#81CDC6", "#81CDC6"]
sns.barplot(x="income", y="seller_id", data=highest_rank_seller.sort_values
            ('income', ascending=False).head(5), palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("Total Revenue")
ax.tick_params(axis ='y', labelsize=12)
st.pyplot(fig)

#PERSEBARAN LOKASI CUSTOMER
st.subheader("Distribution of Customer's City on Map")
geoloc_data = geoloc(cust_map)
#Ambil data gambar map dengan memanfaatkan library geopandas
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
brazil = world[world.name == 'Brazil'] #Ambil peta negara Brazil
#BERI BATASAN BUAT TIAP NEGARA BAGIAN >> AMBIL DATA DARI LUAR
brazil_state = gpd.read_file("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
geoloc = gpd.GeoDataFrame(
    geoloc_data,
    geometry=gpd.points_from_xy(geoloc_data['geolocation_lng'], geoloc_data['geolocation_lat'])
)
fig, ax = plt.subplots(figsize=(10, 10)) #Atur ukuran subplot
brazil.plot(ax=ax, color='#CAF0F8', edgecolor='black')  #PLOT PETA BRAZIL
brazil_state.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)  #PLOT UTK NEGARA BAGIAN >> BIAR ADA BOUNDARYNYA
geoloc.plot(ax=ax, color='#03045E', markersize=25, alpha=0.7, label='Cities')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend() #BUAT MUNCULIN KETERANGAN DI DLM PLOT
st.pyplot(fig)
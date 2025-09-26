# 🌤️ Weather Dashboard App

## 1. Deskripsi Singkat Program
Program ini adalah aplikasi **web sederhana untuk menampilkan informasi cuaca dan kualitas udara**. Pengguna dapat memasukkan nama kota, dan aplikasi akan menampilkan:  

- Cuaca saat ini (suhu, kelembaban, kecepatan angin, kondisi awan)  
- Polusi udara / Air Quality Index (AQI) dan PM2.5/PM10  
- Ramalan cuaca per jam (hourly forecast) dalam bentuk grafik  
- Ramalan cuaca harian (daily forecast) selama 5 hari  

Aplikasi ini dibuat menggunakan **Python Flask** dengan tampilan berbasis HTML + Chart.js.

---

## 2. Deskripsi Singkat API yang Digunakan

Program ini menggunakan **OpenWeatherMap API** (gratis, membutuhkan API key):

| API Endpoint        | Fungsi                                              | Syarat Penggunaan                                      |
|---------------------|-----------------------------------------------------|--------------------------------------------------------|
| `/weather`          | Mendapatkan cuaca saat ini untuk kota tertentu      | Membutuhkan `q` (nama kota) dan `appid` (API key)      |
| `/forecast`         | Mendapatkan 5-day forecast per 3 jam                | Membutuhkan `q`, `appid`, dan `units` (metric/imperial)|
| `/air_pollution`    | Mendapatkan indeks kualitas udara (AQI) dan polusi  | Membutuhkan `lat`, `lon`, dan `appid`                  |

> Catatan: Semua API memerlukan API Key yang valid. Penggunaan gratis memiliki limit 60 request/menit.

---

## 3. Metode / Teknik API Call Request

- Bahasa pemrograman: **Python 3**
- Framework: **Flask**
- Library: **requests** untuk melakukan HTTP request  

**Contoh request:**
```python
import requests

params = {"q": "Jakarta", "appid": API_KEY, "units": "metric"}
response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
data = response.json()
```

## **6. Cara Menjalankan Program**

1. Clone / Download project ke komputer.
2. Buat virtual environment (opsional tapi direkomendasikan):
      ```
         python -m venv venv
      ```
      ##Windows
      ```
         venv\Scripts\activate
      ```
      ## Mac/Linux
      ```
      source venv/bin/activate
      ```
4. Install dependencies:
      ```
         pip install flask requests
      ```
5. Jalankan Flask App:
      ```
         python app.py
      ```
7. Buka browser dan akses:
      ```
         http://127.0.0.1:5000/
      ```

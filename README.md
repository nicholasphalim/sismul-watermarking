# Evaluasi Kinerja Watermarking pada Foto Wajah menggunakan Kompresi JPEG (Manual DCT)

Nama: Nicholas Putra Halim  
NIM: 18224098  
Mata Kuliah: II2240 Sistem Multimedia  
Tanggal: 19 Mei 2026  

## 1. Tujuan Tugas
Tugas ini bertujuan untuk menyisipkan watermark pada foto wajah secara matematis, saya menggunakan metode Transformasi Kosinus Diskrit (DCT) 2D murni, ini tidak menggunakan library watermarking atau library pihak ketiga untuk kompresi dan pemrosesan DCT. Evaluasi kinerja dapat dilihat dari hasil ketahanan watermark terhadap berbagai level kompresi JPEG (Quality Factor / QF).

## 2. Langkah Kerja
Proses pemrosesan citra dilakukan secara sekuensial dengan langkah-langkah berikut:
<img width="1367" height="754" alt="image" src="https://github.com/user-attachments/assets/e879aa12-ec57-4633-be06-f474900e8d9a" />


- Konversi Ruang Warna (RGB ke YCbCr): Foto asli dipecah menjadi komponen Luminance (Y) dan Chrominance (Cb, Cr). Penyisipan watermark hanya dilakukan pada kanal Y karena mata manusia kurang sensitif terhadap variasi intensitas cahaya dibandingkan variasi warna.
- Pembuatan Watermark Biner: Pembuatan pola watermark visual (kotak putih di background hitam) berukuran proporsional dengan jumlah blok 8x8 pada foto aslinya (1 bit dialokasikan per blok 8x8).
- DCT 2D dan Penyisipan (Embedding): Matriks piksel dibagi menjadi blok-blok berukuran 8x8.
  - Setiap blok dikonversi ke ranah frekuensi menggunakan perkalian matriks DCT ortogonal.
  - Bit watermark disisipkan dengan memodifikasi dua koefisien frekuensi menengah (mid-frequency), yaitu pada indeks (4,3) dan (3,4), menggunakan relasi matematis dengan parameter delta=30.
  - Blok dikembalikan ke ranah spasial (IDCT).
- Simulasi Kompresi JPEG: Membuat matriks kuantisasi spesifik untuk Luminance dan Chrominance berdasarkan nilai tingkat-tingkat Quality Factor (QF).
  - Saluran Y, Cb, dan Cr diubah ke ranah DCT dan dikuantisasi dengan matriks tersebut, lalu didekuantisasi dan di-IDCT-kan kembali. Ini merepresentasikan proses hilangnya data (lossy compression).
- Ekstraksi dan Evaluasi: Ekstraksi dilakukan secara blind (tanpa menggunakan foto asli) dengan mengevaluasi relasi matematis kedua koefisien (4,3) dan (3,4) setelah kompresi. Kinerja watermarking dievaluasi berdasarkan persentase dari Bit Error Rate (BER).

## 3. Hasil dan Pembahasan
### A. Tabel Evaluasi Kinerja
Berikut adalah hasil ekstraksi watermark setelah foto dilakukan kompresi JPEG dengan 11 tingkat QF yang berbeda (diambil dari Terminal).

<img width="785" height="377" alt="image" src="https://github.com/user-attachments/assets/6e1839e2-db46-4910-8756-c653f01d3bcf" />  

Berdasarkan data kuantitatif di atas, watermark menunjukkan ketahanan tinggi pada rentang QF 100 hingga 70. Tingkat kegagalan ekstraksi (titik hancur) di mana Bit Error Rate merusak visualisasi watermark secara signifikan terjadi pada batas QF < 70.

### B. Visualisasi Dampak Kerusakan Kuantisasi
![Visualisasi Dampak Kerusakan Kuantisasi](Visualisasi_Interval_QF.png)

Analisis:
- QF 90: Matriks kuantisasi membagi dengan angka yang sangat kecil, resolusi warna masih tajam, dan koefisien yang menampung watermark tidak ada perubahan signifikan.
- QF 50: Foto mulai menunjukkan blocking artifacts ringan, dan hasil ekstraksi mulai menunjukkan titik-titik noise di watermarknya akibat pergeseran nilai koefisien.
- QF 10: Matriks kuantisasi membulatkan hampir seluruh komponen AC menjadi nol. Foto kehilangan detail warna yang parah, dan watermark sudah tidak bisa terlihat lagi.

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

# --- 1. MATRIKS DCT MANUAL ---
def generate_dct_matrix():
    A = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            if i == 0:
                A[i, j] = 1 / np.sqrt(8)
            else:
                A[i, j] = np.sqrt(2 / 8) * np.cos((2 * j + 1) * i * np.pi / 16)
    return A

def dct2_manual(block, A):
    return A @ block @ A.T

def idct2_manual(block, A):
    return A.T @ block @ A

# --- 2. LOGIKA EMBEDDING WATERMARK ---
def embed_bit(c1, c2, bit, delta=30):
    if bit == 1:
        if c1 <= c2 + delta:
            avg = (c1 + c2) / 2
            c1 = avg + delta / 2 + 1
            c2 = avg - delta / 2 - 1
    else:
        if c1 >= c2 - delta:
            avg = (c1 + c2) / 2
            c1 = avg - delta / 2 - 1
            c2 = avg + delta / 2 + 1
    return c1, c2

def extract_bit(c1, c2):
    return 1 if c1 > c2 else 0

# --- 3. SIMULASI KOMPRESI JPEG MANUAL LENGKAP ---
Q50_Y = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
])

Q50_C = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99]
])

def get_quantization_matrix(qf, is_luma=True):
    if qf <= 0: qf = 1
    if qf > 100: qf = 100
    if qf < 50: scale = 50 / qf
    else: scale = (100 - qf) / 50
    base_Q = Q50_Y if is_luma else Q50_C
    Q = np.floor(base_Q * scale + 0.5)
    Q[Q < 1] = 1
    return Q

def simulate_jpeg_compression_channel(channel, A, Q_matrix):
    h, w = channel.shape
    compressed = np.zeros_like(channel, dtype=float)
    for i in range(0, h - h%8, 8):
        for j in range(0, w - w%8, 8):
            block = channel[i:i+8, j:j+8] - 128
            dct_block = dct2_manual(block, A)
            q_block = np.round(dct_block / Q_matrix)
            dq_block = q_block * Q_matrix
            idct_block = idct2_manual(dq_block, A)
            compressed[i:i+8, j:j+8] = idct_block + 128
    return np.clip(compressed, 0, 255)

def ycbcr_to_rgb(Y, Cb, Cr):
    R = Y + 1.402 * (Cr - 128)
    G = Y - 0.34414 * (Cb - 128) - 0.71414 * (Cr - 128)
    B = Y + 1.772 * (Cb - 128)
    img_rgb = np.stack([R, G, B], axis=2)
    return np.clip(img_rgb, 0, 255).astype(np.uint8)

# --- 4. ALUR PROGRAM UTAMA ---
def main():
    file_path = "Foto diri.jpg"
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan di direktori aktif.")
        return

    print("Membaca citra asli...")
    img = np.array(Image.open(file_path).convert('RGB'), dtype=float)
    
    # Ekstraksi komponen YCbCr
    R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = -0.1687 * R - 0.3313 * G + 0.5 * B + 128
    Cr = 0.5 * R - 0.4187 * G - 0.0813 * B + 128

    A = generate_dct_matrix()
    h, w = Y.shape
    
    # Generate Watermark Visual Biner (Bentuk Kotak)
    wm_h, wm_w = h // 8, w // 8
    watermark_asli = np.zeros((wm_h, wm_w), dtype=int)
    pad_h, pad_w = wm_h // 4, wm_w // 4
    watermark_asli[pad_h:wm_h-pad_h, pad_w:wm_w-pad_w] = 1
    total_bits = wm_h * wm_w
    
    # EMBEDDING PADA KANAL LUMINANCE
    print("Menyisipkan watermark...")
    Y_watermarked = np.copy(Y)
    u1, v1, u2, v2 = 4, 3, 3, 4 
    
    for i in range(wm_h):
        for j in range(wm_w):
            row, col = i * 8, j * 8
            block = Y_watermarked[row:row+8, col:col+8] - 128
            dct_block = dct2_manual(block, A)
            
            dct_block[u1, v1], dct_block[u2, v2] = embed_bit(
                dct_block[u1, v1], dct_block[u2, v2], watermark_asli[i, j], delta=30
            )
            
            idct_block = idct2_manual(dct_block, A)
            Y_watermarked[row:row+8, col:col+8] = idct_block + 128

    img_watermarked_rgb = ycbcr_to_rgb(Y_watermarked, Cb, Cr)

    # =========================================================================
    # TAHAP 1: PRINT TABEL EVALUASI KINERJA KOTAK KERUSAKAN DI TERMINAL
    # =========================================================================
    print("\n" + "="*80)
    print(f"{'TABEL EVALUASI KINERJA WATERMARK':^80}")
    print("="*80)
    print(f"{'Quality Factor (QF)':<20} | {'Bit Error Rate (BER)':<22} | {'Status Kerusakan (Objektif)'}")
    print("-" * 80)
    
    qf_test_list = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5]

    for qf_test in qf_test_list:
        Q_Y = get_quantization_matrix(qf_test, is_luma=True)
        Q_C = get_quantization_matrix(qf_test, is_luma=False)

        Y_comp_test = simulate_jpeg_compression_channel(Y_watermarked, A, Q_Y)
        
        wm_ekstrak_test = np.zeros((wm_h, wm_w), dtype=int)
        for i in range(wm_h):
            for j in range(wm_w):
                row, col = i * 8, j * 8
                block = Y_comp_test[row:row+8, col:col+8] - 128
                dct_block = dct2_manual(block, A)
                wm_ekstrak_test[i, j] = extract_bit(dct_block[u1, v1], dct_block[u2, v2])
        
        error = np.sum(watermark_asli != wm_ekstrak_test)
        ber = (error / total_bits) * 100
        
        if ber == 0: status = "Utuh (Lossless / Tidak ada error)"
        elif ber <= 5: status = "Rusak Ringan (Pola kotak sangat jelas)"
        elif ber <= 15: status = "Rusak Sedang (Pola kotak masih dapat dikenali)"
        elif ber <= 30: status = "Rusak Berat (Banyak noise, pola kotak kabur)"
        else: status = "Hancur (Gagal diekstrak / Nilai acak)"
            
        print(f"{qf_test:<20} | {ber:>18.2f} % | {status}")
    print("="*80 + "\n")

    # =========================================================================
    # TAHAP 2: GENERATE PNG RINGKASAN TAHAPAN PROSES (QF = 40 DEMO)
    # =========================================================================
    print("Membuat Gambar 1: Ringkasan Tahapan Proses (QF=40)...")
    qf_demo = 40
    Q_Y_demo = get_quantization_matrix(qf_demo, is_luma=True)
    Q_C_demo = get_quantization_matrix(qf_demo, is_luma=False)
    
    Y_compressed_40 = simulate_jpeg_compression_channel(Y_watermarked, A, Q_Y_demo)
    Cb_compressed_40 = simulate_jpeg_compression_channel(Cb, A, Q_C_demo)
    Cr_compressed_40 = simulate_jpeg_compression_channel(Cr, A, Q_C_demo)
    img_compressed_rgb_40 = ycbcr_to_rgb(Y_compressed_40, Cb_compressed_40, Cr_compressed_40)
    
    watermark_ekstrak_40 = np.zeros((wm_h, wm_w), dtype=int)
    for i in range(wm_h):
        for j in range(wm_w):
            row, col = i * 8, j * 8
            block = Y_compressed_40[row:row+8, col:col+8] - 128
            dct_block = dct2_manual(block, A)
            watermark_ekstrak_40[i, j] = extract_bit(dct_block[u1, v1], dct_block[u2, v2])

    fig1, axes1 = plt.subplots(1, 5, figsize=(22, 5))
    axes1[0].imshow(img.astype(np.uint8)); axes1[0].set_title("1. Foto Asli", fontsize=12); axes1[0].axis('off')
    axes1[1].imshow(watermark_asli, cmap='gray'); axes1[1].set_title("2. Watermark Asli", fontsize=12); axes1[1].axis('off')
    axes1[2].imshow(img_watermarked_rgb); axes1[2].set_title("3. Hasil Watermark", fontsize=12); axes1[2].axis('off')
    axes1[3].imshow(img_compressed_rgb_40); axes1[3].set_title(f"4. Kompresi (QF={qf_demo})", fontsize=12); axes1[3].axis('off')
    axes1[4].imshow(watermark_ekstrak_40, cmap='gray'); axes1[4].set_title(f"5. Ekstrak (QF={qf_demo})", fontsize=12); axes1[4].axis('off')
    
    plt.tight_layout()
    plt.savefig("Ringkasan_Tahapan_Proses.png", dpi=300, bbox_inches='tight')
    plt.close()

    # =========================================================================
    # TAHAP 3: GENERATE PNG VISUALISASI INTERVAL MULTI-QF (90, 50, 10)
    # =========================================================================
    print("Membuat Gambar 2: Visualisasi Beberapa Tingkat Interval QF...")
    qf_visual_list = [90, 50, 10]
    num_qfs = len(qf_visual_list)
    
    fig2, axes2 = plt.subplots(num_qfs, 2, figsize=(12, 5 * num_qfs))

    for idx, qf_v in enumerate(qf_visual_list):
        Q_Y_v = get_quantization_matrix(qf_v, is_luma=True)
        Q_C_v = get_quantization_matrix(qf_v, is_luma=False)
        
        Y_comp_v = simulate_jpeg_compression_channel(Y_watermarked, A, Q_Y_v)
        Cb_comp_v = simulate_jpeg_compression_channel(Cb, A, Q_C_v)
        Cr_comp_v = simulate_jpeg_compression_channel(Cr, A, Q_C_v)
        img_comp_rgb_v = ycbcr_to_rgb(Y_comp_v, Cb_comp_v, Cr_comp_v)
        
        wm_ekstrak_v = np.zeros((wm_h, wm_w), dtype=int)
        for i in range(wm_h):
            for j in range(wm_w):
                row, col = i * 8, j * 8
                block = Y_comp_v[row:row+8, col:col+8] - 128
                dct_block = dct2_manual(block, A)
                wm_ekstrak_v[i, j] = extract_bit(dct_block[u1, v1], dct_block[u2, v2])

        err_v = np.sum(watermark_asli != wm_ekstrak_v)
        ber_v = (err_v / total_bits) * 100

        axes2[idx, 0].imshow(img_comp_rgb_v)
        axes2[idx, 0].set_title(f"Gambar Terkompresi (QF={qf_v})", fontsize=12)
        axes2[idx, 0].axis('off')
        
        axes2[idx, 1].imshow(wm_ekstrak_v, cmap='gray')
        axes2[idx, 1].set_title(f"Ekstraksi WM (QF={qf_v}, BER={ber_v:.1f}%)", fontsize=12)
        axes2[idx, 1].axis('off')

    plt.tight_layout()
    plt.savefig("Visualisasi_Interval_QF.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\n[SUKSES] Semua output berhasil dibuat!")
    print("- Lihat terminal untuk data tabel kuantitatif.")
    print("- Buka 'Ringkasan_Tahapan_Proses.png' untuk gambar alur sequensial.")
    print("- Buka 'Visualisasi_Interval_QF.png' untuk analisis multi-QF.")

if __name__ == "__main__":
    main()
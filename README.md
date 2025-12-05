# Algoritma-SMA---Kelompok-G---SOKA

## Anggota Kelompok
| No | Nama | NRP |
|----|-------|-------|
| 1  |   Wira Samudra S    |  5027231041     |
| 2  |  Farand Febriansyah     |  5027231084   |
| 3  |  Muhammad Syahmi A    |   5027231085    |
| 4  |  Veri Rahman    |   5027231088    |
| 5. |  Abid Ubaidillah A  |   5027231089    |

# Pengujian Algoritma Task Scheduler pada Server IT

Dokumentasi ini disusun untuk menjelaskan tahapan pengujian task scheduling pada lingkungan server IT melalui perbandingan empat algoritma penjadwalan, yaitu SMA, FCFS, RR, dan SHC. Pengujian dilakukan menggunakan tiga jenis dataset yang berbeda sebagai bagian dari pemenuhan tugas mata kuliah **Strategi Optimasi Komputasi Awan (SOKA).**

## Persiapan

1. Install `uv` sebagai dependency manager. Lihat [link berikut](https://docs.astral.sh/uv/getting-started/installation/)

2. Install semua requirement

```bash
uv sync
```

3. Buat file `.env` kemudian isi menggunakan variabel pada `.env.example`. Isi nilai setiap variabel sesuai kebutuhan

```conf
VM1_IP=""
VM2_IP=""
VM3_IP=""
VM4_IP=""

VM_PORT=5000
```

4. Kelompok kami menggunakan algortima ` Slime Mould Algorithm `

5. Untuk menjalankan server, jalankan docker

```bash
docker compose build --no-cache
docker compose up -d
```

6. Inisiasi Dataset untuk scheduler. Buat folder `Dataset` kemudian isi dengan 3 dataset yaitu, RandomSimple, RandomStratified, Low-High : 

```
Dataset/
│
├── RandomSimple.txt
├── RandomStratified.txt
└── Low-High.txt
```

7. Untuk menjalankan scheduler, jalankan file `scheduler.py`. **Jangan lupa menggunakan VPN / Wifi ITS**

```bash
uv run scheduler.py
```

8. Program ini akan menjalankan empat algoritma (SMA, SHC, FCFS, dan RR) pada tiga dataset. Setiap dataset dieksekusi sebanyak 10 kali untuk setiap algoritma, dan setiap run akan menghasilkan satu file output sesuai algoritma dan dataset yang digunakan. Output finalnya ialah rata" 10x run dari masing-masing algoritma pada setiap dataset.

# Uji Teknis (Technical Testing)

## Lingkup Pengujian

Pengujian dilakukan dengan tujuan untuk:

1. Mengukur performa empat algoritma penjadwalan:

  - Slime Mould Algorithm (SMA)
  
  - First-Come First-Served (FCFS)
  
  - Round Robin (RR)
  
  - Stochastic Hill Climbing (SHC)

2. Menjalankan semua algoritma terhadap 3 dataset berbeda, masing-masing sebanyak 10 kali run.

3. Mengirim task secara asynchronous ke empat VM simulasi server.

4. Mengumpulkan metrik performa untuk analisis akhir.

## Dataset Pengujian

Terdapat tiga dataset dalam folder Dataset/:
```
Dataset/
 ├── RandomSimple.txt
 ├── RandomStratified.txt
 └── Low-High.txt
```

Struktur dataset berisi daftar angka index task (misal: 1, 5, 7, 12, …).
Setiap task akan dikonversi ke CPU load menggunakan:

`cpu_load = index² × 10000`

## Lingkungan Eksekusi

Setiap task dijalankan pada empat VM simulasi, dengan spesifikasi:

|VM|	CPU Cores|	RAM	|Digunakan Untuk|
|---|---|---|---|
|vm1  |1 core	|1GB	|Beban rendah|
|vm2	|2 core	|2GB	|Beban ringan–sedang|
|vm3	|4 core	|4GB	|Beban menengah|
|vm4	|8 core	|4GB	|Beban berat|

IP setiap VM diambil dari file .env:
```
VM1_IP=...
VM2_IP=...
VM3_IP=...
VM4_IP=...
```

## Mekanisme Pengujian

1. Eksekusi Penjadwalan

Setiap dataset dijalankan sebanyak 10 kali run, dan pada setiap run semua algoritma dipanggil:
```
assignments = {
    "SMA": slime_mould_algorithm(tasks, vms, SMA_ITERATIONS),
    "FCFS": fcfs(tasks, vms),
    "RR": rr(tasks, vms),
    "SHC": shc(tasks, vms, calculate_estimated_makespan, iterations=500)
}
```

Pengaturan iterasi:

- SMA = 5000 iterasi (global metaheuristic)

- SHC = 500 iterasi (local search)

- FCFS & RR tidak memiliki iterasi karena bersifat deterministik

2️. Eksekusi Task ke VM

Setiap task dikirim ke VM menggunakan:

`http://<VM_IP>:5000/task/<index>`

Dengan concurrency dibatasi oleh CPU VM menggunakan `asyncio.Semaphore`.

Setiap task dicatat:

- VM yang digunakan

- Waktu mulai

- Waktu eksekusi

- Waktu selesai

- Waktu tunggu (waiting time)

3️. Penyimpanan Hasil (Per Run)

Setelah semua task selesai, hasil disimpan dalam file:

`Result/<ALGO>_<DATASET>_run<N>.csv`


Isi file mencakup:

- Execution time

- Waiting time

- Assigned VM

- Start/Finish time (distandarkan dari t=0)

## Perhitungan Metrik

Setelah satu run selesai, dihitung beberapa metrik performa:

|Metrik	| Penjelasan |
|---|---|
|Makespan	|Total waktu keseluruhan sampai semua task selesai|
|Avg. Execution Time	|Rata-rata waktu eksekusi task|
|Avg. Wait Time	|Waktu tunggu sebelum task diproses|
|Throughput	|Jumlah task yang diproses per detik|
|Imbalance	|Ketidakseimbangan beban antar VM|
|Resource Utilization|	Pemanfaatan CPU VM|

Perhitungan dilakukan melalui fungsi:

`compute_metrics()`

## Summary per Dataset

Setiap dataset memiliki summary hasil rata-rata dari 10 run:

`Result/Summary_<DatasetName>.csv`

Isi summary mencakup rata-rata:

- makespan

- throughput

- avg_exec

- avg_wait

- imbalance

- resource_util

Ini adalah output final yang digunakan untuk dianalisis.

## Alur Pengujian Final

Secara ringkas, uji teknis berjalan seperti berikut:

```
Untuk setiap Dataset (3 dataset):
    Untuk Run 1 sampai 10:
        Hitung penjadwalan memakai 4 algoritma
        Eksekusi task asynchronous ke VM
        Simpan hasil run ke CSV
        Hitung metrik peforma
    Hitung rata-rata 10 run → Save Summary
```

Total eksekusi:

3 Dataset × 10 run × 4 algoritma = 120 eksekusi algoritma

# Analisis Kinerja setiap Algoritma (SMA, SHC, RR, FCFS) pada setiap dataset

## RandomSimple

Tabel ringkasan hasil:

| Algoritma | Makespan | Avg Exec  | Avg Wait  | Throughput | Imbalance | Resource Util |
| --------- | -------- | --------- | --------- | ---------- | --------- | ------------- |
| **SMA**   | 200.6732 | 21.409871 | 32.786012 | 0.318219   | 1.289361  | 0.436343      |
| **FCFS**  | 587.9049 | 23.432418 | 90.169413 | 0.088969   | 1.090446  | 0.129924      |
| **RR**    | 625.3122 | 23.738800 | 93.270342 | 0.083850   | 1.414184  | 0.127911      |
| **SHC**   | 185.6592 | 18.502311 | 27.423579 | 0.322120   | 1.178459  | 0.372975      |

1. Makespan

SHC menghasilkan makespan terbaik (185.65), diikuti oleh SMA (200.67).
Sementara FCFS dan RR menunjukkan performa sangat buruk.

Interpretasi:

- SHC efektif dalam menemukan alokasi tugas yang lebih optimal dan cepat selesai.

- SMA juga menunjukkan performa sangat baik dan stabil.

- FCFS dan RR bekerja tanpa optimasi, menyebabkan antrean panjang dan waktu penyelesaian lebih lama.

Kesimpulan: SHC dan SMA adalah algoritma yang paling efisien untuk menyelesaikan seluruh tugas.

2. Average Execution Time

Nilai avg_exec relatif mirip untuk seluruh algoritma, namun:

- SHC memiliki waktu eksekusi rata-rata paling rendah (18.50)
→ menandakan pembagian beban kerja yang lebih optimal.

- SMA sedikit lebih tinggi (21.40) tetapi masih efisien.

Interpretasi:
Algoritma berbasis heuristik/optimasi (SMA & SHC) dapat mengurangi waktu eksekusi per tugas.

3. Average Waiting Time

Perbedaan paling signifikan terlihat pada metrik ini.

- SHC (27.42) dan SMA (32.79) jauh lebih kecil dibanding:

- FCFS (90.17) dan RR (93.27)

Interpretasi:

- SMA dan SHC mampu menekan waktu tunggu di antrean.

- FCFS dan RR gagal menangani distribusi beban, sehingga banyak tugas menunggu lama.

Kesimpulan:
SHC dan SMA memberikan pengalaman sistem yang jauh lebih responsif.

4. Throughput

Nilai tertinggi diperoleh oleh:

  1. SHC: 0.322120
  
  2. SMA: 0.318219

Sementara FCFS dan RR memiliki throughput sangat rendah (< 0.09).

Interpretasi:
SHC dan SMA mampu menyelesaikan lebih banyak tugas per satuan waktu, menunjukkan efisiensi tinggi.

5. Load Imbalance

Metrik imbalance yang lebih rendah lebih baik.

- SHC memiliki ketidakseimbangan terendah (1.178)

- SMA sedikit lebih tinggi (1.289)

- RR yang terburuk (1.414)

Interpretasi:
SHC mampu mendistribusikan tugas lebih merata pada server/VM, mengurangi bottleneck.

6. Resource Utilization

Nilai pemanfaatan sumber daya:

- SMA tertinggi: 0.436

- SHC kedua: 0.3729

- FCFS & RR sangat rendah: ~0.128

Interpretasi:

- SMA memaksimalkan penggunaan CPU/VM secara efisien.

- SHC juga baik, meski sedikit di bawah SMA.

- FCFS dan RR gagal memanfaatkan resource secara optimal.

### Kesimpulan

Pada dataset RandomSimple, algoritma SHC memberikan hasil terbaik dengan makespan, waktu eksekusi, dan waktu tunggu paling rendah, sedangkan SMA juga tampil baik dengan pemanfaatan sumber daya tertinggi. Sebaliknya, algoritma FCFS dan RR menunjukkan kinerja paling rendah dengan makespan tinggi dan pemanfaatan sumber daya yang kurang optimal. Hasil ini menunjukkan bahwa algoritma optimasi seperti SHC dan SMA lebih efektif dibandingkan algoritma tradisional.

## RandomStratified

## Low-High
Tabel ringkasan hasil:

| Algoritma | Makespan | Avg Exec  | Avg Wait  | Throughput | Imbalance | Resource Util |
| --------- | -------- | --------- | --------- | ---------- | --------- | ------------- |
| **SMA**   | 110.7594 | 19.296921 | 9.157610  |  0.348596  | 1.588728  | 0.429177      |
| **FCFS**  | 375.4764 | 20.624185 | 44.582877 |0.072266    | 0.986705  | 0.096842      |
| **RR**    | 405.4657 | 19.694585 | 48.769750 | 0.066220   | 1.039915  | 0.086015      |
| **SHC**   | 208.5062 | 21.426938 | 17.605345 | 0.168491   | 1.326200  | 0.230582      |

## Interpretasi Metrik Kinerja (Dataset Low-High)
### Makespan (Waktu Penyelesaian Total)
- SMA menghasilkan Makespan terbaik (110.76 detik).

- SHC berada di urutan kedua (208.51 detik).

- FCFS dan RR menunjukkan performa sangat buruk, mencapai lebih dari 375 detik.

## Interpretasi:

- Pada dataset Low-High (yang memiliki variasi beban tugas yang ekstrem), algoritma SMA terbukti sangat efektif dalam menyeimbangkan tugas. SMA mampu menemukan alokasi tugas yang paling efisien, jauh mengungguli SHC.

- Performa SHC, meskipun lebih baik dari FCFS/RR, menurun signifikan dibandingkan dengan Makespan SMA.

- FCFS dan RR, tanpa mekanisme optimasi, gagal total menangani beban tugas yang tidak seragam ini.

Average Execution Time (Waktu Eksekusi Rata-Rata)
Nilai `avg_exec` SMA adalah yang terendah (`19.29 detik`).

SHC memiliki waktu eksekusi rata-rata tertinggi (`21.42 detik`).

## Interpretasi:

Meskipun nilai `avg_exec` relatif mirip, perbedaan Makespan yang besar mengindikasikan bahwa SMA paling berhasil menempatkan tugas-tugas berat pada VM dengan core CPU yang sesuai.

Waktu eksekusi rata-rata yang lebih rendah pada SMA menandakan bahwa, rata-rata, tugas-tugas ditempatkan pada VM yang dapat menyelesaikannya lebih cepat.

Average Waiting Time (Waktu Tunggu Rata-Rata)
Perbedaan paling signifikan terlihat pada metrik ini.

- SMA (9.16 detik) memiliki waktu tunggu rata-rata jauh lebih kecil dibandingkan semua algoritma lain.

- SHC (17.61 detik) berada di urutan kedua.

- FCFS (44.58 detik) dan RR (48.77 detik) menghasilkan waktu tunggu yang sangat lama.

## Interpretasi:

Waktu tunggu yang sangat kecil pada SMA adalah penyebab utama Makespan yang unggul. Ini menunjukkan bahwa SMA mampu mengatasi kemacetan (bottleneck) dan mengurangi antrean tugas secara dramatis.

Algoritma FCFS dan RR gagal mendistribusikan tugas besar, memaksa tugas lain menunggu sangat lama.

Throughput (Laju Penyelesaian Tugas)
- SMA memperoleh nilai tertinggi (0.3486 tugas/detik).

- SHC berada di urutan kedua (0.1685 tugas/detik).

## Interpretasi:

Makespan yang sangat rendah pada SMA secara otomatis menghasilkan Throughput tertinggi. Ini menunjukkan bahwa SMA mampu menyelesaikan lebih dari dua kali lipat tugas per satuan waktu dibandingkan SHC di lingkungan Low-High ini.

Load Imbalance (Tingkat Ketidakseimbangan)
- FCFS memiliki ketidakseimbangan terendah (0.9867), diikuti oleh RR (1.0399).

- SHC memiliki Imbalance Degree 1.3262.

- SMA memiliki ketidakseimbangan tertinggi (1.5887).

## Interpretasi:

Ini adalah hasil yang kontra-intuitif namun penting: Load Imbalance yang tinggi tidak selalu berarti Makespan yang buruk.

- FCFS dan RR memiliki Imbalance Degree rendah karena tugas-tugas sangat besar terdistribusi secara serial. Namun, meskipun seimbang, mereka lambat (Makespan tinggi).

- SMA (Imbalance 1.5887) mampu mengorbankan keseimbangan sempurna untuk mencapai eksekusi paralel tercepat. Ini berarti SMA dengan cerdas membebani VM tercepat secara ekstrem untuk menampung sebagian besar beban tugas, sehingga Makespan total menjadi sangat rendah.


### Shutterstock
Resource Utilization (Pemanfaatan Sumber Daya)
- SMA tertinggi (0.4291).

- SHC kedua (0.2305).

## Interpretasi:

Sama seperti Makespan, SMA unggul dalam metrik efisiensi. SMA memaksimalkan penggunaan CPU/VM secara efisien karena Makespan yang sangat pendek menunjukkan bahwa sumber daya tidak terbuang untuk idle time yang lama.

Pemanfaatan rendah pada FCFS dan RR disebabkan oleh waktu idle yang sangat panjang pada VM lain ketika VM yang memegang tugas terberat sedang memprosesnya.

## Kesimpulan Akhir (Dataset Low-High)
Pada dataset Low-High (dengan beban tugas yang tidak seragam dan ekstrem), algoritma SMA memberikan hasil terbaik di hampir semua metrik kritis: Makespan, Waktu Tunggu, Throughput, dan Pemanfaatan Sumber Daya. Meskipun SMA memiliki Load Imbalance tertinggi, hal itu disebabkan oleh strategi yang efektif: mengoptimalkan Makespan dengan memfokuskan beban tugas ke sumber daya tercepat, alih-alih mengejar keseimbangan beban kerja yang sempurna.

Sebaliknya, FCFS dan RR menunjukkan kinerja yang sangat buruk, sementara SHC, meskipun lebih baik dari FCFS/RR, tidak dapat menandingi efisiensi dan kecepatan SMA dalam lingkungan Low-High ini.

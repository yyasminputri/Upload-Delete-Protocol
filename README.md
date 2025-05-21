# LAPORAN 
## TUGAS 3 - Implementasi Fitur Upload dan Delete pada File Server Protocol

1. Update Spesifikasi PROTOKOL.txt
```
FILE SERVER
TUJUAN: melayani client dalam request file server

ATURAN PROTOKOL:
- client harus mengirimkan request dalam bentuk string
- string harus dalam format
  REQUEST spasi PARAMETER
- PARAMETER dapat berkembang menjadi PARAMETER1 spasi PARAMETER2 dan seterusnya

REQUEST YANG DILAYANI:
- informasi umum:
  * Jika request tidak dikenali akan menghasilkan pesan
    - status: ERROR
    - data: request tidak dikenali
  * Semua result akan diberikan dalam bentuk JSON dan diakhiri
    dengan character ascii code #13#10#13#10 atau "\r\n\r\n"

LIST
* TUJUAN: untuk mendapatkan daftar seluruh file yang dilayani oleh file server
* PARAMETER: tidak ada
* RESULT:
- BERHASIL:
  - status: OK
  - data: list file
- GAGAL:
  - status: ERROR
  - data: pesan kesalahan

GET
* TUJUAN: untuk mendapatkan isi file dengan menyebutkan nama file dalam parameter
* PARAMETER:
  - PARAMETER1 : nama file
* RESULT:
- BERHASIL:
  - status: OK
  - data_namafile : nama file yang diminta
  - data_file : isi file yang diminta (dalam bentuk base64)
- GAGAL:
  - status: ERROR
  - data: pesan kesalahan
  
UPLOAD
* TUJUAN: untuk mengunggah file ke file server
* PARAMETER:
  - PARAMETER1 : nama file
  - PARAMETER2 : isi file dalam format base64
* RESULT:
- BERHASIL:
  - status: OK
  - data: <nama file> uploaded successfully
- GAGAL:
  - status: ERROR
  - data: pesan kesalahan

DELETE
* TUJUAN: untuk menghapus file dari file server
* PARAMETER:
  - PARAMETER1 : nama file
* RESULT:
- BERHASIL:
  - status: OK
  - data: <nama file> deleted successfully
- GAGAL:
  - status: ERROR
  - data: pesan kesalahan
```

Dua perintah baru ditambahkan ke dalam protokol, yaitu UPLOAD dan DELETE. Perintah UPLOAD memungkinkan client untuk mengirimkan file ke server dengan isi file yang sudah di-encode dalam format base64. Hal ini dilakukan agar data tetap aman dan tidak rusak selama pengiriman melalui protokol berbasis teks. Perintah DELETE memberikan kemampuan bagi client untuk menghapus file yang sudah tidak diperlukan di server. Kedua perintah ini menjadikan sistem file server lebih lengkap dan mendekati fungsi dasar cloud storage sederhana.

2. Penjelasan Modifikasi Client dan Server
- Modifikasi pada Server
Penambahan dilakukan pada file file_interface.py:
```
def upload(self, params=[]):
    try:
        filename = params[0]
        filecontent = params[1]
        # Tambah padding base64 jika kurang
        missing_padding = len(filecontent) % 4
        if missing_padding != 0:
            filecontent += '=' * (4 - missing_padding)
        filecontent = base64.b64decode(filecontent)
        with open(filename, 'wb') as fp:
            fp.write(filecontent)
        return dict(status='OK', data=f"{filename} uploaded successfully")
    except Exception as e:
        return dict(status='ERROR', data=str(e))

def delete(self, params=[]):
    try:
        filename = params[0]
        os.remove(filename)
        return dict(status='OK', data=f"{filename} deleted successfully")
    except Exception as e:
        return dict(status='ERROR', data=str(e))
```

Fungsi upload() menerima parameter berupa nama file dan isi file yang sudah diencode base64. Isi file ini kemudian didecode kembali ke bentuk aslinya dan disimpan di direktori server. Fungsi delete() menerima nama file sebagai parameter dan langsung menghapus file tersebut dari server.

Di file file_protocol.py, bagian parsing perintah diubah agar mendukung perintah baru ini:
```
def proses_string(self, string_datamasuk=''):
    ...
    c = shlex.split(string_datamasuk)
    c_request = c[0].strip().lower()
    params = c[1:]
    cl = getattr(self.file, c_request)(params)
    return json.dumps(cl)
```

Pada sisi server, dua metode baru ditambahkan ke dalam kelas FileInterface upload() dan delete(). Fungsi upload() menerima nama file dan konten file dalam bentuk string base64, lalu mendekodenya dan menyimpannya ke direktori files/. Fungsi delete() menerima nama file dan langsung menghapusnya dari sistem file. Di sisi FileProtocol, perintah baru ini dikenali dari input string dan langsung diarahkan ke metode yang sesuai dalam FileInterface. Struktur JSON yang dikembalikan juga disesuaikan agar respons tetap konsisten.

- Modifikasi pada Client
Pada sisi client, file program diubah agar dapat menangani perintah UPLOAD dan DELETE. Client diberi kemampuan membaca isi file secara lokal, mengkonversinya menjadi base64, lalu mengirimnya dalam format yang sesuai dengan protokol. Berikut cuplikan kode client yang menangani perintah tersebut:
```
elif command.startswith("UPLOAD"):
    filename = input("Enter the filename to upload: ").strip()
    with open(filename, 'rb') as file:
        filecontent = base64.b64encode(file.read()).decode('utf-8')
    send_request(f"UPLOAD {filename} {filecontent}")


elif command.startswith("DELETE"):
    filename = input("Enter filename to delete: ").strip()
    send_request(f"DELETE {filename}")
```

Kode ini memastikan client bisa melakukan encode base64 sebelum mengirim ke server untuk operasi UPLOAD, dan cukup mengirim nama file saat melakukan DELETE. Client ditambahkan kemampuan menangani perintah UPLOAD dan DELETE. Untuk UPLOAD, client akan membaca isi file dari disk, meng-encode ke base64, lalu mengirimkan string UPLOAD <filename> <base64-content>. Untuk DELETE, cukup mengirimkan perintah DELETE <filename>. Dengan perintah ini, user dapat secara langsung mengelola file dari sisi client melalui terminal.

3. Penjelasan Modifikasi Client dan Server <br>
<img width="574" alt="Screenshot 2025-05-21 at 19 29 53" src="https://github.com/user-attachments/assets/6b311b49-c684-4278-859f-ab4ccb5dcf1e" /> <br>
Pada gambar ini, terlihat proses client melakukan upload file bernama test.txt. File berhasil dibaca dan diencode base64 lalu dikirim ke server. Server merespon dengan pesan konfirmasi bahwa file berhasil diunggah.
**Upload**: Pada saat operasi upload dilakukan, pengguna memasukkan perintah UPLOAD diikuti dengan nama file yang ingin diunggah. Program client kemudian membuka file tersebut, membacanya sebagai data biner, dan mengubahnya menjadi format base64. Setelah itu, perintah dikirim ke server dengan format UPLOAD <nama_file> <isi_file_base64>. Server menerima data ini, melakukan decoding base64 untuk mendapatkan data asli, kemudian menyimpannya ke dalam direktori file server. Server akan merespons dengan JSON yang menandakan status operasi, yaitu OK jika file berhasil disimpan, atau ERROR jika terjadi masalah. Proses ini memungkinkan transfer file biner dengan aman dan konsisten melalui protokol berbasis teks.


<img width="486" alt="Screenshot 2025-05-21 at 19 29 59" src="https://github.com/user-attachments/assets/16afc751-d60c-4c02-83e9-14e35b52d108" /> <br>
Gambar ini memperlihatkan client mengirimkan perintah delete untuk file test.txt. Server memproses permintaan dan menghapus file tersebut, kemudian mengirimkan respons sukses.
<br>
**Delete**: Operasi delete memungkinkan pengguna untuk menghapus file yang sudah tidak diperlukan di server. Pengguna cukup memasukkan perintah DELETE dan nama file yang ingin dihapus. Client mengirimkan perintah tersebut ke server, yang kemudian mencoba menghapus file tersebut dari sistem file lokalnya. Jika file berhasil dihapus, server akan mengirimkan respons dengan status OK, beserta pesan konfirmasi. Jika file tidak ditemukan atau terjadi error lain, server mengirimkan status ERROR beserta deskripsi kesalahan. Dengan begitu, pengguna dapat mengelola penyimpanan file secara lebih fleksibel dan efisien.

4. Kesimpulan Hasil 
Screenshot UPLOAD dan DELETE di atas membuktikan bahwa implementasi kedua fitur ini berjalan dengan baik. Client mampu mengirimkan file berukuran kecil hingga sedang dengan format base64, dan server dapat menyimpan serta menghapus file tersebut sesuai permintaan. Respon JSON yang diterima client konsisten dengan protokol yang ditentukan, sehingga client dapat memproses hasil operasi dengan mudah. Secara keseluruhan, modifikasi ini meningkatkan fungsi file server dari sekedar read-only menjadi read-write dengan fitur manajemen file yang lengkap.





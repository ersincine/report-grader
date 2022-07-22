Bu program öğrencilere ait PDF dosyalarını notlandırmaya yarar.

## 1) Yüklenen PDF raporlarını (ödev, sınav vb.) indir ve sıkıştırılmış dosyayı çıkart.

Her öğrencinin kendisine ait bir dizini ve o dizinin içinde raporu olmalı.
  
## 2) report_grader.py ve config.js dosyalarını rapor dizininin içine koy (yani öyle bir dizin olsun ki içinde bu 2 dosya ve öğrenci sayısı kadar dizin olsun) ve **config.js** dosyasını değiştir.
 - **prefix** ve **suffix**
	 - studentno_hw1.pdf için prefix="", suffix="_hw1" olur.
	 - ceng311_studentno_hw1.pdf için prefix="ceng311_", suffix="_hw1" olur.
	 - Büyük-küçük harf ayrımıyla ilgili bir hata varsa bu hata görmezden gelinecek.
- **command**
	- PDF açmak için terminal komutu. Ubuntu'da xdg-open komutunu kullanıyorum. Değiştirilebilir.
- **everyone**
	- Rapor yükleyen herkese verilecek puan. (Sırf yükleme yaptı diye puan verilmeyecekse 0.)
	- Puanlar tamsayı olmak zorunda değil.
- **minimum**
	- Bütün notlandırmalar bittikten sonra toplam bundan daha düşükse bu not verilir. (Mesela 0'dan daha düşük bir not alınması istenmiyorsa 0.)
	- minimum ile everyone farklı şeyler. grade = max((everyone + diğer notlandırmalar), minimum)
- **format**
	- Kişi PDF yüklemiş mi? (Yoksa DOCX falan mı yüklemiş?) İlk sayı PDF yüklediyse kazanacağı puan, ikinci sayı PDF yüklemediyse kaybedeceği puan.
	- 5 ve 0 olursa doğru yükleyenler 5 puan kazanır, 0 ve -5 olursa yanlış yükleyenler 5 puan kaybeder.
	- PDF haricinde (ekstra) dosya yüklendiyse bunlardan puan kırılmayacak ama bu dosyalar değerlendirilmeyecek.
	- Eğer hiç PDF yüklememiş veya 1'den fazla PDF yüklemiş öğrenciler var ise program çıktılarla sizi yönlendirecek.
- **naming**
	- Kişi PDF'in adlandırmasını doğru şekilde yapmış mı? Örneğin abc.pdf yerine def.pdf yüklendiyse isimlendirme yanlıştır. (evetse_kazanacağı_puan, hayırsa_kaybedeceği_puan)
	- Eğer PDF yüklenmediyse isimlendirme otomatik olarak yanlış sayılır. Örneğin abc.pdf yerine abc.docx yüklendiyse isimlendirme yanlış sayılır.
- **features**
	- Rapordan rapora değişen ve elle notlandırılacak kısım. Burası tamamen değiştirilir.
	- Birbiriyle alakalı olup da aynı anda değerlendirilmesi gereken özellikler varsa aynı grupta yazılır (Bir sorunun başlıkları gibi).
	- Örneğin bunun [[x, y], [z], [t]] olduğunu ve A, B, C, ... öğrencilerinin olduğunu düşünelim.
	- Notlandırma şu sırayla yapılır: Ax, Ay, Bx, By, Cx, Cy, ..., Az, Bz, Cz, ..., At, Bt, Ct, ... (Böylece daha adil bir notlandırma mümkün olur.)
	- Bir feature 4 şeyden oluşur: ["column name", "explanation (for yourself)", two_or_more_grading_options, explanations_for_grading_options]
	- two_or_more_grading_options ve explanations_for_grading_options eşit sayıda elemandan oluşmalıdır.
	
## 3) Bu programı çalıştır.
Eğer bir notu yanlış girersen daha sonra değiştirmek üzere bir yere not al. Programı kapatınca CSV dosyasında ilgili değişiklikleri yap.
- İstediğin anda programı sonlandırıp sonra tekrar kaldığın yerden devam edebilirsin.
- Program her tekrar çalıştırıldığında yeni bir CSV dosyası oluşturulur. En güncel dosya en büyük numaralı dosyadır.
- En son ortaya çıkan tablo öğrenci numaralarına göre sıralanmış şekildedir.

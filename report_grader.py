"""
1) Yüklenen raporları indir ve sıkıştırılmış dosyayı çıkart.

2) Bu dosyayı ve config.js dosyasını rapor dizininin içine koy ve config.js dosyasını değiştir.

prefix ve suffix
- studentno_hw1.pdf için prefix="", suffix="_hw1" olur.
- ceng311_studentno_hw1.pdf için prefix="ceng311_", suffix="_hw1" olur.
- Büyük-küçük harf ayrımıyla ilgili bir hata varsa bu hata görmezden gelinecek.

command
- PDF açmak için terminal komutu. Ubuntu'da bu programı kullanıyorum. Değiştirilebilir.

grading
- Puanlar tamsayı olmak zorunda değil.
- everyone
-- Rapor yükleyen herkese verilecek puan. (Böyle bir puan verilmeyecekse 0.)
- minimum
-- Bütün notlandırmalar bittikten sonra toplam bundan daha düşükse bu not verilir. (Mesela 0'dan daha düşük bir not alınmasın isteniyorsa 0.)
-- minimum ile everyone farklı şeyler. grade = max((everyone + diğer notlandırmalar), minimum)
- format
-- Kişi PDF yüklemiş mi? (Yoksa DOCX falan mı yüklemiş?) İlk sayı PDF yüklediyse kazanacağı puan, ikinci sayı PDF yüklemediyse kaybedeceği puan.
-- PDF haricinde (ekstra) dosya yüklendiyse bunlardan puan kırılmayacak ama bunlar değerlendirmeye de alınmayacak.
-- Eğer hiç PDF yüklememiş veya 1'den fazla PDF yüklemiş öğrenciler var ise program çıktılarla sizi yönlendirecek.
- naming
-- Kişi PDF'in adlandırmasını doğru şekilde yapmış mı? (evetse_kazanacağı_puan, hayırsa_kaybedeceği_puan)
-- Eğer PDF yüklenmediyse isimlendirme otomatik olarak yanlış sayılır.
- features
-- Rapordan rapora değişen asıl notlandırılacak kısım.
-- Burası tamamen değiştirilebilir.
-- Birbiriyle alakalı olup da aynı anda değerlendirilmesi gereken özellikler varsa aynı grupta yazılır (Bir sorunun başlıkları gibi).
-- Örneğin bunun [[x, y], [z], [t]] olduğunu ve A, B, C, ... öğrencilerinin olduğunu düşünelim.
-- Notlandırma şu sırayla yapılır:  Ax, Ay, Bx, By, Cx, Cy, ..., Az, Bz, Cz, ..., At, Bt, Ct, ... (Böylece daha adil bir notlandırma mümkün olur.)
-- Bir feature 4 şeyden oluşur: ["column name", "explanation (for yourself)", two_or_more_grading_options, explanations_for_grading_options]
-- two_or_more_grading_options ve explanations_for_grading_options eşit sayıda elemandan oluşmalıdır.

3) Bu programı çalıştır.
Eğer bir notu yanlış girersen daha sonra değiştirmek üzere bir yere not al. Programı kapatınca CSV dosyasında ilgili değişiklikleri yap.
(Birden fazla CSV dosyası varsa en son değişiklikler en büyük numaralı dosyada bulunur.)
İstediğin anda programı sonlandırıp sonra tekrar kaldığın yerden devam edebilirsin.
En son ortaya çıkan tablo öğrenci numaralarına göre sıralanmış şekildedir.
(Sınıf listesiyle birleştirmek olabildiğince kolay olur: Asıl listede yukarıdan aşağıya doğru giderken bazı satırlar (rapor yüklemeyenler) atlanır sadece.).

19.01.2022 Ersin Çine
"""

import os
import csv
import json


def okay(x):
    return GREEN + str(x) + DEFAULT


def warning(x):
    return YELLOW + str(x) + DEFAULT


def error(x):
    return RED + str(x) + DEFAULT


def check_submissions(submission_dirs):
    num_submissions = len(submission_dirs)
    print("Yüklenen rapor adedi:", num_submissions, "\n")
    return num_submissions


def check_report_formats(submission_dirs):
    # Herkes raporunu düzgün yükledi mi? (PDF dosyası var mı?)
    format_grades = []
    report_paths = []
    num_errors = 0
    for submission_dir in submission_dirs:
        pdf_report_paths = [submission_dir + "/" + submitted_file for submitted_file in os.listdir(submission_dir) if submitted_file.lower().endswith(".pdf")]
        if len(pdf_report_paths) == 1:
            # PDF dışında dosyalar varsa bunlardan puan kırılmayacak. Ama değerlendirmeye alınmayacaklar da.
            pdf_report_path = pdf_report_paths[0]
            report_paths.append(pdf_report_path)
            format_error = pdf_report_path.endswith("_converted.pdf")
        else:
            print(error(f"{submission_dir} dizininde {len(pdf_report_paths)} PDF var."))
            format_error = True
            num_errors += 1
        format_grade = -GRADING["format"]["penalty"] if format_error else GRADING["format"]["reward"]
        format_grades.append(format_grade)
    if num_errors > 0:
        print(error("Biçim problemi olan rapor adedi:"), num_errors, "\n")
        print("İlgili raporlar muhtemelen PDF yerine DOCX, DOC, TXT falan.")
        print("Bunları", error("studentno_converted.pdf"), "şeklinde PDF dosyalarına çevir.")
        exit()
    return report_paths, format_grades


def check_student_nos(submission_dirs):
    def is_valid_student_no(s):
        return len(s) == STUDENT_NO_LENGTH and s.isdigit()

    def get_student_no(pdf_report_name):
        pdf_report_name = pdf_report_name.lower()
        for penalized_end in ("_fixed.pdf", "_converted.pdf"):
            if pdf_report_name.endswith(penalized_end) and is_valid_student_no(pdf_report_name[:-len(penalized_end)]):
                student_no = pdf_report_name[:-len(penalized_end)]
                should_reward = False
                break
        else:
            if pdf_report_name.startswith(PREFIX) and pdf_report_name.endswith(SUFFIX + ".pdf") and is_valid_student_no(pdf_report_name[len(PREFIX):-len(SUFFIX + ".pdf")]):
                student_no = pdf_report_name[len(PREFIX):-len(SUFFIX + ".pdf")]
                should_reward = True
            else:
                student_no = None
                should_reward = False
        return student_no, should_reward

    student_nos = []
    naming_grades = []
    for submission_dir in submission_dirs:
        pdf_report_names = [submitted_file for submitted_file in os.listdir(submission_dir) if submitted_file.lower().endswith(".pdf")]
        assert len(pdf_report_names) == 1
        pdf_report_name = pdf_report_names[0]

        student_no, should_reward = get_student_no(pdf_report_name)
        naming_grade = GRADING["naming"]["reward"] if should_reward else -GRADING["naming"]["penalty"]
        if student_no is None:
            print(submission_dir, pdf_report_name)
            while True:
                student_no = input("What is the student no for the report above? ")
                if is_valid_student_no(student_no):
                    os.rename(submission_dir + "/" + pdf_report_name, submission_dir + "/" + student_no + "_fixed.pdf")
                    break

        if student_no in student_nos:
            print(error(student_no + " numaralı öğrenci zaten var!"))
            exit()
        student_nos.append(student_no)
        naming_grades.append(naming_grade)
    return student_nos, naming_grades


def load_table(csv_path):
    all_grades = {}
    with open(csv_path, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row_no, row in enumerate(reader):
            if row_no == 0:
                assert row == get_all_columns()  # Aksi halde aslında kod değişmiş. Eski CSV'den devam etmemek lazım.
            else:
                student_no = row[0]
                student_grades = row[1:]
                all_grades[student_no] = student_grades
    return all_grades


def get_all_columns():
    def calc_max_possible_grade():
        max_possible_grade = GRADING["everyone"] + GRADING["format"]["reward"] + GRADING["naming"]["reward"]
        for feature_group in GRADING["features"]:
            for feature in feature_group:
                max_possible_grade += max(feature[GRADE_OPTIONS_IDX])
        max_possible_grade = max(GRADING["minimum"], max_possible_grade)
        return max_possible_grade

    columns = ["student no", "everyone", "format", "naming"]
    for feature_group in GRADING["features"]:
        for feature in feature_group:
            column_name = feature[COLUMN_NAME_IDX]
            columns.append(column_name)
    columns.append("total")
    columns.append(f"grade (min possible: {GRADING['minimum']}, max possible: {calc_max_possible_grade()})")
    return columns


def save_table(csv_path, all_grades):
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(get_all_columns())
        for student_no, student_grades in all_grades.items():
            writer.writerow([student_no] + student_grades)


def get_option(question, options, explanations_for_options, other_options):
    print("-" * 100)
    print(question)
    for i, (option, explanation) in enumerate(zip(options, explanations_for_options)):
        print(okay("(" + chr(ord("1") + i) + ")"), option, warning(explanation))
    for message, _, _ in other_options:
        print(okay(message))
    while True:
        inp = input(f"Birini seçin: ").upper()
        for _, condition, function in other_options:
            if condition(inp):
                function(inp)
                break
        if len(inp) == 1 and "1" <= inp < chr(ord("1") + len(options)):
            option = options[ord(inp) - ord("1")]
            return option


def evaluate_report_for_feature_group(report_path, feature_group, student_grades):
    something_updated = False
    grades = []
    for student_grade, feature in zip(student_grades, feature_group):
        if student_grade == "?":
            command = f"{COMMAND} '{report_path}'"
            os.system(command)
            explanation = feature[1]
            grade_options = ["?"] + list(feature[GRADE_OPTIONS_IDX])
            explanations_for_options = ["Şimdilik atla"] + list(feature[GRADE_EXPLANATIONS_IDX])
            other_option = ("Raporu tekrar açmak için boş bırakın.",
                            lambda inp: inp == "",
                            lambda _: os.system(command))
            grade = get_option(explanation, grade_options, explanations_for_options, [other_option])
            something_updated = True
        else:
            grade = student_grade
        grades.append(grade)
    return grades, something_updated


def csv_stuff(student_nos, format_grades, naming_grades):
    if os.path.exists(ORIGINAL_CSV_PATH):
        csv_files = [ORIGINAL_CSV_PATH]
        i = 2
        while True:
            csv_files.append(ORIGINAL_CSV_PATH[:-len(".csv")] + f"_{i}.csv")
            if os.path.exists(csv_files[-1]):
                i += 1
            else:
                next_csv_file = csv_files[-1]
                del csv_files[-1]
                break
        print(csv_files[-1], "exists.")
        while True:
            inp = input(
                "Is this file still valid? (Valid if you did not change config.json after creating this CSV file.) (yes/no)\n"
                "yes ➜ This (latest) CSV file will be loaded.\n"
                "no ➜ All CSV files will be removed.\n")
            if inp in ("yes", "y", "no", "n"):
                is_load = inp in ("yes", "y")
                break
        if is_load:
            print("Latest CSV file will be loaded into memory.")
        else:
            print("CSV files will be removed.")
            for csv_file in csv_files:
                os.remove(csv_file)
    else:
        is_load = False

    if is_load:
        all_grades = load_table(csv_files[-1])
    else:
        # Hazır yüklenmeyecekse sıfırdan oluşturmak lazım.
        next_csv_file = ORIGINAL_CSV_PATH
        all_grades = {}
        for student_no, format_grade, naming_grade in zip(student_nos, format_grades, naming_grades):
            all_grades[student_no] = [GRADING["everyone"], format_grade, naming_grade]
            for feature_group in GRADING["features"]:
                for _ in feature_group:
                    all_grades[student_no].append("?")
            all_grades[student_no].append("?")   # total
            all_grades[student_no].append("?")   # grade

    return all_grades, next_csv_file


def main():
    submission_dirs = sorted([file for file in os.listdir() if os.path.isdir(file) and file != "venv" and not file.startswith(".")])  # PyCharm için sadece.
    num_students = check_submissions(submission_dirs)
    report_paths, format_grades = check_report_formats(submission_dirs)
    student_nos, naming_grades = check_student_nos(submission_dirs)
    assert num_students == len(report_paths) == len(format_grades) == len(student_nos) == len(naming_grades)
    assert len(set(student_nos)) == len(student_nos)  # Aynı numaradan 1 tane olması lazım.
    student_nos, report_paths, format_grades, naming_grades = zip(*sorted(zip(student_nos, report_paths, format_grades, naming_grades), key=lambda x: x[0]))

    all_grades, next_csv_file = csv_stuff(student_nos, format_grades, naming_grades)

    grades_start_index = 3  # everyone, format, naming
    for feature_group in GRADING["features"]:
        print()
        for index, (student_no, report_path) in enumerate(zip(student_nos, report_paths)):
            print("Student", index + 1, ":", student_no)
            grades, something_updated = evaluate_report_for_feature_group(report_path, feature_group, all_grades[student_no][grades_start_index:])
            all_grades[student_no][grades_start_index:grades_start_index + len(grades)] = grades
            if something_updated:
                save_table(next_csv_file, all_grades)
                print(okay("\nTablo kaydedildi.\n"))
        grades_start_index += len(feature_group)

    something_updated = False
    all_done = True
    for student_no in student_nos:
        if "?" in all_grades[student_no][:-2]:  # Son 2 sütun (total, grade) hariç ? var mı?
            all_done = False
        else:
            something_updated = True
            total = sum(map(float, all_grades[student_no][:-2]))
            grade = max(total, GRADING["minimum"])
            all_grades[student_no][-2] = str(total)
            all_grades[student_no][-1] = str(grade)

    if something_updated:
        print("-" * 100)
        print("Toplam notlar hesaplandı.")
        save_table(next_csv_file, all_grades)
        print(okay("\nTablo kaydedildi.\n"))

    print("-" * 100)
    if all_done:
        print(okay("Bitti! Geçmiş olsun."))
        # TODO: Notlara göre sıralayıp hepsini tekrar göster. (Düzeltme yapılacaksa yapılabilsin.)
    else:
        print(warning("Ama atlanan notlar var. Programı tekrar çalıştırın."))
    print("-" * 100)


if __name__ == "__main__":

    # paths
    CONFIG_PATH = "config.json"
    ORIGINAL_CSV_PATH = "grades.csv"

    # student no
    STUDENT_NO_LENGTH = 9  # Each student has a number with this many digits

    # colors
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DEFAULT = "\033[0m"

    # indices
    COLUMN_NAME_IDX = 0
    EXPLANATION_IDX = 1
    GRADE_OPTIONS_IDX = 2
    GRADE_EXPLANATIONS_IDX = 3

    if not os.path.exists(CONFIG_PATH):
        print(CONFIG_PATH, "dosyası bulunamadı.")
        exit()

    with open(CONFIG_PATH) as config_file:
        config = json.load(config_file)

    PREFIX = config["prefix"].lower()
    SUFFIX = config["suffix"].lower()
    COMMAND = config["command"]
    GRADING = config["grading"]

    assert GRADING["everyone"] >= 0
    assert GRADING["minimum"] >= 0
    assert GRADING["format"]["reward"] >= 0
    assert GRADING["format"]["penalty"] >= 0
    assert GRADING["naming"]["reward"] >= 0
    assert GRADING["naming"]["penalty"] >= 0
    for feature_group in GRADING["features"]:
        for feature in feature_group:
            assert len(feature[GRADE_OPTIONS_IDX]) == len(feature[GRADE_EXPLANATIONS_IDX])
            for grade_option in feature[GRADE_OPTIONS_IDX]:
                assert grade_option >= 0

    main()

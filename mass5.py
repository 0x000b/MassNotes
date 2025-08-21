#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

SouhailZamal = argparse.ArgumentParser()
SouhailZamal.add_argument('--userId','-u',type=str,required=True, help='Massar dyalak aflan/a ')
SouhailZamal.add_argument('--passwd','-p',type=str,required=True, help='bach baghi dkhol bsalam ?? tadir mot de pass hhhh')

args = SouhailZamal.parse_args()

login_url = "https://massarservice.men.gov.ma/moutamadris/Account"
session = requests.Session()
response = session.get(login_url)

if response.status_code != 200:
    print("Error: Couldn't fetch the login page.")
    exit()

# Extract CSRF token
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': '__RequestVerificationToken'})['value']

# Login data
login_data = {
    '__RequestVerificationToken': csrf_token,
    'UserName': args.userId,
    'Password': args.passwd
}

# Login
login_response = session.post(login_url, data=login_data)
if 'تسجيل الدخول' not in login_response.text:
    print("Login Successful ✅")

    # Arabic → French translation mapping
    translate_headers = {
        "المادة": "Matière",
        "الفرض الأول": "1er contrôle",
        "الفرض الثاني": "2ème contrôle",
        "الفرض الثالث": "3ème contrôle",
        "الفرض الرابع": "4ème contrôle",
        "الأنشطة المندمجة": "Activités intégrées"
    }

    translate_subjects = {
        "الاجتماعيات": "Sciences sociales",
        "التربية الأسرية": "Éducation familiale",
        "التربية الإسلامية": "Éducation islamique",
        "التربية البدنية": "Éducation physique",
        "الرياضيات": "Mathématiques",
        "الفيزياء والكيمياء": "Physique & Chimie",
        "اللغة العربية": "Arabe",
        "اللغة الفرنسية": "Français",
        "علوم الحياة والأرض": "Sciences de la vie et de la Terre"
    }

    # Loop for multiple requests without restarting program
    while True:
        year = input('l3am (année scolaire, ex: 2024) : ')
        dawra = input('dawra (session, ex: 1 ou 2) : ')

        res_url = 'https://massarservice.men.gov.ma/moutamadris/TuteurEleves/GetBulletins'
        res = {
            'Annee': year,
            'IdSession': dawra
        }

        # Get bulletins
        notes = session.post(res_url, data=res)
        notes.encoding = "utf-8"  # make sure Arabic is correct

        soup = BeautifulSoup(notes.text, 'html.parser')
        table = soup.find("div", id="tab_cc").find("table")

        if not table:
            print("⚠️ Impossible de trouver le tableau des notes.")
        else:
            headers = [translate_headers.get(th.get_text(strip=True), th.get_text(strip=True))
                       for th in table.find_all("th")]

            rows = []
            for tr in table.find("tbody").find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    cells[0] = translate_subjects.get(cells[0], cells[0])
                rows.append(cells)

            print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        # Ask if user wants to check another session
        again = input("\nVoulez-vous vérifier une autre session ? (o/n) : ").strip().lower()
        if again != "o":
            break

else:
    print("Login Failed ❌")


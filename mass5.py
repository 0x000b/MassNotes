#!/usr/bin/env python3 

import argparse
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

Args = argparse.ArgumentParser()
Args.add_argument('--userId','-u',type=str,required=True, help='Enter your UserName in the following Format: 123456789@taalim.ma')
Args.add_argument('--passwd','-p',type=str,required=True, help='Provide your Password')

args = Args.parse_args()

LoginUrl = "https://massarservice.men.gov.ma/moutamadris/Account"
session = requests.Session()
response = session.get(LoginUrl)

if response.status_code != 200:
    print("Error: Couldn't fetch the login page.")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
CsrfToken = soup.find('input', {'name': '__RequestVerificationToken'})['value']
CsrfToken
LoginData = {
    '__RequestVerificationToken': CsrfToken,
    'UserName': args.userId,
    'Password': args.passwd
}

LoginResponse = session.post(LoginUrl, data=LoginData)
if 'تسجيل الدخول' not in LoginResponse.text:
    print("Login Successful")

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

    while True:
        year = input('Please Enter which year you want to review')
        dawra = input('Please Enter which session you want to review ')

        ResUrl = 'https://massarservice.men.gov.ma/moutamadris/TuteurEleves/GetBulletins'
        res = {
            'Annee': year,
            'IdSession': dawra
        }

        
        notes = session.post(ResUrl, data=res)
        notes.encoding = "utf-8"  
        soup = BeautifulSoup(notes.text, 'html.parser')
        table = soup.find("div", id="tab_cc").find("table")

        if not table:
            print("Error: Enable to get table of notes")
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

        again = input("\n Do you want anotherr Session? (y/n) : ").strip().lower()
        if again != "y":
            break

else:
    print("Error: Login Failed")

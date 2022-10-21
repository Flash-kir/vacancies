import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


LANGUAGES = [
    'Python',
    'Java',
    'Javascript',
    'C#',
    'C',
    'Go',
    'Shell',
    'Scala',
    'Swift',
    'TypeScript',
    'Objective C'
    ]


def predict_rub_salary(salary_from, salary_to):
    salary = 0
    if isinstance(salary_from, int) & isinstance(salary_to, int):
        salary = (salary_from + salary_to) / 2
    elif isinstance(salary_from, int):
        salary = salary_from * 1.2
    elif isinstance(salary_to, int):
        salary = salary_to * 0.8
    else:
        return None
    return int(salary)


def predict_sj_rub_salary(vacancie):
    if not vacancie or vacancie['currency'] != 'rub':
        return None
    salary_from = vacancie['payment_from']
    salary_to = vacancie['payment_to']
    return predict_rub_salary(salary_from, salary_to)


def predict_hh_rub_salary(vacancie_salary):
    if not vacancie_salary or vacancie_salary['currency'] != 'RUR':
        return None
    salary_from = vacancie_salary['from']
    salary_to = vacancie_salary['to']
    return predict_rub_salary(salary_from, salary_to)


def get_sj_vacancies(sj_secret_key, language, page, town=4):
    params = {
        'page': page,
        'keyword': language,
        'town': town,
        'app_key': sj_secret_key
    }
    url = 'https://api.superjob.ru/2.0/vacancies/'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_hh_vacancies(text='', page=1, area='1'):
    params = {
        'text': text,
        'area': area,
        'page': page,
        'per_page': 100
    }
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_sj_vacancies_content(sj_secret_key, town=4):
    language_salaries = {}
    for language in LANGUAGES:
        salary_sum = 0
        vacancies_count = 0
        page = 0
        language_salaries[language] = {}
        more = True
        while more:
            vacancies = get_sj_vacancies(sj_secret_key, language, page, town)
            if 'objects' in vacancies.keys():
                for vacancie in vacancies['objects']:
                    salary = predict_sj_rub_salary(vacancie)
                    if isinstance(salary, int):
                        if salary > 0:
                            vacancies_count += 1
                        salary_sum += salary
            page += 1
            more = vacancies['more']
        language_salaries[language]['vacancies_found'] = vacancies['total']
        language_salaries[language]['vacancies_processed'] = vacancies_count
        if vacancies_count > 0:
            average_salary = int(salary_sum / vacancies_count)
        else:
            average_salary = 0
        language_salaries[language]['average_salary'] = average_salary
    return language_salaries


def get_hh_vacancies_content(area='1'):
    language_salaries = {}
    for language in LANGUAGES:
        salary_sum = 0
        vacancies_count = 0
        page = 0
        language_salaries[language] = {}
        last_page = False
        while not last_page:
            vacancies = get_hh_vacancies(language, page, area)
            if 'items' in vacancies.keys():
                for vacancie in vacancies['items']:
                    salary = predict_hh_rub_salary(vacancie['salary'])
                    if isinstance(salary, int):
                        vacancies_count += 1
                        salary_sum += salary
            page += 1
            last_page = page == vacancies['pages']
        language_salaries[language]['vacancies_found'] = vacancies['found']
        language_salaries[language]['vacancies_processed'] = vacancies_count
        if vacancies_count > 0:
            average_salary = int(salary_sum / vacancies_count)
        else:
            average_salary = 0
        language_salaries[language]['average_salary'] = average_salary
    return language_salaries


def print_vacancies_table(vacancies_content, title):
    table_salary = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for language in vacancies_content.keys():
        language_salaries = vacancies_content[language]
        table_salary.append(
            [
                language,
                language_salaries['vacancies_found'],
                language_salaries['vacancies_processed'],
                language_salaries['average_salary']
            ]
        )
    table = AsciiTable(table_salary, title)
    print(table.table)


if __name__ == '__main__':
    load_dotenv()
    sj_secret_key = os.environ.get('SUPERJOB_SECRET_KEY')
    print_vacancies_table(get_hh_vacancies_content(), 'HeadHunter Moscow')
    print_vacancies_table(
        get_sj_vacancies_content(sj_secret_key), 
        'SuperJob Moscow'
        )

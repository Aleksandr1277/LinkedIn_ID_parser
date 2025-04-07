import time
import csv
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def get_company_id_from_url(url):
    """
    Ищет в URL параметр вида currentCompany=%5B%22xxxxxx%22%5D и возвращает xxxxxx (айди компании).
    """
    match = re.search(r'currentCompany=%5B%22(\d+)%22%5D', url)
    if match:
        return match.group(1)
    return None

def human_delay(a=3, b=6):
    """Возвращает случайную задержку между a и b секундами."""
    time.sleep(random.uniform(a, b))

def main():
    # Файлы
    user_agent = "your_user_agent_here"  # Замените на ваш User-Agent
    input_file = './companies.txt'   # Файл со ссылками, по одной на строке
    output_file = './output.csv'       # Выходной CSV с результатами

    # Инициализация undetected-chromedriver
    options = uc.ChromeOptions()
    # Задаём пользовательский User-Agent (при необходимости)
    options.add_argument("user-agent={user_agent}")
    
    driver = uc.Chrome(options=options)

    # Переходим на страницу логина LinkedIn для авторизации
    driver.get("https://www.linkedin.com/login")
    print("Откройте браузер и выполните вход в LinkedIn. После успешного входа нажмите Enter в консоли.")
    input()  # Ждём ручного входа

    # Открываем CSV для записи результатов
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Company Name", "Company ID"])

        # Читаем ссылки из файла
        with open(input_file, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]

        for link in links:
            try:
                print(f"Обработка: {link}")
                driver.get(link)
                human_delay(4, 7)  # задержка для загрузки страницы
                
                # Сохраняем ссылку как "название" компании
                company_name = link

                # Ищем ссылку на раздел "employees"
                try:
                    # Ищем элемент по части текста "employee"
                    employees_link = driver.find_element(By.PARTIAL_LINK_TEXT, "employee")
                    employees_link.click()
                    human_delay(4, 7)  # ждем загрузки страницы сотрудников
                except Exception as e:
                    print("Не удалось найти/кликнуть по ссылке сотрудников:", e)
                    writer.writerow([company_name, "N/A"])
                    continue

                # Извлекаем текущий URL, где содержится параметр с айди компании
                employees_url = driver.current_url
                company_id = get_company_id_from_url(employees_url)
                if not company_id:
                    company_id = "N/A"
                print(f"Найдено: {company_name} - ID: {company_id}")

                writer.writerow([company_name, company_id])
                human_delay(2, 4)
            except Exception as e:
                print("Ошибка при обработке ссылки:", link, e)
                writer.writerow([link, "Ошибка"])
                continue

    driver.quit()
    print(f"Готово! Результаты сохранены в файле: {output_file}")

if __name__ == "__main__":
    main()

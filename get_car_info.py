import time
import psycopg2
import re

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from main import create_driver, print_message


def get_car_info(url):
    global car_id_external

    driver = create_driver()

    car_id_match = re.findall(r"\d+", url)
    car_id = car_id_match[0]
    car_id_external = car_id

    try:
        # solver = TwoCaptcha("89a8f41a0641f085c8ca6e861e0fa571")

        is_recaptcha_solved = True

        driver.get(url)
        time.sleep(3)

        # if "reCAPTCHA" in driver.page_source:
        #     is_recaptcha_solved = False
        #     print_message("Обнаружена reCAPTCHA, решаем...")

        #     sitekey = extract_sitekey(driver, url)
        #     print(f"Sitekey: {sitekey}")

        #     result = solver.recaptcha(sitekey, url)
        #     print(f'reCAPTCHA result: {result["code"][0:50]}...')

        #     is_recaptcha_solved = send_recaptcha_token(result["code"])

        if is_recaptcha_solved:
            # Достаём данные об авто после решения капчи
            car_date, car_price, car_engine_displacement, car_title = "", "", "", ""

            price_el = driver.find_element(By.CLASS_NAME, "DetailLeadCase_point__vdG4b")
            car_price = re.sub(r"\D", "", price_el.text)
            time.sleep(3)

            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '자세히')]")
                )
            )
            button.click()
            time.sleep(2)

            content = driver.find_element(
                By.CLASS_NAME,
                "BottomSheet-module_bottom_sheet__LeljN",
            )
            splitted_content = content.text.split("\n")
            car_engine_displacement = re.sub(r"\D", "", splitted_content[9])

            car_date = splitted_content[5]
            year = re.sub(r"\D", "", car_date.split(" ")[0])
            month = re.sub(r"\D", "", car_date.split(" ")[1])
            formatted_car_date = f"01{month}{year}"

            print_message(
                f"{car_id}\n{car_title}\nRegistration Date: {formatted_car_date}\nEngine Displacement: {car_engine_displacement}\nPrice: {car_price} KRW"
            )

            # Сохранение данных в базу
            conn = psycopg2.connect(DATABASE_URL, sslmode="require")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO car_info (car_id, date, engine_volume, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (car_id) DO NOTHING
                """,
                (car_id, formatted_car_date, car_engine_displacement, car_price),
            )
            conn.commit()
            cursor.close()
            conn.close()
            print("Автомобиль был сохранён в базе данных")

            new_url = f"https://plugin-back-versusm.amvera.io/car-ab-korea/{car_id}?price={car_price}&date={formatted_car_date}&volume={car_engine_displacement}"

            driver.quit()
            return [new_url, car_title]

    except WebDriverException as e:
        print(f"Ошибка Selenium: {e}")
        driver.quit()
        return ["", "Произошла ошибка получения данных..."]

    return ["", ""]

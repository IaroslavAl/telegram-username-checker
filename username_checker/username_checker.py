import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from names_dataset import NameDataset, NameWrapper
from transliterate import translit

# https://github.com/philipperemy/name-dataset

class TelegramGroupCreator:
    def __init__(self):
        self.driver = None
        self.cookies_file = "telegram_cookies.json"
        self.local_storage_file = "telegram_local_storage.json"

    def setup_driver(self):
        """Настройка веб-драйвера Chrome с профилем"""
        options = webdriver.ChromeOptions()

        # Указываем пользовательский профиль Chrome
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def save_session_data(self):
        """Сохранение cookies и localStorage для последующего использования"""
        # Сохраняем cookies
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

        # Сохраняем localStorage
        local_storage = self.driver.execute_script("return Object.assign({}, window.localStorage);")
        with open(self.local_storage_file, 'w') as f:
            json.dump(local_storage, f)

        print("Данные сессии сохранены")

    def load_session_data(self):
        """Загрузка сохраненной сессии"""
        try:
            # Загружаем cookies
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)

                self.driver.get("https://web.telegram.org/")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)

            # Загружаем localStorage
            if os.path.exists(self.local_storage_file):
                with open(self.local_storage_file, 'r') as f:
                    local_storage = json.load(f)

                self.driver.get("https://web.telegram.org/")
                for key, value in local_storage.items():
                    self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

            print("Данные сессии загружены")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке сессии: {e}")
            return False

    def is_logged_in(self):
        """Проверка, выполнен ли вход в аккаунт"""
        try:
            self.driver.get("https://web.telegram.org/")
            time.sleep(2)

            # Проверяем наличие элемента чатов (признак успешного входа)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chat-list')]"))
            )
            return True
        except:
            return False

    def wait_for_manual_login(self):
        """Ожидание ручной авторизации пользователя"""
        print("Пожалуйста, войдите в Telegram вручную в открывшемся окне браузера...")

        while not self.is_logged_in():
            time.sleep(5)  # Проверяем каждые 5 секунд
            print("Ожидание авторизации... (Закройте браузер или нажмите Ctrl+C для отмены)")

        print("Авторизация успешно выполнена!")

    def is_link_field_available(self):
        """Проверка, есть ли поле link"""
        try:
            # Проверяем наличие элемента чатов (признак успешного входа)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@class='form-control' and @type='text' and @aria-label='Link']")
                )
            )
            return True
        except:
            return False

    def wait_for_link_field(self):
        """Ожидание поля линк"""
        print("Пожалуйста, откройте поле link")

        while not self.is_link_field_available():
            time.sleep(5)  # Проверяем каждые 5 секунд
            print("Ожидание авторизации... (Закройте браузер или нажмите Ctrl+C для отмены)")

        print("Поле link доступно!")

    def check_names(self):
        try:
            # Отключаем неявные ожидания для ускорения
            self.driver.implicitly_wait(0)

            # Находим поле ввода один раз
            input_field = self.driver.find_element(
                By.XPATH, "//input[@class='form-control' and @aria-label='Link']"
            )

            # Получаем элемент статуса один раз
            status_locator = (By.XPATH, "//div[contains(@class, 'input-group')]//label")

            names = bot.get_names()

            # for name in names:
            for newName in common_words:
                # newName = translit(name, "ru", reversed=True).replace("'", "")
                # if len(newName) < 5:
                #     continue

                # Комбинированный JS-вызов (установка значения + событие)
                self.driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                """, input_field, f"https://t.me/{newName}")

                try:
                    # Ждём исчезновения "Checking..." (макс 1.5 сек)
                    WebDriverWait(self.driver, 1.5).until_not(
                        lambda d: "Checking..." in d.find_element(*status_locator).text
                    )

                    # Мгновенная проверка доступности
                    if "available" in self.driver.find_element(*status_locator).text:
                        print(f"✓ {newName}")
                    else:
                        print(f"✗ {newName}")

                except Exception:
                    print(f"↻ {newName} (таймаут)")

            return True

        except Exception as e:
            print(f"Ошибка: {str(e)[:100]}...")
            return False
        finally:
            # Восстанавливаем неявные ожидания
            self.driver.implicitly_wait(10)

    def get_names(self) -> list[str]:
        nd = NameDataset()
        result = nd.get_top_names(n=1000, gender='Male', country_alpha2='RU')
        names = result['RU']['M']
        return names

    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
            print("Браузер закрыт.")


if __name__ == "__main__":
    # Создание и запуск бота
    bot = TelegramGroupCreator()

    try:
        bot.setup_driver()

        if not bot.is_logged_in():
            bot.wait_for_manual_login()

        if not bot.is_link_field_available():
            bot.wait_for_link_field()

        bot.check_names()

        # Пауза перед закрытием
        input("Нажмите Enter для завершения...")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        bot.close()

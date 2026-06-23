import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

##############################################################
#                       CONFIGURACIÓN                        #
###############################################################

# 1. URL directa a la búsqueda ordenada por "Más recientes"
timestamp_actual = int(time.time())
URL_VINTED = f"https://www.vinted.es/catalog?search_text=slam+dunk+kanzenban&catalog[]=2312&order=newest_first&page=1&time={timestamp_actual}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_HISTORIAL = os.path.join(BASE_DIR, "historial.txt")

TOKEN_TELEGRAM = os.environ.get("TOKEN_TELEGRAM")
CHAT_ID = os.environ.get("CHAT_ID")


def cargar_historial():
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()


def guardar_en_historial(texto):
    with open(ARCHIVO_HISTORIAL, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


def enviar_telegram(mensaje, foto_url=None):
    if foto_url:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"

        payload = {"chat_id": CHAT_ID, "photo": foto_url, "caption": mensaje, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"

        payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML"}

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")


##############################################################
#                      Empieza el script                     #
##############################################################

def ejecutar_revision():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    browser = webdriver.Chrome(options=chrome_options)

    try:
        browser.get(URL_VINTED)

        # --- ACEPTAR COOKIES ---
        try:
            wait_cookie = WebDriverWait(browser, 5)
            boton_cookies = wait_cookie.until(EC.element_to_be_clickable((By.XPATH,
                                                                          "//div[contains(text(), 'Permitir todas las cookies')] | //button[@id='onetrust-accept-btn-handler']")))
            boton_cookies.click()
            time.sleep(1)
        except:
            pass  # Si no salen, seguimos

        # --- SCROLL MÚLTIPLE PARA CARGAR MÁS ARTÍCULOS ---
        # El número 4 indica cuántas veces va a bajar la página.
        num_scrolls = 4

        for i in range(num_scrolls):
            # Baja hasta el fondo de lo que hay cargado actualmente
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Esperamos 2.5 segundos para que Vinted procese y cargue los siguientes
            time.sleep(2.5)

        html = browser.page_source
        browser.quit()

        ref_doc = BeautifulSoup(html, 'html.parser')

        # 2. Búsqueda robusta: Buscamos elementos por data-testid (más estable)
        todos_los_posts = ref_doc.find_all('div', {'data-testid': lambda x: x and x.startswith('grid-item')})

        historial = cargar_historial()
        # 3. Las keywords DEBEN estar en minúscula para que el match funcione
        keywords = ["slam dunk", "kanzenban", "kanzeban", "slamdunk"]

        # Si el anuncio tiene alguna de estas palabras, el bot lo ignorará
        palabras_prohibidas = ["vf", "français", "francais", "frances", "italiano", "ita", "portugues", "kana", "panini", "française", "tome", "japonais", "jap" , "giapponese"]

        nuevos_encontrados = 0
        for post in todos_los_posts:
            # Intentamos extraer el enlace del producto
            enlace_tag = post.find('a', href=True)
            if not enlace_tag:
                continue

            enlace = enlace_tag['href']
            if not enlace.startswith('http'):
                enlace = "https://www.vinted.es" + enlace

            img_tag = post.find('img')
            foto_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

            texto_post = post.get_text(separator=" | ", strip=True)

            # 4. ID Único y fiable: Extraemos el ID numérico del artículo
            post_id = enlace.split('/')[-1].split('-')[0]

            if post_id not in historial:
                texto_lower = texto_post.lower()

                # Comprobamos si tiene las keywords de Slam Dunk
                if any(key in texto_lower for key in keywords):

                    # Comprobamos que NO tenga palabras en otro idioma
                    if not any(prohibida in texto_lower for prohibida in palabras_prohibidas):
                        mensaje = (
                            f" <b>¡Nueva oferta de Slam Dunk Kanzenban!</b>\n\n"
                            f" <i>Detalles:</i> {texto_post}\n\n"
                            f" <a href='{enlace}'>Ir al artículo</a>"
                        )
                        enviar_telegram(mensaje, foto_url)

                # Lo guardamos en el historial siempre
                guardar_en_historial(post_id)
                historial.add(post_id)
                nuevos_encontrados += 1

    except Exception as e:
        print(f"Error durante el scraping: {e}")
        if 'browser' in locals(): browser.quit()


def actualizar_historial_en_github():
    os.system('git config --global user.name "Requies"')
    os.system('git config --global user.email "jonrequies13@gmail.com"')
    os.system(f'git add "{ARCHIVO_HISTORIAL}"')
    os.system('git commit -m "Actualizar historial .txt" || exit 0')
    os.system('git push')


if __name__ == "__main__":
    ejecutar_revision()
    actualizar_historial_en_github()
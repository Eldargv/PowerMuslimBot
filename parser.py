import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
}
Quran = {}
all_chapters_url = "https://umma.ru/perevod-korana/"
browser = webdriver.Chrome(
    executable_path="C:\\Users\\drevn\\PycharmProjects\\PowerMuslimParser\\chromedriver\\chromedriver.exe"
)
wait = WebDriverWait(browser, 5)
action = ActionChains(browser)


def get_chapter(url):
    browser.get(url)
    while True:
        try:
            Load_More = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[1]/section/main/article/button"))
            )
            action.move_to_element(Load_More).click().perform()
            sp = BeautifulSoup(browser.page_source)
            ending = sp.find_all("div", class_="row quran-block")[-1].text
            print(ending)
            if str(ending).find("Священного Корана подошел к концу") != -1:
                break
        except Exception as Ec:
            print(Ec)
            break
    html_resources = browser.page_source
    soup = BeautifulSoup(html_resources, "lxml")
    # удаление всех сносок из Суры (которые открываются при нажатии)
    for explanation in soup.find_all("div", class_="explanation explanation--quran"):
        explanation.clear()
    # возвращает все блоки-аяты
    return soup.find_all("div", class_="row quran-block")


def get_verses(chapter):
    verses = {}
    for verse in chapter:
        num = verse.find("h3", class_="verse")
        txt = verse.find("div", class_="text")
        # удаление все ссылок на сноски (на которые нужно нажимать, чтобы показать сноски)
        for more in txt.find_all("a", class_="sdfootnoteanc"):
            more.clear()
        verses[num.text] = txt.text
    # возвращаются все аяты в виде словаря
    return verses


def get_chapters():
    r = requests.get(url=all_chapters_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    chapters = []
    number = -1
    for chap in soup.find("ol", class_="items-list").find_all("li"):
        if number <= 0:
            number += 1
            continue
        chapters.append(chap.find("a").get("href"))
    # возвращает сслыки на все суры в виде списка
    return chapters


def main():
    chapters = get_chapters()
    for i in range(len(chapters)):
        url = "https://umma.ru/" + chapters[i]
        verses = get_verses(get_chapter(url))
        Quran[i + 1] = verses
        with open("Quran2.json", "w", encoding='utf-8') as file:
            json.dump(Quran, file, indent=4, ensure_ascii=False)
    browser.close()
    browser.quit()


if __name__ == '__main__':
    main()

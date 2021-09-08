import requests
from bs4 import BeautifulSoup
from requests.api import request
from databaseConnector import create_server_connection
from time import sleep
import os


class MAL_Parser:
    def parse(self, page):
        characterList = []

        response = requests.get(f"https://myanimelist.net/character.php?limit={50 * (page-1)}")
        html = response.text
        parsed_html = BeautifulSoup(html, features="html.parser")
        ranking_list = parsed_html.body.find_all("tr", attrs={"class":"ranking-list"})
        for element in ranking_list:
            character = dict()
            character["rank"] = element.find_next("span").text                               # Rank
            try:
                character["name"] = element.find_next("a", attrs={"class":"fs14 fw-b"}).text     # Name
            except:
                continue

            try:
                character["japName"] = element.find_next("span", attrs={"class":"fs12 fn-grey6"}).text   # Japanese Name
            except:
                character["japName"] = ""

            character["charLink"] = element.find_next("a", attrs={"class":"fs14 fw-b"}).get("href")      # Character Page Link

            response = requests.get(character["charLink"])
            parsed_html = BeautifulSoup(response.text, features="html.parser")
            try:
                character["picLink"] = parsed_html.body.find_next("img", attrs={"class":"lazyload"}).get("data-src") # Image Link
            except:
                continue

            characterList.append(character)
            print(f"Waifu {character['name']}")
            sleep(4)

        return characterList            
        



connection = create_server_connection("10.100.0.32", "waifubot", os.environ.get("DB"))
cursor = connection.cursor()

parser = MAL_Parser()
upperBound = 4
characterList = []
for i in range(1, upperBound+1):
    characterList = parser.parse(i)
    print("[", end="")
    for j in range(i):
        print("■", end="")
    for j in range(upperBound-i):
        print(" ", end="")
    print("]")

    for c in characterList:
        query = "INSERT INTO Waifu (WaifuRank, WaifuName, JapaneseName, CharLink, PicLink) "
        query+=f"VALUES ({c['rank']},  '{c['name']}', '{c['japName']}', '{c['charLink']}', '{c['picLink']}');"
        #print(query)
        try:
            cursor.execute(query)
        except:
            continue

    connection.commit()


query = "SELECT * FROM Waifu;"
cursor.execute(query)
for element in cursor:
    print(element)
connection.commit()

cursor.close()
connection.close()

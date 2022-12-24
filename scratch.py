import bs4
import lxml
import requests

x = bs4.BeautifulSoup(
    requests.get("https://www.google.com").content, features="lxml"
).title.text.strip()
print(x)

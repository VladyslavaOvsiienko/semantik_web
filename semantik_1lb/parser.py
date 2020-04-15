import requests
from bs4 import BeautifulSoup
import re
import lxml

URL = "https://roll-club.kh.ua/tovar-category/nabory/"
HEADERS = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/80.0.3987.163 Safari/537.36",
           'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                     "application/signed-exchange;v=b3;q=0.9"}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    sets = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='product-wrap product-wrap-hasdesc')

    for item in items:
        raw_description = item.find('div', class_="product-description__content").get_text()
        raw_description = re.sub(r"[\n\xa0*]", "", raw_description)
        description = raw_description.split(":")

        raw_composition = description[1][:-19].split(",")
        composition = []
        for i in raw_composition:
            composition_el = []
            elements = i.split(' ')
            name = ' '.join(elements[:-2]).strip()
            count = ' '.join(elements[-2:]).strip()
            composition_el.append(name)
            composition_el.append(count)
            composition.append(composition_el)

        comments = item.find('span', class_="star-rating__count")
        if comments:
            comments = item.find('span', class_="star-rating__count").get_text()
        else:
            comments = 'None'

        rating = item.find('strong', class_="rating")
        if rating:
            rating = item.find('strong', class_="rating").get_text()
        else:
            rating = 'None'

        sets.append({
            'title': item.find('h3', class_="product-title").find('a').get_text(strip=True),
            'image': item.find("a", class_="product-image").find('img').get('data-src'),
            'composition': composition,
            'total-amount': description[2][:-3].strip(),
            'weight': description[3].strip(),
            'price': item.find('meta', itemprop='price').get('content') + ' грн.',
            'amount of comments': comments,
            'rating': rating
        })
    print(sets)
    return sets


def parser():
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        print("Data from current url was not parsed")


def create_xml(items):
    soup_xml = BeautifulSoup(features='xml')
    sets_tag = soup_xml.new_tag('sushi-sets', attrs={"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                                     "xsi:noNamespaceSchemaLocation": "./roll_club_sushi_sets.xsd"})
    for i in range(len(items)):
        set_tag = soup_xml.new_tag('sushi-set', attrs={'id': i})

        title_tag = soup_xml.new_tag('set-name')
        title_tag.string = items[i]['title']
        set_tag.append(title_tag)

        image_tag = soup_xml.new_tag('image')
        image_tag.string = items[i]['image']
        set_tag.append(image_tag)

        composition_tag = soup_xml.new_tag('ingredients')
        for item in items[i]['composition']:
            ingredient_tag = soup_xml.new_tag('ingredient')

            name_tag = soup_xml.new_tag('ingredient-name')
            name_tag.string = item[0]
            ingredient_tag.append(name_tag)

            amount_tag = soup_xml.new_tag('ingredient-amount')
            amount_tag.string = item[1]
            ingredient_tag.append(amount_tag)
            composition_tag.append(ingredient_tag)
        set_tag.append(composition_tag)

        total_tag = soup_xml.new_tag('total-amount')
        total_tag.string = items[i]['total-amount']
        set_tag.append(total_tag)

        weight_tag = soup_xml.new_tag('set-weight')
        weight_tag.string = items[i]['weight']
        set_tag.append(weight_tag)

        price_tag = soup_xml.new_tag('price')
        price_tag.string = items[i]['price']
        set_tag.append(price_tag)

        comment_tag = soup_xml.new_tag('comments-amount')
        comment_tag.string = items[i]['amount of comments']
        set_tag.append(comment_tag)

        rating_tag = soup_xml.new_tag('rating')
        rating_tag.string = items[i]['rating']
        set_tag.append(rating_tag)
        sets_tag.append(set_tag)
    soup_xml.append(sets_tag)

    with open("roll_club_sushi_sets.xml", "w") as file:
        file.write(soup_xml.prettify('utf-8').decode('utf-8'))


if __name__ == '__main__':
    sets = parser()
    create_xml(sets)

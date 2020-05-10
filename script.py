import requests
from pathlib import Path
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathvalidate import sanitize_filename
import os
from urllib.parse import urljoin
import json
import argparse
import re


def download_txt(url, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    if response.is_redirect:
        return False
    filename = sanitize_filename(filename)
    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return path


def download_image(url, filename, folder='images/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def get_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }
    response = requests.get(url, headers=headers, allow_redirects=False)
    response.raise_for_status()
    if response.status_code >= 300 and response.status_code <= 399:
        print(f'Found redirect {url}')
        return None
    return response.text


def get_book_title(soup):
    tag_h1 = soup.select_one('h1')
    title = tag_h1.text.split('::')[0] if tag_h1 else 'No title'
    return title.strip()


def get_book_author(soup):
    tag_h1 = soup.select_one('h1')
    author = tag_h1.text.split('::')[1] if tag_h1 else 'No Author'
    return author.strip()


def get_book_image_link(soup, url):
    tag_image = soup.select_one('.bookimage img')
    path_image = urljoin(url, tag_image['src'])
    return path_image


def get_book_comments(soup):
    comments_tags = soup.select('.texts .black')
    comments = []
    for comment in comments_tags:
        comments.append(comment.text)
    return comments


def get_book_genre(soup):
    tag_genre = soup.select_one('span.d_book').select('a')
    genres = []
    for genre in tag_genre:
        genres.append(genre.text)
    return genres


def get_book_id(soup):
    book_id = soup.select_one('input[name="bookid"]')['value']
    return book_id


def get_book_links(soup):
    books_cards = soup.select('.bookimage a')
    book_links = []
    for book_card in books_cards:
        link = urljoin('http://tululu.org/', book_card['href'])
        book_links.append(
            link
        )
    return book_links


def parse_links_from_pagination(category_id, start_page, max_page):
    book_links = []
    end_page = get_end_page(category_id)
    max_page = end_page if max_page > end_page else max_page
    try:
        for id in tqdm(range(start_page, max_page + 1)):
            content = get_content(f'http://tululu.org/l{category_id}/{id}/')
            if content:
                soup = BeautifulSoup(content, 'lxml')
                for link in get_book_links(soup):
                    book_links.append(link)
            time.sleep(0.5)
        return book_links
    except requests.exceptions.HTTPError as error:
        print(f'Can`t get data:\n{error}')


def get_all_categories():
    main_page = 'http://tululu.org/'
    category_links = []
    content = get_content(main_page)
    soup = BeautifulSoup(content, 'lxml')
    sections = soup.select('#leftnavmenu li a')
    for section in tqdm(sections):
        link = urljoin(main_page, section['href'])
        content = get_content(link)
        soup = BeautifulSoup(content, 'lxml')
        links = soup.select('a')
        for link in links:
            if link.has_attr('href'):
                # regex example: /l1/, /l55/, /l123/
                result = re.search(r'\/l(?P<id>\d+)\/$', link['href'])
                if result:
                    category_name = re.sub(r'(&.+;)|(•)', '', link.text).strip()
                    category_link = urljoin(main_page, link['href'])
                    category_id = result.group('id')
                    category_links.append({
                        'category_name': category_name.capitalize(),
                        'category_link': category_link,
                        'category_id': category_id
                    })
        time.sleep(0.5)
    categories_links = [dict(t) for t in {tuple(d.items()) for d in category_links}]
    with open('categories.json', 'w', encoding='utf-8') as file:
        json.dump(categories_links, file, ensure_ascii=False)
    print(f'Спарсил {len(categories_links)} категорий')


def show_categories():
    get_all_categories()
    with open('categories.json', 'r', encoding='utf-8') as file:
        categories = json.load(file)
    categories = sorted(categories, key=lambda d: d["category_name"])
    print('{:<35} {:<25} {:<5}'.format('Категория', 'Ссылка', 'ID'))
    for category in categories:
        print(
            '{:<35} {:<25} {:<5}'.format(category['category_name'], category['category_link'], category['category_id']))


def get_end_page(category_id):
    content = get_content(f'http://tululu.org/l{category_id}/')
    soup = BeautifulSoup(content, 'lxml')
    pagination = soup.select('a.npage')
    return int(pagination[-1].text) if pagination else 1


def init_argparse():
    parser = argparse.ArgumentParser(description='Скачивание книг с сайта http://tululu.org/')
    parser.add_argument('--start_page', type=int, default=1, help='Начальная страница.')
    parser.add_argument('--end_page', type=int, help='Конечная страница.')
    parser.add_argument('--category_id', type=int, default=55, help='Какую категорию хотим скачать. Указывать ID.')
    parser.add_argument('--show_categories', action='store_true', help='Показать список всех категорий.')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать картинки. По умолчанию False.',
                        default=False)
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать книги. По умолчанию False.',
                        default=False)
    return parser.parse_args()


def parse_books(args, book_links):
    library = []
    for book_link in tqdm(book_links):
        content = get_content(book_link)
        if content:
            soup = BeautifulSoup(content, 'lxml')
            title = get_book_title(soup)
            author = get_book_author(soup)
            image_link = get_book_image_link(soup, book_link)
            book_id = get_book_id(soup)
            book_path = 'Skip download' if args.skip_txt else download_txt(
                f'http://tululu.org/txt.php?id={book_id}', f'{title}.txt')
            if not book_path:
                continue
            image_path = 'Skip images' if args.skip_imgs else download_image(image_link, f'{book_id}.jpg')
            comments = get_book_comments(soup)
            genres = get_book_genre(soup)
            library.append({
                'book_id': book_id,
                'title': title,
                'author': author,
                'img_src': image_path,
                'book_path': book_path,
                'comments': comments,
                'genres': genres
            })
            time.sleep(0.5)
    with open('library.json', 'w', encoding='utf-8') as file:
        json.dump(library, file, ensure_ascii=False)
    for library_item in library:
        print('http://tululu.org/b{}/'.format(library_item['book_id']))


def main():
    args = init_argparse()
    if args.show_categories:
        show_categories()
        quit()
    try:
        start_page = args.start_page
        category_id = args.category_id
        end_page = args.end_page if args.end_page else get_end_page(category_id)
        if start_page > end_page:
            print('start_page не может быть больше end_page')
            quit()
        book_links = parse_links_from_pagination(category_id, start_page, end_page)
        print(f'Спарсил {len(book_links)} ссылок на книги. Приступаю к их граббингу.')
        parse_books(args, book_links)
    except requests.exceptions.HTTPError as error:
        print(f'Can`t get data:\n{error}')
    except KeyError as error:
        print(f'Catch key error:\n{error}')
    except requests.exceptions.ConnectionError as error:
        print(f'Connection error:\n{error}')


if __name__ == '__main__':
    main()

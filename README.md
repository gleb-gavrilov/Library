# Library

## Описание
Скрипт позволяет скачивать книги, изображения, комментарии с [бесплатной библиотеки](http://tululu.org/).

## Требования к окружению
Разработка велась на Python 3.7.3 + IDE PyCharm.

## Как установить
Скачайте и установите зависимости `requirements.txt`

`pip install -r requirements.txt`

## Примеры запуска
Скрипт можно запускать с аргументами:

    --start_page Начальная страница.
    --end_page Конечная страница.
    --category_id Какую категорию хотим скачать. Указывать ID.
    --update_categories Обновить список категорий с сайта.
    --show_categories Показать список всех категорий.
    --skip_imgs Не скачивать картинки. По умолчанию False.
    --skip_txt  Не скачивать книги. По умолчанию False.

Если запускать просто без аргументов:

`python script.py`
 
то по умолчанию будет скачиваться вся категория [научной фантастики](http://tululu.org/l55/).

Информация по книгам сохранится в файл `library.json`. Рядом со скриптом будут созданы папки `books` и `images` — 
где соответственно будут лежать тексты книг и изображения.

Чтобы вывести список всех категорий, их сначала надо скачать:

`python script.py --update_categories`

Теперь можно посмотреть список категорий:

`python script.py --show_categories`

Для парсинга определенной категории нужно передать её **ID**. Например, надо скачать категорию **Физика** ( у неё id 104 ):

`python script.py --category_id 104` - скачаются все книги с данной категории.

Если нам надо ограничить скачивание, то надо передать аргументы `--start_page` и `--end_page`. Например, категория **Политика**:

`python script.py --start_page 1 --end_page 10 --category_id 59` - скачаются книги с 1 по 10 страницу включительно.

Также можно ограничить скачивание изображений к книгам `--skip_imgs` или самих книг `--skip_txt`. Например:

`python script.py --start_page 1 --end_page 10 --category_id 59 --skip_imgs` - скачаются книги из раздела **Политика**
с 1 по 10 стр., но изображения к книгам не будет скачиваться.

`python script.py --start_page 1 --end_page 10 --category_id 59 --skip_txt` - скачается информация по книгам из раздела **Политика**
с 1 по 10 стр., но сами тексты книг скачиватся не будут.  


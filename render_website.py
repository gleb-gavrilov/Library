import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import math
from pathlib import Path


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    with open('library.json', encoding='utf-8') as file:
        library = json.load(file)
    books_on_page = 20
    total_pages = len(library) / books_on_page
    total_pages = math.ceil(total_pages)
    chunked_library = chunked(library, books_on_page)
    for num, library in enumerate(chunked_library):
        library = chunked(library, 2)
        rendered_page = template.render(library=library,
                                        total_pages=total_pages,
                                        current_page=num,
                                        next_page=num+1,
                                        prev_page=num-1)
        Path(f'pages').mkdir(parents=True, exist_ok=True)
        with open(f'pages/index{num}.html', 'w', encoding='utf-8') as file:
            file.write(rendered_page)



def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
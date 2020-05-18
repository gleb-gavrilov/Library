import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import math


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    with open('library.json', encoding='utf-8') as file:
        library = json.load(file)
    length = len(library) / 2
    length = math.ceil(length)
    library = chunked(library, length)
    rendered_page = template.render(library=library)
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
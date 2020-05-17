import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    with open('library.json', encoding='utf-8') as file:
        library = json.load(file)
    rendered_page = template.render(library=library)
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(rendered_page)



if __name__ == '__main__':
    main()
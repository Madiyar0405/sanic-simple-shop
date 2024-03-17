class Jinja:
    def __init__(self):
        from jinja2 import Environment, FileSystemLoader
        self.env = Environment(loader=FileSystemLoader('templates'))

    def get_template(self, path: str):
        template = self.env.get_template(path)
        return template


jinja = Jinja()

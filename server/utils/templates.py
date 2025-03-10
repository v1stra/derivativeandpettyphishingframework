from jinja2 import Environment, meta, DebugUndefined, BaseLoader

def get_template_variables(file_path: str) -> list:
    """ loads and parses template from file path and returns a list of variables """
    env = Environment()
    with open(file_path, 'r') as f:
        data = f.read()
    ast = env.parse(data)
    vars = meta.find_undeclared_variables(ast)
    return sorted(vars)

def check_unused_variables_from_file(file_path: str, kwargs) -> tuple[list, bool]:
    """ renders a template based on file path along with kwargs to determine if all variables have been defined """
    env = Environment(undefined=DebugUndefined)

    with open(file_path, 'r') as f:
        data = f.read()

    template = env.from_string(data)
    rendered = template.render(kwargs)
    ast = env.parse(rendered)
    vars = meta.find_undeclared_variables(ast)
    if len(vars) > 0:
        return sorted(vars), False
    return sorted(vars), True

import jinja2


def render(path, filename, context):
    """ Given jinja2 template, generate HTML
    Adapted from http://matthiaseisen.com/pp/patterns/p0198/

    Args:
        * filename - jinja2 template
        * context - dict of variables to pass in

    Returns:
        * rendered HTML from jinja2 templating engine
    """
    return (
        jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./"))
        .get_template(filename)
        .render(context)
    )

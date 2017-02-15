import markdown.util as util
import markdown.inlinepatterns
import re

class InternalLinkPattern(markdown.inlinepatterns.Pattern):
    """Return a link element from the given match.

    Only matches:
        - Markdown links using []() syntax.
        - Links that don't start with:
            - http:
            - https:
            - ftp:
            - ftps:
            - mailto:
            - news:
    """

    def __init__(self, ext, *args, **kwargs):
        self.ext = ext
        self.processor = 'internal-link'
        self.pattern = self.ext.processor_patterns[self.processor]['pattern']
        self.compiled_re = re.compile("^(.*?){}(.*)$".format(self.pattern),
            re.DOTALL | re.UNICODE)
        self.template = ext.jinja_templates[self.processor]

    def handleMatch(self, match):
        element = util.etree.Element("a")
        element.text = match.group('link_text')
        href = match.group('link_url')
        context = {'link_path': href}
        html_string = self.template.render(context)
        element.set("href", html_string)
        return element

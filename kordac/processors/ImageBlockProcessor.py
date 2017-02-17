from markdown.blockprocessors import BlockProcessor
import re
from kordac.processors.utils import parse_argument, centre_html
from markdown.util import etree
from kordac.processors.utils import check_required_parameters, check_optional_parameters
import jinja2

# NTS needs to include alt tags
class ImageBlockProcessor(BlockProcessor):

    def __init__(self, ext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = 'image'
        self.pattern = re.compile(ext.processor_patterns[self.processor]['pattern'])
        self.template = ext.jinja_templates[self.processor]
        self.relative_image_template = ext.jinja_templates['relative-image-link']
        self.required = ext.required_files['images']
        self.required_parameters = {'file_path'}
        self.optional_parameters = {'alt': set(), 'caption': set(), 'caption_link': {'caption'}, 'source': set(), 'alignment': set(), 'hover_text':{}}

    def test(self, parent, block):
        return self.pattern.search(block) is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)
        match = self.pattern.match(block)

        arguments = match.group('args')

        # check if internal or external image
        file_path = parse_argument('file-path', arguments)
        external_path_match = re.search(r'^http', file_path)
        if external_path_match is None: # internal image
            self.required.add(file_path)
            file_path = self.relative_image_template.render({'file_path': file_path})

        context = dict()
        context['file_path'] = file_path
        context['alt'] = parse_argument('alt', arguments)
        context['title'] =  parse_argument('title', arguments)
        context['caption'] = parse_argument('caption', arguments)
        context['caption_link'] = parse_argument('caption-link', arguments)
        context['source_link'] = parse_argument('source', arguments)
        context['alignment'] = parse_argument('alignment', arguments)
        context['hover_text'] =  parse_argument('hover-text', arguments)

        check_required_parameters(self.processor, self.required_parameters, context)
        check_optional_parameters(self.processor, self.optional_parameters, context)

        html_string = self.template.render(context)
        node = etree.fromstring(html_string)
        parent.append(node)

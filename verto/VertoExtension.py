from markdown.extensions import Extension
import markdown.util as utils

from verto.processors.CommentPreprocessor import CommentPreprocessor
from verto.processors.VideoBlockProcessor import VideoBlockProcessor
from verto.processors.ImageInlinePattern import ImageInlinePattern
from verto.processors.ImageTagBlockProcessor import ImageTagBlockProcessor
from verto.processors.ImageContainerBlockProcessor import ImageContainerBlockProcessor
from verto.processors.InteractiveBlockProcessor import InteractiveBlockProcessor
from verto.processors.RelativeLinkPattern import RelativeLinkPattern
from verto.processors.RemoveTitlePreprocessor import RemoveTitlePreprocessor
from verto.processors.SaveTitlePreprocessor import SaveTitlePreprocessor
from verto.processors.GlossaryLinkPattern import GlossaryLinkPattern
from verto.processors.ConditionalProcessor import ConditionalProcessor
from verto.processors.StylePreprocessor import StylePreprocessor
from verto.processors.RemovePostprocessor import RemovePostprocessor
from verto.processors.JinjaPostprocessor import JinjaPostprocessor
from verto.processors.HeadingBlockProcessor import HeadingBlockProcessor
from verto.processors.ScratchTreeprocessor import ScratchTreeprocessor
from verto.processors.ScratchInlineTreeprocessor import ScratchInlineTreeprocessor
from verto.processors.ScratchCompatibilityPreprocessor import ScratchCompatibilityPreprocessor
from verto.processors.ScratchCompatibilityPreprocessor import FENCED_BLOCK_RE_OVERRIDE
from verto.processors.GenericTagBlockProcessor import GenericTagBlockProcessor
from verto.processors.GenericContainerBlockProcessor import GenericContainerBlockProcessor
from verto.processors.PanelBlockProcessor import PanelBlockProcessor

from verto.utils.UniqueSlugify import UniqueSlugify
from verto.utils.HeadingNode import HeadingNode
from verto.utils.overrides import BLOCK_LEVEL_ELEMENTS, is_block_level
from verto.utils.overrides import OListProcessor
from verto.utils.overrides import UListProcessor

from collections import defaultdict, OrderedDict
from os import listdir
import os.path
import re
import json

from jinja2 import Environment, PackageLoader, select_autoescape
import pkg_resources


class VertoExtension(Extension):
    '''The Verto markdown extension which enables all the processors,
    and extracts all the important information to expose externally to
    the Verto converter.
    '''

    def __init__(self, processors=[], html_templates={}, extensions=[], *args, **kwargs):
        '''
        Args:
            processors: A set of processor names given as strings for which
                their processors are enabled. If given, all other
                processors are skipped.
            html_templates: A dictionary of HTML templates to override
                existing HTML templates for processors. Dictionary contains
                processor names given as a string as keys mapping HTML strings
                as values.
                eg: {'image': '<img src={{ source }}>'}
            extensions: A list of extra extensions for compatibility.
        '''
        super().__init__(*args, **kwargs)
        self.jinja_templates = self.loadJinjaTemplates(html_templates)
        self.processor_info = self.loadProcessorInfo()
        self.processors = processors
        self.title = None
        self.heading_tree = None
        self.custom_slugify = UniqueSlugify()
        self.glossary_terms = defaultdict(list)
        self.required_files = defaultdict(set)
        self.compatibility = []
        for extension in extensions:
            if isinstance(extension, utils.string_type):
                if extension.endswith('codehilite'):
                    self.compatibility.append('hilite')
                if extension.endswith('fenced_code'):
                    self.compatibility.append('fenced_code_block')

    def extendMarkdown(self, md, md_globals):
        '''Inherited from the markdown.Extension class. Extends
        markdown with custom processors.
            ['style', StylePreprocessor(self, md), '_begin']

        Args:
            md: An instance of the markdown object to extend.
            md_globals: Global variables in the markdown module namespace.
        '''
        self.buildProcessors(md, md_globals)

        def update_processors(processors, markdown_processors):
            for processor_data in processors:
                if processor_data[0] in self.processors:
                    markdown_processors.add(processor_data[0], processor_data[1], processor_data[2])

        update_processors(self.preprocessors, md.preprocessors)
        update_processors(self.blockprocessors, md.parser.blockprocessors)
        update_processors(self.inlinepatterns, md.inlinePatterns)
        update_processors(self.treeprocessors, md.treeprocessors)
        update_processors(self.postprocessors, md.postprocessors)

        md.preprocessors.add('style', StylePreprocessor(self, md), '_begin')
        md.postprocessors.add('remove', RemovePostprocessor(md), '_end')
        md.postprocessors.add('jinja', JinjaPostprocessor(md), '_end')

        # Compatibility modules
        md.postprocessors['raw_html'].isblocklevel = lambda html: is_block_level(html, BLOCK_LEVEL_ELEMENTS)
        md.parser.blockprocessors['olist'] = OListProcessor(md.parser)
        md.parser.blockprocessors['ulist'] = UListProcessor(md.parser)

        if ('fenced_code_block' in self.compatibility and 'scratch' in self.processors):
            md.preprocessors['fenced_code_block'].FENCED_BLOCK_RE = FENCED_BLOCK_RE_OVERRIDE

        if ('hilite' in self.compatibility and 'fenced_code_block' in self.compatibility and
           'scratch' in self.processors):
            processor = ScratchCompatibilityPreprocessor(self, md)
            md.preprocessors.add('scratch-compatibility', processor, '<fenced_code_block')

    def clear_document_data(self):
        '''Clears information stored for a specific document.
        '''
        self.title = None
        self.heading_tree = None

    def clear_saved_data(self):
        '''Clears stored information from processors, should be called
        between runs on unrelated documents.
        '''
        self.custom_slugify.clear()
        self.glossary_terms.clear()
        for key in self.required_files.keys():
            self.required_files[key].clear()

    def loadJinjaTemplates(self, custom_templates):
        '''Loads default templates from the templates directory, if
        a custom template is given that will override the default
        template.

        Args:
            custom_templates: a dictionary of names to custom templates
                which are used to override default templates.
        Returns:
            A dictionary of tuples containing template-names to
            compiled jinja templated.
        '''
        templates = {}
        env = Environment(
                loader=PackageLoader('verto', 'html-templates'),
                autoescape=select_autoescape(['html'])
                )
        for file in listdir(os.path.join(os.path.dirname(__file__), 'html-templates')):
            html_file = re.search(r'(.*?).html$', file)
            if html_file:
                processor_name = html_file.groups()[0]
                if processor_name in custom_templates:
                    templates[processor_name] = env.from_string(custom_templates[processor_name])
                else:
                    templates[processor_name] = env.get_template(file)
        return templates

    def buildProcessors(self, md, md_globals):
        '''
        Populates internal variables for processors. This should not be
        called externally, this is used by the extendMarkdown method.
        Args:
            md: An instance of the markdown object being extended.
            md_globals: Global variables in the markdown module namespace.
        '''
        self.preprocessors = [
            ['comment', CommentPreprocessor(self, md), '_begin'],
            ['save-title', SaveTitlePreprocessor(self, md), '_end'],
            ['remove-title', RemoveTitlePreprocessor(self, md), '_end'],
        ]
        self.blockprocessors = [
            # Markdown overrides
            ['heading', HeadingBlockProcessor(self, md.parser), '<hashheader'],
            # Single line (in increasing complexity)
            ['interactive', InteractiveBlockProcessor(self, md.parser), '<paragraph'],
            ['image-container', ImageContainerBlockProcessor(self, md.parser), '<paragraph'],
            ['image-tag', ImageTagBlockProcessor(self, md.parser), '<paragraph'],
            ['video', VideoBlockProcessor(self, md.parser), '<paragraph'],
            ['conditional', ConditionalProcessor(self, md.parser), '<paragraph'],
            ['panel', PanelBlockProcessor(self, md.parser), '<paragraph'],
            # Multiline
        ]
        self.inlinepatterns = [  # A special treeprocessor
            ['relative-link', RelativeLinkPattern(self, md), '_begin'],
            ['glossary-link', GlossaryLinkPattern(self, md), '_begin'],
            ['image-inline', ImageInlinePattern(self, md), '_begin']
        ]
        scratch_ordering = '>inline' if 'hilite' not in self.compatibility else '<hilite'
        self.treeprocessors = [
            ['scratch', ScratchTreeprocessor(self, md), scratch_ordering],
            ['scratch-inline', ScratchInlineTreeprocessor(self, md), '>inline'],
        ]
        self.postprocessors = []
        self.buildGenericProcessors(md, md_globals)

    def buildGenericProcessors(self, md, md_globals):
        '''Builds any generic processors as described by the processor
        info stored in the json file.
        Args:
            md: An instance of the markdown object to extend.
            md_globals: Global variables in the markdown module namespace.
        '''
        for processor, processor_info in self.processor_info.items():
            processor_class = processor_info.get('class', None)
            if processor_class == 'generic_tag':
                processor_object = GenericTagBlockProcessor(processor, self, md.parser)
                self.blockprocessors.insert(0, [processor, processor_object, '<paragraph'])
            if processor_class == 'generic_container':
                processor_object = GenericContainerBlockProcessor(processor, self, md.parser)
                self.blockprocessors.append([processor, processor_object, '<paragraph'])

    def loadProcessorInfo(self):
        '''Loads processor descriptions from a json file.

        Returns:
            The json object of the file where objects are ordered dictionaries.
        '''
        json_data = pkg_resources.resource_string('verto', 'processor-info.json').decode('utf-8')
        return json.loads(json_data, object_pairs_hook=OrderedDict)

    def get_heading_tree(self):
        '''
        Gets the heading tree as described by the heading processor.

        Returns:
            The internal heading tree object. None if heading processor
            has not been run.
        '''
        return self.heading_tree

    def _set_heading_tree(self, tree):
        ''' An internal method for setting the heading tree from
        an external processor.

        Args:
            tree: A tuple of HeadingNodes to become the new tree.
        '''
        assert isinstance(tree, tuple)
        assert all(isinstance(child, HeadingNode) for child in tree)
        self.heading_tree = tree

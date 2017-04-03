import unittest
from verto.Verto import Verto, VertoResult
from verto.processors.ScratchTreeprocessor import ScratchImageMetaData
from verto.utils.HeadingNode import HeadingNode
import jinja2
from verto.tests.BaseTest import BaseTest
from collections import defaultdict

class ConfigurationTest(BaseTest):
    '''Test configuration methods of Verto

    These are not true unit tests, as they create the complete Verto
    system, however we are using the unittest framework for ease of
    use and simplicity of our testing suite.
    '''

    def __init__(self, *args, **kwargs):
        '''Creates BaseTest Case class

        Create class inheiriting from TestCase, while also storing
        the path to test files and the maxiumum difference to display
        on test failures.
        '''
        BaseTest.__init__(self, *args, **kwargs)
        self.test_name = 'configuration'
        self.maxDiff = None
        self.custom_templates = {
            'image': '<img class=\'test\'/>',
            'boxed-text': '<div class=\'box\'>{% autoescape false %}{{ text }}{% endautoescape %}</div>'
        }

    def test_multiple_calls(self):
        '''Checks all fields of VertoResult are correct for multiple
        Verto calls.
        '''
        test_cases = [
            ('all_processors.md',
                VertoResult(
                    html_string=self.read_test_file(self.test_name, 'all_processors_expected.html', strip=True),
                    title='Example Title',
                    required_files={
                        'interactives': {
                            'binary-cards'
                        },
                        'images': set(),
                        'page_scripts': set(),
                        'scratch_images': {
                            ScratchImageMetaData(
                                hash='a0f8fcad796864abfacac8bda6e0719813833fd1fca348700abbd040557c1576',
                                text='when flag clicked\nclear\nforever\npen down\nif <<mouse down?> and <touching [mouse-pointer v]?>> then\nswitch costume to [button v]\nelse\nadd (x position) to [list v]\nend\nmove (foo) steps\nturn ccw (9) degrees'
                            ),
                        }
                    },
                    heading_tree=(HeadingNode(
                            title='Example Title',
                            title_slug='example-title',
                            level=1,
                            children=(),
                        ),
                        HeadingNode(
                            title='Example Title 2',
                            title_slug='example-title-2',
                            level=1,
                            children=()
                        ),
                    ),
                    required_glossary_terms=defaultdict(list)
                )
            ),
            ('some_processors.md',
                VertoResult(
                    html_string=self.read_test_file(self.test_name, 'some_processors_expected.html', strip=True),
                    title='Another Example Title',
                    required_files={
                        'interactives': set(),
                        'images': {'totally-legit-image.png'},
                        'page_scripts': set(),
                        'scratch_images': set()
                    },
                    heading_tree=(HeadingNode(
                        title='Another Example Title',
                        title_slug='another-example-title',
                        level=1,
                        children=(HeadingNode(
                            title='This is an H2',
                            title_slug='this-is-an-h2',
                            level=2,
                            children=()
                        ),),
                    ),),
                    required_glossary_terms={
                        'chomsky-hierarchy':
                            [('Formal languages', 'glossary-chomsky-hierarchy')]
                    }
                )
            ),
            ('some_processors_2.md',
                VertoResult(
                    html_string=self.read_test_file(self.test_name, 'some_processors_2_expected.html', strip=True),
                    title='Another Example Title',
                    required_files={
                        'interactives': set(),
                        'images': {
                            'totally-legit-image.png',
                            'finite-state-automata-no-trap-example.png',
                            'finite-state-automata-trap-added-example.png',
                            'finite-state-automata-trap-added-extreme-example.png',
                            },
                        'page_scripts': set(),
                        'scratch_images': set()
                    },
                    heading_tree=(HeadingNode(
                        title='Another Example Title',
                        title_slug='another-example-title',
                        level=1,
                        children=(),
                    ),),
                    required_glossary_terms={
                        'algorithm':
                            [('computer program', 'glossary-algorithm'),
                             ('algorithm cost', 'glossary-algorithm-2'),
                             ('searching algorithms', 'glossary-algorithm-3'),
                             ('sorting algorithms', 'glossary-algorithm-4')]
                    }
                )
            )
        ]

        for test in test_cases:
            verto = Verto()
            test_string = self.read_test_file(self.test_name, test[0])
            verto_result = verto.convert(test_string)

            self.assertEqual(verto_result.title, test[1].title)
            self.assertEqual(verto_result.required_files, test[1].required_files)
            self.assertTupleEqual(verto_result.heading_tree, test[1].heading_tree)
            self.assertDictEqual(verto_result.required_glossary_terms, test[1].required_glossary_terms)

    def test_custom_processors_and_custom_templates_on_creation(self):
        '''Checks if custom processors and custom templates work
        together on creation of verto.
        '''
        processors = {'image', 'boxed-text'}
        verto = Verto(processors=processors, html_templates=self.custom_templates)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'custom_processors_custom_templates_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_custom_processors_and_custom_templates_after_creation(self):
        '''Checks if custom processors and custom templates work
        together after creation of verto.
        '''
        processors = {'image', 'boxed-text'}
        verto = Verto()
        verto.update_processors(processors)
        verto.update_templates(self.custom_templates)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'custom_processors_custom_templates_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_default_processors_on_creation(self):
        '''Checks if all expected default processors work on default
        creation.
        '''
        verto = Verto()
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'all_processors_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_custom_processors_on_creation(self):
        '''Checks if system only uses specified processors.
        '''
        processors = {'panel', 'image'}
        verto = Verto(processors=processors)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'custom_processors_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_custom_processors_after_creation(self):
        '''Checks if extension correct changes processors.
        '''
        verto = Verto()
        processors = Verto.processor_defaults()
        processors.add('example_processor')
        processors.remove('comment')
        verto.update_processors(processors)
        # Check example_processor is now stored in extension processors
        self.assertEqual(verto.verto_extension.processors, processors)
        # Check comments are now skipped
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'all_processors_except_comment_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_unique_custom_processors(self):
        '''Checks if unique processors are stored when duplicates
        provided.
        '''
        processors = ['comment', 'comment', 'comment']
        verto = Verto(processors=processors)
        self.assertEqual(verto.verto_extension.processors, set(processors))
        processors = list(Verto.processor_defaults())
        processors.append('example_processor')
        processors.append('example_processor')
        processors.append('example_processor')
        verto.update_processors(processors)
        self.assertTrue(verto.verto_extension.processors, processors)

    def test_custom_templates_on_creation(self):
        '''Checks custom templates are used when given on creation.
        '''
        verto = Verto(html_templates=self.custom_templates)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'all_processors_custom_html_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_custom_templates_after_creation(self):
        '''Checks custom templates are used when given after creation.
        '''
        verto = Verto()
        verto.update_templates(self.custom_templates)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'all_processors_custom_html_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_reset_templates_after_custom(self):
        '''Checks custom templates are reset when given at creation.
        '''
        verto = Verto(html_templates=self.custom_templates)
        verto.clear_templates()
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'all_processors_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)

    def test_multiline_custom_templates(self):
        '''Checks that multiple multiline custom templates are loaded
        and used correctly.
        '''
        custom_templates = {
            'image': '''<div class="text-center">
                          <img src="{{ file_path }}" class="rounded img-thumbnail"/>
                        </div>''',
            'boxed-text': '''<div class="card">
                               <div class="card-block">
                                 {{ text }}
                               </div>
                             </div>''',
            'heading': '''<{{ heading_type }} id="{{ title_slug }}">
                            <span class="section_number">
                              {{ level_1 }}.{{ level_2 }}.{{ level_3 }}.{{ level_4 }}.{{ level_5 }}.{{ level_6 }}.
                            </span>
                            {{ title }}
                          </{{ heading_type }}>'''
        }

        verto = Verto(html_templates=custom_templates)
        test_string = self.read_test_file(self.test_name, 'all_processors.md')
        converted_test_string = verto.convert(test_string).html_string
        expected_string = self.read_test_file(self.test_name, 'multiline_templates_expected.html', strip=True)
        self.assertEqual(expected_string, converted_test_string)
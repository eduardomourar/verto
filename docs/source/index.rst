Welcome to Verto
#################

Verto is an extension of the Python `Markdown <https://pypi.python.org/pypi/Markdown>`_ package, which allows authors to include complex HTML elements with simple text tags in their Markdown files.

For example:

.. code-block:: python

    >>> import verto
    >>> converter = verto.Verto()
    >>> result = converter.convert('{video url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"}')
    >>> result.html_string
    "<iframe src='http://www.youtube.com/embed/dQw4w9WgXcQ?rel=0' frameborder='0' allowfullscreen></iframe>"

.. toctree::
    :maxdepth: 2
    :caption: Contents

    install
    usage
    processors/index
    extensions
    contributing
    changelog

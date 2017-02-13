![Kordac Logo](kordac/images/kordac-logo.png)

[![Build Status](https://travis-ci.org/uccser/kordac.svg?branch=master)](https://travis-ci.org/uccser/kordac)

Kordac is an extension of the Python Markdown package, which allows authors to include complex HTML elements with simple text tags in their Markdown files.

**Warning:** *This repository is currently in development!
Therefore features may not be implemented yet, may change, be buggy, or completely broken.*

## Installing development version as local package

1. `$ git clone https://github.com/uccser/kordac.git`
2. `$ cd kordac`
3. `$ pip3 install .`

## Quick usage

```python
>>> import kordac
>>> convertor = kordac.Kordac()
>>> result = convertor.run('Hi')
>>> result.html_string
'<p>Hi</p>'
```

## Docs

Temp docs available [here](https://docs.google.com/document/d/1_cnHTaaNOQTLYJ7Cxx7PjuBAJcFMR7J62i4qXJ-0Rl4/edit?usp=sharing)

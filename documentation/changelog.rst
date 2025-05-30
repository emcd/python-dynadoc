.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Release Notes
*******************************************************************************

.. towncrier release notes start

Dynadoc 1.1 (2025-05-29)
========================

Enhancements
------------

- Improve argument and return documentation on Sphinx Autodoc renderer.


Repairs
-------

- Ensure multiline descriptions render correctly by indenting all subsequent
  lines after the first one.


Dynadoc 1.0 (2025-05-25)
========================

Enhancements
------------

- Add support for CPython 3.10, 3.11, 3.12, and 3.13.
- Add support for PyPy 3.10.
- Automatic docstring generation from ``Doc`` and ``Raises`` annotations.
  Extracts rich documentation metadata from type annotations and generates
  comprehensive Sphinx-compatible docstrings.
- Configurable introspection with recursive documentation of classes, functions,
  properties, and modules. Fine-grained control over documentation depth,
  inheritance processing, and attribute scanning.
- Extensible architecture with custom renderers, fragment rectifiers, and
  introspection limiters. Configurable contexts and error handling strategies
  for different development workflows and deployment environments.
- Flexible visibility control system with support for ``__all__`` declarations,
  custom visibility deciders, and explicit ``Visibilities`` annotations.
  Controls which attributes appear in generated documentation.
- Function and class decoration with ``@with_docstring`` decorator. Processes
  annotated parameters, return values, and exception specifications to generate
  detailed reStructuredText documentation.
- Module-level documentation generation with ``assign_module_docstring``.
  Automatically documents module attributes, type aliases, and exported
  functions with comprehensive introspection capabilities.
- Reusable documentation fragment system with ``Fname`` annotations. Enables
  consistent terminology across projects through fragment tables and
  class-based fragment storage via ``_dynadoc_fragments_`` attributes.
- Sphinx Autodoc-compatible reStructuredText renderer with multiple formatting
  styles. Generates proper ``:argument:``, ``:type:``, ``:returns:``, and
  ``:raises:`` directives for seamless integration with Sphinx documentation.

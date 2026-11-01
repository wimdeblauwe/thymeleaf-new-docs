---
title: "Introducing Thymeleaf"
description: "Thymeleaf is a modern server-side Java template engine for both web and standalone environments, capable of processing HTML, XML, JavaScript, CSS and even plain text."
sidebar:
  order: 1
---

## What is Thymeleaf?

Thymeleaf is a modern server-side Java template engine for both web and
standalone environments, capable of processing HTML, XML, JavaScript, CSS and
even plain text. 

The main goal of Thymeleaf is to provide an elegant and highly-maintainable way
of creating templates. To achieve this, it builds on the concept of *Natural
Templates* to inject its logic into template files in a way that doesn't affect
the template from being used as a design prototype. This improves communication
of design and bridges the gap between design and development teams.

Thymeleaf has also been designed from the beginning with Web Standards in mind
-- especially **HTML5** -- allowing you to create fully validating templates if
that is a need for you.

## What kind of templates can Thymeleaf process?

Out-of-the-box, Thymeleaf allows you to process six kinds of templates, each of
which is called a **Template Mode**:

 * HTML
 * XML
 * TEXT
 * JAVASCRIPT
 * CSS
 * RAW 

There are two *markup* template modes (`HTML` and `XML`), three *textual* template 
modes (`TEXT`, `JAVASCRIPT` and `CSS`) and a *no-op* template mode (`RAW`).

The **`HTML`** template mode will allow any kind of HTML input, including HTML5,
HTML 4 and XHTML. No validation or well-formedness check will be performed, and
template code/structure will be respected to the biggest possible extent in
output.

The **`XML`** template mode will allow XML input. In this case, code is expected 
to be well-formed -- no unclosed tags, no unquoted attributes, etc -- and
the parser will throw exceptions if well-formedness violations are found. Note
that no *validation* (against a DTD or XML Schema) will be performed.

The **`TEXT`** template mode will allow the use of a special syntax for
templates of a non-markup nature. Examples of such templates might be text
emails or templated documentation. Note that HTML or XML templates can be also
processed as `TEXT`, in which case they will not be parsed as markup, and every
tag, DOCTYPE, comment, etc, will be treated as mere text.

The **`JAVASCRIPT`** template mode will allow the processing of JavaScript files 
in a Thymeleaf application. This means being able to use model data inside
JavaScript files in the same way it can be done in HTML files, but with
JavaScript-specific integrations such as specialized escaping or *natural
scripting*. The `JAVASCRIPT` template mode is considered a *textual* mode 
and therefore uses the same special syntax as the `TEXT` template mode.

The **`CSS`** template mode will allow the processing of CSS files involved in a
Thymeleaf application. Similar to the `JAVASCRIPT` mode, the `CSS` template mode
is also a *textual* mode and uses the special processing syntax from the `TEXT`
template mode.

The **`RAW`** template mode will simply not process templates at all. It is meant 
to be used for inserting untouched resources (files, URL responses, etc.) into
the templates being processed. For example, external, uncontrolled resources in
HTML format could be included into application templates, safely knowing that
any Thymeleaf code that these resources might include will not be executed.

## Dialects: The Standard Dialect

Thymeleaf is an extremely extensible template engine (in fact it could be called
a _template engine framework_) that allows you to define and customize the way
your templates will be processed to a fine level of detail.

An object that applies some logic to a markup artifact (a tag, some text, a
comment, or a mere placeholder if templates are not markup) is called a _processor_,
and a set of these processors -- plus perhaps some extra artifacts -- is what
a **dialect** is normally comprised of. Out of the box, Thymeleaf's core library
provides a dialect called the **Standard Dialect**, which should be enough for
most users. 

> Note that dialects can actually have no processors and be entirely comprised
> of other kinds of artifacts, but processors are definitely the most common
> use case.

_This tutorial covers the Standard Dialect_. Every attribute and syntax feature
you will learn about in the following pages is defined by this dialect, even if
that isn't explicitly mentioned.

Of course, users can create their own dialects (even extending the Standard one)
if they want to define their own processing logic while taking advantage of the
library's advanced features. Thymeleaf can also be configured to use several
dialects at a time.

> The official thymeleaf-spring3 and thymeleaf-spring4 integration packages
> both define a dialect called the "SpringStandard Dialect", which is mostly the
> same as the Standard Dialect, but with small adaptations to make better use of
> some features in the Spring Framework (for example, by using Spring Expression
> Language or SpringEL instead of OGNL). So if you are a Spring MVC user you are
> not wasting your time, as almost everything you learn here will be of use in
> your Spring applications.

Most of the processors of the Standard Dialect are _attribute processors_. This
allows browsers to correctly display HTML template files even before
being processed because they will simply ignore the additional attributes. For
example, while a JSP using tag libraries could include a fragment of code not
directly displayable by a browser like:

```html
<form:inputText name="userName" value="${user.name}" />
```

...the Thymeleaf Standard Dialect would allow us to achieve the same
functionality with:

```html
<input type="text" name="userName" value="James Carrot" th:value="${user.name}" />
```

Not only will this be correctly displayed by browsers, but this also allows us to
(optionally) specify a value attribute in it ("James Carrot", in this case) that
will be displayed when the prototype is statically opened in a browser, and that
will be substituted by the value resulting from the evaluation of `${user.name}`
during processing of the template.

This helps your designer and developer to work on the very same template file
and reduce the effort required to transform a static prototype into a working
template file. The ability to do this is a feature called _Natural Templating_.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#introducing-thymeleaf) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

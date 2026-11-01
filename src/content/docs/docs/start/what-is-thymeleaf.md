---
title: "What is Thymeleaf?"
description: "Thymeleaf is a server-side Java template engine for web and standalone applications. It processes HTML, XML, JavaScript, CSS and plain text."
sidebar:
  order: 1
---

Thymeleaf is a server-side Java template engine for web and standalone applications. It processes HTML, XML, JavaScript, CSS and plain text.

Its main idea is the [natural template](../natural-templates/). Thymeleaf's logic lives in the template file without stopping that file from working as a design prototype, so designers and developers can work on the same file.

Thymeleaf was designed with web standards in mind, HTML5 in particular. You can write templates that fully validate if you need to.

## What kind of templates can Thymeleaf process?

Thymeleaf has six **template modes**. `HTML` and `XML` are markup modes, `TEXT`, `JAVASCRIPT` and `CSS` are textual modes, and `RAW` is a no-op mode.

`HTML` accepts any kind of HTML, including HTML5, HTML 4 and XHTML. Thymeleaf doesn't validate the input or check that it's well formed, and it keeps your code and structure in the output as far as it can.

`XML` expects well-formed input, so the parser throws an exception on an unclosed tag or an unquoted attribute. It doesn't validate against a DTD or XML Schema.

`TEXT` uses a special syntax for templates that aren't markup, such as text emails or templated documentation. You can also process HTML or XML as `TEXT`. Thymeleaf then doesn't parse them as markup, and treats every tag, DOCTYPE and comment as plain text.

`JAVASCRIPT` processes JavaScript files. You use model data in them the same way you do in HTML files, with JavaScript-specific additions such as specialized escaping and *natural scripting*. It's a textual mode, so it uses the `TEXT` syntax.

`CSS` processes CSS files. Like `JAVASCRIPT`, it's a textual mode and uses the `TEXT` syntax.

`RAW` doesn't process templates at all. Use it to insert untouched resources, such as files or URL responses, into the templates you're processing. Any Thymeleaf code inside an external HTML resource won't run, so you can include uncontrolled content this way.

## Dialects: the Standard Dialect

You can customize how Thymeleaf processes your templates in fine detail. It's close to a template engine framework.

A *processor* is an object that applies logic to a markup artifact, such as a tag, some text, a comment, or a placeholder if the template isn't markup. A **dialect** is usually a set of processors, sometimes with other artifacts.

> A dialect can have no processors at all and consist only of other kinds of artifacts, but that's rare.

Thymeleaf's core library includes the **Standard Dialect**, which is enough for most users. These docs cover it unless they say otherwise, so assume every attribute and syntax feature in the Templates section comes from this dialect.

You can [write your own dialect](../../extending/dialects-and-processors/) to add your own processing logic, and it can extend the Standard Dialect. Thymeleaf can also use several dialects at once.

> The `thymeleaf-spring5` and `thymeleaf-spring6` integration packages define the [SpringStandard Dialect](../../spring/spring-standard-dialect/). It's mostly the same as the Standard Dialect, with small changes for Spring, such as using Spring Expression Language instead of OGNL. If you use Spring MVC, almost everything you learn about the Standard Dialect still applies.

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [What is Thymeleaf?](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#what-is-thymeleaf), [What kind of templates can Thymeleaf process?](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#what-kind-of-templates-can-thymeleaf-process), [Dialects: The Standard Dialect](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#dialects-the-standard-dialect).*

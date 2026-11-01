---
title: "Natural templates"
description: "A natural template is an HTML file that works both as a Thymeleaf template and as a static page you can open in a browser."
sidebar:
  order: 2
---

A natural template is an HTML file that works in two ways. A browser can open it directly as a static page, and Thymeleaf can process it into the real page. Designers and developers can work on the same file, and you can check a layout without starting an application.

This works because most of the Standard Dialect's logic lives in attributes. Browsers ignore attributes they don't know, so `th:*` does nothing until Thymeleaf processes the file.

## A minimal example

Each element keeps a placeholder for the browser, and a `th:*` attribute for Thymeleaf:

```html title="Template"
<p th:text="${product.name}">Placeholder product</p>
<input type="text" name="name" value="Placeholder" th:value="${product.name}">
```

```html title="Output"
<p>Fresh sweet basil</p>
<input type="text" name="name" value="Fresh sweet basil">
```

Opened directly, the file shows "Placeholder product". Processed, it shows the model's value, and the `th:*` attributes are gone.

Compare that with a JSP tag, which a browser can't display:

```html
<form:input path="name" />
```

## Keep prototype data out of the output

A prototype often needs more than one row to look right, but only the first row should be repeated. `th:remove="all-but-first"` removes the other children when Thymeleaf processes the file:

```html title="Template"
<ul th:remove="all-but-first">
  <li th:each="product : ${products}" th:text="${product.name}">Fresh sweet basil</li>
  <li>Italian tomato</li>
  <li>Thymus vulgaris</li>
</ul>
```

```html title="Output"
<ul>
  <li>Fresh sweet basil</li>
  <li>Italian tomato</li>
</ul>
```

The output's two items come from `${products}`. The two static items only exist in the prototype.

## Hide template-only and prototype-only markup

Thymeleaf has two comment forms for markup that belongs to one side only.

To keep markup out of the output but show it in the prototype, wrap it in a parser-level comment written like this. The browser sees two ordinary comments with the markup between them, and Thymeleaf removes everything from `<!--/*` to `*/-->`:

```html title="Template"
<!--/*-->
<p>Only in the prototype</p>
<!--*/-->
<p>In both</p>
```

```html title="Output"
<p>In both</p>
```

A prototype-only comment does the opposite. The browser sees an ordinary comment, and Thymeleaf uncomments the content and processes it:

```html title="Template"
<!--/*/ <p th:text="${product.name}">Placeholder</p> /*/-->
```

```html title="Output"
<p>Fresh sweet basil</p>
```

## Link to assets that work both ways

Give a link both a static `href` and a `th:href`. The browser uses the first, and Thymeleaf replaces it with the second, which also adds the application's context path:

```html title="Template"
<link rel="stylesheet" href="../static/css/shop.css" th:href="@{/css/shop.css}">
```

```html title="Output"
<link rel="stylesheet" href="/css/shop.css">
```

## A complete page

Here's a form from the Seed Starter Manager, opened directly in a browser without running the application. It isn't a working application and the data isn't real, but it's a fully displayable prototype:

![STSM natural templating](../images/thymeleafspring/stsm-natural-templating.png)

## Common mistakes

- **Fragments hide the prototype:** a page built only from `th:replace` shows almost nothing when opened directly. Keep representative markup inside the element you replace.
- **Expressions in plain text:** `[[${product.name}]]` appears literally in a prototype. Prefer `th:text` on pages that you open directly.
- **Root-relative asset links:** `href="/css/shop.css"` breaks when you open the file from disk, so use a relative path for the static value.

## Related pages

- [Comments and blocks](../../templates/comments-and-blocks/)
- [`th:remove` in the attributes reference](../../reference/attributes/#th-remove)
- [From HTML to HTML (via HTML)](../html-history/), the history of the HTML standards

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Dialects: The Standard Dialect](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#dialects-the-standard-dialect), [It's still a Prototype!](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#its-still-a-prototype).*

---
title: What is Thymeleaf?
description: A short introduction to Thymeleaf and natural templates.
---

Thymeleaf is a server-side Java template engine. It processes HTML, XML, JavaScript, CSS and plain text, and it's most often used to render the HTML views of web applications.

## Natural templates

A Thymeleaf template is valid HTML. Its logic lives in attributes that a browser ignores, so you can open the file directly and still see a realistic page.

```html
<p th:text="${product.name}">Fresh basil</p>
```

Opened as a file, this shows "Fresh basil". When Thymeleaf renders it, the value of `product.name` replaces that text.

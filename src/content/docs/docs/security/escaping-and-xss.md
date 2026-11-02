---
title: "Escaping and XSS"
description: "How Thymeleaf escapes output, which features skip it, and how to avoid cross-site scripting in templates."
sidebar:
  order: 1
---

Cross-site scripting (XSS) happens when a value from a user reaches the browser as code instead of text. Thymeleaf escapes output by default, so `th:text` and most attributes are safe. This page covers how far that protection goes, and the places where you have to do more.

The examples use a `comment` value of `<b>Tasty</b> & fresh`, which stands in for text from a user. All of them run against Thymeleaf 3.1.5.

## Escaped by default

`th:text` and the inlined form `[[...]]` HTML-escape the value, so the browser shows the characters instead of treating them as markup:

```html title="Template"
<p th:text="${comment}">Placeholder</p>
<p>[[${comment}]]</p>
```

```html title="Output"
<p>&lt;b&gt;Tasty&lt;/b&gt; &amp; fresh</p>
<p>&lt;b&gt;Tasty&lt;/b&gt; &amp; fresh</p>
```

Attribute values are escaped too:

```html title="Template"
<img src="basil.png" th:alt="${comment}">
```

```html title="Output"
<img src="basil.png" alt="&lt;b&gt;Tasty&lt;/b&gt; &amp; fresh">
```

## Unescaped output

`th:utext` and the inlined form `[(...)]` write the value as it is:

```html title="Template"
<p th:utext="${comment}">Placeholder</p>
<p>[(${comment})]</p>
```

```html title="Output"
<p><b>Tasty</b> & fresh</p>
<p><b>Tasty</b> & fresh</p>
```

:::danger
Only use `th:utext` and `[(...)]` for HTML that you trust, such as content written by your own team. If a user can influence the value, they can run scripts in other users' browsers.
:::

If you need to display HTML from users, such as a rich text comment, clean it on the server with an allow-list HTML sanitizer before it reaches the model. Don't try to filter it in the template.

## Escaping depends on where the value goes

HTML escaping is only correct for HTML. Each other context has its own rules:

| Where the value goes | What to use |
| --- | --- |
| Element text | `th:text`, `[[...]]` |
| Attribute value | `th:title`, `th:value`, `th:data-*` |
| URL | `@{...}`, and validate the scheme of a user-supplied URL |
| JavaScript | `th:inline="javascript"` |
| CSS | `th:inline="css"` |
| Inline event handler | Don't. Use a `data-*` attribute |
| Alpine.js or other client-side expression | Don't. Use a `data-*` attribute |

### JavaScript

Use `th:inline="javascript"` for a `<script>` block. Thymeleaf then writes the value as a JavaScript literal, with its own escaping. Here `customerName` is `Ann'; alert(1); //`:

```html title="Template"
<script th:inline="javascript">
  const customer = [[${customerName}]];
</script>
```

```html title="Output"
<script>
  const customer = "Ann'; alert(1); \/\/";
</script>
```

The value stays a string. Without `th:inline="javascript"` the expression isn't processed in the `<script>`, and you get the literal text `[[${customerName}]]`.

:::caution
`[(...)]` in a script skips this escaping, in the same way as it does in HTML.
:::

### Event handlers

Thymeleaf only accepts numbers and booleans from a variable expression in `th:on*` attributes, because no escaping makes text safe there:

```html title="Rejected"
<button th:onclick="${product.name}">Add</button>
```

A number is fine:

```html title="Template"
<button th:onclick="${product.stock}">Add</button>
```

```html title="Output"
<button onclick="3">Add</button>
```

To pass text to a script, put it in a `data-*` attribute and read it from there:

```html title="Template"
<button th:data-name="${customerName}" onclick="addToBasket(this.dataset.name)">Add</button>
```

```html title="Output"
<button data-name="Ann&#39;; alert(1); //" onclick="addToBasket(this.dataset.name)">Add</button>
```

The same applies to attributes that hold code for a client-side library. HTML escaping doesn't help there, because the browser decodes the attribute before the library reads it. We confirmed this with Alpine.js 3.17.5: a quote in a value placed in `x-data` through `th:x-data` broke out of its string and ran. See [Set Alpine.js attributes from the server](../../interactive-uis/overview/#set-alpinejs-attributes-from-the-server).

### URLs

Link expressions encode parameters, so a value can't escape from them:

```html title="Template"
<a th:href="@{/search(q=${comment})}">Search</a>
```

```html title="Output"
<a href="/search?q=%3Cb%3ETasty%3C/b%3E%20%26%20fresh">Search</a>
```

The base of a URL is different. Thymeleaf writes the URL your application gives it. Here `website` is a value a user entered, `javascript:alert(1)`:

```html title="Template"
<a th:href="${website}">Website</a>
```

```html title="Output"
<a href="javascript:alert(1)">Website</a>
```

Validating URLs that come from users is your application's job, as it is for any other user input. Check them on the server, and allow only the schemes you expect, such as `http` and `https`.

## Restricted expression mode

In some positions Thymeleaf refuses request parameters outright, which stops the most direct way of sending user input into a sensitive place. `th:text` can read a parameter, because it escapes the value:

```html title="Template, with ?q=basil"
<p th:text="${param.q}">Placeholder</p>
```

```html title="Output"
<p>basil</p>
```

`th:utext` can't:

```html title="Rejected, with ?q=basil"
<p th:utext="${param.q}">Placeholder</p>
```

The same goes for the default attribute processor, which handles attributes like `th:data-*` and `th:hx-*`:

```html title="Rejected, with ?q=basil"
<p th:data-query="${param.q}">Placeholder</p>
```

These checks are a second layer of defence. They only look at how an expression is written, so a model attribute that holds the same parameter value passes. [Expression restrictions](../expression-restrictions/) lists every context.

## Don't build expressions from user input

Thymeleaf runs expressions, so user input must never become part of one. The risky places are view names, fragment names, and preprocessing with `__...__`:

```java
// Don't: the user chooses what Thymeleaf evaluates
@GetMapping("/products")
public String products(@RequestParam String view) {
    return "products/" + view;
}
```

Map the input onto values that you control instead:

```java
@GetMapping("/products")
public String products(@RequestParam String view) {
    return switch (view) {
        case "grid" -> "products/grid";
        default -> "products/list";
    };
}
```

Thymeleaf's [security policy](https://github.com/thymeleaf/thymeleaf/blob/3.1-master/SECURITY.md) is clear on this: validating input is the application's job, whichever part of a template the input ends up in. Thymeleaf's restrictions are defence in depth and not a boundary to rely on.

## Checklist

- Use `th:text` and `[[...]]` unless you have a specific reason not to.
- Search your templates for `th:utext` and `[(`, and check where each value comes from.
- Use `th:inline="javascript"` for values in scripts.
- Keep server data out of event handlers and client-side expressions. Use `data-*` attributes.
- Validate the scheme of user-supplied URLs.
- Never concatenate user input into a view name, fragment name or expression.
- Consider a Content Security Policy as an extra layer.

## Related pages

- [Expression restrictions](../expression-restrictions/)
- [Inlining](../../templates/inlining/)
- [`th:utext` in the attributes reference](../../reference/attributes/#th-utext)

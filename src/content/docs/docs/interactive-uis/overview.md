---
title: "Overview"
description: "Choose an approach for adding interactivity to server-rendered Thymeleaf pages, with htmx and Alpine.js."
sidebar:
  order: 1
---

You can build a responsive interface with Thymeleaf without a JavaScript single-page application. The server keeps owning the HTML, and you add behaviour only where a page needs it.

Two small libraries cover most needs. They work through HTML attributes, which fit well next to `th:*`.

## Choose an approach

| You need to | Use | Thymeleaf's part |
| --- | --- | --- |
| Replace part of a page with fresh server data | [htmx](https://htmx.org) | Render only the fragment that changed |
| Handle local state, such as a dropdown or tabs | [Alpine.js](https://alpinejs.dev) | Render the initial HTML and state |
| Do both on one page | htmx and Alpine.js | Keep the templates as the single source of markup |
| Build a heavily client-driven application, such as a drawing tool or an offline editor | Probably a different architecture | Thymeleaf may only serve the first page |

Both libraries are plain script tags and need no Thymeleaf integration, or any build step. These pages teach only how they fit with Thymeleaf. The libraries' own documentation covers everything else.

## Set htmx attributes from the server

Thymeleaf leaves attributes it doesn't know alone, so `hx-*` attributes pass through unchanged. To compute a value, prefix it with `th:`. The default attribute processor handles any name, so `th:hx-get` sets `hx-get`:

```html title="Template"
<button th:hx-get="@{/products/{name}(name=${product.name})}" hx-target="#details">Details</button>
```

```html title="Output"
<button hx-get="/products/Fresh%20sweet%20basil" hx-target="#details">Details</button>
```

[Partial page updates with htmx](../partial-page-updates/) continues from here.

## Set Alpine.js attributes from the server

Alpine's attributes also pass through unchanged, including the shorthand forms with `@` and `:`:

```html title="Template"
<div x-data="{ open: false }">
  <button @click="open = !open" :class="open && 'active'">Toggle</button>
  <p x-show="open" x-on:click="open = false" th:text="${product.name}">Placeholder</p>
</div>
```

```html title="Output"
<div x-data="{ open: false }">
  <button @click="open = !open" :class="open && 'active'">Toggle</button>
  <p x-show="open" x-on:click="open = false">Fresh sweet basil</p>
</div>
```

Computing these attributes needs more care. What we found by testing:

| Form | Result |
| --- | --- |
| `th:x-data`, `th:@click` | Works through the default attribute processor, but read the warning below |
| `th:attr="@click=..."`, `th:attr="x-on:click=..."` | Template error: `th:attr` can't parse these names |
| `x-data="{ name: '[[${name}]]' }"` | Stays as literal text, because inlining doesn't run inside attributes |

:::danger
Don't put server text into an Alpine expression. `x-data`, `@click` and similar attributes run as JavaScript, and HTML escaping doesn't protect them, because the browser decodes the attribute before Alpine reads it.

With `th:x-data="|{ name: '${name}' }|"` and a value of `x' + (window.pwned = 1) + '`, Thymeleaf correctly escaped the quotes to `&#39;`, and the browser still ran the code.
:::

The safe way is a `data-*` attribute. Thymeleaf escapes the value as HTML, and Alpine reads it as a plain string that it never evaluates:

```html title="src/main/resources/templates/grocery/quantity.html"
  <div x-data="{ quantity: Number($el.dataset.quantity), name: $el.dataset.name }"
       th:data-quantity="${product.stock}"
       th:data-name="${product.name}">
    <p x-text="name">Fresh sweet basil</p>
    <button type="button" @click="quantity--" :disabled="quantity === 0">Remove one</button>
    <output x-text="quantity" th:text="${product.stock}">3</output>
    <button type="button" x-on:click="quantity++">Add one</button>
  </div>
```

The same value that ran as code in `th:x-data` stayed inert text this way. `th:text` on the `<output>` also means the page shows the right number before Alpine starts.

## Tested versions

The examples on this page are in [`samples/showcase`](https://github.com/wimdeblauwe/thymeleaf-new-docs/tree/main/samples/showcase). They were tested in Chrome with htmx 2.0.11, Alpine.js 3.17.5, Thymeleaf 3.1.5 and Spring Boot 4.1.2.

## Next steps

- [Partial page updates with htmx](../partial-page-updates/)
- [Escaping and XSS](../../security/escaping-and-xss/)
- [Components](../../templates/components/), for fragments that both full pages and partial responses can share

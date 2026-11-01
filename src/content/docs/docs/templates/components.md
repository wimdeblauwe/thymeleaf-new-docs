---
title: "Components"
description: "Build reusable UI components from fragments, with parameters, optional values and markup passed in from the caller."
sidebar:
  order: 9
---

A component is a fragment that behaves like a function. You give it parameters, and it renders a piece of UI that looks the same everywhere you use it. Thymeleaf has no separate component feature, because fragments with parameters already do the job.

This page builds up from a one-line badge to a panel that accepts markup from its caller. The examples are in [`samples/showcase`](https://github.com/wimdeblauwe/thymeleaf-new-docs/tree/main/samples/showcase) and run against Thymeleaf 3.1.5. If you haven't used fragments before, read [Fragments](../fragments/) first.

## A first component

Keep components together in a template file, which is a normal template with a `th:fragment` on each component:

```html title="src/main/resources/templates/components/ui.html"
<span th:fragment="badge(label)" class="badge" th:text="${label}">In stock</span>
```

Call it with `th:replace`, passing the value in brackets. The host element disappears, so a `<div>` here doesn't end up in the output:

```html title="Template"
<div th:replace="~{components/ui :: badge('Sold out')}"></div>
```

```html title="Output"
<span class="badge">Sold out</span>
```

Use `th:insert` if you want to keep the host element.

## Several parameters

Pass parameters by position or by name. With names, the order doesn't matter:

```html title="src/main/resources/templates/components/ui.html"
<div th:fragment="alert(kind, message)" class="alert" th:classappend="|alert-${kind}|" role="alert">
  <p th:text="${message}">Your basket was updated.</p>
</div>
```

```html title="Template"
<div th:replace="~{components/ui :: alert('info', 'Delivery is free this week.')}"></div>
<div th:replace="~{components/ui :: alert(message='Out of stock.', kind='error')}"></div>
```

```html title="Output"
<div class="alert alert-info" role="alert">
  <p>Delivery is free this week.</p>
</div>
<div class="alert alert-error" role="alert">
  <p>Out of stock.</p>
</div>
```

The placeholder text in `ui.html` means the file is still a [natural template](../../start/natural-templates/), so you can open it in a browser as a small catalogue of components.

## Pass objects

A parameter can be any value, and a component can use other components. `:: badge` without a template name means the same file:

```html title="src/main/resources/templates/components/ui.html"
<article th:fragment="product-card(product)" class="card">
  <h3 th:text="${product.name}">Fresh sweet basil</h3>
  <p th:text="${#numbers.formatDecimal(product.price, 1, 2)}">4.99</p>
  <span th:replace="~{:: badge(${product.inStock} ? 'In stock' : 'Sold out')}">In stock</span>
</article>
```

```html title="Template"
<div th:each="product : ${products}">
  <article th:replace="~{components/ui :: product-card(${product})}"></article>
</div>
```

```html title="Output"
<div>
  <article class="card">
    <h3>Fresh sweet basil</h3>
    <p>4.99</p>
    <span class="badge">In stock</span>
  </article>
</div>
<div>
  <article class="card">
    <h3>Italian tomato</h3>
    <p>1.25</p>
    <span class="badge">Sold out</span>
  </article>
</div>
```

## Optional parameters

A fragment with a parameter list needs a value for every parameter. This call fails, because `badge` declares one parameter and gets none:

```html title="Rejected"
<div th:replace="~{components/ui :: badge()}"></div>
```

To make a parameter optional, leave the list out of `th:fragment` and call the fragment with named parameters. Inside the fragment, use `?:` to set a default:

```html title="src/main/resources/templates/components/ui.html"
<span th:fragment="chip" class="chip" th:classappend="|chip-${tone ?: 'neutral'}|" th:text="${label}">New</span>
```

```html title="Template"
<div th:replace="~{components/ui :: chip(label='New')}"></div>
<div th:replace="~{components/ui :: chip(label='Sale', tone='warning')}"></div>
```

```html title="Output"
<span class="chip chip-neutral">New</span>
<span class="chip chip-warning">Sale</span>
```

Named parameters work like `th:with`, so the fragment can still see every variable of the caller. If the caller has its own `tone` variable and leaves the parameter out, the fragment picks that up.

## Check parameters

`th:assert` stops rendering if a check fails, so a mistake in a call shows up as an error and not as a broken page:

```html title="src/main/resources/templates/components/ui.html"
<p th:fragment="price-tag(amount)" th:assert="${amount != null}" class="price"
   th:text="${#numbers.formatDecimal(amount, 1, 2)}">4.99</p>
```

```html title="Rejected"
<p th:replace="~{components/ui :: price-tag(${missing})}"></p>
```

<a id="flexible-layouts-beyond-mere-fragment-insertion"></a>

## Pass markup into a component

A parameter can also be a fragment, which gives you the equivalent of slots in other component systems. Use `th:insert` or `th:replace` on the parameter inside the component:

```html title="src/main/resources/templates/components/ui.html"
<section th:fragment="panel(title, body, footer)" class="panel">
  <h2 th:text="${title}">Panel title</h2>
  <div class="panel-body" th:insert="${body}">Panel content</div>
  <footer th:replace="${footer}">Default footer</footer>
</section>
```

The caller selects markup from its own template with `~{:: selector}`:

```html title="Template"
<div th:replace="~{components/ui :: panel('Opening hours', ~{:: #hours}, ~{:: #note})}">
  <ul id="hours">
    <li>Monday to Saturday, 8:00 to 20:00</li>
  </ul>
  <footer id="note">Closed on public holidays.</footer>
</div>
```

```html title="Output"
<section class="panel">
  <h2>Opening hours</h2>
  <div class="panel-body"><ul id="hours">
    <li>Monday to Saturday, 8:00 to 20:00</li>
  </ul></div>
  <footer id="note">Closed on public holidays.</footer>
</section>
```

The selected markup lives inside the host element. That element is replaced, so the markup only appears where the component puts it, and it keeps working in a static prototype.

### Leave a slot out

Two special values control a slot. The no-operation token `_` keeps the component's own markup, which makes that markup a default. The empty fragment `~{}` renders nothing:

```html title="Template"
<div th:replace="~{components/ui :: panel('Newsletter', ~{:: #signup}, _)}">
  <p id="signup">Sign up at the till.</p>
</div>
<div th:replace="~{components/ui :: panel('Newsletter', ~{:: #signup2}, ~{})}">
  <p id="signup2">Sign up at the till.</p>
</div>
```

```html title="Output"
<section class="panel">
  <h2>Newsletter</h2>
  <div class="panel-body"><p id="signup">Sign up at the till.</p></div>
  <footer>Default footer</footer>
</section>
<section class="panel">
  <h2>Newsletter</h2>
  <div class="panel-body"><p id="signup2">Sign up at the till.</p></div>
</section>
```

## Insert a component conditionally

The same two values work with a conditional expression. Use `~{}` to insert nothing if the condition isn't met:

```html title="Template"
<div th:insert="${product.inStock} ? ~{components/ui :: badge('In stock')} : ~{}"></div>
<div th:insert="${noProducts.isEmpty()} ? _ : ~{components/ui :: badge('In stock')}">Nothing to show</div>
```

```html title="Output"
<div><span class="badge">In stock</span></div>
<div>Nothing to show</div>
```

If your template resolvers have `checkExistence` turned on, you can also test whether a fragment exists, and fall back to the existing markup:

```html
<div th:insert="~{common :: salutation} ?: _">
  Welcome [[${user.name}]]
</div>
```

## Common mistakes

- **Using the wrong number of parameters:** a fragment with a parameter list has no optional parameters. See [Optional parameters](#optional-parameters).
- **Expecting isolation:** fragments see the caller's variables, so a typo in a parameter name can silently read an unrelated variable.
- **Passing untrusted fragment names:** fragment expressions are evaluated, so never build one from user input. See [Escaping and XSS](../../security/escaping-and-xss/#dont-build-expressions-from-user-input).
- **Unwrapped syntax:** `th:replace="components/ui :: badge('New')"` without `~{...}` is deprecated, and Thymeleaf logs a warning.

## Related pages

- [Fragments](../fragments/)
- [Layouts](../layouts/)
- [`th:fragment` in the attributes reference](../../reference/attributes/#th-fragment)

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Parameterizable fragment signatures](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#parameterizable-fragment-signatures), [Flexible layouts: beyond mere fragment insertion](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#flexible-layouts-beyond-mere-fragment-insertion).*

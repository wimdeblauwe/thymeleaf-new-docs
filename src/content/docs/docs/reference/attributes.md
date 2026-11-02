---
title: "Attributes"
description: "Every common th: attribute in the Standard Dialect, with its value, precedence and rendered output."
sidebar:
  order: 1
---

This page covers the Standard Dialect's attributes. For `th:field`, `th:errors` and `th:errorclass`, see [Forms](../../spring/forms/).

**Precedence** is the processor's number in the Thymeleaf source. Lower numbers run first, whatever order you write the attributes in. See [Attribute precedence](../attribute-precedence/).

**Since** appears only where the Thymeleaf changelog records when an attribute arrived. The other attributes are older than the changelog's records, or their history isn't documented.

All examples run against Thymeleaf 3.1.5. `product` is a record with a `name`, a `price` and an `inStock` flag.

## Text

<a id="th-text"></a>

### th:text

Replaces the element's body with the value, HTML-escaped.

**Value:** any expression. A null value gives an empty body.\
**Precedence:** 1300

```html title="Template"
<p th:text="${comment}">Placeholder</p>
<p th:text="${missing}">Placeholder</p>
```

```html title="Output"
<p>&lt;b&gt;Tasty&lt;/b&gt; &amp; fresh</p>
<p></p>
```

**Related:** [`th:utext`](#th-utext), [Inlining](../../templates/inlining/)

<a id="th-utext"></a>

### th:utext

Replaces the element's body with the value, **without escaping**.

:::danger
Never use `th:utext` with a value that a user can influence. It writes HTML straight into the page, which allows cross-site scripting. See [Escaping and XSS](../../security/escaping-and-xss/).
:::

**Value:** any expression, evaluated in [restricted mode](../../security/expression-restrictions/)\
**Precedence:** 1400

```html title="Template"
<p th:utext="${description}">Placeholder</p>
```

```html title="Output"
<p><em>Grown</em> nearby</p>
```

**Related:** [`th:text`](#th-text)

## Setting attributes

<a id="th-attr"></a>

### th:attr

Sets attributes by name. Prefer a specific attribute such as `th:title`, which reads better.

**Value:** comma-separated `name=expression` pairs\
**Precedence:** 700

```html title="Template"
<img src="placeholder.png" th:attr="alt=${product.name},title=${product.name}">
```

```html title="Output"
<img src="placeholder.png" alt="Fresh sweet basil" title="Fresh sweet basil">
```

Attribute names containing `@` or `:` don't parse here. See [Interactive UIs](../../interactive-uis/overview/#set-alpinejs-attributes-from-the-server).

<a id="th-attrprepend"></a>
<a id="th-attrappend"></a>

### th:attrprepend, th:attrappend

Add text before or after an attribute's current value, without adding a space.

**Value:** `name=expression` pairs\
**Precedence:** 800 for `th:attrprepend`, 900 for `th:attrappend`

```html title="Template"
<input class="field" th:attrappend="class=${' large'}" th:attrprepend="class=${'wide '}">
```

```html title="Output"
<input class="wide field large">
```

<a id="th-classappend"></a>

### th:classappend

Adds a class to the element, inserting the space for you.

**Value:** expression. A null or empty value leaves the class unchanged.\
**Precedence:** 1100

```html title="Template"
<li class="product" th:classappend="${product.inStock} ? 'available' : 'sold-out'">Basil</li>
<li class="product" th:classappend="${missing}">Basil</li>
```

```html title="Output"
<li class="product available">Basil</li>
<li class="product">Basil</li>
```

<a id="th-styleappend"></a>

### th:styleappend

Adds a declaration to the `style` attribute. Thymeleaf inserts a space but no semicolon, so end the existing value with one.

**Value:** expression\
**Precedence:** 1100\
**Since:** 2.1.3

```html title="Template"
<p style="margin: 0;" th:styleappend="|color: ${colour}|">Basil</p>
```

```html title="Output"
<p style="margin: 0; color: red">Basil</p>
```

<a id="th-href"></a>
<a id="th-src"></a>

### th:href, th:src

Set a URL attribute. Use a [link expression](../../templates/links-and-urls/), which adds the context path and encodes parameters.

**Value:** usually `@{...}`, evaluated in restricted mode\
**Precedence:** 1000

```html title="Template"
<a href="product.html" th:href="@{/products/{name}(name=${product.name},page=2)}">View</a>
```

```html title="Output"
<a href="/products/Fresh%20sweet%20basil?page=2">View</a>
```

:::caution
Thymeleaf doesn't validate URLs. Validate a user-supplied URL in your application before you output it. See [URLs](../../security/escaping-and-xss/#urls).
:::

<a id="th-value"></a>

### th:value

Sets the `value` attribute.

**Value:** any expression\
**Precedence:** 1000 in the Standard Dialect, 1010 in the SpringStandard dialect

```html title="Template"
<input type="text" value="Placeholder" th:value="${product.name}">
```

```html title="Output"
<input type="text" value="Fresh sweet basil">
```

<a id="th-alt-title"></a>
<a id="th-lang-xmllang"></a>

### th:alt-title, th:lang-xmllang

Set two attributes to the same value: `alt` and `title`, or `lang` and `xml:lang`.

**Value:** any expression\
**Precedence:** 990

```html title="Template"
<img src="basil.png" th:alt-title="${product.name}">
```

```html title="Output"
<img src="basil.png" alt="Fresh sweet basil" title="Fresh sweet basil">
```

### th:*, any other attribute

If no processor exists for a name, the default attribute processor sets the attribute of that name. This is how `th:data-*` and `th:hx-*` work.

**Value:** any expression, evaluated in restricted mode. A null or empty value removes the attribute.\
**Precedence:** runs last of all attribute processors

```html title="Template"
<li th:data-sku="${product.name}" th:data-note="${missing}">Basil</li>
```

```html title="Output"
<li data-sku="Fresh sweet basil">Basil</li>
```

### Specific attributes

Each of these sets the HTML attribute of the same name:

|  |  |  |
| --- | --- | --- |
| `th:abbr` | `th:accept` | `th:accept-charset` |
| `th:accesskey` | `th:action` | `th:align` |
| `th:alt` | `th:archive` | `th:audio` |
| `th:autocomplete` | `th:axis` | `th:background` |
| `th:bgcolor` | `th:border` | `th:cellpadding` |
| `th:cellspacing` | `th:challenge` | `th:charset` |
| `th:cite` | `th:class` | `th:classid` |
| `th:codebase` | `th:codetype` | `th:cols` |
| `th:colspan` | `th:compact` | `th:content` |
| `th:contenteditable` | `th:contextmenu` | `th:data` |
| `th:datetime` | `th:dir` | `th:draggable` |
| `th:dropzone` | `th:enctype` | `th:for` |
| `th:form` | `th:formaction` | `th:formenctype` |
| `th:formmethod` | `th:formtarget` | `th:fragment` |
| `th:frame` | `th:frameborder` | `th:headers` |
| `th:height` | `th:high` | `th:href` |
| `th:hreflang` | `th:hspace` | `th:http-equiv` |
| `th:icon` | `th:id` | `th:inline` |
| `th:keytype` | `th:kind` | `th:label` |
| `th:lang` | `th:list` | `th:longdesc` |
| `th:low` | `th:manifest` | `th:marginheight` |
| `th:marginwidth` | `th:max` | `th:maxlength` |
| `th:media` | `th:method` | `th:min` |
| `th:name` | `th:onabort` | `th:onafterprint` |
| `th:onbeforeprint` | `th:onbeforeunload` | `th:onblur` |
| `th:oncanplay` | `th:oncanplaythrough` | `th:onchange` |
| `th:onclick` | `th:oncontextmenu` | `th:ondblclick` |
| `th:ondrag` | `th:ondragend` | `th:ondragenter` |
| `th:ondragleave` | `th:ondragover` | `th:ondragstart` |
| `th:ondrop` | `th:ondurationchange` | `th:onemptied` |
| `th:onended` | `th:onerror` | `th:onfocus` |
| `th:onformchange` | `th:onforminput` | `th:onhashchange` |
| `th:oninput` | `th:oninvalid` | `th:onkeydown` |
| `th:onkeypress` | `th:onkeyup` | `th:onload` |
| `th:onloadeddata` | `th:onloadedmetadata` | `th:onloadstart` |
| `th:onmessage` | `th:onmousedown` | `th:onmousemove` |
| `th:onmouseout` | `th:onmouseover` | `th:onmouseup` |
| `th:onmousewheel` | `th:onoffline` | `th:ononline` |
| `th:onpause` | `th:onplay` | `th:onplaying` |
| `th:onpopstate` | `th:onprogress` | `th:onratechange` |
| `th:onreadystatechange` | `th:onredo` | `th:onreset` |
| `th:onresize` | `th:onscroll` | `th:onseeked` |
| `th:onseeking` | `th:onselect` | `th:onshow` |
| `th:onstalled` | `th:onstorage` | `th:onsubmit` |
| `th:onsuspend` | `th:ontimeupdate` | `th:onundo` |
| `th:onunload` | `th:onvolumechange` | `th:onwaiting` |
| `th:optimum` | `th:pattern` | `th:placeholder` |
| `th:poster` | `th:preload` | `th:radiogroup` |
| `th:rel` | `th:rev` | `th:rows` |
| `th:rowspan` | `th:rules` | `th:sandbox` |
| `th:scheme` | `th:scope` | `th:scrolling` |
| `th:size` | `th:sizes` | `th:span` |
| `th:spellcheck` | `th:src` | `th:srclang` |
| `th:standby` | `th:start` | `th:step` |
| `th:style` | `th:summary` | `th:tabindex` |
| `th:target` | `th:title` | `th:type` |
| `th:usemap` | `th:value` | `th:valuetype` |
| `th:vspace` | `th:width` | `th:wrap` |
| `th:xmlbase` | `th:xmllang` | `th:xmlspace` |

Some of these, specifically `th:href`, `th:src` and all the `th:on*` event handler attributes, are subject to stricter expression evaluation for security reasons. See [Expression restrictions](../../security/expression-restrictions/).

### Fixed-value boolean attributes

These write the attribute when the expression is true, and remove it when false. The test follows the [`th:if` rules](#th-if).

**Precedence:** 1000

```html title="Template"
<input type="checkbox" th:checked="${product.inStock}">
<input type="text" th:disabled="${missing}">
```

```html title="Output"
<input type="checkbox" checked="checked">
<input type="text">
```

|  |  |  |
| --- | --- | --- |
| `th:async` | `th:autofocus` | `th:autoplay` |
| `th:checked` | `th:controls` | `th:declare` |
| `th:default` | `th:defer` | `th:disabled` |
| `th:formnovalidate` | `th:hidden` | `th:ismap` |
| `th:loop` | `th:multiple` | `th:novalidate` |
| `th:nowrap` | `th:open` | `th:pubdate` |
| `th:readonly` | `th:required` | `th:reversed` |
| `th:scoped` | `th:seamless` | `th:selected` |

## Conditionals

<a id="th-if"></a>

### th:if

Keeps the element if the value is true, and removes it with its children if not.

**Value:** any expression\
**Precedence:** 300

A value is false if it's null, the boolean `false`, a number equal to zero, a zero character, or the text `false`, `off` or `no` in any case. Everything else is true, **including an empty string and an empty list**:

```html title="Template"
<p th:if="${missing}">Null</p>
<p th:if="'off'">The text off</p>
<p th:if="0">Zero</p>
<p th:if="${noProducts}">An empty list</p>
<p th:if="''">An empty string</p>
<p th:if="${not noProducts.isEmpty()}">A list with items</p>
```

```html title="Output"
<p>An empty list</p>
<p>An empty string</p>
```

**Related:** [`th:unless`](#th-unless), [Conditionals](../../templates/conditionals/)

<a id="th-unless"></a>

### th:unless

The opposite of `th:if`.

**Value:** any expression\
**Precedence:** 400

```html title="Template"
<p th:unless="${product.inStock}">Sold out</p>
<p th:unless="${noProducts.size() > 0}">No products yet</p>
```

```html title="Output"
<p>No products yet</p>
```

<a id="th-switch"></a>
<a id="th-case"></a>

### th:switch, th:case

`th:switch` holds a value, and child elements with `th:case` compare against it. The first match wins. `th:case="*"` is the default, and has to come last.

**Value:** any expression\
**Precedence:** 250 for `th:switch`, 275 for `th:case`\
**Since:** 2.0.0

```html title="Template"
<div th:switch="${role}">
  <p th:case="'admin'">Administrator</p>
  <p th:case="'manager'">Store manager</p>
  <p th:case="*">Customer</p>
</div>
```

```html title="Output"
<div>
  <p>Store manager</p>
</div>
```

## Iteration

<a id="th-each"></a>

### th:each

Repeats the element for each item. Attributes on the same element can use the item, because `th:each` runs before them.

**Value:** `item : ${collection}` or `item, status : ${collection}`\
**Precedence:** 200

The status variable has `index`, `count`, `size`, `current`, `even`, `odd`, `first` and `last`.

```html title="Template"
<ul>
  <li th:each="product, stat : ${products}"
      th:text="|${stat.count} of ${stat.size}: ${product.name}|">Placeholder</li>
</ul>
```

```html title="Output"
<ul>
  <li>1 of 2: Fresh sweet basil</li>
  <li>2 of 2: Italian tomato</li>
</ul>
```

Iterating over a map gives entries with a `key` and a `value`. A null collection gives no iterations.

```html title="Template"
<p th:each="entry : ${prices}" th:text="|${entry.key}: ${entry.value}|">Placeholder</p>
<p th:each="item : ${missing}">Never rendered</p>
```

```html title="Output"
<p>basil: 4.99</p>
<p>tomato: 1.25</p>
```

**Related:** [`th:block`](#th-block), [Iteration](../../templates/iteration/)

## Local variables

<a id="th-with"></a>

### th:with

Defines variables for the element and its children. Later variables can use earlier ones.

**Value:** comma-separated `name=expression` pairs\
**Precedence:** 600

```html title="Template"
<p th:with="first=${products[0]},label=${first.name}" th:text="${label}">Placeholder</p>
```

```html title="Output"
<p>Fresh sweet basil</p>
```

<a id="th-object"></a>

### th:object

Selects an object, so `*{...}` expressions inside the element read from it.

**Value:** an expression that gives an object\
**Precedence:** 500

```html title="Template"
<div th:object="${product}">
  <p th:text="*{name}">Placeholder</p>
</div>
```

```html title="Output"
<div>
  <p>Fresh sweet basil</p>
</div>
```

## Fragments

<a id="th-fragment"></a>

### th:fragment

Names an element, so other templates can include it. It can declare parameters.

**Value:** a name, optionally with a parameter list\
**Precedence:** 1500

See [Components](../../templates/components/).

<a id="th-insert"></a>

### th:insert

Keeps the host element and puts the fragment inside it.

**Value:** a fragment expression, `~{template :: selector}`. The value is evaluated in restricted mode.\
**Precedence:** 100

```html title="Template"
<div th:insert="~{components/ui :: badge('In stock')}"></div>
```

```html title="Output"
<div><span class="badge">In stock</span></div>
```

<a id="th-replace"></a>

### th:replace

Replaces the host element with the fragment.

**Value:** a fragment expression, evaluated in restricted mode\
**Precedence:** 100

```html title="Template"
<div th:replace="~{components/ui :: badge('In stock')}"></div>
```

```html title="Output"
<span class="badge">In stock</span>
```

<a id="th-include"></a>

### th:include

Deprecated. Thymeleaf 3.1 logs a warning when it runs, and the source says it will be removed in version 3.2 or 4.0. Use [`th:insert`](#th-insert).

**Precedence:** 100

<a id="th-remove"></a>

### th:remove

Removes parts of the markup when Thymeleaf processes the file.

**Value:** `all`, `body`, `tag`, `all-but-first` or `none`, or an expression that gives one of them\
**Precedence:** 1600

```html title="Template"
<ul th:remove="body"><li>Removed</li></ul>
<p th:remove="all">Removed</p>
<div th:remove="tag"><p>The div is removed</p></div>
<ul th:remove="all-but-first"><li>Kept</li><li>Removed</li></ul>
<p th:remove="none">Kept</p>
```

```html title="Output"
<ul></ul>
<p>The div is removed</p>
<ul><li>Kept</li></ul>
<p>Kept</p>
```

<a id="th-assert"></a>

### th:assert

Fails template processing unless every expression is true. It's useful for checking a fragment's parameters.

**Value:** comma-separated expressions\
**Precedence:** 1550\
**Since:** 2.1.0

```html title="Rejected"
<p th:assert="${product.inStock},${missing}">Placeholder</p>
```

## Other

<a id="th-block"></a>

### th:block

An element, not an attribute. It runs its attributes, and then disappears from the output, which is useful for repeating several sibling elements.

**Since:** 2.1.0

```html title="Template"
<dl>
  <th:block th:each="product : ${products}">
    <dt th:text="${product.name}">Name</dt>
    <dd th:text="${product.price}">0.00</dd>
  </th:block>
</dl>
```

```html title="Output"
<dl>
  <dt>Fresh sweet basil</dt>
  <dd>4.99</dd>
  <dt>Italian tomato</dt>
  <dd>1.25</dd>
</dl>
```

<a id="th-inline"></a>

### th:inline

Sets the inlining mode for the element's body.

**Value:** `text`, `javascript`, `css` or `none`\
**Precedence:** 1000

```html title="Template"
<p th:inline="none">[[${product.name}]]</p>
<script th:inline="javascript">
  const name = [[${product.name}]];
</script>
```

```html title="Output"
<p>[[${product.name}]]</p>
<script>
  const name = "Fresh sweet basil";
</script>
```

**Related:** [Inlining](../../templates/inlining/)

<a id="th-action"></a>
<a id="th-method"></a>

### th:action, th:method

Set a form's `action` and `method`. In a Spring application, `th:action` also adds the CSRF field, and `th:method` handles HTTP methods that browsers can't send. See [Forms](../../spring/forms/).

**Precedence:** 1000 for `th:action`. 1000 for `th:method` in the Standard Dialect, 990 in the SpringStandard dialect.

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Setting value to specific attributes](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#setting-value-to-specific-attributes), [Fixed-value boolean attributes](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#fixed-value-boolean-attributes).*

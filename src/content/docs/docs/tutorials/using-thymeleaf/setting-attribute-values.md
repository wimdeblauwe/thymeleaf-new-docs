---
title: "Setting Attribute Values"
description: "This chapter will explain the way in which we can set (or modify) values of attributes in our markup."
sidebar:
  order: 5
---

This chapter will explain the way in which we can set (or modify) values of
attributes in our markup.

## Setting the value of any attribute

Say our website publishes a newsletter, and we want our users to be able to
subscribe to it, so we create a `/WEB-INF/templates/subscribe.html` template
with a form:

```html
<form action="subscribe.html">
  <fieldset>
    <input type="text" name="email" />
    <input type="submit" value="Subscribe!" />
  </fieldset>
</form>
```

As with Thymeleaf, this template starts off more like a static prototype than it
does a template for a web application.  First, the `action` attribute in our
form statically links to the template file itself, so that there is no place
for useful URL rewriting. Second, the `value` attribute in the submit button makes
it display a text in English, but we'd like it to be internationalized.

Enter then the `th:attr` attribute, and its ability to change the value of
attributes of the tags it is set in:

```html
<form action="subscribe.html" th:attr="action=@{/subscribe}">
  <fieldset>
    <input type="text" name="email" />
    <input type="submit" value="Subscribe!" th:attr="value=#{subscribe.submit}"/>
  </fieldset>
</form>
```

The concept is quite straightforward: `th:attr` simply takes an expression that
assigns a value to an attribute. Having created the corresponding controller and
messages files, the result of processing this file will be:

```html
<form action="/gtvg/subscribe">
  <fieldset>
    <input type="text" name="email" />
    <input type="submit" value="¡Suscríbe!"/>
  </fieldset>
</form>
```

Besides the new attribute values, you can also see that the application context
name has been automatically prefixed to the URL base in `/gtvg/subscribe`, as
explained in the previous chapter.

But what if we wanted to set more than one attribute at a time? XML rules do not
allow you to set an attribute twice in a tag, so `th:attr` will take a
comma-separated list of assignments, like:

```html
<img src="../../images/gtvglogo.png" 
     th:attr="src=@{/images/gtvglogo.png},title=#{logo},alt=#{logo}" />
```

Given the required messages files, this will output:

```html
<img src="/gtgv/images/gtvglogo.png" title="Logo de Good Thymes" alt="Logo de Good Thymes" />
```

## Setting value to specific attributes

By now, you might be thinking that something like:

```html
<input type="submit" value="Subscribe!" th:attr="value=#{subscribe.submit}"/>
```

...is quite an ugly piece of markup. Specifying an assignment inside an
attribute's value can be very practical, but it is not the most elegant way of
creating templates if you have to do it all the time.

Thymeleaf agrees with you, and that's why `th:attr` is scarcely used in
templates. Normally, you will be using other `th:*` attributes whose task is
setting specific tag attributes (and not just any attribute like `th:attr`).

For example, to set the `value` attribute, use `th:value`:

```html
<input type="submit" value="Subscribe!" th:value="#{subscribe.submit}"/>
```

This looks much better! Let's try and do the same to the `action` attribute in
the `form` tag:

```html
<form action="subscribe.html" th:action="@{/subscribe}">
```

And do you remember those `th:href` we put in our `home.html` before? They are
exactly this same kind of attributes:

```html
<li><a href="product/list.html" th:href="@{/product/list}">Product List</a></li>
```

There are quite a lot of attributes like these, each of them targeting a
specific HTML5 attribute:

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

> Note that some of the attributes listed above — specifically `th:href`,
> `th:src`, and all the `th:on*` event handler attributes — are subject to
> stricter expression evaluation restrictions for security reasons. See
> [Appendix D: Expression Restrictions](../appendix-d-expression-restrictions/).

## Setting more than one value at a time

There are two rather special attributes called `th:alt-title` and `th:lang-xmllang`
which can be used for setting two attributes to the same value at the same time.
Specifically:

 * `th:alt-title` will set `alt` and `title`. 
 * `th:lang-xmllang` will set `lang` and `xml:lang`.

For our GTVG home page, this will allow us to substitute this:

```html
<img src="../../images/gtvglogo.png" 
     th:attr="src=@{/images/gtvglogo.png},title=#{logo},alt=#{logo}" />
```

...or this, which is equivalent:

```html
<img src="../../images/gtvglogo.png" 
     th:src="@{/images/gtvglogo.png}" th:title="#{logo}" th:alt="#{logo}" />
```

...with this:

```html
<img src="../../images/gtvglogo.png" 
     th:src="@{/images/gtvglogo.png}" th:alt-title="#{logo}" />
```

## Appending and prepending

Thymeleaf also offers the `th:attrappend` and `th:attrprepend` attributes, which
append (suffix) or prepend (prefix) the result of their evaluation to the
existing attribute values.

For example, you might want to store the name of a CSS class to be added (not
set, just added) to one of your buttons in a context variable, because the
specific CSS class to be used would depend on something that the user did before:

```html
<input type="button" value="Do it!" class="btn" th:attrappend="class=${' ' + cssStyle}" />
```

If you process this template with the `cssStyle` variable set to `"warning"`,
you will get:

```html
<input type="button" value="Do it!" class="btn warning" />
```

There are also two specific _appending attributes_ in the Standard Dialect: the
`th:classappend` and `th:styleappend` attributes, which are used for adding a
CSS class or a fragment of _style_ to an element without overwriting the
existing ones:

```html
<tr th:each="prod : ${prods}" class="row" th:classappend="${prodStat.odd}? 'odd'">
```

(Don't worry about that `th:each` attribute. It is an _iterating attribute_ and
we will talk about it later.)

## Fixed-value boolean attributes

HTML has the concept of _boolean attributes_, attributes that have no value and
the presence of one means that value is "true".  In XHTML, these attributes
take just 1 value, which is itself.

For example, `checked`:

```html
<input type="checkbox" name="option2" checked /> <!-- HTML -->
<input type="checkbox" name="option1" checked="checked" /> <!-- XHTML -->
```

The Standard Dialect includes attributes that allow you to set these attributes
by evaluating a condition, so that if evaluated to true, the attribute will be
set to its fixed value, and if evaluated to false, the attribute will not be set:

```html
<input type="checkbox" name="active" th:checked="${user.active}" />
```

The following fixed-value boolean attributes exist in the Standard Dialect:

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

## Setting the value of any attribute (default attribute processor)

Thymeleaf offers a *default attribute processor* that allows us to set the value
of *any* attribute, even if no specific `th:*` processor has been defined for it
at the Standard Dialect.

So something like:

```html
<span th:whatever="${user.name}">...</span>
```

Will result in:

```html
<span whatever="John Apricot">...</span>
```

## Support for HTML5-friendly attribute and element names

It is also possible to use a completely different syntax to apply processors to
your templates in a more HTML5-friendly manner.

```html	
<table>
    <tr data-th-each="user : ${users}">
        <td data-th-text="${user.login}">...</td>
        <td data-th-text="${user.name}">...</td>
    </tr>
</table>
```

The `data-{prefix}-{name}` syntax is the standard way to write custom attributes
in HTML5, without requiring developers to use any namespaced names like `th:*`.
Thymeleaf makes this syntax automatically available to all your dialects (not
only the Standard ones).

There is also a syntax to specify custom tags: `{prefix}-{name}`, which follows
the _W3C Custom Elements specification_ (a part of the larger _W3C Web
Components spec_). This can be used, for example, for the `th:block` element (or
also `th-block`), which will be explained in a later section. 

**Important:** this syntax is an addition to the namespaced `th:*` one, it does
not replace it. There is no intention at all to deprecate the namespaced syntax
in the future. 

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#setting-attribute-values) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

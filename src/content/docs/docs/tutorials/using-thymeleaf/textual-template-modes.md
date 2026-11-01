---
title: "Textual template modes"
description: "Three of the Thymeleaf template modes are considered textual: TEXT, JAVASCRIPT and CSS."
sidebar:
  order: 13
---

## Textual syntax

Three of the Thymeleaf *template modes* are considered **textual**: `TEXT`, `JAVASCRIPT`
and `CSS`. This differentiates them from the markup template modes: `HTML` and `XML`.

The key difference between *textual* template modes and the markup ones is that
in a textual template there are no tags into which to insert logic in the form
of attributes, so we have to rely on other mechanisms.

The first and most basic of these mechanisms is **inlining**, which we have
already detailed in the previous chapter. Inlining syntax is the most simple way
to output results of expressions in textual template mode, so this is a
perfectly valid template for a text email.

```
  Dear [(${name})],

  Please find attached the results of the report you requested
  with name "[(${report.name})]".

  Sincerely,
    The Reporter.
```

Even without tags, the example above is a complete and valid Thymeleaf template
that can be executed in the `TEXT` template mode.

But in order to include more complex logic than mere *output expressions*, we
need a new non-tag-based syntax:

```
[# th:each="item : ${items}"]
  - [(${item})]
[/]
```

Which is actually the *condensed* version of the more verbose:

```
[#th:block th:each="item : ${items}"]
  - [#th:block th:utext="${item}" /]
[/th:block]
```

Note how this new syntax is based on elements (i.e. processable tags) that are
declared as `[#element ...]` instead of `<element ...>`. Elements are open like
`[#element ...]` and closed like `[/element]`, and standalone tags can be
declared by minimizing the open element with a `/` in a way almost equivalent to
XML tags: `[#element ... /]`.

The Standard Dialect only contains a processor for one of these elements: the
already-known `th:block`, though we could extend this in our dialects and create
new elements in the usual way. Also, the `th:block` element (`[#th:block ...] ... [/th:block]`)
is allowed to be abbreviated as the empty string (`[# ...] ... [/]`), so the
above block is actually equivalent to:

```
[# th:each="item : ${items}"]
  - [# th:utext="${item}" /]
[/]
```

And given `[# th:utext="${item}" /]` is equivalent to an *inlined unescaped
expression*, we could just use it in order to have less code. Thus we end up
with the first fragment of code we saw above:

```
[# th:each="item : ${items}"]
  - [(${item})]
[/]
```

Note that the *textual syntax requires full element balance (no unclosed tags)
and quoted attributes* -- it's more XML-style than HTML-style.

Let's have a look at a more complete example of a `TEXT` template, a *plain text*
email template:

```
Dear [(${customer.name})],

This is the list of our products:

[# th:each="prod : ${products}"]
   - [(${prod.name})]. Price: [(${prod.price})] EUR/kg
[/]

Thanks,
  The Thymeleaf Shop
```

After executing, the result of this could be something like:

```
Dear Mary Ann Blueberry,

This is the list of our products:


   - Apricots. Price: 1.12 EUR/kg

   - Bananas. Price: 1.78 EUR/kg

   - Apples. Price: 0.85 EUR/kg

   - Watermelon. Price: 1.91 EUR/kg


Thanks,
  The Thymeleaf Shop
```

Note that `[# th:each="..."]` and `[/]` each occupy their own line in the template, and the
newline at the end of each of those lines is part of the surrounding text and is therefore included
in the output. This means the `[# ...]` line contributes an extra blank line before the first item,
each iteration boundary contributes a blank line between items, and the `[/]` line contributes an
extra blank line before "Thanks,". If compact output is needed, the tags can be placed at the end
of adjacent content lines rather than on lines of their own.

And another example in `JAVASCRIPT` template mode, a `greeter.js` file, we
process as a textual template and which result we call from our HTML pages. Note
this is *not* a `<script>` block in an HTML template, but a `.js` file being
processed as a template on its own:

```javascript
var greeter = function() {

    var username = [[${session.user.name}]];

    [# th:each="salut : ${salutations}"]    
      alert([[${salut}]] + " " + username);
    [/]

};
```

After executing, the result of this could be something like:

```javascript
var greeter = function() {

    var username = "Bertrand \"Crunchy\" Pear";

      alert("Hello" + " " + username);
      alert("Ol\u00E1" + " " + username);
      alert("Hola" + " " + username);

};
```

> Note that the `TEXT` template mode is subject to stricter expression evaluation restrictions
> for security reasons. See [Appendix D: Expression Restrictions](../appendix-d-expression-restrictions/).

### Escaped element attributes

In order to avoid interactions with parts of the template that might be
processed in other modes (e.g. `text`-mode inlining inside an `HTML` template),
Thymeleaf 3.0 allows the attributes in elements in its *textual syntax* to be
escaped. So:

 * Attributes in `TEXT` template mode will be *HTML-unescaped*.
 * Attributes in `JAVASCRIPT` template mode will be *JavaScript-unescaped*.
 * Attributes in `CSS` template mode will be *CSS-unescaped*.

So this would be perfectly OK in a `TEXT`-mode template (note the `&gt;`):
```
  [# th:if="${120&lt;user.age}"]
     Congratulations!
  [/]
```

Of course that `&lt;` would make no sense in a *real text* template, but it is a
good idea if we are processing an HTML template with a `th:inline="text"` block
containing the code above and we want to make sure our browser doesn't take that
`<user.age` for the name of an open tag when statically opening the file as a
prototype.

## Extensibility

One of the advantages of this syntax is that it is just as extensible as the 
*markup* one. Developers can still define their own dialects with custom
elements and attributes, apply a prefix to them (optionally), and then use them
in textual template modes:

```
  [#myorg:dosomething myorg:importantattr="211"]some text[/myorg:dosomething]
```

## Textual prototype-only comment blocks: adding code

The `JAVASCRIPT` and `CSS` template modes (not available for `TEXT`) allow 
including code between a special comment syntax `/*[+...+]*/` so that Thymeleaf
will automatically uncomment such code when processing the template:

```javascript
var x = 23;

/*[+

var msg  = "This is a working application";

+]*/

var f = function() {
    ...
```

Will be executed as:

```javascript
var x = 23;

var msg  = "This is a working application";

var f = function() {
...
```

You can include expressions inside these comments, and they will be evaluated:

```javascript
var x = 23;

/*[+

var msg  = "Hello, " + [[${session.user.name}]];

+]*/

var f = function() {
...
```

## Textual parser-level comment blocks: removing code

In a way similar to that of prototype-only comment blocks, all the three textual
template modes (`TEXT`, `JAVASCRIPT` and `CSS`) make it possible to instruct
Thymeleaf to remove code between special `/*[- */` and `/* -]*/` marks, like
this:

```javascript
var x = 23;

/*[- */

var msg  = "This is shown only when executed statically!";

/* -]*/

var f = function() {
...
```

Or this, in `TEXT` mode:

```
...
/*[- Note the user is obtained from the session, which must exist -]*/
Welcome [(${session.user.name})]!
...
```

## Natural JavaScript and CSS templates

As seen in the previous chapter, JavaScript and CSS inlining offer the
possibility to include inlined expressions inside JavaScript/CSS comments, like:

```javascript
...
var username = /*[[${session.user.name}]]*/ "Sebastian Lychee";
...
```

...which is valid JavaScript, and once executed could look like:

```html
...
var username = "John Apricot";
...
```

This same *trick* of enclosing inlined expressions inside comments can in fact be
used for the entire textual mode syntax:

```
  /*[# th:if="${user.admin}"]*/
     alert('Welcome admin');
  /*[/]*/
```

That alert in the code above will be shown when the template is open statically
-- because it is 100% valid JavaScript --, and also when the template is run if
the user is an admin. It is equivalent to:

```
  [# th:if="${user.admin}"]
     alert('Welcome admin');
  [/]
```

...which is actually the code to which the initial version is converted during
template parsing. 

Note however that wrapping elements in comments does not clean the lines they
live in (to the right until a `;` is found) as inlined output expressions do.
That behaviour is reserved for inlined output expressions only.

So Thymeleaf 3.0 allows the development of **complex JavaScript scripts and CSS
style sheets in the form of natural templates**, valid both as a *prototype* and
as a *working template*.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#textual-template-modes) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

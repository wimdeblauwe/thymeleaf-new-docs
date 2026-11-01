---
title: "Inlining"
description: "Although the Standard Dialect allows us to do almost everything using tag attributes, there are situations in which we could prefer writing expressions directly into our HTML texts."
sidebar:
  order: 11
---

## Expression inlining

Although the Standard Dialect allows us to do almost everything using tag
attributes, there are situations in which we could prefer writing expressions
directly into our HTML texts. For example, we could prefer writing this:

```html
<p>Hello, [[${session.user.name}]]!</p>
```

...instead of this:

```html
<p>Hello, <span th:text="${session.user.name}">Sebastian</span>!</p>
```

Expressions between `[[...]]` or `[(...)]` are considered **inlined expressions**
in Thymeleaf, and inside them we can use any kind of expression that would also
be valid in a `th:text` or `th:utext` attribute.

Note that, while `[[...]]` corresponds to `th:text` (i.e. result will be *HTML-escaped*), 
`[(...)]` corresponds to `th:utext` and will not perform any HTML-escaping. So
with a variable such as `msg = 'This is <b>great!</b>'`, given this fragment:

```html
<p>The message is "[(${msg})]"</p>
```

The result will have those `<b>` tags unescaped, so:

```html
<p>The message is "This is <b>great!</b>"</p>
```

Whereas if escaped like:

```html
<p>The message is "[[${msg}]]"</p>
```

The result will be HTML-escaped:

```html
<p>The message is "This is &lt;b&gt;great!&lt;/b&gt;"</p>
```

Note that **text inlining is active by default** in the body of every tag in our
markup –- not the tags themselves -–, so there is nothing we need to do to
enable it.

### Inlining vs natural templates

If you come from other template engines in which this way of outputting text is
the norm, you might be asking: _Why aren't we doing this from the beginning?
It's less code than all those_ `th:text` _attributes!_ 

Well, be careful there, because although you might find inlining quite 
interesting, you should always remember that inlined expressions will be 
displayed verbatim in your HTML files when you open them statically, so you 
probably won't be able to use them as design prototypes anymore!

The difference between how a browser would statically display our fragment of
code without using inlining...

```
Hello, Sebastian!
```

...and using it...

```
Hello, [[${session.user.name}]]!
```

...is quite clear in terms of design usefulness.

### Disabling inlining

This mechanism can be disabled though, because there might actually be occasions
in which we do want to output the `[[...]]` or  `[(...)]` sequences without its
contents being processed as an expression. For that, we will use `th:inline="none"`:

```html
<p th:inline="none">A double array looks like this: [[1, 2, 3], [4, 5]]!</p>
```

This will result in:

```html
<p>A double array looks like this: [[1, 2, 3], [4, 5]]!</p>
```

## Text inlining

*Text inlining* is very similar to the *expression inlining* capability we have
just seen, but it actually adds more power. It has to be enabled explicitly with
`th:inline="text"`.

Text inlining not only allows us to use the same *inlined expressions* we just
saw, but in fact processes *tag bodies* as if they were templates processed in
the `TEXT` template mode, which allows us to perform text-based template logic
(not only output expressions).

We will see more about this in [Text, JavaScript and CSS templates](../text-javascript-css/).

## JavaScript inlining

JavaScript inlining allows for a better integration of JavaScript `<script>`
blocks in templates being processed in the `HTML` template mode.

As with *text inlining*, this is actually equivalent to processing the scripts
contents as if they were templates in the `JAVASCRIPT` template mode, and
therefore all the power of the *textual template modes* (see [Text, JavaScript and CSS templates](../text-javascript-css/)) will
be at hand. However, in this section we will focus on how we can use it for 
adding the output of our Thymeleaf expressions into our JavaScript blocks.

This mode has to be explicitly enabled using `th:inline="javascript"`:

```html
<script th:inline="javascript">
    ...
    var username = [[${session.user.name}]];
    ...
</script>
```

This will result in:

```html
<script th:inline="javascript">
    ...
    var username = "Sebastian \"Fruity\" Applejuice";
    ...
</script>
```

Two important things to note in the code above: 

*First*, that JavaScript inlining will not only output the required text, but 
also enclose it with quotes and JavaScript-escape its contents, so that the
expression results are output as a **well-formed JavaScript literal**.

*Second*, that this is happening because we are outputting the `${session.user.name}`
expression as **escaped**, i.e. using a double-bracket expression: `[[${session.user.name}]]`.
If instead we used *unescaped* like:

```html
<script th:inline="javascript">
    ...
    var username = [(${session.user.name})];
    ...
</script>
```

The result would look like:

```html
<script th:inline="javascript">
    ...
    var username = Sebastian "Fruity" Applejuice;
    ...
</script>
```

...which is malformed JavaScript code. But outputting something unescaped might
be what we need if we are building parts of our script by means of appending
inlined expressions, so it's good to have this tool at hand.

### JavaScript natural templates

The mentioned *intelligence* of the JavaScript inlining mechanism goes much
further than just applying JavaScript-specific escaping and outputting
expression results as valid literals.

For example, we can wrap our (escaped) inlined expressions in JavaScript
comments like:

```html
<script th:inline="javascript">
    ...
    var username = /*[[${session.user.name}]]*/ "Gertrud Kiwifruit";
    ...
</script>
```

And Thymeleaf will ignore everything we have written *after the comment and
before the semicolon* (in this case ` 'Gertrud Kiwifruit'`), so the result of
executing this will look exactly like when we were not using the wrapping
comments:

```html
<script th:inline="javascript">
    ...
    var username = "Sebastian \"Fruity\" Applejuice";
    ...
</script>
```

But have another careful look at the original template code:

```html
<script th:inline="javascript">
    ...
    var username = /*[[${session.user.name}]]*/ "Gertrud Kiwifruit";
    ...
</script>
```

Note how this is **valid JavaScript** code. And it will perfectly execute when
you open your template file in a static manner (without executing it at a
server).

So what we have here is a way to do **JavaScript natural templates**!

### Advanced inlined evaluation and JavaScript serialization

An important thing to note regarding JavaScript inlining is that this
expression evaluation is intelligent and not limited to Strings. Thymeleaf will
correctly write in JavaScript syntax the following kinds of objects:

 * Strings
 * Numbers
 * Booleans
 * Arrays
 * Collections
 * Maps
 * Beans (objects with _getter_ and _setter_ methods)

For example, if we had the following code:

```html
<script th:inline="javascript">
    ...
    var user = /*[[${session.user}]]*/ null;
    ...
</script>
```

That `${session.user}` expression will evaluate to a `User` object, and
Thymeleaf will correctly convert it to Javascript syntax:

```html
<script th:inline="javascript">
    ...
    var user = {"age":null,"firstName":"John","lastName":"Apricot",
                "name":"John Apricot","nationality":"Antarctica"};
    ...
</script>
```

The way this JavaScript serialization is done is by means of an implementation
of the `org.thymeleaf.standard.serializer.IStandardJavaScriptSerializer`
interface, which can be configured at the instance of the `StandardDialect`
being used at the template engine.

The default implementation of this JS serialization mechanism will look for the
[Jackson library](https://github.com/FasterXML/jackson) in the classpath and, if
present, will use it. If not, it will apply a built-in serialization mechanism
that covers the needs of most scenarios and produces similar results (but is
less flexible).

## CSS inlining

Thymeleaf also allows the use of inlining in CSS `<style>` tags, such as:

```html
<style th:inline="css">
  ...
</style>
```

For example, say we have two variables set to two different `String` values:

```
classname = 'main elems'
align = 'center'
```

We could use them just like:

```html
<style th:inline="css">
    .[[${classname}]] {
      text-align: [[${align}]];
    }
</style>
```

And the result would be:

```html
<style th:inline="css">
    .main\ elems {
      text-align: center;
    }
</style>
```

Note how CSS inlining also bears some *intelligence*, just like JavaScript's.
Specifically, expressions output via *escaped* expressions like `[[${classname}]]`
will be escaped as **CSS identifiers**. That is why our `classname = 'main elems'`
has turned into `main\ elems` in the fragment of code above.

### Advanced features: CSS natural templates, etc.

In an equivalent way to what was explained before for JavaScript, CSS inlining
also allows for our `<style>` tags to work both statically and dynamically, i.e.
 as **CSS natural templates** by means of wrapping inlined expressions in
 comments. See:

```html
<style th:inline="css">
    .main\ elems {
      text-align: /*[[${align}]]*/ left;
    }
</style>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#inlining) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

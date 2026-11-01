---
title: "Template Layout"
description: "In our templates, we will often want to include parts from other templates, parts like footers, headers, menus..."
sidebar:
  order: 8
---

## Including template fragments

### Defining and referencing fragments

In our templates, we will often want to include parts from other templates,
parts like footers, headers, menus...

In order to do this, Thymeleaf needs us to define these parts, "fragments", for
inclusion, which can be done using the `th:fragment` attribute. 

Say we want to add a standard copyright footer to all our grocery pages, so we
create a `/WEB-INF/templates/footer.html` file containing this code:

```html
<!DOCTYPE html>

<html xmlns:th="http://www.thymeleaf.org">

  <body>
  
    <div th:fragment="copy">
      &copy; 2011 The Good Thymes Virtual Grocery
    </div>
  
  </body>
  
</html>
```

The code above defines a fragment called `copy` that we can easily include in
our home page using one of the `th:insert` or `th:replace` attributes:

```html
<body>

  ...

  <div th:insert="~{footer :: copy}"></div>
  
</body>
```

Note that `th:insert` expects a *fragment expression* (`~{...}`), which is *an
expression that results in a fragment*.

### Fragment specification syntax

The syntax of *fragment expressions* is quite straightforward. There are three
different formats:

 * `"~{templatename::selector}"` Includes the fragment resulting from applying
   the specified Markup Selector on the template named `templatename`.  Note
   that `selector` can be a mere fragment name, so you could specify something
   as simple as `~{templatename::fragmentname}` like in the `~{footer :: copy}`
   above.

   > Markup Selector syntax is defined by the underlying AttoParser parsing
   > library, and is similar to XPath expressions or CSS selectors. See
   > [Appendix C](../appendix-c-markup-selector-syntax/) for more info.

 * `"~{templatename}"` Includes the complete template named `templatename`.

   > Note that the template name you use in `th:insert`/`th:replace` tags
   > will have to be resolvable by the Template Resolver currently being used by
   > the Template Engine.

 * `~{::selector}"` or `"~{this::selector}"` Inserts a fragment from the same
   template, matching `selector`. If not found on the template where the expression
   appears, the stack of template calls (insertions) is traversed towards the
   originally processed template (the *root*), until `selector` matches at 
   some level.

Both `templatename` and `selector` in the above examples can be fully-featured
expressions (even conditionals!) like:

```html
<div th:insert="~{ footer :: (${user.isAdmin}? #{footer.admin} : #{footer.normaluser}) }"></div>
```

Fragments can include any `th:*` attributes. These attributes will be evaluated
once the fragment is included into the target template (the one with the `th:insert`/`th:replace`
attribute), and they will be able to reference any context variables defined in
this target template.

> A big advantage of this approach to fragments is that you can write your
> fragments in pages that are perfectly displayable by a browser, with a
> complete and even *valid* markup structure, while still retaining the ability
> to make Thymeleaf include them into other templates.

> Note that fragment expressions are subject to stricter expression evaluation restrictions
> for security reasons. See [Appendix D: Expression Restrictions](../appendix-d-expression-restrictions/).

### Referencing fragments without `th:fragment`

Thanks to the power of Markup Selectors, we can include fragments that do not use any 
`th:fragment` attributes. It can even be markup code coming from a different application 
with no knowledge of Thymeleaf at all:

```html
...
<div id="copy-section">
  &copy; 2011 The Good Thymes Virtual Grocery
</div>
...
```

We can use the fragment above simply referencing it by its `id` attribute, in a similar way to a CSS selector:

```html
<body>

  ...

  <div th:insert="~{footer :: #copy-section}"></div>
  
</body>
```

### Difference between `th:insert` and `th:replace`

And what is the difference between `th:insert` and `th:replace`?

 * `th:insert` will simply insert the specified fragment as the body
   of its host tag.

 * `th:replace` actually *replaces* its host tag with the specified fragment.

So an HTML fragment like this:

```html
<footer th:fragment="copy">
  &copy; 2011 The Good Thymes Virtual Grocery
</footer>
```

...included twice in host `<div>` tags, like this:

```html
<body>

  ...

  <div th:insert="~{footer :: copy}"></div>

  <div th:replace="~{footer :: copy}"></div>
  
</body>
```

...will result in:

```html
<body>

  ...

  <div>
    <footer>
      &copy; 2011 The Good Thymes Virtual Grocery
    </footer>
  </div>

  <footer>
    &copy; 2011 The Good Thymes Virtual Grocery
  </footer>
  
</body>
```

## Parameterizable fragment signatures

In order to create a more _function-like_ mechanism for template fragments,
fragments defined with `th:fragment` can specify a set of parameters:
	
```html
<div th:fragment="frag (onevar,twovar)">
    <p th:text="${onevar} + ' - ' + ${twovar}">...</p>
</div>
```

This requires the use of one of these two syntaxes to call the fragment from
`th:insert` or `th:replace`:

```html
<div th:replace="~{ ::frag (${value1},${value2}) }">...</div>
<div th:replace="~{ ::frag (onevar=${value1},twovar=${value2}) }">...</div>
```

Note that order is not important in the last option:

```html
<div th:replace="~{ ::frag (twovar=${value2},onevar=${value1}) }">...</div>
```

### Fragment local variables without fragment arguments

Even if fragments are defined without arguments like this:

```html	
<div th:fragment="frag">
    ...
</div>
```

We could use the second syntax specified above to call them (and only the second one):

```html	
<div th:replace="~{::frag (onevar=${value1},twovar=${value2})}">
```

This would be equivalent to a combination of `th:replace` and `th:with`:

```html	
<div th:replace="~{::frag}" th:with="onevar=${value1},twovar=${value2}">
```

**Note** that this specification of local variables for a fragment -- no matter
whether it has an argument signature or not -- does not cause the context to be
emptied prior to its execution. Fragments will still be able to access every
context variable being used at the calling template like they currently are. 

### th:assert for in-template assertions

The `th:assert` attribute can specify a comma-separated list of expressions
which should be evaluated and produce true for every evaluation, raising an
exception if not.

```html
<div th:assert="${onevar},(${twovar} != 43)">...</div>
```

This comes in handy for validating parameters at a fragment signature:

```html
<header th:fragment="contentheader(title)" th:assert="${!#strings.isEmpty(title)}">...</header>
```

## Flexible layouts: beyond mere fragment insertion

Thanks to *fragment expressions*, we can specify parameters for fragments that
are not texts, numbers, bean objects... but instead fragments of markup.

This allows us to create our fragments in a way such that they can be *enriched*
with markup coming from the calling templates, resulting in a very flexible
**template layout mechanism**.

Note the use of the `title` and `links` variables in the fragment below:

```html
<head th:fragment="common_header(title,links)">

  <title th:replace="${title}">The awesome application</title>

  <!-- Common styles and scripts -->
  <link rel="stylesheet" type="text/css" media="all" th:href="@{/css/awesomeapp.css}">
  <link rel="shortcut icon" th:href="@{/images/favicon.ico}">
  <script type="text/javascript" th:src="@{/sh/scripts/codebase.js}"></script>

  <!--/* Per-page placeholder for additional links */-->
  <th:block th:replace="${links}" />

</head>
```

We can now call this fragment like:

```html
...
<head th:replace="~{ base :: common_header(~{::title},~{::link}) }">

  <title>Awesome - Main</title>

  <link rel="stylesheet" th:href="@{/css/bootstrap.min.css}">
  <link rel="stylesheet" th:href="@{/themes/smoothness/jquery-ui.css}">

</head>
...
```

...and the result will use the actual `<title>` and `<link>` tags from our
calling template as the values of the `title` and `links` variables, resulting
in our fragment being customized during insertion:

```html
...
<head>

  <title>Awesome - Main</title>

  <!-- Common styles and scripts -->
  <link rel="stylesheet" type="text/css" media="all" href="/awe/css/awesomeapp.css">
  <link rel="shortcut icon" href="/awe/images/favicon.ico">
  <script type="text/javascript" src="/awe/sh/scripts/codebase.js"></script>

  <link rel="stylesheet" href="/awe/css/bootstrap.min.css">
  <link rel="stylesheet" href="/awe/themes/smoothness/jquery-ui.css">

</head>
...
```

### Using the empty fragment

A special fragment expression, the *empty fragment* (`~{}`), can be used for
specifying *no markup*. Using the previous example:

```html
<head th:replace="~{ base :: common_header(~{::title},~{}) }">

  <title>Awesome - Main</title>

</head>
...
```

Note how the second parameter of the fragment (`links`) is set to the *empty
fragment* and therefore nothing is written for the `<th:block th:replace="${links}" />`
block:

```html
...
<head>

  <title>Awesome - Main</title>

  <!-- Common styles and scripts -->
  <link rel="stylesheet" type="text/css" media="all" href="/awe/css/awesomeapp.css">
  <link rel="shortcut icon" href="/awe/images/favicon.ico">
  <script type="text/javascript" src="/awe/sh/scripts/codebase.js"></script>

</head>
...
```

### Using the no-operation token

The no-op can be also used as a parameter to a fragment if we just want to let
our fragment use  its current markup as a default value. Again, using the
`common_header` example:

```html
...
<head th:replace="~{base :: common_header(_,~{::link})}">

  <title>Awesome - Main</title>

  <link rel="stylesheet" th:href="@{/css/bootstrap.min.css}">
  <link rel="stylesheet" th:href="@{/themes/smoothness/jquery-ui.css}">

</head>
...
```

See how the `title` argument (first argument of the `common_header` fragment) is
set to *no-op* (`_`), which results in this part of the fragment not being
executed at all (`title` = *no-operation*):

```html
  <title th:replace="${title}">The awesome application</title>
```

So the result is:

```html
...
<head>

  <title>The awesome application</title>

  <!-- Common styles and scripts -->
  <link rel="stylesheet" type="text/css" media="all" href="/awe/css/awesomeapp.css">
  <link rel="shortcut icon" href="/awe/images/favicon.ico">
  <script type="text/javascript" src="/awe/sh/scripts/codebase.js"></script>

  <link rel="stylesheet" href="/awe/css/bootstrap.min.css">
  <link rel="stylesheet" href="/awe/themes/smoothness/jquery-ui.css">

</head>
...
```

### Advanced conditional insertion of fragments

The availability of both the *empty fragment* and *no-operation token* allows us
to perform conditional insertion of fragments in a very easy and elegant way.

For example, we could do this in order to insert our `common :: adminhead`
fragment *only* if the user is an administrator, and insert nothing (empty
fragment) if not:

```html
...
<div th:insert="${user.isAdmin()} ? ~{common :: adminhead} : ~{}">...</div>
...
```

Also, we can use the *no-operation token* in order to insert a fragment only if
the specified condition is met, but leave the markup without modifications if
the condition is not met:

```html
...
<div th:insert="${user.isAdmin()} ? ~{common :: adminhead} : _">
    Welcome [[${user.name}]], click <a th:href="@{/support}">here</a> for help-desk support.
</div>
...
```

Additionally, if we have configured our template resolvers to *check for
existence* of the template resources –- by means of their `checkExistence` flag
-– we can use the existence of the fragment itself as the condition in a *default*
operation:

```html
...
<!-- The body of the <div> will be used if the "common :: salutation" fragment  -->
<!-- does not exist (or is empty).                                              -->
<div th:insert="~{common :: salutation} ?: _">
    Welcome [[${user.name}]], click <a th:href="@{/support}">here</a> for help-desk support.
</div>
...
```

## Removing template fragments

Back to the example application, let's revisit the last version of our product list template:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
</table>
```

This code is just fine as a template, but as a static page (when directly open
by a browser without Thymeleaf processing it) it would not make a nice prototype. 

Why? Because, although perfectly displayable by browsers, that table only has a
row, and this row has mock data. As a prototype, it simply wouldn't look
realistic enough... we should have more than one product, _we need more rows_.

So let's add some:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
  <tr class="odd">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr>
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

Ok, now we have three, definitely better for a prototype. But... what will
happen when we process it with Thymeleaf?:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr>
    <td>Fresh Sweet Basil</td>
    <td>4.99</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Italian Tomato</td>
    <td>1.25</td>
    <td>no</td>
    <td>
      <span>2</span> comment/s
      <a href="/gtvg/product/comments?prodId=2">view</a>
    </td>
  </tr>
  <tr>
    <td>Yellow Bell Pepper</td>
    <td>2.50</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Old Cheddar</td>
    <td>18.75</td>
    <td>yes</td>
    <td>
      <span>1</span> comment/s
      <a href="/gtvg/product/comments?prodId=4">view</a>
    </td>
  </tr>
  <tr class="odd">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr>
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

The last two rows are mock rows! Well, of course they are: iteration was only
applied to the first row, so there is no reason why Thymeleaf should have
removed the other two.

We need a way to remove those two rows during template processing. Let's use the
`th:remove` attribute on the second and third `<tr>` tags:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
  <tr class="odd" th:remove="all">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr th:remove="all">
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

Once processed, everything will look again as it should:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr>
    <td>Fresh Sweet Basil</td>
    <td>4.99</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Italian Tomato</td>
    <td>1.25</td>
    <td>no</td>
    <td>
      <span>2</span> comment/s
      <a href="/gtvg/product/comments?prodId=2">view</a>
    </td>
  </tr>
  <tr>
    <td>Yellow Bell Pepper</td>
    <td>2.50</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Old Cheddar</td>
    <td>18.75</td>
    <td>yes</td>
    <td>
      <span>1</span> comment/s
      <a href="/gtvg/product/comments?prodId=4">view</a>
    </td>
  </tr>
</table>
```

And what does that `all` value in the attribute, mean? `th:remove` can behave in
five different ways, depending on its value:

 * `all`: Remove both the containing tag and all its children.
 * `body`: Do not remove the containing tag, but remove all its children.
 * `tag`: Remove the containing tag, but do not remove its children. (`tags`, plural, is also allowed as an alias for this value.)
 * `all-but-first`: Remove all children of the containing tag except the first one.
 * `none` : Do nothing. This value is useful for dynamic evaluation.

What can that `all-but-first` value be useful for? It will let us save some `th:remove="all"`
when prototyping:

```html
<table>
  <thead>
    <tr>
      <th>NAME</th>
      <th>PRICE</th>
      <th>IN STOCK</th>
      <th>COMMENTS</th>
    </tr>
  </thead>
  <tbody th:remove="all-but-first">
    <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
      <td th:text="${prod.name}">Onions</td>
      <td th:text="${prod.price}">2.41</td>
      <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
      <td>
        <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
        <a href="comments.html" 
           th:href="@{/product/comments(prodId=${prod.id})}" 
           th:unless="${#lists.isEmpty(prod.comments)}">view</a>
      </td>
    </tr>
    <tr class="odd">
      <td>Blue Lettuce</td>
      <td>9.55</td>
      <td>no</td>
      <td>
        <span>0</span> comment/s
      </td>
    </tr>
    <tr>
      <td>Mild Cinnamon</td>
      <td>1.99</td>
      <td>yes</td>
      <td>
        <span>3</span> comment/s
        <a href="comments.html">view</a>
      </td>
    </tr>
  </tbody>
</table>
```

The `th:remove` attribute can take any _Thymeleaf Standard Expression_, as long
as it returns one of the allowed String values (`all`, `tag`, `body`, `all-but-first`
or `none`).

This means removals could be conditional, like:

```html
<a href="/something" th:remove="${condition}? tag : none">Link text not to be removed</a>
```

Also note that `th:remove` considers `null` a synonym to `none`, so the
following works the same as the example above:

```html
<a href="/something" th:remove="${condition}? tag">Link text not to be removed</a>
```

In this case, if `${condition}` is false, `null` will be returned, and thus no
removal will be performed. 

## Layout Inheritance

To be able to have a single file as layout, fragments can be used. An example 
of a simple layout having `title` and `content` using `th:fragment` and 
`th:replace`:

```html
<!DOCTYPE html>
<html th:fragment="layout (title, content)" xmlns:th="http://www.thymeleaf.org">
<head>
    <title th:replace="${title}">Layout Title</title>
</head>
<body>
    <h1>Layout H1</h1>
    <div th:replace="${content}">
        <p>Layout content</p>
    </div>
    <footer>
        Layout footer
    </footer>
</body>
</html>
```

This example declares a fragment called **layout** having _title_ and _content_ as
parameters. Both will be replaced on page inheriting it by provided fragment 
expressions in the example below.

```html
<!DOCTYPE html>
<html th:replace="~{layoutFile :: layout(~{::title}, ~{::section})}">
<head>
    <title>Page Title</title>
</head>
<body>
<section>
    <p>Page content</p>
    <div>Included on page</div>
</section>
</body>
</html>
```

In this file, the `html` tag will be replaced by _layout_, but in the layout 
`title` and `content` will have been replaced by `title` and `section` blocks
respectively.

If desired, the layout can be composed by several fragments as _header_ 
and _footer_.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#template-layout) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

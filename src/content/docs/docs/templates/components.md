---
title: "Components"
description: "In order to create a more function-like mechanism for template fragments, fragments defined with th:fragment can specify a set of parameters."
sidebar:
  order: 9
---

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

## Fragment local variables without fragment arguments

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

## th:assert for in-template assertions

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

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Parameterizable fragment signatures](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#parameterizable-fragment-signatures), [Flexible layouts: beyond mere fragment insertion](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#flexible-layouts-beyond-mere-fragment-insertion).*

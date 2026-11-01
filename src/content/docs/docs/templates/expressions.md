---
title: "Expressions"
description: "We will take a small break in the development of our grocery virtual store to learn about one of the most important parts of the Thymeleaf Standard Dialect: the Thymeleaf Standard Expression syntax."
sidebar:
  order: 1
---

We will take a small break in the development of our grocery virtual store to
learn about one of the most important parts of the Thymeleaf Standard Dialect:
the Thymeleaf Standard Expression syntax.

We have already seen two types of valid attribute values expressed in this
syntax: message and variable expressions:

```html
<p th:utext="#{home.welcome}">Welcome to our grocery store!</p>

<p>Today is: <span th:text="${today}">13 february 2011</span></p>
```

But there are more types of expressions, and more interesting details to learn
about the ones we already know. For a quick summary of the Standard Expression
features, see [Expression syntax](../../reference/expression-syntax/).

## Messages

As we already know, `#{...}` message expressions allow us to link this:

```html
<p th:utext="#{home.welcome}">Welcome to our grocery store!</p>
```

...to this:

```
home.welcome=¡Bienvenido a nuestra tienda de comestibles!
```

But there's one aspect we still haven't thought of: what happens if the message
text is not completely static? What if, for example, our application knew who is
the user visiting the site at any moment and we wanted to greet them by name?

```html
<p>¡Bienvenido a nuestra tienda de comestibles, John Apricot!</p>
```

This means we would need to add a parameter to our message. Just like this:

```
home.welcome=¡Bienvenido a nuestra tienda de comestibles, {0}!
```

Parameters are specified according to the
[`java.text.MessageFormat`](https://docs.oracle.com/javase/10/docs/api/java/text/MessageFormat.html)
standard syntax, which means you can format to numbers and dates as specified
in the API docs for classes in the `java.text.*` package.

In order to specify a value for our parameter, and given an HTTP session
attribute called `user`, we could have:

```html
<p th:utext="#{home.welcome(${session.user.name})}">
  Welcome to our grocery store, Sebastian Pepper!
</p>
```

> Note that the use of `th:utext` here means that the formatted message will
> not be escaped. This example assumes that `user.name` is already escaped.

Several parameters can be specified, separated by commas.

The message key itself can come from a variable:

```html
<p th:utext="#{${welcomeMsgKey}(${session.user.name})}">
  Welcome to our grocery store, Sebastian Pepper!
</p>
```

## Variables

We already mentioned that `${...}` expressions are in fact OGNL (Object-Graph
Navigation Language) expressions executed on the map of variables contained in
the context.

> For detailed info about OGNL syntax and features, you should read the 
> [OGNL Language Guide](http://commons.apache.org/ognl/)
> 
> In Spring MVC-enabled applications OGNL will be replaced with **SpringEL**,
> but its syntax is very similar to that of OGNL (actually, exactly the same for
> most common cases).

From OGNL's syntax, we know that the expression in:

```html
<p>Today is: <span th:text="${today}">13 february 2011</span>.</p>
```

...is in fact equivalent to this:

```java
ctx.getVariable("today");
```

But OGNL allows us to create quite more powerful expressions, and that's how
this:

```html
<p th:utext="#{home.welcome(${session.user.name})}">
  Welcome to our grocery store, Sebastian Pepper!
</p>
```

...obtains the user name by executing:

```java
((User) ctx.getVariable("session").get("user")).getName();
```

But getter method navigation is just one of OGNL's features. Let's see some more:

```java
/*
 * Access to properties using the point (.). Equivalent to calling property getters.
 */
${person.father.name}

/*
 * Access to properties can also be made by using brackets ([]) and writing 
 * the name of the property as a variable or between single quotes.
 */
${person['father']['name']}

/*
 * If the object is a map, both dot and bracket syntax will be equivalent to 
 * executing a call on its get(...) method.
 */
${countriesByCode.ES}
${personsByName['Stephen Zucchini'].age}

/*
 * Indexed access to arrays or collections is also performed with brackets, 
 * writing the index without quotes.
 */
${personsArray[0].name}

/*
 * Methods can be called, even with arguments.
 */
${person.createCompleteName()}
${person.createCompleteNameWithSeparator('-')}
```

### Expression Basic Objects

When evaluating OGNL expressions on the context variables, some objects are made
available to expressions for higher flexibility. These objects will be
referenced (per OGNL standard) starting with the `#` symbol:

 * `#ctx`: the context object.
 * `#vars:` the context variables.
 * `#locale`: the context locale.

So we can do this:

```html
Established locale country: <span th:text="${#locale.country}">US</span>.
```

You can read the full reference of these objects in [Basic objects](../../reference/basic-objects/).

### Expression Utility Objects

Besides these basic objects, Thymeleaf will offer us a set of utility objects
that will help us perform common tasks in our expressions.

 * `#execInfo`: information about the template being processed.
 * `#messages`: methods for obtaining externalized messages inside variables
   expressions, in the same way as they would be obtained using #{...} syntax.
 * `#uris`: methods for escaping parts of URLs/URIs
 * `#conversions`: methods for executing the configured *conversion service* (if any).
 * `#dates`: methods for `java.util.Date` objects: formatting, component
   extraction, etc.
 * `#calendars`: analogous to `#dates`, but for `java.util.Calendar` objects.
 * `#temporals`: for dealing with dates and times using the `java.time` API in JDK8+.
 * `#numbers`: methods for formatting numeric objects.
 * `#strings`: methods for `String` objects: contains, startsWith, prepending/appending,
   etc.
 * `#objects`: methods for objects in general.
 * `#bools`: methods for boolean evaluation.
 * `#arrays`: methods for arrays.
 * `#lists`: methods for lists.
 * `#sets`: methods for sets.
 * `#maps`: methods for maps.
 * `#aggregates`: methods for creating aggregates on arrays or collections.
 * `#ids`: methods for dealing with id attributes that might be repeated (for
   example, as a result of an iteration).

You can check what functions are offered by each of these utility objects in the
[Utility objects](../../reference/utility-objects/).

### Reformatting dates in our home page

Now we know about these utility objects, we could use them to change the way in
which we show the date in our home page. Instead of doing this in our `HomeController`:

```java
SimpleDateFormat dateFormat = new SimpleDateFormat("dd MMMM yyyy");
Calendar cal = Calendar.getInstance();

WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
ctx.setVariable("today", dateFormat.format(cal.getTime()));

templateEngine.process("home", ctx, writer);
```

...we can do just this:

```java
WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
ctx.setVariable("today", Calendar.getInstance());

templateEngine.process("home", ctx, writer);
```

...and then perform date formatting in the view layer itself:

```html
<p>
  Today is: <span th:text="${#calendars.format(today,'dd MMMM yyyy')}">13 May 2011</span>
</p>
```

## Expressions on selections (asterisk syntax)

Not only can variable expressions be written as `${...}`, but also as `*{...}`.

There is an important difference though: the asterisk syntax evaluates
expressions on _selected objects_ rather than on the whole context.  That is, as
long as there is no selected object, the dollar and the asterisk syntaxes do
exactly the same.

And what is a selected object? The result of an expression using the `th:object`
attribute. Let's use one in our user profile (`userprofile.html`) page:

```html
  <div th:object="${session.user}">
    <p>Name: <span th:text="*{firstName}">Sebastian</span>.</p>
    <p>Surname: <span th:text="*{lastName}">Pepper</span>.</p>
    <p>Nationality: <span th:text="*{nationality}">Saturn</span>.</p>
  </div>
```

Which is exactly equivalent to:

```html
<div>
  <p>Name: <span th:text="${session.user.firstName}">Sebastian</span>.</p>
  <p>Surname: <span th:text="${session.user.lastName}">Pepper</span>.</p>
  <p>Nationality: <span th:text="${session.user.nationality}">Saturn</span>.</p>
</div>
```

Of course, dollar and asterisk syntax can be mixed:

```html
<div th:object="${session.user}">
  <p>Name: <span th:text="*{firstName}">Sebastian</span>.</p>
  <p>Surname: <span th:text="${session.user.lastName}">Pepper</span>.</p>
  <p>Nationality: <span th:text="*{nationality}">Saturn</span>.</p>
</div>
```

When an object selection is in place, the selected object will also be available
to dollar expressions as the `#object` expression variable:

```html
<div th:object="${session.user}">
  <p>Name: <span th:text="${#object.firstName}">Sebastian</span>.</p>
  <p>Surname: <span th:text="${session.user.lastName}">Pepper</span>.</p>
  <p>Nationality: <span th:text="*{nationality}">Saturn</span>.</p>
</div>
```

As said, if no object selection has been performed, dollar and asterisk syntaxes
are equivalent.

```html
<div>
  <p>Name: <span th:text="*{session.user.name}">Sebastian</span>.</p>
  <p>Surname: <span th:text="*{session.user.surname}">Pepper</span>.</p>
  <p>Nationality: <span th:text="*{session.user.nationality}">Saturn</span>.</p>
</div>
```

## Link URLs

Because of their importance, URLs are first-class citizens in web application
templates, and the _Thymeleaf Standard Dialect_ has a special syntax for them,
the `@` syntax: `@{...}`

There are different types of URLs:

 * Absolute URLs: `http://www.thymeleaf.org`
 * Relative URLs, which can be:
    * Page-relative: `user/login.html`
    * Context-relative: `/itemdetails?id=3` (context name in server will be
      added automatically)
    * Server-relative: `~/billing/processInvoice` (allows calling URLs in
      another context (= application) in the same server.
    * Protocol-relative URLs: `//code.jquery.com/jquery-2.0.3.min.js`

The real processing of these expressions and their conversion to the URLs that
will be output is done by implementations of the `org.thymeleaf.linkbuilder.ILinkBuilder`
interface that are registered into the `ITemplateEngine` object being used.

By default, a single implementation of this interface is registered of the class
`org.thymeleaf.linkbuilder.StandardLinkBuilder`, which is enough for both offline
(non-web) and also web scenarios based on the Servlet API. Other scenarios (like
integration with non-ServletAPI web frameworks) might need specific
implementations of the link builder interface.

Let's use this new syntax. Meet the `th:href` attribute:

```html
<!-- Will produce 'http://localhost:8080/gtvg/order/details?orderId=3' (plus rewriting) -->
<a href="details.html" 
   th:href="@{http://localhost:8080/gtvg/order/details(orderId=${o.id})}">view</a>

<!-- Will produce '/gtvg/order/details?orderId=3' (plus rewriting) -->
<a href="details.html" th:href="@{/order/details(orderId=${o.id})}">view</a>

<!-- Will produce '/gtvg/order/3/details' (plus rewriting) -->
<a href="details.html" th:href="@{/order/{orderId}/details(orderId=${o.id})}">view</a>
```

Some things to note here:

 * `th:href` is a modifier attribute: once processed, it will compute the link
   URL to be used and set that value to the `href` attribute of the `<a>` tag.
 * We are allowed to use expressions for URL parameters (as you can see in `orderId=${o.id}`).
   The required URL-parameter-encoding operations will also be automatically
   performed.
 * If several parameters are needed, these will be separated by commas: `@{/order/process(execId=${execId},execType='FAST')}`
 * Variable templates are also allowed in URL paths: `@{/order/{orderId}/details(orderId=${orderId})}`
 * Relative URLs starting with `/` (eg: `/order/details`) will be automatically
   prefixed by the application context name.
 * If cookies are not enabled or this is not yet known, a `";jsessionid=..."`
   suffix might be added to relative URLs so that the session is preserved. This
   is called _URL Rewriting_ and Thymeleaf allows you to plug in your own
   rewriting filters by using the `response.encodeURL(...)` mechanism from the
   Servlet API for every URL.
 * The `th:href` attribute allows us to (optionally) have a working static `href`
   attribute in our template, so that our template links remained navigable by a
   browser when opened directly for prototyping purposes.

As was the case with the message syntax (`#{...}`), URL bases can also be the
result of evaluating another expression:

```html
<a th:href="@{${url}(orderId=${o.id})}">view</a>
<a th:href="@{'/details/'+${user.login}(orderId=${o.id})}">view</a>
```

### A menu for our home page

Now that we know how to create link URLs, what about adding a small menu in our
home page for some of the other pages in the site?

```html
<p>Please select an option</p>
<ol>
  <li><a href="product/list.html" th:href="@{/product/list}">Product List</a></li>
  <li><a href="order/list.html" th:href="@{/order/list}">Order List</a></li>
  <li><a href="subscribe.html" th:href="@{/subscribe}">Subscribe to our Newsletter</a></li>
  <li><a href="userprofile.html" th:href="@{/userprofile}">See User Profile</a></li>
</ol>
```

### Server root relative URLs

An additional syntax can be used to create server-root-relative (instead of
context-root-relative) URLs in order to link to different contexts in the same
server. These URLs will be specified like `@{~/path/to/something}`

## Fragments

Fragment expressions are an easy way to represent fragments of markup and move
them around templates. This allows us to replicate them, pass them to other
templates as arguments, and so on.

The most common use is for fragment insertion using `th:insert` or `th:replace`
(more on these in a later section):

```html
<div th:insert="~{commons :: main}">...</div>
```

But they can be used anywhere, just as any other variable:

```html
<div th:with="frag=~{footer :: #main/text()}">
  <p th:insert="${frag}">
</div>
```

[Fragments](../fragments/) has an entire page devoted to this,
including deeper explanation of fragment expressions.

## Literals

### Text literals

Text literals are just character strings specified between single quotes. They
can include any character, but you should escape any single quotes inside them
using `\'`.

```html
<p>
  Now you are looking at a <span th:text="'working web application'">template file</span>.
</p>
```

### Number literals

Numeric literals are just that: numbers.

```html
<p>The year is <span th:text="2013">1492</span>.</p>
<p>In two years, it will be <span th:text="2013 + 2">1494</span>.</p>
```

### Boolean literals

The boolean literals are `true` and `false`. For example:

```html
<div th:if="${user.isAdmin()} == false"> ...
```

In this example, the `== false` is written outside the braces, and so it is
Thymeleaf that takes care of it. If it were written inside the braces, it would
be the responsibility of the OGNL/SpringEL engines:

```html
<div th:if="${user.isAdmin() == false}"> ...
```

### The null literal

The `null` literal can be also used:

```html
<div th:if="${variable.something} == null"> ...
```

### Literal tokens

Numeric, boolean and null literals are in fact a particular case of _literal tokens_.

These tokens allow a little bit of simplification in Standard Expressions. They
work exactly the same as text literals (`'...'`), but they only allow letters (`A-Z`
and `a-z`), numbers (`0-9`), brackets (`[` and `]`), dots (`.`), hyphens (`-`)
and underscores (`_`). So no whitespaces, no commas, etc.

The nice part? Tokens don't need any quotes surrounding them. So we can do this:

```html
<div th:class="content">...</div>
```

instead of:

```html
<div th:class="'content'">...</div>
```

## Appending texts

Texts, no matter whether they are literals or the result of evaluating variable
or message expressions, can be easily appended using the `+` operator:

```html
<span th:text="'The name of the user is ' + ${user.name}">
```

## Literal substitutions

Literal substitutions allow for an easy formatting of strings containing values
from variables without the need to append literals with `'...' + '...'`.

These substitutions must be surrounded by vertical bars (`|`), like:

```html
<span th:text="|Welcome to our application, ${user.name}!|">
```

Which is equivalent to:

```html
<span th:text="'Welcome to our application, ' + ${user.name} + '!'">
```

Literal substitutions can be combined with other types of expressions:

```html
<span th:text="${onevar} + ' ' + |${twovar}, ${threevar}|">
```

> Only variable/message expressions (`${...}`, `*{...}`, `#{...}`) are allowed 
> inside `|...|` literal substitutions. No other literals (`'...'`), 
> boolean/numeric tokens, conditional expressions etc. are. 

## Arithmetic operations

Some arithmetic operations are also available: `+`, `-`, `*`, `/` and `%`.

```html
<div th:with="isEven=(${prodStat.count} % 2 == 0)">
```

Note that these operators can also be applied inside OGNL variable expressions
themselves (and in that case will be executed by OGNL instead of the Thymeleaf
Standard Expression engine):

```html
<div th:with="isEven=${prodStat.count % 2 == 0}">
```

Note that textual aliases exist for some of these operators: `div` (`/`), `mod` (`%`).

## Comparators and Equality

Values in expressions can be compared with the `>`, `<`, `>=` and `<=` symbols,
and the `==` and `!=` operators can be used to check for equality (or the lack
of it). Note that XML establishes that the `<` and `>` symbols should not be
used in attribute values, and so they should be substituted by `&lt;` and
`&gt;`.

```html
<div th:if="${prodStat.count} &gt; 1">
<span th:text="'Execution mode is ' + ( (${execMode} == 'dev')? 'Development' : 'Production')">
```

A simpler alternative may be using textual aliases that exist for some of these
operators: `gt` (`>`), `lt` (`<`), `ge` (`>=`), `le` (`<=`), `not` (`!`). Also
`eq` (`==`), `neq`/`ne` (`!=`).

## Conditional expressions

_Conditional expressions_ are meant to evaluate only one of two expressions
depending on the result of evaluating a condition (which is itself another
expression).

Let's have a look at an example fragment (introducing another _attribute modifier_,
`th:class`):

```html
<tr th:class="${row.even}? 'even' : 'odd'">
  ...
</tr>
```

All three parts of a conditional expression (`condition`, `then` and `else`) are
themselves  expressions, which means that they can be variables (`${...}`, `*{...}`),
messages (`#{...}`), URLs (`@{...}`) or literals (`'...'`).

Conditional expressions can also be nested using parentheses:

```html
<tr th:class="${row.even}? (${row.first}? 'first' : 'even') : 'odd'">
  ...
</tr>
```

Else expressions can also be omitted, in which case a null value is returned if
the condition is false:

```html
<tr th:class="${row.even}? 'alt'">
  ...
</tr>
```

## Default expressions (Elvis operator)

A _default expression_ is a special kind of conditional value without a _then_
part. It is equivalent to the _Elvis operator_ present in some languages like
Groovy, lets you specify two expressions: the first one is used if it doesn't
evaluate to null, but if it does then the second one is used.

Let's see it in action in our user profile page:

```html
<div th:object="${session.user}">
  ...
  <p>Age: <span th:text="*{age}?: '(no age specified)'">27</span>.</p>
</div>
```

As you can see, the operator is `?:`, and we use it here to specify a default
value for a name (a literal value, in this case) only if the result of
evaluating `*{age}` is null. This is therefore equivalent to:

```html
<p>Age: <span th:text="*{age != null}? *{age} : '(no age specified)'">27</span>.</p>
```

As with conditional values, they can contain nested expressions between
parentheses:

```html
<p>
  Name: 
  <span th:text="*{firstName}?: (*{admin}? 'Admin' : #{default.username})">Sebastian</span>
</p>
```

## The No-Operation token

The No-Operation token is represented by an underscore symbol (`_`).

The idea behind this token is to specify that the desired result for an
expression is to *do nothing*, i.e. do exactly as if the processable attribute
(e.g. `th:text`) was not there at all.

Among other possibilities, this allows developers to use prototyping text as
default values. For example, instead of:

```html
<span th:text="${user.name} ?: 'no user authenticated'">...</span>
```

...we can directly use *'no user authenticated'* as a prototyping text, which results in code that 
is both more concise and versatile from a design standpoint:

```html
<span th:text="${user.name} ?: _">no user authenticated</span>
```

## Data Conversion / Formatting

Thymeleaf defines a *double-brace* syntax for variable (`${...}`) and selection
(`*{...}`) expressions that allows us to apply *data conversion* by means of a
configured *conversion service*.

It basically goes like this:

```html
<td th:text="${{user.lastAccessDate}}">...</td>
```

Noticed the double brace there?: `${{...}}`. That instructs Thymeleaf to pass
the result of the `user.lastAccessDate` expression to the *conversion service*
and asks it to perform a **formatting operation** (a conversion to `String`)
before writing the result.

Assuming that `user.lastAccessDate` is of type `java.util.Calendar`, if a *conversion service* 
(implementation of `IStandardConversionService`) has been registered and contains a valid 
conversion for `Calendar -> String`, it will be applied.

The default implementation of `IStandardConversionService` (the `StandardConversionService`
class) simply executes `.toString()` on any object converted to `String`. For more information on
how to register a custom *conversion service* implementation, have a look at the
[More on Configuration](../../configuration/template-engine-and-resolvers/) section.

> The official thymeleaf-spring3 and thymeleaf-spring4 integration packages 
> transparently integrate Thymeleaf's conversion service mechanism with Spring's
> own *Conversion Service* infrastructure, so that conversion services and
> formatters declared in the Spring configuration will be made automatically
> available to `${{...}}` and `*{{...}}` expressions.

## Preprocessing

In addition to all these features for expression processing, Thymeleaf has the
feature of _preprocessing_ expressions.

Preprocessing is an execution of the expressions done before the normal one that
allows for modification of the expression that will eventually be executed.

Preprocessed expressions are exactly like normal ones, but appear surrounded by
a double underscore symbol (like `__${expression}__`).

Let's imagine we have an i18n `Messages_fr.properties` entry containing an OGNL
expression calling a language-specific static method, like:

```java
article.text=@myapp.translator.Translator@translateToFrench({0})
```

...and a `Messages_es.properties equivalent`:

```java
article.text=@myapp.translator.Translator@translateToSpanish({0})
```

We can create a fragment of markup that evaluates one expression or the other
depending on the locale. For this, we will first select the expression (by
preprocessing) and then let Thymeleaf execute it:

```html
<p th:text="${__#{article.text('textVar')}__}">Some text here...</p>
```

Note that the preprocessing step for a French locale will be creating the
following equivalent:

```html
<p th:text="${@myapp.translator.Translator@translateToFrench(textVar)}">Some text here...</p>
```

The preprocessing String `__` can be escaped in attributes using `\_\_`.

> Note that preprocessing is subject to stricter expression evaluation restrictions
> for security reasons. See [Expression restrictions](../../security/expression-restrictions/).

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#standard-expression-syntax) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

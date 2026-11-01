---
title: "Using Texts"
description: "Our first task will be to create a home page for our grocery site."
sidebar:
  order: 3
---

## A multi-language welcome

Our first task will be to create a home page for our grocery site.

The first version of this page will be extremely simple: just a title and a
welcome message. This is our `/WEB-INF/templates/home.html` file:

```html
<!DOCTYPE html>

<html xmlns:th="http://www.thymeleaf.org">

  <head>
    <title>Good Thymes Virtual Grocery</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" type="text/css" media="all" 
          href="../../css/gtvg.css" th:href="@{/css/gtvg.css}" />
  </head>

  <body>
  
    <p th:text="#{home.welcome}">Welcome to our grocery store!</p>
  
  </body>

</html>
```

The first thing you will notice is that this file is HTML5 that can be correctly
displayed by any browser because it does not include any non-HTML tags (browsers
ignore all attributes they don't understand, like `th:text`).

But you may also notice that this template is not really a _valid_ HTML5
document, because these non-standard attributes we are using in the `th:*` form
are not allowed by the HTML5 specification. In fact, we are even adding an `xmlns:th` 
attribute to our `<html>` tag, something absolutely non-HTML5-ish:

```html
<html xmlns:th="http://www.thymeleaf.org">
```

...which has no influence at all in template processing, but works as an
*incantation* that prevents our IDE from complaining about the lack of a
namespace definition for all those `th:*` attributes.

So what if we wanted to make this template **HTML5-valid**? Easy: switch to
Thymeleaf's data attribute syntax, using the `data-` prefix for attribute names
and hyphen (`-`) separators instead of semi-colons (`:`):

```html
<!DOCTYPE html>

<html>

  <head>
    <title>Good Thymes Virtual Grocery</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" type="text/css" media="all" 
          href="../../css/gtvg.css" data-th-href="@{/css/gtvg.css}" />
  </head>

  <body>
  
    <p data-th-text="#{home.welcome}">Welcome to our grocery store!</p>
  
  </body>

</html>
```

Custom `data-` prefixed attributes are allowed by the HTML5 specification, so,
with this code above, our template would be a *valid HTML5 document*.

> Both notations are completely equivalent and interchangeable, but for the sake
> of simplicity and compactness of the code samples, this tutorial will use the
> *namespace notation* (`th:*`). Also, the `th:*` notation is more general and
> allowed in every Thymeleaf template mode (`XML`, `TEXT`...) whereas the `data-`
> notation is only allowed in `HTML` mode.

### Using th:text and externalizing text

Externalizing text is extracting fragments of template code out of template
files so that they can be kept in separate files (typically `.properties` files)
and that they can be easily replaced with equivalent texts written in other
languages (a process called internationalization or simply _i18n_). Externalized
fragments of text are usually called *"messages"*.

Messages always have a key that identifies them, and Thymeleaf allows you to
specify that a text should correspond to a specific message with the `#{...}`
syntax:

```html
<p th:text="#{home.welcome}">Welcome to our grocery store!</p>
```

What we can see here are in fact two different features of the Thymeleaf
Standard Dialect:

 * The `th:text` attribute, which evaluates its value expression and sets the
   result as the body of the host tag, effectively replacing the "Welcome to our
   grocery store!" text we see in the code.
 * The `#{home.welcome}` expression, specified in the _Standard Expression Syntax_,
   instructing that the text to be used by the `th:text` attribute should be the
   message with the `home.welcome` key corresponding to whichever locale we are
   processing the template with.

Now, where is this externalized text?

The location of externalized text in Thymeleaf is fully configurable, and it
will depend on the specific `org.thymeleaf.messageresolver.IMessageResolver`
implementation being used. Normally, an implementation based on `.properties`
files will be used, but we could create our own implementations if we wanted,
for example, to obtain messages from a database.

However, we have not specified a message resolver for our template engine during
initialization, and that means that our application is using the _Standard Message Resolver_,
implemented by `org.thymeleaf.messageresolver.StandardMessageResolver`.

The standard message resolver expects to find messages for `/WEB-INF/templates/home.html`
in properties files in the same folder and with the same name as the template,
like:

 * `/WEB-INF/templates/home_en.properties` for English texts.
 * `/WEB-INF/templates/home_es.properties` for Spanish language texts.
 * `/WEB-INF/templates/home_pt_BR.properties` for Portuguese (Brazil) language
   texts.
 * `/WEB-INF/templates/home.properties` for default texts (if the locale is not
   matched).

Let's have a look at our `home_es.properties` file:

```
home.welcome=¡Bienvenido a nuestra tienda de comestibles!
```

This is all we need for making Thymeleaf process our template. Let's create our
Home controller then.

### Contexts

In order to process our template, we will create a `HomeController` class
implementing the `IGTVGController` interface we saw before:

```java
public class HomeController implements IGTVGController {

    public void process(
            final IWebExchange webExchange, 
            final ITemplateEngine templateEngine,
            final Writer writer)
            throws Exception {
        
        WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
        
        templateEngine.process("home", ctx, writer);
        
    }

}
```

The first thing we see is the creation of a *context*. A Thymeleaf context is an
object implementing the `org.thymeleaf.context.IContext` interface. Contexts
should contain all the data required for an execution of the template engine in
a variables map, and also reference the locale that must be used for
externalized messages.

```java
public interface IContext {

    public Locale getLocale();
    public boolean containsVariable(final String name);
    public Set<String> getVariableNames();
    public Object getVariable(final String name);
    
}
```

There is a specialized extension of this interface, `org.thymeleaf.context.IWebContext`,
meant to be used in web applications.

```java
public interface IWebContext extends IContext {
    
    public IWebExchange getExchange();
    
}
```

The Thymeleaf core library offers an implementation of each of these interfaces:

 * `org.thymeleaf.context.Context` implements `IContext`
 * `org.thymeleaf.context.WebContext` implements `IWebContext`

And as you can see in the controller code, `WebContext` is the one we use. In
fact we have to, because the use of a `WebApplicationTemplateResolver` requires
that we use a context implementing `IWebContext`.

```java
WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
```

The `WebContext` constructor requires information contained in the `IWebExchange`
abstraction object that was created at the filter representing this
web-based interchange (i.e. request + response). The default locale of the
system will be used if none is specified (although you
should never let this happen in real applications).

There are some specialized expressions that we will be able to use to obtain the
request parameters and the request, session and application attributes from the
`WebContext` in our templates. For example:

 * `${x}` will return a variable `x` stored into the Thymeleaf context or as an *exchange attribute* (A *"request attribute"* in Servlet jargon).
 * `${param.x}` will return a *request parameter* called `x` (which might be multivalued).
 * `${session.x}` will return a *session attribute* called `x`.
 * `${application.x}` will return an *application attribute* called `x` (a *"servlet context attribute"* in Servlet jargon).

### Executing the template engine

With our context object ready, now we can tell the template engine to process
the template (by its name) using the context, and passing it a response writer
so that the response can be written to it:

```java
templateEngine.process("home", ctx, writer);
```

Let's see the results of this using the Spanish locale:

```html
<!DOCTYPE html>

<html>

  <head>
    <title>Good Thymes Virtual Grocery</title>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type"/>
    <link rel="stylesheet" type="text/css" media="all" href="/gtvg/css/gtvg.css" />
  </head>

  <body>
  
    <p>¡Bienvenido a nuestra tienda de comestibles!</p>

  </body>

</html>
```

## More on texts and variables

### Unescaped Text

The simplest version of our Home page seems to be ready now, but there is
something we have not thought about... what if we had a message like this?

```java
home.welcome=Welcome to our <b>fantastic</b> grocery store!
```

If we execute this template like before, we will obtain:

```html
<p>Welcome to our &lt;b&gt;fantastic&lt;/b&gt; grocery store!</p>
```

Which is not exactly what we expected, because our `<b>` tag has been escaped
and therefore it will be displayed in the browser.

This is the default behaviour of the `th:text` attribute. If we want Thymeleaf
to respect our HTML tags and not escape them, we will have to use a different
attribute: `th:utext` (for "unescaped text"):

```html
<p th:utext="#{home.welcome}">Welcome to our grocery store!</p>
```

This will output our message just like we wanted it:

```html
<p>Welcome to our <b>fantastic</b> grocery store!</p>
```

> Note that `th:utext` is subject to stricter expression evaluation restrictions
> for security reasons. See [Appendix D: Expression Restrictions](../appendix-d-expression-restrictions/).

### Using and displaying variables

Now let's add some more content to our home page. For example, we may want to
display the date below our welcome message, like this:

```
Welcome to our fantastic grocery store!

Today is: 12 july 2010
```

First of all, we will have to modify our controller so that we add that date as
a context variable:

```java
public void process(
        final IWebExchange webExchange, 
        final ITemplateEngine templateEngine,
        final Writer writer)
        throws Exception {
        
    SimpleDateFormat dateFormat = new SimpleDateFormat("dd MMMM yyyy");
    Calendar cal = Calendar.getInstance();

    WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
    ctx.setVariable("today", dateFormat.format(cal.getTime()));
    
    templateEngine.process("home", ctx, writer);

}
```

We have added a `String` variable called `today` to our context, and now we can display
it in our template:

```html
<body>

  <p th:utext="#{home.welcome}">Welcome to our grocery store!</p>

  <p>Today is: <span th:text="${today}">13 February 2011</span></p>
  
</body>
```

As you can see, we are still using the `th:text` attribute for the job (and
that's correct, because we want to replace the tag's body), but the syntax is
a little bit different this time and instead of a `#{...}` expression value, we
are using a `${...}` one. This is a **variable expression**, and it contains
an expression in a language called _OGNL (Object-Graph Navigation Language)_
that will be executed on the context variables map we talked about before.

The `${today}` expression simply means "get the variable called today", but
these expressions could be more complex (like `${user.name}` for "get the
variable called user, and call its `getName()` method").

There are quite a lot of possibilities in attribute values: messages, variable
expressions... and quite a lot more. The next chapter will show us what all
these possibilities are.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#using-texts) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

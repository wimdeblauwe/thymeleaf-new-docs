---
title: "Text and messages"
description: "Externalizing text is extracting fragments of template code out of template files so that they can be kept in separate files (typically .properties files) and that they can be easily replaced with…"
sidebar:
  order: 2
---

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
> for security reasons. See [Expression restrictions](../../security/expression-restrictions/).

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
expressions... and quite a lot more. [Expressions](../expressions/) shows what all
these possibilities are.

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Using th:text and externalizing text](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#using-thtext-and-externalizing-text), [More on texts and variables](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#more-on-texts-and-variables).*

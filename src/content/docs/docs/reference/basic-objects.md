---
title: "Basic objects"
description: "Some objects and variable maps are always available to be invoked."
sidebar:
  order: 3
---

Some objects and variable maps are always available to be invoked. Let's see
them:

## Base objects

 * **\#ctx** : the context object. An implementation of `org.thymeleaf.context.IContext` 
   or `org.thymeleaf.context.IWebContext` depending on our environment
   (standalone or web).

   Note `#vars` and `#root` are synonyms for the same object, but using `#ctx`
   is recommended.

```java
/*
 * ======================================================================
 * See javadoc API for class org.thymeleaf.context.IContext
 * ======================================================================
 */

${#ctx.locale}
${#ctx.variableNames}

/*
 * ======================================================================
 * See javadoc API for classes org.thymeleaf.context.IWebContext
 * and org.thymeleaf.web.IWebExchange
 * ======================================================================
 */

${#ctx.exchange}
${#ctx.exchange.request}
${#ctx.exchange.session}
${#ctx.exchange.application}
```

 * **\#locale** : direct access to the `java.util.Locale` associated with
   current request.

```java
${#locale}
```

## Web context namespaces for request/session attributes, etc.

When using Thymeleaf in a web environment, we can use a series of shortcuts for
accessing request parameters, session attributes and application attributes:

> Note these are not *context objects*, but maps added to the context as
> variables, so we access them without `#`. In some way, they act as *namespaces*.

 * **param** : for retrieving request parameters. `${param.foo}` is a `String[]`
   with the values of the `foo` request parameter, so `${param.foo[0]}` will
   normally be used for getting the first value.

```java
${param.foo}              // Retrieves a String[] with the values of request parameter 'foo'
${param.size()}
${param.isEmpty()}
${param.containsKey('foo')}
...
```

 * **session** : for retrieving session attributes.

```java
${session.foo}                 // Retrieves the session attribute 'foo'
${session.size()}
${session.isEmpty()}
${session.containsKey('foo')}
...
```

 * **application** : for retrieving application/servlet context attributes.

```java
${application.foo}              // Retrieves the ServletContext attribute 'foo'
${application.size()}
${application.isEmpty()}
${application.containsKey('foo')}
...
```

Note there is **no need to specify a namespace for accessing request attributes**
(as opposed to *request parameters*) because all request attributes are
automatically added to the context as variables in the context root:

```java
${myRequestAttribute}
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#appendix-a-expression-basic-objects) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

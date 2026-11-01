---
title: "More on Configuration"
description: "For our Good Thymes Virtual Grocery, we chose an ITemplateResolver implementation called WebApplicationTemplateResolver that allowed us to obtain templates as resources from the application resources…"
sidebar:
  order: 15
---

## Template Resolvers

For our Good Thymes Virtual Grocery, we chose an `ITemplateResolver`
implementation called `WebApplicationTemplateResolver` that allowed us to obtain
templates as resources from the application resources (the _Servlet Context_
in a Servlet-based webapp).

Besides giving us the ability to create our own template resolver by
implementing `ITemplateResolver,` Thymeleaf includes four implementations out of
the box:

 * `org.thymeleaf.templateresolver.ClassLoaderTemplateResolver`, which resolves
   templates as classloader resources, like:

    ```java
    return Thread.currentThread().getContextClassLoader().getResourceAsStream(template);
    ```

 * `org.thymeleaf.templateresolver.FileTemplateResolver`, which resolves
   templates as files from the file system, like:

    ```java
    return new FileInputStream(new File(template));
    ```

 * `org.thymeleaf.templateresolver.UrlTemplateResolver`, which resolves
   templates as URLs (even non-local ones), like:

    ```java
    return (new URL(template)).openStream();
    ```

 * `org.thymeleaf.templateresolver.StringTemplateResolver`, which resolves
   templates directly as the `String` being specified as `template` (or
   *template name*, which in this case is obviously much more than a mere name):

    ```java
    return new StringReader(templateName);
    ```

All of the pre-bundled implementations of `ITemplateResolver` allow the same set
of configuration parameters, which include:

 * Prefix and suffix (as already seen):

    ```java
    templateResolver.setPrefix("/WEB-INF/templates/");
    templateResolver.setSuffix(".html");
    ```

 * Template aliases that allow the use of template names that do not directly
   correspond to file names. If both suffix/prefix and alias exist, alias will
   be applied before prefix/suffix:

    ```java
    templateResolver.addTemplateAlias("adminHome","profiles/admin/home");
    templateResolver.setTemplateAliases(aliasesMap);
    ```

 * Encoding to be applied when reading templates:

    ```java
    templateResolver.setCharacterEncoding("UTF-8");
    ```

 * Template mode to be used:

    ```java
    // Default is HTML
    templateResolver.setTemplateMode(TemplateMode.XML);
    ```

 * Default mode for template cache, and patterns for defining whether specific
   templates are cacheable or not:

    ```java
    // Default is true
    templateResolver.setCacheable(false);
    templateResolver.getCacheablePatternSpec().addPattern("/users/*");
    ```

 * TTL in milliseconds for parsed template cache entries originated in this
   template resolver. If not set, the only way to remove an entry from the cache
   will be to exceed the cache max size (oldest entry will be removed).

    ```java
    // Default is no TTL (only cache size exceeded would remove entries)
    templateResolver.setCacheTTLMs(60000L);
    ```

> The Thymeleaf + Spring integration packages offer a `SpringResourceTemplateResolver`
> implementation which uses all the Spring infrastructure for accessing and
> reading resources in applications, and which is the recommended implementation
> in Spring-enabled applications.

### Chaining Template Resolvers

Also, a Template Engine can specify several template resolvers, in which case an
order can be established between them for template resolution so that, if the
first one is not able to resolve the template, the second one is asked, and so
on:

```java
ClassLoaderTemplateResolver classLoaderTemplateResolver = new ClassLoaderTemplateResolver();
classLoaderTemplateResolver.setOrder(Integer.valueOf(1));

WebApplicationTemplateResolver webApplicationTemplateResolver = 
        new WebApplicationTemplateResolver(application);
webApplicationTemplateResolver.setOrder(Integer.valueOf(2));

templateEngine.addTemplateResolver(classLoaderTemplateResolver);
templateEngine.addTemplateResolver(webApplicationTemplateResolver);
```

When several template resolvers are applied, it is recommended to specify
patterns for each template resolver so that Thymeleaf can quickly discard those
template resolvers that are not meant to resolve the template, enhancing
performance. Doing this is not a requirement, but a recommendation:

```java
ClassLoaderTemplateResolver classLoaderTemplateResolver = new ClassLoaderTemplateResolver();
classLoaderTemplateResolver.setOrder(Integer.valueOf(1));
// This classloader will not be even asked for any templates not matching these patterns 
classLoaderTemplateResolver.getResolvablePatternSpec().addPattern("/layout/*.html");
classLoaderTemplateResolver.getResolvablePatternSpec().addPattern("/menu/*.html");

WebApplicationTemplateResolver webApplicationTemplateResolver = 
        new WebApplicationTemplateResolver(application);
webApplicationTemplateResolver.setOrder(Integer.valueOf(2));
```

If these *resolvable patterns* are not specified, we will be relying on the
specific capabilities of each of the `ITemplateResolver` implementations we are
using. Note that not all implementations might be able to determine the
existence of a template before resolving, and thus could always consider a
template as *resolvable* and break the resolution chain (not allowing other
resolvers to check for the same template), but then be unable to read the real
resource.

All the `ITemplateResolver` implementations that are included with core
Thymeleaf include a mechanism that will allow us to make the resolvers *really
check* if a resource exists before considering it *resolvable*. It is the
`checkExistence` flag, which works like:

```java
ClassLoaderTemplateResolver classLoaderTemplateResolver = new ClassLoaderTemplateResolver();
classLoaderTemplateResolver.setOrder(Integer.valueOf(1));
classLoaderTemplateResolver.setCheckExistence(true);
```

This `checkExistence` flag forces the resolver to perform a *real check* for
resource existence during the resolution phase (and let the following resolver
in the chain be called if existence check returns false). While this might sound
good in every case, in most cases this will mean a double access to the resource
itself (once for checking existence, another time for reading it), and could be
a performance issue in some scenarios, e.g. remote URL-based template resources
-- a potential performance issue that might anyway get largely mitigated by the
use of the template cache (in which case templates will only be *resolved* the
first time they are accessed).

## Message Resolvers

We did not explicitly specify a Message Resolver implementation for our Grocery
application, and as it was explained before, this meant that the implementation
being used was an `org.thymeleaf.messageresolver.StandardMessageResolver` object.

`StandardMessageResolver` is the standard implementation of the `IMessageResolver` 
interface, but we could create our own if we wanted, adapted to the specific
needs of our application.

> The Thymeleaf + Spring integration packages offer by default an `IMessageResolver`
> implementation which uses the standard Spring way of retrieving externalized
> messages, by using `MessageSource` beans declared at the Spring Application
> Context.

### Standard Message Resolver

So how does `StandardMessageResolver` look for the messages requested at a
specific template?

If the template name is `home` and it is located in `/WEB-INF/templates/home.html`,
and the requested locale is `gl_ES` then this resolver will look for messages in
the following files, in this order:

 * `/WEB-INF/templates/home_gl_ES.properties`
 * `/WEB-INF/templates/home_gl.properties`
 * `/WEB-INF/templates/home.properties`

Refer to the JavaDoc documentation of the `StandardMessageResolver` class for
more detail on how the complete message resolution mechanism works.

### Configuring message resolvers

What if we wanted to add a message resolver (or more) to the Template Engine?
Easy:

```java
// For setting only one
templateEngine.setMessageResolver(messageResolver);

// For setting more than one
templateEngine.addMessageResolver(messageResolver);
```

And why would we want to have more than one message resolver? For the same
reason as template resolvers: message resolvers are ordered and if the first one
cannot resolve a specific message, the second one will be asked, then the third,
etc.

## Conversion Services

The *conversion service* that enables us to perform data conversion and
formatting operations by means of the *double-brace* syntax (`${{...}}`) is
actually a feature of the Standard Dialect, not of the Thymeleaf Template Engine
itself.

As such, the way to configure it is by setting our custom implementation of the
`IStandardConversionService` interface directly into the instance of `StandardDialect`
that is being configured into the template engine. Like:

```java
IStandardConversionService customConversionService = ...

StandardDialect dialect = new StandardDialect();
dialect.setConversionService(customConversionService);

templateEngine.setDialect(dialect);
```

> Note that the thymeleaf-spring3 and thymeleaf-spring4 packages contain the
> `SpringStandardDialect`, and this dialect already comes pre-configured with an
> implementation of `IStandardConversionService` that integrates Spring's own
> *Conversion Service* infrastructure into Thymeleaf.

## Logging

Thymeleaf pays quite a lot of attention to logging, and always tries to offer
the maximum amount of useful information through its logging interface.

The logging library used is `slf4j,` which in fact acts as a bridge to whichever
logging implementation we might want to use in our application (for example, `log4j`).

Thymeleaf classes will log `TRACE`, `DEBUG` and `INFO`-level information,
depending on the level of detail we desire, and besides general logging it will
use three special loggers associated with the TemplateEngine class which we can
configure separately for different purposes:

 * `org.thymeleaf.TemplateEngine.CONFIG` will output detailed configuration of
   the library during initialization.
 * `org.thymeleaf.TemplateEngine.TIMER` will output information about the amount
   of time taken to process each template (useful for benchmarking!)
 * `org.thymeleaf.TemplateEngine.cache` is the prefix for a set of loggers that
   output specific information about the caches. Although the names of the cache
   loggers are configurable by the user and thus could change, by default they
   are:
    * `org.thymeleaf.TemplateEngine.cache.TEMPLATE_CACHE`
    * `org.thymeleaf.TemplateEngine.cache.EXPRESSION_CACHE`

An example configuration for Thymeleaf's logging infrastructure, using `log4j`,
could be:

```
log4j.logger.org.thymeleaf=DEBUG
log4j.logger.org.thymeleaf.TemplateEngine.CONFIG=TRACE
log4j.logger.org.thymeleaf.TemplateEngine.TIMER=TRACE
log4j.logger.org.thymeleaf.TemplateEngine.cache.TEMPLATE_CACHE=TRACE
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#more-on-configuration) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

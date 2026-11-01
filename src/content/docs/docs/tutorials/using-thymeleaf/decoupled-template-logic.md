---
title: "Decoupled Template Logic"
description: "So far we have worked for our Grocery Store with templates done the usual way, with logic being inserted into our templates in the form of attributes."
sidebar:
  order: 17
---

## Decoupled logic: The concept

So far we have worked for our Grocery Store with templates done the *usual way*,
with logic being inserted into our templates in the form of attributes.

But Thymeleaf also allows us to completely *decouple* the template markup from
its logic, allowing the creation of **completely logic-less markup templates**
in the `HTML` and `XML` template modes.

The main idea is that template logic will be defined in a separate *logic file*
(more exactly a *logic resource*, as it doesn't need to be a *file*). By default,
that logic resource will  be an additional file living in the same place (e.g.
folder) as the template file, with the same name but with `.th.xml` extension:

```
/templates
+->/home.html
+->/home.th.xml
```

So the `home.html` file can be completely logic-less. It might look like this:

```html
<!DOCTYPE html>
<html>
  <body>
    <table id="usersTable">
      <tr>
        <td class="username">Jeremy Grapefruit</td>
        <td class="usertype">Normal User</td>
      </tr>
      <tr>
        <td class="username">Alice Watermelon</td>
        <td class="usertype">Administrator</td>
      </tr>
    </table>
  </body>
</html>
```

Absolutely no Thymeleaf code there. This is a template file that a designer with
no Thymeleaf or templating knowledge could have created, edited and/or
understood. Or a fragment of HTML provided by some external system with no
Thymeleaf hooks at all.

Let's now turn that `home.html` template into a Thymeleaf template by creating 
our additional `home.th.xml` file like this:

```xml
<?xml version="1.0"?>
<thlogic>
  <attr sel="#usersTable" th:remove="all-but-first">
    <attr sel="/tr[0]" th:each="user : ${users}">
      <attr sel="td.username" th:text="${user.name}" />
      <attr sel="td.usertype" th:text="#{|user.type.${user.type}|}" />
    </attr>
  </attr>
</thlogic>
```

Here we can see a lot of `<attr>` tags inside a `thlogic` block. Those `<attr>`
tags perform *attribute injection* on nodes of the original template selected by
means of their `sel` attributes, which contain Thymeleaf *markup selectors*
(actually *AttoParser markup selectors*). 

Also note that `<attr>` tags can be nested so that their selectors are *appended*.
That `sel="/tr[0]"` above, for example, will be processed as `sel="#usersTable/tr[0]"`.
And the selector for the user name `<td>` will be processed as `sel="#usersTable/tr[0]//td.username"`.

So once merged, both files seen above will be the same as:

```html
<!DOCTYPE html>
<html>
  <body>
    <table id="usersTable" th:remove="all-but-first">
      <tr th:each="user : ${users}">
        <td class="username" th:text="${user.name}">Jeremy Grapefruit</td>
        <td class="usertype" th:text="#{|user.type.${user.type}|}">Normal User</td>
      </tr>
      <tr>
        <td class="username">Alice Watermelon</td>
        <td class="usertype">Administrator</td>
      </tr>
    </table>
  </body>
</html>
```

This looks more familiar, and is indeed less *verbose* than creating two
separate files. But the advantage of *decoupled templates* is that we can
give for our templates total independence from Thymeleaf, and therefore better
maintainability from the design standpoint.

Of course some *contracts* between designers or developers will still be needed
-- e.g. the fact that the users `<table>` will need an `id="usersTable"` --, but
in many scenarios a pure-HTML template will be a much better communication
artifact between design and development teams.

## Configuring decoupled templates

### Enabling decoupled templates

Decoupled logic will not be expected for every template by default. Instead, the
configured template resolvers (implementations of `ITemplateResolver`) will need
to specifically mark the templates they resolve as *using decoupled logic*.

Except for `StringTemplateResolver` (which does not allow decoupled logic), all
other out-of-the-box implementations of `ITemplateResolver` will provide a flag
called `useDecoupledLogic` that will mark all templates resolved by that
resolver as potentially having all or part of its logic living in a separate
resource:

```java
final WebApplicationTemplateResolver templateResolver = 
        new WebApplicationTemplateResolver(application);
...
templateResolver.setUseDecoupledLogic(true);
```

### Mixing coupled and decoupled logic

Decoupled template logic, when enabled, is not a requirement. When enabled, it
means that the engine will *look for* a resource containing decoupled logic,
parsing and merging it with the original template if it exists. No error will be
thrown if the decoupled logic resource does not exist.

Also, in the same template we can mix both *coupled* and *decoupled* logic, for
example by adding some Thymeleaf attributes at the original template file but
leaving others for the separate decoupled logic file. The most common case for
this is using the new (in v3.0) `th:ref` attribute.

## The th:ref attribute

`th:ref` is only a marker attribute. It does nothing from the processing
standpoint and simply disappears when the template is processed, but its
usefulness lies in the fact that it acts as a *markup reference*, i.e. it can be
resolved by name from a *markup selector* just like a *tag name* or a *fragment*
(`th:fragment`).

So if we have a selector like:

```xml
  <attr sel="whatever" .../>
```

This will match:

 * Any `<whatever>` tags.
 * Any tags with a `th:fragment="whatever"` attribute.
 * Any tags with a `th:ref="whatever"` attribute.

What is the advantage of `th:ref` against, for example, using a pure-HTML `id`
attribute? Merely the fact that we might not want to add so many `id` and `class`
attributes to our tags to act as *logic anchors*, which might end up *polluting*
our output. 

And in the same sense, what is the disadvantage of `th:ref`? Well, obviously
that we'd be adding a bit of Thymeleaf logic (*"logic"*) to our templates.

Note this applicability of the `th:ref` attribute **does not only apply to
decoupled logic template files**: it works the same in other types of scenarios,
like in fragment expressions (`~{...}`).

## Performance impact of decoupled templates

The impact is extremely small. When a resolved template is marked to use
decoupled logic and it is not cached, the template logic resource will be
resolved first, parsed and processed into a sequence of instructions in-memory:
basically a list of attributes to be injected to each markup selector.

But this is the only *additional step* required because, after this, the real
template will be parsed, and while it is parsed these attributes will be
injected *on-the-fly* by the parser itself, thanks to the advanced capabilities
for node selection in AttoParser. So parsed nodes will come out of the parser as
if they had their injected attributes written in the original template file.

The biggest advantage of this? When a template is configured to be cached, it
will be cached already containing the injected attributes. So the overhead of
using *decoupled templates* for cacheable templates, once they are cached, 
will be absolutely *zero*.

## Resolution of decoupled logic

The way Thymeleaf resolves the decoupled logic resources corresponding to each
template is configurable by the user. It is determined by an extension point,
the `org.thymeleaf.templateparser.markup.decoupled.IDecoupledTemplateLogicResolver`, 
for which a *default implementation* is provided: `StandardDecoupledTemplateLogicResolver`.

What does this standard implementation do?

 * First, it applies a `prefix` and a `suffix` to the *base name* of the
   template resource (obtained by means of its `ITemplateResource#getBaseName()`
   method). Both prefix and suffix can be configured and, by default, the prefix
   will be empty and the suffix will be `.th.xml`.
 * Second, it asks the template resource to resolve a *relative resource* with
   the computed name by means of its `ITemplateResource#relative(String relativeLocation)`
   method.

The specific implementation of `IDecoupledTemplateLogicResolver` to be used can
be configured at the `TemplateEngine` easily:

```java
final StandardDecoupledTemplateLogicResolver decoupledResolver = 
        new StandardDecoupledTemplateLogicResolver();
decoupledResolver.setPrefix("../viewlogic/");
...
templateEngine.setDecoupledTemplateLogicResolver(decoupledResolver);
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#decoupled-template-logic) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

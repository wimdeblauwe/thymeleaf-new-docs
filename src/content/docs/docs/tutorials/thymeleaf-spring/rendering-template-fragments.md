---
title: "Rendering Template Fragments"
description: "Thymeleaf offers the possibility to render only part of a template as the result of its execution: a fragment."
sidebar:
  order: 11
---

Thymeleaf offers the possibility to render only part of a template as the result of its execution: a *fragment*. 

This can be a useful componentization tool. For example, it can be used at controllers that execute on AJAX calls, which might return markup fragments of a page that is already loaded at the browser (for updating a select, enabling/disabling buttons...).

Fragmentary rendering can be achieved by using Thymeleaf's *fragment specs*: objects implementing the `org.thymeleaf.fragment.IFragmentSpec` interface.

The most common of these implementations is `org.thymeleaf.standard.fragment.StandardDOMSelectorFragmentSpec`, which allows specifying a fragment using a DOM Selector exactly like the ones used at `th:include` or `th:replace`.

## Specifying fragments in view beans

*View beans* are beans of the `org.thymeleaf.spring6.view.ThymeleafView` class declared at the application 
context (`@Bean` declarations if you are using Java configuration). They allow the specification of fragments like this:

```java
@Bean(name="content-part")
@Scope("prototype")
public ThymeleafView someViewBean() {
    ThymeleafView view = new ThymeleafView("index"); // templateName = 'index'
    view.setMarkupSelector("content");
    return view;
}
``` 

Given the above bean definition, if our controller returns `content-part` (the name of the above bean)...

```java    
@RequestMapping("/showContentPart")
public String showContentPart() {
    ...
    return "content-part";
}
```

...thymeleaf will return only the `content` fragment of the `index` template -- which location will 
probably be something like `/WEB-INF/templates/index.html`, once prefix and suffix are applied. So 
the result will be completely equivalent to specifying `index :: content`:

```html
<!DOCTYPE html>
<html>
  ...
  <body>
    ...
    <div th:fragment="content">
      Only this div will be rendered!
    </div>
    ...
  </body>
</html>
```

Note also that, thanks to the power of Thymeleaf Markup Selectors, we could select a fragment in a 
template without needing any `th:fragment` attributes at all. Let's use the `id` attribute, for example:

```java
@Bean(name="content-part")
@Scope("prototype")
public ThymeleafView someViewBean() {
    ThymeleafView view = new ThymeleafView("index"); // templateName = 'index'
    view.setMarkupSelector("#content");
    return view;
}
``` 

...which will perfectly select:

```html
<!DOCTYPE html>
<html>
  ...
  <body>
    ...
    <div id="content">
      Only this div will be rendered!
    </div>
    ...
  </body>
</html>
```

## Specifying fragments in controller return values

Instead of declaring *view beans*, fragments can be specified from the controllers themselves by using the 
syntax of *fragment expressions*. Just like in `th:insert` or `th:replace` attributes:

```java    
@RequestMapping("/showContentPart")
public String showContentPart() {
    ...
    return "index :: content";
}
```

Of course, again the full power of DOM Selectors is available, so we could select our fragment based on 
standard HTML attributes, like `id="content"`:

```java    
@RequestMapping("/showContentPart")
public String showContentPart() {
    ...
    return "index :: #content";
}
```

And we can also use parameters, like:

```java    
@RequestMapping("/showContentPart")
public String showContentPart() {
    ...
    return "index :: #content ('myvalue')";
}
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#rendering-template-fragments) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

---
title: "Views and View Resolvers"
description: "There are two interfaces in Spring MVC that conform the core of its templating system."
sidebar:
  order: 4
---

## Views and View Resolvers in Spring MVC

There are two interfaces in Spring MVC that conform the core of its templating
system:

 * `org.springframework.web.servlet.View`
 * `org.springframework.web.servlet.ViewResolver`

Views model pages in our applications and allow us to modify and predefine their
behaviour by defining them as beans. Views are in charge of rendering the actual
HTML interface, usually by the execution of some template engine like Thymeleaf.

ViewResolvers are the objects in charge of obtaining View objects for a specific
operation and locale. Typically, controllers ask ViewResolvers to forward to a
view with a specific name (a String returned by the controller method), and then
all the view resolvers in the application execute in ordered chain until one of
them is able to resolve that view, in which case a View object is returned and
control is passed to it for the renderization of HTML.

> Note that not all pages in our applications have to be defined as Views, but
> only those which behaviour we wish to be non-standard or configured in a
> specific way (for example, by wiring some special beans to it). If a
> ViewResolver is asked a view that has no corresponding bean --which is the
> common case--, a new View object is created ad hoc and returned.

A typical configuration for a JSP+JSTL ViewResolver in a Spring MVC application
from the past looked like this:

```xml
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
  <property name="viewClass" value="org.springframework.web.servlet.view.JstlView" />
  <property name="prefix" value="/WEB-INF/jsps/" />
  <property name="suffix" value=".jsp" />
  <property name="order" value="2" />
  <property name="viewNames" value="*jsp" />
</bean>
```

A quick look at its properties is enough to know about how it was configured:

 * `viewClass` establishes the class of the View instances. This is needed for a
   JSP resolver, but it will not be needed at all when we're working with Thymeleaf.
 * `prefix` and `suffix` work in a similar way to the attributes of the same
   names in Thymeleaf's TemplateResolver objects.
 * `order` establishes the order in which the ViewResolver will be queried in
   the chain.
 * `viewNames` allows the definition (with wildcards) of the view names that
   will be resolved by this ViewResolver.

## Views and View Resolvers in Thymeleaf

Thymeleaf offers implementations for the two interfaces mentioned above:

 * `org.thymeleaf.spring6.view.ThymeleafView`
 * `org.thymeleaf.spring6.view.ThymeleafViewResolver`

These two classes will be in charge of processing Thymeleaf templates as a
result of the execution of controllers.

Configuration of the Thymeleaf View Resolver is very similar to that of JSP:

```java
@Bean
public ThymeleafViewResolver viewResolver(){
    ThymeleafViewResolver viewResolver = new ThymeleafViewResolver();
    viewResolver.setTemplateEngine(templateEngine());
    // NOTE 'order' and 'viewNames' are optional
    viewResolver.setOrder(1);
    viewResolver.setViewNames(new String[] {".html", ".xhtml"});
    return viewResolver;
}
```

...or in XML:

```xml
<bean class="org.thymeleaf.spring6.view.ThymeleafViewResolver">
  <property name="templateEngine" ref="templateEngine" />
  <!-- NOTE 'order' and 'viewNames' are optional -->
  <property name="order" value="1" />
  <property name="viewNames" value="*.html,*.xhtml" />
</bean>
```

The `templateEngine` parameter is, of course, the `SpringTemplateEngine` object
we defined in the previous chapter. The other two (`order` and `viewNames`) are
both optional, and have the same meaning as in the JSP ViewResolver we saw
before.

Note that we do not need `prefix` or `suffix` parameters, because these are
already specified at the Template Resolver (which in turn is passed to the
Template Engine).

And what if we wanted to define a `View` bean and add some static variables to
it? Easy, just define a *prototype* bean for it:

```java
@Bean
@Scope("prototype")
public ThymeleafView mainView() {
    ThymeleafView view = new ThymeleafView("main"); // templateName = 'main'
    view.setStaticVariables(
        Collections.singletonMap("footer", "The ACME Fruit Company"));
    return view;
}
```

By doing this, you will be able to execute specifically this view bean
selecting it by bean name (`mainView`, in this case).

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#views-and-view-resolvers) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

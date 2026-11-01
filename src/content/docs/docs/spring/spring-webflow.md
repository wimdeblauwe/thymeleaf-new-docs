---
title: "Spring WebFlow"
description: "The Thymeleaf + Spring integration packages include integration with Spring WebFlow."
sidebar:
  order: 11
---

## Basic configuration

The Thymeleaf + Spring integration packages include integration with Spring
WebFlow.

_Note: Spring WebFlow 3.0+ is required when Thymeleaf is used with Spring 6, and
Spring WebFlow 2.5 is needed with Spring 5._

WebFlow includes some AJAX capabilities for rendering fragments of the displayed
page when specific events (_transitions_) are triggered, and in order to enable
Thymeleaf to attend these AJAX requests, we will have to use a different `ViewResolver`
implementation, configured like this:

```java
@Bean
public FlowDefinitionRegistry flowRegistry() {
    // NOTE: Additional configuration might be needed in your app
    return getFlowDefinitionRegistryBuilder()
            .addFlowLocation("...")
            .setFlowBuilderServices(flowBuilderServices())
            .build();
}

@Bean
public FlowExecutor flowExecutor() {
    // NOTE: Additional configuration might be needed in your app
    return getFlowExecutorBuilder(flowRegistry()).build();
}

@Bean
public FlowBuilderServices flowBuilderServices() {
    // NOTE: Additional configuration might be needed in your app
    return getFlowBuilderServicesBuilder()
            .setViewFactoryCreator(viewFactoryCreator())
            .build();
}

@Bean
public ViewFactoryCreator viewFactoryCreator() {
    MvcViewFactoryCreator factoryCreator = new MvcViewFactoryCreator();
    factoryCreator.setViewResolvers(
            Collections.singletonList(thymeleafViewResolver()));
    factoryCreator.setUseSpringBeanBinding(true);
    return factoryCreator;
}

@Bean
public ViewResolver thymeleafViewResolver() {
    AjaxThymeleafViewResolver viewResolver = new AjaxThymeleafViewResolver();
    // We need to set a special ThymeleafView implementation: FlowAjaxThymeleafView
    viewResolver.setViewClass(FlowAjaxThymeleafView.class);
    viewResolver.setTemplateEngine(templateEngine());
    return viewResolver;
}

```

Note the above is not a complete configuration: you will still need to configure your handlers, etc. Refer to the
Spring WebFlow documentation for that.

From here on, you can specify Thymeleaf templates in your view-state's:

```xml
<view-state id="detail" view="bookingDetail">
    ...
</view-state>
```

In the above example, `bookingDetail` is a Thymeleaf template specified in the
usual way, understandable by any of the _Template Resolvers_ configured at the `TemplateEngine`.

## AJAX fragments in Spring WebFlow

> Note that what is explained here is just the way to create AJAX fragments to be used
> with Spring WebFlow. If you are not using WebFlow, creating a Spring MVC controller that
> responds to an AJAX request and returns a chunk of HTML is as straightforward as creating
> any other template-returning controller, with the only exception that you would probably
> be returning a fragment like `"main :: admin"` from your controller method.

WebFlow allows the specification of fragments to be rendered via AJAX with `<render>`
tags, like this:

```xml
<view-state id="detail" view="bookingDetail">
    <transition on="updateData">
        <render fragments="hoteldata"/>
    </transition>
</view-state>
```

These fragments (`hoteldata`, in this case) can be a comma-separated list of
fragments specified at the markup with `th:fragment`:

```xml
<div id="data" th:fragment="hoteldata">
    This is a content to be changed
</div>
```

_Always remember that the specified fragments must have an `id` attribute, so
that the Spring JavaScript libraries running on the browser are capable of
substituting the markup._

`<render>` tags can also be specified using DOM selectors:

```html
<view-state id="detail" view="bookingDetail">
    <transition on="updateData">
        <render fragments="[//div[@id='data']]"/>
    </transition>
</view-state>
```

...and this will mean no `th:fragment` is needed:

```html
<div id="data">
    This is a content to be changed
</div>
```

As for the code that triggers the `updateData` transition, it looks like:

```html
<script type="text/javascript" th:src="@{/resources/dojo/dojo.js}"></script>
<script type="text/javascript" th:src="@{/resources/spring/Spring.js}"></script>
<script type="text/javascript" th:src="@{/resources/spring/Spring-Dojo.js}"></script>

  ...

<form id="triggerform" method="post" action="">
    <input type="submit" id="doUpdate" name="_eventId_updateData" value="Update now!" />
</form>

<script type="text/javascript">
    Spring.addDecoration(
        new Spring.AjaxEventDecoration({formId:'triggerform',elementId:'doUpdate',event:'onclick'}));
</script>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#spring-webflow-integration) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

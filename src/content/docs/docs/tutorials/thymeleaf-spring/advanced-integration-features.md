---
title: "Advanced Integration Features"
description: "Thymeleaf seamlessly integrates with Spring's RequestDataValueProcessor interface."
sidebar:
  order: 12
---

## Integration with `RequestDataValueProcessor`

Thymeleaf seamlessly integrates with Spring's `RequestDataValueProcessor` interface. This interface allows the interception of link URLs, form URLs and form field values before they are written to the markup result, as well as transparently adding hidden form fields that enable security features like e.g. protection against CSRF (Cross-Site Request Forgery).

An implementation of `RequestDataValueProcessor` can be easily configured at the Application Context. It needs to implement
the `org.springframework.web.servlet.support.RequestDataValueProcessor` interface and have 
`requestDataValueProcessor` as a bean name:

```java
@Bean
public RequestDataValueProcessor requestDataValueProcessor() {
  return new MyRequestDataValueProcessor();
}
```

...and Thymeleaf will use it this way:

  * `th:href` and `th:src` call `RequestDataValueProcessor.processUrl(...)` before rendering the URL.

  * `th:action` calls `RequestDataValueProcessor.processAction(...)` before rendering the form's `action` attribute, and additionally it detects when this attribute is being applied on a `<form>` tag ---which should be the only place, anyway---, and in such case calls `RequestDataValueProcessor.getExtraHiddenFields(...)` and adds the returned hidden fields just after the opening `<form>` tag (i.e. at the beginning of the form's body).

  * `th:value` calls `RequestDataValueProcessor.processFormFieldValue(...)` for rendering the value it refers to, unless there is a `th:field` present in the same tag (in which case `th:field` will take care).

  * `th:field` calls `RequestDataValueProcessor.processFormFieldValue(...)` for rendering the value of the field it applies to (or the tag body if it is a `<textarea>`).

> Note there are very few scenarios in which you would need to explicitly implement `RequestDataValueProcessor`
> in your application. In most cases, this will be used automatically by security libraries you transparently use, 
> like e.g. Spring Security's CSRF support.

## Building URIs to controllers

Spring allows the possibility to build links to annotated controllers directly from views, without the 
need to know the URIs these controllers are mapped to.

In Thymeleaf, this can be achieved by means of the `#mvc.url(...)` expression object method, which allows the 
specification of controller methods by the capital letters of the controller class they are in, followed by 
the name of the method itself. This is equivalent to JSP's `spring:mvcUrl(...)` custom function. 

For example, for:
```java
public class ExampleController {

    @RequestMapping("/data")
    public String getData(Model model) { ... return "template" }

    @RequestMapping("/data")
    public String getDataParam(@RequestParam String type) { ... return "template" }

}
```
The following code will create a link to it:
```html
<a th:href="${(#mvc.url('EC#getData')).build()}">Get Data Param</a>
<a th:href="${(#mvc.url('EC#getDataParam').arg(0,'internal')).build()}">Get Data Param</a>
``` 

You can read more about this mechanism 
at https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-methods/uri-building.html

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#advanced-integration-features) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

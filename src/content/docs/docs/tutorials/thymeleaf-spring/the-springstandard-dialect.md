---
title: "The SpringStandard Dialect"
description: "In order to achieve an easier and better integration, Thymeleaf provides a dialect which specifically implements all the needed features for it to work correctly with Spring."
sidebar:
  order: 3
---

In order to achieve an easier and better integration, Thymeleaf provides a
dialect which specifically implements all the needed features for it to work
correctly with Spring.

This specific dialect is based on the Thymeleaf Standard Dialect and is
implemented in a class called `org.thymeleaf.spring6.dialect.SpringStandardDialect`,
which in fact extends from `org.thymeleaf.standard.StandardDialect`.

Besides all the features already present in the Standard Dialect --and therefore
inherited--, the SpringStandard Dialect introduces the following specific
features:

 * Use Spring Expression Language (Spring EL or SpEL) as a variable expression
   language, instead of OGNL. Consequently, all `${...}` and `*{...}`
   expressions will be evaluated by Spring's Expression Language engine. Note also
   that support for the Spring EL compiler is available.
 * Access any beans in your application context using SpringEL's syntax: `${@myBean.doSomething()}`
 * New attributes for form processing: `th:field`, `th:errors` and `th:errorclass`, besides a new
   implementation of `th:object` that allows it to be used for form command
   selection.
 * An expression object and method, `#themes.code(...)`, which is equivalent
   to the `spring:theme` JSP custom tag.
 * An expression object and method, `#mvc.url(...)`, which is equivalent to 
   the `spring:mvcUrl(...)` JSP custom function. 

Note that most of the times _you shouldn't be using this dialect directly in a normal 
`TemplateEngine` object_ as a part of its configuration. Unless you have very specific
Spring integration needs, you should instead be creating an instance of a new template
engine class that performs all the required configuration steps automatically: 
`org.thymeleaf.spring6.SpringTemplateEngine`.

An example bean configuration:

```java
@Bean
public SpringResourceTemplateResolver templateResolver(){
    // SpringResourceTemplateResolver automatically integrates with Spring's own
    // resource resolution infrastructure, which is highly recommended.
    SpringResourceTemplateResolver templateResolver = new SpringResourceTemplateResolver();
    templateResolver.setApplicationContext(this.applicationContext);
    templateResolver.setPrefix("/WEB-INF/templates/");
    templateResolver.setSuffix(".html");
    // HTML is the default value, added here for the sake of clarity.
    templateResolver.setTemplateMode(TemplateMode.HTML);
    // Template cache is true by default. Set to false if you want
    // templates to be automatically updated when modified.
    templateResolver.setCacheable(true);
    return templateResolver;
}

@Bean
public SpringTemplateEngine templateEngine(){
    // SpringTemplateEngine automatically applies SpringStandardDialect and
    // enables Spring's own MessageSource message resolution mechanisms.
    SpringTemplateEngine templateEngine = new SpringTemplateEngine();
    templateEngine.setTemplateResolver(templateResolver());
    // Enabling the SpringEL compiler can speed up execution in most
    // scenarios, but might be incompatible with specific cases when
    // expressions in one template are reused across different data
    // types, so this flag is "false" by default for safer backwards
    // compatibility.
    templateEngine.setEnableSpringELCompiler(true);
    return templateEngine;
}
```

Or, using Spring's XML-based configuration:

```xml
<!-- SpringResourceTemplateResolver automatically integrates with Spring's own -->
<!-- resource resolution infrastructure, which is highly recommended.          -->
<bean id="templateResolver"
       class="org.thymeleaf.spring6.templateresolver.SpringResourceTemplateResolver">
  <property name="prefix" value="/WEB-INF/templates/" />
  <property name="suffix" value=".html" />
  <!-- HTML is the default value, added here for the sake of clarity.          -->
  <property name="templateMode" value="HTML" />
  <!-- Template cache is true by default. Set to false if you want             -->
  <!-- templates to be automatically updated when modified.                    -->
  <property name="cacheable" value="true" />
</bean>
    
<!-- SpringTemplateEngine automatically applies SpringStandardDialect and      -->
<!-- enables Spring's own MessageSource message resolution mechanisms.         -->
<bean id="templateEngine"
      class="org.thymeleaf.spring6.SpringTemplateEngine">
  <property name="templateResolver" ref="templateResolver" />
  <!-- Enabling the SpringEL compiler can speed up execution in most           -->
  <!-- scenarios, but might be incompatible with specific cases when           -->
  <!-- expressions in one template are reused across different data types, so  -->
  <!-- this flag is "false" by default for safer backwards compatibility.      -->
  <property name="enableSpringELCompiler" value="true" />
</bean>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#the-springstandard-dialect) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

---
title: "Spring Standard dialect"
description: "In order to achieve an easier and better integration, Thymeleaf provides a dialect which specifically implements all the needed features for it to work correctly with Spring."
sidebar:
  order: 2
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

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#the-springstandard-dialect) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

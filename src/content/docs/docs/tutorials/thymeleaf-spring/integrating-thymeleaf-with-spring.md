---
title: "Integrating Thymeleaf with Spring"
description: "Thymeleaf offers a set of Spring integrations that allow you to use it as a fully-featured substitute for JSP in Spring MVC applications."
sidebar:
  order: 2
---

Thymeleaf offers a set of Spring integrations that allow you to use it as a
fully-featured substitute for JSP in Spring MVC applications.

These integrations will allow you to:

 * Make the mapped methods in your Spring MVC `@Controller` objects forward to
   templates managed by Thymeleaf, exactly like you do with JSPs.
 * Use **Spring Expression Language** (Spring EL) instead of OGNL in your
   templates.
 * Create forms in your templates that are completely integrated with your
   form-backing beans and result bindings, including the use of property editors, conversion services and validation error handling.
 * Display internationalization messages from message files managed by Spring
   (through the usual `MessageSource` objects).
 * Resolve your templates using Spring's own resource resolution mechanisms.

Note that in order to fully understand this tutorial, you should have first gone
through the _"Using Thymeleaf"_ tutorial, which explains the Standard Dialect in depth.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#integrating-thymeleaf-with-spring) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

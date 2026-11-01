---
title: "Preface"
description: "This tutorial explains how Thymeleaf can be integrated with the Spring Framework, especially (but not only) Spring MVC."
sidebar:
  order: 1
---

This tutorial explains how Thymeleaf can be integrated with the Spring Framework, especially (but not only) Spring MVC.

Note that Thymeleaf has integrations for both versions 5.x and 6.x of the Spring Framework, provided by two
separate libraries called `thymeleaf-spring5` and `thymeleaf-spring6`. These libraries are packaged in separate
`.jar` files (`thymeleaf-spring5-{version}.jar` and `thymeleaf-spring6-{version}.jar`) and need to be added to your
classpath in order to use Thymeleaf's Spring integrations in your application.

The code samples and example application in this tutorial make use of **Spring 6.x** and its corresponding
Thymeleaf integrations, but the contents of this text are valid also for Spring 5.x. If your application uses
Spring 5.x, all you have to do is replace the `org.thymeleaf.spring6` package with `org.thymeleaf.spring5` in the
code samples. 

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#preface) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

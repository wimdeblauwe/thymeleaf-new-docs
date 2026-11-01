---
title: "Quickstart: Spring Boot"
description: "Create a Spring Boot application, render your first Thymeleaf template and set up template reloading."
sidebar:
  order: 3
---

In this guide you create a Spring Boot application that renders a list of seed starter varieties with Thymeleaf.

Tested with Spring Boot 4.1.2, which manages Thymeleaf 3.1.5, built for Java 21 and run on Java 25. The finished code is in [`samples/quickstart`](https://github.com/wimdeblauwe/thymeleaf-new-docs/tree/main/samples/quickstart).

## Prerequisites

- Java 17 or later
- Maven, or the Maven wrapper that the generated project includes

## Create the project

Go to [start.spring.io](https://start.spring.io) and generate a Maven project with the **Spring Web**, **Thymeleaf** and **Spring Boot DevTools** dependencies.

The two starters that matter here are in `pom.xml`:

```xml title="pom.xml"
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-thymeleaf</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc</artifactId>
		</dependency>
```

Boot configures the template engine for you. You don't need any Java configuration.

## Add a controller

A controller fills the model and returns a view name:

```java title="src/main/java/org/thymeleaf/samples/quickstart/SeedStarterController.java"
package org.thymeleaf.samples.quickstart;

import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SeedStarterController {

    @GetMapping("/")
    public String seedStarters(Model model) {
        model.addAttribute("title", "Seed starters");
        model.addAttribute("varieties", List.of("Thymus vulgaris", "Thymus serpyllum"));
        return "seedstarters";
    }
}
```

Boot adds the prefix `classpath:/templates/` and the suffix `.html`, so `seedstarters` resolves to `src/main/resources/templates/seedstarters.html`.

## Add a template

```html title="src/main/resources/templates/seedstarters.html"
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
  <meta charset="UTF-8">
  <title th:text="${title}">Page title</title>
</head>
<body>
  <h1 th:text="${title}">Page title</h1>
  <ul>
    <li th:each="variety : ${varieties}" th:text="${variety}">Thymus citriodorus</li>
  </ul>
</body>
</html>
```

- `th:text` replaces the element's body with the value of the expression. The value is HTML-escaped.
- `${...}` reads a value from the model.
- `th:each` repeats the `<li>` once per variety.

The `xmlns:th` declaration isn't required. It stops editors and validators from flagging `th:*` attributes as unknown.

## Run the application

```sh
./mvnw spring-boot:run
```

Open `http://localhost:8080` in a browser. The server sends this HTML:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Seed starters</title>
</head>
<body>
  <h1>Seed starters</h1>
  <ul>
    <li>Thymus vulgaris</li>
    <li>Thymus serpyllum</li>
  </ul>
</body>
</html>
```

The `th:*` attributes are gone, and so is the placeholder text. Open the template file directly in a browser and you see the placeholders instead. That's a [natural template](../natural-templates/).

## Reload templates during development

Boot caches parsed templates by default (`spring.thymeleaf.cache=true`), so template changes wouldn't normally show up until you restart. DevTools turns that cache off while you run the application from your project, so you only need to rebuild the changed template and refresh the page.

DevTools is left out of packaged builds by default, so production keeps the cache on.

## Common mistakes

- **Error resolving template:** the view name has to match the file's path below `src/main/resources/templates/`, without the `.html`.
- **The view name appears as plain text:** you used `@RestController`, which writes the return value to the response. Use `@Controller`.
- **The page shows the placeholder text:** the attribute is on the wrong element, or a `th:text` typo means Thymeleaf doesn't recognise it.

## Next steps

- [Syntax at a glance](../syntax-at-a-glance/) shows the Standard Dialect in one page.
- [Forms](../../spring/forms/) adds input handling.
- [Attributes reference](../../reference/attributes/) lists what each `th:*` attribute does.

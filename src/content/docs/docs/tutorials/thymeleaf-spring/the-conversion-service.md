---
title: "The Conversion Service"
description: "As explained before, Thymeleaf can make use of a Conversion Service registered at the Application Context."
sidebar:
  order: 10
---

## Configuration

As explained before, Thymeleaf can make use of a Conversion Service registered at the Application Context. Our
application configuration class, by implementing Spring's own `WebMvcConfigurer` interface, will automatically
register such conversion service, which we can configure by adding the *formatters* that we need. Let's see 
again what it looks like:

```java
@Override
public void addFormatters(final FormatterRegistry registry) {
    super.addFormatters(registry);
    registry.addFormatter(varietyFormatter());
    registry.addFormatter(dateFormatter());
}

@Bean
public VarietyFormatter varietyFormatter() {
    return new VarietyFormatter();
}

@Bean
public DateFormatter dateFormatter() {
    return new DateFormatter();
}
```

## Double-brace syntax

The Conversion Service can be easily applied in order to convert/format any object into String. This 
is done by means of the double-brace expression syntax:

  * For variable expressions: `${{...}}`
  * For selection expressions: `*{{...}}`
  
So, for example, given an Integer-to-String converter that adds commas as a thousands separator, this:

```html
<p th:text="${val}">...</p>
<p th:text="${{val}}">...</p>
```

...should result in:

```html
<p>1234567890</p>
<p>1,234,567,890</p>
```

## Use in forms

We saw before that every `th:field` attribute will always apply the conversion service, so this:

```html
<input type="text" th:field="*{datePlanted}" />
```

...is actually equivalent to:

```html
<input type="text" th:field="*{{datePlanted}}" />
```

Note that, per requirement of Spring, this is the only scenario in which the Conversion Service 
is applied in expressions using single-brace syntax.

## `#conversions` utility object

The `#conversions` expression utility object allows the manual execution of the Conversion Service wherever needed:

```html
<p th:text="${'Val: ' + #conversions.convert(val,'String')}">...</p>
```

Syntax for this utility object:

  * `#conversions.convert(Object,Class)`: converts the object to the specified class.
  * `#conversions.convert(Object,String)`: same as above, but specifying the target class as a String (note the `java.lang.` package can be omitted).

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#the-conversion-service) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

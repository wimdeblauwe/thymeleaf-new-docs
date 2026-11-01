---
title: "Conversion and formatting"
description: "As explained before, Thymeleaf can make use of a Conversion Service registered at the Application Context."
sidebar:
  order: 6
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

## Configuring a Conversion Service

In order to allow easy formatting of `Date` and also `Variety` objects in our view layer, we 
configured our application so that a Spring `ConversionService` object was created and
initialized (by the `WebMvcConfigurer` we implement) with a couple of *formatter*
objects we will need. See it again:

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

Spring *formatters* are implementations of the `org.springframework.format.Formatter` 
interface. For more information on how the Spring conversion infrastructure works, 
see the docs at [spring.io](https://docs.spring.io/spring-framework/reference/core/validation/format.html).

Let's have a look at the `DateFormatter`, which formats dates according to a format 
string present at the `date.format` message key of our `Messages.properties`:

```java
public class DateFormatter implements Formatter<Date> {

    @Autowired
    private MessageSource messageSource;


    public DateFormatter() {
        super();
    }

    public Date parse(final String text, final Locale locale) throws ParseException {
        final SimpleDateFormat dateFormat = createDateFormat(locale);
        return dateFormat.parse(text);
    }

    public String print(final Date object, final Locale locale) {
        final SimpleDateFormat dateFormat = createDateFormat(locale);
        return dateFormat.format(object);
    }

    private SimpleDateFormat createDateFormat(final Locale locale) {
        final String format = this.messageSource.getMessage("date.format", null, locale);
        final SimpleDateFormat dateFormat = new SimpleDateFormat(format);
        dateFormat.setLenient(false);
        return dateFormat;
    }

}
```

The `VarietyFormatter` automatically converts between our `Variety` entities and the way we want to use them in our forms (basically, by their `id` field values):

```java
public class VarietyFormatter implements Formatter<Variety> {

    @Autowired
    private VarietyService varietyService;


    public VarietyFormatter() {
        super();
    }

    public Variety parse(final String text, final Locale locale) throws ParseException {
        final Integer varietyId = Integer.valueOf(text);
        return this.varietyService.findById(varietyId);
    }


    public String print(final Variety object, final Locale locale) {
        return (object != null ? object.getId().toString() : "");
    }

}
```

We will learn more on how these formatters affect the way our data is displayed later on. 

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [The Conversion Service](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#the-conversion-service), [Configuring a Conversion Service](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#configuring-a-conversion-service).*

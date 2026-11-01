---
title: "Forms"
description: "Bind HTML forms to Java objects with th:object and th:field, and handle CSRF protection and HTTP methods."
sidebar:
  order: 4
---

Spring MVC binds form fields to a Java object, called the *command object* or form-backing bean. In the template, `th:object` selects that object and `th:field` connects each input to one of its properties.

The examples come from the Seed Starter Manager in [`samples/showcase`](https://github.com/wimdeblauwe/thymeleaf-new-docs/tree/main/samples/showcase), tested with Spring Boot 4.1.2, Spring Security and Thymeleaf 3.1.5.

## A minimal form

The controller puts an empty object in the model to show the form, and receives a filled one on submit:

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("seedStarter", new SeedStarter());
        return "seedstarters/form";
    }
```

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @PostMapping
    public String create(@Valid SeedStarter seedStarter, BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "seedstarters/form";
        }
        seedStarters.save(seedStarter);
        return "redirect:/seedstarters";
    }
```

The template names the object, and each field names a property:

```html title="src/main/resources/templates/seedstarters/form.html"
  <form action="#" th:action="@{/seedstarters}" th:object="${seedStarter}" method="post">
    <div>
      <label for="name">Name</label>
      <input type="text" th:field="*{name}" th:errorclass="invalid">
      <p th:errors="*{name}">Must not be blank</p>
    </div>
```

This renders:

```html
<form action="/seedstarters" method="post"><input type="hidden" name="_csrf" value="..."/>
  <div>
    <label for="name">Name</label>
    <input type="text" id="name" name="name" value="">
  </div>
```

`th:field` set the `id`, `name` and `value`. `th:errors` rendered nothing, because there's no error yet. The hidden `_csrf` field comes from `th:action`, as described in [CSRF protection](#csrf-protection).

### Rules for th:object and th:field

- `th:object` on a form has to be a variable expression naming a model attribute, with no property navigation. `${seedStarter}` works, and `${seedStarter.data}` doesn't.
- You can't use another `th:object` inside the form.
- The name has to match the model attribute. By default, Spring names the attribute after the class, so a `SeedStarter` parameter becomes `seedStarter`.
- `th:field` takes a selection expression, `*{...}`, which can include property navigation such as `*{rows[0].variety}`.

## Validation errors

When a submitted form is invalid, return the form view with the `BindingResult`. `th:errors` shows the messages for a field, and `th:errorclass` adds a class to the input. Submitting an empty name gives:

```html
<input type="text" id="name" name="name" value="" class="invalid">
<p>must not be blank</p>
```

[Validation and errors](../validation-and-errors/) has the details.

## CSRF protection

If Spring Security is on the classpath, it requires a CSRF token on every `POST`, `PUT`, `PATCH` and `DELETE` request. In the sample, a `POST` without a token gets a `403 Forbidden`.

You usually don't have to do anything, because **`th:action` adds the token for you**. It calls Spring's `RequestDataValueProcessor`, which Spring Security provides, and places the hidden field at the start of the form. The form needs `th:action`, because a plain `action` attribute doesn't get a token.

For requests that don't come from a `<form>`, such as JavaScript or htmx, send the token in a header. Spring Security exposes the current token as `_csrf`, so a template can read it. See [Partial page updates with htmx](../../interactive-uis/partial-page-updates/#send-the-csrf-token).

## HTTP methods other than POST

Browsers can only send `GET` and `POST` from a form. To map a form to `@PutMapping` or `@DeleteMapping`, use `th:method`:

```html title="src/main/resources/templates/seedstarters/edit.html"
  <form th:action="@{/seedstarters/{id}(id=${seedStarter.id})}" th:method="delete">
    <button type="submit">Delete</button>
  </form>
```

Thymeleaf renders `method="post"`, and adds a hidden `_method` field:

```html
<form action="/seedstarters/1" method="post"><input type="hidden" name="_csrf" value="..."/><input type="hidden" name="_method" value="delete"/>
  <button type="submit">Delete</button>
</form>
```

That field only has an effect if the server reads it. Spring's `HiddenHttpMethodFilter` does this, and it's off by default in Spring Boot, so turn it on:

```properties title="src/main/resources/application.properties"
spring.mvc.hiddenmethod.filter.enabled=true
```

The request then reaches your `@DeleteMapping`:

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @DeleteMapping("/{id}")
    public String delete(@PathVariable long id) {
        seedStarters.deleteById(id);
        return "redirect:/seedstarters";
    }
```

:::caution
`th:method` only adds the `_method` field on a `<form>`, and a plain `method="delete"` attribute doesn't work: the browser falls back to `GET`.
:::

## Field types

`th:field` adapts to the element it's on. It also applies your conversion service, so a date field shows the formatted value. The value is always HTML-escaped, and you can't turn that off.

HTML5 input types such as `type="date"` work too:

```html title="src/main/resources/templates/seedstarters/form.html"
      <input type="date" th:field="*{datePlanted}" th:errorclass="invalid">
```

The `LocalDate` property is annotated with `@DateTimeFormat(iso = DateTimeFormat.ISO.DATE)`, which matches the format that `type="date"` uses.

### Checkboxes

A boolean property needs one checkbox. A label needs the generated `id`, which `#ids.prev(...)` gives you, and which has to come after the input:

```html title="src/main/resources/templates/seedstarters/form.html"
      <input type="checkbox" th:field="*{covered}">
      <label th:for="${#ids.prev('covered')}">Covered</label>
```

For a collection, repeat the checkbox and give each one a `th:value`:

```html title="src/main/resources/templates/seedstarters/form.html"
      <li th:each="feature : ${allFeatures}">
        <input type="checkbox" th:field="*{features}" th:value="${feature}">
        <label th:for="${#ids.prev('features')}"
               th:text="#{${'seedstarter.feature.' + feature}}">Heating</label>
      </li>
```

```html
<li>
  <input type="checkbox" id="features1" name="features" value="FERTILIZER"><input type="hidden" name="_features" value="on"/>
  <label for="features1">Fertilizer used</label>
</li>
```

Ids get a sequence number, because several inputs share a property. The hidden `_features` field tells Spring the field was on the form, since browsers don't send unchecked checkboxes. If the property already contains a value, `th:field` adds `checked="checked"`.

Label ids also work before the input, with `${#ids.next('covered')}`.

### Radio buttons

Radio buttons work like a multi-valued checkbox, but the property holds one value:

```html title="src/main/resources/templates/seedstarters/form.html"
      <li th:each="type : ${allTypes}">
        <input type="radio" th:field="*{type}" th:value="${type}">
        <label th:for="${#ids.prev('type')}"
               th:text="#{${'seedstarter.type.' + type}}">Wood</label>
      </li>
```

### Dropdowns

Put `th:field` on the `<select>` only. Each `<option>` needs a `th:value`, which is how Thymeleaf finds the selected one. `th:each` can sit on the `<option>` itself, because [it runs first](../../reference/attribute-precedence/).

```html title="src/main/resources/templates/seedstarters/form.html"
            <select th:field="*{rows[__${rowStat.index}__].variety}">
              <option th:each="variety : ${allVarieties}"
                      th:value="${variety}"
                      th:text="${variety}">Thymus vulgaris</option>
            </select>
```

## Dynamic rows

A property that holds a list can bind to any number of rows. Buttons named `addRow` and `removeRow` post the form to mapped methods that change the list and show the form again:

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @PostMapping(params = "addRow")
    public String addRow(SeedStarter seedStarter, BindingResult bindingResult) {
        seedStarter.getRows().add(new Row());
        return "seedstarters/form";
    }

    @PostMapping(params = "removeRow")
    public String removeRow(SeedStarter seedStarter, BindingResult bindingResult,
                            @RequestParam int removeRow) {
        seedStarter.getRows().remove(removeRow);
        return "seedstarters/form";
    }
```

```html title="src/main/resources/templates/seedstarters/form.html"
        <tr th:each="row, rowStat : *{rows}">
          <td>
            <select th:field="*{rows[__${rowStat.index}__].variety}">
              <option th:each="variety : ${allVarieties}"
                      th:value="${variety}"
                      th:text="${variety}">Thymus vulgaris</option>
            </select>
          </td>
          <td>
            <input type="number" th:field="*{rows[__${rowStat.index}__].seedsPerCell}">
          </td>
          <td>
            <button type="submit" name="removeRow" th:value="${rowStat.index}">Remove row</button>
          </td>
        </tr>
```

The `__${rowStat.index}__` part is a preprocessing expression, which Thymeleaf evaluates before the rest. It's needed because Spring EL doesn't evaluate variables inside index brackets, so `*{rows[rowStat.index].variety}` wouldn't work. The output has real indexes:

```html
<select id="rows0.variety" name="rows[0].variety">
```

## Integration with `RequestDataValueProcessor`

Spring's `RequestDataValueProcessor` intercepts link URLs, form URLs and field values before they're written, and can add hidden fields. Spring Security's CSRF support is built on it, so you rarely need your own. If you do, declare a bean named `requestDataValueProcessor`:

```java
@Bean
public RequestDataValueProcessor requestDataValueProcessor() {
    return new MyRequestDataValueProcessor();
}
```

Thymeleaf calls it as follows:

- `th:href` and `th:src` call `processUrl(...)`.
- `th:action` calls `processAction(...)`. On a `<form>`, it also calls `getExtraHiddenFields(...)`, and adds the fields at the start of the form.
- `th:value` calls `processFormFieldValue(...)`, unless the tag has a `th:field`.
- `th:field` calls `processFormFieldValue(...)`, for the value or, on a `<textarea>`, the tag body.

## Common mistakes

- **403 on submit:** the form has `action` instead of `th:action`, so it has no CSRF token.
- **405 on submit with `th:method`:** `spring.mvc.hiddenmethod.filter.enabled` isn't set.
- **Neither BindingResult nor plain target object:** the object named in `th:object` isn't in the model. Add it when you show the form, and also on any path that shows the form again.
- **BindingResult ignored:** the `BindingResult` parameter has to come directly after the object it belongs to.
- **Lost lists on a failed submit:** values such as `allTypes` have to be in the model on every render. An `@ModelAttribute` method in the controller does that.

## Related pages

- [Validation and errors](../validation-and-errors/)
- [Conversion and formatting](../conversion-and-formatting/)
- [Spring Security](../spring-security/)

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Creating a Form](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#creating-a-form), [Integration with RequestDataValueProcessor](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#integration-with-requestdatavalueprocessor).*

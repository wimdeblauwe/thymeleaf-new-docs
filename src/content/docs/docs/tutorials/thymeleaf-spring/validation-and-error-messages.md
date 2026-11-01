---
title: "Validation and Error Messages"
description: "Most of our forms will need to show validation messages in order to inform the user of the errors he/she has made."
sidebar:
  order: 8
---

Most of our forms will need to show validation messages in order to inform the
user of the errors he/she has made.

Thymeleaf offers some tools for this: a couple of functions in the `#fields`
object, the `th:errors` and the `th:errorclass` attributes.

## Field errors

Let's see how we could set a specific CSS class to a field if it has an error:

```html
<input type="text" th:field="*{datePlanted}" 
                   th:class="${#fields.hasErrors('datePlanted')}? fieldError" />
```

As you can see, the `#fields.hasErrors(...)` function receives the field
expression as a parameter (`datePlanted`), and returns a boolean telling whether any validation
errors exist for that field.

We could also obtain all the errors for that field and iterate them:

```html
<ul>
  <li th:each="err : ${#fields.errors('datePlanted')}" th:text="${err}" />
</ul>
```

Instead of iterating, we could have also used `th:errors`, a specialized attribute which builds a list with all the errors for the specified selector, separated by `<br />`:

```html
<input type="text" th:field="*{datePlanted}" />
<p th:if="${#fields.hasErrors('datePlanted')}" th:errors="*{datePlanted}">Incorrect date</p>
```

### Simplifying error-based CSS styling: `th:errorclass`

The example we saw above, *setting a CSS class to a form input if that field has errors*, is so common that Thymeleaf offers a specific attribute for doing exactly that: `th:errorclass`.

Applied to a form field tag (input, select, textarea...), it will read the name of the field to be examined from any existing `name` or `th:field` attributes in the same tag, and then append the specified CSS class to the tag if such field has any associated errors:

```html
<input type="text" th:field="*{datePlanted}" class="small" th:errorclass="fieldError" />
```

If `datePlanted` has errors, this will render as:

```html
<input type="text" id="datePlanted" name="datePlanted" value="2013-01-01" class="small fieldError" />
```

## All errors

And what if we want to show all the errors in the form? We just need to query the `#fields.hasErrors(...)` and `#fields.errors(...)` methods with the `'*'` or `'all'` constants (which are equivalent):

```html
<ul th:if="${#fields.hasErrors('*')}">
  <li th:each="err : ${#fields.errors('*')}" th:text="${err}">Input is incorrect</li>
</ul>
```

As in the examples above, we could obtain all the errors and iterate them...

```html
<ul>
  <li th:each="err : ${#fields.errors('*')}" th:text="${err}" />
</ul>
```
...as well as build a `<br />`-separated list:

```html
<p th:if="${#fields.hasErrors('all')}" th:errors="*{all}">Incorrect date</p>
```

Finally note that `#fields.hasErrors('*')` is equivalent to `#fields.hasAnyErrors()` and `#fields.errors('*')` is equivalent to `#fields.allErrors()`. Use whichever syntax you prefer:

```html
<div th:if="${#fields.hasAnyErrors()}">
  <p th:each="err : ${#fields.allErrors()}" th:text="${err}">...</p>
</div>
```

Note that the `*{all}` selection expression (e.g. `th:errors="*{all}"`) can only
be used inside an element with a `th:object` attribute (or nested inside one,
such as a `<form>`), as selection expressions are always evaluated on the
object selected by the closest `th:object` in scope. See *7.4 Displaying
errors outside forms* below for how to display the same errors when there is
no `th:object` in scope.

## Global errors

There is a third type of error in a Spring form: *global* errors. These are errors that are not associated with any specific fields in the form, but still exist.

Thymeleaf offers the `global` constant for accessing these errors:

```html
<ul th:if="${#fields.hasErrors('global')}">
  <li th:each="err : ${#fields.errors('global')}" th:text="${err}">Input is incorrect</li>
</ul>
```

```html
<p th:if="${#fields.hasErrors('global')}" th:errors="*{global}">Incorrect date</p>
```

...as well as equivalent `#fields.hasGlobalErrors()` and `#fields.globalErrors()` convenience methods: 

```html
<div th:if="${#fields.hasGlobalErrors()}">
  <p th:each="err : ${#fields.globalErrors()}" th:text="${err}">...</p>
</div>
```

As with `*{all}`, the `*{global}` selection expression (e.g.
`th:errors="*{global}"`) requires a `th:object` in scope. See *7.4 Displaying
errors outside forms* below for the alternative syntax to use when there is no
`th:object` in scope.

## Displaying errors outside forms

Form validation errors can also be displayed outside forms by using variable (`${...}`) instead of selection (`*{...}`) expressions and prefixing the name of the form-backing bean: 

```html
<div th:errors="${myForm}">...</div>
<div th:errors="${myForm.date}">...</div>
<div th:errors="${myForm.*}">...</div>

<div th:if="${#fields.hasErrors('${myForm}')}">...</div>
<div th:if="${#fields.hasErrors('${myForm.date}')}">...</div>
<div th:if="${#fields.hasErrors('${myForm.*}')}">...</div>

<form th:object="${myForm}">
    ...
</form>
```

## Rich error objects

Thymeleaf offers the possibility to obtain form error information in the form of beans (instead of mere *strings*), with the `fieldName` (String), `message` (String) and `global` (boolean) attributes.

These errors can be obtained by means of the `#fields.detailedErrors()` utility method:

```html
<ul>
    <li th:each="e : ${#fields.detailedErrors()}" th:class="${e.global}? globalerr : fielderr">
        <span th:text="${e.global}? '*' : ${e.fieldName}">The field name</span> |
        <span th:text="${e.message}">The error message</span>
    </li>
</ul>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#validation-and-error-messages) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

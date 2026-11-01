---
title: "Forms"
description: "Command object is the name Spring MVC gives to form-backing beans, this is, to objects that model a form's fields and provide getter and setter methods that will be used by the framework for…"
sidebar:
  order: 4
---

## Handling the command object

_Command object_ is the name Spring MVC gives to form-backing beans, this is, to
objects that model a form's fields and provide getter and setter methods that
will be used by the framework for establishing and obtaining the values input by
the user at the browser side.

Thymeleaf requires you to specify the command object by using a `th:object`
attribute in your `<form>` tag:

```html
<form action="#" th:action="@{/seedstartermng}" th:object="${seedStarter}" method="post">
    ...
</form>
```

This is consistent with other uses of `th:object,` but in fact this
specific scenario adds some limitations in order to correctly integrate with
Spring MVC's infrastructure:

 * Values for `th:object` attributes in form tags must be variable expressions (`${...}`)
   specifying only the name of a model attribute, without property navigation.
   This means that an expression like `${seedStarter}` is valid, but `${seedStarter.data}`
   would not be.
 * Once inside the `<form>` tag, no other `th:object` attribute can be specified.
   This is consistent with the fact that HTML forms cannot be nested.
 * The name used in `th:object` (`seedStarter` in the example above) must match
   the name of the corresponding model attribute on the Spring MVC side. Unless
   a different name is set explicitly (e.g. via `@ModelAttribute("someName")` on
   the controller method parameter, or `Model#addAttribute("someName", ...)`),
   Spring will use the uncapitalized simple name of the command object's class
   as the model attribute name, so a `SeedStarter` object will by default be
   exposed to the view as `seedStarter`.

## Inputs

Let's see now how to add an input to our form:

```html
<input type="text" th:field="*{datePlanted}" />
```

As you can see, we are introducing a new attribute here: `th:field.` This is a
very important feature for Spring MVC integration because it does all the heavy
work of binding your input with a property in the form-backing bean. You can see
it as an equivalent of the path attribute in a `<form:input>` tag from Spring
MVC's JSP tag library.

The `th:field` attribute behaves differently depending on whether it is attached
to an `<input>`, `<select>` or `<textarea>` tag (and also depending on the
specific type of `<input>` tag). In this case (`input[type=text]`), the above
line of code is similar to:

```html
<input type="text" id="datePlanted" name="datePlanted" th:value="*{datePlanted}" />
```

...but in fact it is a little bit more than that, because `th:field` will also apply the registered Spring Conversion Service, including the `DateFormatter` we saw before (even if the field expression is not double-bracketed). Thanks to this, the date will be shown correctly formatted.

Note that, as with `th:value`, the value rendered by `th:field` is always
HTML-escaped. Unlike Spring MVC's JSP tag library, which lets you disable this
via the `htmlEscape` attribute (or a global `defaultHtmlEscape` setting),
Thymeleaf provides no equivalent way to turn off escaping for `th:field`.

Values for `th:field` attributes must be selection expressions (`*{...}`), which
makes sense given the fact that they will be evaluated on the form-backing bean
and not on the context variables (or model attributes in Spring MVC jargon).

Contrary to the ones in `th:object`, these expressions can include property
navigation (in fact any expression allowed for the path attribute of a `<form:input>`
JSP tag will be allowed here).

Note that `th:field` also understands the new types of `<input>` element
introduced by HTML5 like `<input type="datetime" ... />`, `<input type="color" ... />`,
etc., effectively adding complete HTML5 support to Spring MVC.

## Checkbox fields

`th:field` also allows us to define checkbox inputs. Let's see an example from
our HTML page:

```html
<div>
  <label th:for="${#ids.next('covered')}" th:text="#{seedstarter.covered}">Covered</label>
  <input type="checkbox" th:field="*{covered}" />
</div>
```

Note there's some fine stuff here besides the checkbox itself, like an
externalized label and also the use of the `#ids.next('covered')` function for
obtaining the value that will be applied to the id attribute of the checkbox
input.

Why do we need this dynamic generation of an id attribute for this field?
Because checkboxes are potentially multi-valued, and thus their id values will
always be suffixed a sequence number (by internally using the `#ids.seq(...)`
function) in order to ensure that each of the checkbox inputs for the same
property has a different id value.

We can see this more easily if we look at such a multi-valued checkbox field:

```html
<ul>
  <li th:each="feat : ${allFeatures}">
    <input type="checkbox" th:field="*{features}" th:value="${feat}" />
    <label th:for="${#ids.prev('features')}" 
           th:text="#{${'seedstarter.feature.' + feat}}">Heating</label>
  </li>
</ul>
```

Note that we've added a `th:value` attribute this time, because the features
field is not a boolean like covered was, but instead is an array of values.

Let's see the HTML output generated by this code:

```html
<ul>
  <li>
    <input id="features1" name="features" type="checkbox" value="SEEDSTARTER_SPECIFIC_SUBSTRATE" />
    <input name="_features" type="hidden" value="on" />
    <label for="features1">Seed starter-specific substrate</label>
  </li>
  <li>
    <input id="features2" name="features" type="checkbox" value="FERTILIZER" />
    <input name="_features" type="hidden" value="on" />
    <label for="features2">Fertilizer used</label>
  </li>
  <li>
    <input id="features3" name="features" type="checkbox" value="PH_CORRECTOR" />
    <input name="_features" type="hidden" value="on" />
    <label for="features3">PH Corrector used</label>
  </li>
</ul>
```

We can see here how a sequence suffix is added to each input's id attribute, and
how the `#ids.prev(...)` function allows us to retrieve the last sequence value
generated for a specific input id.

> Don't worry about those hidden inputs with `name="_features"`: they are
> automatically added in order to avoid problems with browsers not sending
> unchecked checkbox values to the server upon form submission.

Also note that if our features property contained some selected values in our
form-backing bean, `th:field` would have taken care of that and would have added
a `checked="checked"` attribute to the corresponding input tags.

## Radio Button fields

Radio button fields are specified in a similar way to non-boolean (multi-valued)
checkboxes ---except that they are not multivalued, of course:

```html
<ul>
  <li th:each="ty : ${allTypes}">
    <input type="radio" th:field="*{type}" th:value="${ty}" />
    <label th:for="${#ids.prev('type')}" th:text="#{${'seedstarter.type.' + ty}}">Wireframe</label>
  </li>
</ul>
```

## Dropdown/List selectors

Select fields have two parts: the `<select>` tag and its nested `<option>` tags.
When creating this kind of field, only the `<select>` tag has to include a `th:field`
attribute, but the `th:value` attributes in the nested `<option>` tags will be
very important because they will provide the means of knowing which is the
currently selected option (in a similar way to non-boolean checkboxes and radio
buttons).

Let's re-build the type field as a dropdown select:

```html
<select th:field="*{type}">
  <option th:each="type : ${allTypes}" 
          th:value="${type}" 
          th:text="#{${'seedstarter.type.' + type}}">Wireframe</option>
</select>
```

At this point, understanding this piece of code is quite easy. Just notice how
attribute precedence allows us to set the `th:each` attribute in the `<option>`
tag itself.

## Dynamic fields

Thanks to the advanced form-field binding capabilities in Spring MVC, we can use
complex Spring EL expressions to bind dynamic form fields to our form-backing
bean. This will allow us to create new Row objects in our `SeedStarter` bean,
and to add those rows' fields to our form at user request. 

In order to do this, we will need a couple of new mapped methods in our
controller, which will add or remove a row from our `SeedStarter` depending on
the existence of specific request parameters:

```java
@RequestMapping(value="/seedstartermng", params={"addRow"})
public String addRow(final SeedStarter seedStarter, final BindingResult bindingResult) {
    seedStarter.getRows().add(new Row());
    return "seedstartermng";
}

@RequestMapping(value="/seedstartermng", params={"removeRow"})
public String removeRow(
        final SeedStarter seedStarter, final BindingResult bindingResult, 
        final HttpServletRequest req) {
    final Integer rowId = Integer.valueOf(req.getParameter("removeRow"));
    seedStarter.getRows().remove(rowId.intValue());
    return "seedstartermng";
}
```

And now we can add a dynamic table to our form:

```html
<table>
  <thead>
    <tr>
      <th th:text="#{seedstarter.rows.head.rownum}">Row</th>
      <th th:text="#{seedstarter.rows.head.variety}">Variety</th>
      <th th:text="#{seedstarter.rows.head.seedsPerCell}">Seeds per cell</th>
      <th>
        <button type="submit" name="addRow" th:text="#{seedstarter.row.add}">Add row</button>
      </th>
    </tr>
  </thead>
  <tbody>
    <tr th:each="row,rowStat : *{rows}">
      <td th:text="${rowStat.count}">1</td>
      <td>
        <select th:field="*{rows[__${rowStat.index}__].variety}">
          <option th:each="var : ${allVarieties}" 
                  th:value="${var.id}" 
                  th:text="${var.name}">Thymus Thymi</option>
        </select>
      </td>
      <td>
        <input type="text" th:field="*{rows[__${rowStat.index}__].seedsPerCell}" />
      </td>
      <td>
        <button type="submit" name="removeRow" 
                th:value="${rowStat.index}" th:text="#{seedstarter.row.remove}">Remove row</button>
      </td>
    </tr>
  </tbody>
</table>
```

Quite a lot of things to see here, but nothing we shouldn't understand by now...
except for one `strange` thing:

```html
<select th:field="*{rows[__${rowStat.index}__].variety}">

    ...

</select>
```

If you recall from the _"Using Thymeleaf"_ tutorial, that `__${...}__` syntax is
a preprocessing expression, which is an inner expression that is evaluated
before actually evaluating the whole expression. But why that way of specifying
the row index? Wouldn't it be enough with:

```html
<select th:field="*{rows[rowStat.index].variety}">

    ...

</select>
```

...well, actually, no. The problem is that Spring EL does not evaluate variables
inside array index brackets, so when executing the above expression we would
obtain an error telling us that `rows[rowStat.index]` (instead of `rows[0]`,
`rows[1]`, etc) is not a valid position in the rows collection. That's why
preprocessing is needed here.

Let's have a look at a fragment of the resulting HTML after pressing _"Add Row"_
a couple of times:

```html
<tbody>
  <tr>
    <td>1</td>
    <td>
      <select id="rows0.variety" name="rows[0].variety">
        <option selected="selected" value="1">Thymus vulgaris</option>
        <option value="2">Thymus x citriodorus</option>
        <option value="3">Thymus herba-barona</option>
        <option value="4">Thymus pseudolaginosus</option>
        <option value="5">Thymus serpyllum</option>
      </select>
    </td>
    <td>
      <input id="rows0.seedsPerCell" name="rows[0].seedsPerCell" type="text" value="" />
    </td>
    <td>
      <button name="removeRow" type="submit" value="0">Remove row</button>
    </td>
  </tr>
  <tr>
    <td>2</td>
    <td>
      <select id="rows1.variety" name="rows[1].variety">
        <option selected="selected" value="1">Thymus vulgaris</option>
        <option value="2">Thymus x citriodorus</option>
        <option value="3">Thymus herba-barona</option>
        <option value="4">Thymus pseudolaginosus</option>
        <option value="5">Thymus serpyllum</option>
      </select>
    </td>
    <td>
      <input id="rows1.seedsPerCell" name="rows[1].seedsPerCell" type="text" value="" />
    </td>
    <td>
      <button name="removeRow" type="submit" value="1">Remove row</button>
    </td>
  </tr>
</tbody>
```

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

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Creating a Form](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#creating-a-form), [Integration with RequestDataValueProcessor](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#integration-with-requestdatavalueprocessor).*

---
title: "Listing Seed Starter Data"
description: "The first thing that our /WEB-INF/templates/seedstartermng.html page will show is a listing with the seed starters currently stored."
sidebar:
  order: 6
---

The first thing that our `/WEB-INF/templates/seedstartermng.html` page will show
is a listing with the seed starters currently stored. For this we will need some
externalized messages and also some expression evaluation on model attributes.
Like this:

```html
<div class="seedstarterlist" th:unless="${#lists.isEmpty(allSeedStarters)}">
    
  <h2 th:text="#{title.list}">List of Seed Starters</h2>
  
  <table>
    <thead>
      <tr>
        <th th:text="#{seedstarter.datePlanted}">Date Planted</th>
        <th th:text="#{seedstarter.covered}">Covered</th>
        <th th:text="#{seedstarter.type}">Type</th>
        <th th:text="#{seedstarter.features}">Features</th>
        <th th:text="#{seedstarter.rows}">Rows</th>
      </tr>
    </thead>
    <tbody>
      <tr th:each="sb : ${allSeedStarters}">
        <td th:text="${{sb.datePlanted}}">13/01/2011</td>
        <td th:text="#{|bool.${sb.covered}|}">yes</td>
        <td th:text="#{|seedstarter.type.${sb.type}|}">Wireframe</td>
        <td th:text="${#strings.arrayJoin(
                           #messages.arrayMsg(
                               #strings.arrayPrepend(sb.features,'seedstarter.feature.')),
                           ', ')}">Electric Heating, Turf</td>
        <td>
          <table>
            <tbody>
              <tr th:each="row,rowStat : ${sb.rows}">
                <td th:text="${rowStat.count}">1</td>
                <td th:text="${row.variety.name}">Thymus Thymi</td>
                <td th:text="${row.seedsPerCell}">12</td>
              </tr>
            </tbody>
          </table>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

Lots to see here. Let's have a look at each fragment separately.

First of all, this section will only be shown if there are any seed starters. We
achieve that with a th:unless attribute and the `#lists.isEmpty(...)` function.

```html
<div class="seedstarterlist" th:unless="${#lists.isEmpty(allSeedStarters)}">
```

Note that all utility objects like `#lists` are available in Spring EL
expressions just as they were in OGNL expressions in the Standard Dialect.

The next thing to see is a lot of internationalized (externalized) texts, like:

```html
<h2 th:text="#{title.list}">List of Seed Starters</h2>

<table>
  <thead>
    <tr>
      <th th:text="#{seedstarter.datePlanted}">Date Planted</th>
      <th th:text="#{seedstarter.covered}">Covered</th>
      <th th:text="#{seedstarter.type}">Type</th>
      <th th:text="#{seedstarter.features}">Features</th>
      <th th:text="#{seedstarter.rows}">Rows</th>
      ...
```

This being a Spring MVC application, we already defined a `MessageSource` bean
in our Spring configuration (`MessageSource` objects are the standard way of
managing externalized texts in Spring MVC):

```java
@Bean
public ResourceBundleMessageSource messageSource() {
    ResourceBundleMessageSource messageSource = new ResourceBundleMessageSource();
    messageSource.setBasename("Messages");
    return messageSource;
}
```

...and that `basename` property indicates that we will have files like `Messages_es.properties`
or `Messages_en.properties` in our classpath. Let's have a look at the Spanish
version:

```properties
title.list=Lista de semilleros

date.format=dd/MM/yyyy
bool.true=sí
bool.false=no

seedstarter.datePlanted=Fecha de plantación
seedstarter.covered=Cubierto
seedstarter.type=Tipo
seedstarter.features=Características
seedstarter.rows=Filas

seedstarter.type.WOOD=Madera
seedstarter.type.PLASTIC=Plástico

seedstarter.feature.SEEDSTARTER_SPECIFIC_SUBSTRATE=Sustrato específico para semilleros
seedstarter.feature.FERTILIZER=Fertilizante
seedstarter.feature.PH_CORRECTOR=Corrector de PH
```

In the first column of the table listing we will show the date when the seed
starter was prepared. But **we will show it formatted** in the way we defined 
in our `DateFormatter`. In order to do that we will use the double-brace 
syntax (`${{...}}`), which will automatically apply the Spring Conversion Service,
including the `DateFormatter` we registered at configuration.

```html
<td th:text="${{sb.datePlanted}}">13/01/2011</td>
```

Next is showing whether the seed starter container is covered or not, by
transforming the value of the boolean covered bean property into an
internationalized _"yes"_ or _"no"_ with a literal substitution expression:

```html
<td th:text="#{|bool.${sb.covered}|}">yes</td>
```

Now we have to show the type of seed starter container. Type is a java enum with
two values (`WOOD` and `PLASTIC`), and that's why we defined two properties in
our `Messages` file called `seedstarter.type.WOOD` and `seedstarter.type.PLASTIC`.

But in order to obtain the internationalized names of the types, we will need to
add the `seedstarter.type.` prefix to the enum value by means of an expression,
which result we will then use as the message key:

```html
<td th:text="#{|seedstarter.type.${sb.type}|}">Wireframe</td>
```

The most difficult part of this listing is the _features_ column. In it we want
to display all the features of our container ---that come in the form of an array
of `Feature` enums---, separated by commas. Like _"Electric Heating, Turf"_.

Note that this is particularly difficult because these enum values also need to
be externalized, as we did with Types. The flow is then:

1. Prepend the corresponding prefix to all the elements of the `features` array.
2. Obtain the externalized messages corresponding to all the keys from step 1.
3. Join all the messages obtained in step 2, using a comma as a delimiter.

For achieving this, we create the following code:

```html
<td th:text="${#strings.arrayJoin(
                   #messages.arrayMsg(
                       #strings.arrayPrepend(sb.features,'seedstarter.feature.')),
                   ', ')}">Electric Heating, Turf</td>
```

The last column of our listing will be quite simple, in fact. Even if it has a
nested table for showing the contents of each row in the container:

```html
<td>
  <table>
    <tbody>
      <tr th:each="row,rowStat : ${sb.rows}">
        <td th:text="${rowStat.count}">1</td>
        <td th:text="${row.variety.name}">Thymus Thymi</td>
        <td th:text="${row.seedsPerCell}">12</td>
      </tr>
    </tbody>
  </table>
</td>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#listing-seed-starter-data) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

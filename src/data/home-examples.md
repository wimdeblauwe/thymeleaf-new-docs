The home page shows these blocks. DocsExamplesTest runs them like the examples in the docs.

```html title="Template"
<table>
  <tr>
    <th>Product</th>
    <th>Price</th>
  </tr>
  <tr th:each="product : ${products}">
    <td th:text="${product.name}">Oranges</td>
    <td th:text="${product.price}">0.99</td>
  </tr>
</table>
```

```html title="Output"
<table>
  <tr>
    <th>Product</th>
    <th>Price</th>
  </tr>
  <tr>
    <td>Fresh sweet basil</td>
    <td>4.99</td>
  </tr>
  <tr>
    <td>Italian tomato</td>
    <td>1.25</td>
  </tr>
</table>
```

```html title="src/main/resources/templates/seedstarters/list.html"
  <input type="search" name="search" aria-label="Search seed starters"
         th:value="${search}"
         th:hx-get="@{/seedstarters}"
         hx-trigger="input changed delay:300ms, search"
         hx-target="#seedstarter-rows"
         hx-swap="outerHTML"
         hx-push-url="true">
```

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
            return "seedstarters/list :: rows";
```

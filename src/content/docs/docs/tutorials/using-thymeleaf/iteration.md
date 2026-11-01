---
title: "Iteration"
description: "So far we have created a home page, a user profile page and also a page for letting users subscribe to our newsletter... but what about our products?"
sidebar:
  order: 6
---

So far we have created a home page, a user profile page and also a page for
letting users subscribe to our newsletter... but what about our products?  For
that, we will need a way to iterate over items in a collection to build out our
product page.

## Iteration basics

To display products in our `/WEB-INF/templates/product/list.html` page we will
use a table. Each of our products will be displayed in a row (a `<tr>` element),
and so for our template we will need to create a _template row_ -- one
that will exemplify how we want each product to be displayed -- and then instruct
Thymeleaf to repeat it, once for each product.

The Standard Dialect offers us an attribute for exactly that: `th:each`.

### Using th:each

For our product list page, we will need a controller method that retrieves the
list of products from the service layer and adds it to the template context:

```java
public void process(
        final IWebExchange webExchange, 
        final ITemplateEngine templateEngine, 
        final Writer writer)
        throws Exception {
    
    final ProductService productService = new ProductService();
    final List<Product> allProducts = productService.findAll();
    
    final WebContext ctx = new WebContext(webExchange, webExchange.getLocale());
    ctx.setVariable("prods", allProducts);
    
    templateEngine.process("product/list", ctx, writer);
    
}
```

And then we will use `th:each` in our template to iterate over the list of
products:

```html
<!DOCTYPE html>

<html xmlns:th="http://www.thymeleaf.org">

  <head>
    <title>Good Thymes Virtual Grocery</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" type="text/css" media="all" 
          href="../../../css/gtvg.css" th:href="@{/css/gtvg.css}" />
  </head>

  <body>

    <h1>Product list</h1>
  
    <table>
      <tr>
        <th>NAME</th>
        <th>PRICE</th>
        <th>IN STOCK</th>
      </tr>
      <tr th:each="prod : ${prods}">
        <td th:text="${prod.name}">Onions</td>
        <td th:text="${prod.price}">2.41</td>
        <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
      </tr>
    </table>
  
    <p>
      <a href="../home.html" th:href="@{/}">Return to home</a>
    </p>

  </body>

</html>
```

That `prod : ${prods}` attribute value you see above means "for each element in
the result of evaluating `${prods}`, repeat this fragment of template, using the
current element in a variable called prod". Let's give a name each of the things
we see:

 * We will call `${prods}` the _iterated expression_ or _iterated variable_.
 * We will call `prod` the _iteration variable_ or simply _iter variable_.

Note that the `prod` iter variable is scoped to the `<tr>` element, which means
it is available to inner tags like `<td>`.

### Iterable values

The `java.util.List` class isn't the only value that can be used for iteration in
Thymeleaf. There is a quite complete set of objects that are considered _iterable_
by a `th:each` attribute:

 * Any object implementing `java.util.Iterable`
 * Any object implementing `java.util.Enumeration`.
 * Any object implementing `java.util.Iterator`, whose values will be used as
   they are returned by the iterator, without the need to cache all values in memory.
 * Any object implementing `java.util.Map`. When iterating maps, iter variables
   will be of class `java.util.Map.Entry`.
 * Any object implementing `java.util.stream.Stream`.
 * Any array.
 * Any other object will be treated as if it were a single-valued list
   containing the object itself.

## Keeping iteration status

When using `th:each`, Thymeleaf offers a mechanism useful for keeping track of
the status of your iteration: the _status variable_.

Status variables are defined within a `th:each` attribute and contain the
following data:

 * The current _iteration index_, starting with 0. This is the `index` property.
 * The current _iteration index_, starting with 1. This is the `count` property.
 * The total amount of elements in the iterated variable. This is the `size`
   property.
 * The _iter variable_ for each iteration. This is the `current` property.
 * Whether the current iteration is even or odd. These are the `even/odd` boolean
   properties.
 * Whether the current iteration is the first one. This is the `first` boolean
   property.
 * Whether the current iteration is the last one. This is the `last` boolean
   property.

Let's see how we could use it with the previous example:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
  </tr>
  <tr th:each="prod,iterStat : ${prods}" th:class="${iterStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
  </tr>
</table>
```

The status variable (`iterStat` in this example) is defined in the `th:each`
attribute by writing its name after the iter variable itself, separated by a
comma. Just like the iter variable, the status variable is also scoped to the
fragment of code defined by the tag holding the `th:each` attribute.

Let's have a look at the result of processing our template:

```html
<!DOCTYPE html>

<html>

  <head>
    <title>Good Thymes Virtual Grocery</title>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type"/>
    <link rel="stylesheet" type="text/css" media="all" href="/gtvg/css/gtvg.css" />
  </head>

  <body>

    <h1>Product list</h1>
  
    <table>
      <tr>
        <th>NAME</th>
        <th>PRICE</th>
        <th>IN STOCK</th>
      </tr>
      <tr class="odd">
        <td>Fresh Sweet Basil</td>
        <td>4.99</td>
        <td>yes</td>
      </tr>
      <tr>
        <td>Italian Tomato</td>
        <td>1.25</td>
        <td>no</td>
      </tr>
      <tr class="odd">
        <td>Yellow Bell Pepper</td>
        <td>2.50</td>
        <td>yes</td>
      </tr>
      <tr>
        <td>Old Cheddar</td>
        <td>18.75</td>
        <td>yes</td>
      </tr>
    </table>
  
    <p>
      <a href="/gtvg/" shape="rect">Return to home</a>
    </p>

  </body>
  
</html>
```

Note that our iteration status variable has worked perfectly, establishing the
`odd` CSS class only to odd rows.

If you don't explicitly set a status variable, Thymeleaf will always create one
for you by suffixing `Stat` to the name of the iteration variable:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
  </tr>
</table>
```

## Optimizing through lazy retrieval of data

Sometimes we might want to optimize the retrieval of collections of data (e.g.
from a database) so that these collections are only retrieved if they are really
going to be used. 

> Actually, this is something that can be applied to *any* piece of data, but given the size
> that in-memory collections might have, retrieving collections that are meant to be iterated
> is the most common case for this scenario.

In order to support this, Thymeleaf offers a mechanism to *lazily load context
variables*. Context variables that implement the `ILazyContextVariable`
interface -- most probably by extending its `LazyContextVariable` default
implementation -- will be resolved in the moment of being executed. For example:

```java
context.setVariable(
     "users",
     new LazyContextVariable<List<User>>() {
         @Override
         protected List<User> loadValue() {
             return databaseRepository.findAllUsers();
         }
     });
```

This variable can be used without knowledge of its *laziness*, in code such as:

```html
<ul>
  <li th:each="u : ${users}" th:text="${u.name}">user name</li>
</ul>
```

But at the same time, will never be initialized (its `loadValue()` method will
never be called) if `condition` evaluates to `false` in code such as:

```html
<ul th:if="${condition}">
  <li th:each="u : ${users}" th:text="${u.name}">user name</li>
</ul>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#iteration) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

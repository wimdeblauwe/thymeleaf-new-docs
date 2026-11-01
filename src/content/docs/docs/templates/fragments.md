---
title: "Fragments"
description: "In our templates, we will often want to include parts from other templates, parts like footers, headers, menus..."
sidebar:
  order: 8
---

## Defining and referencing fragments

In our templates, we will often want to include parts from other templates,
parts like footers, headers, menus...

In order to do this, Thymeleaf needs us to define these parts, "fragments", for
inclusion, which can be done using the `th:fragment` attribute. 

Say we want to add a standard copyright footer to all our grocery pages, so we
create a `/WEB-INF/templates/footer.html` file containing this code:

```html
<!DOCTYPE html>

<html xmlns:th="http://www.thymeleaf.org">

  <body>
  
    <div th:fragment="copy">
      &copy; 2011 The Good Thymes Virtual Grocery
    </div>
  
  </body>
  
</html>
```

The code above defines a fragment called `copy` that we can easily include in
our home page using one of the `th:insert` or `th:replace` attributes:

```html
<body>

  ...

  <div th:insert="~{footer :: copy}"></div>
  
</body>
```

Note that `th:insert` expects a *fragment expression* (`~{...}`), which is *an
expression that results in a fragment*.

## Fragment specification syntax

The syntax of *fragment expressions* is quite straightforward. There are three
different formats:

 * `"~{templatename::selector}"` Includes the fragment resulting from applying
   the specified Markup Selector on the template named `templatename`.  Note
   that `selector` can be a mere fragment name, so you could specify something
   as simple as `~{templatename::fragmentname}` like in the `~{footer :: copy}`
   above.

   > Markup Selector syntax is defined by the underlying AttoParser parsing
   > library, and is similar to XPath expressions or CSS selectors. See
   > [Markup selectors](../../reference/markup-selectors/) for more info.

 * `"~{templatename}"` Includes the complete template named `templatename`.

   > Note that the template name you use in `th:insert`/`th:replace` tags
   > will have to be resolvable by the Template Resolver currently being used by
   > the Template Engine.

 * `~{::selector}"` or `"~{this::selector}"` Inserts a fragment from the same
   template, matching `selector`. If not found on the template where the expression
   appears, the stack of template calls (insertions) is traversed towards the
   originally processed template (the *root*), until `selector` matches at 
   some level.

Both `templatename` and `selector` in the above examples can be fully-featured
expressions (even conditionals!) like:

```html
<div th:insert="~{ footer :: (${user.isAdmin}? #{footer.admin} : #{footer.normaluser}) }"></div>
```

Fragments can include any `th:*` attributes. These attributes will be evaluated
once the fragment is included into the target template (the one with the `th:insert`/`th:replace`
attribute), and they will be able to reference any context variables defined in
this target template.

> A big advantage of this approach to fragments is that you can write your
> fragments in pages that are perfectly displayable by a browser, with a
> complete and even *valid* markup structure, while still retaining the ability
> to make Thymeleaf include them into other templates.

> Note that fragment expressions are subject to stricter expression evaluation restrictions
> for security reasons. See [Expression restrictions](../../security/expression-restrictions/).

## Referencing fragments without `th:fragment`

Thanks to the power of Markup Selectors, we can include fragments that do not use any 
`th:fragment` attributes. It can even be markup code coming from a different application 
with no knowledge of Thymeleaf at all:

```html
...
<div id="copy-section">
  &copy; 2011 The Good Thymes Virtual Grocery
</div>
...
```

We can use the fragment above simply referencing it by its `id` attribute, in a similar way to a CSS selector:

```html
<body>

  ...

  <div th:insert="~{footer :: #copy-section}"></div>
  
</body>
```

## Difference between `th:insert` and `th:replace`

And what is the difference between `th:insert` and `th:replace`?

 * `th:insert` will simply insert the specified fragment as the body
   of its host tag.

 * `th:replace` actually *replaces* its host tag with the specified fragment.

So an HTML fragment like this:

```html
<footer th:fragment="copy">
  &copy; 2011 The Good Thymes Virtual Grocery
</footer>
```

...included twice in host `<div>` tags, like this:

```html
<body>

  ...

  <div th:insert="~{footer :: copy}"></div>

  <div th:replace="~{footer :: copy}"></div>
  
</body>
```

...will result in:

```html
<body>

  ...

  <div>
    <footer>
      &copy; 2011 The Good Thymes Virtual Grocery
    </footer>
  </div>

  <footer>
    &copy; 2011 The Good Thymes Virtual Grocery
  </footer>
  
</body>
```

## Removing template fragments

Back to the example application, let's revisit the last version of our product list template:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
</table>
```

This code is just fine as a template, but as a static page (when directly open
by a browser without Thymeleaf processing it) it would not make a nice prototype. 

Why? Because, although perfectly displayable by browsers, that table only has a
row, and this row has mock data. As a prototype, it simply wouldn't look
realistic enough... we should have more than one product, _we need more rows_.

So let's add some:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
  <tr class="odd">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr>
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

Ok, now we have three, definitely better for a prototype. But... what will
happen when we process it with Thymeleaf?:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr>
    <td>Fresh Sweet Basil</td>
    <td>4.99</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Italian Tomato</td>
    <td>1.25</td>
    <td>no</td>
    <td>
      <span>2</span> comment/s
      <a href="/gtvg/product/comments?prodId=2">view</a>
    </td>
  </tr>
  <tr>
    <td>Yellow Bell Pepper</td>
    <td>2.50</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Old Cheddar</td>
    <td>18.75</td>
    <td>yes</td>
    <td>
      <span>1</span> comment/s
      <a href="/gtvg/product/comments?prodId=4">view</a>
    </td>
  </tr>
  <tr class="odd">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr>
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

The last two rows are mock rows! Well, of course they are: iteration was only
applied to the first row, so there is no reason why Thymeleaf should have
removed the other two.

We need a way to remove those two rows during template processing. Let's use the
`th:remove` attribute on the second and third `<tr>` tags:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
    <td th:text="${prod.name}">Onions</td>
    <td th:text="${prod.price}">2.41</td>
    <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
    <td>
      <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
      <a href="comments.html" 
         th:href="@{/product/comments(prodId=${prod.id})}" 
         th:unless="${#lists.isEmpty(prod.comments)}">view</a>
    </td>
  </tr>
  <tr class="odd" th:remove="all">
    <td>Blue Lettuce</td>
    <td>9.55</td>
    <td>no</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr th:remove="all">
    <td>Mild Cinnamon</td>
    <td>1.99</td>
    <td>yes</td>
    <td>
      <span>3</span> comment/s
      <a href="comments.html">view</a>
    </td>
  </tr>
</table>
```

Once processed, everything will look again as it should:

```html
<table>
  <tr>
    <th>NAME</th>
    <th>PRICE</th>
    <th>IN STOCK</th>
    <th>COMMENTS</th>
  </tr>
  <tr>
    <td>Fresh Sweet Basil</td>
    <td>4.99</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Italian Tomato</td>
    <td>1.25</td>
    <td>no</td>
    <td>
      <span>2</span> comment/s
      <a href="/gtvg/product/comments?prodId=2">view</a>
    </td>
  </tr>
  <tr>
    <td>Yellow Bell Pepper</td>
    <td>2.50</td>
    <td>yes</td>
    <td>
      <span>0</span> comment/s
    </td>
  </tr>
  <tr class="odd">
    <td>Old Cheddar</td>
    <td>18.75</td>
    <td>yes</td>
    <td>
      <span>1</span> comment/s
      <a href="/gtvg/product/comments?prodId=4">view</a>
    </td>
  </tr>
</table>
```

And what does that `all` value in the attribute, mean? `th:remove` can behave in
five different ways, depending on its value:

 * `all`: Remove both the containing tag and all its children.
 * `body`: Do not remove the containing tag, but remove all its children.
 * `tag`: Remove the containing tag, but do not remove its children. (`tags`, plural, is also allowed as an alias for this value.)
 * `all-but-first`: Remove all children of the containing tag except the first one.
 * `none` : Do nothing. This value is useful for dynamic evaluation.

What can that `all-but-first` value be useful for? It will let us save some `th:remove="all"`
when prototyping:

```html
<table>
  <thead>
    <tr>
      <th>NAME</th>
      <th>PRICE</th>
      <th>IN STOCK</th>
      <th>COMMENTS</th>
    </tr>
  </thead>
  <tbody th:remove="all-but-first">
    <tr th:each="prod : ${prods}" th:class="${prodStat.odd}? 'odd'">
      <td th:text="${prod.name}">Onions</td>
      <td th:text="${prod.price}">2.41</td>
      <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
      <td>
        <span th:text="${#lists.size(prod.comments)}">2</span> comment/s
        <a href="comments.html" 
           th:href="@{/product/comments(prodId=${prod.id})}" 
           th:unless="${#lists.isEmpty(prod.comments)}">view</a>
      </td>
    </tr>
    <tr class="odd">
      <td>Blue Lettuce</td>
      <td>9.55</td>
      <td>no</td>
      <td>
        <span>0</span> comment/s
      </td>
    </tr>
    <tr>
      <td>Mild Cinnamon</td>
      <td>1.99</td>
      <td>yes</td>
      <td>
        <span>3</span> comment/s
        <a href="comments.html">view</a>
      </td>
    </tr>
  </tbody>
</table>
```

The `th:remove` attribute can take any _Thymeleaf Standard Expression_, as long
as it returns one of the allowed String values (`all`, `tag`, `body`, `all-but-first`
or `none`).

This means removals could be conditional, like:

```html
<a href="/something" th:remove="${condition}? tag : none">Link text not to be removed</a>
```

Also note that `th:remove` considers `null` a synonym to `none`, so the
following works the same as the example above:

```html
<a href="/something" th:remove="${condition}? tag">Link text not to be removed</a>
```

In this case, if `${condition}` is false, `null` will be returned, and thus no
removal will be performed. 

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [Including template fragments](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#including-template-fragments), [Removing template fragments](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#removing-template-fragments).*

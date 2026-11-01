---
title: "Attribute Precedence"
description: "What happens when you write more than one th: attribute in the same tag?"
sidebar:
  order: 10
---

What happens when you write more than one `th:*` attribute in the same tag? For
example:

```html
<ul>
  <li th:each="item : ${items}" th:text="${item.description}">Item description here...</li>
</ul>
```

We would expect that `th:each` attribute to execute before the `th:text` so that
we get the results we want, but given the fact that the HTML/XML standards do
not give any kind of meaning to the order in which the attributes in a tag are 
written, a _precedence_ mechanism had to be established in the attributes
themselves in order to be sure that this will work as expected.

So, all Thymeleaf attributes define a numeric precedence, which establishes the
order in which they are executed in the tag. This order is:

| Order | Feature | Attributes |
| --- | --- | --- |
| 1 | Fragment inclusion | `th:insert`<br>`th:replace` |
| 2 | Fragment iteration | `th:each` |
| 3 | Conditional evaluation | `th:if`<br>`th:unless`<br>`th:switch`<br>`th:case` |
| 4 | Local variable definition | `th:object`<br>`th:with` |
| 5 | General attribute modification | `th:attr`<br>`th:attrprepend`<br>`th:attrappend` |
| 6 | Specific attribute modification | `th:value`<br>`th:href`<br>`th:src`<br>`...` |
| 7 | Text (tag body modification) | `th:text`<br>`th:utext` |
| 8 | Fragment specification | `th:fragment` |
| 9 | Fragment removal | `th:remove` |

This precedence mechanism means that the above iteration fragment will give
exactly the same results if the attribute position is inverted (although it
would be slightly less readable):

```html
<ul>
  <li th:text="${item.description}" th:each="item : ${items}">Item description here...</li>
</ul>
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#attribute-precedence) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

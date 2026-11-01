---
title: "Comments and Blocks"
description: "Standard HTML/XML comments <!-- ... --> can be used anywhere in Thymeleaf templates."
sidebar:
  order: 11
---

## Standard HTML/XML comments

Standard HTML/XML comments `<!-- ... -->` can be used anywhere in Thymeleaf
templates. Anything inside these comments will be processed by Thymeleaf as
any other block of text in the template:

```html
<!-- User info follows -->
<div th:text="${...}">
  ...
</div>
```

## Thymeleaf parser-level comment blocks

Parser-level comment blocks are code that will be simply removed from the
template when Thymeleaf parses it. They look like this:

```html
<!--/* This code will be removed at Thymeleaf parsing time! */-->
``` 

Thymeleaf will remove everything between `<!--/*` and `*/-->`, so these comment
blocks can also be used for displaying code when a template is statically open,
knowing that it will be removed when Thymeleaf processes it:

```html
<!--/*--> 
  <div>
     you can see me only before Thymeleaf processes me!
  </div>
<!--*/-->
```

This might come very handy for prototyping tables with a lot of `<tr>`'s, for
example:

```html
<table>
   <tr th:each="x : ${xs}">
     ...
   </tr>
   <!--/*-->
   <tr>
     ...
   </tr>
   <tr>
     ...
   </tr>
   <!--*/-->
</table>
```

## Thymeleaf prototype-only comment blocks

Thymeleaf allows the definition of special comment blocks marked to be comments
when the template is open statically (i.e. as a prototype), but considered
normal markup by Thymeleaf when executing the template.

```html
<span>hello!</span>
<!--/*/
  <div th:text="${...}">
    ...
  </div>
/*/-->
<span>goodbye!</span>
```

Thymeleaf's parsing system will simply remove the `<!--/*/` and `/*/-->` markers,
but not its contents, which will be left therefore uncommented. So when
executing the template, Thymeleaf will actually see this:

```html
<span>hello!</span>
 
  <div th:text="${...}">
    ...
  </div>
 
<span>goodbye!</span>
```

As with parser-level comment blocks, this feature is dialect-independent.

## Synthetic `th:block` tag

Thymeleaf's only element processor (not an attribute) included in the Standard
Dialects is `th:block`.

`th:block` is a mere attribute container that allows template developers to
specify whichever attributes they want. Thymeleaf will execute these attributes
and then simply make the block, but not its contents, disappear.

So it could be useful, for example, when creating iterated tables that require
more than one `<tr>` for each element:

```html
<table>
  <th:block th:each="user : ${users}">
    <tr>
        <td th:text="${user.login}">...</td>
        <td th:text="${user.name}">...</td>
    </tr>
    <tr>
        <td colspan="2" th:text="${user.address}">...</td>
    </tr>
  </th:block>
</table>
```

And especially useful when used in combination with prototype-only comment blocks:

```html
<table>
    <!--/*/ <th:block th:each="user : ${users}"> /*/-->
    <tr>
        <td th:text="${user.login}">...</td>
        <td th:text="${user.name}">...</td>
    </tr>
    <tr>
        <td colspan="2" th:text="${user.address}">...</td>
    </tr>
    <!--/*/ </th:block> /*/-->
</table>
```

Note how this solution allows templates to be valid HTML (no need to add
forbidden `<div>` blocks inside `<table>`), and still works OK when open
statically in browsers as prototypes! 

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#comments-and-blocks) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

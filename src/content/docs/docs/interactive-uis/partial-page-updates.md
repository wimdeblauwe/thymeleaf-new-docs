---
title: "Partial page updates with htmx"
description: "Update part of a page by rendering one Thymeleaf fragment from a Spring controller and swapping it in with htmx."
sidebar:
  order: 2
---

With htmx, an element can send a request and swap the HTML response into the page. Thymeleaf suits this well, because a controller can render one fragment of a template. The same file then serves both the full page and every partial update, so there's no separate markup to keep in sync.

In this guide you add live search and delete without a reload to a seed starter list.

Tested with htmx 2.0.11, Spring Boot 4.1.2, Spring Security and Thymeleaf 3.1.5, in Chrome. The code is in [`samples/showcase`](https://github.com/wimdeblauwe/thymeleaf-new-docs/tree/main/samples/showcase).

## Prerequisites

- A Spring Boot application with Thymeleaf. See [Quickstart: Spring Boot](../../start/quickstart-spring-boot/).
- Basic knowledge of [fragments](../../templates/fragments/).

## Add htmx

Add the script to the page. It's the only setup that htmx needs:

```html title="src/main/resources/templates/seedstarters/list.html"
  <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"></script>
```

## Mark the part that changes

Name the part of the page that updates with `th:fragment`. It stays in place, so the full page still renders it as normal:

```html title="src/main/resources/templates/seedstarters/list.html"
    <tbody id="seedstarter-rows" th:fragment="rows">
      <tr th:each="seedStarter : ${seedStarters}">
        <td th:text="${seedStarter.name}">Greenhouse tray</td>
        <td th:text="${seedStarter.datePlanted}">2026-03-14</td>
        <td>
          <button th:hx-delete="@{/seedstarters/{id}(id=${seedStarter.id})}"
                  hx-target="closest tr"
                  hx-swap="delete">Delete</button>
        </td>
      </tr>
      <tr th:if="${seedStarters.isEmpty()}">
        <td colspan="3">No seed starters found.</td>
      </tr>
    </tbody>
```

## Trigger the request

The search field sends a `GET` as you type. `th:hx-get` builds the URL, so it includes the context path. `hx-target` and `hx-swap` replace the whole `<tbody>`, because the response is the whole `<tbody>`. `hx-push-url` keeps the address bar in step:

```html title="src/main/resources/templates/seedstarters/list.html"
  <input type="search" name="search" aria-label="Search seed starters"
         th:value="${search}"
         th:hx-get="@{/seedstarters}"
         hx-trigger="input changed delay:300ms, search"
         hx-target="#seedstarter-rows"
         hx-swap="outerHTML"
         hx-push-url="true">
```

## Return the fragment from the controller

htmx sends an `HX-Request` header. The controller uses it to choose a view, and a view name with `::` renders only that fragment:

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @GetMapping
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestHeader(name = "HX-Request", required = false) String htmxRequest,
                       @RequestHeader(name = "HX-History-Restore-Request", required = false) String historyRestore,
                       HttpServletResponse response,
                       Model model) {
        model.addAttribute("search", search);
        model.addAttribute("seedStarters", seedStarters.search(search));
        model.addAttribute("total", seedStarters.count());
        response.addHeader("Vary", "HX-Request");
        if (htmxRequest != null && historyRestore == null) {
            return "seedstarters/list :: rows";
        }
        return "seedstarters/list";
    }
```

Three details make this robust:

- **The URL works without htmx.** Open `/seedstarters?search=kit` directly and you get the full page, filtered.
- **`Vary: HX-Request`** stops a browser or proxy cache from serving the fragment in place of the page.
- **`HX-History-Restore-Request`** is set when htmx reloads a page for the back button after its history cache misses. That request needs the full page, even though it also has `HX-Request`.

A search now responds with just this:

```html
<tbody id="seedstarter-rows">
  <tr>
    <td>Kitchen window</td>
    <td>2026-03-14</td>
    <td>
      <button hx-delete="/seedstarters/2"
              hx-target="closest tr"
              hx-swap="delete">Delete</button>
    </td>
  </tr>
</tbody>
```

## Send the CSRF token

Spring Security rejects a `DELETE` without a CSRF token with `403 Forbidden`, and `th:action` can't help here because there's no form. Set a header for all htmx requests on the page instead. `hx-headers` is inherited, so it can go on `<body>`:

```html title="src/main/resources/templates/seedstarters/list.html"
<body th:hx-headers="|{&quot;${_csrf.headerName}&quot;: &quot;${_csrf.token}&quot;}|">
```

```html
<body hx-headers="{&quot;X-CSRF-TOKEN&quot;: &quot;...&quot;}">
```

Fragment responses don't need to repeat it. The attribute stays on the page, and every swapped-in button inherits it.

This is safe in `hx-headers` because the header name and token come from Spring Security and contain no user input. `hx-headers` is parsed as JSON. Don't place user input in it.

## Update several parts at once

Deleting a row removes it from the table, but the total above the table changes too. htmx can update elements outside the target if the response includes them with `hx-swap-oob`:

```html title="src/main/resources/templates/seedstarters/list.html"
  <p><span id="seedstarter-count" th:fragment="count" hx-swap-oob="true" th:text="${total}">3</span> in total</p>
```

The attribute has no effect during a normal page load. On the delete request, return that fragment. Spring's `FragmentsRendering` can return one fragment or several, and it works with Thymeleaf view names:

```java title="src/main/java/org/thymeleaf/samples/showcase/seedstarter/SeedStarterController.java"
    @DeleteMapping(path = "/{id}", headers = "HX-Request")
    public FragmentsRendering deleteWithHtmx(@PathVariable long id, Model model) {
        seedStarters.deleteById(id);
        model.addAttribute("total", seedStarters.count());
        return FragmentsRendering.fragment("seedstarters/list :: count").build();
    }
```

The button's `hx-swap="delete"` removes the row, and the response body updates the count:

```html
<span id="seedstarter-count" hx-swap-oob="true">2</span>
```

The `headers = "HX-Request"` condition keeps the normal `@DeleteMapping` for the form-based delete in [Forms](../../spring/forms/#http-methods-other-than-post).

## Common mistakes

- **The table loses its rows or gains a nested `<tbody>`:** the response holds the `<tbody>` but the swap is the default `innerHTML`. Use `hx-swap="outerHTML"`.
- **403 on `hx-post` or `hx-delete`:** the CSRF header is missing.
- **The fragment is shown as a whole page after pressing back:** the controller ignores `HX-History-Restore-Request`, or the response has no `Vary` header.
- **`th:hx-get` with `${param.x}` fails:** the default attribute processor runs in [restricted mode](../../security/expression-restrictions/), which forbids request parameters. Pass the value through the model.

## Related pages

- [Rendering fragments](../../spring/rendering-fragments/)
- [Components](../../templates/components/)
- [Escaping and XSS](../../security/escaping-and-xss/)
- [htmx documentation](https://htmx.org/docs/)

## Going further

[htmx-spring-boot](https://github.com/wimdeblauwe/htmx-spring-boot) is a community project that adds typed access to the htmx headers, and `hx:*` attributes for Thymeleaf. The code on this page doesn't depend on it.

---
title: "Expression restrictions"
description: "For security reasons, Thymeleaf applies restrictions on the use of certain Thymeleaf Standard Expressions depending on the context in which those expressions are evaluated."
sidebar:
  order: 2
---

For security reasons, Thymeleaf applies restrictions on the use of certain
Thymeleaf Standard Expressions depending on the context in which those
expressions are evaluated. There are two types of restrictions:

 * General restrictions, applied to every expression: static use (instantiation,
   calling static methods…) of most classes from Thymeleaf's, Spring's and
   Java/Jakarta's base infrastructure is forbidden, as well as a number of
   well-known third-party framework packages.
   **This is not meant to be an exhaustive filter** but a mere helper that
   bans a set of the most obvious common classes that could be potentially misused.
 * Stricter restrictions applied in specific contexts on the use of some
   kinds of expression syntax and available objects. These restrictions are
   collectively referred to as the **restricted expression evaluation mode**.

It must be stressed, however, that **these restrictions are not a substitute
for proper input validation**. It is always the responsibility of the
application to validate and sanitise all data coming from users or external
sources before it is used in any way, including before being added to the
template context. Thymeleaf is only a template engine, and these expression
restrictions are meant to be an additional defence-in-depth mechanism, 
not a first line of defence.

## Restricted mode: Contexts in which it applies

The restricted expression evaluation mode is applied when expressions are
evaluated in the following contexts:

 * **Preprocessing expressions**: `__...__`
 * **Unescaped text output**: `th:utext` and unescaped inlined expressions.
 * **JavaScript event handler attributes**: all `th:on*` attribute processors
   whose value is a Thymeleaf Standard Expression.
 * **The `th:attr` attribute processor** when used for creating attributes with
   arbitrary names.
 * **The default attribute processor**, which allows the rendering of any
   attribute with an arbitrary name.
 * **Template and fragment names, and fragment parameters** in Fragment
   Expressions (`~{...}`) and in `th:insert`, `th:replace`, `th:include`, and
   `th:substituteby` attributes.
 * **The base (non-parameter) part of URL expressions**: `@{...}` URL bases,
   `th:href`, and `th:src` (URL parameters within Link Expressions are not
   restricted).
 * **All output expressions in `TEXT` template mode**, whether escaped or not,
   due to the lack of knowledge about the specific context in which they will
   be used.

It is important to remember that **Thymeleaf will not apply these checks in 
any other scenarios other than the ones listed above**, so expressions should
be assumed to execute without restrictions elsewhere.

## Restricted mode: Restrictions applied

When expressions are evaluated in restricted mode, the following are forbidden:

 * Access to request parameters via `${param.*}`.
 * Instantiation of new objects (e.g. `new com.example.SomeClass()`).
 * Access to static classes and their members (OGNL's `@identifier@` syntax,
   or Spring EL's `T(identifier)` syntax).
 * Access to some of Thymeleaf's context-level expression utility objects like
   `#execInfo`.
 * In `th:on*` event handler attributes specifically: variable expressions
   that result in values of a type other than a numeric or boolean type are
   also forbidden.
 * In Spring Applictions: access to beans from the application context via the
   `@beanName` syntax.

Attempts to evaluate a restricted expression in one of the above scenarios
will result in a template processing exception being raised at runtime.

It is important to note that **any checks not explicitly listed above will
not be performed**, and that these checks can never be considered a replacement
for data and user input validation at the application's code.

## Important note for application developers

These restrictions are a security feature, not a configuration option. They
are designed to prevent certain classes of injection vulnerabilities that could
otherwise arise from the use of user-controlled input in sensitive expression
positions. They are applied automatically by the template engine and cannot be
disabled on a per-expression or per-template basis.

That said, no template engine security mechanism can replace careful,
thorough input validation at the application level. All data originating from
users or any other external source —request parameters, headers, cookies,
database contents, third-party service responses, and so on— must be
validated and, where appropriate, sanitised by the application before being
used, regardless of where or how it will eventually appear in a template.
Trusting external data without validation and relying solely on Thymeleaf's
expression restrictions for protection is not an acceptable security posture.

What is more: Thymeleaf, being a template engine and not a full application
framework, does not have the technical capability to check whether the values
that an application puts into the context for template processing
did originate as direct user input in the current or previous requests or
user interactions, and therefore under no circumstances it should be
assumed that it would able to verify such origin. Whatever the origin of
the expressions being executed, **they will be executed** if they do not
match any of the filters listed above, in the specific contexts listed above.

Lastly, if an expression that previously worked causes a restriction error after a
Thymeleaf upgrade, this most likely means it was being used in a way that
poses a potential security risk. The recommended approach is to refactor the
template logic so that the affected data is introduced into the template
context by the application code, rather than being computed directly inside
the template expression in a restricted context. And, of course, ensuring
that such data has been properly validated before it reaches the template
context at all.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#appendix-d-expression-restrictions) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

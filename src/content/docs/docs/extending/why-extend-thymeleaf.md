---
title: "Why extend Thymeleaf"
description: "Thymeleaf is an extremely extensible library."
sidebar:
  order: 1
---

Thymeleaf is an extremely extensible library. The key to it is that most of its
user-oriented features are not directly built into its core, but rather just
packaged and componentized into feature sets called _dialects_.

The library offers you two dialects out-of-the-box: the _Standard_ and the _SpringStandard_
dialects, but you can easily create your own. Let's explore some of the reasons
for doing this:

**Scenario 1: adding features to the Standard dialects**

Say your application uses the _SpringStandard_ dialect and that it needs to show
an alert text box in blue or red background depending on the user's role (admin
or non-admin) from Monday to Saturday, but always in green on Sundays. You can
compute this with conditional expressions on your template, but too many
conditions could render your code a little bit hard to read...

Solution: create a new attribute called `alertclass` and an attribute processor
for it (Java code that will compute the right CSS class), and package it into
your own `MyOwnDialect` dialect. Add this dialect to your template engine with
the `th` prefix (same as the _SpringStandard_ one) and you'll now be able to use
`th:alertclass="${user.role}"`!

**Scenario 2: view-layer components**

Let's say your company uses Thymeleaf extensively, and you want to create a
repository of common functionalities (tags and/or attributes) that you can use
in several applications without having to copy-paste them from one application
to the next. This is, you want to create view-layer components in a similar way
to JSPs _taglibs_.

Solution: create a Thymeleaf dialect for each set of related functionalities,
and add these dialects to your applications as needed. Note that if the tags or
attributes in these dialects make use of externalized (internationalized)
messages, you will be able to package these messages along with your dialects
(in the shape of _processor messages_) instead of requiring that all of your
applications include them in their messages `.properties` files as you would
with JSP.

**Scenario 3: creating your own template system**

Now imagine you are creating a public website that allows users to create their
own design templates for showing their content. Of course, you don't want your
users to be able to do absolutely everything in their templates, not even all that
the Standard Dialect allows (for example, execute OGNL expressions). So you need
to offer your users the ability to add to their templates only a very specific
set of features that are under your control (like showing a profile photo, a
blog entry text, etc).

Solution: create a Thymeleaf dialect with the tags or attributes you want your
users to be able to use, like `<mysite:profilePhoto />` or `<mysite:blogentries fromDate="23/4/2011" />`.
Then allow your users to create their own templates using these features and
just let Thymeleaf execute them, being sure nobody will be doing what they're
not allowed to.

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/extendingthymeleaf.html#some-reasons-to-extend-thymeleaf) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

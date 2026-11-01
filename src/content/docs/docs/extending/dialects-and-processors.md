---
title: "Dialects and processors"
description: "If you've read the Using Thymeleaf tutorial before getting here ---which you should have done--- you should know that what you've been learning all this time was not exactly Thymeleaf, but rather its…"
sidebar:
  order: 2
---

## Dialects

If you've read the _Using Thymeleaf_ tutorial before getting here ---which you
should have done--- you should know that what you've been learning all this time
was not exactly _Thymeleaf_, but rather its _Standard Dialect_ (or the _SpringStandard Dialect_,
if you've also read the _Thymeleaf + Spring_ tutorial).

What does that mean? It means that all those `th:x` attributes you learned to
use are only a standard, out-of-the-box set of features, but you can define your
own set of attributes (or tags) with the names you wish and use them in
Thymeleaf to process your templates. *You can define your own dialects.*

Dialects are objects implementing the `org.thymeleaf.dialect.IDialect` interface,
which cannot be any simpler:

```java
public interface IDialect {

    public String getName();

}
```

The only core requirement of a dialect is to have a name that can be used for its
identification. But this alone is of little use, so dialects will normally implement
one or several subinterfaces of `IDialect`, depending
on what they provide to the Thymeleaf engine:

  * `IProcessorDialect` for dialects that provide *processors*.
  * `IPreProcessorDialect` for dialects that provide *pre-processors*.
  * `IPostProcessorDialect` for dialects that provide *post-processors*.
  * `IExpressionObjectDialect` for dialects that provide *expression objects*.
  * `IExecutionAttributeDialect` for dialects that provide *execution attributes*.

### Processor dialects: `IProcessorDialect`

The `IProcessorDialect` interface looks like this:

```java
public interface IProcessorDialect extends IDialect {

    public String getPrefix();
    public int getDialectProcessorPrecedence();
    public Set<IProcessor> getProcessors(final String dialectPrefix);

}
```

**Processors** are the objects in charge of executing most of the logic
in Thymeleaf templates, and possibly the most important Thymeleaf extension
artifact. We will cover processors in more detail in next sections.

This dialect only defines three items:

  * The *prefix*, which is the prefix or namespace that should be applied
    *by default* to the elements and attributes matched by the dialect's
    processors. So a dialect with prefix `th` like e.g. the *Standard
    Dialect* will be able to define processors matching attributes like
    `th:text`, `th:if` or `th:whatever` (or `data-th-text`, `data-th-if`
    and `data-th-whatever` if we prefer *pure HTML5* syntax). Note however
    that the prefix returned here by a dialect is **only the default one**
    to be used for that dialect, but such prefix can be changed during
    template engine configuration. Also note that prefix can be `null` if
    we want our processors to execute on unprefixed tags/attributes.

  * The *dialect precedence* allows the sorting of processors across 
    dialects. Processors define their own *precedence* value, but these
    processor precedences are considered *relative to 
    dialect precedence*, so every processor in a specific dialect can be 
    configured to be executed before all processors
    from a different dialect just by setting the correct values for this
    *dialect precedence*.

  * The *processors* are, as its name implies, the set of *processors* provided
    by the dialect. Note the `getProcessors(...)` method is passed the
    `dialectPrefix` as an argument in case the dialect has been configured
    at the Template Engine with a prefix different to the default one. Most probably
    the `IProcessor` instances will need this information during their
    initialization.

### Pre-processor dialects: `IPreProcessorDialect`

**Pre-processors** and **post-processors** are different to *processors* in 
that instead of executing on a single event or on an event model (a fragment of
a template), they apply to the entire template execution process as an additional step in
the engine's processing chain. Therefore they follow an API completely
different to that of processors, much more event-oriented, defined by the 
lower-level `ITemplateHandler` interface.

In the specific case of the pre-processors, they apply **before** the Thymeleaf engine
starts executing processors for a specific template.

The `IPreProcessorDialect` interface looks like:

```java
public interface IPreProcessorDialect extends IDialect {

    public int getDialectPreProcessorPrecedence();
    public Set<IPreProcessor> getPreProcessors();

}
```

Which is very similar to the `IProcessorDialect` above –including its own 
dialect-level precedence for pre-processors– but lacks a *prefix*, as 
pre-processors don't need it at all (they don't *match* on specific 
events – instead they handle all of them).

### Post-processor dialects: `IPostProcessorDialect`

As stated above, **post-processors** are an additional step in the template execution
chain, but this time they execute **after** the Thymeleaf engine has applied
all the needed processors. This means post-processors apply just before
template output happens (and can therefore modify what is being output).

The `IPostProcessorDialect` interface looks like:

```java
public interface IPostProcessorDialect extends IDialect {

    public int getDialectPostProcessorPrecedence();
    public Set<IPostProcessor> getPostProcessors();

}
```

...which is completely analogous to the `IPreProcessorDialect` interface, but of 
course for post-processors in this case.

### Expression Object dialects: `IExpressionObjectDialect`

Dialects implementing this interface provide new *expression objects* or *expression 
utility objects* that can be used in expressions anywhere in templates, such as 
the `#strings`, `#numbers`, `#dates`, etc. provided by the Standard Dialect.

The `IExpressionObjectDialect` interface looks like this:

```java
public interface IExpressionObjectDialect extends IDialect {

    public IExpressionObjectFactory getExpressionObjectFactory();

}
```

Which, as we can see, does not return the expression objects themselves, 
but only a *factory*. The reason for this is some *expression objects* might 
require data from the processing context in order to be built, so it won't 
be possible to build them until we really are processing the template... and 
besides, most expressions don't need *expression objects* at all, so it's 
just better to build them *on demand*, only when they are really needed 
for specific expressions (and build only those that are needed).

This is the `IExpressionObjectFactory` interface:

```java
public interface IExpressionObjectFactory {

    public Map<String,ExpressionObjectDefinition> getObjectDefinitions();

    public Object buildObject(final IExpressionContext context, final String expressionObjectName);

}
```

### Execution Attribute dialects: `IExecutionAttributeDialect`

Dialects implementing this interface are allowed to provide *execution attributes*, 
i.e. objects that are available to every processor being executed during template 
processing.

For example, the Standard Dialect implements this interface in order to provide to 
every processor:

   * The *Thymeleaf Standard Expression parser* so that Standard Expressions in 
     any attribute can be parsed and executed.
   * The *Variable Expression Evaluator* so that `${...}` expressions are executed 
     either in OGNL or SpringEL (depending on whether we are using the Spring 
     integration module or not).
   * The *Conversion Service* that performs conversion operations in `${{...}}` expressions.

Note that these objects are not available at the context, so
they cannot be used from template expressions. Their availability is limited to
implementations of extension points such as processors, pre-processors, etc.

The `IExecutionAttributeDialect` interface is very simple:

```java
public interface IExecutionAttributeDialect extends IDialect {

    public Map<String,Object> getExecutionAttributes();

}
```

## Processors

Processors are objects implementing the `org.thymeleaf.processor.IProcessor`
interface, and they contain the real logic to be applied on the different parts
of a template (which we will represent as **events**, given Thymeleaf is an
event-based engine). This interface looks like this:

```java
public interface IProcessor {

    public TemplateMode getTemplateMode();
    public int getPrecedence();

}
```

As with dialects, this is a very simple interface that only specified the template
mode in which the processor can be applied and its precedence.

But there are several types of *processor*, one for each possible type of event:

  * Template start/end
  * Element Tags
  * Texts
  * Comments
  * CDATA Sections
  * DOCTYPE Clauses
  * XML Declarations
  * Processing Instructions

And also for **models**: sequences of events representing an *entire element*, i.e. 
an element with its entire body, including any nested elements or any other 
kind of artifacts that might appear inside. If the modelled element is a 
*standalone element*, the model will only contain its corresponding event; 
but if the modelled element has a body, the model will contain every event 
from its *open tag* to its *close tag*, both included.

All these types of processors are created by implementing a specific interface, or 
by extending one of the available *abstract implementations*. All these artifacts 
conforming the Thymeleaf Processor API live at the `org.thymeleaf.processor` 
package.

### Element Processors

Element processors are those that are executed on the *open element* (`IOpenElementTag`) 
or *standalone element* (`IStandaloneElementTag`) events, normally by means of matching 
the name of the element (and/or one of its attributes) with a matching configuration 
specified by the processor. This is what the `IElementProcessor` interface looks like:

```java
public interface IElementProcessor extends IProcessor {

    public MatchingElementName getMatchingElementName();
    public MatchingAttributeName getMatchingAttributeName();

}
```

Note however that element processor implementations are not meant to directly implement 
this interface. Instead, element processors should fall into one of two categories:

  * **Element Tag Processors**, implementing the `IElementTagProcessor` interface. 
    These processors execute on *open/standalone tag events only* (no processors 
    can be applied to *close tags*), and have no direct access to the element body.
  * **Element Model Processors**, implementing the `IElementModelProcessor` interface. 
    These processors execute on *complete elements*, including their bodies, in the 
    form of `IModel` objects.

We should have a look at each of these interfaces separately:

### Element Tag Processors: `IElementTagProcessor`

Element Tag Processors, as explained, execute on the single *open element* or 
*standalone element* tag that matches its matching configuration (seen in 
`IElementProcessor`). The interface to be implemented is `IElementTagProcessor`, 
which looks like this:

```java
public interface IElementTagProcessor extends IElementProcessor {

    public void process(
            final ITemplateContext context, 
            final IProcessableElementTag tag,
            final IElementTagStructureHandler structureHandler);

}
```

As we can see, besides extending `IElementProcessor` it only specifies a 
`process(...)` method that will be executed when the *matching configuration* 
matches (and in the order established by its *precedence*, established at the 
`IProcessor` superinterface). The `process(...)` signature is quite compact, 
and follows a pattern found in every Thymeleaf processor interface:

   * The `process(...)` method returns `void`. Any actions will be performed 
     via the `structureHandler`.
   * The `context` argument contains the context with which the template is 
     being executed: variables, template data, etc.
   * The `tag` argument is the event on which the processor is being fired. 
     It contains both the name of the element and its attributes.
   * The `structureHandler` is a special object that allows the processor to 
     give instructions to the engine about actions that it should perform as 
     a consequence of the execution of the processor.

**Using the `structureHandler`**

The `tag` argument passed to `process(...)` is an **immutable** object. So there is 
no way to, for example, directly modify the attributes of a tag on the `tag` object 
itself. Instead, the `structureHandler` should be used.

For example, let's see how we would read the value of a specific `tag` attribute, 
unescape it and keep it in a variable, and then remove the attribute from the tag:

```java
// Obtain the attribute value
String attributeValue = tag.getAttributeValue(attributeName);

// Unescape the attribute value
attributeValue = 
    EscapedAttributeUtils.unescapeAttribute(context.getTemplateMode(), attributeValue);

// Instruct the structureHandler to remove the attribute from the tag
structureHandler.removeAttribute(attributeName);

... // do something with that attributeValue
```

*Note that the code above is only meant to showcase some attribute management 
concepts -- in most processors we won't need to do this "get value + unescape + remove" 
operation manually as it will all be handled by an extended superclass such as 
`AbstractAttributeTagProcessor`*.

Above we've seen only one of the *operations* offered by the `structureHandler`. There is 
a *structure handler* for each type of processor in Thymeleaf, and the one 
for *element tag* processors implements the `IElementTagStructureHandler` interface, which 
looks like this:

```java
public interface IElementTagStructureHandler {

    public void reset();

    public void setLocalVariable(final String name, final Object value);
    public void removeLocalVariable(final String name);

    public void setAttribute(final String attributeName, final String attributeValue);
    public void setAttribute(final String attributeName, final String attributeValue, 
                             final AttributeValueQuotes attributeValueQuotes);

    public void replaceAttribute(final AttributeName oldAttributeName, 
                                 final String attributeName, final String attributeValue);
    public void replaceAttribute(final AttributeName oldAttributeName, 
                                 final String attributeName, final String attributeValue, 
                                 final AttributeValueQuotes attributeValueQuotes);

    public void removeAttribute(final String attributeName);
    public void removeAttribute(final String prefix, final String name);
    public void removeAttribute(final AttributeName attributeName);

    public void setSelectionTarget(final Object selectionTarget);

    public void setInliner(final IInliner inliner);

    public void setTemplateData(final TemplateData templateData);

    public void setBody(final CharSequence text, final boolean processable);
    public void setBody(final IModel model, final boolean processable);

    public void insertBefore(final IModel model); // cannot be processable
    public void insertImmediatelyAfter(final IModel model, final boolean processable);

    public void replaceWith(final CharSequence text, final boolean processable);
    public void replaceWith(final IModel model, final boolean processable);


    public void removeElement();
    public void removeTags();
    public void removeBody();
    public void removeAllButFirstChild();

    public void iterateElement(final String iterVariableName, 
                               final String iterStatusVariableName, 
                               final Object iteratedObject);

}
```

There we can see all the actions that a processor can ask the template engine to do as 
a result of its execution. The method names are quite self-explanatory (and there is 
javadoc for them), but very briefly:

  * `setLocalVariable(...)`/`removeLocalVariable(...)` will add a local variable to the 
    template execution. This *local variable* will be accessible during the rest of the 
    execution of the current event, and also during all its *body* (i.e. until its 
    corresponding *close tag*)
  * `setAttribute(...)` adds a new attribute to the tag with a specified value (and 
    maybe also type of surrounding quotes). If the attribute already exists, its value 
    will be replaced.
  * `replaceAttribute(...)` replaces an existing attribute with a new one, taking its 
    place in the attribute (including its surrounding white space, for example).
  * `removeAttribute(...)` removes an attribute from the tag.
  * `setSelectionTarget(...)` modifies the object that is to be considered the 
    *selection target*, i.e. the object on which *selection expressions* (`*{...}`) will 
    be executed. In the Standard Dialect, this *selection target* is usually modified by 
    means of the `th:object` attribute, but custom processors can do it too. Note the 
    *selection target* has the same scope as a local variable, and will therefore be 
    accessible only inside the body of the element being processed.
  * `setInliner(...)` modifies the *inliner* to be used for processing all text nodes 
    (`IText` events) appearing in the body of the element being processed. This is the 
    mechanism used by the `th:inline` attribute to enable *inlining* in any of the 
    specified modes (`text`, `javascript`, etc).
  * `setTemplateData(...)` modifies the metadata about the template that is actually 
    being processed. When inserting fragments, this allows the engine to know data about 
    the specific fragment being processed, and also the complete stack of fragments being 
    nested.
  * `setBody(...)` replaces all the body of the element being processed with the passed 
    text or model (sequence of events = fragment of markup). This is the way e.g. that 
    `th:text`/`th:utext` work. Note that the specified replacement text or model can be 
    set as *processable* or not, depending on whether we want to execute any processors 
    that might be associated with them. In the case of `th:utext="${var}"`, for example, 
    the replacement is set as *non-processable* in order to avoid executing any markup 
    that might be returned by `${var}` as a part of the template.
  * `insertBefore(...)`/`insertImmediatelyAfter(...)` allow the specification of a model 
    (fragment of markup) that should appear before or *immediately* after the tag being 
    processed. Note that `insertImmediatelyAfter` means *after the tag being processed* 
    (and therefore as the first part of the element's body) and not *after the entire 
    element that opens here, and closes in a close tag somewhere*.
  * `replaceWith(...)` allows the current *element* (entire element) to be replaced with 
    the text or model specified as argument.
  * `removeElement()`/`removeTags()`/`removeBody()`/`removeAllButFirstChild()` allow the 
    processor to remove, respectively, the entire element including its body, only the 
    executed tags (open + close) but not the body, only the body but not the wrapping tags, 
    and lastly all the tag's children except the first child element. Note all these options 
    basically mirror the different values that can be used at the `th:remove` attribute.
  * `iterateElement(...)` allows the current element (body included) to be iterated as many 
    times as elements exist in the `iteratedObject` (which will usually be a `Collection`, 
    `Map`, `Iterator` or an array). The other two arguments will be used for specifying the 
    names of the variables used for the iterated elements and the status variable.

**Abstract implementations for `IElementTagProcessor`**

Thymeleaf offers two basic implementations of `IElementTagProcessor` that processors might 
implement for convenience:

  * `org.thymeleaf.processor.element.AbstractElementTagProcessor`, meant for processors that 
    match element events by their element name (i.e. without looking at attributes).
  * `org.thymeleaf.processor.element.AbstractAttributeTagProcessor`, meant for processors that 
    match element events by one of their attributes (and optionally also the element name).

### Element Model Processors: `IElementModelProcessor`

Element Model Processors execute on the entire elements they match –including their bodies–
in the form of an `IModel` object that contains the complete sequence of events that models 
such element and its contents. The `IElementModelProcessor` is very similar to the one seen 
above for *tag processors*:

```java
public interface IElementModelProcessor extends IElementProcessor {

    public void process(
            final ITemplateContext context, 
            final IModel model,
            final IElementModelStructureHandler structureHandler);

}
```

Note how this interface also extends `IElementProcessor`, and how the `process(...)` method 
it contains follows the same structure as the one in tag processors, replacing `tag` with 
`model` of course:

   * `process(...)` returns `void`. Actions will be performed on `model` or `structureHandler`, 
     not by returning anything.
   * `context` contains the execution context: variables, etc.
   * `model` is the sequence of events modelling the entire element on which the processor is 
     being executed. This model can be directly modified from the processor.
   * `structureHandler` allows instructing the engine to perform actions beyond model 
     modification (e.g. setting local variables).

**Reading and modifying the model**

The `IModel` object passed as a parameter to the `process()` method is a **mutable** model, so 
it allows any modifications to be done on it (*models* are mutable, *events* such as *tags* are 
immutable). For example, we might want to modify it so that we replace every text node from its 
body with a comment with the same contents:

```java
final IModelFactory modelFactory =  context.getModelFactory();

int n = model.size();
while (n-- != 0) {
    final ITemplateEvent event = model.get(n);
    if (event instanceof IText) {
        final IComment comment =
                modelFactory.createComment(((IText)event).getText());
        model.insert(n, comment);
        model.remove(n + 1);
    }
}
```

Note also that the `IModel` interface includes an `accept(IModelVisitor visitor)` method, useful 
for traversing an entire model looking for specific nodes or relevant data using the *Visitor*
pattern.

**Using the `structureHandler`**

Similarly to *tag processors*, model processors are passed a *structure handler* object that allows 
them to instruct the engine to take any actions that cannot be done by directly acting on the 
`IModel model` object itself. The interface these structure handlers implement, much smaller than 
the one for tag processors, is `IElementModelStructureHandler`:

```java
public interface IElementModelStructureHandler {

    public void reset();

    public void setLocalVariable(final String name, final Object value);
    public void removeLocalVariable(final String name);

    public void setSelectionTarget(final Object selectionTarget);

    public void setInliner(final IInliner inliner);

    public void setTemplateData(final TemplateData templateData);

}
```

It's easy to see this is a subset of the one for tag processors. The few methods there work the 
same way:

  * `setLocalVariable(...)`/`removeLocalVariable(...)` for adding/removing local variables that will 
    be available during the model's execution (after the current processor's execution).
  * `setSelectionTarget(...)` for modifying the *selection target* applied during the model's execution.
  * `setInliner(...)` for setting an inliner.
  * `setTemplateData(...)` for setting metadata about the template being processed.

**Abstract implementations for `IElementModelProcessor`**

Thymeleaf offers two basic implementations of `IElementModelProcessor` that processors might implement 
for convenience:

  * `org.thymeleaf.processor.element.AbstractElementModelProcessor`, meant for processors that match 
    element events by their element name (i.e. without looking at attributes).
  * `org.thymeleaf.processor.element.AbstractAttributeModelProcessor`, meant for processors that match 
    element events by one of their attributes (and optionally also the element name).

### Template start/end Processors: `ITemplateBoundariesProcessor`

Template Boundaries Processors are a kind of processor that executes on the *template start* and 
*template end* events fired during template processing. They allow to perform any kind of initialization 
or disposal of resources at beginning or end of the template processing operation. Note that these events 
are **only fired for the first-level template**, and not for each of the fragments that might be parsed 
and/or included into the template being processed.

The `ITemplateBoundariesProcessor` interface looks like this:

```java
public interface ITemplateBoundariesProcessor extends IProcessor {

    public void processTemplateStart(
            final ITemplateContext context,
            final ITemplateStart templateStart,
            final ITemplateBoundariesStructureHandler structureHandler);

    public void processTemplateEnd(
            final ITemplateContext context,
            final ITemplateEnd templateEnd,
            final ITemplateBoundariesStructureHandler structureHandler);

}
```

This time the interface offers two `process*(...)` methods, one for the
*template start* and another one for the *template end* events. Their signature
follows the same pattern as the other `process(...)` methods we saw before,
receiving the context, the event object, and the structure handler. Structure
handler that, in this case, implements a quite simple `ITemplateBoundariesStructureHandler`
interface:

```java
public interface ITemplateBoundariesStructureHandler {

    public void reset();

    public void setLocalVariable(final String name, final Object value);
    public void removeLocalVariable(final String name);

    public void setSelectionTarget(final Object selectionTarget);

    public void setInliner(final IInliner inliner);

    public void insert(final String text, final boolean processable);
    public void insert(final IModel model, final boolean processable);

}
```

We can see how, besides the usual methods for managing local variables, selection target and inliner, we can also 
use the structure handler for inserting text or a model, which in this case will appear at the very beginning or 
the very end of the result (depending on the event being processed).

### Other processors

There are other events for which Thymeleaf 3.0 allows processors to be declared, each of them implementing 
their corresponding interface:

   * **Text** events: interface `ITextProcessor`
   * **Comment** events: interface `ICommentProcessor`
   * **CDATA Section** events: interface `ICDATASectionProcessor`
   * **DOCTYPE Clause** events: interface `IDocTypeProcessor`
   * **XML Declaration** events: interface `IXMLDeclarationProcessor`
   * **Processing Instruction** events: interface `IProcessingInstructionProcessor`

All of them look pretty much like this (which is the one for text events):

```java
public interface ITextProcessor extends IProcessor {

    public void process(
            final ITemplateContext context, 
            final IText text,
            final ITextStructureHandler structureHandler);

}
```

Same pattern as all other `process(...)` methods: context, event, structure handler. And these structure 
handlers are very simple, just like this (again, the one for text events):

```java
public interface ITextStructureHandler {

    public void reset();

    public void setText(final CharSequence text);

    public void replaceWith(final IModel model, final boolean processable);

    public void removeText();

}
```

---

*Adapted from the [Thymeleaf documentation](https://www.thymeleaf.org/doc/tutorials/3.1/extendingthymeleaf.html#dialects-and-processors) at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).*

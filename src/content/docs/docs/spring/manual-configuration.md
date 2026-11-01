---
title: "Manual configuration without Boot"
description: "Note that most of the times you shouldn't be using the SpringStandard dialect directly in a normal TemplateEngine object as a part of its configuration."
sidebar:
  order: 10
---

Note that most of the times _you shouldn't be using the SpringStandard dialect directly in a normal 
`TemplateEngine` object_ as a part of its configuration. Unless you have very specific
Spring integration needs, you should instead be creating an instance of a new template
engine class that performs all the required configuration steps automatically: 
`org.thymeleaf.spring6.SpringTemplateEngine`.

An example bean configuration:

```java
@Bean
public SpringResourceTemplateResolver templateResolver(){
    // SpringResourceTemplateResolver automatically integrates with Spring's own
    // resource resolution infrastructure, which is highly recommended.
    SpringResourceTemplateResolver templateResolver = new SpringResourceTemplateResolver();
    templateResolver.setApplicationContext(this.applicationContext);
    templateResolver.setPrefix("/WEB-INF/templates/");
    templateResolver.setSuffix(".html");
    // HTML is the default value, added here for the sake of clarity.
    templateResolver.setTemplateMode(TemplateMode.HTML);
    // Template cache is true by default. Set to false if you want
    // templates to be automatically updated when modified.
    templateResolver.setCacheable(true);
    return templateResolver;
}

@Bean
public SpringTemplateEngine templateEngine(){
    // SpringTemplateEngine automatically applies SpringStandardDialect and
    // enables Spring's own MessageSource message resolution mechanisms.
    SpringTemplateEngine templateEngine = new SpringTemplateEngine();
    templateEngine.setTemplateResolver(templateResolver());
    // Enabling the SpringEL compiler can speed up execution in most
    // scenarios, but might be incompatible with specific cases when
    // expressions in one template are reused across different data
    // types, so this flag is "false" by default for safer backwards
    // compatibility.
    templateEngine.setEnableSpringELCompiler(true);
    return templateEngine;
}
```

Or, using Spring's XML-based configuration:

```xml
<!-- SpringResourceTemplateResolver automatically integrates with Spring's own -->
<!-- resource resolution infrastructure, which is highly recommended.          -->
<bean id="templateResolver"
       class="org.thymeleaf.spring6.templateresolver.SpringResourceTemplateResolver">
  <property name="prefix" value="/WEB-INF/templates/" />
  <property name="suffix" value=".html" />
  <!-- HTML is the default value, added here for the sake of clarity.          -->
  <property name="templateMode" value="HTML" />
  <!-- Template cache is true by default. Set to false if you want             -->
  <!-- templates to be automatically updated when modified.                    -->
  <property name="cacheable" value="true" />
</bean>
    
<!-- SpringTemplateEngine automatically applies SpringStandardDialect and      -->
<!-- enables Spring's own MessageSource message resolution mechanisms.         -->
<bean id="templateEngine"
      class="org.thymeleaf.spring6.SpringTemplateEngine">
  <property name="templateResolver" ref="templateResolver" />
  <!-- Enabling the SpringEL compiler can speed up execution in most           -->
  <!-- scenarios, but might be incompatible with specific cases when           -->
  <!-- expressions in one template are reused across different data types, so  -->
  <!-- this flag is "false" by default for safer backwards compatibility.      -->
  <property name="enableSpringELCompiler" value="true" />
</bean>
```

## Views and View Resolvers

### Views and View Resolvers in Spring MVC

There are two interfaces in Spring MVC that conform the core of its templating
system:

 * `org.springframework.web.servlet.View`
 * `org.springframework.web.servlet.ViewResolver`

Views model pages in our applications and allow us to modify and predefine their
behaviour by defining them as beans. Views are in charge of rendering the actual
HTML interface, usually by the execution of some template engine like Thymeleaf.

ViewResolvers are the objects in charge of obtaining View objects for a specific
operation and locale. Typically, controllers ask ViewResolvers to forward to a
view with a specific name (a String returned by the controller method), and then
all the view resolvers in the application execute in ordered chain until one of
them is able to resolve that view, in which case a View object is returned and
control is passed to it for the renderization of HTML.

> Note that not all pages in our applications have to be defined as Views, but
> only those which behaviour we wish to be non-standard or configured in a
> specific way (for example, by wiring some special beans to it). If a
> ViewResolver is asked a view that has no corresponding bean --which is the
> common case--, a new View object is created ad hoc and returned.

A typical configuration for a JSP+JSTL ViewResolver in a Spring MVC application
from the past looked like this:

```xml
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
  <property name="viewClass" value="org.springframework.web.servlet.view.JstlView" />
  <property name="prefix" value="/WEB-INF/jsps/" />
  <property name="suffix" value=".jsp" />
  <property name="order" value="2" />
  <property name="viewNames" value="*jsp" />
</bean>
```

A quick look at its properties is enough to know about how it was configured:

 * `viewClass` establishes the class of the View instances. This is needed for a
   JSP resolver, but it will not be needed at all when we're working with Thymeleaf.
 * `prefix` and `suffix` work in a similar way to the attributes of the same
   names in Thymeleaf's TemplateResolver objects.
 * `order` establishes the order in which the ViewResolver will be queried in
   the chain.
 * `viewNames` allows the definition (with wildcards) of the view names that
   will be resolved by this ViewResolver.

### Views and View Resolvers in Thymeleaf

Thymeleaf offers implementations for the two interfaces mentioned above:

 * `org.thymeleaf.spring6.view.ThymeleafView`
 * `org.thymeleaf.spring6.view.ThymeleafViewResolver`

These two classes will be in charge of processing Thymeleaf templates as a
result of the execution of controllers.

Configuration of the Thymeleaf View Resolver is very similar to that of JSP:

```java
@Bean
public ThymeleafViewResolver viewResolver(){
    ThymeleafViewResolver viewResolver = new ThymeleafViewResolver();
    viewResolver.setTemplateEngine(templateEngine());
    // NOTE 'order' and 'viewNames' are optional
    viewResolver.setOrder(1);
    viewResolver.setViewNames(new String[] {".html", ".xhtml"});
    return viewResolver;
}
```

...or in XML:

```xml
<bean class="org.thymeleaf.spring6.view.ThymeleafViewResolver">
  <property name="templateEngine" ref="templateEngine" />
  <!-- NOTE 'order' and 'viewNames' are optional -->
  <property name="order" value="1" />
  <property name="viewNames" value="*.html,*.xhtml" />
</bean>
```

The `templateEngine` parameter is, of course, the `SpringTemplateEngine` object
we defined above. The other two (`order` and `viewNames`) are
both optional, and have the same meaning as in the JSP ViewResolver we saw
before.

Note that we do not need `prefix` or `suffix` parameters, because these are
already specified at the Template Resolver (which in turn is passed to the
Template Engine).

And what if we wanted to define a `View` bean and add some static variables to
it? Easy, just define a *prototype* bean for it:

```java
@Bean
@Scope("prototype")
public ThymeleafView mainView() {
    ThymeleafView view = new ThymeleafView("main"); // templateName = 'main'
    view.setStaticVariables(
        Collections.singletonMap("footer", "The ACME Fruit Company"));
    return view;
}
```

By doing this, you will be able to execute specifically this view bean
selecting it by bean name (`mainView`, in this case).

## Spring MVC configuration

Next we need to set up the Spring MVC configuration for the application, which
will include not only the standard Spring MVC artifacts like resource handling
or annotation scanning, but also the creation of the Template Engine and View
Resolver instances.

```java
@Configuration
@EnableWebMvc
@ComponentScan
public class SpringWebConfig
        implements WebMvcConfigurer, ApplicationContextAware {

    private ApplicationContext applicationContext;


    public SpringWebConfig() {
        super();
    }


    public void setApplicationContext(final ApplicationContext applicationContext)
            throws BeansException {
        this.applicationContext = applicationContext;
    }



    /* ******************************************************************* */
    /*  GENERAL CONFIGURATION ARTIFACTS                                    */
    /*  Static Resources, i18n Messages, Formatters (Conversion Service)   */
    /* ******************************************************************* */

    @Override
    public void addResourceHandlers(final ResourceHandlerRegistry registry) {
        super.addResourceHandlers(registry);
        registry.addResourceHandler("/images/**").addResourceLocations("/images/");
        registry.addResourceHandler("/css/**").addResourceLocations("/css/");
        registry.addResourceHandler("/js/**").addResourceLocations("/js/");
    }

    @Bean
    public ResourceBundleMessageSource messageSource() {
        ResourceBundleMessageSource messageSource = new ResourceBundleMessageSource();
        messageSource.setBasename("Messages");
        return messageSource;
    }

    @Override
    public void addFormatters(final FormatterRegistry registry) {
        super.addFormatters(registry);
        registry.addFormatter(varietyFormatter());
        registry.addFormatter(dateFormatter());
    }

    @Bean
    public VarietyFormatter varietyFormatter() {
        return new VarietyFormatter();
    }

    @Bean
    public DateFormatter dateFormatter() {
        return new DateFormatter();
    }



    /* **************************************************************** */
    /*  THYMELEAF-SPECIFIC ARTIFACTS                                    */
    /*  TemplateResolver <- TemplateEngine <- ViewResolver              */
    /* **************************************************************** */

    @Bean
    public SpringResourceTemplateResolver templateResolver(){
        // SpringResourceTemplateResolver automatically integrates with Spring's own
        // resource resolution infrastructure, which is highly recommended.
        SpringResourceTemplateResolver templateResolver = new SpringResourceTemplateResolver();
        templateResolver.setApplicationContext(this.applicationContext);
        templateResolver.setPrefix("/WEB-INF/templates/");
        templateResolver.setSuffix(".html");
        // HTML is the default value, added here for the sake of clarity.
        templateResolver.setTemplateMode(TemplateMode.HTML);
        // Template cache is true by default. Set to false if you want
        // templates to be automatically updated when modified.
        templateResolver.setCacheable(true);
        return templateResolver;
    }

    @Bean
    public SpringTemplateEngine templateEngine(){
        // SpringTemplateEngine automatically applies SpringStandardDialect and
        // enables Spring's own MessageSource message resolution mechanisms.
        SpringTemplateEngine templateEngine = new SpringTemplateEngine();
        templateEngine.setTemplateResolver(templateResolver());
        // Enabling the SpringEL compiler can speed up execution in most
        // scenarios, but might be incompatible with specific cases when
        // expressions in one template are reused across different data
        // types, so this flag is "false" by default for safer backwards
        // compatibility.
        templateEngine.setEnableSpringELCompiler(true);
        return templateEngine;
    }

    @Bean
    public ThymeleafViewResolver viewResolver(){
        ThymeleafViewResolver viewResolver = new ThymeleafViewResolver();
        viewResolver.setTemplateEngine(templateEngine());
        return viewResolver;
    }

}
```

---

*Adapted from the Thymeleaf documentation at thymeleaf.org, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/): [The SpringStandard Dialect](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#the-springstandard-dialect), [Views and View Resolvers](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#views-and-view-resolvers), [Spring MVC configuration](https://www.thymeleaf.org/doc/tutorials/3.1/thymeleafspring.html#spring-mvc-configuration).*

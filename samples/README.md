# Samples

The examples in the docs run here, against Spring Boot 4.1.2 and Thymeleaf 3.1.5.

- `quickstart`: the application from Quickstart: Spring Boot.
- `showcase`: the Seed Starter Manager and grocery examples, with Spring Security, htmx and Alpine.js.

```sh
cd samples/showcase
./mvnw test             # needs Java 21 or later
./mvnw spring-boot:run  # http://localhost:8080/seedstarters and /grocery/products
```

`DocsExamplesTest` in `showcase` reads the pages in `src/content/docs/docs` and runs their code blocks:

- A block titled `Template` must render to the `Output` block after it.
- A block titled `Rejected` must fail with a `TemplateProcessingException`.
- A block titled with a file path must appear verbatim in that file in a sample.

Add `, with ?name=value` to a `Template` or `Rejected` title to set a request parameter.

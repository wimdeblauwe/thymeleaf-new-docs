package org.thymeleaf.samples.showcase;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;
import org.springframework.context.support.StaticMessageSource;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.thymeleaf.context.WebContext;
import org.thymeleaf.exceptions.TemplateProcessingException;
import org.thymeleaf.samples.showcase.grocery.Product;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.ClassLoaderTemplateResolver;
import org.thymeleaf.templateresolver.StringTemplateResolver;
import org.thymeleaf.web.servlet.JakartaServletWebApplication;

/**
 * Runs the examples in the published pages, so a page can't drift from what Thymeleaf does.
 *
 * In any page below src/content/docs/docs, and in the home page's examples:
 * - a "Template" code block followed by an "Output" block must render to that output
 * - a "Rejected" code block must fail with a TemplateProcessingException
 * - a block titled with a file path must appear verbatim in that file of a sample application
 */
class DocsExamplesTest {

    private static final Path REPOSITORY = Path.of("../..").toAbsolutePath().normalize();
    private static final Path DOCS = REPOSITORY.resolve("src/content/docs/docs");
    private static final Path HOME_EXAMPLES = REPOSITORY.resolve("src/data/home-examples.md");
    private static final Pattern BLOCK = Pattern.compile(
            "^```(\\w+)(?: title=\"([^\"]*)\")?\\n(.*?)^```$", Pattern.DOTALL | Pattern.MULTILINE);

    private static SpringTemplateEngine engine;

    private record Block(String title, String code, int end, int start) {
    }

    @BeforeAll
    static void createEngine() {
        ClassLoaderTemplateResolver files = new ClassLoaderTemplateResolver();
        files.setPrefix("templates/");
        files.setSuffix(".html");
        files.setCheckExistence(true);
        files.setOrder(1);
        StringTemplateResolver strings = new StringTemplateResolver();
        strings.setOrder(2);
        StaticMessageSource messages = new StaticMessageSource();
        messages.addMessage("home.welcome", java.util.Locale.ENGLISH, "Welcome, {0}!");
        engine = new SpringTemplateEngine();
        engine.setTemplateResolvers(java.util.Set.of(files, strings));
        engine.setMessageSource(messages);
    }

    private static Map<String, Object> model() {
        Product basil = new Product("Fresh sweet basil", new BigDecimal("4.99"), true, 3);
        Product tomato = new Product("Italian tomato", new BigDecimal("1.25"), false, 0);
        Map<String, Object> model = new LinkedHashMap<>();
        model.put("product", basil);
        model.put("products", List.of(basil, tomato));
        model.put("noProducts", List.of());
        model.put("prices", new java.util.TreeMap<>(Map.of("basil", 4.99, "tomato", 1.25)));
        model.put("role", "manager");
        model.put("loggedIn", true);
        model.put("missing", null);
        model.put("comment", "<b>Tasty</b> & fresh");
        model.put("description", "<em>Grown</em> nearby");
        model.put("website", "javascript:alert(1)");
        model.put("customerName", "Ann'; alert(1); //");
        model.put("colour", "red");
        return model;
    }

    private static String render(String template, String query) {
        MockServletContext servletContext = new MockServletContext();
        MockHttpServletRequest request = new MockHttpServletRequest(servletContext, "GET", "/grocery/products");
        request.setContextPath("");
        request.setPreferredLocales(List.of(java.util.Locale.ENGLISH));
        if (query != null) {
            for (String pair : query.split("&")) {
                String[] parts = pair.split("=", 2);
                request.addParameter(parts[0], parts[1]);
            }
        }
        WebContext context = new WebContext(
                JakartaServletWebApplication.buildApplication(servletContext)
                        .buildExchange(request, new MockHttpServletResponse()),
                java.util.Locale.ENGLISH, model());
        return engine.process(template, context);
    }

    private static String normalise(String html) {
        return html.replaceAll(">\\s+<", "><").replaceAll("\\s+", " ").trim();
    }

    private static List<Path> pages() throws IOException {
        try (Stream<Path> files = Files.walk(DOCS)) {
            return Stream.concat(files.filter(file -> file.toString().endsWith(".md")).sorted(),
                    Stream.of(HOME_EXAMPLES)).toList();
        }
    }

    private static List<Block> blocks(Path page) throws IOException {
        String text = Files.readString(page);
        List<Block> blocks = new ArrayList<>();
        Matcher matcher = BLOCK.matcher(text);
        while (matcher.find()) {
            blocks.add(new Block(matcher.group(2), matcher.group(3), matcher.end(), matcher.start()));
        }
        return blocks;
    }

    @TestFactory
    List<DynamicTest> examplesInThePagesRun() throws IOException {
        List<DynamicTest> tests = new ArrayList<>();
        for (Path page : pages()) {
            String text = Files.readString(page);
            String name = REPOSITORY.relativize(page).toString();
            List<Block> blocks = blocks(page);
            for (int i = 0; i < blocks.size(); i++) {
                Block block = blocks.get(i);
                if (block.title() == null) {
                    continue;
                }
                String label = name + " block " + (i + 1) + " " + block.title();
                if (block.title().equals("Template") || block.title().startsWith("Template, ")) {
                    Block output = i + 1 < blocks.size() ? blocks.get(i + 1) : null;
                    assertThat(output).as(label).isNotNull();
                    assertThat(output.title()).as(label + " needs an Output block").isEqualTo("Output");
                    assertThat(text.substring(block.end(), output.start()).trim()).as(label + " separator").isEmpty();
                    String query = block.title().contains("?") ? block.title().split("\\?")[1] : null;
                    tests.add(DynamicTest.dynamicTest(label, () ->
                            assertThat(normalise(render(block.code(), query))).isEqualTo(normalise(output.code()))));
                }
                else if (block.title().equals("Rejected") || block.title().startsWith("Rejected, ")) {
                    String query = block.title().contains("?") ? block.title().split("\\?")[1] : null;
                    tests.add(DynamicTest.dynamicTest(label, () ->
                            assertThatThrownBy(() -> render(block.code(), query))
                                    .isInstanceOf(TemplateProcessingException.class)));
                }
                else if (block.title().contains("/") || block.title().equals("pom.xml")) {
                    tests.add(DynamicTest.dynamicTest(label, () -> assertInSample(block)));
                }
            }
        }
        return tests;
    }

    private static void assertInSample(Block block) throws IOException {
        for (String sample : List.of("quickstart", "showcase")) {
            Path file = REPOSITORY.resolve("samples").resolve(sample).resolve(block.title());
            if (Files.exists(file) && Files.readString(file).contains(block.code().stripTrailing())) {
                return;
            }
        }
        throw new AssertionError("Not found verbatim in a sample: " + block.title() + "\n" + block.code());
    }
}

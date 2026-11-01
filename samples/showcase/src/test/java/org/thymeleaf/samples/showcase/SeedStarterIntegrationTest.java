package org.thymeleaf.samples.showcase;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.matchesPattern;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;

/** Checks the behaviour that the Forms, Partial page updates and Components pages describe. */
@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
class SeedStarterIntegrationTest {

    @Autowired
    private MockMvc mvc;

    @Test
    void thActionAddsTheCsrfField() throws Exception {
        mvc.perform(get("/seedstarters/new"))
                .andExpect(content().string(containsString("<input type=\"hidden\" name=\"_csrf\"")));
    }

    @Test
    void postWithoutCsrfTokenIsForbidden() throws Exception {
        mvc.perform(post("/seedstarters").param("name", "Porch")).andExpect(status().isForbidden());
    }

    @Test
    void thMethodRendersPostAndHiddenField() throws Exception {
        mvc.perform(get("/seedstarters/1/edit"))
                .andExpect(content().string(containsString("method=\"post\"")))
                .andExpect(content().string(containsString("<input type=\"hidden\" name=\"_method\" value=\"delete\"/>")))
                .andExpect(content().string(containsString("<input type=\"hidden\" name=\"_method\" value=\"put\"/>")));
    }

    @Test
    void hiddenMethodReachesDeleteMapping() throws Exception {
        mvc.perform(post("/seedstarters/1").param("_method", "delete").with(csrf()))
                .andExpect(redirectedUrl("/seedstarters"));
    }

    @Test
    void invalidFormShowsErrorsAndKeepsInput() throws Exception {
        mvc.perform(post("/seedstarters").param("name", "").param("datePlanted", "").with(csrf()))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString(
                        "<input type=\"text\" id=\"name\" name=\"name\" value=\"\" class=\"invalid\">")))
                .andExpect(content().string(containsString("<p>must not be blank</p>")));
    }

    @Test
    void addRowRendersIndexedFields() throws Exception {
        mvc.perform(post("/seedstarters").param("addRow", "").with(csrf()))
                .andExpect(content().string(containsString("<select id=\"rows0.variety\" name=\"rows[0].variety\">")))
                .andExpect(content().string(containsString("name=\"rows[0].seedsPerCell\"")));
    }

    @Test
    void checkboxGetsMarkerField() throws Exception {
        mvc.perform(get("/seedstarters/new"))
                .andExpect(content().string(containsString("<input type=\"hidden\" name=\"_features\" value=\"on\"/>")));
    }

    @Test
    void htmxSearchGetsOnlyTheRows() throws Exception {
        mvc.perform(get("/seedstarters").param("search", "kit").header("HX-Request", "true"))
                .andExpect(header().string("Vary", "HX-Request"))
                .andExpect(content().string(allOf(startsWith("<tbody id=\"seedstarter-rows\">"),
                        containsString("Kitchen window"), not(containsString("Balcony box")),
                        not(containsString("<html")))));
    }

    @Test
    void historyRestoreGetsTheFullPage() throws Exception {
        mvc.perform(get("/seedstarters").header("HX-Request", "true").header("HX-History-Restore-Request", "true"))
                .andExpect(content().string(containsString("<html")));
    }

    @Test
    void htmxDeleteReturnsTheNewCount() throws Exception {
        mvc.perform(delete("/seedstarters/1").header("HX-Request", "true").with(csrf()))
                .andExpect(status().isOk())
                .andExpect(content().string("<span id=\"seedstarter-count\" hx-swap-oob=\"true\">2</span>"));
    }

    @Test
    void htmxDeleteWithoutTokenIsForbidden() throws Exception {
        mvc.perform(delete("/seedstarters/1").header("HX-Request", "true")).andExpect(status().isForbidden());
    }

    @Test
    void pageCarriesTheCsrfHeaderForHtmx() throws Exception {
        mvc.perform(get("/seedstarters"))
                .andExpect(content().string(matchesPatternDotAll(
                        ".*<body hx-headers=\"\\{&quot;X-CSRF-TOKEN&quot;: &quot;[^&]+&quot;\\}\">.*")));
    }

    @Test
    void componentsRender() throws Exception {
        mvc.perform(get("/grocery/products"))
                .andExpect(content().string(containsString("<div class=\"alert alert-info\" role=\"alert\">")))
                .andExpect(content().string(containsString("<span class=\"badge\">Sold out</span>")))
                .andExpect(content().string(containsString("<footer>Default footer</footer>")))
                .andExpect(content().string(not(containsString("th:"))));
    }

    @Test
    void alpineAttributesPassThrough() throws Exception {
        mvc.perform(get("/grocery/quantity"))
                .andExpect(content().string(containsString("@click=\"quantity--\" :disabled=\"quantity === 0\"")))
                .andExpect(content().string(containsString("x-on:click=\"quantity++\"")))
                .andExpect(content().string(containsString("data-quantity=\"3\"")));
    }

    private static org.hamcrest.Matcher<String> matchesPatternDotAll(String regex) {
        return matchesPattern(java.util.regex.Pattern.compile(regex, java.util.regex.Pattern.DOTALL));
    }
}

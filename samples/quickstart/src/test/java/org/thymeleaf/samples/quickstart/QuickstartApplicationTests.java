package org.thymeleaf.samples.quickstart;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class QuickstartApplicationTests {

    @Autowired
    private MockMvc mvc;

    @Test
    void rendersTheSeedStarterPage() throws Exception {
        mvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("<title>Seed starters</title>")))
                .andExpect(content().string(containsString("<li>Thymus vulgaris</li>")))
                .andExpect(content().string(containsString("<li>Thymus serpyllum</li>")))
                .andExpect(content().string(not(containsString("Thymus citriodorus"))))
                .andExpect(content().string(not(containsString("th:"))));
    }
}

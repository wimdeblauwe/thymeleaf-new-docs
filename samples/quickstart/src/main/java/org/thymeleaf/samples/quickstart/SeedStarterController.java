package org.thymeleaf.samples.quickstart;

import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SeedStarterController {

    @GetMapping("/")
    public String seedStarters(Model model) {
        model.addAttribute("title", "Seed starters");
        model.addAttribute("varieties", List.of("Thymus vulgaris", "Thymus serpyllum"));
        return "seedstarters";
    }
}

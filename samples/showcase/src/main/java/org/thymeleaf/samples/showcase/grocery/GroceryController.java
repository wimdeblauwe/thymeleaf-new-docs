package org.thymeleaf.samples.showcase.grocery;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/grocery")
public class GroceryController {

    private static final Product BASIL = new Product("Fresh sweet basil", new BigDecimal("4.99"), true, 3);
    private static final Product TOMATO = new Product("Italian tomato", new BigDecimal("1.25"), false, 0);

    @GetMapping("/products")
    public String products(Model model) {
        model.addAttribute("products", List.of(BASIL, TOMATO));
        return "grocery/products";
    }

    @GetMapping("/quantity")
    public String quantity(Model model) {
        model.addAttribute("product", BASIL);
        return "grocery/quantity";
    }
}

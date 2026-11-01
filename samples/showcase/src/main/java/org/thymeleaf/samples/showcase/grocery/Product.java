package org.thymeleaf.samples.showcase.grocery;

import java.math.BigDecimal;

public record Product(String name, BigDecimal price, boolean inStock, int stock) {
}

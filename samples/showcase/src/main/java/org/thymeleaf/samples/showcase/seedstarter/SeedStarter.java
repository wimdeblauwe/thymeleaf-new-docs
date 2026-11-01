package org.thymeleaf.samples.showcase.seedstarter;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.format.annotation.DateTimeFormat;

public class SeedStarter {

    private Long id;

    @NotBlank
    private String name;

    @NotNull
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate datePlanted;

    private boolean covered;
    private Type type = Type.PLASTIC;
    private Set<Feature> features = EnumSet.noneOf(Feature.class);
    private List<Row> rows = new ArrayList<>();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public LocalDate getDatePlanted() { return datePlanted; }
    public void setDatePlanted(LocalDate datePlanted) { this.datePlanted = datePlanted; }
    public boolean isCovered() { return covered; }
    public void setCovered(boolean covered) { this.covered = covered; }
    public Type getType() { return type; }
    public void setType(Type type) { this.type = type; }
    public Set<Feature> getFeatures() { return features; }
    public void setFeatures(Set<Feature> features) { this.features = features; }
    public List<Row> getRows() { return rows; }
    public void setRows(List<Row> rows) { this.rows = rows; }
}

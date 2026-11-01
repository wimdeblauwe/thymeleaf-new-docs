package org.thymeleaf.samples.showcase.seedstarter;

import java.time.LocalDate;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Repository;

/** Keeps seed starters in memory, so the sample needs no database. */
@Repository
public class SeedStarterRepository {

    private final Map<Long, SeedStarter> seedStarters = new ConcurrentSkipListMap<>();
    private final AtomicLong nextId = new AtomicLong(1);

    public SeedStarterRepository() {
        for (String name : List.of("Greenhouse tray", "Kitchen window", "Balcony box")) {
            SeedStarter seedStarter = new SeedStarter();
            seedStarter.setName(name);
            seedStarter.setDatePlanted(LocalDate.of(2026, 3, 14));
            save(seedStarter);
        }
    }

    public List<SeedStarter> search(String text) {
        String lowerCaseText = text.toLowerCase(Locale.ROOT);
        return seedStarters.values().stream()
                .filter(seedStarter -> seedStarter.getName().toLowerCase(Locale.ROOT).contains(lowerCaseText))
                .toList();
    }

    public Optional<SeedStarter> findById(long id) {
        return Optional.ofNullable(seedStarters.get(id));
    }

    public void save(SeedStarter seedStarter) {
        if (seedStarter.getId() == null) {
            seedStarter.setId(nextId.getAndIncrement());
        }
        seedStarters.put(seedStarter.getId(), seedStarter);
    }

    public void deleteById(long id) {
        seedStarters.remove(id);
    }

    public int count() {
        return seedStarters.size();
    }
}

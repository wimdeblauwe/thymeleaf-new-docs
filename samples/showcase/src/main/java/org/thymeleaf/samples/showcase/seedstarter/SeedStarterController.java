package org.thymeleaf.samples.showcase.seedstarter;

import java.util.List;

import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.view.FragmentsRendering;

@Controller
@RequestMapping("/seedstarters")
public class SeedStarterController {

    private final SeedStarterRepository seedStarters;

    public SeedStarterController(SeedStarterRepository seedStarters) {
        this.seedStarters = seedStarters;
    }

    @ModelAttribute("allTypes")
    public Type[] allTypes() {
        return Type.values();
    }

    @ModelAttribute("allFeatures")
    public Feature[] allFeatures() {
        return Feature.values();
    }

    @ModelAttribute("allVarieties")
    public List<String> allVarieties() {
        return List.of("Thymus vulgaris", "Thymus serpyllum");
    }

    @GetMapping
    public String list(@RequestParam(defaultValue = "") String search,
                       @RequestHeader(name = "HX-Request", required = false) String htmxRequest,
                       @RequestHeader(name = "HX-History-Restore-Request", required = false) String historyRestore,
                       HttpServletResponse response,
                       Model model) {
        model.addAttribute("search", search);
        model.addAttribute("seedStarters", seedStarters.search(search));
        model.addAttribute("total", seedStarters.count());
        response.addHeader("Vary", "HX-Request");
        if (htmxRequest != null && historyRestore == null) {
            return "seedstarters/list :: rows";
        }
        return "seedstarters/list";
    }

    @GetMapping("/new")
    public String newForm(Model model) {
        model.addAttribute("seedStarter", new SeedStarter());
        return "seedstarters/form";
    }

    @GetMapping("/{id}/edit")
    public String editForm(@PathVariable long id, Model model) {
        model.addAttribute("seedStarter", find(id));
        return "seedstarters/edit";
    }

    @PostMapping(params = "addRow")
    public String addRow(SeedStarter seedStarter, BindingResult bindingResult) {
        seedStarter.getRows().add(new Row());
        return "seedstarters/form";
    }

    @PostMapping(params = "removeRow")
    public String removeRow(SeedStarter seedStarter, BindingResult bindingResult,
                            @RequestParam int removeRow) {
        seedStarter.getRows().remove(removeRow);
        return "seedstarters/form";
    }

    @PostMapping
    public String create(@Valid SeedStarter seedStarter, BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "seedstarters/form";
        }
        seedStarters.save(seedStarter);
        return "redirect:/seedstarters";
    }

    @PutMapping("/{id}")
    public String update(@PathVariable long id, @Valid SeedStarter seedStarter,
                         BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "seedstarters/edit";
        }
        seedStarter.setId(id);
        seedStarters.save(seedStarter);
        return "redirect:/seedstarters";
    }

    @DeleteMapping(path = "/{id}", headers = "HX-Request")
    public FragmentsRendering deleteWithHtmx(@PathVariable long id, Model model) {
        seedStarters.deleteById(id);
        model.addAttribute("total", seedStarters.count());
        return FragmentsRendering.fragment("seedstarters/list :: count").build();
    }

    @DeleteMapping("/{id}")
    public String delete(@PathVariable long id) {
        seedStarters.deleteById(id);
        return "redirect:/seedstarters";
    }

    private SeedStarter find(long id) {
        return seedStarters.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }
}

package de.hilbert.voebbwatchlist;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.shell.standard.ShellComponent;
import org.springframework.shell.standard.ShellMethod;
import org.springframework.shell.standard.ShellOption;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@ShellComponent
@Slf4j
public class MyCommands {

    @Autowired
    private VoebbCrawler voebbCrawler;

    @Autowired
    private EmailService emailService;

    @Value("${app.mail.delivery.enable}")
    private Boolean MAIL_DELIVERY_ENABLED;

    @ShellMethod(key = "hello-world")
    public String helloWorld(@ShellOption(defaultValue = "spring") String arg) {
        return "Hello world " + arg;
    }

    @ShellMethod(key = "check-wishlist", value = "checks availability for given mediums.txt and given libraries.")
    public void checkAvailability(@ShellOption(defaultValue = "mediums.txt") String mediumsPath,
                                  @ShellOption(defaultValue = "libraries.txt") String librariesPath) {
        try {
            List<String> mediumLines = Files.readAllLines(Paths.get(mediumsPath));
            List<String> libraries = Files.readAllLines(Paths.get(librariesPath));

            log.info("Checking availability of {} mediumLines ({}) in {} libraries ({}) ...", mediumLines.size(), mediumsPath, libraries.size(), librariesPath);

            ArrayList<Medium> mediums = new ArrayList<>();

            for (String mediumLine : mediumLines) {
                String sakId = mediumLine.split(",")[0];

                if (mediumLine.isEmpty() || sakId == null || sakId.isEmpty()) {
                    log.warn("skipping empty line or sakId");
                    continue;
                }

                String customTitle = mediumLine.split(",").length < 2 ? null : mediumLine.split(",")[1];

                Medium medium = voebbCrawler.crawlForMedium(sakId, libraries);

                medium.setSakId(sakId);
                medium.setTitleCustom(customTitle);
                mediums.add(medium);
            }

            mediums.forEach(medium -> log.info(medium.toString()));
            String printableMediums = prettify(mediums);

            log.info(printableMediums);

            if (MAIL_DELIVERY_ENABLED) {
                log.info("desired mail delivery recognised, will proceed with mail delivery");
                emailService.sendSimpleMessage(printableMediums);
            }

        } catch (Exception e) {
            log.error("Error", e);
        }
    }

    /**
     * tranforms the given mediums to a string represantation which can be printed.
     * the format looks like this:
     * <p>
     * Folgende Medien deiner Wunschliste sind nun verfügbar:
     * 1. kurztitel --> Ort
     * 2. kurztitel --> Ort
     * 3. kurztitel --> Ort
     * <p>
     * Folgende Medien deiner Wunschliste gibt es in deinen Bibliotheken, siond jedoch gerade nicht verfügbar:
     * 1. kurztitel
     * 2. kurztitel
     * 3. kurztitel
     * <p>
     * Folgende Medien deiner Wunschliste gibt es leider in keiner deiner Bibliotheken:
     * 1. kurztitel
     * 2. kurztitel
     * 3. kurztitel
     */
    private String prettify(ArrayList<Medium> mediums) {
        StringBuilder available = new StringBuilder("Folgende Medien deiner Wunschliste sind nun verfügbar:\n");
        StringBuilder notAvailable = new StringBuilder("Folgende Medien deiner Wunschliste gibt es in deinen Bibliotheken, sind jedoch gerade nicht verfügbar:\n");
        StringBuilder notInLibraries = new StringBuilder("Folgende Medien deiner Wunschliste gibt es leider in keiner deiner Bibliotheken:\n");

        int availableCount = 1;
        int notAvailableCount = 1;
        int notInLibrariesCount = 1;

        for (Medium medium : mediums) {

            StringBuilder location = new StringBuilder();

            if (!medium.getAvailableWantedLibraries().isEmpty()) {
                for (Location availableWantedLibrary : medium.getAvailableWantedLibraries()) {
                    location.append("\n\t");
                    location.append(availableWantedLibrary.name());
                    location.append(": ");
                    location.append(availableWantedLibrary.area());
                    location.append(" --> ");
                    location.append(availableWantedLibrary.precise());
                }
            }

            String entry = String.format("%d. %s (%s) %s\n",
                    !medium.getAvailableWantedLibraries().isEmpty() ? availableCount++ :
                            !medium.getUnavailableWantedLibraries().isEmpty() ? notAvailableCount++ :
                                    notInLibrariesCount++,
                    medium.getTitleCustom() == null ? medium.getTitle() : medium.getTitleCustom(),
                    medium.getDirectLink(),
                    location);

            if (!medium.getAvailableWantedLibraries().isEmpty()) {
                available.append(entry);
            } else if (!medium.getUnavailableWantedLibraries().isEmpty()) {
                notAvailable.append(entry);
            } else {
                notInLibraries.append(entry);
            }
        }

        return available
                .append("\n")
                .append(notAvailable)
                .append("\n")
                .append(notInLibraries)
                .append("\n\n")
                .toString();
    }
}

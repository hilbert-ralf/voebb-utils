package de.hilbert.voebbwatchlist;

import lombok.extern.log4j.Log4j;
import lombok.extern.slf4j.Slf4j;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
@Slf4j
public class VoebbCrawler {
    private static final String URL_MEDIUM = "https://www.voebb.de//aDISWeb/app?service=direct/0/Home/$DirectLink&sp=SPROD00&sp=SAK";

    public Medium crawlForMedium(String sakId, List<String> libraries) {
        Medium medium = new Medium();
        RestTemplate restTemplate = new RestTemplate();
        String url = URL_MEDIUM + sakId;

        medium.setDirectLink(url);

        log.info("crawl for sakId: " + sakId);
        String response = restTemplate.getForObject(url, String.class);

        log.debug("Response from {}: {}", url, response);

        Document doc = Jsoup.parse(response);
        Elements tables = doc.select("table");

        if (tables.size() < 2 || tables.get(1).text().isEmpty()) {
            log.warn("Table with availabilities not found. Medium with sakId '{}' will be skipped", sakId);
            medium.setPhysicallyFound(false);
            return medium;
        }
        medium.setPhysicallyFound(true);

        if (!tables.get(0).select("tr").get(4).text().isEmpty() ) {
            String title = tables.get(0).select("tr").get(4).text();
            medium.setTitle(title);
        }

        Element availabilityTable = tables.get(1);
        Elements availabilityRows = availabilityTable.select("tr");

        for (Element availabilityRow : availabilityRows) {
            Elements columns = availabilityRow.select("td");

            if (columns.size() >= 3) {
                String library = columns.get(0).text();
                String locationArea = columns.get(1).text();
                String locationPrecise = columns.get(2).text();
                String availability = columns.getLast().text(); // sometimes the column amount differs but availability is always in last column

                if (libraries.contains(library)) {
                    if ("Verfügbar".equals(availability)) {
                        log.debug("\"{}\" in library {} available and to be found at: {} --> {}", medium.getTitle(), library, locationArea, locationPrecise);
                        medium.getAvailableWantedLibraries().add(new Location(library, locationArea, locationPrecise));
                    } else {
                        log.debug("In inventory of library {} but currently not available", library);
                        medium.getUnavailableWantedLibraries().add(new Location(library, locationArea, locationPrecise));
                    }
                } else {
                    log.debug("Library {} does not have this mediumLine.", library);
                }
            }
        }
        return medium;
    }
}

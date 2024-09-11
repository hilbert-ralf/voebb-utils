package de.hilbert.voebbwatchlist;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Data
public class Medium {
    private String sakId;
    private String titleCustom;
    private String title;
    private boolean physicallyFound;
    private List<Location> availableWantedLibraries = new ArrayList<>();
    private List<Location> unavailableWantedLibraries = new ArrayList<>();
}

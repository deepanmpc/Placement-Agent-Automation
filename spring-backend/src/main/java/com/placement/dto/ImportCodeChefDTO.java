package com.placement.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ImportCodeChefDTO {

    @NotBlank(message = "Student UUID is required")
    private String studentUuid;

    private Integer currentRating;
    private Integer highestRating;
    private String currentStars;
    private Integer globalRank;
    private Integer countryRank;

    private Integer totalProblemsSolved;
    private Integer contestsParticipated;

    /**
     * JSON string of problem-solving breakdown.
     */
    private String problemStatsJson;

    /**
     * JSON string of recent contest results.
     */
    private String recentContestsJson;

    private String profileUrl;
    private LocalDateTime snapshotDate;
}

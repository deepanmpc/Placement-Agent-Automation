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
public class ImportCodeforcesDTO {

    @NotBlank(message = "Student UUID is required")
    private String studentUuid;

    private Integer currentRating;
    private Integer maxRating;
    private String currentRank;
    private String maxRank;
    private Integer contestsParticipated;

    /**
     * JSON string of problem-solving stats by difficulty/tag.
     */
    private String problemStatsJson;

    /**
     * JSON string of recent contest performance.
     */
    private String recentContestsJson;

    private Integer totalSubmissions;
    private Integer acceptedSubmissions;
    private Integer totalProblemsSolved;

    private String profileUrl;
    private LocalDateTime snapshotDate;
}

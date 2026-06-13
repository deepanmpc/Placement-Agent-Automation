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
public class ImportLeetCodeDTO {

    @NotBlank(message = "Student UUID is required")
    private String studentUuid;

    private Integer totalSolved;
    private Integer easySolved;
    private Integer mediumSolved;
    private Integer hardSolved;
    private Integer totalQuestions;

    private Double acceptanceRate;
    private Integer ranking;
    private Integer contestRating;
    private Integer contestsAttended;
    private Integer globalRanking;

    /**
     * JSON string of recent submissions.
     */
    private String recentSubmissionsJson;

    /**
     * JSON string of skills/tags distribution.
     */
    private String skillsJson;

    /**
     * JSON string of badge information.
     */
    private String badgesJson;

    private String profileUrl;
    private LocalDateTime snapshotDate;
}

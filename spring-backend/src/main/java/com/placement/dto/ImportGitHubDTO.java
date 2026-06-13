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
public class ImportGitHubDTO {

    @NotBlank(message = "Student UUID is required")
    private String studentUuid;

    private Integer publicRepos;
    private Integer totalStars;
    private Integer totalForks;
    private Integer followers;
    private Integer following;
    private Integer totalCommitsLastYear;
    private Integer totalPrsLastYear;
    private Integer totalIssuesLastYear;

    /**
     * JSON string of top languages.
     * Example: {"Java": 45.2, "Python": 30.1, "JavaScript": 24.7}
     */
    private String topLanguagesJson;

    /**
     * JSON string of pinned/top repositories.
     */
    private String topReposJson;

    private String profileUrl;
    private String bio;
    private String company;
    private String location;

    private LocalDateTime snapshotDate;
}

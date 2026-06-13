package com.placement.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ImportRankingDTO {

    @NotBlank(message = "Student UUID is required")
    private String studentUuid;

    @NotNull(message = "Job ID is required")
    private Long jobId;

    private BigDecimal ruleScore;
    private BigDecimal semanticScore;
    private BigDecimal finalScore;
    private Integer rankPosition;

    /**
     * JSON string containing detailed scoring explanation.
     * Example: {"skill_match": 8.5, "experience_fit": 7.0, ...}
     */
    private String explanationJson;
}

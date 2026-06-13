package com.placement.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class JobDescriptionDTO {

    private Long id;

    @NotBlank(message = "Title is required")
    private String title;

    @NotBlank(message = "Company is required")
    private String company;

    private String description;

    /**
     * JSON string of required skills.
     * Example: ["Java", "Spring Boot", "SQL"]
     */
    private String requiredSkillsJson;

    /**
     * JSON string of eligibility criteria.
     * Example: {"min_cgpa": 7.0, "departments": ["CSE","IT"]}
     */
    private String eligibilityJson;
}

package com.placement.dto;

import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StudentDTO {

    private String uuid;

    @NotBlank(message = "Name is required")
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;

    private String phone;

    @NotBlank(message = "Department is required")
    private String department;

    private Integer graduationYear;

    @DecimalMin(value = "0.0", message = "CGPA must be >= 0")
    @DecimalMax(value = "10.0", message = "CGPA must be <= 10")
    private BigDecimal cgpa;

    private String resumeUrl;

    // ── Platform Usernames ──────────────────────────────
    private String githubUsername;
    private String leetcodeUsername;
    private String codeforcesUsername;
    private String codechefUsername;

    // ── Extracted Resume Data (JSON strings) ────────────
    private String skillsJson;
    private String projectsJson;
    private String certificationsJson;
    private String experienceJson;

    // ── Status ──────────────────────────────────────────
    private Boolean active;
}

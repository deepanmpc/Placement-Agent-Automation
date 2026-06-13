package com.placement.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ImportStudentProfileDTO {

    @NotBlank(message = "Name is required")
    private String name;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    private String email;

    private String phone;
    private String department;
    private Integer graduationYear;
    private BigDecimal cgpa;

    // ── Platform Usernames ──────────────────────────────
    private String githubUsername;
    private String leetcodeUsername;
    private String codeforcesUsername;
    private String codechefUsername;

    // ── Resume Data ─────────────────────────────────────
    private String resumeUrl;

    /**
     * JSON string of extracted skills from resume.
     */
    private String skillsJson;

    /**
     * JSON string of extracted projects from resume.
     */
    private String projectsJson;

    /**
     * JSON string of certifications from resume.
     */
    private String certificationsJson;

    /**
     * JSON string of work experience from resume.
     */
    private String experienceJson;

    /**
     * JSON string of education details from resume.
     */
    private String educationJson;

    /**
     * Raw text extracted from resume.
     */
    private String resumeRawText;
}

package com.placement.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DashboardStatsDTO {

    private Long studentCount;
    private Long departmentCount;
    private BigDecimal avgCgpa;

    // ── Platform Averages ───────────────────────────────
    private Double avgGithubRepos;
    private Double avgLeetcodeRating;

    // ── Top Students (list of summary maps/DTOs) ────────
    private List<TopStudentSummary> topStudents;

    // ── Recent Imports ──────────────────────────────────
    private List<RecentImportSummary> recentImports;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TopStudentSummary {
        private String uuid;
        private String name;
        private String department;
        private BigDecimal cgpa;
        private Integer githubRepos;
        private Integer leetcodeSolved;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RecentImportSummary {
        private String type;
        private String studentName;
        private String studentUuid;
        private String importedAt;
    }
}

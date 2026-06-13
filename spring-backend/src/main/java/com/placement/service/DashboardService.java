package com.placement.service;

import com.placement.dto.DashboardStatsDTO;
import com.placement.entity.platform.GitHubSnapshot;
import com.placement.entity.platform.LeetCodeSnapshot;
import com.placement.entity.student.Student;
import com.placement.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class DashboardService {

    private final StudentService studentService;
    private final StudentRepository studentRepository;
    private final JobDescriptionRepository jobDescriptionRepository;
    private final RankingResultRepository rankingResultRepository;
    private final GitHubSnapshotRepository gitHubSnapshotRepository;
    private final LeetCodeSnapshotRepository leetCodeSnapshotRepository;

    /**
     * Computes and returns aggregated dashboard statistics.
     */
    public DashboardStatsDTO getDashboardStats() {
        long studentCount = studentService.getStudentCount();
        long departmentCount = studentService.getDepartmentCount();
        double averageCgpa = studentService.getAverageCgpa();

        // Compute average GitHub repos across latest snapshots
        List<Student> allStudents = studentRepository.findAll();
        double avgGithubRepos = allStudents.stream()
                .map(s -> gitHubSnapshotRepository.findTopByStudentIdOrderBySnapshotDateDesc(s.getId()))
                .filter(java.util.Optional::isPresent)
                .map(java.util.Optional::get)
                .mapToInt(GitHubSnapshot::getPublicRepos)
                .average()
                .orElse(0.0);

        // Compute average LeetCode rating across latest snapshots
        double avgLeetcodeRating = allStudents.stream()
                .map(s -> leetCodeSnapshotRepository.findTopByStudentIdOrderBySnapshotDateDesc(s.getId()))
                .filter(java.util.Optional::isPresent)
                .map(java.util.Optional::get)
                .mapToDouble(LeetCodeSnapshot::getRating)
                .average()
                .orElse(0.0);

        // Top students by CGPA
        List<DashboardStatsDTO.TopStudentSummary> topStudents = allStudents.stream()
                .filter(s -> s.getCgpa() != null)
                .sorted((a, b) -> Double.compare(b.getCgpa(), a.getCgpa()))
                .limit(10)
                .map(s -> {
                    int githubRepos = gitHubSnapshotRepository
                            .findTopByStudentIdOrderBySnapshotDateDesc(s.getId())
                            .map(GitHubSnapshot::getPublicRepos)
                            .orElse(0);
                    int leetcodeSolved = leetCodeSnapshotRepository
                            .findTopByStudentIdOrderBySnapshotDateDesc(s.getId())
                            .map(LeetCodeSnapshot::getTotalSolved)
                            .orElse(0);

                    return DashboardStatsDTO.TopStudentSummary.builder()
                            .uuid(s.getStudentUuid())
                            .name(s.getName())
                            .department(s.getBranch())
                            .cgpa(BigDecimal.valueOf(s.getCgpa()).setScale(2, RoundingMode.HALF_UP))
                            .githubRepos(githubRepos)
                            .leetcodeSolved(leetcodeSolved)
                            .build();
                })
                .collect(Collectors.toList());

        DashboardStatsDTO stats = DashboardStatsDTO.builder()
                .studentCount(studentCount)
                .departmentCount(departmentCount)
                .avgCgpa(BigDecimal.valueOf(averageCgpa).setScale(2, RoundingMode.HALF_UP))
                .avgGithubRepos(avgGithubRepos)
                .avgLeetcodeRating(avgLeetcodeRating)
                .topStudents(topStudents)
                .build();

        log.debug("Dashboard stats: students={}, departments={}, avgCgpa={}",
                studentCount, departmentCount, averageCgpa);

        return stats;
    }
}

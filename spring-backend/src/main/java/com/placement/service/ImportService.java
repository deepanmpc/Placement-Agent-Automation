package com.placement.service;

import com.placement.dto.*;
import com.placement.entity.platform.CodeChefSnapshot;
import com.placement.entity.platform.CodeforcesSnapshot;
import com.placement.entity.platform.GitHubSnapshot;
import com.placement.entity.platform.LeetCodeSnapshot;
import com.placement.entity.ranking.RankingResult;
import com.placement.entity.student.Student;
import com.placement.entity.job.JobDescription;
import com.placement.exception.ResourceNotFoundException;
import com.placement.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ImportService {

    private final StudentRepository studentRepository;
    private final GitHubSnapshotRepository gitHubSnapshotRepository;
    private final LeetCodeSnapshotRepository leetCodeSnapshotRepository;
    private final CodeforcesSnapshotRepository codeforcesSnapshotRepository;
    private final CodeChefSnapshotRepository codeChefSnapshotRepository;
    private final RankingResultRepository rankingResultRepository;
    private final JobDescriptionRepository jobDescriptionRepository;
    private final AuditService auditService;

    // ── Student Profile Upsert ───────────────────────────────

    /**
     * Upsert a student profile.
     * Looks up by email; if exists, updates. Otherwise creates with a new UUID.
     */
    @Transactional
    public Student importStudentProfile(ImportStudentProfileDTO dto) {
        // Try to find existing student by email
        Student student = studentRepository.findByEmail(dto.getEmail())
                .orElseGet(() -> {
                    Student s = new Student();
                    s.setStudentUuid(UUID.randomUUID().toString());
                    return s;
                });

        // Map all fields from the DTO
        if (dto.getName() != null) student.setName(dto.getName());
        if (dto.getEmail() != null) student.setEmail(dto.getEmail());
        if (dto.getPhone() != null) student.setPhone(dto.getPhone());
        if (dto.getDepartment() != null) student.setBranch(dto.getDepartment());
        if (dto.getGraduationYear() != null) student.setGraduationYear(dto.getGraduationYear());
        if (dto.getCgpa() != null) student.setCgpa(dto.getCgpa().doubleValue());
        if (dto.getGithubUsername() != null) student.setGithubUsername(dto.getGithubUsername());
        if (dto.getLeetcodeUsername() != null) student.setLeetcodeUsername(dto.getLeetcodeUsername());
        if (dto.getCodeforcesUsername() != null) student.setCodeforcesUsername(dto.getCodeforcesUsername());
        if (dto.getCodechefUsername() != null) student.setCodechefUsername(dto.getCodechefUsername());
        if (dto.getResumeUrl() != null) student.setPortfolioUrl(dto.getResumeUrl());

        Student saved = studentRepository.save(student);
        auditService.log("SYSTEM", "IMPORT_STUDENT_PROFILE", "Student", saved.getId().toString());
        log.info("Imported student profile id={} uuid={}", saved.getId(), saved.getStudentUuid());
        return saved;
    }

    // ── GitHub Snapshot ──────────────────────────────────────

    /**
     * Always inserts a new GitHub snapshot (never overwrites).
     */
    @Transactional
    public GitHubSnapshot importGitHub(ImportGitHubDTO dto) {
        Student student = findStudentByUuid(dto.getStudentUuid());

        GitHubSnapshot snapshot = new GitHubSnapshot();
        snapshot.setStudent(student);
        snapshot.setSnapshotDate(dto.getSnapshotDate() != null
                ? dto.getSnapshotDate().toLocalDate() : LocalDate.now());
        if (dto.getPublicRepos() != null) snapshot.setPublicRepos(dto.getPublicRepos());
        if (dto.getTotalStars() != null) snapshot.setStars(dto.getTotalStars());
        if (dto.getFollowers() != null) snapshot.setFollowers(dto.getFollowers());
        if (dto.getFollowing() != null) snapshot.setFollowing(dto.getFollowing());
        if (dto.getTotalCommitsLastYear() != null) snapshot.setCommits365(dto.getTotalCommitsLastYear());
        if (dto.getTotalPrsLastYear() != null) snapshot.setMergedPrs(dto.getTotalPrsLastYear());
        if (dto.getTotalIssuesLastYear() != null) snapshot.setIssuesClosed(dto.getTotalIssuesLastYear());
        if (dto.getTopLanguagesJson() != null) snapshot.setLanguageDistributionJson(dto.getTopLanguagesJson());

        GitHubSnapshot saved = gitHubSnapshotRepository.save(snapshot);
        auditService.log("SYSTEM", "IMPORT_GITHUB", "GitHubSnapshot", saved.getId().toString());
        log.info("Imported GitHub snapshot id={} for student uuid={}", saved.getId(), dto.getStudentUuid());
        return saved;
    }

    // ── LeetCode Snapshot ────────────────────────────────────

    /**
     * Always inserts a new LeetCode snapshot (never overwrites).
     */
    @Transactional
    public LeetCodeSnapshot importLeetCode(ImportLeetCodeDTO dto) {
        Student student = findStudentByUuid(dto.getStudentUuid());

        LeetCodeSnapshot snapshot = new LeetCodeSnapshot();
        snapshot.setStudent(student);
        snapshot.setSnapshotDate(dto.getSnapshotDate() != null
                ? dto.getSnapshotDate().toLocalDate() : LocalDate.now());
        if (dto.getTotalSolved() != null) snapshot.setTotalSolved(dto.getTotalSolved());
        if (dto.getEasySolved() != null) snapshot.setEasySolved(dto.getEasySolved());
        if (dto.getMediumSolved() != null) snapshot.setMediumSolved(dto.getMediumSolved());
        if (dto.getHardSolved() != null) snapshot.setHardSolved(dto.getHardSolved());
        if (dto.getRanking() != null) snapshot.setRanking(dto.getRanking());
        if (dto.getContestRating() != null) snapshot.setRating(dto.getContestRating().doubleValue());
        if (dto.getContestsAttended() != null) snapshot.setContestsParticipated(dto.getContestsAttended());

        LeetCodeSnapshot saved = leetCodeSnapshotRepository.save(snapshot);
        auditService.log("SYSTEM", "IMPORT_LEETCODE", "LeetCodeSnapshot", saved.getId().toString());
        log.info("Imported LeetCode snapshot id={} for student uuid={}", saved.getId(), dto.getStudentUuid());
        return saved;
    }

    // ── Codeforces Snapshot ──────────────────────────────────

    /**
     * Always inserts a new Codeforces snapshot (never overwrites).
     */
    @Transactional
    public CodeforcesSnapshot importCodeforces(ImportCodeforcesDTO dto) {
        Student student = findStudentByUuid(dto.getStudentUuid());

        CodeforcesSnapshot snapshot = new CodeforcesSnapshot();
        snapshot.setStudent(student);
        snapshot.setSnapshotDate(dto.getSnapshotDate() != null
                ? dto.getSnapshotDate().toLocalDate() : LocalDate.now());
        if (dto.getCurrentRating() != null) snapshot.setRating(dto.getCurrentRating());
        if (dto.getMaxRating() != null) snapshot.setMaxRating(dto.getMaxRating());
        if (dto.getCurrentRank() != null) snapshot.setRank(dto.getCurrentRank());
        if (dto.getContestsParticipated() != null) snapshot.setContests(dto.getContestsParticipated());
        if (dto.getTotalProblemsSolved() != null) snapshot.setSolvedCount(dto.getTotalProblemsSolved());

        CodeforcesSnapshot saved = codeforcesSnapshotRepository.save(snapshot);
        auditService.log("SYSTEM", "IMPORT_CODEFORCES", "CodeforcesSnapshot", saved.getId().toString());
        log.info("Imported Codeforces snapshot id={} for student uuid={}", saved.getId(), dto.getStudentUuid());
        return saved;
    }

    // ── CodeChef Snapshot ────────────────────────────────────

    /**
     * Always inserts a new CodeChef snapshot (never overwrites).
     */
    @Transactional
    public CodeChefSnapshot importCodeChef(ImportCodeChefDTO dto) {
        Student student = findStudentByUuid(dto.getStudentUuid());

        CodeChefSnapshot snapshot = new CodeChefSnapshot();
        snapshot.setStudent(student);
        snapshot.setSnapshotDate(dto.getSnapshotDate() != null
                ? dto.getSnapshotDate().toLocalDate() : LocalDate.now());
        if (dto.getCurrentRating() != null) snapshot.setRating(dto.getCurrentRating());
        if (dto.getHighestRating() != null) snapshot.setHighestRating(dto.getHighestRating());
        if (dto.getCurrentStars() != null) snapshot.setStars(dto.getCurrentStars());
        if (dto.getContestsParticipated() != null) snapshot.setContests(dto.getContestsParticipated());
        if (dto.getTotalProblemsSolved() != null) snapshot.setSolvedCount(dto.getTotalProblemsSolved());

        CodeChefSnapshot saved = codeChefSnapshotRepository.save(snapshot);
        auditService.log("SYSTEM", "IMPORT_CODECHEF", "CodeChefSnapshot", saved.getId().toString());
        log.info("Imported CodeChef snapshot id={} for student uuid={}", saved.getId(), dto.getStudentUuid());
        return saved;
    }

    // ── Ranking Import ───────────────────────────────────────

    /**
     * Imports a ranking result for a student against a job description.
     */
    @Transactional
    public RankingResult importRanking(ImportRankingDTO dto) {
        Student student = findStudentByUuid(dto.getStudentUuid());

        JobDescription job = jobDescriptionRepository.findById(dto.getJobId())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "JobDescription not found with id: " + dto.getJobId()));

        RankingResult result = new RankingResult();
        result.setStudent(student);
        result.setJobDescription(job);
        if (dto.getRuleScore() != null) result.setRuleScore(dto.getRuleScore().doubleValue());
        if (dto.getSemanticScore() != null) result.setSemanticScore(dto.getSemanticScore().doubleValue());
        if (dto.getFinalScore() != null) result.setFinalScore(dto.getFinalScore().doubleValue());
        if (dto.getRankPosition() != null) result.setRankPosition(dto.getRankPosition());
        if (dto.getExplanationJson() != null) result.setExplanationJson(dto.getExplanationJson());

        RankingResult saved = rankingResultRepository.save(result);
        auditService.log("SYSTEM", "IMPORT_RANKING", "RankingResult", saved.getId().toString());
        log.info("Imported ranking id={} for student uuid={} job={}", saved.getId(), dto.getStudentUuid(), dto.getJobId());
        return saved;
    }

    // ── Private Helpers ──────────────────────────────────────

    private Student findStudentByUuid(String studentUuid) {
        return studentRepository.findByStudentUuid(studentUuid)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Student not found with uuid: " + studentUuid));
    }
}

package com.placement.controller;

import com.placement.dto.*;
import com.placement.entity.platform.CodeChefSnapshot;
import com.placement.entity.platform.CodeforcesSnapshot;
import com.placement.entity.platform.GitHubSnapshot;
import com.placement.entity.platform.LeetCodeSnapshot;
import com.placement.entity.ranking.RankingResult;
import com.placement.entity.student.Student;
import com.placement.service.ImportService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/import")
@RequiredArgsConstructor
public class ImportController {

    private final ImportService importService;

    /**
     * POST /api/import/student-profile
     * Upserts a student profile by email.
     */
    @PostMapping("/student-profile")
    public ResponseEntity<ApiResponse<Student>> importStudentProfile(
            @Valid @RequestBody ImportStudentProfileDTO dto) {
        Student student = importService.importStudentProfile(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Student profile imported successfully", student));
    }

    /**
     * POST /api/import/github
     * Creates a new GitHub snapshot for a student.
     */
    @PostMapping("/github")
    public ResponseEntity<ApiResponse<GitHubSnapshot>> importGitHub(
            @Valid @RequestBody ImportGitHubDTO dto) {
        GitHubSnapshot snapshot = importService.importGitHub(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("GitHub snapshot imported successfully", snapshot));
    }

    /**
     * POST /api/import/leetcode
     * Creates a new LeetCode snapshot for a student.
     */
    @PostMapping("/leetcode")
    public ResponseEntity<ApiResponse<LeetCodeSnapshot>> importLeetCode(
            @Valid @RequestBody ImportLeetCodeDTO dto) {
        LeetCodeSnapshot snapshot = importService.importLeetCode(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("LeetCode snapshot imported successfully", snapshot));
    }

    /**
     * POST /api/import/codeforces
     * Creates a new Codeforces snapshot for a student.
     */
    @PostMapping("/codeforces")
    public ResponseEntity<ApiResponse<CodeforcesSnapshot>> importCodeforces(
            @Valid @RequestBody ImportCodeforcesDTO dto) {
        CodeforcesSnapshot snapshot = importService.importCodeforces(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Codeforces snapshot imported successfully", snapshot));
    }

    /**
     * POST /api/import/codechef
     * Creates a new CodeChef snapshot for a student.
     */
    @PostMapping("/codechef")
    public ResponseEntity<ApiResponse<CodeChefSnapshot>> importCodeChef(
            @Valid @RequestBody ImportCodeChefDTO dto) {
        CodeChefSnapshot snapshot = importService.importCodeChef(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("CodeChef snapshot imported successfully", snapshot));
    }

    /**
     * POST /api/import/ranking
     * Imports a ranking result for a student against a job.
     */
    @PostMapping("/ranking")
    public ResponseEntity<ApiResponse<RankingResult>> importRanking(
            @Valid @RequestBody ImportRankingDTO dto) {
        RankingResult result = importService.importRanking(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Ranking imported successfully", result));
    }
}

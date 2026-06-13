package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.entity.ranking.RankingResult;
import com.placement.service.RankingService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/rankings")
@RequiredArgsConstructor
public class RankingController {

    private final RankingService rankingService;

    /**
     * GET /api/rankings?page=0&size=20
     * Returns a paginated list of all rankings.
     */
    @GetMapping
    public ResponseEntity<ApiResponse<Page<RankingResult>>> getAllRankings(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<RankingResult> rankings = rankingService.getAllRankings(page, size);
        return ResponseEntity.ok(ApiResponse.success("Rankings retrieved successfully", rankings));
    }

    /**
     * GET /api/rankings/{id}
     * Returns a single ranking by ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<RankingResult>> getRankingById(@PathVariable Long id) {
        RankingResult ranking = rankingService.getRankingById(id);
        return ResponseEntity.ok(ApiResponse.success("Ranking retrieved successfully", ranking));
    }

    /**
     * GET /api/rankings/job/{jobId}
     * Returns all rankings for a given job description.
     */
    @GetMapping("/job/{jobId}")
    public ResponseEntity<ApiResponse<List<RankingResult>>> getRankingsByJobId(
            @PathVariable Long jobId) {
        List<RankingResult> rankings = rankingService.getRankingsByJobId(jobId);
        return ResponseEntity.ok(ApiResponse.success("Rankings for job retrieved successfully", rankings));
    }

    /**
     * GET /api/rankings/student/{studentId}
     * Returns all rankings for a given student.
     */
    @GetMapping("/student/{studentId}")
    public ResponseEntity<ApiResponse<List<RankingResult>>> getRankingsByStudentId(
            @PathVariable Long studentId) {
        List<RankingResult> rankings = rankingService.getRankingsByStudentId(studentId);
        return ResponseEntity.ok(ApiResponse.success("Rankings for student retrieved successfully", rankings));
    }
}

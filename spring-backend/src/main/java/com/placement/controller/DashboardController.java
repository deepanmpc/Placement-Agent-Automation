package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.dto.DashboardStatsDTO;
import com.placement.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    /**
     * GET /api/dashboard/stats
     * Returns aggregated dashboard statistics.
     */
    @GetMapping("/stats")
    public ResponseEntity<ApiResponse<DashboardStatsDTO>> getDashboardStats() {
        DashboardStatsDTO stats = dashboardService.getDashboardStats();
        return ResponseEntity.ok(ApiResponse.success("Dashboard stats retrieved successfully", stats));
    }
}

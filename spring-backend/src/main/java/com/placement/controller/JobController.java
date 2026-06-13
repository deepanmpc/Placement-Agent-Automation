package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.dto.JobDescriptionDTO;
import com.placement.entity.job.JobDescription;
import com.placement.service.JobService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/jobs")
@RequiredArgsConstructor
public class JobController {

    private final JobService jobService;

    /**
     * POST /api/jobs
     * Creates a new job description.
     */
    @PostMapping
    public ResponseEntity<ApiResponse<JobDescription>> createJob(
            @Valid @RequestBody JobDescriptionDTO dto) {
        JobDescription job = jobService.createJob(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Job created successfully", job));
    }

    /**
     * GET /api/jobs?page=0&size=20
     * Returns a paginated list of all jobs.
     */
    @GetMapping
    public ResponseEntity<ApiResponse<Page<JobDescription>>> getAllJobs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<JobDescription> jobs = jobService.getAllJobs(page, size);
        return ResponseEntity.ok(ApiResponse.success("Jobs retrieved successfully", jobs));
    }

    /**
     * GET /api/jobs/{id}
     * Returns a single job by ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<JobDescription>> getJobById(@PathVariable Long id) {
        JobDescription job = jobService.getJobById(id);
        return ResponseEntity.ok(ApiResponse.success("Job retrieved successfully", job));
    }

    /**
     * PUT /api/jobs/{id}
     * Updates an existing job.
     */
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<JobDescription>> updateJob(
            @PathVariable Long id,
            @Valid @RequestBody JobDescriptionDTO dto) {
        JobDescription job = jobService.updateJob(id, dto);
        return ResponseEntity.ok(ApiResponse.success("Job updated successfully", job));
    }

    /**
     * DELETE /api/jobs/{id}
     * Deletes a job.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteJob(@PathVariable Long id) {
        jobService.deleteJob(id);
        return ResponseEntity.ok(ApiResponse.success("Job deleted successfully"));
    }
}

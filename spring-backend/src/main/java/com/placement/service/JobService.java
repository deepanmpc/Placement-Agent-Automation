package com.placement.service;

import com.placement.dto.JobDescriptionDTO;
import com.placement.entity.job.JobDescription;
import com.placement.exception.ResourceNotFoundException;
import com.placement.repository.JobDescriptionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class JobService {

    private final JobDescriptionRepository jobDescriptionRepository;

    /**
     * Returns a paginated list of all job descriptions.
     */
    public Page<JobDescription> getAllJobs(int page, int size) {
        return jobDescriptionRepository.findAll(PageRequest.of(page, size));
    }

    /**
     * Finds a job description by ID.
     */
    public JobDescription getJobById(Long id) {
        return jobDescriptionRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Job not found with id: " + id));
    }

    /**
     * Creates a new job description from the DTO.
     */
    @Transactional
    public JobDescription createJob(JobDescriptionDTO dto) {
        JobDescription job = new JobDescription();
        mapDtoToEntity(dto, job);
        JobDescription saved = jobDescriptionRepository.save(job);
        log.info("Created job id={} title={}", saved.getId(), saved.getTitle());
        return saved;
    }

    /**
     * Updates an existing job description.
     */
    @Transactional
    public JobDescription updateJob(Long id, JobDescriptionDTO dto) {
        JobDescription job = getJobById(id);
        mapDtoToEntity(dto, job);
        JobDescription saved = jobDescriptionRepository.save(job);
        log.info("Updated job id={}", saved.getId());
        return saved;
    }

    /**
     * Deletes a job description by ID.
     */
    @Transactional
    public void deleteJob(Long id) {
        JobDescription job = getJobById(id);
        jobDescriptionRepository.delete(job);
        log.info("Deleted job id={}", id);
    }

    // ── Private helpers ──────────────────────────────────────

    private void mapDtoToEntity(JobDescriptionDTO dto, JobDescription job) {
        if (dto.getTitle() != null) job.setTitle(dto.getTitle());
        if (dto.getCompany() != null) job.setCompany(dto.getCompany());
        if (dto.getDescription() != null) job.setDescription(dto.getDescription());
        if (dto.getRequiredSkillsJson() != null) job.setRequiredSkillsJson(dto.getRequiredSkillsJson());
        if (dto.getEligibilityJson() != null) job.setEligibilityJson(dto.getEligibilityJson());
    }
}

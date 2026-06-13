package com.placement.service;

import com.placement.entity.ranking.RankingResult;
import com.placement.exception.ResourceNotFoundException;
import com.placement.repository.RankingResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class RankingService {

    private final RankingResultRepository rankingResultRepository;

    /**
     * Returns a paginated list of all ranking results.
     */
    public Page<RankingResult> getAllRankings(int page, int size) {
        return rankingResultRepository.findAll(PageRequest.of(page, size));
    }

    /**
     * Finds a ranking result by ID.
     */
    public RankingResult getRankingById(Long id) {
        return rankingResultRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Ranking not found with id: " + id));
    }

    /**
     * Returns all ranking results for a given job description.
     */
    public List<RankingResult> getRankingsByJobId(Long jobId) {
        return rankingResultRepository.findByJobDescriptionId(jobId);
    }

    /**
     * Returns all ranking results for a given student.
     */
    public List<RankingResult> getRankingsByStudentId(Long studentId) {
        return rankingResultRepository.findByStudentId(studentId);
    }
}

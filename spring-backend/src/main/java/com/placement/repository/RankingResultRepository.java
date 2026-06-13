package com.placement.repository;

import com.placement.entity.ranking.RankingResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RankingResultRepository extends JpaRepository<RankingResult, Long> {

    List<RankingResult> findByJobDescriptionId(Long jobId);

    List<RankingResult> findByStudentId(Long studentId);

    List<RankingResult> findTop10ByOrderByFinalScoreDesc();
}

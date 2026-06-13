package com.placement.entity.ranking;

import com.placement.entity.job.JobDescription;
import com.placement.entity.student.Student;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "ranking_results", indexes = {
        @Index(name = "idx_ranking_student_id", columnList = "student_id"),
        @Index(name = "idx_ranking_job_id", columnList = "job_description_id"),
        @Index(name = "idx_ranking_final_score", columnList = "final_score")
})
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RankingResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_description_id")
    private JobDescription jobDescription;

    @Column(name = "rule_score")
    private double ruleScore;

    @Column(name = "semantic_score")
    private double semanticScore;

    @Column(name = "final_score")
    private double finalScore;

    @Column(name = "rank_position")
    private int rankPosition;

    @Column(name = "explanation_json", columnDefinition = "TEXT")
    private String explanationJson;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

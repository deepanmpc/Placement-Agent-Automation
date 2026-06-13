package com.placement.entity.platform;

import com.placement.entity.student.Student;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "leetcode_snapshots", indexes = {
        @Index(name = "idx_leetcode_student_id", columnList = "student_id"),
        @Index(name = "idx_leetcode_snapshot_date", columnList = "snapshot_date")
},
        uniqueConstraints = @UniqueConstraint(
                name = "uk_leetcode_student_date",
                columnNames = {"student_id", "snapshot_date"}
        ))
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LeetCodeSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @Column(name = "snapshot_date", nullable = false)
    private LocalDate snapshotDate;

    private double rating;

    private int ranking;

    @Column(name = "easy_solved")
    private int easySolved;

    @Column(name = "medium_solved")
    private int mediumSolved;

    @Column(name = "hard_solved")
    private int hardSolved;

    @Column(name = "total_solved")
    private int totalSolved;

    @Column(name = "contests_participated")
    private int contestsParticipated;

    @Column(name = "active_days")
    private int activeDays;

    private int submissions;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

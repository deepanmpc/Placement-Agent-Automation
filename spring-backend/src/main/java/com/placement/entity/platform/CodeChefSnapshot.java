package com.placement.entity.platform;

import com.placement.entity.student.Student;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "codechef_snapshots", indexes = {
        @Index(name = "idx_codechef_student_id", columnList = "student_id"),
        @Index(name = "idx_codechef_snapshot_date", columnList = "snapshot_date")
},
        uniqueConstraints = @UniqueConstraint(
                name = "uk_codechef_student_date",
                columnNames = {"student_id", "snapshot_date"}
        ))
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CodeChefSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @Column(name = "snapshot_date", nullable = false)
    private LocalDate snapshotDate;

    private int rating;

    @Column(length = 10)
    private String stars;

    @Column(name = "highest_rating")
    private int highestRating;

    private int contests;

    @Column(name = "solved_count")
    private int solvedCount;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

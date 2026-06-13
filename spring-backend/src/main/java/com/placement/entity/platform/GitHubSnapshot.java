package com.placement.entity.platform;

import com.placement.entity.student.Student;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "github_snapshots", indexes = {
        @Index(name = "idx_github_student_id", columnList = "student_id"),
        @Index(name = "idx_github_snapshot_date", columnList = "snapshot_date")
},
        uniqueConstraints = @UniqueConstraint(
                name = "uk_github_student_date",
                columnNames = {"student_id", "snapshot_date"}
        ))
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GitHubSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @Column(name = "snapshot_date", nullable = false)
    private LocalDate snapshotDate;

    @Column(name = "public_repos")
    private int publicRepos;

    private int stars;

    private int followers;

    private int following;

    @Column(name = "commits_365")
    private int commits365;

    @Column(name = "contribution_days_365")
    private int contributionDays365;

    @Column(name = "active_days_90")
    private int activeDays90;

    @Column(name = "merged_prs")
    private int mergedPrs;

    @Column(name = "issues_closed")
    private int issuesClosed;

    @Column(name = "language_distribution_json", columnDefinition = "TEXT")
    private String languageDistributionJson;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

package com.placement.entity.job;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "job_descriptions")
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class JobDescription {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 300)
    private String title;

    @Column(length = 300)
    private String company;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "required_skills_json", columnDefinition = "TEXT")
    private String requiredSkillsJson;

    @Column(name = "eligibility_json", columnDefinition = "TEXT")
    private String eligibilityJson;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

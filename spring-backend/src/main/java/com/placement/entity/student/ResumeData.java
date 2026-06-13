package com.placement.entity.student;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "resume_data", indexes = {
        @Index(name = "idx_resume_student_id", columnList = "student_id")
})
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResumeData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "student_id", nullable = false)
    private Student student;

    @Column(name = "skills_json", columnDefinition = "TEXT")
    private String skillsJson;

    @Column(name = "projects_json", columnDefinition = "TEXT")
    private String projectsJson;

    @Column(name = "certifications_json", columnDefinition = "TEXT")
    private String certificationsJson;

    @Column(name = "achievements_json", columnDefinition = "TEXT")
    private String achievementsJson;

    @Column(name = "experience_json", columnDefinition = "TEXT")
    private String experienceJson;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
}

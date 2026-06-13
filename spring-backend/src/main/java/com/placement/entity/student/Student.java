package com.placement.entity.student;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "students", indexes = {
        @Index(name = "idx_student_uuid", columnList = "studentUuid"),
        @Index(name = "idx_student_email", columnList = "email"),
        @Index(name = "idx_student_graduation_year", columnList = "graduationYear")
})
@EntityListeners(AuditingEntityListener.class)
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "student_uuid", unique = true, nullable = false, length = 36)
    private String studentUuid;

    @Column(name = "roll_number", length = 50)
    private String rollNumber;

    @Column(length = 200)
    private String name;

    @Column(unique = true, length = 200)
    private String email;

    @Column(length = 20)
    private String phone;

    @Column(length = 50)
    private String degree;

    @Column(length = 100)
    private String branch;

    private Double cgpa;

    @Column(name = "graduation_year")
    private Integer graduationYear;

    @Column(name = "github_username", length = 100)
    private String githubUsername;

    @Column(name = "leetcode_username", length = 100)
    private String leetcodeUsername;

    @Column(name = "codeforces_username", length = 100)
    private String codeforcesUsername;

    @Column(name = "codechef_username", length = 100)
    private String codechefUsername;

    @Column(name = "linkedin_url", length = 500)
    private String linkedinUrl;

    @Column(name = "portfolio_url", length = 500)
    private String portfolioUrl;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}

package com.placement.repository;

import com.placement.entity.student.ResumeData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ResumeDataRepository extends JpaRepository<ResumeData, Long> {

    Optional<ResumeData> findByStudentId(Long studentId);
}

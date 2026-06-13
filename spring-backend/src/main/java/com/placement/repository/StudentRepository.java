package com.placement.repository;

import com.placement.entity.student.Student;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {

    Optional<Student> findByStudentUuid(String uuid);

    Optional<Student> findByEmail(String email);

    List<Student> findByGraduationYear(Integer year);

    long countByBranch(String branch);
}

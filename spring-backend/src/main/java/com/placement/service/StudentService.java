package com.placement.service;

import com.placement.dto.StudentDTO;
import com.placement.entity.student.Student;
import com.placement.exception.ResourceNotFoundException;
import com.placement.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class StudentService {

    private final StudentRepository studentRepository;

    /**
     * Returns a paginated list of all students.
     */
    public Page<Student> getAllStudents(int page, int size) {
        return studentRepository.findAll(PageRequest.of(page, size));
    }

    /**
     * Finds a student by database ID.
     */
    public Student getStudentById(Long id) {
        return studentRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Student not found with id: " + id));
    }

    /**
     * Finds a student by their external UUID.
     */
    public Student getStudentByUuid(String uuid) {
        return studentRepository.findByStudentUuid(uuid)
                .orElseThrow(() -> new ResourceNotFoundException("Student not found with uuid: " + uuid));
    }

    /**
     * Creates a new student from the DTO.
     */
    @Transactional
    public Student createStudent(StudentDTO dto) {
        Student student = new Student();
        // Generate UUID if not provided
        student.setStudentUuid(dto.getUuid() != null ? dto.getUuid() : UUID.randomUUID().toString());
        mapDtoToEntity(dto, student);
        Student saved = studentRepository.save(student);
        log.info("Created student id={} uuid={}", saved.getId(), saved.getStudentUuid());
        return saved;
    }

    /**
     * Updates an existing student.
     */
    @Transactional
    public Student updateStudent(Long id, StudentDTO dto) {
        Student student = getStudentById(id);
        mapDtoToEntity(dto, student);
        Student saved = studentRepository.save(student);
        log.info("Updated student id={}", saved.getId());
        return saved;
    }

    /**
     * Deletes a student by ID.
     */
    @Transactional
    public void deleteStudent(Long id) {
        Student student = getStudentById(id);
        studentRepository.delete(student);
        log.info("Deleted student id={}", id);
    }

    /**
     * Total count of students.
     */
    public long getStudentCount() {
        return studentRepository.count();
    }

    /**
     * Count of distinct departments (branches).
     */
    public long getDepartmentCount() {
        return studentRepository.findAll().stream()
                .map(Student::getBranch)
                .filter(b -> b != null && !b.isBlank())
                .distinct()
                .count();
    }

    /**
     * Average CGPA across all students.
     */
    public double getAverageCgpa() {
        return studentRepository.findAll().stream()
                .filter(s -> s.getCgpa() != null)
                .mapToDouble(Student::getCgpa)
                .average()
                .orElse(0.0);
    }

    // ── Private helpers ──────────────────────────────────────

    private void mapDtoToEntity(StudentDTO dto, Student student) {
        if (dto.getName() != null) student.setName(dto.getName());
        if (dto.getEmail() != null) student.setEmail(dto.getEmail());
        if (dto.getPhone() != null) student.setPhone(dto.getPhone());
        if (dto.getDepartment() != null) student.setBranch(dto.getDepartment());
        if (dto.getGraduationYear() != null) student.setGraduationYear(dto.getGraduationYear());
        if (dto.getCgpa() != null) student.setCgpa(dto.getCgpa().doubleValue());
        if (dto.getGithubUsername() != null) student.setGithubUsername(dto.getGithubUsername());
        if (dto.getLeetcodeUsername() != null) student.setLeetcodeUsername(dto.getLeetcodeUsername());
        if (dto.getCodeforcesUsername() != null) student.setCodeforcesUsername(dto.getCodeforcesUsername());
        if (dto.getCodechefUsername() != null) student.setCodechefUsername(dto.getCodechefUsername());
        if (dto.getResumeUrl() != null) student.setLinkedinUrl(dto.getResumeUrl());
    }
}

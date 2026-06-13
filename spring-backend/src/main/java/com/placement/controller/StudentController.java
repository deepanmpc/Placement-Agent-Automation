package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.dto.StudentDTO;
import com.placement.entity.student.Student;
import com.placement.service.StudentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/students")
@RequiredArgsConstructor
public class StudentController {

    private final StudentService studentService;

    /**
     * GET /api/students?page=0&size=20
     * Returns a paginated list of all students.
     */
    @GetMapping
    public ResponseEntity<ApiResponse<Page<Student>>> getAllStudents(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<Student> students = studentService.getAllStudents(page, size);
        return ResponseEntity.ok(ApiResponse.success("Students retrieved successfully", students));
    }

    /**
     * GET /api/students/{id}
     * Returns a single student by ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Student>> getStudentById(@PathVariable Long id) {
        Student student = studentService.getStudentById(id);
        return ResponseEntity.ok(ApiResponse.success("Student retrieved successfully", student));
    }

    /**
     * POST /api/students
     * Creates a new student.
     */
    @PostMapping
    public ResponseEntity<ApiResponse<Student>> createStudent(@Valid @RequestBody StudentDTO dto) {
        Student student = studentService.createStudent(dto);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Student created successfully", student));
    }

    /**
     * PUT /api/students/{id}
     * Updates an existing student.
     */
    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<Student>> updateStudent(
            @PathVariable Long id,
            @Valid @RequestBody StudentDTO dto) {
        Student student = studentService.updateStudent(id, dto);
        return ResponseEntity.ok(ApiResponse.success("Student updated successfully", student));
    }

    /**
     * DELETE /api/students/{id}
     * Deletes a student.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteStudent(@PathVariable Long id) {
        studentService.deleteStudent(id);
        return ResponseEntity.ok(ApiResponse.success("Student deleted successfully"));
    }
}

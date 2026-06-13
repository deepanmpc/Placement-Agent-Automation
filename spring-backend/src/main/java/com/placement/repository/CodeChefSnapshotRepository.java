package com.placement.repository;

import com.placement.entity.platform.CodeChefSnapshot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CodeChefSnapshotRepository extends JpaRepository<CodeChefSnapshot, Long> {

    List<CodeChefSnapshot> findByStudentIdOrderBySnapshotDateDesc(Long studentId);

    Optional<CodeChefSnapshot> findTopByStudentIdOrderBySnapshotDateDesc(Long studentId);
}

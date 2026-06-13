package com.placement.repository;

import com.placement.entity.platform.LeetCodeSnapshot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface LeetCodeSnapshotRepository extends JpaRepository<LeetCodeSnapshot, Long> {

    List<LeetCodeSnapshot> findByStudentIdOrderBySnapshotDateDesc(Long studentId);

    Optional<LeetCodeSnapshot> findTopByStudentIdOrderBySnapshotDateDesc(Long studentId);
}

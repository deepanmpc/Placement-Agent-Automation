package com.placement.repository;

import com.placement.entity.platform.CodeforcesSnapshot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CodeforcesSnapshotRepository extends JpaRepository<CodeforcesSnapshot, Long> {

    List<CodeforcesSnapshot> findByStudentIdOrderBySnapshotDateDesc(Long studentId);

    Optional<CodeforcesSnapshot> findTopByStudentIdOrderBySnapshotDateDesc(Long studentId);
}

package com.placement.repository;

import com.placement.entity.platform.GitHubSnapshot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GitHubSnapshotRepository extends JpaRepository<GitHubSnapshot, Long> {

    List<GitHubSnapshot> findByStudentIdOrderBySnapshotDateDesc(Long studentId);

    Optional<GitHubSnapshot> findTopByStudentIdOrderBySnapshotDateDesc(Long studentId);
}

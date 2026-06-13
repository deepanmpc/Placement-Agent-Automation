package com.placement.repository;

import com.placement.entity.job.JobDescription;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface JobDescriptionRepository extends JpaRepository<JobDescription, Long> {

    List<JobDescription> findTop10ByOrderByCreatedAtDesc();
}

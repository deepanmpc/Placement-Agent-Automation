package com.placement.repository;

import com.placement.entity.audit.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {

    List<AuditLog> findTop50ByOrderByTimestampDesc();

    @Transactional
    void deleteByTimestampBefore(LocalDateTime cutoff);
}

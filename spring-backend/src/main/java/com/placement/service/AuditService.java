package com.placement.service;

import com.placement.entity.audit.AuditLog;
import com.placement.repository.AuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    /**
     * Logs an admin action to the audit trail.
     */
    @Transactional
    public void log(String adminId, String action, String entityType, String entityId) {
        AuditLog auditLog = new AuditLog();
        auditLog.setAdminId(adminId);
        auditLog.setAction(action);
        auditLog.setEntityType(entityType);
        auditLog.setEntityId(entityId);
        auditLog.setTimestamp(LocalDateTime.now());

        auditLogRepository.save(auditLog);
        log.info("Audit: admin={} action={} entity={}:{}", adminId, action, entityType, entityId);
    }

    /**
     * Returns the most recent audit logs (up to 50).
     */
    public List<AuditLog> getRecentAuditLogs(int limit) {
        // Repository method returns top 50 by default
        return auditLogRepository.findTop50ByOrderByTimestampDesc();
    }
}

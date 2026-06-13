package com.placement.scheduler;

import com.placement.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Daily cleanup scheduler that removes old snapshots and audit logs
 * beyond their configured retention periods.
 *
 * Retention periods are read from application.properties:
 *   scheduler.snapshot-retention-days (default: 365)
 *   scheduler.audit-retention-days (default: 180)
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class CleanupScheduler {

    private final GitHubSnapshotRepository gitHubSnapshotRepository;
    private final LeetCodeSnapshotRepository leetCodeSnapshotRepository;
    private final CodeforcesSnapshotRepository codeforcesSnapshotRepository;
    private final CodeChefSnapshotRepository codeChefSnapshotRepository;
    private final AuditLogRepository auditLogRepository;

    @Value("${scheduler.snapshot-retention-days:365}")
    private int snapshotRetentionDays;

    @Value("${scheduler.audit-retention-days:180}")
    private int auditRetentionDays;

    /**
     * Runs daily at 2:00 AM to clean up old snapshots and audit logs.
     */
    @Scheduled(cron = "0 0 2 * * *")
    @Transactional
    public void cleanupOldData() {
        log.info("Starting daily cleanup task...");

        cleanupSnapshots();
        cleanupAuditLogs();

        log.info("Daily cleanup task completed.");
    }

    /**
     * Removes platform snapshots older than the configured retention period.
     * The snapshot entities use LocalDate for snapshotDate.
     */
    private void cleanupSnapshots() {
        LocalDate snapshotCutoff = LocalDate.now().minusDays(snapshotRetentionDays);
        log.info("Cleaning up snapshots with snapshotDate before {} (retention={} days)",
                snapshotCutoff, snapshotRetentionDays);

        try {
            long ghCount = gitHubSnapshotRepository.findAll().stream()
                    .filter(s -> s.getSnapshotDate().isBefore(snapshotCutoff))
                    .peek(s -> gitHubSnapshotRepository.delete(s))
                    .count();
            log.info("Cleaned up {} old GitHub snapshots", ghCount);
        } catch (Exception e) {
            log.error("Error cleaning up GitHub snapshots: {}", e.getMessage(), e);
        }

        try {
            long lcCount = leetCodeSnapshotRepository.findAll().stream()
                    .filter(s -> s.getSnapshotDate().isBefore(snapshotCutoff))
                    .peek(s -> leetCodeSnapshotRepository.delete(s))
                    .count();
            log.info("Cleaned up {} old LeetCode snapshots", lcCount);
        } catch (Exception e) {
            log.error("Error cleaning up LeetCode snapshots: {}", e.getMessage(), e);
        }

        try {
            long cfCount = codeforcesSnapshotRepository.findAll().stream()
                    .filter(s -> s.getSnapshotDate().isBefore(snapshotCutoff))
                    .peek(s -> codeforcesSnapshotRepository.delete(s))
                    .count();
            log.info("Cleaned up {} old Codeforces snapshots", cfCount);
        } catch (Exception e) {
            log.error("Error cleaning up Codeforces snapshots: {}", e.getMessage(), e);
        }

        try {
            long ccCount = codeChefSnapshotRepository.findAll().stream()
                    .filter(s -> s.getSnapshotDate().isBefore(snapshotCutoff))
                    .peek(s -> codeChefSnapshotRepository.delete(s))
                    .count();
            log.info("Cleaned up {} old CodeChef snapshots", ccCount);
        } catch (Exception e) {
            log.error("Error cleaning up CodeChef snapshots: {}", e.getMessage(), e);
        }
    }

    /**
     * Removes audit logs older than the configured retention period.
     */
    private void cleanupAuditLogs() {
        LocalDateTime auditCutoff = LocalDateTime.now().minusDays(auditRetentionDays);
        log.info("Cleaning up audit logs with timestamp before {} (retention={} days)",
                auditCutoff, auditRetentionDays);

        try {
            auditLogRepository.deleteByTimestampBefore(auditCutoff);
            log.info("Cleaned up old audit logs");
        } catch (Exception e) {
            log.error("Error cleaning up audit logs: {}", e.getMessage(), e);
        }
    }
}

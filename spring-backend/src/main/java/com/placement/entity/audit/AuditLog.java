package com.placement.entity.audit;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "audit_logs", indexes = {
        @Index(name = "idx_audit_timestamp", columnList = "timestamp"),
        @Index(name = "idx_audit_admin_id", columnList = "admin_id")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "admin_id", length = 100)
    private String adminId;

    @Column(length = 100)
    private String action;

    @Column(name = "entity_type", length = 100)
    private String entityType;

    @Column(name = "entity_id", length = 100)
    private String entityId;

    @Column(nullable = false)
    private LocalDateTime timestamp;
}

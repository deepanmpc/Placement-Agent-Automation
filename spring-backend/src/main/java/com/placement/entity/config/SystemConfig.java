package com.placement.entity.config;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "system_config")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SystemConfig {

    @Id
    private String configKey;

    private String configValue;

}

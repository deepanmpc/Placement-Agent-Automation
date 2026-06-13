package com.placement.service;

import com.placement.entity.config.SystemConfig;
import com.placement.repository.SystemConfigRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class SystemConfigService {

    private final SystemConfigRepository repository;

    public Map<String, String> getAllConfigs() {
        List<SystemConfig> configs = repository.findAll();
        Map<String, String> configMap = new HashMap<>();
        for (SystemConfig config : configs) {
            configMap.put(config.getConfigKey(), config.getConfigValue());
        }
        return configMap;
    }

    public void saveConfigs(Map<String, String> configs) {
        for (Map.Entry<String, String> entry : configs.entrySet()) {
            SystemConfig config = SystemConfig.builder()
                    .configKey(entry.getKey())
                    .configValue(entry.getValue())
                    .build();
            repository.save(config);
        }
    }
}

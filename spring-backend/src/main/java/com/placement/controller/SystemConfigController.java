package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.service.SystemConfigService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/config")
@RequiredArgsConstructor
public class SystemConfigController {

    private final SystemConfigService configService;

    @GetMapping
    public ResponseEntity<ApiResponse<Map<String, String>>> getAllConfigs() {
        return ResponseEntity.ok(ApiResponse.success("Configs retrieved", configService.getAllConfigs()));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<String>> saveConfigs(@RequestBody Map<String, String> configs) {
        configService.saveConfigs(configs);
        return ResponseEntity.ok(ApiResponse.success("Configs saved successfully", null));
    }
}

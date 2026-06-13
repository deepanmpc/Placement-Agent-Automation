package com.placement.controller;

import com.placement.dto.ApiResponse;
import com.placement.dto.AuthRequest;
import com.placement.dto.AuthResponse;
import com.placement.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    /**
     * POST /api/auth/login
     * Authenticates an admin user and returns a JWT token.
     */
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody AuthRequest request) {
        AuthResponse response = authService.authenticate(request);
        return ResponseEntity.ok(ApiResponse.success("Login successful", response));
    }
}

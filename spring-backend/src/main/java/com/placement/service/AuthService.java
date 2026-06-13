package com.placement.service;

import com.placement.config.JwtTokenProvider;
import com.placement.dto.AuthRequest;
import com.placement.dto.AuthResponse;
import com.placement.entity.audit.AdminUser;
import com.placement.repository.AdminUserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final AdminUserRepository adminUserRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    /**
     * Authenticates an admin user and returns a JWT token.
     *
     * @param request contains username and password
     * @return AuthResponse with JWT token and user details
     * @throws RuntimeException if credentials are invalid
     */
    public AuthResponse authenticate(AuthRequest request) {
        AdminUser admin = adminUserRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> {
                    log.warn("Authentication failed: user '{}' not found", request.getUsername());
                    return new RuntimeException("Invalid username or password");
                });

        if (!passwordEncoder.matches(request.getPassword(), admin.getPassword())) {
            log.warn("Authentication failed: invalid password for user '{}'", request.getUsername());
            throw new RuntimeException("Invalid username or password");
        }

        String token = jwtTokenProvider.generateToken(admin.getUsername());

        log.info("Admin '{}' authenticated successfully", admin.getUsername());

        return AuthResponse.builder()
                .token(token)
                .username(admin.getUsername())
                .role(admin.getRole())
                .build();
    }
}

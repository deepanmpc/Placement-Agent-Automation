package com.placement.config;

import com.placement.entity.audit.AdminUser;
import com.placement.repository.AdminUserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class AdminSeeder implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(AdminSeeder.class);

    private final AdminUserRepository adminUserRepository;
    private final PasswordEncoder passwordEncoder;

    @Value("${admin.default.username}")
    private String defaultUsername;

    @Value("${admin.default.password}")
    private String defaultPassword;

    public AdminSeeder(AdminUserRepository adminUserRepository,
                       PasswordEncoder passwordEncoder) {
        this.adminUserRepository = adminUserRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        if (adminUserRepository.findByUsername(defaultUsername).isEmpty()) {
            AdminUser admin = new AdminUser();
            admin.setUsername(defaultUsername);
            admin.setPassword(passwordEncoder.encode(defaultPassword));
            admin.setRole("ADMIN");

            adminUserRepository.save(admin);
            logger.info("✅ Default admin user '{}' created successfully.", defaultUsername);
        } else {
            logger.info("ℹ️ Admin user '{}' already exists. Skipping seed.", defaultUsername);
        }
    }
}

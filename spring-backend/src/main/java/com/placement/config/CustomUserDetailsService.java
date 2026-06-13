package com.placement.config;

import com.placement.entity.audit.AdminUser;
import com.placement.repository.AdminUserRepository;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.ArrayList;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final AdminUserRepository adminRepository;

    public CustomUserDetailsService(AdminUserRepository adminRepository) {
        this.adminRepository = adminRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        AdminUser admin = adminRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("Admin not found: " + username));
        
        return new User(admin.getUsername(), admin.getPassword(), new ArrayList<>());
    }
}

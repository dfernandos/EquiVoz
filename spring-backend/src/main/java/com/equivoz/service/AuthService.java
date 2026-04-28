package com.equivoz.service;

import com.equivoz.dto.LoginRequest;
import com.equivoz.dto.RegisterRequest;
import com.equivoz.dto.TokenResponse;
import com.equivoz.dto.UserResponse;
import com.equivoz.model.User;
import com.equivoz.repository.UserRepository;
import com.equivoz.security.JwtService;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Transactional
    public UserResponse register(RegisterRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        if (userRepository.existsByEmail(email)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "E-mail já cadastrado");
        }
        User user = new User();
        user.setEmail(email);
        user.setHashedPassword(passwordEncoder.encode(request.getPassword()));
        user.setName(request.getName().trim());
        user = userRepository.save(user);
        return UserResponse.from(user);
    }

    public TokenResponse login(LoginRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        User user =
                userRepository.findByEmail(email).orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.UNAUTHORIZED, "E-mail ou senha incorretos"));
        if (!passwordEncoder.matches(request.getPassword(), user.getHashedPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "E-mail ou senha incorretos");
        }
        return TokenResponse.of(jwtService.generateToken(user.getEmail()));
    }
}

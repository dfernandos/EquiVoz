package com.equivoz.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.equivoz.dto.LoginRequest;
import com.equivoz.dto.RegisterRequest;
import com.equivoz.dto.TokenResponse;
import com.equivoz.dto.UserResponse;
import com.equivoz.model.User;
import com.equivoz.repository.UserRepository;
import com.equivoz.security.JwtService;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.server.ResponseStatusException;

/** Testes unitários de {@link AuthService} com repositório e encoder mockados. */
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtService jwtService;

    @InjectMocks
    private AuthService authService;

    @Test
    void register_persistsNewUser() {
        when(userRepository.existsByEmail("novo@test.com")).thenReturn(false);
        when(passwordEncoder.encode("secret12")).thenReturn("HASH");
        when(userRepository.save(any(User.class)))
                .thenAnswer(
                        inv -> {
                            User u = inv.getArgument(0);
                            u.setId(1L);
                            return u;
                        });

        RegisterRequest req = new RegisterRequest();
        req.setEmail("novo@test.com");
        req.setPassword("secret12");
        req.setName("Novo");

        UserResponse out = authService.register(req);
        assertThat(out.email()).isEqualTo("novo@test.com");
        assertThat(out.name()).isEqualTo("Novo");
        assertThat(out.id()).isEqualTo(1L);
        verify(passwordEncoder).encode("secret12");
    }

    @Test
    void register_duplicateEmail_throws400() {
        when(userRepository.existsByEmail("dup@test.com")).thenReturn(true);
        RegisterRequest req = new RegisterRequest();
        req.setEmail("dup@test.com");
        req.setPassword("secret12");
        req.setName("X");

        assertThatThrownBy(() -> authService.register(req))
                .isInstanceOf(ResponseStatusException.class)
                .satisfies(
                        ex -> assertThat(((ResponseStatusException) ex).getStatusCode().value())
                                .isEqualTo(HttpStatus.BAD_REQUEST.value()));
    }

    @Test
    void login_returnsTokenWhenCredentialsMatch() {
        User user = new User();
        user.setId(2L);
        user.setEmail("u@test.com");
        user.setHashedPassword("HASH");
        when(userRepository.findByEmail("u@test.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("ok", "HASH")).thenReturn(true);
        when(jwtService.generateToken("u@test.com")).thenReturn("jwt-token");

        LoginRequest req = new LoginRequest();
        req.setEmail("u@test.com");
        req.setPassword("ok");

        TokenResponse token = authService.login(req);
        assertThat(token.accessToken()).isEqualTo("jwt-token");
        assertThat(token.tokenType()).isEqualTo("bearer");
        verify(jwtService).generateToken(eq("u@test.com"));
    }

    @Test
    void login_wrongPassword_throws401() {
        User user = new User();
        user.setEmail("u@test.com");
        user.setHashedPassword("HASH");
        when(userRepository.findByEmail("u@test.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("bad", "HASH")).thenReturn(false);

        LoginRequest req = new LoginRequest();
        req.setEmail("u@test.com");
        req.setPassword("bad");

        assertThatThrownBy(() -> authService.login(req))
                .isInstanceOf(ResponseStatusException.class)
                .satisfies(
                        ex -> assertThat(((ResponseStatusException) ex).getStatusCode().value())
                                .isEqualTo(HttpStatus.UNAUTHORIZED.value()));
    }
}

package com.equivoz.security;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

/** Teste unitário puro: {@link JwtService} sem contexto Spring. */
class JwtServiceTest {

    private final JwtService jwtService =
            new JwtService("test-secret-key-at-least-32-bytes-long!!", 60L);

    @Test
    void generateAndExtractEmail_roundTrip() {
        String token = jwtService.generateToken("user@example.com");
        assertThat(token).isNotBlank();
        assertThat(jwtService.isValid(token)).isTrue();
        assertThat(jwtService.extractEmail(token)).isEqualTo("user@example.com");
    }

    @Test
    void invalidToken_isNotValid() {
        assertThat(jwtService.isValid("not-a-jwt")).isFalse();
    }
}

package com.equivoz.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record TokenResponse(
        @JsonProperty("access_token") String accessToken,
        @JsonProperty("token_type") String tokenType) {

    public static TokenResponse of(String accessToken) {
        return new TokenResponse(accessToken, "bearer");
    }
}

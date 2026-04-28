package com.equivoz.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.equivoz.model.User;
import java.time.Instant;

public record UserResponse(
        Long id, String email, String name, @JsonProperty("created_at") Instant createdAt) {

    public static UserResponse from(User user) {
        return new UserResponse(user.getId(), user.getEmail(), user.getName(), user.getCreatedAt());
    }
}

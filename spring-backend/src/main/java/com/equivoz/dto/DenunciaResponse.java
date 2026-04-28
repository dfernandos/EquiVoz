package com.equivoz.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.equivoz.model.Denuncia;
import java.time.Instant;

public record DenunciaResponse(
        Long id,
        @JsonProperty("user_id") Long userId,
        String title,
        String description,
        @JsonProperty("violation_type") String violationType,
        @JsonProperty("occurred_at") Instant occurredAt,
        @JsonProperty("location_text") String locationText,
        Double latitude,
        Double longitude,
        @JsonProperty("created_at") Instant createdAt) {

    public static DenunciaResponse from(Denuncia d) {
        return new DenunciaResponse(
                d.getId(),
                d.getUser() != null ? d.getUser().getId() : null,
                d.getTitle(),
                d.getDescription(),
                d.getViolationType(),
                d.getOccurredAt(),
                d.getLocationText(),
                d.getLatitude(),
                d.getLongitude(),
                d.getCreatedAt());
    }
}

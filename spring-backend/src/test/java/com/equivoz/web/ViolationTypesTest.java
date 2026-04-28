package com.equivoz.web;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

/** Teste unitário puro: mapa de tipos sem Spring. */
class ViolationTypesTest {

    @Test
    void asList_containsExpectedIds() {
        var list = ViolationTypes.asList();
        assertThat(list).hasSize(8);
        assertThat(list.stream().map(v -> v.id()).toList()).contains("racismo", "outro");
    }
}

package com.equivoz.web;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.equivoz.dto.LoginRequest;
import com.equivoz.dto.RegisterRequest;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

/** Testes de integração HTTP (MockMvc + contexto Spring + H2). */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class ApiIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void health_ok() throws Exception {
        mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"))
                .andExpect(jsonPath("$.service").value("equivoz"));
    }

    @Test
    void register_login_createDenuncia_flow() throws Exception {
        RegisterRequest reg = new RegisterRequest();
        reg.setEmail("flow@test.com");
        reg.setPassword("secret12");
        reg.setName("Flow");

        mockMvc.perform(
                        post("/api/auth/register")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value("flow@test.com"));

        LoginRequest login = new LoginRequest();
        login.setEmail("flow@test.com");
        login.setPassword("secret12");

        var loginRes = mockMvc.perform(
                        post("/api/auth/login")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(login)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.access_token").exists())
                .andReturn();

        String token =
                objectMapper.readTree(loginRes.getResponse().getContentAsString()).get("access_token").asText();

        mockMvc.perform(
                        post("/api/denuncias")
                                .header("Authorization", "Bearer " + token)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(
                                        objectMapper.writeValueAsString(
                                                Map.of(
                                                        "title",
                                                        "Título de teste",
                                                        "description",
                                                        "Descrição com mais de dez caracteres.",
                                                        "violation_type",
                                                        "racismo"))))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.violation_type").value("racismo"));

        mockMvc.perform(get("/api/denuncias/minhas").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Título de teste"));
    }

    @Test
    void denuncias_withoutToken_returns401() throws Exception {
        mockMvc.perform(
                        post("/api/denuncias")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(
                                        objectMapper.writeValueAsString(
                                                Map.of(
                                                        "title",
                                                        "abc",
                                                        "description",
                                                        "1234567890ab",
                                                        "violation_type",
                                                        "outro"))))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Não autenticado"));
    }
}

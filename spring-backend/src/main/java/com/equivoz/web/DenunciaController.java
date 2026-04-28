package com.equivoz.web;

import com.equivoz.dto.DenunciaCreateRequest;
import com.equivoz.dto.DenunciaResponse;
import com.equivoz.dto.ViolationTypeDto;
import com.equivoz.model.User;
import com.equivoz.service.DenunciaService;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/denuncias")
public class DenunciaController {

    private final DenunciaService denunciaService;

    public DenunciaController(DenunciaService denunciaService) {
        this.denunciaService = denunciaService;
    }

    @GetMapping("/tipos-violacao")
    public List<ViolationTypeDto> tiposViolacao() {
        return ViolationTypes.asList();
    }

    @PostMapping
    public ResponseEntity<DenunciaResponse> create(
            @AuthenticationPrincipal User user, @Valid @RequestBody DenunciaCreateRequest body) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(denunciaService.create(user.getId(), body));
    }

    @GetMapping("/minhas")
    public List<DenunciaResponse> minhas(@AuthenticationPrincipal User user) {
        return denunciaService.listMine(user.getId());
    }
}

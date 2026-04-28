package com.equivoz.service;

import com.equivoz.dto.DenunciaCreateRequest;
import com.equivoz.dto.DenunciaResponse;
import com.equivoz.model.Denuncia;
import com.equivoz.model.User;
import com.equivoz.repository.DenunciaRepository;
import com.equivoz.repository.UserRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DenunciaService {

    private final DenunciaRepository denunciaRepository;
    private final UserRepository userRepository;

    public DenunciaService(DenunciaRepository denunciaRepository, UserRepository userRepository) {
        this.denunciaRepository = denunciaRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public DenunciaResponse create(Long userId, DenunciaCreateRequest request) {
        User user = userRepository.findById(userId).orElseThrow();
        Denuncia d = new Denuncia();
        d.setUser(user);
        d.setTitle(request.getTitle().trim());
        d.setDescription(request.getDescription().trim());
        d.setViolationType(request.getViolationType().trim());
        d.setOccurredAt(request.getOccurredAt());
        if (request.getLocationText() != null && !request.getLocationText().isBlank()) {
            d.setLocationText(request.getLocationText().trim());
        }
        d.setLatitude(request.getLatitude());
        d.setLongitude(request.getLongitude());
        d = denunciaRepository.save(d);
        return DenunciaResponse.from(d);
    }

    @Transactional(readOnly = true)
    public List<DenunciaResponse> listMine(Long userId) {
        return denunciaRepository.findByUser_IdOrderByCreatedAtDesc(userId).stream()
                .map(DenunciaResponse::from)
                .toList();
    }
}

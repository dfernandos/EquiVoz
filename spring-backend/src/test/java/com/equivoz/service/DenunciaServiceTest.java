package com.equivoz.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.equivoz.dto.DenunciaCreateRequest;
import com.equivoz.dto.DenunciaResponse;
import com.equivoz.model.Denuncia;
import com.equivoz.model.User;
import com.equivoz.repository.DenunciaRepository;
import com.equivoz.repository.UserRepository;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/** Testes unitários de {@link DenunciaService} com repositórios mockados. */
@ExtendWith(MockitoExtension.class)
class DenunciaServiceTest {

    @Mock
    private DenunciaRepository denunciaRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private DenunciaService denunciaService;

    @Test
    void create_mapsRequestAndReturnsResponse() {
        User user = new User();
        user.setId(10L);
        user.setEmail("a@b.com");
        when(userRepository.findById(10L)).thenReturn(Optional.of(user));
        when(denunciaRepository.save(any(Denuncia.class)))
                .thenAnswer(
                        inv -> {
                            Denuncia d = inv.getArgument(0);
                            d.setId(100L);
                            return d;
                        });

        DenunciaCreateRequest req = new DenunciaCreateRequest();
        req.setTitle("Título válido aqui");
        req.setDescription("Descrição com mais de dez caracteres.");
        req.setViolationType("racismo");

        DenunciaResponse out = denunciaService.create(10L, req);
        assertThat(out.id()).isEqualTo(100L);
        assertThat(out.userId()).isEqualTo(10L);
        assertThat(out.violationType()).isEqualTo("racismo");
        verify(denunciaRepository).save(any(Denuncia.class));
    }

    @Test
    void listMine_delegatesToRepository() {
        User u = new User();
        u.setId(1L);
        Denuncia d = new Denuncia();
        d.setId(5L);
        d.setUser(u);
        d.setTitle("t");
        d.setDescription("1234567890ab");
        d.setViolationType("outro");
        when(denunciaRepository.findByUser_IdOrderByCreatedAtDesc(1L)).thenReturn(List.of(d));

        List<DenunciaResponse> list = denunciaService.listMine(1L);
        assertThat(list).hasSize(1);
        assertThat(list.get(0).title()).isEqualTo("t");
    }
}

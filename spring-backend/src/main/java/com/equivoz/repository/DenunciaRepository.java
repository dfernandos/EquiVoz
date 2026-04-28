package com.equivoz.repository;

import com.equivoz.model.Denuncia;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DenunciaRepository extends JpaRepository<Denuncia, Long> {

    List<Denuncia> findByUser_IdOrderByCreatedAtDesc(Long userId);
}

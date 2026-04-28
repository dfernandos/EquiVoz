package com.equivoz.web;

import com.equivoz.dto.ViolationTypeDto;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class ViolationTypes {

    private static final Map<String, String> LABELS = new LinkedHashMap<>();

    static {
        LABELS.put("racismo", "Racismo");
        LABELS.put("discriminacao_genero", "Discriminação de gênero");
        LABELS.put("discriminacao_orientacao", "Discriminação por orientação sexual");
        LABELS.put("discriminacao_religiosa", "Discriminação religiosa");
        LABELS.put("discriminacao_deficiencia", "Discriminação por deficiência");
        LABELS.put("violencia", "Violência");
        LABELS.put("servico_publico", "Serviço público (educação, saúde, segurança)");
        LABELS.put("outro", "Outro");
    }

    private ViolationTypes() {}

    public static List<ViolationTypeDto> asList() {
        return LABELS.entrySet().stream()
                .map(e -> new ViolationTypeDto(e.getKey(), e.getValue()))
                .toList();
    }
}

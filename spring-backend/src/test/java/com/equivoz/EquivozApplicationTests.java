package com.equivoz;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/** Smoke test de integração: sobe o ApplicationContext completo. */
@SpringBootTest
@ActiveProfiles("test")
class EquivozApplicationTests {

    @Test
    void contextLoads() {}
}

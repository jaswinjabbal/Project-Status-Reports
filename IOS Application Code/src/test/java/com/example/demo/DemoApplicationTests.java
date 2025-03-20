package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.autoconfigure.ImportAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;

@SpringBootTest(classes = DemoApplication.class)
@ImportAutoConfiguration(exclude = {DataSourceAutoConfiguration.class, HibernateJpaAutoConfiguration.class}) // ✅ Disable DB auto-config in tests
class DemoApplicationTests {

    @Test
    void contextLoads() {
        System.out.println("✅ Test ran successfully without database dependency!");
    }
}

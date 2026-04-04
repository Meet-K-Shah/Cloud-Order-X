package com.cloudorderx.service;

import com.cloudorderx.model.*;
import com.cloudorderx.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import java.math.BigDecimal;

@Component
@RequiredArgsConstructor
@Slf4j
@Profile("!test")
public class DataSeederService implements CommandLineRunner {

    private final CustomerRepository customerRepo;
    private final ProductRepository  productRepo;
    private final OrderRepository    orderRepo;

    @Override
    public void run(String... args) {
        if (customerRepo.count() > 0) return;

        log.info("Seeding demo data...");

        Customer alice = customerRepo.save(Customer.builder().name("Alice Johnson").email("alice@example.com").phone("555-1001").address("123 Main St").city("New York").zipCode("10001").country("USA").build());
        Customer bob   = customerRepo.save(Customer.builder().name("Bob Smith").email("bob@example.com").phone("555-1002").address("456 Oak Ave").city("Chicago").zipCode("60601").country("USA").build());
        Customer carol = customerRepo.save(Customer.builder().name("Carol Davis").email("carol@example.com").phone("555-1003").address("789 Pine Rd").city("San Francisco").zipCode("94102").country("USA").build());

        Product p1 = productRepo.save(Product.builder().name("Laptop Pro X1").description("High-performance business laptop").price(new BigDecimal("1299.99")).stockQuantity(50).category("Electronics").sku("LAP-001").build());
        Product p2 = productRepo.save(Product.builder().name("Wireless Mouse").description("Ergonomic wireless mouse").price(new BigDecimal("39.99")).stockQuantity(200).category("Accessories").sku("MOU-001").build());
        Product p3 = productRepo.save(Product.builder().name("USB-C Hub").description("7-in-1 USB-C hub").price(new BigDecimal("59.99")).stockQuantity(150).category("Accessories").sku("HUB-001").build());
        Product p4 = productRepo.save(Product.builder().name("4K Monitor").description("27-inch 4K IPS display").price(new BigDecimal("499.99")).stockQuantity(30).category("Electronics").sku("MON-001").build());
        Product p5 = productRepo.save(Product.builder().name("Mechanical Keyboard").description("TKL mechanical keyboard").price(new BigDecimal("129.99")).stockQuantity(80).category("Accessories").sku("KEY-001").build());

        log.info("Demo data seeded: 3 customers, 5 products");
    }
}

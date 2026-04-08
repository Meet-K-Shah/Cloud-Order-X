package com.cloudorderx.repository;

import com.cloudorderx.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(String category);
    Optional<Product> findBySku(String sku);
    List<Product> findByStockQuantityLessThan(int threshold);
    List<Product> findByNameContainingIgnoreCase(String name);
}

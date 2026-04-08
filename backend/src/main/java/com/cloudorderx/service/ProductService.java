package com.cloudorderx.service;

import com.cloudorderx.model.Product;
import com.cloudorderx.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository repository;

    public List<Product> getAll()                        { return repository.findAll(); }
    public Product getById(Long id)                      { return repository.findById(id).orElseThrow(() -> new NoSuchElementException("Product not found: " + id)); }
    public List<Product> search(String name)             { return repository.findByNameContainingIgnoreCase(name); }
    public List<Product> getLowStock(int threshold)      { return repository.findByStockQuantityLessThan(threshold); }

    @Transactional
    public Product create(Product product)               { return repository.save(product); }

    @Transactional
    public Product update(Long id, Product updated) {
        Product existing = getById(id);
        existing.setName(updated.getName());
        existing.setDescription(updated.getDescription());
        existing.setPrice(updated.getPrice());
        existing.setStockQuantity(updated.getStockQuantity());
        existing.setCategory(updated.getCategory());
        existing.setSku(updated.getSku());
        return repository.save(existing);
    }

    @Transactional
    public void delete(Long id) {
        repository.deleteById(id);
    }
}

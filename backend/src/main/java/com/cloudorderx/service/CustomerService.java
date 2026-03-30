package com.cloudorderx.service;

import com.cloudorderx.model.Customer;
import com.cloudorderx.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
public class CustomerService {

    private final CustomerRepository repository;

    public List<Customer> getAll()       { return repository.findAll(); }
    public Customer getById(Long id)     { return repository.findById(id).orElseThrow(() -> new NoSuchElementException("Customer not found: " + id)); }
    public Customer getByEmail(String e) { return repository.findByEmail(e).orElseThrow(() -> new NoSuchElementException("Customer not found: " + e)); }

    @Transactional
    public Customer create(Customer c) {
        if (repository.existsByEmail(c.getEmail())) throw new IllegalArgumentException("Email already registered: " + c.getEmail());
        return repository.save(c);
    }

    @Transactional
    public Customer update(Long id, Customer updated) {
        Customer existing = getById(id);
        existing.setName(updated.getName());
        existing.setPhone(updated.getPhone());
        existing.setAddress(updated.getAddress());
        existing.setCity(updated.getCity());
        existing.setZipCode(updated.getZipCode());
        existing.setCountry(updated.getCountry());
        return repository.save(existing);
    }

    @Transactional
    public void delete(Long id) { repository.deleteById(id); }
}

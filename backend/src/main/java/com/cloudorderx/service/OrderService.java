package com.cloudorderx.service;

import com.cloudorderx.dto.*;
import com.cloudorderx.model.*;
import com.cloudorderx.repository.*;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository     orderRepository;
    private final CustomerRepository  customerRepository;
    private final ProductRepository   productRepository;
    private final SimpMessagingTemplate messagingTemplate;
    private final MeterRegistry       meterRegistry;

    private Counter ordersCreatedCounter;
    private Counter ordersDeliveredCounter;
    private Counter ordersCancelledCounter;

    @PostConstruct
    public void initMetrics() {
        ordersCreatedCounter   = Counter.builder("orders.created").description("Total orders created").register(meterRegistry);
        ordersDeliveredCounter = Counter.builder("orders.delivered").description("Total orders delivered").register(meterRegistry);
        ordersCancelledCounter = Counter.builder("orders.cancelled").description("Total orders cancelled").register(meterRegistry);
    }

    // ─── CREATE ───────────────────────────────────────────────────────────────
    @Transactional
    public OrderResponse createOrder(CreateOrderRequest req) {
        Customer customer = customerRepository.findById(req.getCustomerId())
            .orElseThrow(() -> new NoSuchElementException("Customer not found: " + req.getCustomerId()));

        Order order = Order.builder()
            .customer(customer)
            .shippingAddress(req.getShippingAddress() != null ? req.getShippingAddress() : customer.getAddress())
            .notes(req.getNotes())
            .build();

        List<OrderItem> items = new ArrayList<>();
        for (OrderItemRequest itemReq : req.getItems()) {
            Product product = productRepository.findById(itemReq.getProductId())
                .orElseThrow(() -> new NoSuchElementException("Product not found: " + itemReq.getProductId()));

            if (product.getStockQuantity() < itemReq.getQuantity()) {
                throw new IllegalStateException("Insufficient stock for product: " + product.getName());
            }

            product.setStockQuantity(product.getStockQuantity() - itemReq.getQuantity());
            productRepository.save(product);

            items.add(OrderItem.builder()
                .order(order)
                .product(product)
                .quantity(itemReq.getQuantity())
                .unitPrice(product.getPrice())
                .build());
        }

        order.setItems(items);
        order.recalculateTotal();
        Order saved = orderRepository.save(order);

        ordersCreatedCounter.increment();
        log.info("Order created: {}", saved.getOrderNumber());

        OrderResponse response = toResponse(saved);
        messagingTemplate.convertAndSend("/topic/orders", response);
        return response;
    }

    // ─── READ ─────────────────────────────────────────────────────────────────
    @Transactional(readOnly = true)
    public List<OrderResponse> getAllOrders() {
        return orderRepository.findAll().stream().map(this::toResponse).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderById(Long id) {
        return orderRepository.findById(id).map(this::toResponse)
            .orElseThrow(() -> new NoSuchElementException("Order not found: " + id));
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderByNumber(String orderNumber) {
        return orderRepository.findByOrderNumber(orderNumber).map(this::toResponse)
            .orElseThrow(() -> new NoSuchElementException("Order not found: " + orderNumber));
    }

    @Transactional(readOnly = true)
    public List<OrderResponse> getOrdersByCustomer(Long customerId) {
        return orderRepository.findByCustomerId(customerId).stream().map(this::toResponse).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<OrderResponse> getOrdersByStatus(OrderStatus status) {
        return orderRepository.findByStatus(status).stream().map(this::toResponse).collect(Collectors.toList());
    }

    // ─── UPDATE ───────────────────────────────────────────────────────────────
    @Transactional
    public OrderResponse updateOrderStatus(Long id, UpdateOrderStatusRequest req) {
        Order order = orderRepository.findById(id)
            .orElseThrow(() -> new NoSuchElementException("Order not found: " + id));

        OrderStatus prev = order.getStatus();
        order.setStatus(req.getStatus());
        if (req.getPaymentStatus() != null) order.setPaymentStatus(req.getPaymentStatus());
        if (req.getTrackingNumber() != null) order.setTrackingNumber(req.getTrackingNumber());

        Order saved = orderRepository.save(order);

        if (req.getStatus() == OrderStatus.DELIVERED) ordersDeliveredCounter.increment();
        if (req.getStatus() == OrderStatus.CANCELLED)  ordersCancelledCounter.increment();

        log.info("Order {} status changed: {} → {}", order.getOrderNumber(), prev, req.getStatus());

        OrderResponse response = toResponse(saved);
        messagingTemplate.convertAndSend("/topic/orders/" + id, response);
        messagingTemplate.convertAndSend("/topic/orders", response);
        return response;
    }

    // ─── DELETE ───────────────────────────────────────────────────────────────
    @Transactional
    public void deleteOrder(Long id) {
        Order order = orderRepository.findById(id)
            .orElseThrow(() -> new NoSuchElementException("Order not found: " + id));
        orderRepository.delete(order);
        log.info("Order deleted: {}", order.getOrderNumber());
    }

    // ─── REPORTS ──────────────────────────────────────────────────────────────
    @Transactional(readOnly = true)
    public ReportSummaryDto getReportSummary() {
        long total     = orderRepository.count();
        long pending   = orderRepository.countByStatus(OrderStatus.PENDING);
        long delivered = orderRepository.countByStatus(OrderStatus.DELIVERED);
        long cancelled = orderRepository.countByStatus(OrderStatus.CANCELLED);
        BigDecimal revenue = orderRepository.sumTotalRevenue();
        BigDecimal avg     = orderRepository.avgOrderValue();

        Map<String, Long> byStatus = new LinkedHashMap<>();
        for (Object[] row : orderRepository.countGroupByStatus()) {
            byStatus.put(row[0].toString(), ((Number) row[1]).longValue());
        }

        Map<String, BigDecimal> byMonth = new LinkedHashMap<>();
        for (Object[] row : orderRepository.revenueByMonth()) {
            byMonth.put(row[0].toString(), row[1] != null ? new BigDecimal(row[1].toString()) : BigDecimal.ZERO);
        }

        return new ReportSummaryDto(total, pending, delivered, cancelled, revenue, avg, byStatus, byMonth);
    }

    @Transactional(readOnly = true)
    public List<OrderResponse> getOrdersByDateRange(LocalDateTime from, LocalDateTime to) {
        return orderRepository.findByCreatedAtBetween(from, to).stream().map(this::toResponse).collect(Collectors.toList());
    }

    // ─── MAPPER ───────────────────────────────────────────────────────────────
    private OrderResponse toResponse(Order order) {
        OrderResponse r = new OrderResponse();
        r.setId(order.getId());
        r.setOrderNumber(order.getOrderNumber());
        r.setStatus(order.getStatus());
        r.setPaymentStatus(order.getPaymentStatus());
        r.setTotalAmount(order.getTotalAmount());
        r.setShippingAddress(order.getShippingAddress());
        r.setTrackingNumber(order.getTrackingNumber());
        r.setNotes(order.getNotes());
        r.setCreatedAt(order.getCreatedAt());
        r.setUpdatedAt(order.getUpdatedAt());

        OrderResponse.CustomerSummary cs = new OrderResponse.CustomerSummary();
        cs.setId(order.getCustomer().getId());
        cs.setName(order.getCustomer().getName());
        cs.setEmail(order.getCustomer().getEmail());
        r.setCustomer(cs);

        List<OrderResponse.OrderItemResponse> itemResponses = order.getItems().stream().map(i -> {
            OrderResponse.OrderItemResponse ir = new OrderResponse.OrderItemResponse();
            ir.setId(i.getId());
            ir.setProductId(i.getProduct().getId());
            ir.setProductName(i.getProduct().getName());
            ir.setQuantity(i.getQuantity());
            ir.setUnitPrice(i.getUnitPrice());
            ir.setSubtotal(i.getSubtotal());
            return ir;
        }).collect(Collectors.toList());
        r.setItems(itemResponses);

        return r;
    }
}

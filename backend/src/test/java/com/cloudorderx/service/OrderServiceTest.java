package com.cloudorderx.service;

import com.cloudorderx.dto.*;
import com.cloudorderx.model.*;
import com.cloudorderx.repository.*;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.*;
import org.mockito.*;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(org.mockito.junit.jupiter.MockitoExtension.class)
class OrderServiceTest {

    @Mock OrderRepository    orderRepository;
    @Mock CustomerRepository customerRepository;
    @Mock ProductRepository  productRepository;
    @Mock SimpMessagingTemplate messagingTemplate;

    OrderService orderService;

    @BeforeEach
    void setUp() {
        orderService = new OrderService(
            orderRepository, customerRepository, productRepository,
            messagingTemplate, new SimpleMeterRegistry()
        );
        orderService.initMetrics();
    }

    @Test
    void createOrder_shouldReturnOrderResponse() {
        Customer customer = Customer.builder().id(1L).name("Alice").email("alice@test.com").build();
        Product product = Product.builder().id(1L).name("Laptop").price(new BigDecimal("999.00")).stockQuantity(10).build();

        when(customerRepository.findById(1L)).thenReturn(Optional.of(customer));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(productRepository.save(any())).thenReturn(product);

        Order savedOrder = Order.builder()
            .id(1L)
            .orderNumber("ORD-TEST-001")
            .customer(customer)
            .status(OrderStatus.PENDING)
            .paymentStatus(PaymentStatus.UNPAID)
            .totalAmount(new BigDecimal("999.00"))
            .build();
        savedOrder.setItems(List.of(OrderItem.builder()
            .id(1L).order(savedOrder).product(product).quantity(1)
            .unitPrice(new BigDecimal("999.00")).build()));

        when(orderRepository.save(any())).thenReturn(savedOrder);

        OrderItemRequest itemReq = new OrderItemRequest();
        itemReq.setProductId(1L);
        itemReq.setQuantity(1);

        CreateOrderRequest req = new CreateOrderRequest();
        req.setCustomerId(1L);
        req.setItems(List.of(itemReq));

        OrderResponse response = orderService.createOrder(req);

        assertThat(response).isNotNull();
        assertThat(response.getOrderNumber()).isEqualTo("ORD-TEST-001");
        assertThat(response.getStatus()).isEqualTo(OrderStatus.PENDING);
        verify(orderRepository).save(any(Order.class));
    }

    @Test
    void createOrder_withInsufficientStock_shouldThrow() {
        Customer customer = Customer.builder().id(1L).name("Alice").email("alice@test.com").build();
        Product product = Product.builder().id(1L).name("Laptop").price(new BigDecimal("999.00")).stockQuantity(0).build();

        when(customerRepository.findById(1L)).thenReturn(Optional.of(customer));
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        OrderItemRequest itemReq = new OrderItemRequest();
        itemReq.setProductId(1L);
        itemReq.setQuantity(5);

        CreateOrderRequest req = new CreateOrderRequest();
        req.setCustomerId(1L);
        req.setItems(List.of(itemReq));

        assertThatThrownBy(() -> orderService.createOrder(req))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("Insufficient stock");
    }
}

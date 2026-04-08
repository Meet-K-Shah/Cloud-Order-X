package com.cloudorderx.dto;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.util.List;

@Data
public class CreateOrderRequest {
    @NotNull
    private Long customerId;

    @NotEmpty
    private List<OrderItemRequest> items;

    private String shippingAddress;
    private String notes;
}

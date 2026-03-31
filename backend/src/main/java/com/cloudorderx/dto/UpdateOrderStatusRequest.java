package com.cloudorderx.dto;

import com.cloudorderx.model.OrderStatus;
import com.cloudorderx.model.PaymentStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class UpdateOrderStatusRequest {
    @NotNull
    private OrderStatus status;

    private PaymentStatus paymentStatus;
    private String trackingNumber;
}

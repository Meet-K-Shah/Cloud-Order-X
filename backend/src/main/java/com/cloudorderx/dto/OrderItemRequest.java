package com.cloudorderx.dto;

import jakarta.validation.constraints.*;
import lombok.Data;

@Data
public class OrderItemRequest {
    @NotNull
    private Long productId;

    @Min(1)
    @NotNull
    private Integer quantity;
}

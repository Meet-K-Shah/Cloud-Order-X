package com.cloudorderx.repository;

import com.cloudorderx.model.Order;
import com.cloudorderx.model.OrderStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    Optional<Order> findByOrderNumber(String orderNumber);

    List<Order> findByCustomerId(Long customerId);

    List<Order> findByStatus(OrderStatus status);

    List<Order> findByCreatedAtBetween(LocalDateTime from, LocalDateTime to);

    @Query("SELECT COUNT(o) FROM Order o WHERE o.status = :status")
    long countByStatus(@Param("status") OrderStatus status);

    @Query("SELECT COALESCE(SUM(o.totalAmount), 0) FROM Order o WHERE o.status != 'CANCELLED'")
    BigDecimal sumTotalRevenue();

    @Query("SELECT COALESCE(AVG(o.totalAmount), 0) FROM Order o WHERE o.status != 'CANCELLED'")
    BigDecimal avgOrderValue();

    @Query("SELECT o.status, COUNT(o) FROM Order o GROUP BY o.status")
    List<Object[]> countGroupByStatus();

    @Query(value = "SELECT FORMATDATETIME(o.created_at, 'yyyy-MM') as month, " +
                   "SUM(o.total_amount) as revenue " +
                   "FROM orders o WHERE o.status != 'CANCELLED' " +
                   "GROUP BY FORMATDATETIME(o.created_at, 'yyyy-MM') " +
                   "ORDER BY month", nativeQuery = true)
    List<Object[]> revenueByMonth();
}

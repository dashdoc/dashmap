from django.core.exceptions import ValidationError
from django.db import transaction, models
from typing import List, Dict, Any
from .models import Trip, TripStop
from orders.models import Stop, Order


class TripValidationError(ValidationError):
    """Custom validation error for trip-related violations"""

    pass


def validate_trip_stops_completeness(trip: Trip) -> None:
    """
    Validate that all orders in a trip have both pickup and delivery stops.

    Args:
        trip: The Trip instance to validate

    Raises:
        TripValidationError: If any order is missing its pickup or delivery stop
    """
    incomplete_orders = get_incomplete_orders(trip)
    if incomplete_orders:
        order_numbers = [order.order_number for order in incomplete_orders]
        raise TripValidationError(
            f"Trip '{trip.name}' contains incomplete orders. "
            f"Orders {order_numbers} are missing either pickup or delivery stops. "
            f"All orders must have both pickup and delivery stops in the trip."
        )


def validate_new_trip_stop(trip: Trip, stop: Stop) -> None:
    """
    Validate that adding a new stop to a trip maintains order completeness.

    Args:
        trip: The Trip instance to add the stop to
        stop: The Stop instance to be added

    Raises:
        TripValidationError: If adding this stop would violate the completeness rule
    """
    if not stop.order:
        # Stops without orders are allowed (legacy or special stops)
        return

    order = stop.order
    trip_stops = trip.trip_stops.all()
    existing_stop_ids = set(ts.stop.id for ts in trip_stops)

    # Get the paired stop (pickup if this is delivery, delivery if this is pickup)
    paired_stop_type = "pickup" if stop.stop_type == "delivery" else "delivery"
    paired_stop = order.stops.filter(stop_type=paired_stop_type).first()

    if not paired_stop:
        raise TripValidationError(
            f"Order {order.order_number} does not have a {paired_stop_type} stop. "
            f"Cannot add {stop.stop_type} stop without its pair."
        )

    # If the paired stop is not in the trip, this would create an incomplete order
    if paired_stop.id not in existing_stop_ids:
        raise TripValidationError(
            f"Cannot add {stop.stop_type} stop for order {order.order_number} "
            f"without also including its {paired_stop_type} stop. "
            f"Trips must contain complete order journeys (both pickup and delivery)."
        )


def get_incomplete_orders(trip: Trip) -> List[Order]:
    """
    Get a list of orders that have incomplete stop pairs in the trip.

    Args:
        trip: The Trip instance to check

    Returns:
        List of Order instances that are missing either pickup or delivery stops
    """
    trip_stops = trip.trip_stops.select_related("stop", "stop__order").all()
    orders_in_trip = {}

    # Group stops by order
    for trip_stop in trip_stops:
        if trip_stop.stop.order:
            order = trip_stop.stop.order
            if order.id not in orders_in_trip:
                orders_in_trip[order.id] = {"order": order, "stops": []}
            orders_in_trip[order.id]["stops"].append(trip_stop.stop)

    incomplete_orders = []
    for order_data in orders_in_trip.values():
        order = order_data["order"]
        stops = order_data["stops"]
        stop_types = {stop.stop_type for stop in stops}

        # Check if both pickup and delivery are present
        if "pickup" not in stop_types or "delivery" not in stop_types:
            incomplete_orders.append(order)

    return incomplete_orders


def ensure_order_pair_in_trip(trip: Trip, order: Order) -> Dict[str, Any]:
    """
    Ensure both pickup and delivery stops for an order are in the trip.

    Args:
        trip: The Trip instance
        order: The Order instance to ensure completeness for

    Returns:
        Dict with 'pickup_stop' and 'delivery_stop' that should be in the trip

    Raises:
        TripValidationError: If the order doesn't have both pickup and delivery stops
    """
    pickup_stop = order.stops.filter(stop_type="pickup").first()
    delivery_stop = order.stops.filter(stop_type="delivery").first()

    if not pickup_stop:
        raise TripValidationError(
            f"Order {order.order_number} does not have a pickup stop."
        )

    if not delivery_stop:
        raise TripValidationError(
            f"Order {order.order_number} does not have a delivery stop."
        )

    return {"pickup_stop": pickup_stop, "delivery_stop": delivery_stop}


def add_order_to_trip(
    trip: Trip, order: Order, pickup_time, delivery_time, notes: str = ""
) -> Dict[str, Any]:
    """
    Add both pickup and delivery stops for an order to a trip atomically.

    Args:
        trip: The Trip instance to add stops to
        order: The Order instance to add
        pickup_time: Time for pickup stop
        delivery_time: Time for delivery stop
        notes: Optional notes for both stops

    Returns:
        Dict with 'pickup_trip_stop' and 'delivery_trip_stop' instances

    Raises:
        TripValidationError: If the order doesn't have both pickup and delivery stops
    """
    from django.db import transaction
    from .models import TripStop

    # Validate the order has both stops
    order_stops = ensure_order_pair_in_trip(trip, order)
    pickup_stop = order_stops["pickup_stop"]
    delivery_stop = order_stops["delivery_stop"]

    with transaction.atomic():
        # Get the next available sequence numbers for the trip
        last_sequence = (
            trip.trip_stops.aggregate(max_sequence=models.Max("sequence"))[
                "max_sequence"
            ]
            or 0
        )

        pickup_sequence = last_sequence + 1
        delivery_sequence = last_sequence + 2

        # Create both trip stops with validation disabled
        pickup_trip_stop = TripStop(
            trip=trip,
            stop=pickup_stop,
            sequence=pickup_sequence,
            planned_arrival_time=pickup_time,
            notes=notes or f"Pickup for {order.order_number}",
        )
        pickup_trip_stop.save(skip_validation=True)

        delivery_trip_stop = TripStop(
            trip=trip,
            stop=delivery_stop,
            sequence=delivery_sequence,
            planned_arrival_time=delivery_time,
            notes=notes or f"Delivery for {order.order_number}",
        )
        delivery_trip_stop.save(skip_validation=True)

    return {
        "pickup_trip_stop": pickup_trip_stop,
        "delivery_trip_stop": delivery_trip_stop,
    }


def validate_pickup_before_delivery(trip: Trip) -> None:
    """
    Validate that for each order in a trip, pickup stops occur before delivery stops.

    Args:
        trip: The Trip instance to validate

    Raises:
        TripValidationError: If any order has delivery before pickup
    """
    trip_stops = trip.trip_stops.select_related("stop", "stop__order").order_by(
        "sequence"
    )
    orders_in_trip = {}

    # Group stops by order and track their positions
    for trip_stop in trip_stops:
        if trip_stop.stop.order:
            order = trip_stop.stop.order
            if order.id not in orders_in_trip:
                orders_in_trip[order.id] = {"order": order, "stops": []}
            orders_in_trip[order.id]["stops"].append(
                {
                    "trip_stop": trip_stop,
                    "stop_type": trip_stop.stop.stop_type,
                    "sequence_position": trip_stop.sequence,
                }
            )

    # Check each order's pickup-delivery ordering
    for order_data in orders_in_trip.values():
        order = order_data["order"]
        stops = order_data["stops"]

        pickup_positions = [
            s["sequence_position"] for s in stops if s["stop_type"] == "pickup"
        ]
        delivery_positions = [
            s["sequence_position"] for s in stops if s["stop_type"] == "delivery"
        ]

        # If both pickup and delivery exist, pickup must come before delivery
        if pickup_positions and delivery_positions:
            min_pickup_pos = min(pickup_positions)
            min_delivery_pos = min(delivery_positions)

            if min_pickup_pos <= min_delivery_pos:
                raise TripValidationError(
                    f"Order {order.order_number} has delivery stop (position {min_delivery_pos}) "
                    f"before or at same position as pickup stop (position {min_pickup_pos}). "
                    f"Pickup must occur before delivery."
                )


def get_orders_requiring_both_stops() -> List[Order]:
    """
    Get all orders that have both pickup and delivery stops defined.
    This is useful for trip planning to ensure we only work with complete orders.

    Returns:
        List of Order instances that have both pickup and delivery stops
    """
    orders_with_both_stops = []

    for order in Order.objects.prefetch_related("stops").all():
        stops = order.stops.all()
        stop_types = {stop.stop_type for stop in stops}

        if "pickup" in stop_types and "delivery" in stop_types:
            orders_with_both_stops.append(order)

    return orders_with_both_stops


def update_trip_stop_sequences(trip: Trip, new_sequences: List[Dict[str, Any]]) -> None:
    """
    Update the sequence order of trip stops.

    Args:
        trip: The Trip instance to update
        new_sequences: List of dicts with 'id' and 'sequence' keys

    Raises:
        TripValidationError: If some trip stops don't belong to this trip
    """

    with transaction.atomic():
        # Validate that all provided stop IDs belong to this trip
        provided_stop_ids = [item["id"] for item in new_sequences]
        existing_stops = TripStop.objects.filter(trip=trip, id__in=provided_stop_ids)

        if len(existing_stops) != len(provided_stop_ids):
            raise TripValidationError("Some trip stops do not belong to this trip")

        # First, set all orders to very high values to avoid constraint conflicts
        # Use values starting from 10000 to avoid conflicts with existing orders
        for i, sequence_item in enumerate(new_sequences):
            trip_stop = TripStop.objects.get(id=sequence_item["id"], trip=trip)
            trip_stop.sequence = 10000 + i  # Use high values temporarily
            trip_stop.save()

        # Then set the final order values
        for sequence_item in new_sequences:
            trip_stop = TripStop.objects.get(id=sequence_item["id"], trip=trip)
            sequence_value = sequence_item.get("sequence")
            if sequence_value is not None:
                trip_stop.sequence = sequence_value
                trip_stop.save()

from django.db import transaction
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
import json
from datetime import datetime
from .models import Trip, TripStop
from .services import add_order_to_trip, validate_pickup_before_delivery, TripValidationError
from orders.models import Order

logger = logging.getLogger(__name__)


def get_linked_order_for_stop(stop):
    """Get the order that this stop belongs to"""
    if stop.order:
        return {
            "id": stop.order.id,
            "order_number": stop.order.order_number,
            "customer_name": stop.order.customer_name,
        }
    return None


@method_decorator(csrf_exempt, name="dispatch")
class TripListCreateView(View):
    def get(self, request):
        trips = (
            Trip.objects.select_related("vehicle", "dispatcher")
            .prefetch_related("trip_stops__stop")
            .all()
        )

        vehicle_id = request.GET.get("vehicle")
        company_id = request.GET.get("company")

        if vehicle_id:
            trips = trips.filter(vehicle_id=vehicle_id)
        if company_id:
            trips = trips.filter(vehicle__company_id=company_id)

        data = []
        for trip in trips:
            # Include trip_stops data in list view to eliminate N+1 queries
            trip_stops = []
            for trip_stop in trip.trip_stops.all().order_by("sequence"):
                trip_stops.append(
                    {
                        "id": trip_stop.id,
                        "stop": {
                            "id": trip_stop.stop.id,
                            "name": trip_stop.stop.name,
                            "address": trip_stop.stop.address,
                            "latitude": str(trip_stop.stop.latitude)
                            if trip_stop.stop.latitude
                            else None,
                            "longitude": str(trip_stop.stop.longitude)
                            if trip_stop.stop.longitude
                            else None,
                            "stop_type": trip_stop.stop.stop_type,
                            "contact_name": trip_stop.stop.contact_name,
                            "contact_phone": trip_stop.stop.contact_phone,
                            "notes": trip_stop.stop.notes,
                        },
                        "sequence": trip_stop.sequence,
                        "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                        "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                        if trip_stop.actual_arrival_datetime
                        else None,
                        "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                        if trip_stop.actual_departure_datetime
                        else None,
                        "notes": trip_stop.notes,
                        "is_completed": trip_stop.is_completed,
                        "linked_order": get_linked_order_for_stop(trip_stop.stop),
                    }
                )

            data.append(
                {
                    "id": trip.id,
                    "vehicle": trip.vehicle.id,
                    "vehicle_license_plate": trip.vehicle.license_plate,
                    "dispatcher": trip.dispatcher.id,
                    "dispatcher_name": trip.dispatcher.get_full_name(),
                    "name": trip.name,
                    "status": trip.status,
                    "planned_start_date": trip.planned_start_date.isoformat(),
                    "planned_start_time": trip.planned_start_time.isoformat(),
                    "actual_start_datetime": trip.actual_start_datetime.isoformat()
                    if trip.actual_start_datetime
                    else None,
                    "actual_end_datetime": trip.actual_end_datetime.isoformat()
                    if trip.actual_end_datetime
                    else None,
                    "notes": trip.notes,
                    "driver_notified": trip.driver_notified,
                    "trip_stops": trip_stops,
                    "created_at": trip.created_at.isoformat(),
                    "updated_at": trip.updated_at.isoformat(),
                }
            )
        return JsonResponse({"results": data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            trip = Trip.objects.create(
                vehicle_id=data["vehicle"],
                dispatcher_id=data["dispatcher"],
                name=data["name"],
                status=data.get("status", "draft"),
                planned_start_date=data["planned_start_date"],
                planned_start_time=data["planned_start_time"],
                notes=data.get("notes", ""),
            )
            trip.refresh_from_db()
            return JsonResponse(
                {
                    "id": trip.id,
                    "vehicle": trip.vehicle.id,
                    "vehicle_license_plate": trip.vehicle.license_plate,
                    "dispatcher": trip.dispatcher.id,
                    "dispatcher_name": trip.dispatcher.get_full_name(),
                    "name": trip.name,
                    "status": trip.status,
                    "planned_start_date": trip.planned_start_date.isoformat(),
                    "planned_start_time": trip.planned_start_time.isoformat(),
                    "actual_start_datetime": trip.actual_start_datetime.isoformat()
                    if trip.actual_start_datetime
                    else None,
                    "actual_end_datetime": trip.actual_end_datetime.isoformat()
                    if trip.actual_end_datetime
                    else None,
                    "notes": trip.notes,
                    "driver_notified": trip.driver_notified,
                    "created_at": trip.created_at.isoformat(),
                    "updated_at": trip.updated_at.isoformat(),
                },
                status=201,
            )
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({"error": "Invalid data"}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class TripDetailView(View):
    def get_object(self, pk):
        try:
            return (
                Trip.objects.select_related("vehicle", "dispatcher")
                .prefetch_related("trip_stops__stop")
                .get(pk=pk)
            )
        except Trip.DoesNotExist:
            return None

    def get(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({"error": "Trip not found"}, status=404)

        trip_stops = []
        for trip_stop in trip.trip_stops.all().order_by("sequence"):
            trip_stops.append(
                {
                    "id": trip_stop.id,
                    "stop": {
                        "id": trip_stop.stop.id,
                        "name": trip_stop.stop.name,
                        "address": trip_stop.stop.address,
                        "latitude": str(trip_stop.stop.latitude)
                        if trip_stop.stop.latitude
                        else None,
                        "longitude": str(trip_stop.stop.longitude)
                        if trip_stop.stop.longitude
                        else None,
                        "stop_type": trip_stop.stop.stop_type,
                        "contact_name": trip_stop.stop.contact_name,
                        "contact_phone": trip_stop.stop.contact_phone,
                        "notes": trip_stop.stop.notes,
                    },
                    "sequence": trip_stop.sequence,
                    "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                    "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                    if trip_stop.actual_arrival_datetime
                    else None,
                    "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                    if trip_stop.actual_departure_datetime
                    else None,
                    "notes": trip_stop.notes,
                    "is_completed": trip_stop.is_completed,
                    "linked_order": get_linked_order_for_stop(trip_stop.stop),
                }
            )

        return JsonResponse(
            {
                "id": trip.id,
                "vehicle": trip.vehicle.id,
                "vehicle_license_plate": trip.vehicle.license_plate,
                "dispatcher": trip.dispatcher.id,
                "dispatcher_name": trip.dispatcher.get_full_name(),
                "name": trip.name,
                "status": trip.status,
                "planned_start_date": trip.planned_start_date.isoformat(),
                "planned_start_time": trip.planned_start_time.isoformat(),
                "actual_start_datetime": trip.actual_start_datetime.isoformat()
                if trip.actual_start_datetime
                else None,
                "actual_end_datetime": trip.actual_end_datetime.isoformat()
                if trip.actual_end_datetime
                else None,
                "notes": trip.notes,
                "driver_notified": trip.driver_notified,
                "trip_stops": trip_stops,
                "created_at": trip.created_at.isoformat(),
                "updated_at": trip.updated_at.isoformat(),
            }
        )

    def put(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({"error": "Trip not found"}, status=404)

        try:
            data = json.loads(request.body)
            trip.vehicle_id = data.get("vehicle", trip.vehicle_id)
            trip.dispatcher_id = data.get("dispatcher", trip.dispatcher_id)
            trip.name = data.get("name", trip.name)
            trip.status = data.get("status", trip.status)

            # Parse date and time strings if provided
            if "planned_start_date" in data:
                planned_start_date = data["planned_start_date"]
                if isinstance(planned_start_date, str):
                    trip.planned_start_date = datetime.strptime(
                        planned_start_date, "%Y-%m-%d"
                    ).date()
                else:
                    trip.planned_start_date = planned_start_date

            if "planned_start_time" in data:
                planned_start_time = data["planned_start_time"]
                if isinstance(planned_start_time, str):
                    trip.planned_start_time = datetime.strptime(
                        planned_start_time, "%H:%M:%S"
                    ).time()
                else:
                    trip.planned_start_time = planned_start_time

            trip.notes = data.get("notes", trip.notes)
            trip.save()

            return JsonResponse(
                {
                    "id": trip.id,
                    "vehicle": trip.vehicle.id,
                    "vehicle_license_plate": trip.vehicle.license_plate,
                    "dispatcher": trip.dispatcher.id,
                    "dispatcher_name": trip.dispatcher.get_full_name(),
                    "name": trip.name,
                    "status": trip.status,
                    "planned_start_date": trip.planned_start_date.isoformat(),
                    "planned_start_time": trip.planned_start_time.isoformat(),
                    "actual_start_datetime": trip.actual_start_datetime.isoformat()
                    if trip.actual_start_datetime
                    else None,
                    "actual_end_datetime": trip.actual_end_datetime.isoformat()
                    if trip.actual_end_datetime
                    else None,
                    "notes": trip.notes,
                    "driver_notified": trip.driver_notified,
                    "created_at": trip.created_at.isoformat(),
                    "updated_at": trip.updated_at.isoformat(),
                }
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    def delete(self, request, pk):
        trip = self.get_object(pk)
        if not trip:
            return JsonResponse({"error": "Trip not found"}, status=404)

        trip.delete()
        return JsonResponse({}, status=204)


@method_decorator(csrf_exempt, name="dispatch")
class TripNotifyDriverView(View):
    def post(self, request, pk):
        try:
            trip = (
                Trip.objects.select_related("vehicle")
                .prefetch_related("trip_stops__stop")
                .get(pk=pk)
            )
        except Trip.DoesNotExist:
            return JsonResponse({"error": "Trip not found"}, status=404)

        if trip.driver_notified:
            return JsonResponse({"message": "Driver already notified"}, status=400)

        subject = f"Trip Assignment: {trip.name}"
        message = f"""Hello {trip.vehicle.driver_name},

You have been assigned to a new trip:

Trip: {trip.name}
Vehicle: {trip.vehicle.license_plate}
Start Date: {trip.planned_start_date}
Start Time: {trip.planned_start_time}

Stops:"""

        for trip_stop in trip.trip_stops.all().order_by("sequence"):
            message += f"\n{trip_stop.sequence}. {trip_stop.stop.name} ({trip_stop.stop.stop_type}) - {trip_stop.planned_arrival_time}"
            message += f"\n   Address: {trip_stop.stop.address}"
            if trip_stop.notes:
                message += f"\n   Notes: {trip_stop.notes}"

        if trip.notes:
            message += f"\n\nTrip Notes: {trip.notes}"

        try:
            send_mail(
                subject,
                message,
                "dispatcher@company.com",
                [trip.vehicle.driver_email],
                fail_silently=False,
            )

            trip.driver_notified = True
            trip.save()

            return JsonResponse({"message": "Driver notified successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class TripStopListView(View):
    def get(self, request):
        trip_stops = TripStop.objects.select_related("trip", "stop").all()

        trip_id = request.GET.get("trip")
        if trip_id:
            trip_stops = trip_stops.filter(trip_id=trip_id)

        data = []
        for trip_stop in trip_stops.order_by("sequence"):
            data.append(
                {
                    "id": trip_stop.id,
                    "trip": trip_stop.trip.id,
                    "stop": {
                        "id": trip_stop.stop.id,
                        "name": trip_stop.stop.name,
                        "address": trip_stop.stop.address,
                        "latitude": str(trip_stop.stop.latitude)
                        if trip_stop.stop.latitude
                        else None,
                        "longitude": str(trip_stop.stop.longitude)
                        if trip_stop.stop.longitude
                        else None,
                        "stop_type": trip_stop.stop.stop_type,
                    },
                    "sequence": trip_stop.sequence,
                    "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                    "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                    if trip_stop.actual_arrival_datetime
                    else None,
                    "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                    if trip_stop.actual_departure_datetime
                    else None,
                    "notes": trip_stop.notes,
                    "is_completed": trip_stop.is_completed,
                }
            )
        return JsonResponse({"results": data})


@method_decorator(csrf_exempt, name="dispatch")
class TripStopDetailView(View):
    def get_object(self, pk):
        try:
            return TripStop.objects.select_related("trip", "stop").get(pk=pk)
        except TripStop.DoesNotExist:
            return None

    def get(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({"error": "Trip stop not found"}, status=404)

        return JsonResponse(
            {
                "id": trip_stop.id,
                "trip": trip_stop.trip.id,
                "stop": {
                    "id": trip_stop.stop.id,
                    "name": trip_stop.stop.name,
                    "address": trip_stop.stop.address,
                    "latitude": str(trip_stop.stop.latitude)
                    if trip_stop.stop.latitude
                    else None,
                    "longitude": str(trip_stop.stop.longitude)
                    if trip_stop.stop.longitude
                    else None,
                    "stop_type": trip_stop.stop.stop_type,
                },
                "sequence": trip_stop.sequence,
                "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                if trip_stop.actual_arrival_datetime
                else None,
                "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                if trip_stop.actual_departure_datetime
                else None,
                "notes": trip_stop.notes,
                "is_completed": trip_stop.is_completed,
            }
        )

    def put(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({"error": "Trip stop not found"}, status=404)

        try:
            data = json.loads(request.body)
            trip_stop.sequence = data.get("sequence", trip_stop.sequence)
            trip_stop.planned_arrival_time = data.get(
                "planned_arrival_time", trip_stop.planned_arrival_time
            )
            trip_stop.notes = data.get("notes", trip_stop.notes)
            trip_stop.is_completed = data.get("is_completed", trip_stop.is_completed)
            trip_stop.save()

            return JsonResponse(
                {
                    "id": trip_stop.id,
                    "trip": trip_stop.trip.id,
                    "stop": {
                        "id": trip_stop.stop.id,
                        "name": trip_stop.stop.name,
                        "address": trip_stop.stop.address,
                        "latitude": str(trip_stop.stop.latitude)
                        if trip_stop.stop.latitude
                        else None,
                        "longitude": str(trip_stop.stop.longitude)
                        if trip_stop.stop.longitude
                        else None,
                        "stop_type": trip_stop.stop.stop_type,
                    },
                    "sequence": trip_stop.sequence,
                    "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                    "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                    if trip_stop.actual_arrival_datetime
                    else None,
                    "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                    if trip_stop.actual_departure_datetime
                    else None,
                    "notes": trip_stop.notes,
                    "is_completed": trip_stop.is_completed,
                }
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    def delete(self, request, pk):
        trip_stop = self.get_object(pk)
        if not trip_stop:
            return JsonResponse({"error": "Trip stop not found"}, status=404)

        trip = trip_stop.trip
        deleted_sequence = trip_stop.sequence

        # Delete the trip stop
        trip_stop.delete()

        # Reorder remaining stops to close gaps
        remaining_stops = TripStop.objects.filter(
            trip=trip, sequence__gt=deleted_sequence
        ).order_by("sequence")

        # Shift all stops with higher sequence numbers down by 1
        for stop in remaining_stops:
            stop.sequence -= 1
            stop.save()

        return JsonResponse({}, status=204)


@method_decorator(csrf_exempt, name="dispatch")
class TripStopReorderView(View):
    def post(self, request, trip_pk):
        """Reorder trip stops for a given trip"""
        try:
            data = json.loads(request.body)
            # Support both 'orders' (legacy) and 'sequences' (new) parameter names
            new_sequences = data.get("sequences") or data.get("orders", [])

            logger.info(f"Reordering stops for trip {trip_pk}: {new_sequences}")

            if not new_sequences:
                return JsonResponse({"error": "No orders provided"}, status=400)

            # Verify the trip exists
            try:
                trip = Trip.objects.get(pk=trip_pk)
            except Trip.DoesNotExist:
                return JsonResponse({"error": "Trip not found"}, status=404)

            with transaction.atomic():
                # Validate that all provided stop IDs belong to this trip
                provided_stop_ids = [item["id"] for item in new_sequences]
                existing_stops = TripStop.objects.filter(
                    trip=trip, id__in=provided_stop_ids
                )

                if len(existing_stops) != len(provided_stop_ids):
                    return JsonResponse(
                        {"error": "Some trip stops do not belong to this trip"},
                        status=400,
                    )

                # First, set all orders to very high values to avoid constraint conflicts
                # Use values starting from 10000 to avoid conflicts with existing orders
                for i, sequence_item in enumerate(new_sequences):
                    trip_stop = TripStop.objects.get(id=sequence_item["id"], trip=trip)
                    trip_stop.sequence = 10000 + i  # Use high values temporarily
                    trip_stop.save()

                # Then set the final order values
                for sequence_item in new_sequences:
                    trip_stop = TripStop.objects.get(id=sequence_item["id"], trip=trip)
                    # Support both 'sequence' (new) and 'order' (legacy) field names in data
                    new_seq = sequence_item.get("sequence") or sequence_item.get("order")
                    trip_stop.sequence = new_seq
                    trip_stop.save()

                # Validate that pickups happen before deliveries
                validate_pickup_before_delivery(trip)

            # Return updated trip stops
            updated_stops = TripStop.objects.filter(trip=trip).order_by("sequence")
            data = []
            for trip_stop in updated_stops:
                data.append(
                    {
                        "id": trip_stop.id,
                        "trip": trip_stop.trip.id,
                        "stop": {
                            "id": trip_stop.stop.id,
                            "name": trip_stop.stop.name,
                            "address": trip_stop.stop.address,
                            "latitude": str(trip_stop.stop.latitude)
                            if trip_stop.stop.latitude
                            else None,
                            "longitude": str(trip_stop.stop.longitude)
                            if trip_stop.stop.longitude
                            else None,
                            "stop_type": trip_stop.stop.stop_type,
                        },
                        "sequence": trip_stop.sequence,
                        "planned_arrival_time": trip_stop.planned_arrival_time.isoformat(),
                        "actual_arrival_datetime": trip_stop.actual_arrival_datetime.isoformat()
                        if trip_stop.actual_arrival_datetime
                        else None,
                        "actual_departure_datetime": trip_stop.actual_departure_datetime.isoformat()
                        if trip_stop.actual_departure_datetime
                        else None,
                        "notes": trip_stop.notes,
                        "is_completed": trip_stop.is_completed,
                    }
                )

            return JsonResponse({"results": data}, status=200)

        except TripValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return JsonResponse({"error": "Invalid data format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class TripAddOrderView(View):
    """Add a complete order (pickup + delivery) to a trip"""

    def post(self, request, trip_pk):
        try:
            from datetime import time as datetime_time

            data = json.loads(request.body)
            trip = Trip.objects.get(pk=trip_pk)
            order = Order.objects.get(pk=data["order"])

            # Convert string times to time objects
            pickup_time = datetime_time.fromisoformat(data["pickup_time"])
            delivery_time = datetime_time.fromisoformat(data["delivery_time"])

            result = add_order_to_trip(
                trip=trip,
                order=order,
                pickup_time=pickup_time,
                delivery_time=delivery_time,
                notes=data.get("notes", ""),
            )

            pickup_ts = result["pickup_trip_stop"]
            delivery_ts = result["delivery_trip_stop"]

            return JsonResponse(
                {
                    "message": f"Successfully added order {order.order_number} to trip",
                    "pickup_trip_stop": {
                        "id": pickup_ts.id,
                        "sequence": pickup_ts.sequence,
                        "planned_arrival_time": pickup_ts.planned_arrival_time.isoformat(),
                        "stop": {
                            "id": pickup_ts.stop.id,
                            "name": pickup_ts.stop.name,
                            "stop_type": pickup_ts.stop.stop_type,
                        },
                    },
                    "delivery_trip_stop": {
                        "id": delivery_ts.id,
                        "sequence": delivery_ts.sequence,
                        "planned_arrival_time": delivery_ts.planned_arrival_time.isoformat(),
                        "stop": {
                            "id": delivery_ts.stop.id,
                            "name": delivery_ts.stop.name,
                            "stop_type": delivery_ts.stop.stop_type,
                        },
                    },
                },
                status=201,
            )

        except Trip.DoesNotExist:
            return JsonResponse({"error": "Trip not found"}, status=404)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except TripValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except (KeyError, json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid data format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

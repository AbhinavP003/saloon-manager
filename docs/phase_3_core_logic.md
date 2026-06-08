# 🛡️ Phase 3 Specification: The Booking Life Cycle

## 1. Objective
To transition the booking system from a static "Request-Only" model to a dynamic "Managed-Appointment" system. This phase ensures that time slots are used efficiently and provide the saloon owner with full control over their daily schedule.

---

## 2. Status Definitions & Terminal States
We will transition from raw strings to a formal **Terminal State** model. Once a record enters a terminal state, it cannot be reverted to protect the integrity of historical logs and future analytics.

| Status | Type | Definition |
| :--- | :--- | :--- |
| `pending` | Active | Initial state. Awaiting owner review. |
| `confirmed` | Active | Owner has accepted; professional is booked. |
| **`cancelled`** | **Terminal** | Appointment dissolved. Slot is returned to the pool. |
| **`completed`** | **Terminal** | Service rendered. Ready for revenue reporting. |
| **`no-show`** | **Terminal** | Slot was held but customer failed to arrive. |

---

## 3. Transition Matrix & Authorization

| Current Status | Target Status | Role | Logic/Rule |
| :--- | :--- | :--- | :--- |
| `pending` | `confirmed` | **Owner** | "I accept this customer request." |
| `pending` | `cancelled` | **Both** | User can cancel anytime while still pending. |
| `confirmed` | `cancelled` | **Both** | User can only cancel if `startTime > 2hrs` from now. |
| `confirmed` | `completed` | **Owner** | "Haircut is done; customer paid." |
| `confirmed` | `no-show` | **Owner** | "I waited 15 mins, no one showed up." |

---

## 4. Availability Recovery
When a status changes to `cancelled`, the engine must ensure the slot is recovered:
- **Backend Query**: The `GET /slots` service filters by `Booking.status != "cancelled"`. 
- **Immediate Effect**: Upon successful `PATCH /status`, the database release the block, making the slot instantly visible to other browsing users.

---

## 5. Cancellation Policy (The 2-Hour Rule)
To prevent last-minute losses for the salon:
- **Client Side**: We will verify `datetime.now() + 2 hours < booking.start_time`. 
- **Error Response**: If within 2 hours, return `400 Bad Request`: "Cancellations late in the window must be handled via telephone with the saloon owner."

---

## 6. Implementation Checklist
1. [x] Define `BookingStatus(str, Enum)` in Models.
2. [ ] Add `status_updated_at` and `status_reason` (optional) to Database — deferred to Phase 5.
3. [x] Implement transition validation (inline in `PATCH /owner/bookings/{id}/status`).
4. [x] Create `PATCH /owner/bookings/{id}/status` endpoint.
5. [x] Create `PATCH /users/bookings/{id}/cancel` endpoint with Time-Gate.

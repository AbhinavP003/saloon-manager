const API_URL = "http://localhost:8000/api/v1";

export async function fetchStores() {
  const res = await fetch(`${API_URL}/users/stores/`);
  if (!res.ok) throw new Error("Failed to fetch stores");
  return res.json();
}

export async function fetchStoreDetails(id: string) {
  const res = await fetch(`${API_URL}/users/stores/${id}`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error("Failed to fetch store details");
  }
  return res.json();
}

export async function fetchStoreServices(id: string) {
  const res = await fetch(`${API_URL}/users/stores/${id}/services`);
  if (!res.ok) throw new Error("Failed to fetch store services");
  return res.json();
}

export async function fetchAvailableSlots(storeId: string, serviceId: string, targetDate: string) {
  const url = `${API_URL}/users/bookings/store/${storeId}/slots?service_id=${serviceId}&target_date=${targetDate}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch available slots");
  return res.json();
}

export async function createBooking(payload: {
  store_id: string;
  service_id: string;
  customer_name: string;
  start_time: string;
}) {
  const res = await fetch(`${API_URL}/users/bookings/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to create booking");
  }
  return res.json();
}

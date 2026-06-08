const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export const API_URL = `${API_BASE}/api/v1`;

// Auth Helpers
export const getStoredToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
};

export const setStoredToken = (token: string) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("token", token);
  }
};

export const clearStoredToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
  }
};

export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Login failed");
  }

  const data = await res.json();
  setStoredToken(data.access_token);
  return data;
}

export async function register(payload: any) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Registration failed");
  }

  return res.json();
}

export async function fetchCurrentUser() {
  const token = getStoredToken();
  if (!token) return null;

  const res = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    clearStoredToken();
    return null;
  }
  return res.json();
}

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
  const token = getStoredToken();
  const headers: any = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/users/bookings/`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to create booking");
  }
  return res.json();
}

export async function fetchBooking(id: string) {
  const res = await fetch(`${API_URL}/users/bookings/${id}`);
  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error("Failed to fetch booking details");
  }
  return res.json();
}

export async function fetchStoreBookings(storeId: string) {
  const token = getStoredToken();
  const res = await fetch(`${API_URL}/owner/bookings/store/${storeId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch store bookings");
  return res.json();
}

export async function updateBookingStatus(bookingId: string, status: string) {
  const token = getStoredToken();
  const res = await fetch(`${API_URL}/owner/bookings/${bookingId}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to update booking status");
  }
  return res.json();
}

export async function fetchMyBookings() {
  const token = getStoredToken();
  if (!token) throw new Error("Authentication required");

  const res = await fetch(`${API_URL}/users/bookings/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error("Failed to fetch your bookings");
  return res.json();
}

export async function fetchStoreAnalytics(storeId: string, month: string) {
  const token = getStoredToken();
  const res = await fetch(
    `${API_URL}/owner/stores/${storeId}/analytics?month=${month}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to fetch store analytics");
  }
  return res.json();
}

export async function cancelBooking(bookingId: string) {
  const token = getStoredToken();
  const headers: any = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/users/bookings/${bookingId}/cancel`, {
    method: "PATCH",
    headers,
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || "Failed to cancel booking");
  }
  return res.json();
}

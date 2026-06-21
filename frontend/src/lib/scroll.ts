const NAVBAR_OFFSET_PX = 88;

/** Scroll to a page section reliably (works even when the hash is already set). */
export function scrollToSection(id: string): boolean {
  const el = document.getElementById(id);
  if (!el) return false;

  const top = el.getBoundingClientRect().top + window.scrollY - NAVBAR_OFFSET_PX;
  window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
  window.history.replaceState(null, "", `#${id}`);
  return true;
}

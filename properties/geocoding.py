"""
properties/geocoding.py

Server-side geocoding and location-obfuscation utilities.

Priority order for geocoding:
  1. Google Geocoding API (place_id) — most precise, requires GOOGLE_MAPS_API_KEY
  2. Google Geocoding API (address string) — fallback if no place_id
  3. OpenStreetMap Nominatim — final fallback, no key needed

PRIVACY GUARANTEE
-----------------
lat_private / lng_private are ONLY stored server-side.
lat_public / lng_public are offset copies — the only coords ever sent to
the browser.  They are randomised within a radius band so the exact address
cannot be reverse-engineered from the circle centre alone.
"""

import json
import logging
import math
import random
import time
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

# ── Google Geocoding ─────────────────────────────────────────────────────────

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def _google_api_key() -> str | None:
    try:
        from django.conf import settings
        return getattr(settings, 'GOOGLE_MAPS_API_KEY', None) or None
    except Exception:
        return None


def geocode_by_place_id(place_id: str) -> tuple[float, float] | None:
    """
    Resolve a Google Place ID to exact (lat, lng) via Google Geocoding API.
    Returns None if key is missing, place_id is blank, or request fails.
    """
    key = _google_api_key()
    if not key or not place_id:
        return None

    params = urllib.parse.urlencode({"place_id": place_id, "key": key})
    url = f"{GOOGLE_GEOCODE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "AdonisGroup/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
        logger.warning("Google Geocoding by place_id %r → status=%s", place_id, data.get("status"))
    except Exception as exc:
        logger.warning("Google Geocoding (place_id) failed: %s", exc)
    return None


def geocode_address_google(address_str: str) -> tuple[float, float] | None:
    """
    Geocode a plain address string using Google Geocoding API.
    Returns None if key is missing or request fails.
    """
    key = _google_api_key()
    if not key or not address_str:
        return None

    params = urllib.parse.urlencode({"address": address_str.strip(), "key": key})
    url = f"{GOOGLE_GEOCODE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "AdonisGroup/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
        logger.warning("Google Geocoding address %r → status=%s", address_str, data.get("status"))
    except Exception as exc:
        logger.warning("Google Geocoding (address) failed: %s", exc)
    return None


# ── Nominatim fallback ────────────────────────────────────────────────────────

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "AdonisGroup/1.0 (contact@adonisgroup.gr)"


def geocode_address_nominatim(address_str: str) -> tuple[float, float] | None:
    """
    Geocode using OpenStreetMap Nominatim (free, no key needed).
    Rate-limited to 1 req/s — acceptable for admin-triggered saves.
    """
    if not address_str or not address_str.strip():
        return None
    params = urllib.parse.urlencode({
        "q": address_str.strip(),
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    })
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        time.sleep(1)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as exc:
        logger.warning("Nominatim geocoding failed for %r: %s", address_str, exc)
    return None


# ── Public entry-point used by Property.save() ───────────────────────────────

def geocode_address(address_str: str) -> tuple[float, float] | None:
    """
    Try Google Geocoding first, then Nominatim.
    Called from Property._run_geocoding() when no place_id is available.
    """
    result = geocode_address_google(address_str)
    if result is None:
        result = geocode_address_nominatim(address_str)
    return result


# ── Obfuscation ───────────────────────────────────────────────────────────────

_METRES_PER_DEG_LAT = 111_320.0

NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

# Keys in a Nominatim address object that indicate the point is on water.
_WATER_KEYS = frozenset({
    "body_of_water", "sea", "bay", "strait", "ocean",
    "lake", "river", "wetland", "waterway",
})

# Keys that confirm the point is on land.
_LAND_KEYS = frozenset({
    "road", "pedestrian", "suburb", "neighbourhood", "quarter",
    "town", "city", "village", "hamlet", "county", "state",
    "postcode", "building", "amenity", "leisure", "landuse",
    "man_made", "military",
})


def _metres_per_deg_lng(lat_deg: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat_deg))


def _is_point_on_land(lat: float, lng: float) -> bool:
    """
    Returns True when the coordinate appears to be on land, False if it is
    in a body of water.

    Uses Nominatim reverse-geocoding at neighbourhood zoom level (15).
    Nominatim rate limit: 1 request per second — call site must ensure this.

    Decision logic:
      - If Nominatim returns an error (Unable to geocode)  → water / unpopulated sea
      - If address contains a known water key               → water
      - If address contains a known land key                → land
      - OSM type is explicitly a water feature              → water
      - Anything else (unclear / rural)                     → assume land
    """
    params = urllib.parse.urlencode({
        "lat": f"{lat:.6f}",
        "lon": f"{lng:.6f}",
        "format": "json",
        "zoom": 15,
        "addressdetails": 1,
    })
    url = f"{NOMINATIM_REVERSE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        logger.warning("Nominatim reverse geocode failed for (%.5f, %.5f): %s", lat, lng, exc)
        return True  # assume land on network failure to avoid infinite retries

    if "error" in data:
        # "Unable to geocode" is the standard Nominatim response for open sea
        logger.debug("Nominatim: no result for (%.5f, %.5f) → treating as water", lat, lng)
        return False

    address = data.get("address", {})
    osm_type = data.get("type", "")

    if any(k in address for k in _WATER_KEYS):
        return False
    if osm_type in ("water", "sea", "bay", "strait", "wetland", "waterway"):
        return False
    if any(k in address for k in _LAND_KEYS):
        return True

    # Ambiguous result (e.g. rural wilderness) — treat as land
    return True


def generate_public_point(
    lat: float,
    lng: float,
    radius_m: int = 400,
    min_offset_m: int = 120,
    check_land: bool = True,
    max_attempts: int = 8,
) -> tuple[float, float]:
    """
    Return a privacy-obfuscated point within the annulus [min_offset_m, radius_m]
    from (lat, lng).

    When check_land=True (default) the function verifies each candidate with a
    Nominatim reverse-geocode call and retries until a land point is found, or
    max_attempts is exhausted.  Each attempt adds ≈1 s due to Nominatim rate
    limiting, so worst-case latency is max_attempts × 1 s.

    Fallback (if all candidates are water): returns the private point offset by
    min_offset_m to the north-east — almost always inland for Greek coastal cities.
    """
    radius_m = max(radius_m, min_offset_m + 50)

    def _candidate() -> tuple[float, float]:
        distance_m = random.uniform(min_offset_m, radius_m)
        bearing_rad = math.radians(random.uniform(0, 360))
        dlat = (distance_m * math.cos(bearing_rad)) / _METRES_PER_DEG_LAT
        dlng = (distance_m * math.sin(bearing_rad)) / _metres_per_deg_lng(lat)
        return lat + dlat, lng + dlng

    if not check_land:
        return _candidate()

    for attempt in range(1, max_attempts + 1):
        candidate_lat, candidate_lng = _candidate()

        # Nominatim ToS: 1 request per second
        time.sleep(1)
        if _is_point_on_land(candidate_lat, candidate_lng):
            logger.info(
                "Land-safe public point found on attempt %d for origin (%.5f, %.5f)",
                attempt, lat, lng,
            )
            return candidate_lat, candidate_lng

        logger.debug(
            "Attempt %d/%d: candidate (%.5f, %.5f) is water, retrying",
            attempt, max_attempts, candidate_lat, candidate_lng,
        )

    # All attempts landed in water — fall back to a north-east offset which is
    # inland for the vast majority of Greek coastal properties.
    logger.warning(
        "All %d land candidates failed for origin (%.5f, %.5f); "
        "falling back to north-east minimal offset.",
        max_attempts, lat, lng,
    )
    ne_bearing = math.radians(45)  # north-east
    dlat = (min_offset_m * math.cos(ne_bearing)) / _METRES_PER_DEG_LAT
    dlng = (min_offset_m * math.sin(ne_bearing)) / _metres_per_deg_lng(lat)
    return lat + dlat, lng + dlng

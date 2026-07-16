import math
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


@router.get("/nearby")
def nearby_hospitals(lat: float, lon: float, radius_m: int = 8000):
    """
    Uses OpenStreetMap's Overpass API (free, no key required) to find hospitals,
    clinics (PHC/CHC equivalents), and pharmacies near the given coordinates.
    Swap to Google Places API for richer data (ratings, live open/closed) if
    GOOGLE_MAPS_API_KEY is configured — see the TODO below.
    """
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="clinic"](around:{radius_m},{lat},{lon});
      node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
      node["healthcare"="centre"](around:{radius_m},{lat},{lon});
    );
    out center;
    """
    try:
        resp = httpx.post(OVERPASS_URL, data={"data": query}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        raise HTTPException(502, "Could not reach the maps service. Please try again.")

    results = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name", "Unnamed facility")
        amenity = tags.get("amenity", tags.get("healthcare", "facility"))
        el_lat, el_lon = el.get("lat"), el.get("lon")
        if el_lat is None or el_lon is None:
            continue
        distance = round(haversine_km(lat, lon, el_lat, el_lon), 2)
        address = ", ".join(
            filter(
                None,
                [
                    tags.get("addr:housenumber"),
                    tags.get("addr:street"),
                    tags.get("addr:village") or tags.get("addr:city"),
                ],
            )
        ) or None

        results.append(
            {
                "name": name,
                "type": amenity,
                "address": address,
                "distance_km": distance,
                "latitude": el_lat,
                "longitude": el_lon,
                "open_now": None,  # TODO: Google Places API provides live open/closed status
            }
        )

    results.sort(key=lambda r: r["distance_km"])
    return results[:25]


@router.get("/by-pincode")
def hospitals_by_pincode(pincode: str):
    """Geocode a PIN code (via OSM Nominatim) then reuse the nearby-search logic."""
    try:
        geo = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params={"postalcode": pincode, "country": "India", "format": "json", "limit": 1},
            headers={"User-Agent": "GramSwasthyaAI/1.0"},
            timeout=15,
        )
        geo.raise_for_status()
        geo_data = geo.json()
    except Exception:
        raise HTTPException(502, "Could not resolve this PIN code right now.")

    if not geo_data:
        raise HTTPException(404, "PIN code not found")

    lat, lon = float(geo_data[0]["lat"]), float(geo_data[0]["lon"])
    return nearby_hospitals(lat=lat, lon=lon)

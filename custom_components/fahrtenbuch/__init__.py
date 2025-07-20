import os
import csv
import datetime

from homeassistant.helpers.event import async_track_state_change
from .const import DOMAIN

def write_trip(file_path, start, end):
    """Blocking file-IO, deshalb später per executor aufrufen."""
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    new_file = not os.path.exists(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if new_file:
            writer.writerow([
                "start_time","start_lat","start_lon","start_battery",
                "end_time","end_lat","end_lon","end_battery"
            ])
        writer.writerow([
            start["time"], start["lat"], start["lon"], start["battery"],
            end["time"], end["lat"], end["lon"], end["battery"]
        ])

async def async_setup_entry(hass, entry):
    cfg = entry.data
    speed_entity = cfg["speed_sensor"]
    gps_lat     = cfg["gps_latitude"]
    gps_lon     = cfg["gps_longitude"]
    battery     = cfg["battery_sensor"]
    threshold   = cfg["threshold"]
    file_path   = hass.config.path(cfg["file_path"])

    # Zwischenablage für den Start
    trip = {}

    def speed_changed(entity, old, new):
        try:
            old_val = float(old.state) if old and old.state not in ("unknown","unavailable") else 0.0
            new_val = float(new.state) if new and new.state not in ("unknown","unavailable") else 0.0
        except (ValueError, TypeError):
            return

        now = datetime.datetime.utcnow().isoformat()
        # Fahrt beginnt
        if old_val < threshold <= new_val:
            trip["start"] = {
                "time": now,
                "lat": hass.states.get(gps_lat).state,
                "lon": hass.states.get(gps_lon).state,
                "battery": hass.states.get(battery).state
            }
        # Fahrt endet
        elif old_val >= threshold > new_val and "start" in trip:
            start = trip.pop("start")
            end = {
                "time": now,
                "lat": hass.states.get(gps_lat).state,
                "lon": hass.states.get(gps_lon).state,
                "battery": hass.states.get(battery).state
            }
            # Schreibjob im Hintergrund
            hass.loop.create_task(
                hass.async_add_executor_job(write_trip, file_path, start, end)
            )

    # Listener auf den Speed-Sensor
    async_track_state_change(hass, speed_entity, speed_changed)
    return True

#https://stackoverflow.com/questions/5222951/easy-way-to-get-the-correct-time-in-python
import ntplib
from datetime import datetime, timezone

def get_ntp_time(ntp_server='pool.ntp.org'):
    """
    Retrieves the current time from an NTP server.
    """
    try:
        client = ntplib.NTPClient()
        response = client.request(ntp_server, version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time, tz=timezone.utc)
        return ntp_time
    except Exception as e:
        print(f"Error getting time from NTP server: {e}")
        return None

# Example usage:
current_utc_time = get_ntp_time()

if current_utc_time:
    print(f"Current UTC time from NTP server: {current_utc_time}")
else:
    print("Could not retrieve time from NTP server.")
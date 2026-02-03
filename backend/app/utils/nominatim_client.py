"""
Nominatim Client - Geocoding and address lookup
"""

import asyncio
import aiohttp
from typing import Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class NominatimClient:
    """Client for Nominatim geocoding service"""

    BASE_URL = "https://nominatim.openstreetmap.org"
    TIMEOUT = 10

    def __init__(self, user_agent: str = "sistema-de-laudos"):
        """
        Initialize Nominatim client.

        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent

    async def geocode(
        self,
        address: str,
        country: str = "Brazil"
    ) -> Optional[Tuple[Decimal, Decimal, str]]:
        """
        Geocode address to coordinates.

        Args:
            address: Full address string
            country: Country name

        Returns:
            Tuple of (latitude, longitude, formatted_address) or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": f"{address}, {country}",
                    "format": "json",
                    "limit": 1
                }
                headers = {"User-Agent": self.user_agent}

                async with session.get(
                    f"{self.BASE_URL}/search",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            result = data[0]
                            lat = Decimal(result["lat"])
                            lon = Decimal(result["lon"])
                            display_name = result.get("display_name", "")
                            logger.info(f"Geocoded: {address} -> {lat}, {lon}")
                            return (lat, lon, display_name)
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout geocoding address: {address}")
            return None
        except Exception as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
            return None

    async def reverse_geocode(
        self,
        latitude: Decimal,
        longitude: Decimal
    ) -> Optional[str]:
        """
        Reverse geocode coordinates to address.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Address string or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "lat": str(latitude),
                    "lon": str(longitude),
                    "format": "json"
                }
                headers = {"User-Agent": self.user_agent}

                async with session.get(
                    f"{self.BASE_URL}/reverse",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        address = data.get("address", {})
                        display_name = data.get("display_name", "")
                        logger.info(f"Reverse geocoded: {latitude}, {longitude} -> {display_name}")
                        return display_name
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout reverse geocoding: {latitude}, {longitude}")
            return None
        except Exception as e:
            logger.error(f"Error reverse geocoding {latitude}, {longitude}: {str(e)}")
            return None

    def geocode_sync(
        self,
        address: str,
        country: str = "Brazil"
    ) -> Optional[Tuple[Decimal, Decimal, str]]:
        """
        Synchronous geocode address (wrapper around async method).

        Args:
            address: Full address string
            country: Country name

        Returns:
            Tuple of (latitude, longitude, formatted_address) or None
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.geocode(address, country))

    def reverse_geocode_sync(
        self,
        latitude: Decimal,
        longitude: Decimal
    ) -> Optional[str]:
        """
        Synchronous reverse geocode (wrapper around async method).

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Address string or None
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.reverse_geocode(latitude, longitude))

"""
Distance Calculator - Calcula distância entre dois pontos usando Haversine Formula
"""

from decimal import Decimal
import math


class DistanceCalculator:
    """Calculate distance between two geographic coordinates"""

    @staticmethod
    def haversine(
        lat1: Decimal,
        lon1: Decimal,
        lat2: Decimal,
        lon2: Decimal
    ) -> Decimal:
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1: Latitude of point 1
            lon1: Longitude of point 1
            lat2: Latitude of point 2
            lon2: Longitude of point 2

        Returns:
            Distance in kilometers
        """
        # Convert Decimal to float for math operations
        lat1_f = float(lat1)
        lon1_f = float(lon1)
        lat2_f = float(lat2)
        lon2_f = float(lon2)

        # Earth's radius in kilometers
        R = 6371.0

        # Convert degrees to radians
        lat1_rad = math.radians(lat1_f)
        lon1_rad = math.radians(lon1_f)
        lat2_rad = math.radians(lat2_f)
        lon2_rad = math.radians(lon2_f)

        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) *
            math.cos(lat2_rad) *
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c

        return Decimal(str(round(distance_km, 2)))

    @staticmethod
    def manhattan_distance(
        lat1: Decimal,
        lon1: Decimal,
        lat2: Decimal,
        lon2: Decimal
    ) -> Decimal:
        """
        Calculate Manhattan distance (for comparison).

        Args:
            lat1: Latitude of point 1
            lon1: Longitude of point 1
            lat2: Latitude of point 2
            lon2: Longitude of point 2

        Returns:
            Distance in kilometers (approximate)
        """
        lat1_f = float(lat1)
        lon1_f = float(lon1)
        lat2_f = float(lat2)
        lon2_f = float(lon2)

        # Approximate conversion (111 km per degree)
        dlat = abs(lat2_f - lat1_f) * 111
        dlon = abs(lon2_f - lon1_f) * 111 * math.cos(math.radians(lat1_f))

        distance_km = dlat + dlon

        return Decimal(str(round(distance_km, 2)))

    @staticmethod
    def get_parecer_type(distance_km: Decimal) -> str:
        """
        Determine parecer type based on distance.

        Args:
            distance_km: Distance in kilometers

        Returns:
            Parecer type (PROXIMAL, MODERADO, DISTANTE, MUITO_DISTANTE)
        """
        dist = float(distance_km)

        if dist <= 5:
            return "PROXIMAL"
        elif dist <= 20:
            return "MODERADO"
        elif dist <= 50:
            return "DISTANTE"
        else:
            return "MUITO_DISTANTE"

    @staticmethod
    def get_parecer_text(
        distance_km: Decimal,
        endereco_origem: str,
        endereco_destino: str
    ) -> str:
        """
        Generate parecer text based on distance and addresses.

        Args:
            distance_km: Distance in kilometers
            endereco_origem: Origin address
            endereco_destino: Destination address

        Returns:
            Generated parecer text
        """
        tipo = DistanceCalculator.get_parecer_type(distance_km)
        dist = float(distance_km)

        if tipo == "PROXIMAL":
            return (
                f"Análise de Geolocalização: Os endereços estão muito próximos, "
                f"a uma distância de apenas {dist:.2f} km. "
                f"Endereço de origem: {endereco_origem}. "
                f"Endereço de destino: {endereco_destino}. "
                f"Parecer: APROVADO - Distâncias compatíveis com documentação."
            )
        elif tipo == "MODERADO":
            return (
                f"Análise de Geolocalização: Os endereços apresentam distância moderada "
                f"de {dist:.2f} km. "
                f"Endereço de origem: {endereco_origem}. "
                f"Endereço de destino: {endereco_destino}. "
                f"Parecer: ATENÇÃO - Verificar justificativas para variação de endereço."
            )
        elif tipo == "DISTANTE":
            return (
                f"Análise de Geolocalização: Os endereços estão significativamente afastados, "
                f"a {dist:.2f} km de distância. "
                f"Endereço de origem: {endereco_origem}. "
                f"Endereço de destino: {endereco_destino}. "
                f"Parecer: ANÁLISE RECOMENDADA - Grande variação geográfica detectada."
            )
        else:  # MUITO_DISTANTE
            return (
                f"Análise de Geolocalização: Os endereços estão muito distantes, "
                f"a {dist:.2f} km de distância. "
                f"Endereço de origem: {endereco_origem}. "
                f"Endereço de destino: {endereco_destino}. "
                f"Parecer: RISCO ALTO - Necessária investigação detalhada da documentação."
            )

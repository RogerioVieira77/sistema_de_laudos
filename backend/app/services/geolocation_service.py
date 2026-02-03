"""
Geolocalização Service - Business logic for geolocation analysis
"""

from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import datetime

from app.repositories import (
    ContratoRepository,
    BureauRepository,
    PareceRepository,
    LogsAnaliseRepository
)
from app.utils import DistanceCalculator, NominatimClient
from app.schemas import GeolocationAnalysisResponse
from .base_service import BaseService


class GeolocalizacaoService(BaseService):
    """Service for geolocation analysis"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.contrato_repo = ContratoRepository(db)
        self.bureau_repo = BureauRepository(db)
        self.parecer_repo = PareceRepository(db)
        self.logs_repo = LogsAnaliseRepository(db)
        self.distance_calc = DistanceCalculator()
        self.nominatim = NominatimClient()

    def analisar_geolocalizacao(
        self,
        contrato_id: int,
        usuario_id: int
    ) -> Optional[GeolocationAnalysisResponse]:
        """
        Analyze geolocation of a contract.

        Args:
            contrato_id: Contract ID
            usuario_id: User ID performing analysis

        Returns:
            Geolocation analysis response or None
        """
        try:
            # Get contract
            contrato = self.contrato_repo.get_by_id(contrato_id)
            if not contrato:
                raise ValueError(f"Contract {contrato_id} not found")

            # Get bureau data
            bureau = self.bureau_repo.get_by_contrato(contrato_id)
            if not bureau:
                raise ValueError(f"Bureau data for contract {contrato_id} not found")

            # Validate coordinates
            if (not contrato.latitude or not contrato.longitude or
                not bureau.latitude or not bureau.longitude):
                raise ValueError("Missing coordinates for geolocation analysis")

            # Calculate distance
            distance_km = self.distance_calc.haversine(
                contrato.latitude,
                contrato.longitude,
                bureau.latitude,
                bureau.longitude
            )

            # Get parecer type
            tipo_parecer = self.distance_calc.get_parecer_type(distance_km)

            # Generate parecer text
            texto_parecer = self.distance_calc.get_parecer_text(
                distance_km,
                contrato.endereco_assinatura or "Endereço contrato",
                bureau.logradouro or "Endereço bureau"
            )

            # Get addresses
            endereco_origem = contrato.endereco_assinatura or "Sem endereço"
            endereco_destino = bureau.logradouro or "Sem endereço"

            # Create analysis response
            analysis = GeolocationAnalysisResponse(
                contrato_id=contrato_id,
                endereco_origem=endereco_origem,
                endereco_destino=endereco_destino,
                latitude_origem=contrato.latitude,
                longitude_origem=contrato.longitude,
                latitude_destino=bureau.latitude,
                longitude_destino=bureau.longitude,
                distancia_km=distance_km,
                tipo_parecer=tipo_parecer,
                texto_parecer=texto_parecer,
                timestamp=datetime.utcnow()
            )

            # Update contract status
            self.contrato_repo.update_status(contrato_id, "CONCLUIDO")

            # Log success
            self.logs_repo.create({
                "contrato_id": contrato_id,
                "usuario_id": usuario_id,
                "tipo_evento": "SUCESSO",
                "mensagem": f"Análise de geolocalização concluída. Distância: {distance_km}km. Tipo: {tipo_parecer}",
            })

            self.log_info(f"Geolocation analysis completed for contract {contrato_id}")

            return analysis

        except Exception as e:
            # Log error
            self.logs_repo.create({
                "contrato_id": contrato_id,
                "usuario_id": usuario_id,
                "tipo_evento": "ERRO",
                "mensagem": f"Erro na análise de geolocalização",
                "detalhes": str(e)
            })
            self.log_error(f"Error analyzing geolocation for contract {contrato_id}", e)
            raise

    def calcular_distancia(
        self,
        lat1: Decimal,
        lon1: Decimal,
        lat2: Decimal,
        lon2: Decimal
    ) -> Decimal:
        """
        Calculate distance between two coordinates.

        Args:
            lat1: Latitude 1
            lon1: Longitude 1
            lat2: Latitude 2
            lon2: Longitude 2

        Returns:
            Distance in kilometers
        """
        return self.distance_calc.haversine(lat1, lon1, lat2, lon2)

    def geocodificar_endereco(
        self,
        endereco: str
    ) -> Optional[tuple[Decimal, Decimal, str]]:
        """
        Geocode an address.

        Args:
            endereco: Address string

        Returns:
            Tuple of (latitude, longitude, formatted_address) or None
        """
        try:
            result = self.nominatim.geocode_sync(endereco)
            if result:
                self.log_info(f"Geocoded address: {endereco}")
            return result
        except Exception as e:
            self.log_error(f"Error geocoding address {endereco}", e)
            return None

    def reverse_geocodificar(
        self,
        latitude: Decimal,
        longitude: Decimal
    ) -> Optional[str]:
        """
        Reverse geocode coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Address string or None
        """
        try:
            address = self.nominatim.reverse_geocode_sync(latitude, longitude)
            if address:
                self.log_info(f"Reverse geocoded: {latitude}, {longitude}")
            return address
        except Exception as e:
            self.log_error(f"Error reverse geocoding {latitude}, {longitude}", e)
            return None

    def obter_parecer_type(self, distance_km: Decimal) -> str:
        """
        Get parecer type for a distance.

        Args:
            distance_km: Distance in kilometers

        Returns:
            Parecer type
        """
        return self.distance_calc.get_parecer_type(distance_km)

    def get_estatisticas_geolocalizacao(self) -> dict:
        """
        Get geolocation statistics.

        Returns:
            Statistics dictionary
        """
        return self.parecer_repo.get_statistics()

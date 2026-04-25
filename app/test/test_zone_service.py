import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.application.zone_service import ZoneService
from app.infrastructure.models import ZoneAnalytics, TransformationLog


class TestZoneService:
    """Suite de pruebas unitarias para ZoneService"""
    
    def test_get_zones_summary_success(self, mock_zone_repository, db_session):
        """
        TC-ZS-001: Verificar que get_zones_summary retorna un resumen de zonas
        con información válida.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
    
    
    def test_get_zones_summary_has_correct_structure(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-002: Verificar que cada zona en el resumen tiene la estructura
        correcta: nombre y cantidad de registros.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        for zone in result:
            assert "name" in zone
            assert "record_count" in zone
            assert isinstance(zone["name"], str)
            assert isinstance(zone["record_count"], int)
    
    
    def test_get_zones_summary_returns_expected_zones(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-003: Verificar que el resumen contiene las zonas esperadas.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        zone_names = [zone["name"] for zone in result]
        assert "BOGOTA" in zone_names
        assert "MEDELLIN" in zone_names
        assert "CALI" in zone_names
    
    
    def test_get_zones_summary_calls_repository(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-004: Verificar que se llama correctamente al repositorio.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        service.get_zones_summary(db_session)
        
        # Assert
        mock_zone_repository.get_zone_summaries.assert_called_once_with(db_session)
    
    
    def test_get_zones_summary_empty_result(self, db_session):
        """
        TC-ZS-005: Verificar que retorna lista vacía cuando no hay zonas.
        """
        # Crear un mock que retorna lista vacía
        empty_repo = Mock()
        empty_repo.get_zone_summaries = Mock(return_value=[])
        
        service = ZoneService(zone_repository=empty_repo)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        assert result == []
        assert isinstance(result, list)
    
    
    def test_get_zones_summary_correct_record_counts(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-006: Verificar que los conteos de registros son correctos.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        zone_dict = {zone["name"]: zone["record_count"] for zone in result}
        assert zone_dict["BOGOTA"] == 5
        assert zone_dict["MEDELLIN"] == 3
        assert zone_dict["CALI"] == 2
    
    
    def test_zone_service_initialization(self, mock_zone_repository):
        """
        TC-ZS-007: Verificar que ZoneService se inicializa correctamente
        con el repositorio inyectado.
        """
        # Act
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Assert
        assert service.zone_repository is not None
        assert service.zone_repository == mock_zone_repository
    
    
    def test_get_zones_summary_maintains_data_integrity(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-008: Verificar que los datos del resumen no son modificados
        durante la devolución.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result1 = service.get_zones_summary(db_session)
        result2 = service.get_zones_summary(db_session)
        
        # Assert
        assert result1 == result2
        assert len(result1) == len(result2)
    
    
    def test_get_zones_summary_returns_list_not_dict(
        self, mock_zone_repository, db_session
    ):
        """
        TC-ZS-009: Verificar que siempre retorna una lista, no un diccionario.
        """
        service = ZoneService(zone_repository=mock_zone_repository)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        assert isinstance(result, list)
        assert not isinstance(result, dict)
    
    
    def test_get_zones_summary_with_large_record_counts(self, db_session):
        """
        TC-ZS-010: Verificar que se maneja correctamente con conteos grandes
        de registros.
        """
        large_repo = Mock()
        large_repo.get_zone_summaries = Mock(
            return_value=[
                {"name": "LARGE_ZONE_1", "record_count": 1000000},
                {"name": "LARGE_ZONE_2", "record_count": 999999},
            ]
        )
        
        service = ZoneService(zone_repository=large_repo)
        
        # Act
        result = service.get_zones_summary(db_session)
        
        # Assert
        assert len(result) == 2
        assert all(zone["record_count"] > 0 for zone in result)

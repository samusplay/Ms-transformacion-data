import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.models import Base, TransformationLog, ZoneAnalytics
from app.schemas.ingestion import TestIngestRequest
from app.schemas.transform import TransformMetricsResponse
from app.schemas.base_response import StandardResponse


class TestSchemas:
    """Suite de pruebas para validación de schemas/modelos"""
    
    def test_test_ingest_request_valid(self):
        """
        TC-SCH-001: Verificar que TestIngestRequest valida correctamente.
        """
        # Act
        request = TestIngestRequest(texto="test data")
        
        # Assert
        assert request.texto == "test data"
    
    
    def test_test_ingest_request_empty_texto_invalid(self):
        """
        TC-SCH-002: Verificar que TestIngestRequest puede tener texto vacío
        (Pydantic no lo valida por defecto).
        """
        # Act
        request = TestIngestRequest(texto="")
        
        # Assert
        assert request.texto == ""
    
    
    def test_transform_metrics_response_valid(self):
        """
        TC-SCH-003: Verificar que TransformMetricsResponse se crea correctamente.
        """
        # Act
        response = TransformMetricsResponse(
            transformed_records=100,
            execution_time_ms=1500.0
        )
        
        # Assert
        assert response.transformed_records == 100
        assert response.execution_time_ms == 1500.0
    
    
    def test_standard_response_success(self):
        """
        TC-SCH-004: Verificar que StandardResponse se crea correctamente
        en caso exitoso.
        """
        # Act
        response = StandardResponse(
            success=True,
            data={"status": "OK"},
            error=None,
            trace_id="trace-123"
        )
        
        # Assert
        assert response.success is True
        assert response.data is not None
        assert response.error is None
    
    
    def test_standard_response_error(self):
        """
        TC-SCH-005: Verificar que StandardResponse se crea correctamente
        en caso de error.
        """
        # Act
        response = StandardResponse(
            success=False,
            data=None,
            error="Error message",
            trace_id="trace-123"
        )
        
        # Assert
        assert response.success is False
        assert response.data is None
        assert response.error == "Error message"


class TestModels:
    """Suite de pruebas para modelos ORM"""
    
    @pytest.fixture
    def db_engine(self):
        """Crea una BD de prueba en memoria"""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        return engine
    
    
    @pytest.fixture
    def db_session(self, db_engine):
        """Crea una sesión de BD para pruebas"""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = SessionLocal()
        yield session
        session.close()
    
    
    def test_transformation_log_creation(self, db_session):
        """
        TC-MOD-001: Verificar que se crea correctamente un TransformationLog.
        """
        # Act
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Assert
        saved_log = db_session.query(TransformationLog).first()
        assert saved_log is not None
        assert saved_log.dataset_load_id == "dataset-001"
        assert saved_log.transformed_records == 100
    
    
    def test_zone_analytics_creation(self, db_session):
        """
        TC-MOD-002: Verificar que se crea correctamente un ZoneAnalytics.
        """
        # Primero crear un TransformationLog
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Act
        zone = ZoneAnalytics(
            transformation_log_id=log.id,
            zone_code="Z001",
            zone_name="BOGOTA",
            region="CUNDINAMARCA",
            metrics={"population": 8000000}
        )
        db_session.add(zone)
        db_session.commit()
        
        # Assert
        saved_zone = db_session.query(ZoneAnalytics).first()
        assert saved_zone is not None
        assert saved_zone.zone_code == "Z001"
        assert saved_zone.zone_name == "BOGOTA"
    
    
    def test_zone_analytics_relationship_with_log(self, db_session):
        """
        TC-MOD-003: Verificar que ZoneAnalytics se relaciona correctamente
        con TransformationLog.
        """
        # Crear TransformationLog
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Crear ZoneAnalytics
        zone = ZoneAnalytics(
            transformation_log_id=log.id,
            zone_code="Z001",
            zone_name="BOGOTA"
        )
        db_session.add(zone)
        db_session.commit()
        
        # Act
        retrieved_zone = db_session.query(ZoneAnalytics).first()
        
        # Assert
        assert retrieved_zone.transformation_log_id == log.id
    
    
    def test_multiple_zones_per_transformation_log(self, db_session):
        """
        TC-MOD-004: Verificar que múltiples zonas pueden asociarse a un
        TransformationLog.
        """
        # Crear TransformationLog
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Crear múltiples zonas
        zones = [
            ZoneAnalytics(
                transformation_log_id=log.id,
                zone_code="Z001",
                zone_name="BOGOTA"
            ),
            ZoneAnalytics(
                transformation_log_id=log.id,
                zone_code="Z002",
                zone_name="MEDELLIN"
            ),
            ZoneAnalytics(
                transformation_log_id=log.id,
                zone_code="Z003",
                zone_name="CALI"
            )
        ]
        
        for zone in zones:
            db_session.add(zone)
        db_session.commit()
        
        # Act
        all_zones = db_session.query(ZoneAnalytics).filter_by(
            transformation_log_id=log.id
        ).all()
        
        # Assert
        assert len(all_zones) == 3
    
    
    def test_transformation_log_id_auto_increment(self, db_session):
        """
        TC-MOD-005: Verificar que los IDs de TransformationLog se auto-incrementan.
        """
        # Crear múltiples logs
        log1 = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log1)
        db_session.commit()
        
        log2 = TransformationLog(
            dataset_load_id="dataset-002",
            transformed_records=200,
            execution_time_ms=2000.0
        )
        db_session.add(log2)
        db_session.commit()
        
        # Assert
        assert log1.id is not None
        assert log2.id is not None
        assert log2.id > log1.id
    
    
    def test_zone_analytics_metrics_dict_nullable(self, db_session):
        """
        TC-MOD-006: Verificar que metrics puede ser None.
        """
        # Crear TransformationLog
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Act
        zone = ZoneAnalytics(
            transformation_log_id=log.id,
            zone_code="Z001",
            zone_name="BOGOTA",
            metrics=None
        )
        db_session.add(zone)
        db_session.commit()
        
        # Assert
        saved_zone = db_session.query(ZoneAnalytics).first()
        assert saved_zone.metrics is None
    
    
    def test_zone_analytics_with_metrics_dict(self, db_session):
        """
        TC-MOD-007: Verificar que metrics se guarda correctamente.
        """
        # Crear TransformationLog
        log = TransformationLog(
            dataset_load_id="dataset-001",
            transformed_records=100,
            execution_time_ms=1500.0
        )
        db_session.add(log)
        db_session.commit()
        
        # Act
        metrics = {
            "population": 8000000,
            "area": 1587,
            "density": 5049
        }
        zone = ZoneAnalytics(
            transformation_log_id=log.id,
            zone_code="Z001",
            zone_name="BOGOTA",
            metrics=metrics
        )
        db_session.add(zone)
        db_session.commit()
        
        # Assert
        saved_zone = db_session.query(ZoneAnalytics).first()
        assert saved_zone.metrics["population"] == 8000000

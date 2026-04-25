# Suite de Pruebas Unitarias - Ms-transformacion-data

## Descripción General

Este directorio contiene un conjunto completo de pruebas unitarias para el microservicio **Ms-transformacion-data**. Las pruebas están organizadas por componente y cubren:

- **Servicios de Aplicación** (TransformService, ZoneService)
- **Repositorios e Implementaciones** (IngestionRepositoryImpl)
- **Routers/Endpoints** (TransformRouter, ZoneRouter)
- **Modelos y Schemas** (ORM models, Pydantic schemas)
- **Aplicación Principal** (FastAPI app initialization)

---

## Estructura de Archivos

```
app/test/
├── __init__.py
├── conftest.py                      # Fixtures compartidas y configuración
├── test_transform_service.py        # Pruebas de TransformService (10 tests)
├── test_zone_service.py             # Pruebas de ZoneService (10 tests)
├── test_ingestion_repository.py     # Pruebas de IngestionRepositoryImpl (10 tests)
├── test_routers.py                  # Pruebas de endpoints (20 tests)
├── test_models_schemas.py           # Pruebas de modelos y schemas (10 tests)
└── test_main.py                     # Pruebas de la app principal (10 tests)

pytest.ini                           # Configuración de pytest
```

---

## Cobertura de Pruebas

### 1. TransformService (10 tests)
- `TC-TS-001`: test_test_connection_to_ingestion_success
- `TC-TS-002`: test_test_connection_to_ingestion_creates_valid_request
- `TC-TS-003`: test_process_dataset_success
- `TC-TS-004`: test_process_dataset_creates_transformation_log
- `TC-TS-005`: test_process_dataset_empty_data_raises_error
- `TC-TS-006`: test_process_dataset_cleans_text_columns
- `TC-TS-007`: test_process_dataset_detects_zone_column
- `TC-TS-008`: test_process_dataset_handles_numeric_columns
- `TC-TS-009`: test_process_dataset_persists_zone_analytics
- `TC-TS-010`: test_process_dataset_execution_time_recorded

### 2. ZoneService (10 tests)
- `TC-ZS-001`: test_get_zones_summary_success
- `TC-ZS-002`: test_get_zones_summary_has_correct_structure
- `TC-ZS-003`: test_get_zones_summary_returns_expected_zones
- `TC-ZS-004`: test_get_zones_summary_calls_repository
- `TC-ZS-005`: test_get_zones_summary_empty_result
- `TC-ZS-006`: test_get_zones_summary_correct_record_counts
- `TC-ZS-007`: test_zone_service_initialization
- `TC-ZS-008`: test_get_zones_summary_maintains_data_integrity
- `TC-ZS-009`: test_get_zones_summary_returns_list_not_dict
- `TC-ZS-010`: test_get_zones_summary_with_large_record_counts

### 3. IngestionRepositoryImpl (10 tests)
- `TC-IR-001`: test_send_test_data_success
- `TC-IR-002`: test_send_test_data_correct_url
- `TC-IR-003`: test_send_test_data_sends_request_body
- `TC-IR-004`: test_fetch_raw_data_success
- `TC-IR-005`: test_fetch_raw_data_correct_url
- `TC-IR-006`: test_initialization_with_missing_env_var
- `TC-IR-007`: test_initialization_with_valid_env_var
- `TC-IR-008`: test_initialization_strips_trailing_slash
- `TC-IR-009`: test_fetch_raw_data_http_error
- `TC-IR-010`: test_send_test_data_with_timeout

### 4. Transform Router (10 tests)
- `TC-TR-001`: test_health_check_endpoint
- `TC-TR-002`: test_health_check_has_trace_id
- `TC-TR-003`: test_health_check_response_structure
- `TC-TR-004`: test_process_dataset_endpoint_not_found
- `TC-TR-005`: test_test_ingestion_endpoint_invalid_request
- `TC-TR-006`: test_test_ingestion_endpoint_with_valid_data
- `TC-TR-007`: test_process_dataset_with_empty_dataset_id
- `TC-TR-008`: test_transform_endpoint_returns_standard_response
- `TC-TR-009`: test_health_check_multiple_calls_have_different_trace_ids
- `TC-TR-010`: test_health_check_content_type

### 5. Zone Router (10 tests)
- `TC-ZR-001`: test_get_zones_endpoint_exists
- `TC-ZR-002`: test_get_zones_returns_success_true
- `TC-ZR-003`: test_get_zones_has_zones_array
- `TC-ZR-004`: test_get_zones_has_error_null
- `TC-ZR-005`: test_get_zones_response_structure
- `TC-ZR-006`: test_get_zones_with_query_parameters
- `TC-ZR-007`: test_get_zones_returns_json
- `TC-ZR-008`: test_get_zones_multiple_calls_consistency
- `TC-ZR-009`: test_get_zones_empty_zones_array_valid
- `TC-ZR-010`: test_get_zones_zone_items_structure

### 6. Schemas y Modelos (10 tests)
- `TC-SCH-001`: test_test_ingest_request_valid
- `TC-SCH-002`: test_test_ingest_request_empty_texto_invalid
- `TC-SCH-003`: test_transform_metrics_response_valid
- `TC-SCH-004`: test_standard_response_success
- `TC-SCH-005`: test_standard_response_error
- `TC-MOD-001`: test_transformation_log_creation
- `TC-MOD-002`: test_zone_analytics_creation
- `TC-MOD-003`: test_zone_analytics_relationship_with_log
- `TC-MOD-004`: test_multiple_zones_per_transformation_log
- `TC-MOD-005`: test_transformation_log_id_auto_increment

### 7. Main/App (10 tests)
- `TC-MAIN-001`: test_app_initialization
- `TC-MAIN-002`: test_app_has_description
- `TC-MAIN-003`: test_app_includes_routers
- `TC-MAIN-004`: test_app_lifespan_context_manager
- `TC-MAIN-005`: test_health_endpoint_available_on_startup
- `TC-MAIN-006`: test_zones_endpoint_available_on_startup
- `TC-MAIN-007`: test_app_openapi_docs_available
- `TC-MAIN-008`: test_app_routes_count_is_positive
- `TC-MAIN-009`: test_app_cors_configuration
- `TC-MAIN-010`: test_app_error_handlers_configured

**Total: 70+ Pruebas Unitarias**

---

## Cómo Ejecutar las Pruebas

### Ejecutar todas las pruebas
```bash
pytest
```

### Ejecutar pruebas de un archivo específico
```bash
pytest app/test/test_transform_service.py -v
```

### Ejecutar una prueba específica
```bash
pytest app/test/test_transform_service.py::TestTransformService::test_process_dataset_success -v
```

### Ejecutar pruebas con cobertura
```bash
pytest --cov=app app/test/
```

### Ejecutar solo pruebas async
```bash
pytest -m asyncio
```

### Ver más detalles de la ejecución
```bash
pytest -v --tb=long
```

### Ejecutar pruebas en paralelo (requiere pytest-xdist)
```bash
pip install pytest-xdist
pytest -n auto
```

---

## Dependencias de Testing

Las siguientes librerías se usan para las pruebas:

```
pytest==8.0.0              # Framework de testing
pytest-asyncio             # Support para funciones async
pytest-mock                # Mocking simplificado
fastapi                    # TestClient para pruebas de endpoints
sqlalchemy                 # ORM y testing de BD
```

---

## Fixtures Disponibles (conftest.py)

### `db_session`
Base de datos SQLite en memoria para pruebas de persistencia.

### `mock_ingestion_repository`
Mock del IngestionRepository con métodos async preconfigurados.

### `mock_zone_repository`
Mock del ZoneRepository con métodos preconfigurados.

### `mock_analytics_client`
Mock del cliente de Analytics.

### `sample_dataset_records`
Datos de prueba para registros transformados.

### `sample_dataframe`
DataFrame de prueba con datos limpios.

### `invalid_dataframe_empty_zone`
DataFrame con zona vacía para validaciones.

### `invalid_dataframe_no_zone`
DataFrame sin columna de zona para manejo de errores.

---

## Estrategia de Testing

### Unit Tests
Cada función se prueba de forma aislada con:
- Mocks de dependencias externas
- Entradas válidas e inválidas
- Casos edge case
- Validación de estructura de respuestas

### Integration Tests
Se prueban interacciones entre componentes:
- Flujo completo de transformación
- Persistencia en BD
- Llamadas HTTP (mockeadas)

### Naming Convention
Cada prueba sigue el patrón: `test_{funcion}_{escenario}`

Ejemplo: `test_process_dataset_empty_data_raises_error`

---

## Casos de Uso Cubiertos

✅ Conexión exitosa a ms-ingestion
✅ Procesamiento completo de dataset
✅ Detección automática de columnas de zona
✅ Limpieza de datos (texto, numéricos)
✅ Persistencia en BD
✅ Manejo de errores
✅ Validación de schemas
✅ Endpoints HTTP
✅ Relationships ORM
✅ Conteos y agregaciones

---

## Notas Importantes

1. **Mocking Externo**: Las llamadas HTTP a otros microservicios están mockeadas para independencia.

2. **BD en Memoria**: Las pruebas usan SQLite en memoria para velocidad y aislamiento.

3. **Async/Await**: Las pruebas async usan pytest-asyncio. Usa `@pytest.mark.asyncio`.

4. **Isolamiento**: Cada prueba es independiente y no afecta a otras.

5. **Documentación**: Cada prueba tiene docstring con ID único (TC-XXX-YYY).

---

## Próximos Pasos (Mejoras Futuras)

- [ ] Agregar pruebas de performance
- [ ] Aumentar cobertura a 90%+
- [ ] Pruebas de carga con locust
- [ ] Pruebas de concurrencia
- [ ] Pruebas e2e con TestContainers
- [ ] Mutation testing

---

## Contacto / Soporte

Para preguntas sobre las pruebas, revisar la documentación en cada archivo o consultar al equipo de desarrollo.

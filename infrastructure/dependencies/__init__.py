"""Dependency injection module.

This module provides all application dependencies organized by domain.
All dependencies are re-exported here for backwards compatibility.

Usage:
    from infrastructure.dependencies import get_user_repository, get_create_user_handler

Or import from specific modules:
    from infrastructure.dependencies.users import get_create_user_handler
    from infrastructure.dependencies.repositories import get_user_repository
"""

# Breed dependencies
from infrastructure.dependencies.breeds import (
    get_breed_query_service,
    get_create_breed_handler,
    get_delete_breed_handler,
    get_update_breed_handler,
)

# Database dependencies
from infrastructure.dependencies.database import get_db_session

# Event dependencies
from infrastructure.dependencies.events import (
    create_test_event_bus,
    create_test_event_publisher,
    get_event_bus,
    get_event_publisher,
    reset_event_bus,
)

# Mapper dependencies
from infrastructure.dependencies.mappers import (
    get_breed_mapper,
    get_gene_mapper,
    get_morph_gene_mapping_mapper,
    get_morphology_mapper,
    get_pet_mapper,
    get_pet_record_mapper,
    get_user_mapper,
)

# Pet record dependencies
from infrastructure.dependencies.pet_records import (
    get_create_pet_record_handler,
    get_delete_pet_record_handler,
    get_pet_record_query_service,
    get_update_pet_record_handler,
)

# Pet dependencies
from infrastructure.dependencies.pets import (
    get_create_pet_handler,
    get_delete_pet_handler,
    get_pet_domain_service,
    get_pet_query_service,
    get_transfer_pet_ownership_handler,
    get_update_pet_handler,
)

# Repository dependencies
from infrastructure.dependencies.repositories import (
    get_breed_repository,
    get_morphology_repository,
    get_pet_record_repository,
    get_pet_repository,
    get_pet_search_repository,
    get_user_repository,
)

# Security dependencies
from infrastructure.dependencies.security import (
    get_password_hasher,
    get_password_policy,
)

# User dependencies
from infrastructure.dependencies.users import (
    get_create_user_handler,
    get_delete_user_handler,
    get_update_password_handler,
    get_update_user_handler,
    get_user_query_service,
)

__all__ = [
    # Database
    "get_db_session",
    # Events
    "get_event_bus",
    "get_event_publisher",
    "reset_event_bus",
    "create_test_event_bus",
    "create_test_event_publisher",
    # Security
    "get_password_hasher",
    "get_password_policy",
    # Mappers
    "get_user_mapper",
    "get_pet_mapper",
    "get_breed_mapper",
    "get_gene_mapper",
    "get_morph_gene_mapping_mapper",
    "get_morphology_mapper",
    "get_pet_record_mapper",
    # Repositories
    "get_user_repository",
    "get_pet_repository",
    "get_pet_search_repository",
    "get_breed_repository",
    "get_morphology_repository",
    "get_pet_record_repository",
    # User handlers and services
    "get_create_user_handler",
    "get_update_user_handler",
    "get_update_password_handler",
    "get_delete_user_handler",
    "get_user_query_service",
    # Pet handlers and services
    "get_pet_domain_service",
    "get_create_pet_handler",
    "get_transfer_pet_ownership_handler",
    "get_update_pet_handler",
    "get_delete_pet_handler",
    "get_pet_query_service",
    # Breed handlers and services
    "get_create_breed_handler",
    "get_update_breed_handler",
    "get_delete_breed_handler",
    "get_breed_query_service",
    # Pet record handlers and services
    "get_create_pet_record_handler",
    "get_update_pet_record_handler",
    "get_delete_pet_record_handler",
    "get_pet_record_query_service",
]


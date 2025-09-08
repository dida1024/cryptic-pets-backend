"""Demo script to test domain events functionality."""

import asyncio
from datetime import datetime

from domain.common.events import get_event_bus
from domain.pets.events import PetCreatedEvent, PetOwnershipChangedEvent
from domain.users.events import UserCreatedEvent
from infrastructure.events.event_registry import register_all_event_handlers


async def demo_domain_events():
    """Demonstrate domain events functionality."""
    print("=== Domain Events Demo ===")
    
    # 注册所有事件处理器
    register_all_event_handlers()
    print("✓ Event handlers registered")
    
    # 获取事件总线
    event_bus = get_event_bus()
    
    # 创建一些测试事件
    print("\n--- Creating and publishing events ---")
    
    # 用户创建事件
    user_event = UserCreatedEvent(
        username="test_user",
        email="test@example.com"
    )
    print(f"Created user event: {user_event.event_type}")
    await event_bus.publish(user_event)
    
    # 宠物创建事件
    pet_event = PetCreatedEvent(
        pet_id="pet_123",
        owner_id="user_456",
        breed_id="breed_789"
    )
    print(f"Created pet event: {pet_event.event_type}")
    await event_bus.publish(pet_event)
    
    # 宠物所有权变更事件
    ownership_event = PetOwnershipChangedEvent(
        pet_id="pet_123",
        old_owner_id="user_456",
        new_owner_id="user_789"
    )
    print(f"Created ownership change event: {ownership_event.event_type}")
    await event_bus.publish(ownership_event)
    
    print("\n--- All events published successfully ---")
    print("Check the logs above to see all event handlers responding to the events.")


if __name__ == "__main__":
    asyncio.run(demo_domain_events())
# 5. Логическая структура (Диаграмма классов)

```mermaid
classDiagram
    class Entity {
        +id: int
        +name: string
        +components: Map~Type, Component~
    }

    class Component {
        <<interface>>
    }

    class PositionComponent { +x: int; +y: int }
    class RenderableComponent { +spriteId: string; +layer: int }
    class StatsComponent { +hp: int; +maxHp: int; +radiation: int }
    class InventoryComponent { +items: List~Entity~ }
    class EquipmentComponent { +artifactSlots: List~Entity~ }
    class BehaviorComponent { +type: BehaviorType }
    class AnomalyComponent { +effect: EffectStrategy; +radius: int }
    class ArtifactComponent { +properties: List~ArtifactProperty~ }

    Entity "1" *-- "many" Component
    Component <|.. PositionComponent
    Component <|.. RenderableComponent
    Component <|.. StatsComponent
    Component <|.. InventoryComponent
    Component <|.. EquipmentComponent
    Component <|.. BehaviorComponent
    Component <|.. AnomalyComponent
    Component <|.. ArtifactComponent

    class Game {
        +run()
    }
    class World {
        +entities: List~Entity~
        +currentSector: Sector
        +generateSector()
    }
    class System {
        <<interface>>
        +update(world: World)
    }
    class MovementSystem { +update(world) }
    class MonsterSystem { +update(world) }
    class AnomalySystem { +update(world) }
    class RadiationSystem { +update(world) }

    Game "1" o-- "1" World
    World "1" o-- "many" System

    System <|.. MovementSystem
    System <|.. MonsterSystem
    System <|.. AnomalySystem
    System <|.. RadiationSystem
```

### Описание ключевых классов и компонентов

| Класс/Компонент | Описание |
|:---|:---|
| **Entity** | Универсальный игровой объект (сталкер, мутант, предмет). Является контейнером для компонентов. |
| **Component** | Контейнер для данных, определяющий один аспект `Entity`. |
| **RenderableComponent** | Хранит `spriteId` (идентификатор спрайта для отрисовки, например `"player_idle.png"`) и `layer` (слой отрисовки, чтобы персонаж рисовался поверх пола). |
| **BehaviorComponent** | Определяет тип поведения сущности с помощью перечисления (enum), например: `AGGRESSIVE` (двигаться к игроку), `COWARDLY` (убегать от игрока). |
| **System** | Класс без состояния (stateless), который содержит всю игровую логику. Каждая система обрабатывает `Entity` с определенным набором компонентов. |
| **MonsterSystem** | Система, реализующая простую логику поведения для `Entity` c `BehaviorComponent`. Для типа `AGGRESSIVE` генерирует команду движения в сторону игрока, если тот в зоне видимости. |
```

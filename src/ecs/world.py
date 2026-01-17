class World:
    def __init__(self):
        self.next_entity_id = 0
        self.entities = {} # id -> set(Component Types)
        self.components = {} # Type -> {id -> Component}
        self.systems = []
        self.texture_registry = ["EMPTY", "DEFAULT_WALL"] # 0=Empty, 1=Default

    def create_entity(self):
        entity_id = self.next_entity_id
        self.entities[entity_id] = {}
        self.next_entity_id += 1
        return entity_id

    def add_component(self, entity_id, component):
        comp_type = type(component)
        self.entities[entity_id][comp_type] = component

    def get_component(self, entity_id, component_type):
        return self.entities[entity_id].get(component_type)

    def has_component(self, entity_id, component_type):
        return component_type in self.entities[entity_id]

    def remove_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def add_system(self, system_func):
        self.systems.append(system_func)

    def update(self, dt, engine):
        for system in self.systems:
            system(self, engine, dt)

    def get_entities_with(self, *component_types):
        """Yield entities that have all specified components."""
        for entity_id, components in self.entities.items():
            if all(ct in components for ct in component_types):
                yield entity_id

    def init_map(self, width, height, vertexes, linedefs, sidedefs):
        self.map_width = width
        self.map_height = height
        self.world_map = [[0 for _ in range(height)] for _ in range(width)]
        self.vertexes = vertexes
        self.linedefs = linedefs
        self.sidedefs = sidedefs
        self.map_bounds = None
        self.linedefs = linedefs if linedefs else []

    def create_wall(self, x1, y1, x2, y2, texture_id=1):
        from src.ecs.components import Wall
        entity_id = self.create_entity()
        self.add_component(entity_id, Wall(x1, y1, x2, y2, texture_id))
        return entity_id

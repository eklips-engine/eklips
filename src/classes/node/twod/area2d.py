## Import inherited
from classes.node.twod.physicsbody2d import PhysicsBody2D
from classes.node.gui.canvasitem import CanvasItem

## Import engine singleton and others
import pyglet as pg
import classes.singleton as engine

## Node
class Area2D(PhysicsBody2D):
    """
    ## An Area node.
    
    This node has a rectangular hitbox, which won't stop if collided with any bodies. Useful for things like triggers.
    """

    def _check_overlap(self, rect1, rect2):
        # Use AABB
        return (
            rect1.x < rect2.x + rect2.scale_x and
            rect1.x + rect1.scale_x > rect2.x and
            rect1.y < rect2.x + rect2.scale_x and
            rect1.y + rect1.scale_u > rect2.y
        )

    def __init__(self, data=CanvasItem.node_base_data, parent=None):
        super().__init__(data,parent)
        self._phys_init()
        self.id                             = f"{self.to_string()}NodeColA{self.w*self.h}"
        self.scene.nodes_collision[self.id] = self
    
    def colliderect(self, rect): return self._check_overlap(self, rect)

    def collidelist(self, rect_list):
        id = 0
        for i in rect_list:
            if self._check_overlap(self, i): return id
            else: id+=1
        return -1

    def collidelistall(self, rect_list):
        il = []
        for i in rect_list:
            if self._check_overlap(self, i): il.append(i)
        return il
    
    def get_all_rects_nearby(self, rang=500):
        il = []
        for i in self.scene.nodes_collision:
            node = self.scene.nodes_collision[i]
            # rang = The range in pixels that this rectangle can be in to count

            if node == self: continue

            if abs(node.x - node.x) < rang:
                if abs(node.y - node.y) < rang:
                    il.append(node)
        return il
    
    def update(self, delta):
        super().update(delta)
        
        nearby   = self.get_all_rects_nearby()
        collided = self.collidelistall(nearby)
        self._physics_update(nearby, collided)  # Update physics based on nearby rectangles and collided ones

    def free(self):
        self.scene.nodes_collision.pop(self.id)
        super().free()
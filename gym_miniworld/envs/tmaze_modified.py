import numpy as np
import math
from ..miniworld import MiniWorldEnv, Room
from ..entity import Box,MeshEnt
from gym import spaces

class TMazeMEnv(MiniWorldEnv):
    """
    Two hallways connected in a T-junction
    """

    def __init__(self, **kwargs):
        super().__init__(
            max_episode_steps=400,
            **kwargs
        )

        # Allow only the movement actions
        self.action_space = spaces.Discrete(self.actions.move_forward+1)

    def _gen_world(self):
        room1 = self.add_rect_room(
            min_x=-1, max_x=8,
            min_z=-2, max_z=2
        )
        room2 = self.add_rect_room(
            min_x=8, max_x=12,
            min_z=-8, max_z=8
        )

        #Each room has another bifurcation
        room1_2 = self.add_rect_room(
            min_x=0, max_x=20,
            min_z=8, max_z=12
        )
        room1_1 = self.add_rect_room(
            min_x=0, max_x=20,
            min_z=-12, max_z=-8
        )
        self.connect_rooms(room1, room2, min_z=-2, max_z=2)
        self.connect_rooms(room2, room1_2, min_x=8, max_x=12)
        self.connect_rooms(room2, room1_1, min_x=8, max_x=12)

        colors = ['red','green', 'blue','purple','yellow','grey']
        target_color = self.rand.int(0,len(colors))


        # Add a box at a random end of the hallway
        self.box = Box(color=colors[target_color],size=0.5)
        self.boxes_other = []


        def place_box_rand(box,room_sel,offset=2):
            if room_sel == 1:
                if self.rand.bool():
                    self.place_entity(box, room=room1_2, min_x=room1_2.max_x - offset)
                else:
                    self.place_entity(box, room=room1_2, max_x=room1_2.max_x + offset)
            elif room_sel == 2:
                if self.rand.bool():
                    self.place_entity(box, room=room1_1, min_x=room1_1.max_x - offset)
                else:
                    self.place_entity(box, room=room1_1, max_x=room1_1.max_x + offset)
            elif room_sel == 3:
                if self.rand.bool():
                    self.place_entity(box, room=room2, min_z=room2.max_z - offset)
                else:
                    self.place_entity(box, room=room2, max_z=room2.max_z + offset)

        #Place target box
        room_sel = self.rand.int(1, 4)
        print(room_sel)
        place_box_rand(self.box, room_sel)
        print('Target color: '+colors[target_color])
        self.target_color = target_color

        objects=['barrel','box','cone','medkit']
        for i in range(6):
            sel = self.rand.int(0,len(colors))
            self_obj = self.rand.int(0,len(objects))
            while sel is target_color:
                sel = self.rand.int(0, len(colors))

            if objects[self_obj] == 'box':
                object = Box(color=colors[sel], size=0.5)
            else:
                object = MeshEnt(objects[self_obj],height=self.rand.float(0.4,0.8))

            self.boxes_other.append(object)
            place_box_rand(object,self.rand.int(1,4),offset=self.rand.int(2,6))

        # Choose a random room and position to spawn at
        self.place_agent(
            dir=self.rand.float(-math.pi/4, math.pi/4),
            room=room1
        )

    def step(self, action):
        obs, reward, done, info = super().step(action)

        if self.near(self.box):
            reward += self._reward()
            done = True
        info['target'] = self.target_color
        return obs, reward, done, info

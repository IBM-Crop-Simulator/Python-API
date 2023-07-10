import unittest
import bpy
import os
from mathutils import Vector

from src.controllers.light_controller import LightController

class LightControllerTest(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        self.light_position = (10, 5, 0)
        self.expected_light_position = Vector((10.0, 5.0, 0.0))

    def test_add_light(self):
        light_controller = LightController()
        light_controller.add_light()
        
        get_position = bpy.context.object.matrix_world.to_translation()

        # Verify that the output file was created
        self.assertEqual(get_position, self.expected_light_position)


if __name__ == "__main__":
    unittest.main()

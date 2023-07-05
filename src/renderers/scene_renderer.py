import os
import bpy

from controllers.segmentation import Segmentation

class SceneRenderer:
    def __init__(self, output_file):
        self.output_file = output_file

    def render_scene(self):
        current_working_directory = str(os.getcwd())
        bpy.context.scene.render.filepath = os.path.join(current_working_directory, self.output_file)
        bpy.ops.render.render(use_viewport=True, write_still=True)

        segmentation = Segmentation({
            1: 0xffff, # Make cubes white in the segmentation map
            2: 0xcccc,
            3: 0x9999,
        })
        segmentation_filename = self.output_file.replace(".png", "_seg.png") if self.output_file.endswith(".png") else self.output_file + "_seg.png"
        segmentation.segment(segmentation_filename)

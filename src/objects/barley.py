import bpy
from mathutils import Vector


from src.controllers.segmentation import SegmentationClass

class Barley:
    def __init__(self, stage, health):
        self.stage = stage
        self.health = health
        self.growth_stage = ["stage0.009", "stage1.009", "stage2.009", "stage3.009", "stage4.009",
                             "stage5.009", "stage6.009", "stage7.009","stage8.009",
                             "stage9.009", "stage10.009"]
        self.active_weeds = []
        self.crop_type = SegmentationClass.PLANT.value
        self.barley_object = self.set_model_stage(self.stage)
        self.GDD_PER_STAGE = 139
        self.name = self.barley_object.name

    def set_model_stage(self, stage):
        bpy.context.active_object.name = self.growth_stage[stage]
        duplicate = bpy.context.scene.objects.get(self.growth_stage[stage])
        barley_stage = duplicate.copy()
        barley_stage.data = duplicate.data.copy()
        barley_stage["segmentation_id"] = self.crop_type
        return barley_stage

    def growth_degree_days(self, t_max, t_min):
        # barley varieties required an average accumulation of 139 GDD
        # to progress to next stage
        t_base = 0                  # celsius, can be fahrenheit
        gdd = (t_max - t_min)/2 - t_base
        self.gdd += gdd

    def progress_stage(self):
        if self.gdd >= self.GDD_PER_STAGE:
            self.stage += 1
            self.set_model_stage(self.stage)

    def set_location(self, location):
        self.barley_object.location = location

    def get_location(self):
        return self.barley_object.location

    def set_height(self, scale):
        self.barley_object.scale = Vector((scale, scale, scale))

    def add_weed(self, weed):
        self.active_weeds.append(weed)

    def get_weeds(self):
        return self.active_weeds

    def measure_height(self, crop_object):
        # Get the coordinates of the object's vertices
        vertices = [v.co for v in crop_object.data.vertices]

        # Get the transformation matrix of the object
        matrix_world = crop_object.matrix_world

        # Initialise min and max Y coordinates
        min_y = float("inf")
        max_y = float("-inf")

        # Calculate the minimum and maximum Y coordinates of the transformed coordinates
        for vertex in vertices:
            transformed_vertex = matrix_world @ vertex
            min_y = min(min_y, transformed_vertex.y)
            max_y = max(max_y, transformed_vertex.y)

        # Calculating the height of an object
        crop_height = max_y - min_y

        return crop_height

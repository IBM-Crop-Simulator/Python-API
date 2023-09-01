import random
import bpy
import os
import math
from .ground_controller import GroundController
from src.objects.barley import Barley
from src.objects.weed import Weed
from src.growth_simulator.growth_manager import CropHealth
from src.controllers.weather_controller import WeatherController

class CropController:
    
    def __init__(self, config, collection):
        self.config = config
        self.collection_name = collection
        self.crop_size = 0.5
        self.counter = 1
        self.crop_data = config["crop"]
        self.crop_type = self.crop_data["type"]
        self.percentage_share = self.crop_data["percentage_share"]
        self.crop_count = self.crop_data["total_number"]
        self.rows = self.crop_data["num_rows"]
        self.columns = math.ceil(self.crop_count / self.rows)
        self.row_widths = self.crop_data["row_widths"]
        self.growth_simulator = config["growth_simulator"]
        self.days_per_stage = self.growth_simulator["days_per_stage"]
        self.all_crops = []
        self.all_plants = []
        self.weed_likelihood = int(config["weed_likelihood"]) * 100
 
        self.weed_spacing = 1 # The bounding area value in for spacing between weed and crop
        self.weed_effect_area = 0.3  # The radius of a crop to be affected by a weed
        self.model_names = {
            "stage0" : "stage0.stand",
            "stage1": "stage1.stand",
            "stage2": "stage2.stand",
            "stage3": "stage3.stand",
            "stage4": "stage4.stand",
            "stage5": "stage5.stand",
            "stage6": "stage6.stand",
            "stage7": "stage7.stand",
            "stage8": "stage8.stand",
            "stage9": "stage9.stand",
            "stage10": "stage10.stand",
            "ground" : "ground",
            "weed" : "weed",
        }
        self.planting_date = self.config["planting_date"]
        self.lat = self.config["latitude"]
        self.lon = self.config["longitude"]
        self.barley_type = self.config["barley_type"]
        self.crop_health = {
            CropHealth.UNHEALTHY.value : (0.6, 0.8, 0.2, 1),  # Yellow-green in RGBA
            CropHealth.DEAD.value : (0.0, 0.0, 0.0, 1.0),  # Brown in RGBA
        }
        self.weather_controller = WeatherController()
        self.weather_data = self.weather_controller.get_merged_weather_data(self.barley_type, self.planting_date, self.lat, self.lon)
        try:
            self.generation_seed = config["generation_seed"]
        except KeyError:
            self.generation_seed = None
        self.procedural_generation_seed_setter()

    def setup_crops(self, day):
        for obj in bpy.context.scene.objects:
            if obj.name not in self.model_names.values():
                obj.select_set(True)
        bpy.ops.object.delete()

        groundcon = GroundController(self.config)
        groundcon.get_ground_stages()
        
        if day == 0:
            self.initialise_crops()
        else:
            self.grow_crops()

        
        collection = bpy.data.collections.get(self.collection_name)
        for obj in bpy.context.scene.objects:
            if obj.name in self.model_names.values():
                target = collection.objects.get(obj.name)
                collection.objects.unlink(target)


    def initialise_crops(self):
        curr_row = 0
        curr_col = 0
        curr_crop = 0
        location = [0, 0, 0]

        for _ in range(self.crop_count):
            crop_model = self.add_crop(self.crop_type[0], location, 0)
            self.all_crops.append(crop_model)  # add crop objects to manipulate later
            self.add_weed(location)
            
            # move along row to next crop position
            curr_crop += 1
            curr_col += 1
            # change row if at end of row
            if curr_col == self.rows:
                curr_col = 0
                curr_row += 1
                location[1] += 1 / self.crop_data["density"]
                location[0] = 0
            else:
                location[0] += self.row_widths / self.crop_data["density"]
            
    def grow_crops(self):
        for crop in self.all_crops:
            crop.grow(crop.location)

    def procedural_generation_seed_setter(self):
        random.seed(self.generation_seed)

    def add_crop(self, crop_type, location, stage):
        crop = None
        if crop_type == "barley":
            crop = Barley(self.config, stage, "healthy", self.weather_data)
        location[0] = location[0] - random.uniform(-.5, .5)
        location[1] = location[1] - random.uniform(-.5, .5)
        crop.set_location([location[0], location[1], location[2]])
        self.counter += 1
        self.all_crops.append(crop) # add crop objects to manipulate later
        self.all_plants.append(crop)
        return crop

    def add_weed(self, location):
        if bool(random.getrandbits(1)):
            weed = Weed()
            location[0] = location[0] - random.uniform(-self.weed_spacing, self.weed_spacing)
            location[1] = location[1] - random.uniform(-self.weed_spacing, self.weed_spacing)
            weed.set_location([location[0], location[1], location[2]])
            bpy.context.collection.objects.link(weed.weed_object)
            self.all_plants.append(weed) # add objects to manipulate later
            self.populate_area_weeds(weed)
            return weed
        return False

    # If X of weed is within X of crop weed radius and Y of weed is within Y of crop weed radius then add it to the crop
    def populate_area_weeds(self, weed):
        for crop_model in self.all_crops:
            if ((crop_model.get_location()[0] + self.weed_effect_area < weed.get_location()[0]) >
                    crop_model.get_location()[0] - self.weed_effect_area and
                    crop_model.get_location()[1] + self.weed_effect_area < weed.get_location()[1] >
                    crop_model.get_location()[1] - self.weed_effect_area):
                crop_model.add_weed(weed)

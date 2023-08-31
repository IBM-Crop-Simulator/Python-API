import typer
import bpy
from dotenv.main import load_dotenv
import time
import sys
import os

from src.controllers.crop_controller import CropController
from src.controllers.yaml_reader import YamlReader
from src.renderers.scene_renderer import SceneRenderer
from src.controllers.weather_controller import WeatherController
from src.machine_learning.text_prompt_manager import TextPromptManager

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


load_dotenv()

class TyperLaunchAPI:
    """
    This class is used to launch the application using the Typer library.
    """

    @staticmethod
    def typer_interface(config_file: str):
        config = YamlReader().read_file(config_file)
        TyperLaunchAPI.launch(config)

    @staticmethod
    def launch(config):

        text_prompt_manager = TextPromptManager()

        start_time = time.time()
        planting_date = config["planting_date"]
        lat = config["latitude"]
        lon = config["longitude"]
        barley_type = config["barley_type"]
        api_key = os.environ["WEATHER_API"]
        weather_controller = WeatherController(api_key)
        weather_controller.get_merged_weather_data(barley_type, planting_date, lat, lon)


        bpy.ops.wm.open_mainfile(filepath="src/blender_assets/CropAssets.blend")
        collection = "Collection"
        # Set the unit system to metric
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.scale_length = 1.0  # Set the scale to 1.0 for metric units
        cropcon = CropController(config, collection)
        scenerender = SceneRenderer(config, collection)
        cropcon.setup_crops()

        cropcon.update_text_prompt_manager(text_prompt_manager)


        scenerender.render_scene()
        end_time = time.time()
        total_time = end_time - start_time
        print("Time taken to run:", total_time)


if __name__ == "__main__":
    typer.run(TyperLaunchAPI.typer_interface)


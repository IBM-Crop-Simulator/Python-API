import typer
import bpy

from controllers.crop_controller import CropController
from controllers.yaml_reader import YamlReader
from renderers.scene_renderer import SceneRenderer
from controllers.camera_controller import CameraController
from controllers.light_controller import LightController


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
        bpy.ops.wm.open_mainfile(filepath="src/blender_assets/CropAssets.blend")
        # for ob in bpy.context.scene.objects:
        #     print(ob.name)
        for ob in bpy.context.scene.objects:
            if ob.name != "stage11.1":
                ob.select_set(True)
        bpy.ops.object.delete()
        collection = "Collection"
        cameracon = CameraController()
        lightcon = LightController()
        lightcon.add_light()
        cropcon = CropController(config["crop"], collection)
        scenerender = SceneRenderer(config["outfile"][0], collection)
        cameracon.setup_camera("camera_one", (10,0,0), (1.57057,0.00174533,1.57057), "Collection")
        cropcon.setup_crops()
        collection1 = bpy.data.collections.get("Collection")
        dupe = collection1.objects.get("stage11.1")
        # dupe.hide_set(True)
        collection1.objects.unlink(dupe)


        scenerender.render_scene()


if __name__ == "__main__":
    typer.run(TyperLaunchAPI.typer_interface)

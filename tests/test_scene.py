from ratcave import Scene, Camera, Light


def test_scene_initializes():
    scene = Scene()
    assert hasattr(scene, 'meshes')
    assert hasattr(scene, 'camera')
    assert hasattr(scene, 'light')
    assert isinstance(scene.camera, Camera)
    assert isinstance(scene.light, Light)
    assert hasattr(scene, 'clear')
    assert hasattr(scene, 'draw')





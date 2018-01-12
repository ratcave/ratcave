from ratcave import texture
import pytest

def test_texture_creation():
    tex = texture.Texture()
    cubetex = texture.TextureCube()
    graytex = texture.GrayscaleTexture()
    graycube = texture.GrayscaleTextureCube()


def test_texture_attributes_created():
    old_id = 0
    for idx, (w, h) in enumerate([(1024, 1024), (256, 128), (200, 301)]):
        tex = texture.Texture(width=w, height=h)
        assert tex.width == w
        assert tex.height == h
        assert tex.id != old_id
        old_id = tex.id

    cube = texture.TextureCube(width=1024, height=1024)
    assert cube.width == 1024
    assert cube.height == 1024
    with pytest.raises(ValueError):
        cube = texture.TextureCube(width=400, height=600)

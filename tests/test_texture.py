from ratcave import texture
import pytest
import os

if not 'APPVEYOR' in os.environ:
    @pytest.fixture
    def tex():
        return texture.Texture()

    @pytest.fixture
    def cubetex():
        return texture.TextureCube()

    @pytest.fixture
    def depthtex():
        return texture.DepthTexture()

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


    def test_texture_default_uniform_names(tex, cubetex, depthtex):
        assert 'TextureMap' in tex.uniforms
        assert 'TextureMap_isBound' in tex.uniforms
        assert 'CubeMap' in cubetex.uniforms
        assert 'CubeMap_isBound' in cubetex.uniforms
        assert 'DepthMap' in depthtex.uniforms
        assert 'DepthMap_isBound' in depthtex.uniforms
        assert 'CubeMap' not in tex.uniforms
        assert 'CubeMap_isBound' not in tex.uniforms
        assert 'TextureMap' not in cubetex.uniforms

        newtex = texture.Texture(name='NewMap')
        assert newtex.name == 'NewMap'
        assert 'NewMap' in newtex.uniforms
        assert 'NewMap_isBound' in newtex.uniforms
        assert 'TextureMap' not in newtex.uniforms

        newtex.name = 'Changed'
        assert newtex.name == 'Changed'
        assert 'Changed' in newtex.uniforms
        assert 'Changed_isBound' in newtex.uniforms
        assert 'NewMap' not in newtex.uniforms
        assert 'NewMap_isBound' not in newtex.uniforms



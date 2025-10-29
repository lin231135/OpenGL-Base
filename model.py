# model.py

from OpenGL.GL import *
from obj import Obj
from buffer import Buffer
import glm
import pygame
import os

class SubMesh:
    def __init__(self, positions, texCoords, normals, texturePath=None, name=""):
        self.positions = Buffer(positions)
        self.texCoords = Buffer(texCoords)
        self.normals   = Buffer(normals)
        self.vertexCount = int(len(positions) // 3)
        self.texture = None
        self.name = name
        if texturePath:
            self.loadTexture(texturePath)
        else:
            if name:
                print(f"[Model] Submesh '{name}' sin map_Kd (se verá sin textura)")

    def loadTexture(self, filename):
        if not os.path.isfile(filename):
            print(f"[Tex] No se encontró textura: {filename}")
            return

        surface = pygame.image.load(filename).convert_alpha()
        # Si no hay alpha, convert_alpha igual produce RGBA; detectamos por bytesize
        bpp = surface.get_bytesize()
        if bpp == 4:
            data = pygame.image.tostring(surface, "RGBA", True)
            fmt  = GL_RGBA
        else:
            data = pygame.image.tostring(surface, "RGB", True)
            fmt  = GL_RGB

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, fmt, surface.get_width(), surface.get_height(),
                     0, fmt, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)

        # Filtros y wrap para evitar “negro” en algunos drivers al samplear mipmaps
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        self.texture = tex

    def render(self):
        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)

        self.positions.Use(0, 3)
        self.texCoords.Use(1, 2)
        self.normals.Use(2, 3)

        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)

class Model:
    def __init__(self, filename):
        self.objFile = Obj(filename)
        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        self.scale    = glm.vec3(1, 1, 1)
        self.submeshes = []
        self._build_submeshes()

    def _build_submeshes(self):
        materialMap = self.objFile.materials  # dict: newmtl → path map_Kd
        currentMaterial = None
        positions, texCoords, normals = [], [], []

        def flush_submesh(matName, pos, uv, nor):
            if not pos:
                return
            texPath = materialMap.get(matName)
            name = matName if matName else "default"
            sm = SubMesh(pos, uv, nor, texPath, name=name)
            self.submeshes.append(sm)

        for face, matName in self.objFile.faces:
            if matName != currentMaterial and positions:
                flush_submesh(currentMaterial, positions, texCoords, normals)
                positions, texCoords, normals = [], [], []
            currentMaterial = matName

            for (vi, ti, ni) in face:
                v = self.objFile.vertices[vi - 1]

                if ti > 0 and ti <= len(self.objFile.texCoords):
                    t = self.objFile.texCoords[ti - 1]
                else:
                    t = [0.0, 0.0]

                if ni > 0 and ni <= len(self.objFile.normals):
                    n = self.objFile.normals[ni - 1]
                else:
                    n = [0.0, 0.0, 1.0]

                positions += v
                texCoords += t
                normals   += n

        # último bloque
        flush_submesh(currentMaterial, positions, texCoords, normals)

        if not self.submeshes:
            print("[Model] No se generaron submeshes. ¿Seguro que el .obj tiene 'f' y 'usemtl'?")
        else:
            print("[Model] Submeshes construidos:")
            for sm in self.submeshes:
                print(f"   - {sm.name} | tex={'OK' if sm.texture else 'None'}")

    def GetModelMatrix(self):
        I = glm.mat4(1)
        T = glm.translate(I, self.position)
        Rx = glm.rotate(I, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        Ry = glm.rotate(I, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        Rz = glm.rotate(I, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        R  = Rx * Ry * Rz
        S  = glm.scale(I, self.scale)
        return T * R * S

    def Render(self):
        for sm in self.submeshes:
            sm.render()

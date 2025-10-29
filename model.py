# model.py
# (mantén este comentario con el nombre del archivo)

from OpenGL.GL import *
from obj import Obj, get_diffuse_maps_from_obj, parse_mtl_maps
from buffer import Buffer

import glm
import os
import pygame


class Model(object):
    def __init__(self, filename):
        self.objFile = Obj(filename)
        self.path = filename

        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        self.scale    = glm.vec3(1, 1, 1)

        self.BuildBuffers()
        self.textures = []  # GL texture ids (tex0, tex1, ...)

    def GetModelMatrix(self):
        I = glm.mat4(1)
        T = glm.translate(I, self.position)
        Rx = glm.rotate(I, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        Ry = glm.rotate(I, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        Rz = glm.rotate(I, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        R = Rx * Ry * Rz
        S = glm.scale(I, self.scale)
        return T * R * S

    # -------------- Parser robusto -> Buffers -----------------

    def BuildBuffers(self):
        """Triangula caras de N lados y tolera faltas de vt / vn."""
        V = self.objFile.vertices
        VT = self.objFile.texCoords
        VN = self.objFile.normals

        positions = []
        texCoords = []
        normals   = []

        def add_triangle(a, b, c):
            # a,b,c = (v,vt,vn)
            idx = [a, b, c]
            # posiciones de los 3 vértices (obligatorio tener v)
            P = []
            UV = []
            NN = []

            for (v, vt, vn) in idx:
                # v es obligatorio
                p = V[v - 1] if v > 0 else [0.0, 0.0, 0.0]
                P.append(p)
                # uv opcional
                uv = VT[vt - 1] if vt > 0 and vt <= len(VT) else [0.0, 0.0]
                UV.append(uv)
                # normal opcional, si no hay la calculamos luego
                n = VN[vn - 1] if vn > 0 and vn <= len(VN) else None
                NN.append(n)

            # Si faltan normales, calcula normal por triángulo
            if NN[0] is None or NN[1] is None or NN[2] is None:
                import math
                p1 = glm.vec3(P[0][0], P[0][1], P[0][2])
                p2 = glm.vec3(P[1][0], P[1][1], P[1][2])
                p3 = glm.vec3(P[2][0], P[2][1], P[2][2])
                ntri = glm.normalize(glm.cross(p2 - p1, p3 - p1))
                ntri = [float(ntri.x), float(ntri.y), float(ntri.z)]
                NN = [ntri, ntri, ntri]
            else:
                # asegurar ser listas de float
                NN = [[float(x), float(y), float(z)] for (x, y, z) in NN]

            # push a arrays finales
            for i in range(3):
                positions.extend(P[i])
                texCoords.extend(UV[i])
                normals.extend(NN[i])

        # triangulación por "fan"
        for face in self.objFile.faces:
            if len(face) < 3:
                continue
            for i in range(1, len(face) - 1):
                add_triangle(face[0], face[i], face[i + 1])

        self.vertexCount = len(positions) // 3
        self.posBuffer      = Buffer(positions)
        self.texCoordsBuffer= Buffer(texCoords)
        self.normalsBuffer  = Buffer(normals)

    # -------------- Texturas (BMP/PNG con alfa) ----------------

    def AddTexture(self, filename):
        """Carga BMP/JPG/PNG (RGBA si aplica), flip vertical, mipmaps."""
        if not os.path.isfile(filename):
            print(f"[Model] ⚠ No existe la textura: {filename}")
            return
        try:
            surf = pygame.image.load(filename)
            surf = pygame.transform.flip(surf, False, True)
            surf = surf.convert_alpha()

            w, h = surf.get_size()
            pixels = pygame.image.tostring(surf, "RGBA", True)

            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glGenerateMipmap(GL_TEXTURE_2D)

            self.textures.append(tex_id)
            print(f"[Model] ✓ Textura cargada: {filename}")
        except Exception as e:
            print(f"[Model] ✖ Error cargando textura {filename}: {e}")

    def AddDiffuseFromMTL(self, load_all=False):
        """
        Carga texturas difusas (map_Kd) del .mtl del OBJ.
          - load_all=False: solo el primer map_Kd -> tex0
          - load_all=True : todos los map_Kd     -> tex0, tex1, ...
        """
        diffuse_maps = []
        # Preferimos mtl ya resuelto por el parser:
        if getattr(self.objFile, "mtl_path", None):
            maps = parse_mtl_maps(self.objFile.mtl_path)
            diffuse_maps = [p for p in maps.get("map_Kd", []) if p]
        else:
            diffuse_maps = get_diffuse_maps_from_obj(self.path)

        if not diffuse_maps:
            print("[Model] (MTL) No se encontró map_Kd o archivo de textura.")
            return

        if not load_all:
            diffuse_maps = diffuse_maps[:1]

        for p in diffuse_maps:
            if os.path.isfile(p):
                self.AddTexture(p)

    # -------------- Render ----------------

    def Render(self):
        # Bindea todas las texturas cargadas secuencialmente (tex0, tex1, ...)
        for i, tex in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, tex)

        self.posBuffer.Use(0, 3)
        self.texCoordsBuffer.Use(1, 2)
        self.normalsBuffer.Use(2, 3)

        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)

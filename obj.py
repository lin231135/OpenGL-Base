# obj.py

import os

class Obj(object):
    def __init__(self, filename):
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.read().splitlines()

        self.vertices = []
        self.texCoords = []
        self.normals = []

        # Cada cara se guarda como (face, materialName)
        self.faces = []
        # Mapa de materiales a textura difusa (map_Kd)
        self.materials = {}

        currentMaterial = None
        basePath = os.path.dirname(os.path.abspath(filename))

        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            prefix = parts[0].lower()

            if prefix == "v":
                self.vertices.append(list(map(float, parts[1:4])))
            elif prefix == "vt":
                uv = list(map(float, parts[1:3]))
                self.texCoords.append(uv)
            elif prefix == "vn":
                self.normals.append(list(map(float, parts[1:4])))
            elif prefix == "usemtl":
                currentMaterial = parts[1]
            elif prefix == "f":
                face = []
                for vert in parts[1:]:
                    comps = vert.split("/")
                    v_idx = int(comps[0])
                    t_idx = int(comps[1]) if len(comps) > 1 and comps[1] != "" else 0
                    n_idx = int(comps[2]) if len(comps) > 2 and comps[2] != "" else 0
                    face.append([v_idx, t_idx, n_idx])
                self.faces.append((face, currentMaterial))
            elif prefix == "mtllib":
                mtl_rel = line[len(parts[0]):].strip()
                mtl_path = os.path.join(basePath, mtl_rel)
                self._load_mtl(mtl_path, basePath)

    def _load_mtl(self, filename, basePath):
        if not os.path.isfile(filename):
            alt = os.path.join(basePath, os.path.basename(filename))
            if os.path.isfile(alt):
                filename = alt
            else:
                print(f"[MTL] No se encontró: {filename}")
                return

        currentMat = None
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                key = parts[0].lower()

                if key == "newmtl":
                    currentMat = line.split(None, 1)[1].strip()
                elif key == "map_kd" and currentMat:
                    rel_path = line.split(None, 1)[1].strip()
                    # Normaliza separadores
                    rel_path = rel_path.replace("\\", os.sep).replace("/", os.sep)
                    tex_path = os.path.normpath(os.path.join(basePath, rel_path))
                    self.materials[currentMat] = tex_path

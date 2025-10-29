# obj.py
# (mantén este comentario con el nombre del archivo)

import os

class Obj(object):
    """
    Lector OBJ robusto:
      - Acepta: v, vt, vn
      - Caras: v / v/vt / v//vn / v/vt/vn
      - Guarda self.faces como lista de listas de tuplas (v, vt, vn) con índices 1-based o 0 si falta.
      - self.mtl_path si hay 'mtllib'.
    """
    def __init__(self, filename):
        self.source_path = filename
        self.vertices = []   # [ [x,y,z], ... ]
        self.texCoords = []  # [ [u,v], ... ]
        self.normals = []    # [ [nx,ny,nz], ... ]
        self.faces = []      # [ [ (v,vt,vn), (v,vt,vn), ... ], ... ]
        self.mtl_path = None

        base_dir = os.path.dirname(filename)
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue

                low = line.lower()

                if low.startswith("mtllib"):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        mtl_file = parts[1].strip()
                        cand = os.path.join(base_dir, mtl_file)
                        if os.path.isfile(cand):
                            self.mtl_path = cand
                        else:
                            alt = os.path.join(base_dir, os.path.basename(mtl_file))
                            if os.path.isfile(alt):
                                self.mtl_path = alt
                    continue

                head, *rest = line.split()
                if head == "v":
                    self.vertices.append(list(map(float, rest)))
                elif head == "vt":
                    # Solo (u,v)
                    uv = list(map(float, rest[:2])) if len(rest) >= 2 else [0.0, 0.0]
                    self.texCoords.append(uv)
                elif head == "vn":
                    self.normals.append(list(map(float, rest)))
                elif head == "f":
                    verts = []
                    for token in rest:
                        # v | v/vt | v//vn | v/vt/vn
                        a = token.split('/')
                        v  = int(a[0]) if a[0] else 0
                        vt = int(a[1]) if len(a) > 1 and a[1] != '' else 0
                        vn = int(a[2]) if len(a) > 2 and a[2] != '' else 0
                        verts.append((v, vt, vn))
                    if len(verts) >= 3:
                        self.faces.append(verts)


# -------------------- Utilidades MTL --------------------

def get_mtl_path_from_obj(obj_path: str) -> str | None:
    """Devuelve la ruta del .mtl declarado dentro del .obj (si existe)."""
    try:
        base_dir = os.path.dirname(obj_path)
        with open(obj_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.lower().startswith("mtllib"):
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        mtl_file = parts[1].strip()
                        mtl_path = os.path.join(base_dir, mtl_file)
                        if os.path.isfile(mtl_path):
                            return mtl_path
                        alt = os.path.join(base_dir, os.path.basename(mtl_file))
                        if os.path.isfile(alt):
                            return alt
        return None
    except Exception:
        return None


def parse_mtl_maps(mtl_path: str):
    """
    Devuelve dict con listas de rutas por tipo de mapa (se resuelven rutas relativas):
      - map_Kd: difusas
      - map_Ks, map_Bump/bump, map_Ka, map_Ns, map_d (por si los quieres luego)
    """
    maps = {
        "map_Kd": [],
        "map_Ks": [],
        "map_Bump": [],
        "bump": [],
        "map_Ka": [],
        "map_Ns": [],
        "map_d": [],
    }
    try:
        base_dir = os.path.dirname(mtl_path)
        with open(mtl_path, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                low = line.lower()
                for key in list(maps.keys()):
                    if low.startswith(key):
                        tokens = line.split()
                        if len(tokens) >= 2:
                            # toma último token como ruta (ignora opciones -blabla)
                            cand = tokens[-1]
                            path = os.path.join(base_dir, cand)
                            if not os.path.isfile(path):
                                alt = os.path.join(base_dir, os.path.basename(cand))
                                tex = os.path.join(base_dir, "textures", os.path.basename(cand))
                                if os.path.isfile(alt):
                                    path = alt
                                elif os.path.isfile(tex):
                                    path = tex
                            maps[key].append(path)
                        break
    except Exception:
        pass
    return maps


def get_diffuse_maps_from_obj(obj_path: str):
    """Devuelve lista de rutas de map_Kd del .mtl referenciado por el .obj."""
    mtl = get_mtl_path_from_obj(obj_path)
    if not mtl:
        return []
    maps = parse_mtl_maps(mtl)
    return [p for p in maps.get("map_Kd", []) if p]

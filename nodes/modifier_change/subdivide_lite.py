# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
from bmesh.ops import subdivide_edges
import numpy as np
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from sverchok.utils.sv_bmesh_utils import bmesh_from_pydata, pydata_from_bmesh


class SvSubdivideLiteNode(bpy.types.Node, SverchCustomTreeNode):
    '''Subdivide Fast'''

    bl_idname = 'SvSubdivideLiteNode'
    bl_label = 'Subdivide lite'
    bl_icon = 'OUTLINER_OB_EMPTY'

    falloff_types = [
            ("0", "Smooth", "", 'SMOOTHCURVE', 0),
            ("1", "Sphere", "", 'SPHERECURVE', 1),
            ("2", "Root", "", 'ROOTCURVE', 2),
            ("3", "Sharp", "", 'SHARPCURVE', 3),
            ("4", "Linear", "", 'LINCURVE', 4),
            ("7", "Inverse Square", "", 'ROOTCURVE', 7)
        ]

    corner_types = [
            ("0", "Inner Vertices", "", 0),
            ("1", "Path", "", 1),
            ("2", "Fan", "", 2),
            ("3", "Straight Cut", "", 3)
        ]

    def update_mode(self, context):
        self.outputs['NewVertices'].hide_safe = not self.show_new
        self.outputs['NewEdges'].hide_safe = not self.show_new
        self.outputs['NewFaces'].hide_safe = not self.show_new
        self.outputs['OldVertices'].hide_safe = not self.show_old
        self.outputs['OldEdges'].hide_safe = not self.show_old
        self.outputs['OldFaces'].hide_safe = not self.show_old
        updateNode(self, context)

    falloff_type = EnumProperty(name="Falloff",
            items=falloff_types,
            default="4",
            update=updateNode)
    corner_type = EnumProperty(name="Corner Cut Type",
            items=corner_types,
            default="0",
            update=updateNode)
    cuts = IntProperty(name="Number of Cuts",
            description="Specifies the number of cuts per edge to make",
            min=1, default=1,
            update=updateNode)
    smooth = FloatProperty(name="Smooth",
            description="Displaces subdivisions to maintain approximate curvature",
            min=0.0, max=1.0, default=0.0,
            update=updateNode)
    fractal = FloatProperty(name="Fractal",
            description="Displaces the vertices in random directions after the mesh is subdivided",
            min=0.0, max=1.0, default=0.0,
            update=updateNode)
    along_normal = FloatProperty(name="Along normal",
            description="Causes the vertices to move along the their normals, instead of random directions",
            min=0.0, max=1.0, default=0.0,
            update=updateNode)
    seed = IntProperty(name="Seed",
            description="Random seed",
            default=0,
            update=updateNode)
    grid_fill = BoolProperty(name="Grid fill",
            description="fill in fully-selected faces with a grid",
            default=True,
            update=updateNode)
    single_edge = BoolProperty(name="Single edge",
            description="tessellate the case of one edge selected in a quad or triangle",
            default=False,
            update=updateNode)
    only_quads = BoolProperty(name="Only Quads",
            description="only subdivide quads (for loopcut)",
            default=False,
            update=updateNode)
    smooth_even = BoolProperty(name="Even smooth",
            description="maintain even offset when smoothing",
            default=False,
            update=updateNode)
    show_new = BoolProperty(name="Show New",
            description="Show outputs with new geometry",
            default=False,
            update=update_mode)
    show_old = BoolProperty(name="Show Old",
            description="Show outputs with old geometry",
            default=False,
            update=update_mode)
    show_options = BoolProperty(name="Show Options",
            description="Show options on the node",
            default=False,
            update=updateNode)
    sel_mode = BoolProperty(name="select",
            description="Select edges by index when True. Select by mask when False",
            default=False,
            update=updateNode)

    def draw_buttons(self, context, layout):
        layout.prop(self, "show_options", toggle=True)
        if self.show_options:
            col = layout.column(align=True)
            row = col.row(align=True)
            col.prop(self, "cuts", text="cuts")
            col.prop(self, "smooth", text="smooth")
            col.prop(self, "fractal", text="fractal")
            col.prop(self, "along_normal", text="along_normal")
            col.prop(self, "seed", text="seed")
            row.prop(self, "show_old", toggle=True)
            row.prop(self, "show_new", toggle=True)
            col.prop(self, "sel_mode", toggle=True)
            col.prop(self, "falloff_type")
            col.prop(self, "corner_type")
            col.prop(self, "grid_fill", toggle=True)
            col.prop(self, "single_edge", toggle=True)
            col.prop(self, "only_quads", toggle=True)
            col.prop(self, "smooth_even", toggle=True)

    def sv_init(self, context):
        sin, son = self.inputs.new, self.outputs.new
        sin('VerticesSocket', "Vertices", "Vertices")
        sin('StringsSocket', 'Edges', 'Edges')
        sin('StringsSocket', 'Faces', 'Faces')
        sin('StringsSocket', 'EdgeIndex')
        son('VerticesSocket', 'Vertices')
        son('StringsSocket', 'Edges')
        son('StringsSocket', 'Faces')
        son('VerticesSocket', 'NewVertices')
        son('StringsSocket', 'NewEdges')
        son('StringsSocket', 'NewFaces')
        son('VerticesSocket', 'OldVertices')
        son('StringsSocket', 'OldEdges')
        son('StringsSocket', 'OldFaces')
        self.update_mode(context)

    def get_result_pydata(self, geom):
        new_verts = [tuple(v.co) for v in geom if isinstance(v, bmesh.types.BMVert)]
        new_edges = [[v.index for v in e.verts] for e in geom if isinstance(e, bmesh.types.BMEdge)]
        new_faces = [[v.index for v in f.verts] for f in geom if isinstance(f, bmesh.types.BMFace)]
        return new_verts, new_edges, new_faces

    def process(self):
        if not any(output.is_linked for output in self.outputs):
            return
        InVert, InEdge, InFace, InEdInd = self.inputs
        OutVert, OutEdg, OutFace, ONVert, ONEdg, ONFace, OOVert, OOEdg, OOFace = self.outputs
        vertices_s = InVert.sv_get()
        edges_s = InEdge.sv_get(default=[[]])
        faces_s = InFace.sv_get(default=[[]])
        rev, ree, ref, riv, rie, rif, rsv, rse, rsf = [],[],[],[],[],[],[],[],[]
        bmlist= [bmesh_from_pydata(v, e, f, normal_update=True) for v,e,f in zip(vertices_s,edges_s,faces_s)]
        if InEdInd.is_linked:
            if self.sel_mode:
                useedges = [np.array(bm.edges[:])[idxs] for bm, idxs in zip(bmlist, InEdInd.sv_get())]
            else:
                useedges = [np.extract(mask, bm.edges[:]) for bm, mask in zip(bmlist, InEdInd.sv_get())]
        else:
            useedges = [bm.edges for bm in bmlist]
        for bm,ind in zip(bmlist,useedges):
            geom = subdivide_edges(bm, edges= ind,
                    smooth= self.smooth,
                    smooth_falloff= int(self.falloff_type),
                    fractal= self.fractal, along_normal= self.along_normal,
                    cuts= self.cuts, seed= self.seed,
                    quad_corner_type= int(self.corner_type),
                    use_grid_fill= self.grid_fill,
                    use_single_edge= self.single_edge,
                    use_only_quads= self.only_quads,
                    use_smooth_even= self.smooth_even)
            new_verts, new_edges, new_faces = pydata_from_bmesh(bm)
            rev.append(new_verts)
            ree.append(new_edges)
            ref.append(new_faces)
            if self.show_new:
                inner_verts, inner_edges, inner_faces = self.get_result_pydata(geom['geom_inner'])
                riv.append(inner_verts)
                rie.append(inner_edges)
                rif.append(inner_faces)
            if self.show_old:
                split_verts, split_edges, split_faces = self.get_result_pydata(geom['geom_split'])
                rsv.append(split_verts)
                rse.append(split_edges)
                rsf.append(split_faces)
            bm.free()
        OutVert.sv_set(rev)
        OutEdg.sv_set(ree)
        OutFace.sv_set(ref)
        ONVert.sv_set(riv)
        ONEdg.sv_set(rie)
        ONFace.sv_set(rif)
        OOVert.sv_set(rsv)
        OOEdg.sv_set(rse)
        OOFace.sv_set(rsf)


def register():
    bpy.utils.register_class(SvSubdivideLiteNode)


def unregister():
    bpy.utils.unregister_class(SvSubdivideLiteNode)

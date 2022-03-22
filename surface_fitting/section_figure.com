
$study = 'Human_Aging';
$subject = 'AGING006';
$condition = 'EIsupine';
 
$fitpath = 'output/'.$subject.'/'.$condition.'/Torso';
$datapath = $study.'/'.$subject.'/'.$condition.'/Torso';
$lungpath = $study.'/'.$subject.'/'.$condition.'/Lung/SurfaceFEMesh';

#'Human_Aging/AGING006/EIsupine/Lung/SurfaceFEMesh/'

gfx read node $fitpath.'/Torso_fitted' reg mesh_TorsoFitted;
gfx read elem $fitpath.'/Torso_fitted' reg mesh_TorsoFitted;
#gfx cre egroup torso_section
#gfx mod egroup torso_section add 121
#gfx mod egroup torso_section add 122..132
#gfx mod egroup torso_section add 137..148
#gfx mod egroup torso_section add 153..164
#gfx mod egroup torso_section add 166..213

gfx mod g_e mesh_TorsoFitted surface mat tissue;
gfx mod g_e mesh_TorsoFitted node_points glyph sphere general size "4*4*4" material blue;

#open com;section_figure

gfx read data $datapath.'/surface_Torsotrimmed_crop';
gfx read node $lungpath.'/'.'Left_fitted' reg mesh_LungLeft;
gfx read elem $lungpath.'/'.'Left_fitted' reg mesh_LungLeft;
gfx read node $lungpath.'/'.'Right_fitted' reg mesh_LungRight;
gfx read elem $lungpath.'/'.'Right_fitted' reg mesh_LungRight;
gfx read node 'cut_plane' reg cut_plane;
gfx read elem 'cut_plane' reg cut_plane;

gfx cre mat lung_test ambient 0.9 0.7 0.7 diffuse 0.9 0.7 0.7 specular 0.9 0.7 0.7 alpha 0.4;
gfx create material lung_test ambient 0.8 0.38 0.33 diffuse 0.8 0.38 0.33 emission 0 0 0 specular 0.8 0.8 0.8 alpha 1 shininess 1
gfx mod g_e surface_Torso data_points glyph point size "4*4*4" material green;
gfx mod g_e mesh_LungLeft surface mat lung_surface;
gfx mod g_e mesh_LungRight surface mat lung_surface;

gfx edit scene;
gfx cre wind;
gfx node_tool edit select;

open com;edit_derivatives

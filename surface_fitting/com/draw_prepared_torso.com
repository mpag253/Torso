
#$study = 'Human_Aging';
#$subject = 'AGING039';
#$condition = 'EIsupine';

$study = 'Human_Lung_Atlas';
$subject ='P2BRP139-H6229';
$condition = 'EIsupine'; 

$lungpath = $study.'/'.$subject.'/'.$condition.'/Lung/SurfaceFEMesh';
$fitpath = 'output/'.$subject.'/'.$condition.'/Torso';
$datapath = $study.'/'.$subject.'/'.$condition.'/Torso';

gfx read node $fitpath.'/Torso_prepared' reg mesh_TorsoPrepared;
gfx read elem $fitpath.'/Torso_prepared' reg mesh_TorsoPrepared;
gfx read data $datapath.'/surface_Torsotrimmed_crop_tf';

gfx read node $lungpath.'/'.'Left_fitted_tf' reg mesh_LungLeft;
gfx read elem $lungpath.'/'.'Left_fitted' reg mesh_LungLeft;
gfx read node $lungpath.'/'.'Right_fitted_tf' reg mesh_LungRight;
gfx read elem $lungpath.'/'.'Right_fitted' reg mesh_LungRight;

gfx cre mat torso_surface ambient 0.4 0.4 0.4 diffuse 0.7 0.7 0.7 specular 0.5 0.5 0.5 alpha 0.4;
gfx mod g_e mesh_TorsoPrepared surface mat torso_surface;
gfx mod g_e mesh_TorsoPrepared node_points glyph sphere general size "4*4*4" material blue;
gfx mod g_e surface_Torso data_points glyph point size "4*4*4" material green;

gfx mod g_e mesh_LungLeft surface mat lung_surface;
gfx mod g_e mesh_LungRight surface mat lung_surface;

gfx edit scene;
gfx cre wind;
#gfx node_tool edit select;

#open com;edit_derivatives

#open com;read_mesh
#open com;write_mesh

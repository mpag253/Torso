
#$study = 'Human_Aging';
#$subject = 'AGING006';
#$condition = 'EIsupine';

$study = 'Human_Lung_Atlas';
$subject = 'P2BRP115-H5977';
$condition = 'EIsupine';
 
$fitpath = 'output/'.$subject.'/'.$condition.'/Torso';
$datapath = $study.'/'.$subject.'/'.$condition.'/Torso';
$lungpath = $study.'/'.$subject.'/'.$condition.'/Lung/SurfaceFEMesh';

gfx read node $fitpath.'/Torso_fitted' reg mesh_TorsoFitted;
gfx read elem $fitpath.'/Torso_fitted' reg mesh_TorsoFitted;
gfx read data $datapath.'/surface_Torsotrimmed_crop';
gfx read node $lungpath.'/'.'Left_fitted' reg mesh_LungLeft;
gfx read elem $lungpath.'/'.'Left_fitted' reg mesh_LungLeft;
gfx read node $lungpath.'/'.'Right_fitted' reg mesh_LungRight;
gfx read elem $lungpath.'/'.'Right_fitted' reg mesh_LungRight;

gfx cre mat plane_mat ambient 0.7 0.7 0.7 diffuse 0.0 0.0 0.0 specular 0.0 0.0 0.0 alpha 0.4;
gfx mod g_e mesh_TorsoFitted surface mat tissue;
gfx mod g_e mesh_LungLeft surface mat muscle;
gfx mod g_e mesh_LungRight surface mat muscle;
gfx mod g_e mesh_TorsoFitted line mat black;
gfx mod g_e mesh_LungLeft line mat black;
gfx mod g_e mesh_LungRight line mat black;

## CUT PLANE
##gfx read node 'cut_plane' reg cut_plane;
##gfx read elem 'cut_plane' reg cut_plane;
#gfx mod g_e cut_plane surface mat plane_mat;
##gfx mod g_e cut_plane line none;
#gfx mod g_e cut_plane line mat plane_mat;

gfx edit scene;
gfx cre wind;
gfx node_tool edit select;

#gfx list all_commands
gfx modify window 1 layout simple ortho_axes z -y eye_spacing 0.25 width 768 height 768;
gfx modify window 1 set perturb_lines;
gfx modify window 1 background colour 1 1 1 texture none;
gfx modify window 1 view parallel eye_point -420.697 -409.697 668.681 interest_point 164 175 -158.206 up_vector 0.5 0.5 0.707107 view_angle 40 near_clipping_plane 11.6939 far_clipping_plane 4179.02 relative_viewport ndc_placement -1 1 2 2 viewport_coordinates 0 0 1 1;
gfx modify window 1 overlay scene none;
gfx modify window 1 set transform_tool current_pane 1 std_view_angle 40 perturb_lines no_antialias depth_of_field 0.0 fast_transparency blend_normal;

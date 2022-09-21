$group = 'fittedTorso';

# Extract the nodal derivatives as vector fields:
gfx def field dx_ds1 node_value fe_field coordinates d/ds1 version 1;
gfx def field dx_ds2 node_value fe_field coordinates d/ds2 version 1;

gfx mod g_e $group node_points glyph arrow_solid size "0*3*3" scale_factors "0.3*0*0" orientation dx_ds1 selected_mat silver draw_selected;

gfx mod g_e $group node_points glyph arrow_solid size "0*3*3" scale_factors "0.3*0*0" orientation dx_ds2 selected_mat silver draw_selected



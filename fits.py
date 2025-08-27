import os
from astropy.io import fits
import numpy as np

from device_types import Stages
from multigo import MultiGoSettings, MultiGoRunVariable
from value_types import AnyValue

# save the settings to the file
def save_settings(path, variables, stages, images, multigo_settings=None, window_layout=None, overwrite=True):
    dc = stages.dc
    stages = stages.stages

    # create the primary HDU
    primary_hdu = fits.PrimaryHDU()

    # save the window layout
    primary_hdu.header['layout'] = str(window_layout)

    # save the camera images
    image_hdu = fits.ImageHDU()
    if images is not None:
        image_hdu.data = images.astype(np.uint16)

    # add the stages
    stage_columns = []

    # add the stage name column
    stage_names = [stage.name for stage in stages]
    stage_names.insert(0, 'dc')
    stage_columns.append(fits.Column(name='stage_name', format='A20', array=stage_names))
    
    # add the enabled column
    enabled = [stage.enabled for stage in stages]
    enabled.insert(0, True)  # dc is always enabled
    stage_columns.append(fits.Column(name='enabled', format='L', array=enabled))

    # add the id column
    ids = [stage.id for stage in stages]
    ids.insert(0, 'dc')
    stage_columns.append(fits.Column(name='id', format='A36', array=ids))

    # add columns for each variable in the gui
    for i, variable in enumerate(variables):
        col = variable.fits_column()

        # gather the column of data
        data = []

        # add the dc value
        dc_value = getattr(dc, variable.id)
        data.append(variable.value_type.constant(dc_value).to_array())

        # add the stage values
        for stage in stages:
            value = getattr(stage, variable.id)
            data.append(value.to_array())

        col.array = np.stack(data)
        stage_columns.append(col)

    # create a fits table hdu for the stages
    stages_hdu = fits.BinTableHDU.from_columns(stage_columns)

    # add the multigo settings
    multigo_columns = []
    if multigo_settings is not None:
        run_variables = multigo_settings.run_variables
        fluorescence_threshold = multigo_settings.fluorescence_threshold

        # add the stage ids
        stage_ids = [var.stage_id for var in run_variables]
        multigo_columns.append(fits.Column(name='stage_id', format='A36', array=stage_ids))

        # add the variable ids
        variable_ids = [var.variable_id for var in run_variables]
        multigo_columns.append(fits.Column(name='variable_id', format='A36', array=variable_ids))

        # add the start and end values
        start_values = [AnyValue(var.start).to_array() for var in run_variables]
        multigo_columns.append(fits.Column(name='start_value', format='4D', dim='(4)', array=start_values))
        end_values = [AnyValue(var.end).to_array() for var in run_variables]
        multigo_columns.append(fits.Column(name='end_value', format='4D', dim='(4)', array=end_values))

        # add the steps
        step_values = [var.steps for var in run_variables]
        multigo_columns.append(fits.Column(name='steps', format='K', array=step_values))

        # create a fits table hdu for the multigo settings
        multigo_hdu = fits.BinTableHDU.from_columns(multigo_columns)
        multigo_hdu.header['fluorthr'] = fluorescence_threshold
    else:
        multigo_hdu = fits.BinTableHDU.from_columns([])

    # make sure path is unique if not overwriting
    if not overwrite:
        path = uniquify(path)

    # write the HDU array
    hdul = fits.HDUList([primary_hdu, image_hdu, stages_hdu, multigo_hdu])
    hdul.writeto(path, overwrite=True)

# load the settings from the file
def load_settings(path, window):
    # read the fits file
    primary_hdu, images_hdu, stages_hdu, multigo_hdu = fits.open(path)

    # load the window layout
    layout = eval(primary_hdu.header['layout'])
    if layout is not None:
        window.restoreState(layout)

    # load the camera images
    images = images_hdu.data
    if images is not None:
        window.plots_gui.update_images(images)

    # load the stages data
    stages_data = stages_hdu.data

    # update the dc widgets with the values from the file
    for dc_widget in window.stages_gui.dc_widgets:
        if dc_widget.variable.id in stages_data.names:
            array = stages_data[0][dc_widget.variable.id]
            value = dc_widget.variable.value_type.from_array(array)
            dc_widget.set_value(value)
        else:
            print(f"Warning: '{dc_widget.variable.id}' not in dc data")
    stages_data = stages_data[1:]  # skip the first row which is the dc

    # clear the current stage widgets
    for i in reversed(range(len(window.stages_gui.stages))):
        window.stages_gui.delete_stage(i)
    window.stages_gui.stages.clear()

    # create new stage widgets based on the loaded data
    for i, stage_row in enumerate(stages_data):
        # create new column of widgets for the stage
        stage_name = stage_row['stage_name'].strip()
        enabled = stage_row['enabled']
        id = stage_row['id'].strip()
        window.stages_gui.insert_stage(len(window.stages_gui.stages), name=stage_name, enabled=enabled, id=id)

        # fill the stage widgets with the values from the file
        for widget in window.stages_gui.stages[i].widgets:
            if widget.variable.id in stages_data.names:
                array = stage_row[widget.variable.id]
                value = widget.variable.value_type.from_array(array)
                widget.set_value(value)
            else:
                print(f"Warning: Unknown variable '{widget.variable.id}' in stage {i} data")

    # load the multigo settings
    if len(multigo_hdu.data) > 0:
        multigo_settings = MultiGoSettings([], 0.0)
        for row in multigo_hdu.data:
            multigo_settings.run_variables.append(MultiGoRunVariable(
                row['stage_id'],
                row['variable_id'],
                AnyValue.from_array(row['start_value']).to_value(),
                AnyValue.from_array(row['end_value']).to_value(),
                row['steps']
            ))
        multigo_settings.fluorescence_threshold = multigo_hdu.header['fluorthr']
        window.stages_gui.multigo_settings = multigo_settings

# turns a file path into a unique one by adding a number to the end
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

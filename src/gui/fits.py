'''
fits.py: this file has the code for saving and loading the gui state as fits files
'''

import numpy as np
import os

from astropy.io import fits

from src.device.ai import AiSettings
from src.device.multigo import MultiGoSettings
from src.gui.run_variables import RunVariable
from src.value_types import AnyValue

# save the settings to the file. this function takes in the different parts of the file instead of just the gui window so it can be called from the device after each experiment without modifying the gui
def save_settings(path, variables, stages, images, multigo_settings=None, ai_settings=None, window_layout=None, overwrite=True):
    stages = [stages.dc] + stages.stages  # include the dc as the first stage

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
    stage_columns.append(fits.Column(name='stage_name', format='A20', array=stage_names))
    
    # add the enabled column
    enabled = [stage.enabled for stage in stages]
    stage_columns.append(fits.Column(name='enabled', format='L', array=enabled))

    # add the id column
    ids = [stage.id for stage in stages]
    stage_columns.append(fits.Column(name='id', format='A36', array=ids))

    # add columns for each variable in the gui
    for i, variable in enumerate(variables):
        col = variable.fits_column()

        # initialize the data array with the dc value
        data = []

        # add the stage values
        for stage in stages:
            value = getattr(stage, variable.id)
            data.append(value.to_array())

        col.array = np.stack(data)
        stage_columns.append(col)

    # create a fits table hdu for the stages
    stages_hdu = fits.BinTableHDU.from_columns(stage_columns)

    # create the multigo settings hdu
    if multigo_settings is not None:
        multigo_hdu = run_variable_list_to_hdu(multigo_settings.run_variables)
        multigo_hdu.header['fluorthr'] = multigo_settings.fluorescence_threshold
    else:
        multigo_hdu = fits.BinTableHDU.from_columns([])

    # create the AI settings HDU
    ai_hdu = fits.BinTableHDU.from_columns([])
    if ai_settings is not None:
        ai_hdu.header['pretrain'] = ai_settings.pre_training_steps
        ai_hdu.header['train'] = ai_settings.training_steps
        ai_hdu.header['learner'] = ai_settings.learner


    # make sure path is unique if not overwriting
    if not overwrite:
        path = uniquify(path)

    # write the HDU array
    hdul = fits.HDUList([primary_hdu, image_hdu, stages_hdu, multigo_hdu, ai_hdu])
    hdul.writeto(path, overwrite=True)

# load the settings from a fits file into the gui
def load_settings(path, window):
    # read the fits file
    primary_hdu, images_hdu, stages_hdu, multigo_hdu, ai_hdu = fits.open(path)

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

    # update the dc and hidden widgets with the values from the file
    dc_widgets = window.stages_gui.dc_widgets
    hidden_widgets = window.hidden_gui.widgets
    for variable_id in stages_data.names:
        array = stages_data[0][variable_id]
        if variable_id in dc_widgets:
            value = dc_widgets[variable_id].variable.value_type.from_array(array)
            dc_widgets[variable_id].set_value(value)
        elif variable_id in hidden_widgets:
            value = hidden_widgets[variable_id].variable.value_type.from_array(array)
            hidden_widgets[variable_id].set_value(value)

    # skip the first row which is the dc
    stages_data = stages_data[1:]

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
        for variable_id, widget in window.stages_gui.stages[i].widgets.items():
            if variable_id in stages_data.names:
                array = stage_row[variable_id]
                value = widget.variable.value_type.from_array(array)
                widget.set_value(value)
            else:
                print(f"Warning: Unknown variable '{widget.variable.id}' in stage {i} data")

    # load the multigo settings
    if len(multigo_hdu.data) > 0:
        run_variables = run_variable_hdu_to_list(multigo_hdu)
        fluorescence_threshold = multigo_hdu.header['fluorthr']
        window.stages_gui.multigo_settings = MultiGoSettings(run_variables, fluorescence_threshold)

    # load the ai settings
    if ai_hdu.header.get("pretrain") is not fits.card.Undefined:
        learner = ai_hdu.header.get('learner', 'neural_net')  # default to neural_net if not found
        window.stages_gui.ai_settings = AiSettings(
            ai_hdu.header['pretrain'],
            ai_hdu.header['train'],
            learner
        )

# saves run variables to a fits file
def save_run_variables(file_path, run_variables):
    hdu = run_variable_list_to_hdu(run_variables)
    hdu.writeto(file_path, overwrite=True)

# loads run variables from a fits file
def load_run_variables(file_path):
    primary_hdu, table_hdu = fits.open(file_path)
    return run_variable_hdu_to_list(table_hdu)

# creates a table hdu of run variables
def run_variable_list_to_hdu(run_variables):
    columns = [
        fits.Column(name='stage_id', format='A36', array=[var.stage_id for var in run_variables]),
        fits.Column(name='variable_id', format='A36', array=[var.variable_id for var in run_variables]),
        fits.Column(name='start_value', format='4D', dim='(4)', array=[AnyValue(var.start).to_array() for var in run_variables]),
        fits.Column(name='end_value', format='4D', dim='(4)', array=[AnyValue(var.end).to_array() for var in run_variables]),
        fits.Column(name='steps', format='K', array=[var.steps for var in run_variables])
    ]
    return fits.BinTableHDU.from_columns(columns)

# loads run variables from a fits table hdu
def run_variable_hdu_to_list(hdu):
    run_variables = []
    for row in hdu.data:
        run_variables.append(RunVariable(
            stage_id=row['stage_id'].strip(),
            variable_id=row['variable_id'].strip(),
            start=AnyValue.from_array(row['start_value']).to_value(),
            end=AnyValue.from_array(row['end_value']).to_value(),
            steps=row['steps']
        ))
    return run_variables

# turns a file path into a unique one by adding a number to the end
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

for tid in range(len(stages)):
    stagetime = stages[tid].time.value()
    timesteps=int(stagetime/self.timestep)
    t_range = np.arange(timesteps)
    for row in range(len(self.devicenames['DAC'])):
        box_val = stages[tid].boxes[row].value()
        if box_val > 0: 
            box_val = dac_conversions[row].getval(box_val)
            
        step_initial = timestepstilnow - prefire_timesteps[row]
        step_final = step_initial + timesteps

        if (box_val < -25):
            rstart = dac_conversions[row].getval(stages[tid].boxes[row].RStart)
            rend = dac_conversions[row].getval(stages[tid].boxes[row].REnd)
            temp = rstart + ((rend-rstart)/timesteps) * t_range
            
        elif ((box_val>=0.0) and (box_val<=5.0)):
            temp = box_val * np.ones(timesteps)

        data[step_initial : step_final, row] = np.round(temp * MAX_INT/5.0).astype(int)#[:]
    timestepstilnow+=timesteps
    self.data=data
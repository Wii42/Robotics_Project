def init_gsensors_record(self):
    data = open("Gsensors.csv", "w")
    if data is None:
        print('Error opening data file!\n')
        return None

    # write header in CSV file
    data.write('step,')
    for i in range(self.robot.GROUND_SENSORS_COUNT):
        data.write('gs' + str(i) + ',')
    data.write('\n')
    return data


def record_gsensors(self, data, gs):
    # write a line of data
    data.write(str(self.counter.get_steps()) + ',')
    for v in gs:
        data.write(str(v) + ',')
    data.write('\n')
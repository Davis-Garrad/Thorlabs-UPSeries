import pyvisa as pv
import serial.tools.list_ports as lp

def get_device_by_tty(tty, rm):
    resources = rm.list_resources()
    for j in resources:
        if(tty in j and '::INSTR' in j):
            dev = rm.open_resource(j)
            return dev
           
class UPLED:
    def __init__(self, sn=''):
        '''Creates an UPLED device, optionally choosing the one with serial number sn'''
        rm = pv.ResourceManager()
        ports = lp.comports()
        available_port = ''
        chosen_port = ''
        for i in ports:
            desc = i.description
            if('upLED' in desc):
                # We have an UPLED
                available_port = i.device
                
                if(sn == ''):
                    chosen_port = available_port
                    break
                else:
                    # open a connection, check SN
                    if(sn == dev_sn):
                        chosen_port = available_port 
                        dev = get_device_by_tty(i.device, rm)
                        dev_sn = dev.query('LEDINFOS?').split('"')[1]
                        dev.close()
                        break

        self.dev = get_device_by_tty(chosen_port, rm)

        print('Connected to UPLED. Info:')
        print(self.get_info())

    def get(self, cmd):
        '''extracts the actual useful info from a query'''
        raw = self.dev.query(cmd)
        # Has form '0,[DATA]\n' response
        return raw.split(',')[1][:-1]

    def get_info(self):
        name = self.get('LEDINFON?')
        sn = self.get('LEDINFOS?')
        I_lim = self.get('LEDINFOL?')
        voltage = self.get('LEDINFOU?')
        onstate = self.get('LED?')

        data = { 'name': name, 'serial': sn, 'current_limit [A]': I_lim, 'voltage [V]': voltage, 'on_state': onstate }
        return data

    def set_current(self, current):
        '''Sets the current, in A'''
        self.dev.query(f'ILED {current}')
        return self.get_current()

    def get_current(self):
        return self.get('ILED?')

    def set_onstate(self, onstate):
        '''Turns the device on/off (1/0, True/False)'''
        self.dev.query(f'LED {int(onstate)}')
        return self.get_onstate()

    def get_onstate(self):
        return self.get('LED?')

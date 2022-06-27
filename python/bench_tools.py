from logging import exception
#from lan import Lan
import struct
import vxi11
import numpy as np
from scipy.signal import butter, lfilter
import pyvisa
from PyQt5.QtWidgets import *
import bz2
import csv

class Hioki:
    def __init__(self,ip,port,timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.lan = Lan(timeout)

    def open_port(self):
        self.lan = Lan(self.timeout)
        if not self.lan.open(self.ip,self.port):
            return False
        
        else:            
            return True
          
    def close_port(self):
        self.lan.close()
        print("Closing port")
    
    def meas(self,channel):
        command = ':MEAS? ' + str(channel) + '\r\n'
        msgBuf = self.lan.SendQueryMsg(command, 1)
        return msgBuf

class Delta:
    def __init__(self,ip,port,timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        # self.lan = Lan(timeout) 
        self.volt='0.0'
        self.cur='0.0'  
        self.power = '0.0'  

    def open_port(self):
        self.lan = Lan(self.timeout)
        if not self.lan.open(self.ip,self.port):
            return False
        else:
            return True                
   
    def close_port(self):
        self.lan.close()
        print("Closing port")
    
    def meas_volt(self):
        msgBuf = self.lan.SendQueryMsg('MEAS:VOLT?' + '\n', 1) 
        self.volt = msgBuf

    def meas_cur(self):
        msgBuf = self.lan.SendQueryMsg('MEAS:CUR?' + '\n', 1) 
        self.cur = msgBuf

    def meas_power(self):
        msgBuf = self.lan.SendQueryMsg('MEAS:POW?' + '\n', 1) 
        self.power = msgBuf

    def set_volt(self,voltage): 
        self.lan.sendMsg('SOUR:VOL '+str(voltage)+ '\n')  

    def set_cur_pos(self,current):
        self.lan.sendMsg('SOUR:CUR ' + str(current) + '\n')   

    def set_cur_neg(self,current):
        self.lan.sendMsg('SOUR:CUR:NEG '+str(current)+ '\n')                

    def enable_out(self):
        self.lan.sendMsg('OUTP ON'+ '\n') 

    def disable_out(self):
        self.lan.sendMsg('OUTP OFF'+ '\n')

    def status_out(self):
        msgBuf = self.lan.SendQueryMsg('OUTP?' + '\n', 1) 
        return msgBuf

    def update(self):
        self.meas_volt()

    def set_control_eth(self):
        self.lan.sendMsg('SYST:REM:CV Ethernet' + '\n')
        self.lan.sendMsg('SYST:REM:CC Ethernet' + '\n')

    def set_control_local(self):
        self.lan.sendMsg('SYST:REM:CV Front' + '\n')
        self.lan.sendMsg('SYST:REM:CC Front' + '\n')
        
class Yokogawa:
    def __init__(self,ip):
        self.ip = ip
        
    def request_wave(self,channel,start,stop):
       
        instr = vxi11.Instrument(self.ip)
        instr.write(":WAVeform:TRACE " +str(channel)) 
        instr.write(":WAVeform:FORMat ASCii")
        instr.write(":WAVeform:STARt "+ str(start))
        instr.write(":WAVeform:END "+ str(stop))
        data = instr.ask(":WAVeform:SEND?")
        instr.close()
        return data
		
		
    def show_file_data(self, f_name='yokogawa_all.csv'):
        f = open(f_name, 'r')
		
    def request_wave_word(self,channel,start,stop):
       
        instr = vxi11.Instrument(self.ip)
        instr.write(":WAVeform:TRACE " +str(channel)) 
        instr.write(":WAVeform:FORMat WORD")
        instr.write(":WAVeform:STARt "+ str(start))
        instr.write(":WAVeform:END "+ str(stop))
        data = instr.ask_raw(str(":WAVeform:SEND?").encode("utf-8"))
        instr.close()
        return data

    def request_yscale(self,channel):
        instr = vxi11.Instrument(self.ip)
        VDIV = instr.ask(":CHANnel"+str(channel)+":VDIV?").split()
        instr.close()
        return(str(float(VDIV[1])))   

    def request_xscale(self):
        instr = vxi11.Instrument(self.ip)
        scale = instr.ask(":TIMebase:TDIV?").split()
        instr.close()
        return(str(float(scale[1])))   

    def request_length(self):
        instr = vxi11.Instrument(self.ip)
        scale = instr.ask(":WAVeform:LENGth?").split()
        instr.close()
        return(str(float(scale[1]))) 

    def request_range(self):
        instr = vxi11.Instrument(self.ip)
        data = instr.ask(":WAVeform:RANGe?").split()
        instr.close()
        return(str(float(data[1]))) 
    
    def data_calc(self,channel,start,stop):

        data_raw = self.request_wave_word(channel,start,stop)
        range_wave = float(self.request_range())
        length_array = len(data_raw)-(data_raw[1]-48)-3
        start_array = 2+data_raw[1]-48
        array_word = np.empty(stop-start)
        data_temp=[1,2]

        for x in range(int(length_array/2)):

            data_temp[0]=data_raw[start_array+(2*x)]
            data_temp[1]=data_raw[start_array+1+(2*x)]
            array_word[x] = (struct.unpack('h',bytearray(data_temp))[0]*range_wave/3200)

        return array_word

 

    def calc_data_from_array(self,data_raw,range_wave):

        length_array = len(data_raw)-(data_raw[1]-48)-3
        start_array = 2+data_raw[1]-48
        array_word = []
        data_temp=[1,2]

        for x in range(int(length_array/2)):

            data_temp[0]=data_raw[start_array+(2*x)]
            data_temp[1]=data_raw[start_array+1+(2*x)]
            array_word.append(struct.unpack('h',bytearray(data_temp))[0]*range_wave/3200)

        return array_word

    def set_timebase(self,timebase):
        instr = vxi11.Instrument(self.ip)
        instr.write(":TIMebase:TDIV "+timebase)
        print(instr.ask(":TIMebase:TDIV?"))
        instr.close()

    def single_shot(self):
        instr = vxi11.Instrument(self.ip)
        instr.ask(":SSTart? 0")
        instr.close()

    def auto_trigger(self):
        instr = vxi11.Instrument(self.ip)
        instr.write(":TRIGger:MODE AUTO")
        instr.close()
    
    def normal_trigger(self):
        instr = vxi11.Instrument(self.ip)
        instr.write(":TRIGger:MODE NORM")
        instr.close()

    def start_aq(self):
        instr = vxi11.Instrument(self.ip)
        instr.write(":STARt")
        instr.close()

    def stop_aq(self):
        instr = vxi11.Instrument(self.ip)
        instr.write(":STOP")
        instr.close()


    def set_acq_length(self,length):
        instr = vxi11.Instrument(self.ip)
        instr.write(":ACQuire:RLENgth "+str(length))
        print(instr.ask(":ACQuire:RLENgth?"))
        instr.close()

    def get_esr(self):
        instr = vxi11.Instrument(self.ip)
        print(instr.ask(":STATus:EESR?"))
        instr.close()
    
    def get_eese(self):
        instr = vxi11.Instrument(self.ip)
        print(instr.ask(":STATus:EESE?"))
        instr.close()

    def get_filter(self):
        instr = vxi11.Instrument(self.ip)
        print(instr.ask(":STATus:FILT?"))
        instr.close()

    def set_filter(self,int,cmd):
        instr = vxi11.Instrument(self.ip)
        instr.write(f":STATus:FILT{int} {cmd}")
        instr.close()

    def get_status(self):
        instr = vxi11.Instrument(self.ip)
        msg=instr.ask(f"STATus:CONDition?")
        instr.close()
        return msg
    
    def get_wave_length(self,channel):
        instr = vxi11.Instrument(self.ip)
        instr.write(":WAVeform:TRACE " +str(channel))
        length=instr.ask("WAVeform:LENGth?").split()
        instr.close()
        return (str(float(length[1])))
        
class Keysight:
    def __init__(self,adres):
        self.adres = adres
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.adres)
        self.instrument.timeout=10000

    def write(self,data):
        self.instrument.write(data)
    
    def query(self,data):
        msg = self.instrument.query(data)
        return msg
    
    def read_binary(self,cmd):
        msg = self.instrument.query_binary_values(cmd)
        return msg
    
    def read_bode_plot(self):
        self.instrument.write(':FRAN:DATA?')
        msg = str(self.instrument.read_raw())
        return msg
    
    def proces_bode_plot_to_file(self,data,location_name):
        datanew =data.split('xb0)')[1]
        datanew = data.split('\\n')
        data_sorted=[]
        gain_array=[]
        phase_array = []
        freq_array = []

        for x in range(1,len(datanew)):
            data_sorted.append(datanew[x].split(',',5))

        for x in range (len(data_sorted)-2):
            freq_array.append(float(data_sorted[x][1]))
            gain_array.append(float(data_sorted[x][3]))
            phase_array.append(float(data_sorted[x][4]))
        
        f = open(location_name,'w')
        f.write(f"{freq_array}'\n'")
        f.write(f"{gain_array}'\n'")
        f.write(f"{phase_array}'\n'")
        f.close()

    def open_bode_file(self,location):
        f=open(location,'r')
        freq_array = f.readline()
        gain_array = f.readline()
        phase_array = f.readline()
        f.close

        tmp=[]

        freq_array = freq_array.replace('[','')
        freq_array = freq_array.replace(']','')
        freq_array = freq_array.replace('\n','')
        freq_array = freq_array.replace("'",'')
        freq_array = freq_array.split(',')

        gain_array = gain_array.replace('[','')
        gain_array = gain_array.replace(']','')
        gain_array = gain_array.replace('\n','')
        gain_array = gain_array.replace("'",'')
        gain_array = gain_array.split(',')

        phase_array = phase_array.replace('[','')
        phase_array = phase_array.replace(']','')
        phase_array = phase_array.replace('\n','')
        phase_array = phase_array.replace("'",'')
        phase_array = phase_array.split(',')

        for x in range(len(freq_array)):
            tmp.append(float(freq_array[x]))

        freq_array=tmp.copy()
        tmp.clear()

        for x in range(len(gain_array)):
            tmp.append(float(gain_array[x]))
        
        gain_array=tmp.copy()
        tmp.clear()
        
        for x in range(len(phase_array)):
            tmp.append(float(phase_array[x]))
        
        phase_array=tmp.copy()
        tmp.clear()

        return freq_array,gain_array,phase_array

    def bode_settings(self,start,stop,points,volt,chin,chout):
        self.write(f":FRANalysis:FREQuency:STARt {str(start)}Hz" )
        self.write(f":FRANalysis:FREQuency:STOP {str(stop)}Hz" )
        self.write(f":FRANalysis:SOURce:INPut CHAN{chin}")
        self.write(f":FRANalysis:SOURce:OUTPut CHAN{chout}")
        self.write(f":FRANalysis:WGEN:VOLT {volt}")
        self.write(f":FRANalysis:SWEep:POINts {points}")

    def bode_run(self):
        self.write(":FRANalysis:RUN")

    def close(self):
        self.instrument.close()

    def get_wave_form(self,channel):
        
        self.instrument.open()
        self.instrument.write("WAVeform:FORMat WORD")
        self.instrument.write(":WAVeform:BYTeorder LSBFirst")
        self.instrument.write(":WAVeform:UNSigned 0")
        self.instrument.write(":WAVeform:POINts MAX")
        self.instrument.write(":WAVeform:POINts:MODE NORMAL")
        Wav_Data = np.array(self.instrument.query_binary_values(':WAVeform:SOURce CHANnel' + str(channel) + ';DATA?', "h", False))
        # aantal_punten=int((self.instrument.query(":WAVeform:POINts?")))
        # x_reference = float(self.instrument.query(":WAVeform:XREFerence?"))
        x_increment = float(self.instrument.query(":WAVeform:XINCrement?"))
        x_origin = float(self.instrument.query(":WAVeform:XORigin?"))
        y_increment = float(self.instrument.query(":WAVeform:YINCrement?"))
        y_origin = float(self.instrument.query(":WAVeform:YORigin?"))
        y_reference = float(self.instrument.query(":WAVeform:YREFerence?"))
        self.close()

        time_val=[]
        voltage=[]
        for i in range(0, len(Wav_Data)):
            time_val.append( x_origin + (i * x_increment))
            voltage.append(((Wav_Data[i] - y_reference) * y_increment) + y_origin)

        return time_val,voltage

class Rigol:
    def __init__(self,adres):
        self.adres = adres
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.adres)
        self.instrument.timeout=10000

    def write(self,data):
        self.instrument.write(data)
    
    def query(self,data):
        msg = self.instrument.query(data)
        return msg

class general:
    def calc_rms(value):
        rms = np.sqrt(np.mean(np.square(value)))
        return rms

    def calc_mean(value):
        mean = np.mean(value)
        return mean

    def process_scope_saved_data(location):
        f = open(location,'r')
        data_raw = f.read()
        tmp = data_raw.splitlines()
        xscale = tmp[0]
        xscale = float(xscale[7:])
        tmp[1] = tmp[1].replace('[','')
        tmp[1] = tmp[1].replace(']','')
        data=[]
        spl = tmp[1].split(", ")
        for x in range(len(spl)):
            data.append(float(spl[x]))
        y1 = np.array(data)
        x1 = np.array([float(x*xscale) for x in range(y1.__len__())])
        return y1,x1

    def process_multi_channel_data(location):
        f = open(location,'r')
        data_raw = f.read()
        tmp = data_raw.splitlines()
        xscale = tmp[0]
        xscale = float(xscale[7:])
        aant_channels = int(tmp[1][14:])

        data=[]
        data_proc=[0]*aant_channels
        
        for x in range(aant_channels):
            tmp[x+2] = tmp[x+2].replace('[','')
            tmp[x+2] = tmp[x+2].replace(']','')

            spl = tmp[x+2].split(", ")
            for y in range(len(spl)):
                data.append(float(spl[y]))
            data_proc[x]=data.copy()  
            data.clear()   
        y1 = np.array(data_proc[0]) 
        x1 = np.array([float(x*xscale) for x in range(y1.__len__())])   
        return data_proc,x1

    def calc_fft(time_array,value_array):
        aant_samples = len(time_array)
        t_sample = time_array[aant_samples-1]
        f_sample = 1/(t_sample/aant_samples)

        data_fft = np.fft.fft(value_array)
        data_N = len(data_fft)
        n = np.arange(data_N)
        data_t = data_N/f_sample
        freq = n/data_t 
        fft_data=(np.abs(data_fft/(data_N/2)))
        return freq,fft_data

    def butter_lowpass_filter_datascope(data_array,time_array, cutoff, order=5):
        aant_samples = len(time_array)
        t_sample = time_array[aant_samples-1]
        f_sample = 1/(t_sample/aant_samples)
        nyq = 0.5 * f_sample
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = lfilter(b, a, data_array)
        return y

    def store_compressed_scope_data(xscale,channels,data,location):
        try:
            with bz2.open(location,'wt') as f:
                f.write(xscale)
                f.write(channels)
                f.write(data)
                f.close()
        except:
            print("Can't store compressed file")

    def open_compressed_scope_data(location):
        try:
            with bz2.open(location,'rt') as f:
                data_raw =f.read()
                f.close()
            tmp = data_raw.splitlines()
            xscale = tmp[0]
            xscale = float(xscale[7:])
            aant_channels = int(tmp[1][14:])

            data=[]
            data_proc=[0]*aant_channels
        
            for x in range(aant_channels):
                tmp[x+2] = tmp[x+2].replace('[','')
                tmp[x+2] = tmp[x+2].replace(']','')

                spl = tmp[x+2].split(", ")
                for y in range(len(spl)):
                    data.append(float(spl[y]))
                data_proc[x]=data.copy()  
                data.clear()   
            y1 = np.array(data_proc[0]) 
            x1 = np.array([float(x*xscale) for x in range(y1.__len__())])   
            return data_proc,x1
        except:
            print("Can't open compressed file")

    def open_bode_file_rigol(locatie):
        try:
            rows = []
            freq=[]
            gain=[]
            phase=[]

            with open(locatie, 'r',newline='') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    rows.append(row)

            for x in range(len(rows)-6):
                k = float(rows[x+5][0])
                freq.append(k)
                k = float(rows[x+5][1])
                gain.append(k)
                k = float(rows[x+5][2])
                phase.append(k)
            return freq,gain,phase
        except:
            print("Can't open bode file")
    
    def open_bode_file(self,location):
        f=open(location,'r')
        freq_array = f.readline()
        gain_array = f.readline()
        phase_array = f.readline()
        f.close

        tmp=[]

        freq_array = freq_array.replace('[','')
        freq_array = freq_array.replace(']','')
        freq_array = freq_array.replace('\n','')
        freq_array = freq_array.replace("'",'')
        freq_array = freq_array.split(',')

        gain_array = gain_array.replace('[','')
        gain_array = gain_array.replace(']','')
        gain_array = gain_array.replace('\n','')
        gain_array = gain_array.replace("'",'')
        gain_array = gain_array.split(',')

        phase_array = phase_array.replace('[','')
        phase_array = phase_array.replace(']','')
        phase_array = phase_array.replace('\n','')
        phase_array = phase_array.replace("'",'')
        phase_array = phase_array.split(',')

        for x in range(len(freq_array)):
            tmp.append(float(freq_array[x]))

        freq_array=tmp.copy()
        tmp.clear()

        for x in range(len(gain_array)):
            tmp.append(float(gain_array[x]))
        
        gain_array=tmp.copy()
        tmp.clear()
        
        for x in range(len(phase_array)):
            tmp.append(float(phase_array[x]))
        
        phase_array=tmp.copy()
        tmp.clear()

        return freq_array,gain_array,phase_array

from re import X
import sys
import os
from pathlib import Path
from tkinter import Label
from numpy import int32, uint32
from sympy import true
import matplotlib.pyplot as plt
# from lan import Lan
#import precan
#import preCANopen

# from hioki_com import Window as HIOKI_COM
from bench_tools import Hioki as Hioki
from bench_tools import Delta as Delta
from bench_tools import Yokogawa as Yokogawa
from bench_tools import general as general

import threading
import time
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,QLabel,QLineEdit,QDialog,
                            QMenuBar, QPushButton, QWidget,QFileDialog)

# import pygame

class powermodule:
    def __init__(self,id):
        try:
            
            self.preCANopenObj = preCANopen.preCANopen()
            self.preCANopenObj.getListOfPCANChannels()
            # self.preCANopenObj.connect('pcan',self.preCANopenObj.getListOfPCANChannels()[0])
            self.node = self.preCANopenObj.addNode(id, "C:/Users/Mike/Documents/EDS Files/EVDC25kw.eds")
            self.voltage_setpoint = 0
            self.voltage_in_meas = 0
            self.voltage_out_meas = 0
            self.current_setpoint = 0
            self.current_in_meas = 0
            self.current_out_meas = 0
            self.id=id
            self.status=0

            self.powermodele_OTP = 0x800
            self.powermodele_OCP = 0x100000
            self.powermodele_PWR = 0x2
            self.powermodele_ENABLED = 0x1
            self.powermodele_OVP_OUT=0x200000
            self.powermodele_OVP_IN=0x20000
            self.powermodele_CAN=0x8000
            
        except:
            print("CANBUS error, no communication with powermoduel possible")
            # exit()

    def update(self):

        self.read_status()

    def enable(self):
        self.node.sdo['Enable disable'][1].raw=0x01
        time.sleep(0.250)
        
    def disable(self):
        self.node.sdo['Enable disable'][1].raw=0x00

    def read_status(self):
        msgBuf = self.node.sdo['Status latched'][1].raw
        return(msgBuf)

    def voltage_out(self):
        self.voltage_out_meas = (self.node.sdo['DC output voltage'][2].raw)/1000

    def current_out(self):
        self.current_out_meas = (self.node.sdo['DC output current'][2].raw)/1000

    def voltage_in(self):
        self.voltage_in_meas = (self.node.sdo['DC input voltage'][2].raw)/1000

    def current_in(self):
        self.current_in_meas = (self.node.sdo['DC input current'][2].raw)/1000

    def disable_uvp(self):
        message = 'inputUVP(0)'
        for i in range(len(message)):
            self.__node.sdo['OS Prompt']['StdIn'].raw = ord(message[i])
            self.__node.sdo['OS Prompt']['StdIn'].raw = ord('\n')

    def mode_1kv(self):
        self.node.sdo['Output mode'].raw=0x01

    def mode_500V(self):
        self.node.sdo['Output mode'].raw=0x00

    def read_omr(self):
        msgBuf = self.node.sdo['Output mode'].raw
        return(msgBuf)

    def send_iout_setpoint(self,setpoint):
        setpoint = setpoint.replace(',','.')
        tmp = int(float(setpoint)*1000)
        self.node.sdo['DC output current'][3].raw = (int32(tmp))

    def send_uout_setpoint(self,setpoint):
        setpoint = setpoint.replace(',','.')
        tmp = int(float(setpoint)*1000)
        self.node.sdo['DC output voltage'][3].raw = (int32(tmp))

    def read_iout_actual_setpoint(self):
        self.current_setpoint = (self.node.sdo['DC output current'][4].raw)/1000

    def read_uout_actual_setpoint(self):
        self.voltage_setpoint = (self.node.sdo['DC output voltage'][4].raw)/1000

class com_setting_window(QWidget):
   
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Hioki COM settings")

        layout = QGridLayout()

        lbl_ip = QLabel("Ip:")
        self.ip = QLineEdit("10.0.0.110")

        lbl_port = QLabel("Port:")
        self.port = QLineEdit("3390")

        self.btn_ok = QPushButton("Ok")

        # self.btn_ok.clicked.connect(self.btn_ok_clicked)

        layout.addWidget(lbl_ip,0,0)
        layout.addWidget(self.ip,0,1)
        layout.addWidget(lbl_port,1,0)
        layout.addWidget(self.port,1,1)
        layout.addWidget(self.btn_ok,3,0)

        self.setLayout(layout)

class canid_window(QWidget):
   
    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        lbl_id = QLabel("Can ID(hex):")
        self.id = QLineEdit("30")
        self.btn_ok = QPushButton("Ok")

        layout.addWidget(lbl_id,0,0)
        layout.addWidget(self.id,0,1)
        layout.addWidget(self.btn_ok,3,0)

        self.setLayout(layout)

class powermodule_group_list:
    def __init__(self,name,id):

        self.name = name
        self.id=id
        self.cnt=0

        self.powermodule = powermodule(id)

        self.button_off_color = "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+"QPushButton:disabled {color: rgb(0, 0, 0)}"
        self.button_on_color = "QPushButton:disabled {background-color: rgb(0, 255, 0)}"+"QPushButton:disabled {color: rgb(0, 0, 0)}"

        self.groupBox = QGroupBox("Power Unit")
        gb_font = self.groupBox.font()
        gb_font.setPointSize(12)
        gb_font.setBold(True)
        self.groupBox.setFont(gb_font)
        layout = QGridLayout()

        lbl_uin = QLabel("Input voltage: ")
        self.uin = QLabel("0.0V")
        self.uin.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lbl_iin = QLabel("Input current: ")
        self.iin = QLabel("0.0A")
        lbl_uout = QLabel("Output voltage: ")
        self.uout = QLabel("0.0V")
        lbl_iout = QLabel("Output current: ")
        self.iout = QLabel("0.0A")

        lbl_setpoints = QLabel("Setpoints")
        font = lbl_setpoints.font()
        font.setBold(True)
        font.setPointSize(10)
        lbl_setpoints.setFont(font)
    
        lbl_iout_req = QLabel("Iout requested: ")
        self.iout_req = QLabel("0.0A") 
        lbl_iout_act = QLabel("Iout actual:")
        self.iout_act = QLabel("0.0A")
        lbl_uout_req = QLabel("Uout requested: ")
        self.uout_req = QLabel("0.0V")
        lbl_uout_act = QLabel("Uout actual:")
        self.uout_act = QLabel("0.0V")

        self.enabled=False

        self.btn_en_pm = QPushButton("Enable")
        self.btn_en_pm.clicked.connect(self.btn_en_pm_clicked)
        self.btn_en_pm.setFixedWidth(150)
        self.btn_en_pm.setDisabled(True)

        self.btn_dis_pm = QPushButton("Disable")
        self.btn_dis_pm.clicked.connect(self.btn_dis_pm_clicked)
        self.btn_dis_pm.setFixedWidth(150)
        self.btn_dis_pm.setDisabled(True)

        self.btn_con_dis_pm = QPushButton("Connect")
        self.btn_con_dis_pm.clicked.connect(self.btn_con_dis_pm_clicked)
        self.btn_con_dis_pm.setFixedWidth(100)

        lbl_iout_pm = QLabel("Iout: ")
        self.edit_iout_pm = QLineEdit("0.0")
        self.edit_iout_pm.setDisabled(True)
        self.edit_iout_pm.returnPressed.connect(self.edit_iout_pm_send)
        i_vali = QDoubleValidator()
        i_vali.setNotation(QDoubleValidator.Notation.StandardNotation)
        i_vali.setRange(0.0,80.0,1)
        self.edit_iout_pm.setValidator(i_vali)
        self.edit_iout_pm.setFixedWidth(50)

        lbl_uout_pm = QLabel("Uout: ")
        self.edit_uout_pm = QLineEdit("0.0")
        self.edit_uout_pm.setDisabled(True)
        self.edit_uout_pm.returnPressed.connect(self.edit_uout_pm_send)
        u_vali = QDoubleValidator()
        u_vali.setNotation(QDoubleValidator.Notation.StandardNotation)
        u_vali.setRange(0.0,1000.0,1)
        self.edit_uout_pm.setValidator(u_vali)
        self.edit_uout_pm.setFixedWidth(50)

        lbl_control = QLabel("Control")
        font = lbl_control.font()
        font.setBold(True)
        font.setPointSize(10)
        lbl_control.setFont(font)

        lbl_status_pm = QLabel("Status")

        self.btn_status_pm_pwr = QPushButton("Power Error")
        self.btn_status_pm_pwr.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_pwr.setDisabled(True)
        self.btn_status_pm_pwr.setFixedWidth(640)

        self.btn_status_pm_ocp = QPushButton("OCP Error")
        self.btn_status_pm_ocp.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_ocp.setDisabled(True)
        self.btn_status_pm_ocp.setFixedWidth(640)

        self.btn_status_pm_otp = QPushButton("OTP Error")
        self.btn_status_pm_otp.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_otp.setDisabled(True)
        self.btn_status_pm_otp.setFixedWidth(640)

        self.btn_status_pm_on = QPushButton("Unit ON")
        self.btn_status_pm_on.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_on.setDisabled(True)
        self.btn_status_pm_on.setFixedWidth(640)
        
        self.btn_pm_uvp = QPushButton("Disable UVP")
        self.btn_pm_uvp.setFixedWidth(640)
        self.btn_pm_uvp.setDisabled(True)
        self.btn_pm_uvp.clicked.connect(self.btn_pm_uvp_clicked)

        self.btn_pm_omr_500v = QPushButton("500v mode")
        self.btn_pm_omr_500v.setFixedWidth(640)
        self.btn_pm_omr_500v.setDisabled(True)
        self.btn_pm_omr_500v.clicked.connect(self.btn_pm_omr_500v_clicked)
        
        self.btn_pm_omr_1kv = QPushButton("1kv mode")
        self.btn_pm_omr_1kv.setFixedWidth(640)
        self.btn_pm_omr_1kv.setDisabled(True)
        self.btn_pm_omr_1kv.clicked.connect(self.btn_pm_omr_1kv_clicked)

        self.btn_status_pm_omr = QPushButton("500V mode")
        self.btn_status_pm_omr.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_omr.setFixedWidth(640)
        self.btn_status_pm_omr.setDisabled(True)

        self.btn_status_pm_ovp_out = QPushButton("OVP OUT")
        self.btn_status_pm_ovp_out.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_ovp_out.setFixedWidth(640)
        self.btn_status_pm_ovp_out.setDisabled(True)

        self.btn_status_pm_ovp_in = QPushButton("OVP IN")
        self.btn_status_pm_ovp_in.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_ovp_in.setFixedWidth(640)
        self.btn_status_pm_ovp_in.setDisabled(True)

        self.btn_status_pm_can = QPushButton("CAN TMO")
        self.btn_status_pm_can.setStyleSheet(
                                        "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+
                                        "QPushButton:disabled {color: rgb(0, 0, 0)}"
                                        "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+
                                        "QPushButton:enabled {color: rgb(0, 0, 0)}"
                                        )
        self.btn_status_pm_can.setFixedWidth(640)
        self.btn_status_pm_can.setDisabled(True)


        layout.addWidget(lbl_uin,1,1)
        layout.addWidget(self.uin,1,2)
        layout.addWidget(lbl_iin,2,1)
        layout.addWidget(self.iin,2,2)
        layout.addWidget(lbl_uout,3,1)
        layout.addWidget(self.uout,3,2)
        layout.addWidget(lbl_iout,4,1,)
        layout.addWidget(self.iout,4,2)

        layout.addWidget(lbl_setpoints,5,1)

        layout.addWidget(lbl_uout_req,6,1)
        layout.addWidget(self.uout_req,6,2)
        layout.addWidget(lbl_uout_act,7,1)
        layout.addWidget(self.uout_act,7,2)

        layout.addWidget(lbl_iout_req,8,1)
        layout.addWidget(self.iout_req,8,2)
        layout.addWidget(lbl_iout_act,9,1)
        layout.addWidget(self.iout_act,9,2)

        layout.addWidget(lbl_control,10,1)  

        layout.addWidget(lbl_uout_pm,11,1,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.edit_uout_pm,11,2,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(lbl_iout_pm,12,1,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.edit_iout_pm,12,2,Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(lbl_status_pm,10,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_pwr,11,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_omr,11,4,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_ocp,12,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_ovp_in,12,4,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_otp,13,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_ovp_out,13,4,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_on,14,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_status_pm_can,14,4,Qt.AlignmentFlag.AlignLeft)        
        
        layout.addWidget(self.btn_en_pm,14,1,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_dis_pm,14,2,Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.btn_pm_omr_500v,15,3,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_pm_omr_1kv,15,4,Qt.AlignmentFlag.AlignLeft)


        layout.addWidget(self.btn_pm_uvp,15,2,Qt.AlignmentFlag.AlignLeft)   
        layout.addWidget(self.btn_con_dis_pm,15,1,Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.btn_pm_uvp,15,2,Qt.AlignmentFlag.AlignLeft)   
        
        layout.setRowStretch(10,1)
        self.groupBox.setFixedWidth(350)
    
        self.groupBox.setLayout(layout)
    
    def group_info_return(self):
        return self.groupBox

    def edit_iout_pm_send(self):
        self.powermodule.send_iout_setpoint(self.edit_iout_pm.text())
        self.iout_req.setText(self.edit_iout_pm.text())

    def edit_uout_pm_send(self):
        self.powermodule.send_uout_setpoint(self.edit_uout_pm.text())
        self.uout_req.setText(self.edit_uout_pm.text())

    def btn_con_dis_pm_clicked(self):
        if self.btn_con_dis_pm.text() == "Connect":
            try:
                print(self.powermodule.preCANopenObj.getListOfPCANChannels()[0])
                self.powermodule.preCANopenObj.connect('pcan',self.powermodule.preCANopenObj.getListOfPCANChannels()[0])
                # self.powermodule.node = self.preCANopenObj.addNode(self.powermodule.id),"GenericPREPowerModule.eds")
                self.edit_iout_pm.setEnabled(True)
                self.edit_uout_pm.setEnabled(True)
                self.btn_en_pm.setEnabled(True)
                self.btn_dis_pm.setEnabled(True)
                self.btn_con_dis_pm.setText("Disconnect")
                self.btn_pm_uvp.setEnabled(True)
                self.btn_pm_omr_1kv.setEnabled(True)
                self.btn_pm_omr_500v.setEnabled(True)
                self.btn_status_pm_omr.setEnabled(True)
            except:
                print("Can not connect to module")
        else:
            self.powermodule.preCANopenObj.disConnect()
            self.btn_con_dis_pm.setText("Connect")
            self.edit_iout_pm.setDisabled(True)
            self.edit_uout_pm.setDisabled(True)
            self.btn_en_pm.setDisabled(True)
            self.btn_dis_pm.setDisabled(True)
            self.btn_pm_uvp.setDisabled(True)
            self.btn_pm_omr_1kv.setDisabled(True)
            self.btn_pm_omr_500v.setDisabled(True)
            self.btn_status_pm_omr.setDisabled(True)
            self.btn_status_pm_pwr.setDisabled(True)
            self.btn_status_pm_otp.setDisabled(True)
            self.btn_status_pm_on.setDisabled(True)
            self.btn_status_pm_ocp.setDisabled(True)
            self.btn_status_pm_ovp_in.setDisabled(True)
            self.btn_status_pm_ovp_out.setDisabled(True)
            self.btn_status_pm_can.setDisabled(True)

    def btn_en_pm_clicked(self):
        
        self.powermodule.enable()

    def btn_dis_pm_clicked(self):

        self.powermodule.disable()

    def btn_pm_uvp_clicked(self):

        message = "inputUVP(0)"
        for i in range(len(message)):
            self.powermodule.node.sdo['OS Prompt']['StdIn'].raw = ord(message[i])
        self.powermodule.node.sdo['OS Prompt']['StdIn'].raw = ord('\n')   

    def btn_pm_omr_500v_clicked(self):
        self.powermodule.mode_500V()

    def btn_pm_omr_1kv_clicked(self):
        self.powermodule.mode_1kv()
    
    def get_info(self):

        if self.btn_con_dis_pm.text() == "Disconnect":

            try:

                self.powermodule.status=self.powermodule.read_status()
            
                self.powermodule.voltage_out()
                self.powermodule.current_out()
                self.powermodule.voltage_in()
                self.powermodule.current_in()
                self.powermodule.read_iout_actual_setpoint()
                self.powermodule.read_uout_actual_setpoint()
                
                if self.cnt ==0:

                    self.uin.setText(str(self.powermodule.voltage_in_meas))
                    self.iin.setText(str(self.powermodule.current_in_meas))

                    self.uout.setText(str(self.powermodule.voltage_out_meas))
                    self.iout.setText(str(self.powermodule.current_out_meas))

                    self.iout_act.setText(str(self.powermodule.current_setpoint))
                    self.uout_act.setText(str(self.powermodule.voltage_setpoint))
                    self.cnt = 1
                else:

                    self.btn_status_pm_pwr.setDisabled(self.powermodule.status & self.powermodule.powermodele_PWR)
                    self.btn_status_pm_otp.setDisabled(self.powermodule.status & self.powermodule.powermodele_OTP)
                    self.btn_status_pm_ocp.setDisabled(self.powermodule.status & self.powermodule.powermodele_OCP)
                    self.btn_status_pm_on.setEnabled(self.powermodule.status & self.powermodule.powermodele_ENABLED)
                    self.btn_status_pm_can.setEnabled(self.powermodule.status & self.powermodule.powermodele_CAN)
                    self.btn_status_pm_ovp_in.setEnabled(self.powermodule.status & self.powermodule.powermodele_OVP_IN)
                    self.btn_status_pm_ovp_out.setEnabled(self.powermodule.status & self.powermodule.powermodele_OVP_OUT)
                    self.cnt = 0

                omr_stat = self.powermodule.read_omr()
                if omr_stat == 1:
                    self.btn_status_pm_omr.setText("1kv mode")
                else:
                    self.btn_status_pm_omr.setText("500v mode")
            except:
                print("No respone from module")

class wave_plot_settings(QWidget):
    
    def __init__(self,aantal,data,tdv):
        super().__init__()

        layout = QGridLayout()
        self.label=[]
        self.edit=[]
        self.checkbox=[]
        self.filter=[]
        self.data = data.copy()
        self.tdv=tdv
        self.data_filterd = data.copy()
        self.color_setting=['yellow','springgreen','magenta','cyan','orangered','orange','blue','purple']
        
        
        for x in range(aantal):
            
            self.label.append(QLabel(f"Waveform {x} name"))
            self.edit.append(QLineEdit(f"Channel {x}"))
            self.checkbox.append(QCheckBox())
            self.checkbox[x].setChecked(True)
            self.filter.append(QPushButton(f"Filter {x}"))
            layout.addWidget(self.label[-1],(2*x),0)
            layout.addWidget(self.edit[-1],(2*x)+1,2)
            layout.addWidget(self.checkbox[-1],(2*x)+1,0)
            layout.addWidget(self.filter[-1],(2*x)+1,1)

        if aantal>0:
            self.filter[0].clicked.connect(lambda:self.show_filter_options(0))
        if aantal>1:
            self.filter[1].clicked.connect(lambda:self.show_filter_options(1))
        if aantal>2:
            self.filter[2].clicked.connect(lambda:self.show_filter_options(2))
        if aantal>3:
            self.filter[3].clicked.connect(lambda:self.show_filter_options(3))
        if aantal>4:
            self.filter[4].clicked.connect(lambda:self.show_filter_options(4))
        if aantal>5:
            self.filter[5].clicked.connect(lambda:self.show_filter_options(5))
        if aantal>6:
            self.filter[6].clicked.connect(lambda:self.show_filter_options(6))
        if aantal>7:
            self.filter[7].clicked.connect(lambda:self.show_filter_options(7))

        self.btn_ok = QPushButton("Ok")
        self.btn_ok.clicked.connect(self.plot_waveforms)
        layout.addWidget(self.btn_ok,(aantal*2)+1,0)

        self.setLayout(layout)

    def show_filter_options(self,channel):
        print(channel)
        pop_up = QDialog()      
        layout = QGridLayout()
        self.setWindowTitle("Filter settings")
        label_freq = QLabel("Cutoff frequency (Hz)")
        self.freq_set = QLineEdit("1000")
        label_order = QLabel("Order of filter")
        self.order_set = QLineEdit("5")
        self.btn_ok = QPushButton("Apply")
        self.btn_ok.clicked.connect(lambda:self.filter_waveform(channel,pop_up))
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.clicked.connect(pop_up.close)

        layout.addWidget(label_freq,0,0)
        layout.addWidget(self.freq_set,0,1)
        layout.addWidget(label_order,1,0)
        layout.addWidget(self.order_set,1,1)
        layout.addWidget(self.btn_ok,2,0)
        layout.addWidget(self.btn_cancel,2,1)
        pop_up.setLayout(layout)
        pop_up.exec()

    def filter_waveform(self,channel,dialog):
        self.data_filterd[channel] = general.butter_lowpass_filter_datascope(self.data[channel],self.tdv,int(self.freq_set.text()),int(self.order_set.text()))
        self.close()
        dialog.close()
        

    def plot_waveforms(self):

        check=0
        for x in range(len(self.data_filterd)):
            if self.checkbox[x].isChecked():
                check = check+1

        fig, axs = plt.subplots(nrows=check, ncols=1,sharex=True)
        y=0

        if(check>1):  
            for x in range(len(self.data_filterd)):
                if(x>0):
                    if self.checkbox[x].isChecked():

                        axs[y].plot(self.tdv,self.data_filterd[x],color=self.color_setting[x],linewidth=0.5)
                        axs[y].sharex=axs[0]
                        axs[y].tick_params('x',labelbottom=False)
                        axs[y].set_title(self.edit[x].text())
                        if x==(len(self.data_filterd)-1):
                            axs[y].set_xlabel("Time is sec") 
                        y=y+1
                else:
                    if self.checkbox[x].isChecked():
                        axs[y].plot(self.tdv,self.data_filterd[x],color='Yellow',linewidth=0.5)
                        axs[y].tick_params('x',labelbottom=False)
                        axs[y].set_title(self.edit[x].text())
                        y=y+1
        else:
                axs.plot(self.tdv,self.data_filterd[x],color='Yellow',linewidth=0.5)
                axs.set_title(self.edit[x].text()) 
                axs.set_xlabel("Time is sec")                 

            
        
        if (check)>1:
            axs[0].tick_params('x',labelbottom=False)
            axs[check-1].tick_params('x', labelbottom=True)
        
        self.close()

        plt.show() 

class Yokogawa_group_list:
    def __init__(self,ip):
        self.groupBox = QGroupBox()
        self.groupBox.setTitle("Yokogawa")
        self.info_cnt=0
        self.file_location = "D:/Metingen"
        
        layout = QGridLayout()
        gb_font = self.groupBox.font()
        gb_font.setPointSize(12)
        gb_font.setBold(True)
        self.groupBox.setFont(gb_font)

        self.yokogawa = Yokogawa(ip)

        self.btn_get_channel = QPushButton("Get wav")
        self.btn_get_channel.clicked.connect(self.get_waveform_thread)
        self.btn_get_channel.setFixedWidth(105)

        label_name = QLabel("File name:")
        self.filename = QLineEdit()
        self.filename.setFixedWidth(105)

        lbl_channel =QLabel("Channel: ")
        self.channel =QLineEdit("1")
        self.channel.setFixedWidth(50)

        self.btn_open_location = QPushButton("Set location")
        self.btn_open_location.clicked.connect(self.set_file_location)
        self.btn_open_location.setFixedWidth(105)

        self.btn_open_scope_file = QPushButton("Open scope file")
        self.btn_open_scope_file.clicked.connect(self.open_scope_file)        
        self.btn_open_scope_file.setFixedWidth(105)

        self.label_status = QLabel("Ready")
        self.label_status.setFixedWidth(150)
        

        layout.addWidget(lbl_channel,1,0)
        layout.addWidget(self.channel,1,1)

        layout.addWidget(label_name,2,0)
        layout.addWidget(self.filename,2,1)

        
        layout.addWidget(self.btn_get_channel,3,0)
        layout.addWidget(self.btn_open_location,6,0,1,2,)
        layout.addWidget(self.btn_open_scope_file,7,0,1,2)
        layout.addWidget(self.label_status,16,0,1,2)

        layout.setRowStretch(13,2)

        self.groupBox.setFixedWidth(200)
        
        self.groupBox.setLayout(layout)
    
    def set_file_location(self):

        locatie =QFileDialog().getExistingDirectory()
        self.file_location=str(locatie)

    def group_info_return(self):
            return self.groupBox

    def open_scope_file(self):
        file= QFileDialog().getOpenFileUrl(filter="*.scope")
        file = file[0].url().split('///')
        try:        
            data,tdv = general.process_multi_channel_data(str(file[1]))

            self.pop_window = wave_plot_settings(len(data),data,tdv)
            self.pop_window.setWindowTitle("Waveform settings")
            self.pop_window.setFocus()
            self.pop_window.show()
            
        except:
            self.label_status.setText("Unable to open scope file")  

    def get_waveform_thread(self):
        t1=threading.Thread(target=self.get_waveform)
        t1.start()


    def get_waveform(self):

        self.label_status.setText("Getting data...")
        now = datetime.now()
        date=str(now.date()).replace('-','_',2)
        ttime=str(now.time()).replace(":","_",2)[:8]

        xscale = float(self.yokogawa.request_xscale())*10 #10div
        xscale = xscale/(float(self.yokogawa.request_length()))

        channels = self.channel.text().split(',')
        if int(self.yokogawa.get_status()) & 1:
            print("stop scope")
            self.yokogawa.stop_aq()
        
        data = [[0]*2]*len(channels)
        for x in range(len(channels)):
            tmp_length = self.yokogawa.get_wave_length(channels[x])
            tmp_data = self.yokogawa.request_wave_word(int(channels[x]),0,tmp_length)
            tmp_range = float(self.yokogawa.request_range())
            data[x] = [tmp_data,tmp_range]


        self.yokogawa.start_aq()

        if self.filename.text() != '' :

            
            f = open(f"{self.file_location}/{self.filename.text()}.scope",'w')
        else:
            f = open(f"{self.file_location}/scope_data_channel_{self.channel.text()}_{date}_{ttime}.scope",'w')

        f.write(f"xscale:{xscale}\n")
        f.write(f"numb channels:{len(channels)}\n")

        for x in range(len(channels)):

            data_c = self.yokogawa.calc_data_from_array(data[x][0],data[x][1])
            f.write(str(data_c)+"\n")

        f.close()
        
        self.label_status.setText(f"Data of channel {self.channel.text()} saved")

class hioki_group_list:
    def __init__(self,name,ip,port):

        self.name = name
        self.groupBox = QGroupBox()
        self.groupBox.setTitle(name)
        self.info_cnt=0
        
        layout = QGridLayout()
        gb_font = self.groupBox.font()
        gb_font.setPointSize(12)
        gb_font.setBold(True)
        self.groupBox.setFont(gb_font)

        self.hioki = Hioki(ip,port,1)

        lbl_uin = QLabel("Urms: ")
        self.uin = QLabel("0.0V")
        lbl_iin = QLabel("Irms: ")
        self.iin = QLabel("0.0A")
        lbl_iinac = QLabel("Iac")
        self.iinac = QLabel("0.0A")
        lbl_pin = QLabel("Pin")
        self.pin = QLabel("0.0W")

        lbl_uout = QLabel("Urms: ")
        self.uout = QLabel("0.0V")
        lbl_iout = QLabel("Irms: ")
        self.iout = QLabel("0.0V")
        lbl_ioutac = QLabel("Iac")
        self.ioutac =QLabel("0.0A")
        lbl_pout = QLabel("Pout")
        self.pout = QLabel("0.0W")

        lbl_loss1 = QLabel("Ploss 1")
        self.loss1 = QLabel("0.0W")
        lbl_loss2 = QLabel("Ploss 2")
        self.loss2 = QLabel("0.0W")

        lbl_eff1 = QLabel("Eff 1")
        self.eff1 = QLabel("0.0%")
        lbl_eff2 = QLabel("Eff 2")
        self.eff2 = QLabel("0.0%")

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.con_dis)

        layout.addWidget(lbl_uin,1,1)
        layout.addWidget(self.uin,1,2)
        layout.addWidget(lbl_iin,2,1)
        layout.addWidget(self.iin,2,2)
        layout.addWidget(lbl_iinac,3,1)
        layout.addWidget(self.iinac,3,2)
        layout.addWidget(lbl_pin,4,1)
        layout.addWidget(self.pin,4,2)

        layout.addWidget(lbl_uout,5,1)
        layout.addWidget(self.uout,5,2)
        layout.addWidget(lbl_iout,6,1)
        layout.addWidget(self.iout,6,2)
        layout.addWidget(lbl_ioutac,7,1)
        layout.addWidget(self.ioutac,7,2)
        layout.addWidget(lbl_pout,8,1)
        layout.addWidget(self.pout,8,2)

        layout.addWidget(lbl_loss1,9,1)
        layout.addWidget(self.loss1,9,2)
        layout.addWidget(lbl_loss2,10,1)
        layout.addWidget(self.loss2,10,2)

        layout.addWidget(lbl_eff1,11,1)
        layout.addWidget(self.eff1,11,2)
        layout.addWidget(lbl_eff2,12,1)
        layout.addWidget(self.eff2,12,2)

        layout.addWidget(self.btn_connect,13,1)

        layout.setRowStretch(13,1)

        self.groupBox.setFixedWidth(200)
        
        self.groupBox.setLayout(layout)

    def group_info_return(self):
            return self.groupBox
    
    def con_dis(self): 
                
        if self.btn_connect.text() == "Connect":
            if self.hioki.open_port() == True:
                
                self.btn_connect.setText("Disconnect")

        else:
            self.hioki.close_port()
            self.btn_connect.setText("Connect")

    def get_info(self):

        if self.btn_connect.text() == "Disconnect":

            if self.info_cnt==0:
                self.uin.setText(str(float(self.hioki.meas("Urms1"))))
                self.iin.setText(str(float(self.hioki.meas("Irms1"))))
                self.iinac.setText(str(float(self.hioki.meas("Iac1"))))
                self.pin.setText(str(float(self.hioki.meas("P1"))))
                self.info_cnt=1

            elif self.info_cnt==1:
                self.uout.setText(str(float(self.hioki.meas("Urms4"))))
                self.iout.setText(str(float(self.hioki.meas("Irms4"))))
                self.ioutac.setText(str(float(self.hioki.meas("Iac4"))))
                self.pout.setText(str(float(self.hioki.meas("P4"))))
                self.info_cnt=2
            
            else:
                self.loss1.setText(str(float(self.hioki.meas("Loss1"))))
                self.loss2.setText(str(float(self.hioki.meas("Loss2"))))
                self.eff1.setText(str(float(self.hioki.meas("Eff1"))))
                self.eff2.setText(str(float(self.hioki.meas("Eff2"))))
                self.info_cnt = 0

class delta_group_list:

        def __init__(self,name,ip,port):

            self.button_off_color = "QPushButton:enabled {background-color: rgb(255, 0, 0)}"+"QPushButton:enabled {color: rgb(0, 0, 0)}"
            self.button_on_color = "QPushButton:enabled {background-color: rgb(0, 255, 0)}"+"QPushButton:enabled {color: rgb(0, 0, 0)}"

            self.delta = Delta(ip,port,1)

            self.name = name
            self.groupBox = QGroupBox()
            self.groupBox.setTitle(name)
        
            layout = QGridLayout()
            gb_font = self.groupBox.font()
            gb_font.setPointSize(12)
            gb_font.setBold(True)
            self.groupBox.setFont(gb_font)

            lbl_uout = QLabel("Output voltage: ")
            self.uout = QLabel("0.0V")
            lbl_iout = QLabel("Output current: ")
            self.iout = QLabel("0.0A")
            lbl_pout = QLabel("Power: ")
            self.pout = QLabel("0.0W")

            lbl_uset =QLabel("Uset: ")
            self.uset =QLineEdit("0.0")
            lbl_set_plus = QLabel("Iset +: ")
            self.iset_plus = QLineEdit("0.0")
            lbl_set_min = QLabel("Iset -: ")
            self.iset_min = QLineEdit("0.0")

            self.uset.setDisabled(True)
            self.iset_min.setDisabled(True)
            self.iset_plus.setDisabled(True)

            self.uset.returnPressed.connect(lambda:self.uset_delta_send())
            self.iset_plus.returnPressed.connect(lambda:self.iset_delta_plus_send())
            self.iset_min.returnPressed.connect(lambda:self.iset_delta_min_send())

            self.btn_connect=QPushButton("Connect")
            self.btn_connect.clicked.connect(self.con_dis)
            self.btn_en_dis=QPushButton("Enable")
            self.btn_en_dis.clicked.connect(self.en_dis)
            self.btn_en_dis.setStyleSheet(self.button_off_color)
            self.btn_en_dis.setDisabled(True)
            

            layout.addWidget(lbl_uout,1,1)
            layout.addWidget(self.uout,1,2)
            layout.addWidget(lbl_iout,2,1)
            layout.addWidget(self.iout,2,2)
            layout.addWidget(lbl_pout,3,1)
            layout.addWidget(self.pout,3,2)


            layout.addWidget(lbl_uset,4,1)
            layout.addWidget(self.uset,4,2)
            layout.addWidget(lbl_set_plus,5,1)
            layout.addWidget(self.iset_plus,5,2)
            layout.addWidget(lbl_set_min,6,1)
            layout.addWidget(self.iset_min,6,2)

            layout.addWidget(self.btn_en_dis,7,1)
            layout.addWidget(self.btn_connect,8,1)
            

            layout.setRowStretch(9,5)
            self.groupBox.setFixedWidth(200)
            self.groupBox.setLayout(layout)


        def group_info_return(self):
            return self.groupBox
    
        def con_dis(self): 
        
            if self.btn_connect.text() == "Connect":

               if self.delta.open_port() == True:
                    self.delta.set_control_eth()
                    self.btn_connect.setText("Disconnect")
                    self.btn_en_dis.setEnabled(True)
                    self.uset.setEnabled(True)
                    self.iset_min.setEnabled(True)
                    self.iset_plus.setEnabled(True)
    
            else:
                self.delta.set_volt("0")
                self.delta.set_cur_neg("0")
                self.delta.set_cur_pos("0")
                self.delta.disable_out()
                self.uset.setDisabled(True)
                self.iset_min.setDisabled(True)
                self.iset_plus.setDisabled(True)

                self.delta.set_control_local()
                self.btn_connect.setText("Connect")
                self.btn_en_dis.setDisabled(True)
                self.delta.close_port()


        def en_dis(self): 

            if(self.delta.status_out()=="1"):
                self.delta.disable_out()
            else:
                self.delta.enable_out()   

        def uset_delta_send(self):
            self.delta.set_volt(self.uset.text())

        def iset_delta_plus_send(self):
            self.delta.set_cur_pos(self.iset_plus.text())
            

        def iset_delta_min_send(self):
            self.delta.set_cur_neg(self.iset_min.text())

        def get_info(self):
            if self.btn_connect.text() == "Disconnect":
                self.delta.meas_volt()
                self.delta.meas_cur()
                self.delta.meas_power()
                output = self.delta.status_out()

                self.uout.setText(self.delta.volt)
                self.iout.setText(self.delta.volt)
                self.pout.setText(self.delta.power)
                if(output == "1"):
                    self.btn_en_dis.setStyleSheet(self.button_on_color)
                    self.btn_en_dis.setText("Enabled")
                else:
                    self.btn_en_dis.setStyleSheet(self.button_off_color)
                    self.btn_en_dis.setText("Disabed")

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bench Mike")

        self.info_cnt = 0

        self.menu_bar = QMenuBar()
        self.com = self.menu_bar.addMenu("COM settings")
        self.file = self.menu_bar.addMenu("File benchmark")

        self.menu_com_pw = self.com.addAction("Power unit")
        self.menu_com_hioki = self.com.addAction("Hioki")
        self.menu_com_delta1 = self.com.addAction("Delta 1")
        self.menu_com_delta2 = self.com.addAction("Delta 2")

        self.com.addAction(self.menu_com_pw)
        self.com.addAction(self.menu_com_hioki)
        self.com.addAction(self.menu_com_delta1)
        self.com.addAction(self.menu_com_delta2)

        self.menu_file_open = self.file.addAction("Open file")
        self.file.addAction(self.menu_file_open)
    
        self.menu_com_pw.triggered.connect(self.com_pu_clicked)
        self.menu_com_hioki.triggered.connect(self.com_hioki_clicked)
        self.menu_com_delta1.triggered.connect(self.com_delta1_clicked)
        self.menu_com_delta2.triggered.connect(self.com_delta2_clicked)

        self.button_off_color = "QPushButton:disabled {background-color: rgb(255, 0, 0)}"+"QPushButton:disabled {color: rgb(0, 0, 0)}"
        self.button_on_color = "QPushButton:disabled {background-color: rgb(0, 255, 0)}"+"QPushButton:disabled {color: rgb(0, 0, 0)}"

        layout = QGridLayout()

        self.delta1_group = delta_group_list("Delta 1","10.0.0.110",8462)
        self.delta2_group = delta_group_list("Delta 2","10.0.0.130",8462)

        self.hioki1 = hioki_group_list("Hioki","10.0.0.220",3390)
        self.yokogawa1 = Yokogawa_group_list("10.0.0.176")

        self.pm1 = powermodule_group_list("Powermodule 1",0x30)

        layout.addWidget(self.menu_bar,0,0)

        layout.addWidget(self.pm1.group_info_return(), 1, 0,15,2)
        layout.addWidget(self.hioki1.group_info_return(), 1, 2,15,1)
        layout.addWidget(self.delta1_group.group_info_return(), 1, 3,15,1)
        layout.addWidget(self.delta2_group.group_info_return(), 1, 4,15,1)
        layout.addWidget(self.yokogawa1.group_info_return(), 1, 5,15,1)

        self.setLayout(layout)

        self.setup_timer = QTimer()
        self.setup_timer.timeout.connect(self.get_setup_info)
        self.setup_timer.setInterval(300)
        self.setup_timer.start()

        self.om_timer = QTimer()
        self.om_timer.timeout.connect(self.get_pm_info)
        self.om_timer.setInterval(200)
        self.om_timer.start()

        print(self.pm1.btn_status_pm_pwr.width())

    def get_setup_info(self):
        
        # if self.info_cnt == 0:  
        #     self.delta1_group.get_info()
        #     self.info_cnt =1
        # elif self.info_cnt == 1:
        #     self.delta2_group.get_info()
        #     self.info_cnt = 2
        # else:
        #     self.hioki1.get_info()
        #     self.info_cnt=0

        #     def get_setup_info(self):
        t_delta1 = threading.Thread(target=self.delta1_group.get_info())
        t_delta2 = threading.Thread(target=self.delta2_group.get_info())
        t_hioki = threading.Thread(target=self.hioki1.get_info())

        t_delta1.start()
        t_delta2.start()
        t_hioki.start()
        # if self.info_cnt == 0:  
        #     self.delta1_group.get_info()
        #     self.info_cnt =1
        # elif self.info_cnt == 1:
        #     self.delta2_group.get_info()
        #     self.info_cnt = 2
        # else:
        #     self.hioki1.get_info()
        #     self.info_cnt=0

    
    def get_pm_info(self):
        t_pm = threading.Thread(target=self.pm1.get_info())
        t_pm.start()
        # self.pm1.get_info()


    def com_pu_clicked(self):
        self.pop_window = canid_window()
        self.pop_window.setWindowTitle("Powermodule CANID")
        self.pop_window.btn_ok.clicked.connect(self.com_set_canid)
        self.pop_window.id.setText(str(hex(self.pm1.id)))
        self.pop_window.show()

    def com_set_canid(self):
        hex_s = self.pop_window.id.text()
        tmp = int(hex_s,16)
        hex_n = hex(tmp)
        self.pm1.id = hex_n
        self.pop_window.close()

    def com_hioki_clicked(self):

        self.pop_window = com_setting_window()
        self.pop_window.setWindowTitle("Hioki COM settings")
        self.pop_window.btn_ok.clicked.connect(self.com_set_hioki_info)
        self.pop_window.ip.setText(self.hioki1.hioki.ip)
        self.pop_window.port.setText(str(self.hioki1.hioki.port))
        self.pop_window.show()

    def com_set_hioki_info(self):
        self.hioki1.hioki.ip = self.pop_window.ip.text()
        self.hioki1.hioki.port = int(self.pop_window.port.text())
        self.pop_window.close()
        

    def com_delta1_clicked(self):
        
        self.pop_window = com_setting_window()
        self.pop_window.setWindowTitle("Delta 1 COM settings")
        self.pop_window.btn_ok.clicked.connect(self.com_set_delta1_info)
        self.pop_window.ip.setText(self.delta1_group.delta.ip)
        self.pop_window.port.setText(str(self.delta1_group.delta.port))
        self.pop_window.show()
    
    def com_set_delta1_info(self):
        self.delta1_group.delta.ip = self.pop_window.ip.text()
        self.delta1_group.delta.port = int(self.pop_window.port.text())
        # self.delta1_group.connect_settings(self.delta1_group.delta.ip,self.delta1_group.delta.port)
        self.pop_window.close()

    def com_delta2_clicked(self):
        
        self.pop_window = com_setting_window()
        self.pop_window.setWindowTitle("Delta 2 COM settings")
        self.pop_window.btn_ok.clicked.connect(self.com_set_delta2_info)
        self.pop_window.ip.setText(self.delta2_group.delta.ip)
        self.pop_window.port.setText(str(self.delta2_group.delta.port))
        self.pop_window.show()

    def com_set_delta2_info(self):
        self.delta2_group.delta.ip = self.pop_window.ip.text()
        self.delta2_group.delta.port = int(self.pop_window.port.text())
        # self.delta2_group.connect_settings(self.delta2.ip,self.delta2.port)
        self.pop_window.close()

# sshFile="./classic.stylesheet"


def main():
    
#play bootup sound

    # pygame.mixer.init()
    # pygame.mixer.music.load('D:/Metingen/heman_power.mp3')
    # pygame.mixer.music.play()
# Set the style of teh GUI
    sshFile="dark_orange.stylesheet"

    p = Path(__file__).with_name(sshFile)
    with p.open('r') as f:
        stylesheet =f.read()
# Start the application
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window=Window()
    # window.setFixedSize(500,500)
    window.show()
    # print(window.adjustSize)
    sys.exit(app.exec())

if __name__ == '__main__':
  main()

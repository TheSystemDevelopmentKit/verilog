#Verilog class 
# Provides verilog-related properties and methods for other classes TheSDK
#
# Adding this class as a superclass enforces the definitions for verilog in the
# subclasses
##############################################################################
import os
import sys
import subprocess
import shlex
from abc import * 
from thesdk import *
import numpy as np
import pandas as pd
from functools import reduce
from verilog.connector import intend
from verilog.testbench import testbench as vtb
from verilog.verilog_iofile import verilog_iofile as verilog_iofile

class verilog(thesdk,metaclass=abc.ABCMeta):
    #These need to be converted to abstact properties
    def __init__(self):
        pass

    @property
    @abstractmethod
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__
    #This must be in every subclass file.
    #@property
    #def _classfile(self):
    #    return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    # These propertios "extend" IO class, but do not need ot be member of it,
    # Furthermore IO._Data _must_ me bidirectional. Otherwise driver and target 
    # Must be defined separately
    #@property  # in | out
    #def dir(self):
    #    if hasattr(self,'_dir'):
    #        return self._dir
    #    else:
    #        self._dir=None
    #    return self._dir

    #@dir.setter
    #def dir(self,value):
    #    self._dir=value

    #@property
    #def iotype(self):  # sample | event
    #    if hasattr(self,'_iotype'):
    #        return self._iotype
    #    else:
    #        self._iotype='sample'
    #    return self._iotype

    #@property
    #def datatype(self):  # complex | int | scomplex | sint
    #    if hasattr(self,'_datatype'):
    #        return self._datatype
    #    else:
    #        self._datatype=None
    #    return self._datatype

    #@datatype.setter
    #def datatype(self,value):
    #    self._datatype=value

    #@property
    #def ionames(self): # list of associated verilog ionames
    #    if hasattr(self,'_ionames'):
    #        return self._ionames
    #    else:
    #        self._ionames=[]
    #    return self._ionames

    #@ionames.setter
    #def ionames(self,value):
    #    self._ionames=value

    @property
    def preserve_iofiles(self):  # if True, do not delete files sfter sim 
        if hasattr(self,'_preserve_iofiles'):
            return self._preserve_iofiles
        else:
            self._preserve_iofiles=False
        return self._preserve_iofiles

    @preserve_iofiles.setter
    def preserve_iofiles(self,value):
        self._preserve_iofiles=value

    @property
    def interactive_verilog(self):# True= launch simulator GUI
        if hasattr(self,'_interactive_verilog'):
            return self._interactive_verilog
        else:
            self._interactive_verilog=False
        return self._interactive_verilog

    @interactive_verilog.setter
    def interactive_verilog(self,value):
        self._interactive_verilog=value
    
    # This property utilises verilog_iofile class to maintain list of io-files
    # that  are automatically assigned to verilogcmd
    @property
    def iofile_bundle(self):
        if not hasattr(self,'_iofile_bundle'):
            self._iofile_bundle=Bundle()
        return self._iofile_bundle

    @iofile_bundle.setter
    def iofile_bundle(self,value):
        self._iofile_bundle=value

    @iofile_bundle.deleter
    def iofile_bundle(self):
        for name, val in self.iofile_bundle.Members.items():
            if val.preserve:
                self.print_log(type="I", msg="Preserve_value is %s" %(val.preserve))
                self.print_log(type="I", msg="Preserving file %s" %(val.file))
            else:
                val.remove()
        #self._iofile_bundle=None

    @property 
    def verilog_submission(self):
        if not hasattr(self, '_verilog_submission'):
            try:
                self._verilog_submission=thesdk.GLOBALS['LSFSUBMISSION']+' '
            except:
                self.print_log(type='W',msg='Variable thesdk.GLOBALS incorrectly defined. _verilog_submission defaults to empty string and simulation is ran in localhost.')
                self._verilog_submission=''

        if hasattr(self,'_interactive_verilog'):
            return self._verilog_submission

        return self._verilog_submission

    @property
    def name(self):
        if not hasattr(self, '_name'):
            #_classfile is an abstract property that must be defined in the class.
            self._name=os.path.splitext(os.path.basename(self._classfile))[0]
        return self._name
    #No setter, no deleter.

    @property
    def entitypath(self):
        if not hasattr(self, '_entitypath'):
            #_classfile is an abstract property that must be defined in the class.
            self._entitypath= os.path.dirname(os.path.dirname(self._classfile))
        return self._entitypath
    #No setter, no deleter.

    @property
    def vlogsrcpath(self):
        if not hasattr(self, '_vlogsrcpath'):
            #_classfile is an abstract property that must be defined in the class.
            self._vlogsrcpath  =  self.entitypath + '/sv'
        return self._vlogsrcpath
    #No setter, no deleter.

    @property
    def vlogsrc(self):
        if not hasattr(self, '_vlogsrc'):
            #_classfile is an abstract property that must be defined in the class.
            self._vlogsrc=self.vlogsrcpath + '/' + self.name + '.sv'
        return self._vlogsrc
    @property
    def vlogtbsrc(self):
        if not hasattr(self, '_vlogtbsrc'):
            #_classfile is an abstract property that must be defined in the class.
            self._vlogtbsrc=self.vlogsrcpath + '/tb_' + self.name + '.sv'
        return self._vlogtbsrc

    @property
    def vlogsimpath(self):
        if not hasattr(self, '_vlogsimpath'):
            #_classfile is an abstract property that must be defined in the class.
            if not (os.path.exists(self.entitypath+'/Simulations')):
                os.mkdir(self.entitypath + '/Simulations')
        self._vlogsimpath  = self.entitypath +'/Simulations/verilogsim'
        if not (os.path.exists(self._vlogsimpath)):
            os.mkdir(self._vlogsimpath)
        return self._vlogsimpath
    #No setter, no deleter.

    @property
    def vlogworkpath(self):
        if not hasattr(self, '_vlogworkpath'):
            self._vlogworkpath    =  self.vlogsimpath +'/work'
        return self._vlogworkpath

    @property
    def vlogparameters(self): 
        if not hasattr(self, '_vlogparameters'):
            self._vlogparameters =dict([])
        return self._vlogparameters
    @vlogparameters.setter
    def vlogparameters(self,value): 
            self._vlogparameters = value
    @vlogparameters.deleter
    def vlogparameters(self): 
            self._vlogparameters = None

    @property
    def vlogmodulefiles(self):
        if not hasattr(self, '_vlogmodulefiles'):
            self._vlogmodulefiles =list([])
        return self._vlogmodulefiles
    @vlogmodulefiles.setter
    def vlogmodulefiles(self,value): 
            self._vlogmodulefiles = value
    @vlogmodulefiles.deleter
    def vlogmodulefiles(self): 
            self._vlogmodulefiles = None 

    #This is obsoleted
    def def_verilog(self):
        self.print_log(type='I', 
                msg='Command def_verilog() is obsoleted. \
                        It does nothing. \nWill be removed in future releases')

    @property
    def vlogcmd(self):
        submission=self.verilog_submission
        vloglibcmd =  'vlib ' +  self.vlogworkpath + ' && sleep 2'
        vloglibmapcmd = 'vmap work ' + self.vlogworkpath
        vlogmodulesstring=' '.join([ self.vlogsrcpath + '/'+ 
            str(param) for param in self.vlogmodulefiles])
        vlogcompcmd = ( 'vlog -work work ' + self.vlogsrc + ' ' +
                       self.vlogtbsrc + ' ' + vlogmodulesstring )
        
        gstring=' '.join([ ('-g ' + str(param) +'='+ str(val)) 
            for param,val in iter(self.vlogparameters.items()) ])

        fileparams=''
        for name, file in self.iofile_bundle.Members.items():
            fileparams+=' '+file.simparam

        if not self.interactive_verilog:
            dostring=' -do "run -all; quit;"'
            vlogsimcmd = ( 'vsim -64 -batch -t 1ps -voptargs=+acc ' 
                    + fileparams + ' ' + gstring
                    +' work.tb_' + self.name  
                    + dostring)
        else:
            dofile=self.vlogsimpath+'/dofile.do'
            if os.path.isfile(dofile):
                dostring=' -do "'+dofile+'"'
            else:
                dostring=''
            submission="" #Local execution
            vlogsimcmd = ( 'vsim -64 -t 1ps -novopt ' + fileparams 
                    + ' ' + gstring +' work.tb_' + self.name + dostring)

        self._vlogcmd =  vloglibcmd  +\
                ' && ' + vloglibmapcmd +\
                ' && ' + vlogcompcmd +\
                ' && ' + submission +\
                vlogsimcmd
        return self._vlogcmd

    # Just to give the freedom to set this if needed
    @vlogcmd.setter
    def vlogcmd(self,value):
        self._vlogcmd=value
    @vlogcmd.deleter
    def vlogcmd(self):
        self._vlogcmd=None
    
    def create_connectors(self):
        # Create TB connectors from the control file
        # See controller.py
        for ioname,io in self.IOS.Members.items():
            # If input is a file, adopt it
            if isinstance(io.Data,verilog_iofile): 
                if io.Data.name is not ioname:
                    self.print_log(type='I', 
                            msg='Unifying file %s name to ioname %s' %(io.Data.name,ioname))
                    io.Data.name=ioname
                io.Data.adopt(parent=self)
                self.tb.parameters.Members.update(io.Data.vlogparam)

                for connector in io.Data.verilog_connectors:
                    self.tb.connectors.Members[connector.name]=connector
                    # Connect them to DUT
                    try: 
                        self.dut.ios.Members[connector.name].connect=connector
                    except:
                        pass
            # If input is not a file, look for corresponding file definition
            elif ioname in self.iofile_bundle.Members:
                val=self.iofile_bundle.Members[ioname]
                self.iofile_bundle.Members[ioname].verilog_connectors=\
                        self.tb.connectors.list(names=val.ionames)
                self.tb.parameters.Members.update(val.vlogparam)
        # Define the iofiles of the testbench. '
        # Needed for creating file io routines 
        self.tb.iofiles=self.iofile_bundle
               
    def connect_inputs(self):
        for ioname,io in self.IOS.Members.items():
            if ioname in self.iofile_bundle.Members:
                val=self.iofile_bundle.Members[ioname]
                # File type inputs are driven by the file.Data, not the input field
                if not isinstance(self.IOS.Members[val.name].Data,verilog_iofile) \
                        and val.dir is 'in':
                    # Data must be properly shaped
                    self.iofile_bundle.Members[ioname].Data=self.IOS.Members[ioname].Data

    # Define if the signals are signed or not
    # Can these be deducted?
    def format_ios(self):
        # Verilog module does not contain information if the bus is signed or not
        # Prior to writing output file, the type of the connecting wire defines
        # how the bus values are interpreted. 
        for ioname,val in self.iofile_bundle.Members.items():
            if val.dir is 'out' \
                    and ((val.datatype is 'sint' ) or (val.datatype is 'scomplex')):
                if val.ionames:
                    for assocname in val.ionames:
                        self.tb.connectors.Members[assocname].type='signed'
                else:
                    self.print_log(type='F', 
                        msg='List of associated ionames no defined for IO %s\n. Provide it as list of strings' %(ioname))

    def execute_verilog_sim(self):
        filetimeout=60 #File appearance timeout in seconds
        count=0
        files_ok=False
        while not files_ok:
            count +=1
            if count >5:
                self.print_log(type='F', msg='Verilog infile writing timeout')
            for name, file in self.iofile_bundle.Members.items(): 
                if file.dir=='in':
                    files_ok=True
                    files_ok=files_ok and os.path.isfile(file.file)
            time.sleep(int(filetimeout/5))

        #Remove existing output files before execution
        for name, file in self.iofile_bundle.Members.items(): 
            if file.dir=='out':
                try:
                    #Still keep the file in the infiles list
                    os.remove(file.name)
                except:
                    pass

        self.print_log(type='I', msg="Running external command %s\n" %(self.vlogcmd) )

        if self.interactive_verilog:
            self.print_log(type='I', msg="""
                Running verilog simulation in interactive mode.
                Add the probes in the simulation as you wish.
                To finish the simulation, run the simulation to end and exit.""")

        subprocess.check_output(self.vlogcmd, shell=True);

        count=0
        files_ok=False
        while not files_ok:
            count +=1
            if count >5:
                self.print_log(type='F', msg="Verilog outfile timeout")
            time.sleep(int(filetimeout/5))
            for name, file in self.iofile_bundle.Members.items(): 
                if file.dir=='out':
                    files_ok=True
                    files_ok=files_ok and os.path.isfile(file.file)
    
    def run_verilog(self):
        if not hasattr(self,'IOS'):
            self.print_log(type='O', msg='You are running Verilog simulation with v1.1 configuration.\n Please see https://github.com/TheSystemDevelopmentKit/thesdk_template\n for examples of migrating to v1.2')
            self.execute_verilog_sim()
        else:  # V1.2 syntax
            if not hasattr(self,'define_io_conditions'):
                self.print_log(type='W', msg="""
                    You are running Verilog simulation with v1.2 configuration.
                    (You have defined IOS attribute)
                    You have NOT defined \'define_io_conditions\' method.
                    With default conditions every rising edge clock reads 
                    an input value  and writes a valid output value. 
                    To add more conditions, see verilog.run_verilog for examples. 
                    Will be forced with abstract method in future releases.""")

        # Input A is read to verilog simulation after 'initd' is set to 1 by controller
        #self.iofile_bundle.Members['A'].verilog_io_condition='initdone'
        # Output is read to verilog simulation when all of the utputs are valid, 
        # and after 'initdo' is set to 1 by controller
        #self.iofile_bundle.Members['Z'].verilog_io_condition_append(cond='&& initdone')

        self.tb=vtb(self)             
        self.tb.define_testbench()    
        self.create_connectors()
        self.connect_inputs()         

        if hasattr(self,'define_io_conditions'):
            self.define_io_conditions()   # Local, this is dependent on how you
                                          # control the simulation
                                          # i.e. when you want to read an write your IO's
        self.format_ios()             
        self.tb.generate_contents() 
        self.tb.export(force=True)
        self.write_infile()           
        self.execute_verilog_sim()            
        self.read_outfile()           
        self.connect_outputs()         


    #This writes all infile
    def write_infile(self):
        for name, val in self.iofile_bundle.Members.items():
            if val.dir=='in':
                self.iofile_bundle.Members[name].write()
    
    #This reads all outfiles
    def read_outfile(self):
        for name, val in self.iofile_bundle.Members.items():
            if val.dir=='out':
                 self.iofile_bundle.Members[name].read()

    def connect_outputs(self):
        for name, val in self.iofile_bundle.Members.items():
            if val.dir=='out':
                self.IOS.Members[name].Data=self.iofile_bundle.Members[name].Data
              




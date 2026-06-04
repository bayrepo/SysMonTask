#!/usr/bin/env python3
# import gi
# gi.require_version("Gtk", "3.24")

from gi.repository import Gtk as g
from os import popen
from xml.etree.ElementTree import fromstring
import re

try:
    from gi_composites import GtkTemplate
except ImportError:
    from sysmontask.gi_composites import GtkTemplate

if __name__=='sysmontask.gpu':
    from sysmontask.sysmontask import files_dir
else:
    from sysmontask import files_dir

@GtkTemplate(ui=files_dir+'/gpu.glade')
class gpuTabWidget(g.ScrolledWindow):

    # Required else you would need to specify the full module
    # name in mywidget.ui (__main__+MyWidget)
    __gtype_name__ = 'gpuTabWidget'

    gpuinfolabel = GtkTemplate.Child()
    gpuutildrawarea=GtkTemplate.Child()
    gpuvramdrawarea=GtkTemplate.Child()
    gpuencodingdrawarea=GtkTemplate.Child()
    gpudecodingdrawarea=GtkTemplate.Child()

    gpuvramlabelvalue=GtkTemplate.Child()
    gpuutilisationlabelvalue=GtkTemplate.Child()
    gpuvramusagelabelvalue=GtkTemplate.Child()

    gputemplabelvalue=GtkTemplate.Child()
    gpushaderspeedlabelvalue=GtkTemplate.Child()

    gpudriverlabelvalue=GtkTemplate.Child()
    gpucudalabelvalue=GtkTemplate.Child()
    gpumaxspeedlabelvalue=GtkTemplate.Child()
    gpuvramspeedlabelvalue=GtkTemplate.Child()
    gpuvrammaxspeedlabelvalue=GtkTemplate.Child()

    # Alternative way to specify multiple widgets
    #label1, entry = GtkTemplate.Child.widgets(2)

    def __init__(self):
        """Construct the GPU widget."""
        super(g.ScrolledWindow, self).__init__()

        # This must occur *after* you initialize your base
        self.init_template()
        # self.gpumxfactor=1             #for the scaling of maximum value on the graph

        #The main class self
        self.secondself=None

    def givedata(self,secondself):
        """
        Method to pass the data to the class(local) object from outside class. And assign them to the local class variables.

        Parameters
        ----------
        secondself : the main class reference(the main global self) which will be calling this function.
        index : index of the net adaptors from the list
        """
        self.gpuutilArray=secondself.gpuUtilArray
        self.gpuvramArray=secondself.gpuVramArray
        self.gpuencodingArray=secondself.gpuEncodingArray
        self.gpudecodingArray=secondself.gpuDecodingArray
        # Handle case where totalvram is "NA" or improperly formatted
        if secondself.totalvram and secondself.totalvram.strip() != 'NA' and len(secondself.totalvram) > 3:
            try:
                self.gputotalvram=int(secondself.totalvram[:-3])
            except ValueError:
                # If parsing fails, set to 0 or extract numeric value from string
                import re
                match = re.search(r'([\d.]+)', secondself.totalvram)
                if match:
                    self.gputotalvram=int(float(match.group(1)))
                else:
                    self.gputotalvram=0
        else:
            self.gputotalvram=0
        self.secondself=secondself

    @GtkTemplate.Callback
    def gpuutildrawarea_draw(self,dr,cr):
        """
        Function Binding(for draw signal) for gpu utilisation drawing area.

        This function draw the GPU Utilisation curves upon called by the queue of request generated in
        the main *updator* function.

        Parameters
        ----------
        dr : the widget on which to draw the graph
        cr : the cairo surface object
        """
        # Default line width
        cr.set_line_width(2)

        # Color Pofile setup
        color=self.secondself.color_profile['gpu'][0]
        rectangle_color=self.secondself.color_profile['gpu'][1]

        # Get the allocated widht and height
        w=self.gpuutildrawarea.get_allocated_width()
        h=self.gpuutildrawarea.get_allocated_height()
        scalingfactor=h/100.0

        #creating outer rectangle
        # cr.set_source_rgba(0,.454,.878,1)
        cr.set_source_rgba(*rectangle_color,1)
        cr.set_line_width(3)
        cr.rectangle(0,0,w,h)
        cr.stroke()
        # creating grid lines
        verticalGap=int(h/10)
        horzontalGap=int(w/10)
        for i in range(1,10):
            # cr.set_source_rgba(.384,.749,1.0,1) #for changing the outer line color
            cr.set_source_rgba(*color,1)
            cr.set_line_width(0.5)
            cr.move_to(0,i*verticalGap)
            cr.line_to(w,i*verticalGap)

            cr.move_to(i*horzontalGap,0)
            cr.line_to(i*horzontalGap,h)
            cr.stroke()
        cr.stroke()

        stepsize=w/99.0
        #print("in draw stepsize",stepsize)
        # for i in range(0,99):
        #     # not effcient way to fill the bars (drawing)
        #     cr.set_source_rgba(.588,.823,.98,0.25)   #for changing the fill color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuutilArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuutilArray[i+1]))
        #     cr.line_to((i+1)*stepsize,h)
        #     cr.line_to(i*stepsize,h)
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuutilArray[i]))

        #     cr.fill()
        #     cr.stroke()
        #     # for outer line
        #     cr.set_line_width(1.5)
        #     cr.set_source_rgba(.384,.749,1.0,1) #for changing the outer line color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuutilArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuutilArray[i+1]))
        #     cr.stroke()

        cr.set_line_width(1.5)
        # cr.set_source_rgba(.384,.749,1.0,1) #for changing the outer line color
        cr.set_source_rgba(*color,1)
        cr.move_to(0,scalingfactor*(100-self.gpuutilArray[0]))
        for i in range(0,99):
            cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuutilArray[i+1]))
        cr.stroke_preserve()

        # cr.set_source_rgba(.588,.823,.98,0.25)   #for changing the fill color
        cr.set_source_rgba(*color,0.2)
        cr.line_to(w,h)
        cr.line_to(0,h)
        cr.move_to(0,scalingfactor*(100-self.gpuutilArray[0]))
        cr.fill()
        cr.stroke()


        return False

    @GtkTemplate.Callback
    def gpuencodingdrawarea_draw(self,dr,cr):
        #print("idsaf")
        cr.set_line_width(2)

        # Color Pofile setup
        color=self.secondself.color_profile['gpu'][0]
        rectangle_color=self.secondself.color_profile['gpu'][1]

        w=self.gpuencodingdrawarea.get_allocated_width()
        h=self.gpuencodingdrawarea.get_allocated_height()
        scalingfactor=h/100.0
        #creating outer rectangle
        cr.set_source_rgba(*rectangle_color,1)
        cr.set_line_width(3)
        cr.rectangle(0,0,w,h)
        cr.stroke()
        # creating grid lines
        verticalGap=int(h/10)
        horzontalGap=int(w/10)
        for i in range(1,10):
            cr.set_source_rgba(*color,1)
            cr.set_line_width(0.5)
            cr.move_to(0,i*verticalGap)
            cr.line_to(w,i*verticalGap)

            cr.move_to(i*horzontalGap,0)
            cr.line_to(i*horzontalGap,h)
            cr.stroke()
        cr.stroke()

        stepsize=w/99.0
        #print("in draw stepsize",stepsize)
        # for i in range(0,99):
        #     # not effcient way to fill the bars (drawing)
        #     cr.set_source_rgba(.588,.823,.98,0.25)   #for changing the fill color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuencodingArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuencodingArray[i+1]))
        #     cr.line_to((i+1)*stepsize,h)
        #     cr.line_to(i*stepsize,h)
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuencodingArray[i]))

        #     cr.fill()
        #     cr.stroke()
        #     # for outer line
        #     cr.set_line_width(1.5)
        #     cr.set_source_rgba(.384,.749,1.0,1) #for changing the outer line color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpuencodingArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuencodingArray[i+1]))
        #     cr.stroke()

        #efficient encoding drawing
        cr.set_line_width(1.5)
        cr.set_source_rgba(*color,1)
        cr.move_to(0,scalingfactor*(100-self.gpuencodingArray[0]))
        for i in range(0,99):
            cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpuencodingArray[i+1]))
        cr.stroke_preserve()

        cr.set_source_rgba(*color,0.2)
        cr.line_to(w,h)
        cr.line_to(0,h)
        cr.move_to(0,scalingfactor*(100-self.gpuencodingArray[0]))
        cr.fill()
        cr.stroke()


        return False

    @GtkTemplate.Callback
    def gpudecodingdrawarea_draw(self,dr,cr):
        #print("idsaf")
        cr.set_line_width(2)

        # Color Pofile setup
        color=self.secondself.color_profile['gpu'][0]
        rectangle_color=self.secondself.color_profile['gpu'][1]

        w=self.gpudecodingdrawarea.get_allocated_width()
        h=self.gpudecodingdrawarea.get_allocated_height()
        scalingfactor=h/100.0
        #creating outer rectangle
        cr.set_source_rgba(*rectangle_color,1)
        cr.set_line_width(3)
        cr.rectangle(0,0,w,h)
        cr.stroke()
        # creating grid lines
        verticalGap=int(h/10)
        horzontalGap=int(w/10)
        for i in range(1,10):
            cr.set_source_rgba(*color,1)
            cr.set_line_width(0.5)
            cr.move_to(0,i*verticalGap)
            cr.line_to(w,i*verticalGap)

            cr.move_to(i*horzontalGap,0)
            cr.line_to(i*horzontalGap,h)
            cr.stroke()
        cr.stroke()

        stepsize=w/99.0
        #print("in draw stepsize",stepsize)
        # for i in range(0,99):
        #     # not effcient way to fill the bars (drawing)
        #     cr.set_source_rgba(.588,.823,.98,0.25)   #for changing the fill color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpudecodingArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpudecodingArray[i+1]))
        #     cr.line_to((i+1)*stepsize,h)
        #     cr.line_to(i*stepsize,h)
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpudecodingArray[i]))

        #     cr.fill()
        #     cr.stroke()
        #     # for outer line
        #     cr.set_line_width(1.5)
        #     cr.set_source_rgba(.384,.749,1.0,1) #for changing the outer line color
        #     cr.move_to(i*stepsize,scalingfactor*(100-self.gpudecodingArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpudecodingArray[i+1]))
        #     cr.stroke()

        cr.set_line_width(1.5)
        cr.set_source_rgba(*color,1)
        cr.move_to(0,scalingfactor*(100-self.gpudecodingArray[0]))
        for i in range(0,99):
            cr.line_to((i+1)*stepsize,scalingfactor*(100-self.gpudecodingArray[i+1]))
        cr.stroke_preserve()

        cr.set_source_rgba(*color,0.2)
        cr.line_to(w,h)
        cr.line_to(0,h)
        cr.move_to(0,scalingfactor*(100-self.gpudecodingArray[0]))
        cr.fill()
        cr.stroke()

        return False

    @GtkTemplate.Callback
    def gpuvramdrawarea_draw(self,dr,cr):
        # print('heloow  gpu')
        cr.set_line_width(2)

        # Color Pofile setup
        color=self.secondself.color_profile['gpu'][0]
        rectangle_color=self.secondself.color_profile['gpu'][1]

        w=self.gpuvramdrawarea.get_allocated_width()
        h=self.gpuvramdrawarea.get_allocated_height()
        
        # Prevent division by zero - use default value if gputotalvram is 0 or missing
        vram_total = getattr(self, 'gputotalvram', 1)
        if vram_total == 0:
            vram_total = 1
        
        scalingfactor=h/vram_total
        # print(self.gputotalvram)
        #creating outer rectangle
        cr.set_source_rgba(*rectangle_color,1)
        cr.set_line_width(3)
        cr.rectangle(0,0,w,h)
        cr.stroke()
        # creating grid lines
        verticalGap=int(h/10)
        horzontalGap=int(w/10)
        for i in range(1,10):
            cr.set_source_rgba(*color,1)
            cr.set_line_width(0.5)
            cr.move_to(0,i*verticalGap)
            cr.line_to(w,i*verticalGap)

            cr.move_to(i*horzontalGap,0)
            cr.line_to(i*horzontalGap,h)
        cr.stroke()

        stepsize=w/99.0
        #print("in draw stepsize",stepsize)
        # for i in range(0,99):
        #     # not effcient way to fill the bars (drawing)
        #     cr.set_source_rgba(.588,.823,.98,0.25)   #for changing the fill color
        #     cr.move_to(i*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i+1]))
        #     cr.line_to((i+1)*stepsize,h)
        #     cr.line_to(i*stepsize,h)
        #     cr.move_to(i*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i]))

        #     cr.fill()
        #     cr.stroke()
        #     # for outer line
        #     cr.set_line_width(1.5)
        #     cr.set_source_rgba(.384,.749,1.0,1)   #for changing the outer line color
        #     cr.move_to(i*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i]))
        #     cr.line_to((i+1)*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i+1]))
        #     cr.stroke()

        cr.set_line_width(1.5)
        cr.set_source_rgba(*color,1)
        cr.move_to(0,scalingfactor*(self.gputotalvram-self.gpuvramArray[0]))
        for i in range(0,99):
            cr.line_to((i+1)*stepsize,scalingfactor*(self.gputotalvram-self.gpuvramArray[i+1]))
        cr.stroke_preserve()

        cr.set_source_rgba(*color,0.2)
        cr.line_to(w,h)
        cr.line_to(0,h)
        cr.move_to(0,scalingfactor*(self.gputotalvram-self.gpuvramArray[0]))
        cr.fill()
        cr.stroke()

        return False



# Helper function to parse sensors output for AMD GPU data
def parse_amd_sensors_output(sensors_output):
    """
    Parse sensors output to extract AMD GPU information.
    
    Returns:
        dict: Dictionary containing fan_rpm, gpu_temp, current_power, max_power
    """
    result = {
        'fan_rpm': 0,
        'gpu_temp': 'NA',
        'current_power': 0,
        'max_power': 1  # Default max power if not found
    }
    
    lines = sensors_output.split('\n')
    in_amdgpu_section = False
    
    for line in lines:
    
        if 'amdgpu-pci' not in line.lower() and not in_amdgpu_section:
            continue
        
        in_amdgpu_section = True
            
        if line.strip() == '':
            in_amdgpu_section = False
            break
            
        # Parse fan1 RPM
        if 'fan1' in line.lower():
            match = re.search(r'(\d+)\s*RPM', line)
            if match:
                result['fan_rpm'] = int(match.group(1))
        
        # Parse edge temperature (GPU temp)
        if 'edge' in line.lower() or line.startswith('edge:'):
            match = re.search(r'\+(\d+\.?\d*)°?C', line)
            if match:
                result['gpu_temp'] = f"+{match.group(1)}°C"
        
        # Parse PPT power (current and max)
        if 'PPT:' in line:
            match = re.search(r'PPT:\s*([\d.]+)\s*W\s*\((cap\s*=\s*)?([\d.]+)\s*W', line, re.IGNORECASE)
            if match:
                result['current_power'] = float(match.group(1))
                result['max_power'] = float(match.group(3))
    
    return result

# Helper function to extract GPU name from glxinfo output
def extract_gpu_name_from_glxinfo(glxinfo_output):
    """
    Extract GPU/device name from glxinfo Extended renderer info.

    Returns:
        str: GPU name or "NA" if not found
    """
    gpu_section = False
    for line in glxinfo_output.splitlines():
        # Detect the start of the Extended renderer info section
        if line.strip().startswith('Extended renderer info (GLX_MESA_query_renderer):') and not gpu_section:
            gpu_section = True
            continue
        if not gpu_section:
            continue
        # End of the section is indicated by a blank line or a line that doesn't start with whitespace
        if line.strip() == '' or not line.startswith(' '):
            break
        # Extract the device line
        stripped = line.strip()
        if stripped.startswith('Device:'):
            device_match = re.search(r'Device:\s*([^\(]+)', stripped)
            if device_match:
                return device_match.group(1).strip()
    return "NA"

# Helper function to extract VRAM info from glxinfo output
def extract_vram_info_from_glxinfo(glxinfo_output):
    """
    Extract VRAM information from glxinfo Memory info sections.
    
    Returns:
        tuple: (total_vram_mb, available_dedicated_memory_mb)
    """
    # First try GL_NVX_gpu_memory_info block (preferred)
    gpu_section = False
    dedicated_match = None
    available_match = None
    for line in glxinfo_output.splitlines():
        # Detect the start of the Extended renderer info section
        if line.strip().startswith('Memory info (GL_NVX_gpu_memory_info):') and not gpu_section:
            gpu_section = True
            continue
        if not gpu_section:
            continue
        # End of the section is indicated by a blank line or a line that doesn't start with whitespace
        if line.strip() == '' or not line.startswith(' '):
            break
        # Extract the device line
        stripped = line.strip()
        if 'Dedicated video memory:' in stripped:
            dedicated_match = re.search(r'Dedicated video memory:\s*([\d.]+)\s*MB', stripped)
        
        if 'Currently available dedicated video memory:' in stripped:
            available_match = re.search(r'Currently available dedicated video memory:\s*([\d.]+)\s*MB', stripped)
    
    if dedicated_match and available_match:
        total_vram = int(float(dedicated_match.group(1)))
        used_dedicated = float(available_match.group(1))
        return f"{total_vram} MiB", f"{used_dedicated:.0f} MiB"
    
    return "0 MiB", "0 MiB"


def gpuinit(self):
    ##logic to determine the number of gpus but for now i just focusing on one gpu
    self.isNvidiagpu=1
    self.gpuUtilArray=[0]*100
    self.gpuEncodingArray=[0]*100
    self.gpuDecodingArray=[0]*100
    self.gpuVramArray=[0]*100
    try:
        p=popen('nvidia-smi -q -x')
        xmlout=p.read()
        p.close()
        gpuinfoRoot=fromstring(xmlout)
        print('okk')
        self.gpuWidget=gpuTabWidget()
        self.performanceStack.add_titled(self.gpuWidget,f'page{self.stack_counter}','GPU')

        self.gpuName=gpuinfoRoot.find('gpu').find('product_name').text
        self.gpuWidget.gpuinfolabel.set_text(self.gpuName)
        self.totalvram=gpuinfoRoot.find('gpu').find('fb_memory_usage').find('total').text
        self.gpuWidget.gpuvramlabelvalue.set_text(self.totalvram)
        self.gpuWidget.gpudriverlabelvalue.set_text(gpuinfoRoot.find('driver_version').text)
        self.gpuWidget.gpucudalabelvalue.set_text(gpuinfoRoot.find('cuda_version').text)
        self.gpuWidget.gpumaxspeedlabelvalue.set_text(gpuinfoRoot.find('gpu').find('max_clocks').find('graphics_clock').text)
        self.gpuWidget.gpuvrammaxspeedlabelvalue.set_text(gpuinfoRoot.find('gpu').find('max_clocks').find('mem_clock').text)

        # For lookup of devices and its assigned stack page numbers
        self.device_stack_page_lookup[self.gpuName]=self.stack_counter
        self.stack_counter+=1

        self.gpuWidget.givedata(self)
    except Exception as e:
        print('no nvidia gpu found',e)
        self.isNvidiagpu=0
    
    self.isAMDgpu=0
    
    try:
        # Check for AMD GPU if Nvidia not found
        # First check for amdgpu-pci in sensors
        sensors_out = popen('sensors 2>/dev/null')
        sensors_output = sensors_out.read()
        sensors_out.close()
        
        if 'amdgpu-pci' in sensors_output:
            # Get glxinfo for GPU name and VRAM
            glxinfo_out = popen('glxinfo 2>/dev/null')
            glxinfo_output = glxinfo_out.read()
            glxinfo_out.close()
            
            # Extract device info from glxinfo
            if 'Vendor: AMD' in glxinfo_output or 'Radeon' in glxinfo_output or 'radeonsi' in glxinfo_output:
                self.isAMDgpu=1
                self.gpuWidget=gpuTabWidget()
                self.performanceStack.add_titled(self.gpuWidget,f'page{self.stack_counter}','GPU')
                self.gpuName = extract_gpu_name_from_glxinfo(glxinfo_output)
                
                # Get VRAM info
                total_vram, vram_usage_str = extract_vram_info_from_glxinfo(glxinfo_output)
                self.totalvram = total_vram
                self.gpuWidget.gpuvramlabelvalue.set_text(total_vram)
                # Initialize gputotalvram as int (required for drawing)
                if total_vram and str(total_vram).strip() != '0MiB' and len(str(total_vram)) > 3:
                    try:
                        self.gputotalvram = int(float(total_vram[:-3]))
                    except ValueError:
                        self.gputotalvram = 0
                
                temp_result = parse_amd_sensors_output(sensors_output)
                
                # Set GPU name and VRAM
                self.gpuWidget.gpuinfolabel.set_text(self.gpuName)
                
                # For AMD, we don't have driver/cuda versions, set to NA
                self.gpuWidget.gpudriverlabelvalue.set_text("NA")
                self.gpuWidget.gpucudalabelvalue.set_text("NA")
                
                # Set clock speeds - AMD doesn't expose this via sensors in same way
                # We'll leave these as NA for now
                self.gpuWidget.gpumaxspeedlabelvalue.set_text("NA")
                self.gpuWidget.gpuvrammaxspeedlabelvalue.set_text("NA")
                
                # Set initial temperature and utilization to sensor values
                gpu_temp = temp_result['gpu_temp']
                self.gpuWidget.gputemplabelvalue.set_text(gpu_temp)
                
                self.gpuWidget.gpushaderspeedlabelvalue.set_text("NA")
                self.gpuWidget.gpuvramspeedlabelvalue.set_text("NA")
                
                # Calculate utilization from PPT power
                if temp_result['current_power'] > 0 and temp_result['max_power'] > 0:
                    gpu_util_pct = int((temp_result['current_power'] / temp_result['max_power']) * 100)
                    self.gpuutil = str(gpu_util_pct) + ' %'
                    self.gpuWidget.gpuutilisationlabelvalue.set_text(f"{gpu_util_pct} %")
                else:
                    self.gpuutil = "0 %"
                    self.gpuWidget.gpuutilisationlabelvalue.set_text("0 %")
                    
                # For lookup of devices and its assigned stack page numbers
                self.device_stack_page_lookup[self.gpuName] = self.stack_counter
                self.stack_counter += 1
                
                self.gpuWidget.givedata(self)
    except Exception as e:
        print('no amd gpu found',e)
        self.isAMDgpu=0


def gpuUpdate(self):
    try:
        if self.isNvidiagpu:
            # Nvidia GPU update path (existing code)
            p=popen('nvidia-smi -q -x')
            xmlout=p.read()
            p.close()
            gpuinfoRoot=fromstring(xmlout)
            self.vramused=gpuinfoRoot.find('gpu').find('fb_memory_usage').find('used').text
            self.gpuutil=gpuinfoRoot.find('gpu').find('utilization').find('gpu_util').text
            self.gpuWidget.gpuutilisationlabelvalue.set_text(self.gpuutil)
            self.gpuWidget.gpuvramusagelabelvalue.set_text(f'{self.vramused[:-3]}/{self.totalvram}')

            gpu_temp=gpuinfoRoot.find('gpu').find('temperature').find('gpu_temp').text
            if gpu_temp[-1]=='C':
                gpu_temp =f'{gpu_temp[:-1]}°C'

            self.gpuWidget.gputemplabelvalue.set_text(gpu_temp)
            self.gpuWidget.gpushaderspeedlabelvalue.set_text(gpuinfoRoot.find('gpu').find('clocks').find('graphics_clock').text)
            self.gpuWidget.gpuvramspeedlabelvalue.set_text(gpuinfoRoot.find('gpu').find('clocks').find('mem_clock').text)

            ############ int conv bug solve ######################
            gpu_enc=gpuinfoRoot.find('gpu').find('utilization').find('encoder_util').text
            try:
                gpu_enc=int(gpu_enc[:-1])
            except Exception:
                gpu_enc=0

            gpu_dec=gpuinfoRoot.find('gpu').find('utilization').find('decoder_util').text

            try:
                gpu_dec=int(gpu_dec[:-1])
            except Exception:
                gpu_dec=0

        elif self.isAMDgpu:
            # AMD GPU update path - use sensors
            sensors_out = popen('sensors 2>/dev/null')
            sensors_output = sensors_out.read()
            sensors_out.close()
            
            glxinfo_out = popen('glxinfo 2>/dev/null')
            glxinfo_output = glxinfo_out.read()
            glxinfo_out.close()
            
            # Parse temperature
            temp_result = parse_amd_sensors_output(sensors_output)
            
            total_vram, vram_usage_str = extract_vram_info_from_glxinfo(glxinfo_output)
            
            # Update labels with sensor data
            self.gpuWidget.gputemplabelvalue.set_text(temp_result['gpu_temp'])
            
            # Calculate utilization from PPT power
            if temp_result['current_power'] > 0 and temp_result['max_power'] > 0:
                gpu_util_pct = int((temp_result['current_power'] / temp_result['max_power']) * 100)
                self.gpuutil = str(gpu_util_pct) + ' %'
                self.gpuWidget.gpuutilisationlabelvalue.set_text(f"{gpu_util_pct} %")
            else:
                self.gpuutil = "0 %"
                self.gpuWidget.gpuutilisationlabelvalue.set_text("0 %")
            
            # Update VRAM usage from glxinfo (static for now, as it changes with OpenGL context)
            # For AMD, we can't reliably get current VRAM usage without glxinfo with specific context
            if hasattr(self, 'totalvram') and self.totalvram and str(self.totalvram).strip() != '0 MiB':
                self.gpuWidget.gpuvramusagelabelvalue.set_text(f"{vram_usage_str[:-3]}/{self.totalvram}")
            
            # Set clocks to NA for AMD (not exposed in sensors)
            self.gpuWidget.gpushaderspeedlabelvalue.set_text("NA")
            self.gpuWidget.gpuvramspeedlabelvalue.set_text("NA")
            
        if self.update_graph_direction:
            self.gpuUtilArray.pop(0)
            try:
                # Extract percentage value from utilization string
                util_val = int(self.gpuutil[:-1]) if '%' in self.gpuutil else int(self.gpuutil)
                self.gpuUtilArray.append(util_val)
            except Exception:
                self.gpuUtilArray.append(0)

            self.gpuVramArray.pop(0)
            # Only get VRAM data if we're on Nvidia (have gpuinfoRoot); otherwise use default
            if 'gpuinfoRoot' in dir():
                try:
                    vram_str = gpuinfoRoot.find('gpu').find('fb_memory_usage').find('used').text[:-3]
                    self.gpuVramArray.append(int(vram_str))
                except Exception:
                    self.gpuVramArray.append(0)
            else:
                # For AMD, use half of total VRAM as placeholder
                try:
                    vram_usage = int(float(vram_usage_str[:-3]))
                except ValueError:
                    vram_usage = 0
                
                self.gpuVramArray.append(vram_usage)

            self.gpuEncodingArray.pop(0)
            self.gpuEncodingArray.append(0)  # AMD doesn't have encoder util in same format

            self.gpuDecodingArray.pop(0)
            self.gpuDecodingArray.append(0)  # AMD doesn't have decoder util in same format
        else:
            self.gpuUtilArray.pop()
            try:
                util_val = int(self.gpuutil[:-1]) if '%' in self.gpuutil else int(self.gpuutil)
                self.gpuUtilArray.insert(0,util_val)
            except Exception:
                self.gpuUtilArray.insert(0,0)

            self.gpuVramArray.pop()
            try:
                if 'gpuinfoRoot' in dir():
                    vram_str = gpuinfoRoot.find('gpu').find('fb_memory_usage').find('used').text[:-3]
                else:
                    vram_str = vram_usage_str[:-3]
                self.gpuVramArray.insert(0,int(vram_str))
            except Exception:
                self.gpuVramArray.insert(0,0)

            self.gpuEncodingArray.pop()
            self.gpuEncodingArray.insert(0,0)
            self.gpuDecodingArray.pop()
            self.gpuDecodingArray.insert(0,0)

        self.gpuWidget.givedata(self)
    except Exception as e:
        print(f"some error in gpu updata: {e}")

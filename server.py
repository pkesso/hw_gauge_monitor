from sys import exit
import GPUtil
import serial
from pyspectator.computer import  Cpu,VirtualMemory
from time import sleep
from yaml import safe_load

# config
try:
    with open("config.yaml", "r") as config_file:
        config = safe_load(config_file)
except yaml.YAMLError as exc:
    print('Can\'t load config from file')
    print(exc)
    exit(1)
    
# serial port
try:
    port = serial.Serial(timeout=3)
    port.baudrate = 115200
    port.port = config['port']
    port.open()
    bad_serial = False
except:
    print('Can\'t open serial port')
    print(exc)
    exit(1)

cpu = Cpu(monitoring_latency=config['delay'])
ram = VirtualMemory(monitoring_latency=config['delay'])

# send loop
try:
    with cpu, ram:
        while True:
            gpu = GPUtil.getGPUs()[config['gpu_index']]    
            #ram = comp.virtual_memory
      
            # raw
            '''
            cpu_load = str(int(cpu.load))
            cpu_temp = str(int(cpu.temperature)) 
            ram_used = str(int(ram.used_percent))
            gpu_load = str(int(100*gpu.load))
            gpu_temp = str(int(gpu.temperature))
            vram_used = str(int(100*round(float(gpu.memoryUsed)/float(gpu.memoryTotal), 0)))
            '''
            gpu_load = str(int(100*gpu.load*2.55))
            gpu_temp = str(int(2.55*100*((gpu.temperature - 30)/(88 - 30)))) # gpu temp 30 - 88
            vram_used = str(int(2.55*100*(float(gpu.memoryUsed)/float(gpu.memoryTotal))))
            cpu_load = str(int(cpu.load*2.55))
            cpu_temp = str(int(cpu.temperature)) # FIXME stuck # cpu temp 20 - 74
            cpu_temp = str(int(2.55*100*((cpu.temperature - 20)/(74 - 20))))
            ram_used = str(int(ram.used_percent*2.55))

            print('###########################')
            print(f"CPU load   raw {cpu.load}    bits {cpu_load}")
            print(f"RAM used   raw {ram.used_percent}     bits {ram_used}")
            print(f"CPU temp   raw {cpu.temperature}     bits {cpu_temp}")
            print(f"GPU load   raw {100*gpu.load}    bits {gpu_load}")
            print(f"VRAM used  raw {round(100*(float(gpu.memoryUsed)/float(gpu.memoryTotal)), 0)}    bits {vram_used}")
            print(f"GPU temp   raw {gpu.temperature}   bits {gpu_temp}")

            # sending bytestring to the device
            port.write(bytes(cpu_load+' '+ram_used+' '+cpu_temp+' '+gpu_load+' '+vram_used+' '+gpu_temp+'\n', encoding="ascii"))
            
            # recieving device's response
            #response = port.readline()
            response = port.readline().decode("ascii")
            #response = port.readline().decode("utf-8")
            print(f"Device says: {response}")
            
            sleep(config['delay'])

# ctrl-c
except (KeyboardInterrupt, IndexError): # IndexError happens on ctrl-c
    exit_code = 0
    print('Keyboard Interrupt')

# serial port disconnection
except serial.SerialException as sp_exc:
    exit_code = 1
    bad_serial = True
    print('Lost serial port connection')
    print(exc)

# other bad things
except Exception as other_exc:
    exit_code = 1
    print('Something went wrong')
    print(other_exc)

# cleanup
finally:
    if not bad_serial:
        port.write(bytes('0 0 0 0 0 0\n', encoding="ascii"))
        port.close()
    print('###########################')
    print(f"Exiting ({exit_code})")
    exit(exit_code)

from typing import List

from nmigen import *
from nmigen.sim import *
from nmigen import Elaboratable, Module, Signal
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner

class Flash_Controller(Elaboratable):
    def __init__(self):
        self.chip_select = Signal()
        self.write_protect = Signal()
        self.hold = Signal() 
        #clk serial clock input
        self.data_in = Signal(24)
        self.data_out = Signal(24)

        self.byte_1 = Signal(8)
        self.byte_2 = Signal(8)
        self.byte_3 = Signal(8)
        self.byte_4 = Signal(8)

        #status registers 
        # self.busy = Signal() #status register s0
        # self.wel = Signal()  #status register s1
        # self.BP2 = Signal()  #status register s4
        # self.BP1 = Signal()  #status register s3
        # self.BP0 = Signal()  #status register s2
        # self.TB = Signal() 
        # #s6 register bit location is reserved for future use
        # self.SRP = Signal()  #status register s7
        self.status_register = Signal(8)
        self.Memory = Array([Signal(256) for i in range(2048)])

        self.write_enable =                0b00000110 #06h
        self.write_enable_VSG =            0b01010000 #50h
        self.write_disable =               0b00000100 #04h
        self.read_status_reg =             0b00000101 #05h
        self.write_status_reg =            0b00000001 #01h
        self.read_data =                   0b00000011 #03h
        self.fast_read =                   0b00001011 #0Bh
        self.fast_read_dual_o =            0b00111011 #3Bh
        self.fast_read_dual_io =           0b10111011 #BBh
        self.page_prog =                   0b00000010 #02h
        self.sec_erase =                   0b00100000 #20h
        self.blk_erase_32kb =              0b01010010 #52h
        self.blk_erase_64kb =              0b11011000 #D8h
        self.chip_erase =                  0b11000111 #C7h  or   0b01100000 60h need to check for both 
        self.power_down =                  0b10111001 #B9h
        self.rel_power_down_dev_id =       0b10101011 # ABh
        self.manufacturer_dev_id =         0b10010000 # 90h
        self.manufacturer_dev_id_dual_io = 0b10010010 # 92h
        self.jedec_id =                    0b10011111 # 9Fh
        self.read_unique_id =              0b00101011 #4Bh
        
        
        self.counter =0b0000000000 
        self.chip_select = 0b1

        

    def elaborate(self,platform:Platform)->Module:
        m= Module()
        m.d.comb += self.chip_select.eq(0b0)
        m.d.neg += self.byte_1[self.counter].eq(self.data_in[self.counter])
        m.d.sync +=  self.counter.eq(self.counter + 0b0000000001)

#need to see about chip select
        with m.Switch(self.byte_1):
            with m.Case(self.write_enable):
                #set write enable latch to 1
                with m.If(self.counter == 0b0000000100) :
                    m.d.sync += self.counter.eq(0b0000000000)
                    m.d.comb += self.chip_select.eq(0b1)
                    m.d.comb+=self.status_register[Const(0)].eq(0b1)
            
            with m.Case(self.write_disable):
                with m.If(self.counter == 0b0000000100) :
                    m.d.sync += self.counter.eq(0b0000000000)
                    m.d.comb += self.chip_select.eq(0b1)
                    m.d.comb+=self.status_register[Const(0)].eq(0b0)
            # with m.Case(self.write_enable_VSG):
            #     m.d.comb += self.
            
            with m.case(self.read_status_reg):
                with m.If(self.counter == 0b0000000100):
                    with m.If(self.status_register[Const(0)]==0b0):
                        m.d.comb+=self.data_out[0:7].eq(self.status_register)

            with m.case(self.write_status_reg):
                with m.If(self.write_protect == 0b1):#write protect pin
                    with m.If(self.status_register[Const(1)]==0b1):
                        with m.If(self.counter == 0b0000001000) :
                            m.d.comb+=self.status_register[Const(7)].eq(self.data_in[Const(7)])
                            m.d.comb+=self.status_register[Const(5)].eq(self.data_in[Const(5)])
                            m.d.comb+=self.status_register[Const(4)].eq(self.data_in[Const(4)])
                            m.d.comb+=self.status_register[Const(3)].eq(self.data_in[Const(3)])
                            m.d.comb+=self.status_register[Const(2)].eq(self.data_in[Const(2)])
                            m.d.comb+=self.status_register[Const(0)].eq(0b1)#busy bit  doubt
                            m.d.comb+=self.status_register[Const(1)].eq(0b0)#wel reset to 0
                            m.d.comb += self.chip_select.eq(0b1)
















        return m 

    def ports(self)->List[Signal]:
        return []     


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    m = Module()
    m.domains.sync = sync = ClockDomain("sync", async_reset=True)
    pos = ClockDomain("pos", async_reset=True)
    neg = ClockDomain("neg",clk_edge="neg",async_reset=True)
    neg.clk = pos.clk
    m.domains += [neg,pos]

    m.submodules.Flash_Controller1 = Flash_Controller1 = Flash_Controller()

    sim = Simulator(m)
    sim.add_clock(1e-6, domain="sync")
    sim.add_clock(1e-6,domain="pos")
    sim.add_clock(1e-6,domain = "neg")
    
    def process():
        yield 
        #yield Delay(1e-6)


sim.add_sync_process(process,domain="sync")
with sim.write_vcd("test.vcd", "test.gtkw", traces=Flash_Controller1.ports()):
    sim.run_until(100e-6, run_passive=True)




# verilog-------------------------------------------------------------------------------
# Flash_Controller  = Flash_Controller()
# frag = Flash_Controller.elaborate(platform=None)
# print(verilog.convert(frag, ports=Flash_Controller.ports()))


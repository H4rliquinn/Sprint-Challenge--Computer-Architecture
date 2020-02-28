"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.ram=[0b00000000]*40
        self.PC=0b00000000   # * `PC`: Program Counter, address of the currently executing instruction
        self.MAR=0b00000000  # * `MAR`: Memory Address Register, holds the memory address we're reading or writing
        self.MDR=0b00000000  # * `MDR`: Memory Data Register, holds the value to write or the value just read
        self.IR=0b00000000   # * `IR`: Instruction Register, contains a copy of the currently executing instruction
        self.FL=0b00000000   # * `FL`: Flags, see below
        self.bt={} #Branch Table
        self.bt[0b00011111]=self.BEEJ
        self.bt[0b10000010]=self.LDI
        self.bt[0b01000111]=self.PRN
        self.bt[0b10100010]=self.MUL
        self.bt[0b10100000]=self.ADD
        self.bt[0b01000101]=self.PUSH
        self.bt[0b01000110]=self.POP
        self.bt[0b01010000]=self.CALL
        self.bt[0b00010001]=self.RET
        self.bt[0b00000001]=self.HLT

        self.registers=[0]*8
        self.R0=0b00000000
        self.R1=0b00000001
        R2=0b00000010
        R3=0b00000011
        R4=0b00000100
        IM=0b00000101   # * R5 is reserved as the interrupt mask (IM)
        IS=0b00000110   # * R6 is reserved as the interrupt status (IS)
        self.SP=0b00000111   # * R7 is reserved as the stack pointer (SP)
        self.registers[self.SP]=40

    def BEEJ(self):
        print("Beej!")

    def LDI(self):
        self.MAR=self.PC+1
        self.ram_read()
        operand_a=self.MDR
        self.MAR=self.PC+2
        self.ram_read()
        operand_b=self.MDR
        self.registers[operand_a]=operand_b

    def PRN(self):
        self.MAR=self.PC+1
        self.ram_read()
        operand_a=self.MDR 
        print(self.registers[operand_a])

    def MUL(self):
        self.MAR=self.PC+1
        self.ram_read()
        operand_a=self.MDR 
        self.MAR=self.PC+2
        self.ram_read()
        operand_b=self.MDR 
        self.alu('MULT',operand_a,operand_b)

    def ADD(self):
        self.MAR=self.PC+1
        self.ram_read()
        operand_a=self.MDR 
        self.MAR=self.PC+2
        self.ram_read()
        operand_b=self.MDR 
        self.alu('ADD',operand_a,operand_b)
        
    def PUSH(self):
        # Get Value to push
        operand_a=self.registers[self.ram[self.PC+1]]
        # Decrement the SP.
        self.registers[self.SP] -= 1
        # Copy the value in the given register to the address pointed to by SP
        self.ram[self.registers[self.SP]] = operand_a

    def POP(self):
        # Grab the value from the top of the stack
        operand_a = self.ram[self.registers[self.SP]]
        # Copy the value from the address pointed to by SP to the given register.
        self.registers[self.ram[self.PC+1]]=operand_a
        # Increment SP.
        self.registers[self.SP] += 1

    def CALL(self):
        self.registers[self.SP] -= 1
        self.ram[self.registers[self.SP]]=self.PC+2
        self.MAR=self.PC+1
        self.ram_read()
        operand_a=self.MDR
        self.PC=self.registers[operand_a]

    def RET(self):
        self.PC=self.ram[self.registers[self.SP]]
        self.registers[self.SP] += 1

    def HLT(self):
        sys.exit(0)

    def ram_read(self):
        self.MDR=self.ram[self.MAR]

    def ram_write(self):
        self.ram[self.MAR]=self.MDR

    def load(self):
        """Load a program into memory."""

        mem_pointer=0
        if len(sys.argv)!=2:
            print("Error: No Filename")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split=line.split("#")
                    value=comment_split[0].strip()
                    if value=='':
                        continue

                    num=int(value,2)
                    self.ram[mem_pointer]=num
                    mem_pointer+=1
        except FileNotFoundError:
            print("File Not Found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "SUB": 
            self.registers[reg_a] -= self.registers[reg_b]
        elif op == "MULT":
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == "DIV":
            self.registers[reg_a] /= self.registers[reg_b]
        elif op == "MOD":
            self.registers[reg_a] %= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            self.MAR=self.PC
            self.ram_read()
            self.IR=self.MDR
            self.bt[self.IR]()
            if self.IR not in [0b01010000,0b00010001]:
                self.PC+=(self.IR>>6)+1

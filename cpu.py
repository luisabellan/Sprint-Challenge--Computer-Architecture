"""CPU functionality."""
import sys


# OP CODES
CMP = 0b10100111
MUL = 0b10100010
LDI = 0b10000010
ADD = 0b10100000
PRN = 0b01000111
JEQ = 0b01010101
JNE = 0b01010110
HLT = 0b00000001
AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
PUSH = 0b01000101
RET = 0b00010001
POP = 0b01000110
CALL = 0b01010000
JMP = 0b01010100
XOR = 0b10101011
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8 
        self.pc = 0 
        self.sp = 244 # F4 = 244 
        self.reg[7] = self.sp
        self.running = True 
        self.flag = [0] * 8 
        self.operations = { 
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET : self.ret,
            CMP: self.cmp,
            JEQ: self.my_jeq,
            JNE: self.my_jne,
            AND: self.my_and,
            NOT: self.my_not,
            OR: self.my_or,
            XOR: self.my_xor
        }
        
    
   

    def load(self):
        """Load a program into memory."""

        address = 0

        filename = sys.argv[1]
      
        with open(filename)as f:
            for line in f:
                line = line.split("#")
                opcode = line[0].strip()
                if opcode == "":
                    continue
                num = int(opcode, 2)
                self.ram_write(num, address)
                address += 1
            
    def ram_read(self, mar):
        
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

   
    def alu(self, op, reg_a, reg_b=0):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == CMP:
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
        # Stretch                
        elif op == AND:
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] |= self.reg[reg_b]
            
        # #########################################
        #    -  Python bitwise not operation   -  #  
        # #########################################
        # def bit_not(n, numbits=8):              #
        #                                         #  
        #     return (1 << numbits) - 1 - n       #
        # #########################################

        elif op == NOT:
           
            self.reg[reg_a] = (1 << 8) - 1 - self.reg[reg_a] 

        elif op == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]
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
    
    # Operations

    def hlt(self, operand_a, operand_b):
        self.running = False

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])





    def push(self, operand_a, operand_b):
        self.sp -= 1
        self.ram_write(self.reg[operand_a], self.sp)

    def pop(self, operand_a, operand_b):
        value = self.ram_read(self.sp)
        self.reg[operand_a] = value
        self.sp += 1




    def call(self, operand_a, operand_b):
        self.sp -= 1
        self.ram_write(self.pc + 2, self.sp)
        self.pc = self.reg[operand_a]
    

    def ret(self, operand_a, operand_b):
        self.pc = self.ram_read(self.sp)
        self.sp += 1
    
    def cmp(self, operand_a, operand_b):
        self.alu(CMP, operand_a, operand_b)
        self.pc += 3
    



    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def my_jeq(self, operand_a, operand_b):
        if self.flag == True:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def my_jne(self, operand_a, operand_b):
        if self.flag != 1:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2



    def my_and(self, operand_a, operand_b):
        self.alu(AND, operand_a, operand_b)
        self.pc += 3
    def my_not(self, operand_a):
        self.alu(NOT, operand_a)
        self.pc += 3

    def my_or(self, operand_a, operand_b):
        self.alu(OR, operand_a, operand_b)
        self.pc += 3

    def my_xor(self, operand_a, operand_b):
        self.alu(XOR, operand_a, operand_b)
        self.pc += 3
    
        

    def run(self):
        """Run the CPU."""
        # While CPU is running
        while self.running:
           
            curr_instruction = self.ram_read(self.pc)

          
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            #  is an ALU operation operation?
            is_alu = (curr_instruction >> 5) & 0b00000001

            if is_alu == 1:
                self.alu(curr_instruction, operand_a, operand_b)
           
            else:
                if curr_instruction in self.operations:
                    self.operations[curr_instruction](operand_a, operand_b)
            
            # Find next instruction 
            next_instruction = (curr_instruction >> 4) & 0b00000001

            if next_instruction == 0:
                
                num_operands = curr_instruction >> 6
               
                self.pc += num_operands + 1
            
           

            
        
        

   
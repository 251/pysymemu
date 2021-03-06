
from smtlib import Solver
from cpu import Cpu

import unittest

sizes = {'RAX': 64, 'EAX': 32, 'AX': 16, 'AL': 8, 'AH': 8, 'RCX': 64, 'ECX': 32, 'CX': 16, 'CL': 8, 'CH': 8, 'RDX': 64, 'EDX': 32, 'DX': 16, 'DL': 8, 'DH': 8, 'RBX': 64, 'EBX': 32, 'BX': 16, 'BL': 8, 'BH': 8, 'RSP': 64, 'ESP': 32, 'SP': 16, 'SPL': 8, 'RBP': 64, 'EBP': 32, 'BP': 16, 'BPL': 8, 'RSI': 64, 'ESI': 32, 'SI': 16, 'SIL': 8, 'RDI': 64, 'EDI': 32, 'DI': 16, 'DIL': 8, 'R8': 64, 'R8D': 32, 'R8W': 16, 'R8B': 8, 'R9': 64, 'R9D': 32, 'R9W': 16, 'R9B': 8, 'R10': 64, 'R10D': 32, 'R10W': 16, 'R10B': 8, 'R11': 64, 'R11D': 32, 'R11W': 16, 'R11B': 8, 'R12': 64, 'R12D': 32, 'R12W': 16, 'R12B': 8, 'R13': 64, 'R13D': 32, 'R13W': 16, 'R13B': 8, 'R14': 64, 'R14D': 32, 'R14W': 16, 'R14B': 8, 'R15': 64, 'R15D': 32, 'R15W': 16, 'R15B': 8, 'ES': 16, 'CS': 16, 'SS': 16, 'DS': 16, 'FS': 16, 'GS': 16, 'RIP': 64, 'EIP':32, 'IP': 16, 'RFLAGS': 64, 'EFLAGS': 32, 'FLAGS': 16, 'XMM0': 128, 'XMM1': 128, 'XMM2': 128, 'XMM3': 128, 'XMM4': 128, 'XMM5': 128, 'XMM6': 128, 'XMM7': 128, 'XMM8': 128, 'XMM9': 128, 'XMM10': 128, 'XMM11': 128, 'XMM12': 128, 'XMM13': 128, 'XMM14': 128, 'XMM15': 128, 'YMM0': 256, 'YMM1': 256, 'YMM2': 256, 'YMM3': 256, 'YMM4': 256, 'YMM5': 256, 'YMM6': 256, 'YMM7': 256, 'YMM8': 256, 'YMM9': 256, 'YMM10': 256, 'YMM11': 256, 'YMM12': 256, 'YMM13': 256, 'YMM14': 256, 'YMM15': 256}

class SymCPUTest(unittest.TestCase):
    class ROOperand(object):
        ''' Mocking class for operand ronly '''
        def __init__(self, size, value):
            self.size = size
            self.value = value
        def read(self):
            return self.value & ((1<<self.size)-1)

    class RWOperand(ROOperand):
        ''' Mocking class for operand rw '''
        def write(self, value):
            self.value = value & ((1<<self.size)-1)
            return self.value

    class SMem(object):
        ''' Mocking class for memory '''
        def __init__(self, array, init):
            self.code = {}
            self.mem = array
            for addr, val in init.items():
                self.mem[addr] = val
        def setcode(self, addr, c):
            assert isinstance(addr,(int,long))
            assert isinstance(c,str) and len(c) == 1
            self.code[addr] = c

        def getchar(self, addr):
            if isinstance(addr, (int,long)) and addr in self.code.keys():
                return self.code[addr]
            if isinstance(addr, (int,long)) and addr == max(self.code.keys())+1:
                raise Exception("no more code!")
            return self.mem[addr]
        def putchar(self, addr, char):
            self.mem[addr]=char
        def isExecutable(self, addr):
            return True




    def test_ADD_1(self):
        ''' 0x4001a5:	add	rax, 0x18 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'text': 'H\x83\xc0\x18', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'disassembly': u'0x4001a5:\tadd\trax, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_10(self):
        ''' 0x40025b:	add	rsp, 0x10 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194907L, 'RBP': 0L}, 'memory': {4194907L: 'H', 4194908L: '\x83', 4194909L: '\xc4', 4194910L: '\x10'}}, 'text': 'H\x83\xc4\x10', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194911L, 'RBP': 0L}, 'memory': {4194907L: 'H', 4194908L: '\x83', 4194909L: '\xc4', 4194910L: '\x10'}}, 'disassembly': u'0x40025b:\tadd\trsp, 0x10', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_11(self):
        ''' 0x400213:	add	rsp, 0x10 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194835L, 'RBP': 0L}, 'memory': {4194835L: 'H', 4194836L: '\x83', 4194837L: '\xc4', 4194838L: '\x10'}}, 'text': 'H\x83\xc4\x10', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194839L, 'RBP': 0L}, 'memory': {4194835L: 'H', 4194836L: '\x83', 4194837L: '\xc4', 4194838L: '\x10'}}, 'disassembly': u'0x400213:\tadd\trsp, 0x10', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_12(self):
        ''' 0x400199:	add	rax, 0x14 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'text': 'H\x83\xc0\x14', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'disassembly': u'0x400199:\tadd\trax, 0x14', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_13(self):
        ''' 0x400217:	add	rsp, 0x18 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194839L, 'RBP': 0L}, 'memory': {4194840L: '\x83', 4194841L: '\xc4', 4194842L: '\x18', 4194839L: 'H'}}, 'text': 'H\x83\xc4\x18', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194843L, 'RBP': 0L}, 'memory': {4194840L: '\x83', 4194841L: '\xc4', 4194842L: '\x18', 4194839L: 'H'}}, 'disassembly': u'0x400217:\tadd\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_14(self):
        ''' 0x4001c9:	add	rsp, 0x60 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194761L, 'RBP': 4L}, 'memory': {4194761L: 'H', 4194762L: '\x83', 4194763L: '\xc4', 4194764L: '`'}}, 'text': 'H\x83\xc4`', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194765L, 'RBP': 4L}, 'memory': {4194761L: 'H', 4194762L: '\x83', 4194763L: '\xc4', 4194764L: '`'}}, 'disassembly': u'0x4001c9:\tadd\trsp, 0x60', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_15(self):
        ''' 0x4001c9:	add	rsp, 0x60 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194761L, 'RBP': 3L}, 'memory': {4194761L: 'H', 4194762L: '\x83', 4194763L: '\xc4', 4194764L: '`'}}, 'text': 'H\x83\xc4`', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194765L, 'RBP': 3L}, 'memory': {4194761L: 'H', 4194762L: '\x83', 4194763L: '\xc4', 4194764L: '`'}}, 'disassembly': u'0x4001c9:\tadd\trsp, 0x60', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_16(self):
        ''' 0x4001a5:	add	rax, 0x18 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'text': 'H\x83\xc0\x18', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'disassembly': u'0x4001a5:\tadd\trax, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_17(self):
        ''' 0x400181:	add	rax, 0xc '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'text': 'H\x83\xc0\x0c', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194693L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'disassembly': u'0x400181:\tadd\trax, 0xc', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_18(self):
        ''' 0x40018d:	add	rax, 0x10 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'text': 'H\x83\xc0\x10', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'disassembly': u'0x40018d:\tadd\trax, 0x10', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_19(self):
        ''' 0x400169:	add	rax, 4 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'text': 'H\x83\xc0\x04', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'disassembly': u'0x400169:\tadd\trax, 4', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_2(self):
        ''' 0x40018d:	add	rax, 0x10 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'text': 'H\x83\xc0\x10', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'disassembly': u'0x40018d:\tadd\trax, 0x10', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_20(self):
        ''' 0x400175:	add	rax, 8 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'text': 'H\x83\xc0\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'disassembly': u'0x400175:\tadd\trax, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_21(self):
        ''' 0x400169:	add	rax, 4 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'text': 'H\x83\xc0\x04', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'disassembly': u'0x400169:\tadd\trax, 4', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_22(self):
        ''' 0x40025f:	add	rsp, 0x18 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194911L, 'RBP': 0L}, 'memory': {4194912L: '\x83', 4194913L: '\xc4', 4194914L: '\x18', 4194911L: 'H'}}, 'text': 'H\x83\xc4\x18', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194915L, 'RBP': 0L}, 'memory': {4194912L: '\x83', 4194913L: '\xc4', 4194914L: '\x18', 4194911L: 'H'}}, 'disassembly': u'0x40025f:\tadd\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_23(self):
        ''' 0x400199:	add	rax, 0x14 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'text': 'H\x83\xc0\x14', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'disassembly': u'0x400199:\tadd\trax, 0x14', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_24(self):
        ''' 0x400175:	add	rax, 8 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'text': 'H\x83\xc0\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'disassembly': u'0x400175:\tadd\trax, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_3(self):
        ''' 0x4001a5:	add	rax, 0x18 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'text': 'H\x83\xc0\x18', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194728L: '\x18', 4194725L: 'H', 4194726L: '\x83', 4194727L: '\xc0'}}, 'disassembly': u'0x4001a5:\tadd\trax, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_4(self):
        ''' 0x400175:	add	rax, 8 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'text': 'H\x83\xc0\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194680L: '\x08', 4194677L: 'H', 4194678L: '\x83', 4194679L: '\xc0'}}, 'disassembly': u'0x400175:\tadd\trax, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_5(self):
        ''' 0x400181:	add	rax, 0xc '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'text': 'H\x83\xc0\x0c', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194693L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'disassembly': u'0x400181:\tadd\trax, 0xc', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_6(self):
        ''' 0x400169:	add	rax, 4 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'text': 'H\x83\xc0\x04', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194665L: 'H', 4194666L: '\x83', 4194667L: '\xc0', 4194668L: '\x04'}}, 'disassembly': u'0x400169:\tadd\trax, 4', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_7(self):
        ''' 0x40018d:	add	rax, 0x10 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'text': 'H\x83\xc0\x10', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {4194704L: '\x10', 4194701L: 'H', 4194702L: '\x83', 4194703L: '\xc0'}}, 'disassembly': u'0x40018d:\tadd\trax, 0x10', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_8(self):
        ''' 0x400181:	add	rax, 0xc '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'text': 'H\x83\xc0\x0c', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194693L, 'RBP': 0L}, 'memory': {4194689L: 'H', 4194690L: '\x83', 4194691L: '\xc0', 4194692L: '\x0c'}}, 'disassembly': u'0x400181:\tadd\trax, 0xc', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_ADD_9(self):
        ''' 0x400199:	add	rax, 0x14 '''
        test = {'mnemonic': u'ADD', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'text': 'H\x83\xc0\x14', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {4194713L: 'H', 4194714L: '\x83', 4194715L: '\xc0', 4194716L: '\x14'}}, 'disassembly': u'0x400199:\tadd\trax, 0x14', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_1(self):
        ''' 0x400298:	call	0x40010c '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194968L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194968L: '\xe8', 4194969L: 'o', 4194970L: '\xfe', 4194971L: '\xff', 4194972L: '\xff', 140737488346751L: '\x00'}}, 'text': '\xe8o\xfe\xff\xff', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '\x9d', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194968L: '\xe8', 4194969L: 'o', 4194970L: '\xfe', 4194971L: '\xff', 4194972L: '\xff', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x400298:\tcall\t0x40010c', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_2(self):
        ''' 0x40020e:	call	0x40010c '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194830L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194833L: '\xff', 4194834L: '\xff', 4194830L: '\xe8', 4194831L: '\xf9', 4194832L: '\xfe', 140737488346751L: '\x00'}}, 'text': '\xe8\xf9\xfe\xff\xff', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 4195120L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194833L: '\xff', 4194834L: '\xff', 4194830L: '\xe8', 4194831L: '\xf9', 4194832L: '\xfe', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40020e:\tcall\t0x40010c', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_3(self):
        ''' 0x4002bc:	call	0x40021c '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4195004L, 'RBP': 0L}, 'memory': {140737488346816L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\x00', 140737488346801L: '\x00', 140737488346802L: '\x00', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 4195007L: '\xff', 4195008L: '\xff', 4195004L: '\xe8', 4195005L: '[', 4195006L: '\xff', 140737488346815L: '\x00'}}, 'text': '\xe8[\xff\xff\xff', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346800L, 'RDX': 1L, 'RIP': 4194844L, 'RBP': 0L}, 'memory': {140737488346816L: '\x00', 140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xc1', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 4195008L: '\xff', 4195004L: '\xe8', 4195005L: '[', 4195006L: '\xff', 4195007L: '\xff'}}, 'disassembly': u'0x4002bc:\tcall\t0x40021c', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_4(self):
        ''' 0x400256:	call	0x40010c '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194902L, 'RBP': 0L}, 'memory': {140737488346752L: '\x00', 140737488346753L: '\x00', 140737488346754L: '\x00', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194902L: '\xe8', 4194903L: '\xb1', 4194904L: '\xfe', 4194905L: '\xff', 4194906L: '\xff', 140737488346751L: '\x00'}}, 'text': '\xe8\xb1\xfe\xff\xff', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 140737488346823L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194902L: '\xe8', 4194903L: '\xb1', 4194904L: '\xfe', 4194905L: '\xff', 4194906L: '\xff', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x400256:\tcall\t0x40010c', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_5(self):
        ''' 0x4002ef:	call	0x4001d4 '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195055L, 'RBP': 0L}, 'memory': {140737488346799L: '\x00', 140737488346800L: '\xc1', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00', 4195055L: '\xe8', 4195056L: '\xe0', 4195057L: '\xfe', 4195058L: '\xff', 4195059L: '\xff'}}, 'text': '\xe8\xe0\xfe\xff\xff', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346800L, 'RDX': 42L, 'RIP': 4194772L, 'RBP': 0L}, 'memory': {140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xf4', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00', 4195055L: '\xe8', 4195056L: '\xe0', 4195057L: '\xfe', 4195058L: '\xff', 4195059L: '\xff'}}, 'disassembly': u'0x4002ef:\tcall\t0x4001d4', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_CALL_6(self):
        ''' 0x4002f9:	call	0x400264 '''
        test = {'mnemonic': u'CALL', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195065L, 'RBP': 0L}, 'memory': {140737488346799L: '\x00', 140737488346800L: '\xf4', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00', 4195065L: '\xe8', 4195066L: 'f', 4195067L: '\xff', 4195068L: '\xff', 4195069L: '\xff'}}, 'text': '\xe8f\xff\xff\xff', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194916L, 'RBP': 0L}, 'memory': {140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xfe', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00', 4195065L: '\xe8', 4195066L: 'f', 4195067L: '\xff', 4195068L: '\xff', 4195069L: '\xff'}}, 'disassembly': u'0x4002f9:\tcall\t0x400264', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_JE_1(self):
        ''' 0x400135:	je	0x40015f '''
        test = {'mnemonic': u'JE', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194613L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'text': 't(', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'disassembly': u'0x400135:\tje\t0x40015f', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_JE_2(self):
        ''' 0x400135:	je	0x40015f '''
        test = {'mnemonic': u'JE', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194613L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'text': 't(', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'disassembly': u'0x400135:\tje\t0x40015f', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_JE_3(self):
        ''' 0x400135:	je	0x40015f '''
        test = {'mnemonic': u'JE', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194613L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'text': 't(', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194613L: 't', 4194614L: '('}}, 'disassembly': u'0x400135:\tje\t0x40015f', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_JNS_1(self):
        ''' 0x4002c8:	jns	0x4002e0 '''
        test = {'mnemonic': u'JNS', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195016L, 'RBP': 0L}, 'memory': {4195016L: 'y', 4195017L: '\x16'}}, 'text': 'y\x16', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195040L, 'RBP': 0L}, 'memory': {4195016L: 'y', 4195017L: '\x16'}}, 'disassembly': u'0x4002c8:\tjns\t0x4002e0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_1(self):
        ''' 0x4001a0:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'disassembly': u'0x4001a0:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_10(self):
        ''' 0x400164:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'disassembly': u'0x400164:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_11(self):
        ''' 0x400170:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'disassembly': u'0x400170:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_12(self):
        ''' 0x4001a0:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'disassembly': u'0x4001a0:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_13(self):
        ''' 0x400164:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'disassembly': u'0x400164:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_14(self):
        ''' 0x400188:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194696L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x400188:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_15(self):
        ''' 0x400194:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 4194708L: 'H', 140737488346517L: '\x00', 4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x03', 4194709L: '\x8d'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 4194708L: 'H', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x03', 4194709L: '\x8d'}}, 'disassembly': u'0x400194:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_16(self):
        ''' 0x400170:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'disassembly': u'0x400170:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_17(self):
        ''' 0x400188:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194696L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x400188:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_18(self):
        ''' 0x400194:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 4194708L: 'H', 140737488346517L: '\x00', 4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x04', 4194709L: '\x8d'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 4194708L: 'H', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x04', 4194709L: '\x8d'}}, 'disassembly': u'0x400194:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_19(self):
        ''' 0x4001a0:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194725L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194720L: 'H', 4194721L: '\x8d', 4194722L: 'D', 4194723L: '$', 4194724L: '\x94'}}, 'disassembly': u'0x4001a0:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_2(self):
        ''' 0x400164:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194665L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194660L: 'H', 4194661L: '\x8d', 4194662L: 'D', 4194663L: '$', 4194664L: '\x94'}}, 'disassembly': u'0x400164:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_3(self):
        ''' 0x400194:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346532L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 4194708L: 'H', 140737488346517L: '\x00', 4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x01', 4194709L: '\x8d'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194713L, 'RBP': 0L}, 'memory': {4194710L: 'D', 4194711L: '$', 140737488346520L: '\x00', 4194708L: 'H', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194712L: '\x94', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 140737488346516L: '\x01', 4194709L: '\x8d'}}, 'disassembly': u'0x400194:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_4(self):
        ''' 0x40017c:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'disassembly': u'0x40017c:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_5(self):
        ''' 0x40017c:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'disassembly': u'0x40017c:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_6(self):
        ''' 0x40017c:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346524L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194689L, 'RBP': 0L}, 'memory': {4194688L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194684L: 'H', 4194685L: '\x8d', 4194686L: 'D', 4194687L: '$'}}, 'disassembly': u'0x40017c:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_7(self):
        ''' 0x4002aa:	lea	rax, qword ptr [rsp + 0xf] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4194986L, 'RBP': 0L}, 'memory': {140737488346823L: '\x00', 140737488346824L: '\x00', 140737488346825L: '\x00', 140737488346826L: '\x00', 140737488346827L: '\x00', 140737488346828L: '\x00', 140737488346829L: '\x00', 140737488346830L: '\x00', 4194986L: 'H', 4194987L: '\x8d', 4194988L: 'D', 4194989L: '$', 4194990L: '\x0f'}}, 'text': 'H\x8dD$\x0f', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4194991L, 'RBP': 0L}, 'memory': {140737488346823L: '\x00', 140737488346824L: '\x00', 140737488346825L: '\x00', 140737488346826L: '\x00', 140737488346827L: '\x00', 140737488346828L: '\x00', 140737488346829L: '\x00', 140737488346830L: '\x00', 4194986L: 'H', 4194987L: '\x8d', 4194988L: 'D', 4194989L: '$', 4194990L: '\x0f'}}, 'disassembly': u'0x4002aa:\tlea\trax, qword ptr [rsp + 0xf]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_8(self):
        ''' 0x400170:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194677L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00', 4194672L: 'H', 4194673L: '\x8d', 4194674L: 'D', 4194675L: '$', 4194676L: '\x94'}}, 'disassembly': u'0x400170:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_LEA_9(self):
        ''' 0x400188:	lea	rax, qword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'LEA', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194696L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'H\x8dD$\x94', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346516L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194701L, 'RBP': 0L}, 'memory': {4194696L: 'H', 4194697L: '\x8d', 4194698L: 'D', 4194699L: '$', 4194700L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x400188:\tlea\trax, qword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOVZX_1(self):
        ''' 0x4002c1:	movzx	eax, byte ptr [rsp + 0xf] '''
        test = {'mnemonic': u'MOVZX', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195009L, 'RBP': 0L}, 'memory': {4195009L: '\x0f', 4195010L: '\xb6', 4195011L: 'D', 4195012L: '$', 4195013L: '\x0f', 140737488346823L: '\x00'}}, 'text': '\x0f\xb6D$\x0f', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195014L, 'RBP': 0L}, 'memory': {4195009L: '\x0f', 4195010L: '\xb6', 4195011L: 'D', 4195012L: '$', 4195013L: '\x0f', 140737488346823L: '\x00'}}, 'disassembly': u'0x4002c1:\tmovzx\teax, byte ptr [rsp + 0xf]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_1(self):
        ''' 0x400234:	mov	eax, dword ptr [rsp + 0xc] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294958791L, 'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 140737488346823L, 'RIP': 4194868L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194868L: '\x8b', 4194870L: '$', 4194871L: '\x0c', 4194869L: 'D'}}, 'text': '\x8bD$\x0c', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 140737488346823L, 'RIP': 4194872L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194868L: '\x8b', 4194870L: '$', 4194871L: '\x0c', 4194869L: 'D'}}, 'disassembly': u'0x400234:\tmov\teax, dword ptr [rsp + 0xc]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_10(self):
        ''' 0x4001d8:	mov	dword ptr [rsp + 0xc], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194776L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194776L: '\x89', 4194777L: '|', 4194778L: '$', 4194779L: '\x0c'}}, 'text': '\x89|$\x0c', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194780L, 'RBP': 0L}, 'memory': {140737488346788L: '\x01', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194776L: '\x89', 4194777L: '|', 4194778L: '$', 4194779L: '\x0c'}}, 'disassembly': u'0x4001d8:\tmov\tdword ptr [rsp + 0xc], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_100(self):
        ''' 0x40011f:	mov	qword ptr [rsp - 0x48], rdx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '\x00', 140737488346553L: '\x00', 140737488346554L: '\x00', 140737488346555L: '\x00', 140737488346556L: '\x00', 140737488346557L: '\x00', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'text': 'H\x89T$\xb8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '\xc7', 140737488346553L: '\xde', 140737488346554L: '\xff', 140737488346555L: '\xff', 140737488346556L: '\xff', 140737488346557L: '\x7f', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'disassembly': u'0x40011f:\tmov\tqword ptr [rsp - 0x48], rdx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_101(self):
        ''' 0x4001a9:	mov	eax, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294958508L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'text': '\x8b\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194731L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'disassembly': u'0x4001a9:\tmov\teax, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_11(self):
        ''' 0x400244:	mov	r8d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194884L, 'RBP': 0L}, 'memory': {4194884L: 'A', 4194885L: '\xb8', 4194886L: '\x00', 4194887L: '\x00', 4194888L: '\x00', 4194889L: '\x00'}}, 'text': 'A\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194890L, 'RBP': 0L}, 'memory': {4194884L: 'A', 4194885L: '\xb8', 4194886L: '\x00', 4194887L: '\x00', 4194888L: '\x00', 4194889L: '\x00'}}, 'disassembly': u'0x400244:\tmov\tr8d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_12(self):
        ''' 0x4001fc:	mov	r8d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194812L, 'RBP': 0L}, 'memory': {4194816L: '\x00', 4194817L: '\x00', 4194812L: 'A', 4194813L: '\xb8', 4194814L: '\x00', 4194815L: '\x00'}}, 'text': 'A\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194818L, 'RBP': 0L}, 'memory': {4194816L: '\x00', 4194817L: '\x00', 4194812L: 'A', 4194813L: '\xb8', 4194814L: '\x00', 4194815L: '\x00'}}, 'disassembly': u'0x4001fc:\tmov\tr8d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_13(self):
        ''' 0x4001ba:	mov	esi, r13d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194746L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'text': 'D\x89\xee', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194749L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'disassembly': u'0x4001ba:\tmov\tesi, r13d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_14(self):
        ''' 0x40028e:	mov	edi, 1 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194958L, 'RBP': 0L}, 'memory': {4194960L: '\x00', 4194961L: '\x00', 4194962L: '\x00', 4194958L: '\xbf', 4194959L: '\x01'}}, 'text': '\xbf\x01\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194963L, 'RBP': 0L}, 'memory': {4194960L: '\x00', 4194961L: '\x00', 4194962L: '\x00', 4194958L: '\xbf', 4194959L: '\x01'}}, 'disassembly': u'0x40028e:\tmov\tedi, 1', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_15(self):
        ''' 0x4001ec:	mov	eax, dword ptr [rsp + 0xc] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 4195120L, 'RIP': 4194796L, 'RBP': 0L}, 'memory': {140737488346788L: '\x01', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194796L: '\x8b', 4194797L: 'D', 4194798L: '$', 4194799L: '\x0c'}}, 'text': '\x8bD$\x0c', 'pos': {'registers': {u'EAX': 1L, 'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346776L, 'RDX': 4195120L, 'RIP': 4194800L, 'RBP': 0L}, 'memory': {140737488346788L: '\x01', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194796L: '\x8b', 4194797L: 'D', 4194798L: '$', 4194799L: '\x0c'}}, 'disassembly': u'0x4001ec:\tmov\teax, dword ptr [rsp + 0xc]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_16(self):
        ''' 0x40024a:	mov	esi, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 0L, u'ESI': 4294958791L, 'RSI': 140737488346823L, 'RIP': 4194890L, u'EAX': 0L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194890L: '\x89', 4194891L: '\xc6'}}, 'text': '\x89\xc6', 'pos': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194892L, u'EAX': 0L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194890L: '\x89', 4194891L: '\xc6'}}, 'disassembly': u'0x40024a:\tmov\tesi, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_17(self):
        ''' 0x40015f:	mov	r8d, dword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'text': 'D\x8bD$\x94', 'pos': {'registers': {u'R8D': 4L, 'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'disassembly': u'0x40015f:\tmov\tr8d, dword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_18(self):
        ''' 0x4001b4:	mov	edx, r11d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, u'R11D': 0L, 'RIP': 4194740L, u'EDX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'text': 'D\x89\xda', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, u'R11D': 0L, 'RIP': 4194743L, u'EDX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'disassembly': u'0x4001b4:\tmov\tedx, r11d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_19(self):
        ''' 0x40012e:	mov	qword ptr [rsp - 0x30], r9 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194606L, 'RDX': 4195120L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'text': 'L\x89L$\xd0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194611L, 'RDX': 4195120L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'disassembly': u'0x40012e:\tmov\tqword ptr [rsp - 0x30], r9', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_2(self):
        ''' 0x40015f:	mov	r8d, dword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'text': 'D\x8bD$\x94', 'pos': {'registers': {u'R8D': 1L, 'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x01', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'disassembly': u'0x40015f:\tmov\tr8d, dword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_20(self):
        ''' 0x4001b7:	mov	edi, r12d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, u'EDI': 1L, 'RIP': 4194743L, u'R12D': 4294967287L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'text': 'D\x89\xe7', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4294967287L, 'RSI': 0L, u'EDI': 4294967287L, 'RIP': 4194746L, u'R12D': 4294967287L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'disassembly': u'0x4001b7:\tmov\tedi, r12d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_21(self):
        ''' 0x40026c:	mov	eax, dword ptr [rsp + 0xc] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294967287L, 'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194924L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194924L: '\x8b', 4194925L: 'D', 4194926L: '$', 4194927L: '\x0c'}}, 'text': '\x8bD$\x0c', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194928L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194924L: '\x8b', 4194925L: 'D', 4194926L: '$', 4194927L: '\x0c'}}, 'disassembly': u'0x40026c:\tmov\teax, dword ptr [rsp + 0xc]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_22(self):
        ''' 0x4001a9:	mov	eax, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294958508L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'text': '\x8b\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194731L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'disassembly': u'0x4001a9:\tmov\teax, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_23(self):
        ''' 0x4001ba:	mov	esi, r13d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 1L, 'RSI': 1L, 'RIP': 4194746L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'text': 'D\x89\xee', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194749L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'disassembly': u'0x4001ba:\tmov\tesi, r13d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_24(self):
        ''' 0x40016d:	mov	r9d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'D\x8b\x08', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x40016d:\tmov\tr9d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_25(self):
        ''' 0x400293:	mov	eax, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194963L, 'RBP': 0L}, 'memory': {4194963L: '\xb8', 4194964L: '\x00', 4194965L: '\x00', 4194966L: '\x00', 4194967L: '\x00'}}, 'text': '\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194968L, 'RBP': 0L}, 'memory': {4194963L: '\xb8', 4194964L: '\x00', 4194965L: '\x00', 4194966L: '\x00', 4194967L: '\x00'}}, 'disassembly': u'0x400293:\tmov\teax, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_26(self):
        ''' 0x4001bd:	mov	ebp, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4294967287L, 'RSI': 0L, 'RIP': 4194749L, u'EAX': 1L, u'EBP': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'text': '\x89\xc5', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 1L, 'RDI': 4294967287L, 'RSI': 0L, 'RIP': 4194751L, u'EAX': 1L, u'EBP': 1L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'disassembly': u'0x4001bd:\tmov\tebp, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_27(self):
        ''' 0x40011a:	mov	qword ptr [rsp - 0x50], rsi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x00', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'text': 'H\x89t$\xb0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x00', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'disassembly': u'0x40011a:\tmov\tqword ptr [rsp - 0x50], rsi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_28(self):
        ''' 0x400228:	mov	dword ptr [rsp + 8], edx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, u'EDX': 1L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194856L, 'RBP': 0L}, 'memory': {140737488346784L: '\x00', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194856L: '\x89', 4194857L: 'T', 4194858L: '$', 4194859L: '\x08'}}, 'text': '\x89T$\x08', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, u'EDX': 1L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194860L, 'RBP': 0L}, 'memory': {140737488346784L: '\x01', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194856L: '\x89', 4194857L: 'T', 4194858L: '$', 4194859L: '\x08'}}, 'disassembly': u'0x400228:\tmov\tdword ptr [rsp + 8], edx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_29(self):
        ''' 0x40012e:	mov	qword ptr [rsp - 0x30], r9 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194606L, 'RDX': 140737488346823L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'text': 'L\x89L$\xd0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194611L, 'RDX': 140737488346823L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'disassembly': u'0x40012e:\tmov\tqword ptr [rsp - 0x30], r9', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_3(self):
        ''' 0x40022c:	mov	ecx, dword ptr [rsp + 8] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, u'ECX': 0L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194860L, 'RBP': 0L}, 'memory': {140737488346784L: '\x01', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194860L: '\x8b', 4194861L: 'L', 4194862L: '$', 4194863L: '\x08'}}, 'text': '\x8bL$\x08', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, u'ECX': 1L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194864L, 'RBP': 0L}, 'memory': {140737488346784L: '\x01', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194860L: '\x8b', 4194861L: 'L', 4194862L: '$', 4194863L: '\x08'}}, 'disassembly': u'0x40022c:\tmov\tecx, dword ptr [rsp + 8]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_30(self):
        ''' 0x40015f:	mov	r8d, dword ptr [rsp - 0x6c] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194655L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'text': 'D\x8bD$\x94', 'pos': {'registers': {u'R8D': 3L, 'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194660L, 'RBP': 0L}, 'memory': {4194656L: '\x8b', 4194657L: 'D', 4194658L: '$', 4194659L: '\x94', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194655L: 'D'}}, 'disassembly': u'0x40015f:\tmov\tr8d, dword ptr [rsp - 0x6c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_31(self):
        ''' 0x4001ab:	mov	eax, r8d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, u'R8D': 4L, 'RIP': 4194731L, u'EAX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'text': 'D\x89\xc0', 'pos': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, u'R8D': 4L, 'RIP': 4194734L, u'EAX': 4L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'disassembly': u'0x4001ab:\tmov\teax, r8d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_32(self):
        ''' 0x4002f4:	mov	edi, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RAX': 4294967287L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195060L, 'RBP': 0L}, 'memory': {4195064L: '\x00', 4195060L: '\xbf', 4195061L: '\x00', 4195062L: '\x00', 4195063L: '\x00'}}, 'text': '\xbf\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RAX': 4294967287L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195065L, 'RBP': 0L}, 'memory': {4195064L: '\x00', 4195060L: '\xbf', 4195061L: '\x00', 4195062L: '\x00', 4195063L: '\x00'}}, 'disassembly': u'0x4002f4:\tmov\tedi, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_33(self):
        ''' 0x4001b1:	mov	ecx, r10d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, 'RIP': 4194737L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L, u'ECX': 0L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'text': 'D\x89\xd1', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, 'RIP': 4194740L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L, u'ECX': 0L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'disassembly': u'0x4001b1:\tmov\tecx, r10d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_34(self):
        ''' 0x4001ae:	mov	ebx, r9d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194734L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'text': 'D\x89\xcb', 'pos': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194737L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'disassembly': u'0x4001ae:\tmov\tebx, r9d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_35(self):
        ''' 0x400129:	mov	qword ptr [rsp - 0x38], r8 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'text': 'L\x89D$\xc8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194606L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'disassembly': u'0x400129:\tmov\tqword ptr [rsp - 0x38], r8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_36(self):
        ''' 0x4001ae:	mov	ebx, r9d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194734L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'text': 'D\x89\xcb', 'pos': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194737L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'disassembly': u'0x4001ae:\tmov\tebx, r9d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_37(self):
        ''' 0x4001a9:	mov	eax, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294958508L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346540L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194729L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'text': '\x8b\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194731L, 'RBP': 0L}, 'memory': {4194729L: '\x8b', 4194730L: '\x00', 140737488346540L: '\x00', 140737488346541L: '\x00', 140737488346542L: '\x00', 140737488346543L: '\x00'}}, 'disassembly': u'0x4001a9:\tmov\teax, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_38(self):
        ''' 0x40012e:	mov	qword ptr [rsp - 0x30], r9 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194606L, 'RDX': 0L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'text': 'L\x89L$\xd0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, 'RBP': 0L, 'RSP': 140737488346624L, u'R9': 0L, 'RIP': 4194611L, 'RDX': 0L}, 'memory': {140737488346576L: '\x00', 140737488346577L: '\x00', 140737488346578L: '\x00', 140737488346579L: '\x00', 140737488346580L: '\x00', 140737488346581L: '\x00', 140737488346582L: '\x00', 140737488346583L: '\x00', 4194606L: 'L', 4194607L: '\x89', 4194608L: 'L', 4194609L: '$', 4194610L: '\xd0'}}, 'disassembly': u'0x40012e:\tmov\tqword ptr [rsp - 0x30], r9', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_39(self):
        ''' 0x40011a:	mov	qword ptr [rsp - 0x50], rsi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x00', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'text': 'H\x89t$\xb0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x01', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'disassembly': u'0x40011a:\tmov\tqword ptr [rsp - 0x50], rsi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_4(self):
        ''' 0x400224:	mov	qword ptr [rsp], rsi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194852L, 'RBP': 0L}, 'memory': {140737488346776L: '\x00', 140737488346777L: '\x00', 140737488346778L: '\x00', 140737488346779L: '\x00', 140737488346780L: '\x00', 140737488346781L: '\x00', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194852L: 'H', 4194853L: '\x89', 4194854L: '4', 4194855L: '$'}}, 'text': 'H\x894$', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194856L, 'RBP': 0L}, 'memory': {140737488346776L: '\xc7', 140737488346777L: '\xde', 140737488346778L: '\xff', 140737488346779L: '\xff', 140737488346780L: '\xff', 140737488346781L: '\x7f', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194852L: 'H', 4194853L: '\x89', 4194854L: '4', 4194855L: '$'}}, 'disassembly': u'0x400224:\tmov\tqword ptr [rsp], rsi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_40(self):
        ''' 0x400287:	mov	edx, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194951L, 'RBP': 0L}, 'memory': {4194952L: '\x00', 4194953L: '\x00', 4194954L: '\x00', 4194955L: '\x00', 4194951L: '\xba'}}, 'text': '\xba\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194956L, 'RBP': 0L}, 'memory': {4194952L: '\x00', 4194953L: '\x00', 4194954L: '\x00', 4194955L: '\x00', 4194951L: '\xba'}}, 'disassembly': u'0x400287:\tmov\tedx, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_41(self):
        ''' 0x400209:	mov	eax, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 1L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194825L, 'RBP': 0L}, 'memory': {4194825L: '\xb8', 4194826L: '\x00', 4194827L: '\x00', 4194828L: '\x00', 4194829L: '\x00'}}, 'text': '\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194830L, 'RBP': 0L}, 'memory': {4194825L: '\xb8', 4194826L: '\x00', 4194827L: '\x00', 4194828L: '\x00', 4194829L: '\x00'}}, 'disassembly': u'0x400209:\tmov\teax, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_42(self):
        ''' 0x40016d:	mov	r9d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'D\x8b\x08', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x40016d:\tmov\tr9d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_43(self):
        ''' 0x4001e0:	mov	dword ptr [rsp + 8], edx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, u'EDX': 42L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194784L, 'RBP': 0L}, 'memory': {140737488346784L: '\x01', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194784L: '\x89', 4194785L: 'T', 4194786L: '$', 4194787L: '\x08'}}, 'text': '\x89T$\x08', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, u'EDX': 42L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194788L, 'RBP': 0L}, 'memory': {140737488346784L: '*', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194784L: '\x89', 4194785L: 'T', 4194786L: '$', 4194787L: '\x08'}}, 'disassembly': u'0x4001e0:\tmov\tdword ptr [rsp + 8], edx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_44(self):
        ''' 0x4001c5:	mov	eax, dword ptr [rsp - 0x5c] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194757L, 'RBP': 3L}, 'memory': {140737488346532L: '\x00', 4194757L: '\x8b', 4194758L: 'D', 140737488346534L: '\x00', 4194760L: '\xa4', 140737488346533L: '\x00', 140737488346535L: '\x00', 4194759L: '$'}}, 'text': '\x8bD$\xa4', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194761L, 'RBP': 3L}, 'memory': {140737488346532L: '\x00', 4194757L: '\x8b', 4194758L: 'D', 140737488346534L: '\x00', 4194760L: '\xa4', 140737488346535L: '\x00', 4194759L: '$', 140737488346533L: '\x00'}}, 'disassembly': u'0x4001c5:\tmov\teax, dword ptr [rsp - 0x5c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_45(self):
        ''' 0x40027c:	mov	r8d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194940L, 'RBP': 0L}, 'memory': {4194944L: '\x00', 4194945L: '\x00', 4194940L: 'A', 4194941L: '\xb8', 4194942L: '\x00', 4194943L: '\x00'}}, 'text': 'A\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'R8D': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194946L, 'RBP': 0L}, 'memory': {4194944L: '\x00', 4194945L: '\x00', 4194940L: 'A', 4194941L: '\xb8', 4194942L: '\x00', 4194943L: '\x00'}}, 'disassembly': u'0x40027c:\tmov\tr8d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_46(self):
        ''' 0x400220:	mov	dword ptr [rsp + 0xc], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RAX': 140737488346823L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194848L, 'RBP': 0L}, 'memory': {4194848L: '\x89', 4194849L: '|', 4194850L: '$', 4194851L: '\x0c', 140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00'}}, 'text': '\x89|$\x0c', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RAX': 140737488346823L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194852L, 'RBP': 0L}, 'memory': {4194848L: '\x89', 4194849L: '|', 4194850L: '$', 4194851L: '\x0c', 140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00'}}, 'disassembly': u'0x400220:\tmov\tdword ptr [rsp + 0xc], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_47(self):
        ''' 0x40011f:	mov	qword ptr [rsp - 0x48], rdx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '0', 140737488346553L: '\x03', 140737488346554L: '@', 140737488346555L: '\x00', 140737488346556L: '\x00', 140737488346557L: '\x00', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'text': 'H\x89T$\xb8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '\x00', 140737488346553L: '\x00', 140737488346554L: '\x00', 140737488346555L: '\x00', 140737488346556L: '\x00', 140737488346557L: '\x00', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'disassembly': u'0x40011f:\tmov\tqword ptr [rsp - 0x48], rdx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_48(self):
        ''' 0x4001e8:	mov	rdx, qword ptr [rsp] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194792L, 'RBP': 0L}, 'memory': {140737488346776L: '0', 140737488346777L: '\x03', 140737488346778L: '@', 140737488346779L: '\x00', 140737488346780L: '\x00', 140737488346781L: '\x00', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194792L: 'H', 4194793L: '\x8b', 4194794L: '\x14', 4194795L: '$'}}, 'text': 'H\x8b\x14$', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 4195120L, 'RIP': 4194796L, 'RBP': 0L}, 'memory': {140737488346776L: '0', 140737488346777L: '\x03', 140737488346778L: '@', 140737488346779L: '\x00', 140737488346780L: '\x00', 140737488346781L: '\x00', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194792L: 'H', 4194793L: '\x8b', 4194794L: '\x14', 4194795L: '$'}}, 'disassembly': u'0x4001e8:\tmov\trdx, qword ptr [rsp]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_49(self):
        ''' 0x400116:	mov	dword ptr [rsp - 0x6c], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194582L: '\x89', 140737488346516L: '\x04', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194584L: '$', 4194585L: '\x94', 4194583L: '|'}}, 'text': '\x89|$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {140737488346516L: '\x01', 140737488346517L: '\x00', 4194582L: '\x89', 4194583L: '|', 4194584L: '$', 4194585L: '\x94', 140737488346519L: '\x00', 140737488346518L: '\x00'}}, 'disassembly': u'0x400116:\tmov\tdword ptr [rsp - 0x6c], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_5(self):
        ''' 0x4001b1:	mov	ecx, r10d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, 'RIP': 4194737L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L, u'ECX': 42L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'text': 'D\x89\xd1', 'pos': {'registers': {'RCX': 0L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, 'RIP': 4194740L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L, u'ECX': 0L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'disassembly': u'0x4001b1:\tmov\tecx, r10d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_50(self):
        ''' 0x400230:	mov	rdx, qword ptr [rsp] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194864L, 'RBP': 0L}, 'memory': {140737488346776L: '\xc7', 140737488346777L: '\xde', 140737488346778L: '\xff', 140737488346779L: '\xff', 140737488346780L: '\xff', 140737488346781L: '\x7f', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194864L: 'H', 4194865L: '\x8b', 4194866L: '\x14', 4194867L: '$'}}, 'text': 'H\x8b\x14$', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 140737488346823L, 'RIP': 4194868L, 'RBP': 0L}, 'memory': {140737488346776L: '\xc7', 140737488346777L: '\xde', 140737488346778L: '\xff', 140737488346779L: '\xff', 140737488346780L: '\xff', 140737488346781L: '\x7f', 140737488346782L: '\x00', 140737488346783L: '\x00', 4194864L: 'H', 4194865L: '\x8b', 4194866L: '\x14', 4194867L: '$'}}, 'disassembly': u'0x400230:\tmov\trdx, qword ptr [rsp]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_51(self):
        ''' 0x40024c:	mov	edi, 3 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194892L, 'RBP': 0L}, 'memory': {4194896L: '\x00', 4194892L: '\xbf', 4194893L: '\x03', 4194894L: '\x00', 4194895L: '\x00'}}, 'text': '\xbf\x03\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, u'EDI': 3L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194897L, 'RBP': 0L}, 'memory': {4194896L: '\x00', 4194892L: '\xbf', 4194893L: '\x03', 4194894L: '\x00', 4194895L: '\x00'}}, 'disassembly': u'0x40024c:\tmov\tedi, 3', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_52(self):
        ''' 0x4002e0:	mov	edx, 0x2a '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195040L, 'RBP': 0L}, 'memory': {4195040L: '\xba', 4195041L: '*', 4195042L: '\x00', 4195043L: '\x00', 4195044L: '\x00'}}, 'text': '\xba*\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 42L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195045L, 'RBP': 0L}, 'memory': {4195040L: '\xba', 4195041L: '*', 4195042L: '\x00', 4195043L: '\x00', 4195044L: '\x00'}}, 'disassembly': u'0x4002e0:\tmov\tedx, 0x2a', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_53(self):
        ''' 0x400179:	mov	r10d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 140737488346524L, 'RDI': 3L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'text': 'D\x8b\x10', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 140737488346524L, 'RDI': 3L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'disassembly': u'0x400179:\tmov\tr10d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_54(self):
        ''' 0x400191:	mov	r12d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RAX': 140737488346532L, 'RDI': 3L, u'R12D': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'text': 'D\x8b ', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 1L, 'RSI': 0L, 'RAX': 140737488346532L, 'RDI': 3L, u'R12D': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'disassembly': u'0x400191:\tmov\tr12d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_55(self):
        ''' 0x400185:	mov	r11d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R11D': 0L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194693L, 'RBP': 0L}, 'memory': {140737488346528L: '\x00', 140737488346529L: '\x00', 140737488346530L: '\x00', 140737488346531L: '\x00', 4194693L: 'D', 4194694L: '\x8b', 4194695L: '\x18'}}, 'text': 'D\x8b\x18', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R11D': 0L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194696L, 'RBP': 0L}, 'memory': {140737488346528L: '\x00', 140737488346529L: '\x00', 140737488346530L: '\x00', 140737488346531L: '\x00', 4194693L: 'D', 4194694L: '\x8b', 4194695L: '\x18'}}, 'disassembly': u'0x400185:\tmov\tr11d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_56(self):
        ''' 0x4001ba:	mov	esi, r13d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4294967287L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194746L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'text': 'D\x89\xee', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4294967287L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194749L, u'R13D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194746L: 'D', 4194747L: '\x89', 4194748L: '\xee'}}, 'disassembly': u'0x4001ba:\tmov\tesi, r13d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_57(self):
        ''' 0x400124:	mov	qword ptr [rsp - 0x40], rcx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {140737488346560L: '\x01', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'text': 'H\x89L$\xc0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346560L: '*', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'disassembly': u'0x400124:\tmov\tqword ptr [rsp - 0x40], rcx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_58(self):
        ''' 0x40019d:	mov	r13d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'text': 'D\x8b(', 'pos': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'disassembly': u'0x40019d:\tmov\tr13d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_59(self):
        ''' 0x400116:	mov	dword ptr [rsp - 0x6c], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, u'EDI': 3L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194582L: '\x89', 140737488346516L: '\x00', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194584L: '$', 4194585L: '\x94', 4194583L: '|'}}, 'text': '\x89|$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, u'EDI': 3L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {140737488346516L: '\x03', 140737488346517L: '\x00', 4194582L: '\x89', 4194583L: '|', 4194584L: '$', 4194585L: '\x94', 140737488346519L: '\x00', 140737488346518L: '\x00'}}, 'disassembly': u'0x400116:\tmov\tdword ptr [rsp - 0x6c], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_6(self):
        ''' 0x4001b7:	mov	edi, r12d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, u'EDI': 4L, 'RIP': 4194743L, u'R12D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'text': 'D\x89\xe7', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, 'RSI': 1L, u'EDI': 0L, 'RIP': 4194746L, u'R12D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'disassembly': u'0x4001b7:\tmov\tedi, r12d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_60(self):
        ''' 0x4001ae:	mov	ebx, r9d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194734L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'text': 'D\x89\xcb', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, 'RSP': 140737488346624L, u'R9D': 0L, 'RIP': 4194737L, u'EBX': 0L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194736L: '\xcb', 4194734L: 'D', 4194735L: '\x89'}}, 'disassembly': u'0x4001ae:\tmov\tebx, r9d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_61(self):
        ''' 0x400129:	mov	qword ptr [rsp - 0x38], r8 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'text': 'L\x89D$\xc8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194606L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'disassembly': u'0x400129:\tmov\tqword ptr [rsp - 0x38], r8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_62(self):
        ''' 0x4001b7:	mov	edi, r12d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, u'EDI': 3L, 'RIP': 4194743L, u'R12D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'text': 'D\x89\xe7', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, 'RSI': 0L, u'EDI': 0L, 'RIP': 4194746L, u'R12D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194744L: '\x89', 4194745L: '\xe7', 4194743L: 'D'}}, 'disassembly': u'0x4001b7:\tmov\tedi, r12d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_63(self):
        ''' 0x400191:	mov	r12d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RAX': 140737488346532L, 'RDI': 4L, u'R12D': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'text': 'D\x8b ', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 42L, 'RSI': 1L, 'RAX': 140737488346532L, 'RDI': 4L, u'R12D': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'disassembly': u'0x400191:\tmov\tr12d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_64(self):
        ''' 0x4001b1:	mov	ecx, r10d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, 'RIP': 4194737L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L, u'ECX': 1L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'text': 'D\x89\xd1', 'pos': {'registers': {'RCX': 0L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, 'RIP': 4194740L, u'R10D': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L, u'ECX': 0L}, 'memory': {4194737L: 'D', 4194738L: '\x89', 4194739L: '\xd1'}}, 'disassembly': u'0x4001b1:\tmov\tecx, r10d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_65(self):
        ''' 0x40019d:	mov	r13d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'text': 'D\x8b(', 'pos': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'disassembly': u'0x40019d:\tmov\tr13d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_66(self):
        ''' 0x400276:	mov	r9d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R9D': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194934L, 'RBP': 0L}, 'memory': {4194934L: 'A', 4194935L: '\xb9', 4194936L: '\x00', 4194937L: '\x00', 4194938L: '\x00', 4194939L: '\x00'}}, 'text': 'A\xb9\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R9D': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194940L, 'RBP': 0L}, 'memory': {4194934L: 'A', 4194935L: '\xb9', 4194936L: '\x00', 4194937L: '\x00', 4194938L: '\x00', 4194939L: '\x00'}}, 'disassembly': u'0x400276:\tmov\tr9d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_67(self):
        ''' 0x40016d:	mov	r9d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194669L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'text': 'D\x8b\x08', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R9D': 0L, 'RAX': 140737488346520L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194672L, 'RBP': 0L}, 'memory': {4194669L: 'D', 4194670L: '\x8b', 4194671L: '\x08', 140737488346520L: '\x00', 140737488346521L: '\x00', 140737488346522L: '\x00', 140737488346523L: '\x00'}}, 'disassembly': u'0x40016d:\tmov\tr9d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_68(self):
        ''' 0x400282:	mov	ecx, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'ECX': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194946L, 'RBP': 0L}, 'memory': {4194946L: '\xb9', 4194947L: '\x00', 4194948L: '\x00', 4194949L: '\x00', 4194950L: '\x00'}}, 'text': '\xb9\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'ECX': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194951L, 'RBP': 0L}, 'memory': {4194946L: '\xb9', 4194947L: '\x00', 4194948L: '\x00', 4194949L: '\x00', 4194950L: '\x00'}}, 'disassembly': u'0x400282:\tmov\tecx, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_69(self):
        ''' 0x4002ea:	mov	edi, 1 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, 'RAX': 0L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195050L, 'RBP': 0L}, 'memory': {4195050L: '\xbf', 4195051L: '\x01', 4195052L: '\x00', 4195053L: '\x00', 4195054L: '\x00'}}, 'text': '\xbf\x01\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, 'RAX': 0L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195055L, 'RBP': 0L}, 'memory': {4195050L: '\xbf', 4195051L: '\x01', 4195052L: '\x00', 4195053L: '\x00', 4195054L: '\x00'}}, 'disassembly': u'0x4002ea:\tmov\tedi, 1', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_7(self):
        ''' 0x4001bd:	mov	ebp, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, 'RSI': 0L, 'RIP': 4194749L, u'EAX': 4L, u'EBP': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'text': '\x89\xc5', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 4L, 'RDI': 0L, 'RSI': 0L, 'RIP': 4194751L, u'EAX': 4L, u'EBP': 4L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'disassembly': u'0x4001bd:\tmov\tebp, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_70(self):
        ''' 0x400251:	mov	eax, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194897L, 'RBP': 0L}, 'memory': {4194897L: '\xb8', 4194898L: '\x00', 4194899L: '\x00', 4194900L: '\x00', 4194901L: '\x00'}}, 'text': '\xb8\x00\x00\x00\x00', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194902L, 'RBP': 0L}, 'memory': {4194897L: '\xb8', 4194898L: '\x00', 4194899L: '\x00', 4194900L: '\x00', 4194901L: '\x00'}}, 'disassembly': u'0x400251:\tmov\teax, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_71(self):
        ''' 0x400191:	mov	r12d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RAX': 140737488346532L, 'RDI': 1L, u'R12D': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194705L, 'RBP': 0L}, 'memory': {140737488346532L: '\xf7', 140737488346533L: '\xff', 140737488346534L: '\xff', 140737488346535L: '\xff', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'text': 'D\x8b ', 'pos': {'registers': {'RFLAGS': 514L, 'RCX': 0L, 'RSI': 0L, 'RAX': 140737488346532L, 'RDI': 1L, u'R12D': 4294967287L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194708L, 'RBP': 0L}, 'memory': {140737488346532L: '\xf7', 140737488346533L: '\xff', 140737488346534L: '\xff', 140737488346535L: '\xff', 4194705L: 'D', 4194706L: '\x8b', 4194707L: ' '}}, 'disassembly': u'0x400191:\tmov\tr12d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_72(self):
        ''' 0x400116:	mov	dword ptr [rsp - 0x6c], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, u'EDI': 4L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194582L: '\x89', 140737488346516L: '\x03', 140737488346517L: '\x00', 140737488346518L: '\x00', 140737488346519L: '\x00', 4194584L: '$', 4194585L: '\x94', 4194583L: '|'}}, 'text': '\x89|$\x94', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, u'EDI': 4L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {140737488346516L: '\x04', 140737488346517L: '\x00', 4194582L: '\x89', 4194583L: '|', 4194584L: '$', 4194585L: '\x94', 140737488346519L: '\x00', 140737488346518L: '\x00'}}, 'disassembly': u'0x400116:\tmov\tdword ptr [rsp - 0x6c], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_73(self):
        ''' 0x4001dc:	mov	qword ptr [rsp], rsi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194780L, 'RBP': 0L}, 'memory': {140737488346776L: '\xc7', 140737488346777L: '\xde', 140737488346778L: '\xff', 140737488346779L: '\xff', 140737488346780L: '\xff', 140737488346781L: '\x7f', 140737488346782L: '\x00', 4194783L: '$', 4194780L: 'H', 4194781L: '\x89', 4194782L: '4', 140737488346783L: '\x00'}}, 'text': 'H\x894$', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194784L, 'RBP': 0L}, 'memory': {140737488346776L: '0', 140737488346777L: '\x03', 140737488346778L: '@', 140737488346779L: '\x00', 4194780L: 'H', 4194781L: '\x89', 4194782L: '4', 140737488346783L: '\x00', 140737488346780L: '\x00', 140737488346781L: '\x00', 140737488346782L: '\x00', 4194783L: '$'}}, 'disassembly': u'0x4001dc:\tmov\tqword ptr [rsp], rsi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_74(self):
        ''' 0x4001ab:	mov	eax, r8d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, u'R8D': 3L, 'RIP': 4194731L, u'EAX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'text': 'D\x89\xc0', 'pos': {'registers': {'RCX': 1L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, u'R8D': 3L, 'RIP': 4194734L, u'EAX': 3L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'disassembly': u'0x4001ab:\tmov\teax, r8d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_75(self):
        ''' 0x400124:	mov	qword ptr [rsp - 0x40], rcx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {140737488346560L: '*', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'text': 'H\x89L$\xc0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346560L: '\x00', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'disassembly': u'0x400124:\tmov\tqword ptr [rsp - 0x40], rcx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_76(self):
        ''' 0x4002b4:	mov	rsi, rax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4194996L, 'RBP': 0L}, 'memory': {4194996L: 'H', 4194997L: '\x89', 4194998L: '\xc6'}}, 'text': 'H\x89\xc6', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4194999L, 'RBP': 0L}, 'memory': {4194996L: 'H', 4194997L: '\x89', 4194998L: '\xc6'}}, 'disassembly': u'0x4002b4:\tmov\trsi, rax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_77(self):
        ''' 0x40028c:	mov	esi, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194956L, u'EAX': 0L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194956L: '\x89', 4194957L: '\xc6'}}, 'text': '\x89\xc6', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, u'ESI': 0L, 'RSI': 0L, 'RIP': 4194958L, u'EAX': 0L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194956L: '\x89', 4194957L: '\xc6'}}, 'disassembly': u'0x40028c:\tmov\tesi, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_78(self):
        ''' 0x400268:	mov	dword ptr [rsp + 0xc], edi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RAX': 4294967287L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194920L, 'RBP': 0L}, 'memory': {140737488346788L: '\x01', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194920L: '\x89', 4194921L: '|', 4194922L: '$', 4194923L: '\x0c'}}, 'text': '\x89|$\x0c', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RAX': 4294967287L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194924L, 'RBP': 0L}, 'memory': {140737488346788L: '\x00', 140737488346789L: '\x00', 140737488346790L: '\x00', 140737488346791L: '\x00', 4194920L: '\x89', 4194921L: '|', 4194922L: '$', 4194923L: '\x0c'}}, 'disassembly': u'0x400268:\tmov\tdword ptr [rsp + 0xc], edi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_79(self):
        ''' 0x4002af:	mov	edx, 1 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4194991L, 'RBP': 0L}, 'memory': {4194992L: '\x01', 4194993L: '\x00', 4194994L: '\x00', 4194995L: '\x00', 4194991L: '\xba'}}, 'text': '\xba\x01\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'EDX': 1L, 'RAX': 140737488346823L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4194996L, 'RBP': 0L}, 'memory': {4194992L: '\x01', 4194993L: '\x00', 4194994L: '\x00', 4194995L: '\x00', 4194991L: '\xba'}}, 'disassembly': u'0x4002af:\tmov\tedx, 1', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_8(self):
        ''' 0x4001b4:	mov	edx, r11d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 140737488346823L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, u'R11D': 0L, 'RIP': 4194740L, u'EDX': 4294958791L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'text': 'D\x89\xda', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 3L, 'RSI': 0L, u'R11D': 0L, 'RIP': 4194743L, u'EDX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'disassembly': u'0x4001b4:\tmov\tedx, r11d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_80(self):
        ''' 0x400202:	mov	esi, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 1L, u'ESI': 4195120L, 'RSI': 4195120L, 'RIP': 4194818L, u'EAX': 1L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194818L: '\x89', 4194819L: '\xc6'}}, 'text': '\x89\xc6', 'pos': {'registers': {'RCX': 42L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 1L, u'ESI': 1L, 'RSI': 1L, 'RIP': 4194820L, u'EAX': 1L, 'RSP': 140737488346760L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194818L: '\x89', 4194819L: '\xc6'}}, 'disassembly': u'0x400202:\tmov\tesi, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_81(self):
        ''' 0x400179:	mov	r10d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 140737488346524L, 'RDI': 4L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'text': 'D\x8b\x10', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 140737488346524L, 'RDI': 4L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'disassembly': u'0x400179:\tmov\tr10d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_82(self):
        ''' 0x40011a:	mov	qword ptr [rsp - 0x50], rsi '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194586L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x01', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'text': 'H\x89t$\xb0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194586L: 'H', 4194587L: '\x89', 4194588L: 't', 4194589L: '$', 4194590L: '\xb0', 140737488346544L: '\x00', 140737488346545L: '\x00', 140737488346546L: '\x00', 140737488346547L: '\x00', 140737488346548L: '\x00', 140737488346549L: '\x00', 140737488346550L: '\x00', 140737488346551L: '\x00'}}, 'disassembly': u'0x40011a:\tmov\tqword ptr [rsp - 0x50], rsi', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_83(self):
        ''' 0x4001e4:	mov	ecx, dword ptr [rsp + 8] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, u'ECX': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194788L, 'RBP': 0L}, 'memory': {140737488346784L: '*', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194788L: '\x8b', 4194789L: 'L', 4194790L: '$', 4194791L: '\x08'}}, 'text': '\x8bL$\x08', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, u'ECX': 42L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194792L, 'RBP': 0L}, 'memory': {140737488346784L: '*', 140737488346785L: '\x00', 140737488346786L: '\x00', 140737488346787L: '\x00', 4194788L: '\x8b', 4194789L: 'L', 4194790L: '$', 4194791L: '\x08'}}, 'disassembly': u'0x4001e4:\tmov\tecx, dword ptr [rsp + 8]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_84(self):
        ''' 0x400129:	mov	qword ptr [rsp - 0x38], r8 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'text': 'L\x89D$\xc8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R8': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194606L, 'RBP': 0L}, 'memory': {140737488346568L: '\x00', 140737488346569L: '\x00', 140737488346570L: '\x00', 140737488346571L: '\x00', 140737488346572L: '\x00', 140737488346573L: '\x00', 140737488346574L: '\x00', 140737488346575L: '\x00', 4194601L: 'L', 4194602L: '\x89', 4194603L: 'D', 4194604L: '$', 4194605L: '\xc8'}}, 'disassembly': u'0x400129:\tmov\tqword ptr [rsp - 0x38], r8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_85(self):
        ''' 0x4001c1:	mov	dword ptr [rsp - 0x5c], eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194753L, 'RBP': 3L}, 'memory': {4194753L: '\x89', 4194754L: 'D', 4194755L: '$', 140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194756L: '\xa4'}}, 'text': '\x89D$\xa4', 'pos': {'registers': {u'EAX': 0L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194757L, 'RBP': 3L}, 'memory': {4194753L: '\x89', 4194754L: 'D', 4194755L: '$', 140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194756L: '\xa4'}}, 'disassembly': u'0x4001c1:\tmov\tdword ptr [rsp - 0x5c], eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_86(self):
        ''' 0x400185:	mov	r11d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R11D': 0L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194693L, 'RBP': 0L}, 'memory': {140737488346528L: '\x00', 140737488346529L: '\x00', 140737488346530L: '\x00', 140737488346531L: '\x00', 4194693L: 'D', 4194694L: '\x8b', 4194695L: '\x18'}}, 'text': 'D\x8b\x18', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R11D': 0L, 'RAX': 140737488346528L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194696L, 'RBP': 0L}, 'memory': {140737488346528L: '\x00', 140737488346529L: '\x00', 140737488346530L: '\x00', 140737488346531L: '\x00', 4194693L: 'D', 4194694L: '\x8b', 4194695L: '\x18'}}, 'disassembly': u'0x400185:\tmov\tr11d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_87(self):
        ''' 0x4001ab:	mov	eax, r8d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, u'R8D': 1L, 'RIP': 4194731L, u'EAX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 0L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'text': 'D\x89\xc0', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 1L, 'RSI': 0L, u'R8D': 1L, 'RIP': 4194734L, u'EAX': 1L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 1L}, 'memory': {4194731L: 'D', 4194732L: '\x89', 4194733L: '\xc0'}}, 'disassembly': u'0x4001ab:\tmov\teax, r8d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_88(self):
        ''' 0x4001c1:	mov	dword ptr [rsp - 0x5c], eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294967287L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 18446744073709551607L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194753L, 'RBP': 4L}, 'memory': {4194753L: '\x89', 4194754L: 'D', 4194755L: '$', 140737488346532L: '\x00', 140737488346533L: '\x00', 140737488346534L: '\x00', 140737488346535L: '\x00', 4194756L: '\xa4'}}, 'text': '\x89D$\xa4', 'pos': {'registers': {u'EAX': 4294967287L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 18446744073709551607L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194757L, 'RBP': 4L}, 'memory': {4194753L: '\x89', 4194754L: 'D', 4194755L: '$', 140737488346532L: '\xf7', 140737488346533L: '\xff', 140737488346534L: '\xff', 140737488346535L: '\xff', 4194756L: '\xa4'}}, 'disassembly': u'0x4001c1:\tmov\tdword ptr [rsp - 0x5c], eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_89(self):
        ''' 0x40019d:	mov	r13d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194717L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'text': 'D\x8b(', 'pos': {'registers': {'RFLAGS': 514L, u'R13D': 0L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 140737488346536L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194720L, 'RBP': 0L}, 'memory': {140737488346536L: '\x00', 140737488346537L: '\x00', 140737488346538L: '\x00', 140737488346539L: '\x00', 4194717L: 'D', 4194718L: '\x8b', 4194719L: '('}}, 'disassembly': u'0x40019d:\tmov\tr13d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_9(self):
        ''' 0x40023e:	mov	r9d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, u'R9D': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194878L, 'RBP': 0L}, 'memory': {4194880L: '\x00', 4194881L: '\x00', 4194882L: '\x00', 4194883L: '\x00', 4194878L: 'A', 4194879L: '\xb9'}}, 'text': 'A\xb9\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, u'R9D': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194884L, 'RBP': 0L}, 'memory': {4194880L: '\x00', 4194881L: '\x00', 4194882L: '\x00', 4194883L: '\x00', 4194878L: 'A', 4194879L: '\xb9'}}, 'disassembly': u'0x40023e:\tmov\tr9d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_90(self):
        ''' 0x4002e5:	mov	esi, 0x400330 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, u'ESI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195045L, 'RBP': 0L}, 'memory': {4195048L: '@', 4195049L: '\x00', 4195045L: '\xbe', 4195046L: '0', 4195047L: '\x03'}}, 'text': '\xbe0\x03@\x00', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, u'ESI': 4195120L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 42L, 'RIP': 4195050L, 'RBP': 0L}, 'memory': {4195048L: '@', 4195049L: '\x00', 4195045L: '\xbe', 4195046L: '0', 4195047L: '\x03'}}, 'disassembly': u'0x4002e5:\tmov\tesi, 0x400330', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_91(self):
        ''' 0x4001c5:	mov	eax, dword ptr [rsp - 0x5c] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {u'EAX': 4294967287L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 18446744073709551607L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194757L, 'RBP': 4L}, 'memory': {140737488346532L: '\xf7', 4194757L: '\x8b', 4194758L: 'D', 140737488346534L: '\xff', 4194760L: '\xa4', 140737488346533L: '\xff', 140737488346535L: '\xff', 4194759L: '$'}}, 'text': '\x8bD$\xa4', 'pos': {'registers': {u'EAX': 4294967287L, 'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194761L, 'RBP': 4L}, 'memory': {140737488346532L: '\xf7', 4194757L: '\x8b', 4194758L: 'D', 140737488346534L: '\xff', 4194760L: '\xa4', 140737488346535L: '\xff', 4194759L: '$', 140737488346533L: '\xff'}}, 'disassembly': u'0x4001c5:\tmov\teax, dword ptr [rsp - 0x5c]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_92(self):
        ''' 0x400124:	mov	qword ptr [rsp - 0x40], rcx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {140737488346560L: '\x00', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'text': 'H\x89L$\xc0', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194601L, 'RBP': 0L}, 'memory': {140737488346560L: '\x01', 140737488346561L: '\x00', 140737488346562L: '\x00', 140737488346563L: '\x00', 140737488346564L: '\x00', 140737488346565L: '\x00', 140737488346566L: '\x00', 140737488346567L: '\x00', 4194596L: 'H', 4194597L: '\x89', 4194598L: 'L', 4194599L: '$', 4194600L: '\xc0'}}, 'disassembly': u'0x400124:\tmov\tqword ptr [rsp - 0x40], rcx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_93(self):
        ''' 0x4001bd:	mov	ebp, eax '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 0L, 'RSI': 0L, 'RIP': 4194749L, u'EAX': 3L, u'EBP': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'text': '\x89\xc5', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 3L, 'RDI': 0L, 'RSI': 0L, 'RIP': 4194751L, u'EAX': 3L, u'EBP': 3L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 3L}, 'memory': {4194749L: '\x89', 4194750L: '\xc5'}}, 'disassembly': u'0x4001bd:\tmov\tebp, eax', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_94(self):
        ''' 0x40011f:	mov	qword ptr [rsp - 0x48], rdx '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194591L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '\xc7', 140737488346553L: '\xde', 140737488346554L: '\xff', 140737488346555L: '\xff', 140737488346556L: '\xff', 140737488346557L: '\x7f', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'text': 'H\x89T$\xb8', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194596L, 'RBP': 0L}, 'memory': {4194591L: 'H', 4194592L: '\x89', 4194593L: 'T', 4194594L: '$', 4194595L: '\xb8', 140737488346552L: '0', 140737488346553L: '\x03', 140737488346554L: '@', 140737488346555L: '\x00', 140737488346556L: '\x00', 140737488346557L: '\x00', 140737488346558L: '\x00', 140737488346559L: '\x00'}}, 'disassembly': u'0x40011f:\tmov\tqword ptr [rsp - 0x48], rdx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_95(self):
        ''' 0x4001b4:	mov	edx, r11d '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RCX': 0L, 'RDX': 4195120L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, u'R11D': 0L, 'RIP': 4194740L, u'EDX': 4195120L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'text': 'D\x89\xda', 'pos': {'registers': {'RCX': 0L, 'RDX': 0L, 'RBP': 0L, 'RDI': 4L, 'RSI': 1L, u'R11D': 0L, 'RIP': 4194743L, u'EDX': 0L, 'RSP': 140737488346624L, 'RFLAGS': 518L, 'RAX': 4L}, 'memory': {4194740L: 'D', 4194741L: '\x89', 4194742L: '\xda'}}, 'disassembly': u'0x4001b4:\tmov\tedx, r11d', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_96(self):
        ''' 0x4002b7:	mov	edi, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RAX': 140737488346823L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4194999L, 'RBP': 0L}, 'memory': {4195000L: '\x00', 4195001L: '\x00', 4195002L: '\x00', 4195003L: '\x00', 4194999L: '\xbf'}}, 'text': '\xbf\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RAX': 140737488346823L, 'RDI': 0L, u'EDI': 0L, 'RSP': 140737488346808L, 'RDX': 1L, 'RIP': 4195004L, 'RBP': 0L}, 'memory': {4195000L: '\x00', 4195001L: '\x00', 4195002L: '\x00', 4195003L: '\x00', 4194999L: '\xbf'}}, 'disassembly': u'0x4002b7:\tmov\tedi, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_97(self):
        ''' 0x4001f6:	mov	r9d, 0 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, u'R9D': 0L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194806L, 'RBP': 0L}, 'memory': {4194806L: 'A', 4194807L: '\xb9', 4194808L: '\x00', 4194809L: '\x00', 4194810L: '\x00', 4194811L: '\x00'}}, 'text': 'A\xb9\x00\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, u'R9D': 0L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194812L, 'RBP': 0L}, 'memory': {4194806L: 'A', 4194807L: '\xb9', 4194808L: '\x00', 4194809L: '\x00', 4194810L: '\x00', 4194811L: '\x00'}}, 'disassembly': u'0x4001f6:\tmov\tr9d, 0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_98(self):
        ''' 0x400179:	mov	r10d, dword ptr [rax] '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 140737488346524L, 'RDI': 1L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194681L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'text': 'D\x8b\x10', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 140737488346524L, 'RDI': 1L, u'R10D': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194684L, 'RBP': 0L}, 'memory': {4194681L: 'D', 4194682L: '\x8b', 4194683L: '\x10', 140737488346524L: '\x00', 140737488346525L: '\x00', 140737488346526L: '\x00', 140737488346527L: '\x00'}}, 'disassembly': u'0x400179:\tmov\tr10d, dword ptr [rax]', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_MOV_99(self):
        ''' 0x400204:	mov	edi, 4 '''
        test = {'mnemonic': u'MOV', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 1L, 'RDI': 1L, u'EDI': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194820L, 'RBP': 0L}, 'memory': {4194824L: '\x00', 4194820L: '\xbf', 4194821L: '\x04', 4194822L: '\x00', 4194823L: '\x00'}}, 'text': '\xbf\x04\x00\x00\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 1L, 'RDI': 4L, u'EDI': 4L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194825L, 'RBP': 0L}, 'memory': {4194824L: '\x00', 4194820L: '\xbf', 4194821L: '\x04', 4194822L: '\x00', 4194823L: '\x00'}}, 'disassembly': u'0x400204:\tmov\tedi, 4', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_1(self):
        ''' 0x4001cf:	pop	r12 '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R12': 0L, 'RAX': 4294967287L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194767L, 'RBP': 0L}, 'memory': {140737488346736L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 4194768L: '\\', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 4194767L: 'A'}}, 'text': 'A\\', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R12': 0L, 'RAX': 4294967287L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194769L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 4194767L: 'A', 4194768L: '\\', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001cf:\tpop\tr12', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_2(self):
        ''' 0x4001d1:	pop	r13 '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R13': 0L, 'RAX': 4294967287L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194769L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194769L: 'A', 4194770L: ']', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'A]', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R13': 0L, 'RAX': 4294967287L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194771L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194769L: 'A', 4194770L: ']', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001d1:\tpop\tr13', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_3(self):
        ''' 0x4001cf:	pop	r12 '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194767L, 'RBP': 0L}, 'memory': {140737488346736L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 4194768L: '\\', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 4194767L: 'A'}}, 'text': 'A\\', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194769L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 4194767L: 'A', 4194768L: '\\', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001cf:\tpop\tr12', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_4(self):
        ''' 0x4001ce:	pop	rbp '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194766L, 'RBP': 4L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194766L: ']', 140737488346719L: '\x00'}}, 'text': ']', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194767L, 'RBP': 0L}, 'memory': {4194766L: ']', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'disassembly': u'0x4001ce:\tpop\trbp', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_5(self):
        ''' 0x4001cd:	pop	rbx '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194765L, 'RBP': 4L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 4194765L: '[', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00'}}, 'text': '[', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194766L, 'RBP': 4L}, 'memory': {4194765L: '[', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00'}}, 'disassembly': u'0x4001cd:\tpop\trbx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_6(self):
        ''' 0x4001ce:	pop	rbp '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194766L, 'RBP': 3L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194766L: ']', 140737488346719L: '\x00'}}, 'text': ']', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194767L, 'RBP': 0L}, 'memory': {4194766L: ']', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'disassembly': u'0x4001ce:\tpop\trbp', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_7(self):
        ''' 0x4001d1:	pop	r13 '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194769L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194769L: 'A', 4194770L: ']', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'A]', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194771L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194769L: 'A', 4194770L: ']', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001d1:\tpop\tr13', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_POP_8(self):
        ''' 0x4001cd:	pop	rbx '''
        test = {'mnemonic': u'POP', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194765L, 'RBP': 3L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 4194765L: '[', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00'}}, 'text': '[', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194766L, 'RBP': 3L}, 'memory': {4194765L: '[', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00'}}, 'disassembly': u'0x4001cd:\tpop\trbx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_1(self):
        ''' 0x400110:	push	rbp '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346736L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 4194576L: 'U', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'text': 'U', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {4194576L: 'U', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'disassembly': u'0x400110:\tpush\trbp', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_10(self):
        ''' 0x40010e:	push	r12 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 4195120L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346747L: '\x00', 4194574L: 'A', 4194575L: 'T', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346735L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AT', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 4195120L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 4194574L: 'A', 4194575L: 'T', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010e:\tpush\tr12', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_11(self):
        ''' 0x400110:	push	rbp '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 4195120L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346736L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 4194576L: 'U', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'text': 'U', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 4195120L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {4194576L: 'U', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'disassembly': u'0x400110:\tpush\trbp', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_12(self):
        ''' 0x40010c:	push	r13 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 4195120L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AU', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 4195120L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010c:\tpush\tr13', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_13(self):
        ''' 0x40023c:	push	0 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346768L, 'RDX': 140737488346823L, 'RIP': 4194876L, 'RBP': 0L}, 'memory': {140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '\xc7', 4194876L: 'j', 4194877L: '\x00'}}, 'text': 'j\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 140737488346823L, 'RIP': 4194878L, 'RBP': 0L}, 'memory': {140737488346752L: '\x00', 140737488346753L: '\x00', 140737488346754L: '\x00', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '\xc7', 4194876L: 'j', 4194877L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40023c:\tpush\t0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_14(self):
        ''' 0x40010e:	push	r12 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 140737488346823L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346747L: '\x00', 4194574L: 'A', 4194575L: 'T', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346735L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AT', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 140737488346823L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 4194574L: 'A', 4194575L: 'T', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010e:\tpush\tr12', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_15(self):
        ''' 0x400110:	push	rbp '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 140737488346823L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346736L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 4194576L: 'U', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'text': 'U', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 140737488346823L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {4194576L: 'U', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00'}}, 'disassembly': u'0x400110:\tpush\trbp', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_2(self):
        ''' 0x400111:	push	rbx '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, u'RBX': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 140737488346823L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194577L: 'S', 140737488346719L: '\x00'}}, 'text': 'S', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, u'RBX': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 140737488346823L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194577L: 'S', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00'}}, 'disassembly': u'0x400111:\tpush\trbx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_3(self):
        ''' 0x40010c:	push	r13 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 140737488346823L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AU', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 140737488346823L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010c:\tpush\tr13', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_4(self):
        ''' 0x400111:	push	rbx '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 0L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194577L: 'S', 140737488346719L: '\x00'}}, 'text': 'S', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, u'RBX': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194577L: 'S', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00'}}, 'disassembly': u'0x400111:\tpush\trbx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_5(self):
        ''' 0x40010c:	push	r13 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194572L, 'RBP': 0L}, 'memory': {140737488346752L: '\x9d', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AU', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R13': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '\x9d', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194572L: 'A', 4194573L: 'U', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010c:\tpush\tr13', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_6(self):
        ''' 0x40010e:	push	r12 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346744L, 'RDX': 0L, 'RIP': 4194574L, 'RBP': 0L}, 'memory': {140737488346752L: '\x9d', 140737488346747L: '\x00', 4194574L: 'A', 4194575L: 'T', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346735L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': 'AT', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, u'R12': 0L, 'RAX': 0L, 'RSP': 140737488346736L, 'RDX': 0L, 'RIP': 4194576L, 'RBP': 0L}, 'memory': {140737488346752L: '\x9d', 4194574L: 'A', 4194575L: 'T', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 140737488346737L: '\x00', 140737488346738L: '\x00', 140737488346739L: '\x00', 140737488346740L: '\x00', 140737488346741L: '\x00', 140737488346742L: '\x00', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x40010e:\tpush\tr12', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_7(self):
        ''' 0x400111:	push	rbx '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, u'RBX': 0L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346728L, 'RDX': 4195120L, 'RIP': 4194577L, 'RBP': 0L}, 'memory': {140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00', 4194577L: 'S', 140737488346719L: '\x00'}}, 'text': 'S', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, u'RBX': 0L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 4195120L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194577L: 'S', 140737488346711L: '\x00', 140737488346712L: '\x00', 140737488346713L: '\x00', 140737488346714L: '\x00', 140737488346715L: '\x00', 140737488346716L: '\x00', 140737488346717L: '\x00', 140737488346718L: '\x00', 140737488346719L: '\x00', 140737488346720L: '\x00', 140737488346721L: '\x00', 140737488346722L: '\x00', 140737488346723L: '\x00', 140737488346724L: '\x00', 140737488346725L: '\x00', 140737488346726L: '\x00', 140737488346727L: '\x00', 140737488346728L: '\x00', 140737488346729L: '\x00', 140737488346730L: '\x00', 140737488346731L: '\x00', 140737488346732L: '\x00', 140737488346733L: '\x00', 140737488346734L: '\x00', 140737488346735L: '\x00', 140737488346736L: '\x00'}}, 'disassembly': u'0x400111:\tpush\trbx', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_8(self):
        ''' 0x4001f4:	push	0 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346768L, 'RDX': 4195120L, 'RIP': 4194804L, 'RBP': 0L}, 'memory': {140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '0', 4194804L: 'j', 4194805L: '\x00'}}, 'text': 'j\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346760L, 'RDX': 4195120L, 'RIP': 4194806L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '0', 4194804L: 'j', 4194805L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001f4:\tpush\t0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_PUSH_9(self):
        ''' 0x400274:	push	0 '''
        test = {'mnemonic': u'PUSH', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346768L, 'RDX': 0L, 'RIP': 4194932L, 'RBP': 0L}, 'memory': {140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '0', 4194932L: 'j', 4194933L: '\x00'}}, 'text': 'j\x00', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194934L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 140737488346769L: '\x00', 140737488346770L: '\x00', 140737488346771L: '\x00', 140737488346772L: '\x00', 140737488346773L: '\x00', 140737488346774L: '\x00', 140737488346775L: '\x00', 140737488346776L: '0', 4194932L: 'j', 4194933L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x400274:\tpush\t0', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_RET_1(self):
        ''' 0x40021b:	ret	 '''
        test = {'mnemonic': u'RET', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194843L, 'RBP': 0L}, 'memory': {140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xf4', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 4194843L: '\xc3'}}, 'text': '\xc3', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195060L, 'RBP': 0L}, 'memory': {4194843L: '\xc3', 140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xf4', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00'}}, 'disassembly': u'0x40021b:\tret\t', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_RET_2(self):
        ''' 0x4001d3:	ret	 '''
        test = {'mnemonic': u'RET', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194771L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194771L: '\xc3', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': '\xc3', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194907L, 'RBP': 0L}, 'memory': {140737488346752L: '[', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194771L: '\xc3', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001d3:\tret\t', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_RET_3(self):
        ''' 0x400263:	ret	 '''
        test = {'mnemonic': u'RET', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194915L, 'RBP': 0L}, 'memory': {4194915L: '\xc3', 140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xc1', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00'}}, 'text': '\xc3', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4195009L, 'RBP': 0L}, 'memory': {140737488346791L: '\x00', 140737488346792L: '\x00', 140737488346793L: '\x00', 140737488346794L: '\x00', 140737488346795L: '\x00', 140737488346796L: '\x00', 140737488346797L: '\x00', 140737488346798L: '\x00', 140737488346799L: '\x00', 140737488346800L: '\xc1', 140737488346801L: '\x02', 140737488346802L: '@', 140737488346803L: '\x00', 140737488346804L: '\x00', 140737488346805L: '\x00', 140737488346806L: '\x00', 140737488346807L: '\x00', 140737488346808L: '\x00', 140737488346809L: '\x00', 140737488346810L: '\x00', 140737488346811L: '\x00', 140737488346812L: '\x00', 140737488346813L: '\x00', 140737488346814L: '\x00', 140737488346815L: '\x00', 140737488346816L: '\x00', 4194915L: '\xc3'}}, 'disassembly': u'0x400263:\tret\t', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_RET_4(self):
        ''' 0x4001d3:	ret	 '''
        test = {'mnemonic': u'RET', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346752L, 'RDX': 0L, 'RIP': 4194771L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 4194771L: '\xc3', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'text': '\xc3', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346760L, 'RDX': 0L, 'RIP': 4194835L, 'RBP': 0L}, 'memory': {140737488346752L: '\x13', 140737488346753L: '\x02', 140737488346754L: '@', 140737488346755L: '\x00', 140737488346756L: '\x00', 140737488346757L: '\x00', 140737488346758L: '\x00', 140737488346759L: '\x00', 140737488346760L: '\x00', 140737488346761L: '\x00', 140737488346762L: '\x00', 140737488346763L: '\x00', 140737488346764L: '\x00', 140737488346765L: '\x00', 140737488346766L: '\x00', 140737488346767L: '\x00', 140737488346768L: '\x00', 4194771L: '\xc3', 140737488346743L: '\x00', 140737488346744L: '\x00', 140737488346745L: '\x00', 140737488346746L: '\x00', 140737488346747L: '\x00', 140737488346748L: '\x00', 140737488346749L: '\x00', 140737488346750L: '\x00', 140737488346751L: '\x00'}}, 'disassembly': u'0x4001d3:\tret\t', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_1(self):
        ''' 0x4002a6:	sub	rsp, 0x18 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 512L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346832L, 'RDX': 0L, 'RIP': 4194982L, 'RBP': 0L}, 'memory': {4194984L: '\xec', 4194985L: '\x18', 4194982L: 'H', 4194983L: '\x83'}}, 'text': 'H\x83\xec\x18', 'pos': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346808L, 'RDX': 0L, 'RIP': 4194986L, 'RBP': 0L}, 'memory': {4194984L: '\xec', 4194985L: '\x18', 4194982L: 'H', 4194983L: '\x83'}}, 'disassembly': u'0x4002a6:\tsub\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_10(self):
        ''' 0x4001f0:	sub	rsp, 8 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346776L, 'RDX': 4195120L, 'RIP': 4194800L, 'RBP': 0L}, 'memory': {4194800L: 'H', 4194801L: '\x83', 4194802L: '\xec', 4194803L: '\x08'}}, 'text': 'H\x83\xec\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 1L, 'RSP': 140737488346768L, 'RDX': 4195120L, 'RIP': 4194804L, 'RBP': 0L}, 'memory': {4194800L: 'H', 4194801L: '\x83', 4194802L: '\xec', 4194803L: '\x08'}}, 'disassembly': u'0x4001f0:\tsub\trsp, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_2(self):
        ''' 0x40021c:	sub	rsp, 0x18 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 534L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346800L, 'RDX': 1L, 'RIP': 4194844L, 'RBP': 0L}, 'memory': {4194844L: 'H', 4194845L: '\x83', 4194846L: '\xec', 4194847L: '\x18'}}, 'text': 'H\x83\xec\x18', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 140737488346823L, 'RSP': 140737488346776L, 'RDX': 1L, 'RIP': 4194848L, 'RBP': 0L}, 'memory': {4194844L: 'H', 4194845L: '\x83', 4194846L: '\xec', 4194847L: '\x18'}}, 'disassembly': u'0x40021c:\tsub\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_3(self):
        ''' 0x400112:	sub	rsp, 0x60 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 0L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'text': 'H\x83\xec`', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 0L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'disassembly': u'0x400112:\tsub\trsp, 0x60', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_4(self):
        ''' 0x400270:	sub	rsp, 8 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194928L, 'RBP': 0L}, 'memory': {4194928L: 'H', 4194929L: '\x83', 4194930L: '\xec', 4194931L: '\x08'}}, 'text': 'H\x83\xec\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346768L, 'RDX': 0L, 'RIP': 4194932L, 'RBP': 0L}, 'memory': {4194928L: 'H', 4194929L: '\x83', 4194930L: '\xec', 4194931L: '\x08'}}, 'disassembly': u'0x400270:\tsub\trsp, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_5(self):
        ''' 0x400112:	sub	rsp, 0x60 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 4195120L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'text': 'H\x83\xec`', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RDI': 4L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 4195120L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'disassembly': u'0x400112:\tsub\trsp, 0x60', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_6(self):
        ''' 0x400264:	sub	rsp, 0x18 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346800L, 'RDX': 0L, 'RIP': 4194916L, 'RBP': 0L}, 'memory': {4194916L: 'H', 4194917L: '\x83', 4194918L: '\xec', 4194919L: '\x18'}}, 'text': 'H\x83\xec\x18', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RDI': 0L, 'RAX': 4294967287L, 'RSP': 140737488346776L, 'RDX': 0L, 'RIP': 4194920L, 'RBP': 0L}, 'memory': {4194916L: 'H', 4194917L: '\x83', 4194918L: '\xec', 4194919L: '\x18'}}, 'disassembly': u'0x400264:\tsub\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_7(self):
        ''' 0x400238:	sub	rsp, 8 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 140737488346823L, 'RIP': 4194872L, 'RBP': 0L}, 'memory': {4194872L: 'H', 4194873L: '\x83', 4194874L: '\xec', 4194875L: '\x08'}}, 'text': 'H\x83\xec\x08', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 140737488346823L, 'RDI': 0L, 'RAX': 0L, 'RSP': 140737488346768L, 'RDX': 140737488346823L, 'RIP': 4194876L, 'RBP': 0L}, 'memory': {4194872L: 'H', 4194873L: '\x83', 4194874L: '\xec', 4194875L: '\x08'}}, 'disassembly': u'0x400238:\tsub\trsp, 8', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_8(self):
        ''' 0x4001d4:	sub	rsp, 0x18 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346800L, 'RDX': 42L, 'RIP': 4194772L, 'RBP': 0L}, 'memory': {4194772L: 'H', 4194773L: '\x83', 4194774L: '\xec', 4194775L: '\x18'}}, 'text': 'H\x83\xec\x18', 'pos': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 4195120L, 'RDI': 1L, 'RAX': 0L, 'RSP': 140737488346776L, 'RDX': 42L, 'RIP': 4194776L, 'RBP': 0L}, 'memory': {4194772L: 'H', 4194773L: '\x83', 4194774L: '\xec', 4194775L: '\x18'}}, 'disassembly': u'0x4001d4:\tsub\trsp, 0x18', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_SUB_9(self):
        ''' 0x400112:	sub	rsp, 0x60 '''
        test = {'mnemonic': u'SUB', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346720L, 'RDX': 140737488346823L, 'RIP': 4194578L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'text': 'H\x83\xec`', 'pos': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RDI': 3L, 'RAX': 0L, 'RSP': 140737488346624L, 'RDX': 140737488346823L, 'RIP': 4194582L, 'RBP': 0L}, 'memory': {4194578L: 'H', 4194579L: '\x83', 4194580L: '\xec', 4194581L: '`'}}, 'disassembly': u'0x400112:\tsub\trsp, 0x60', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_TEST_1(self):
        ''' 0x400133:	test	al, al '''
        test = {'mnemonic': u'TEST', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194611L, 'RDX': 4195120L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'text': '\x84\xc0', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 42L, 'RSI': 1L, 'RAX': 0L, 'RDI': 4L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194613L, 'RDX': 4195120L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'disassembly': u'0x400133:\ttest\tal, al', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_TEST_2(self):
        ''' 0x4002c6:	test	al, al '''
        test = {'mnemonic': u'TEST', 'pre': {'registers': {'RFLAGS': 530L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 0L, 'RBP': 0L, 'RSP': 140737488346808L, u'AL': 0L, 'RIP': 4195014L, 'RDX': 0L}, 'memory': {4195014L: '\x84', 4195015L: '\xc0'}}, 'text': '\x84\xc0', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 0L, 'RBP': 0L, 'RSP': 140737488346808L, u'AL': 0L, 'RIP': 4195016L, 'RDX': 0L}, 'memory': {4195014L: '\x84', 4195015L: '\xc0'}}, 'disassembly': u'0x4002c6:\ttest\tal, al', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_TEST_3(self):
        ''' 0x400133:	test	al, al '''
        test = {'mnemonic': u'TEST', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194611L, 'RDX': 0L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'text': '\x84\xc0', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 0L, 'RSI': 0L, 'RAX': 0L, 'RDI': 1L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194613L, 'RDX': 0L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'disassembly': u'0x400133:\ttest\tal, al', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


    def test_TEST_4(self):
        ''' 0x400133:	test	al, al '''
        test = {'mnemonic': u'TEST', 'pre': {'registers': {'RFLAGS': 518L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194611L, 'RDX': 140737488346823L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'text': '\x84\xc0', 'pos': {'registers': {'RFLAGS': 582L, 'RCX': 1L, 'RSI': 0L, 'RAX': 0L, 'RDI': 3L, 'RBP': 0L, 'RSP': 140737488346624L, u'AL': 0L, 'RIP': 4194613L, 'RDX': 140737488346823L}, 'memory': {4194611L: '\x84', 4194612L: '\xc0'}}, 'disassembly': u'0x400133:\ttest\tal, al', 'arch': 'amd64'}

        solver = Solver()

        mem = SymCPUTest.SMem(solver.mkArray({'i386': 32, 'amd64': 64}[test['arch']]), test['pre']['memory'])
        cpu = Cpu(mem, test['arch'])
        for reg_name in test['pre']['registers']:
            if reg_name in ['RIP','EIP','IP']:
                cpu.setRegister(reg_name, test['pre']['registers'][reg_name])
                try:
                    for i in range(16):
                        addr = test['pre']['registers'][reg_name]+i
                        mem.setcode(addr, test['pre']['memory'][addr])
                except Exception,e:
                    pass
            else:
                var = solver.mkBitVec(sizes[reg_name],reg_name)
                solver.add(var == test['pre']['registers'][reg_name])
                cpu.setRegister(reg_name, var)

        cpu.execute()

        for addr in test['pos']['memory'].keys():
            solver.add(mem.getchar(addr) == test['pos']['memory'][addr])

        for reg_name in test['pos']['registers']:
            if 'FLAG' in reg_name:
                solver.add(cpu.getRegister(reg_name)&0x10cd5 == test['pos']['registers'][reg_name]&0x10cd5)
            else:
                solver.add(cpu.getRegister(reg_name) == test['pos']['registers'][reg_name])
        self.assertEqual(solver.check(), 'sat')


if __name__ == '__main__':
    unittest.main()


# Copyright 2021 PyAge2, Oleksii Kachaiev <kachayev@gmail.com>. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Set of utils to work with Win32 API."""

from ctypes import (WinError, byref, c_int, c_long, c_ulong, c_size_t,
                    create_string_buffer, windll)
from ctypes.wintypes import *
import logging

LPCSTR = LPCTSTR = ctypes.c_char_p
LPDWORD = PDWORD = ctypes.POINTER(DWORD)

class _SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('nLength', DWORD),
                ('lpSecurityDescriptor', LPVOID),
                ('bInheritHandle', BOOL),]

SECURITY_ATTRIBUTES = _SECURITY_ATTRIBUTES
LPSECURITY_ATTRIBUTES = ctypes.POINTER(_SECURITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = LPVOID

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ      = 0x0010
PROCESS_VM_WRITE     = 0x0020
MEM_COMMIT  = 0x00001000
MEM_RESERVE = 0x00002000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40
EXECUTE_IMMEDIATELY = 0x00000000

GetLastError = windll.kernel32.GetLastError
GetLastError.restype = DWORD
GetLastError.argtypes = ()

OpenProcess = windll.kernel32.OpenProcess
OpenProcess.restype = HANDLE
OpenProcess.argtypes = (DWORD, BOOL, DWORD)

GetProcAddress = windll.kernel32.GetProcAddress
GetProcAddress.restype = LPVOID
GetProcAddress.argtypes = (HANDLE, LPCTSTR)

WriteProcessMemory = windll.kernel32.WriteProcessMemory
WriteProcessMemory.restype = BOOL
WriteProcessMemory.argtypes = (HANDLE, LPVOID, LPCVOID, DWORD, DWORD)

CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
CreateRemoteThread.restype = HANDLE
CreateRemoteThread.argtypes = (HANDLE, LPSECURITY_ATTRIBUTES, DWORD, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD)

VirtualAllocEx = windll.kernel32.VirtualAllocEx
VirtualAllocEx.restype = LPVOID
VirtualAllocEx.argtypes = (HANDLE, LPVOID, DWORD, DWORD, DWORD)

VirtualFreeEx = windll.kernel32.VirtualFreeEx
VirtualFreeEx.restype = BOOL
VirtualFreeEx.argtypes = (HANDLE, LPVOID, c_size_t, DWORD)

def get_process_handle(process_id, desired_access, inherit_handle=False):
    handle = OpenProcess(desired_access, inherit_handle, process_id)
    if handle is None or handle == 0:
        raise Exception(f"Win32 API Error: {GetLastError()}")
    return handle

def allocate(hProcess, lpAddress, dwSize, flAllocationType, flProtect):
    lpBuffer = VirtualAllocEx(hProcess, lpAddress, dwSize, flAllocationType, flProtect)
    if lpBuffer is None or lpBuffer == 0:
        raise Exception(f"Win32 API Error: {GetLastError()}")
    return lpBuffer

def allocate_and_write(hProcess, lpAddress, dwSize, flAllocationType, flProtect, lpBuffer):
    lpStartAddress = allocate(hProcess, lpAddress, dwSize, flAllocationType, flProtect)
    result = WriteProcessMemory(hProcess, lpStartAddress, lpBuffer, dwSize, 0)
    if result is None or result == 0:
        raise Exception(f"Win32 API Error: {GetLastError()}")
    return lpStartAddress

def create_thread(hProcess, lpStartAddress, dwStackSize=0, lpParameter=0, dwCreationFlags=EXECUTE_IMMEDIATELY, lpThreadId=0, lpSecurityDescriptor=0, bInheritHandle=False):
    ThreadAttributes = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), lpSecurityDescriptor, bInheritHandle)
    lpThreadAttributes = LPSECURITY_ATTRIBUTES(ThreadAttributes)
    handle = CreateRemoteThread(hProcess, lpThreadAttributes, dwStackSize, lpStartAddress, lpParameter, dwCreationFlags, lpThreadId)
    if handle is None or handle == 0:
        raise Exception(f"Win32 API Error: {GetLastError()}")
    return handle

def get_address_from_module(module, function):
    # xxx(okachaiev): fix this non-sense
    # module_addr = windll.kernel32.GetModuleHandleA(module.encode("ascii"))
    # if not module_addr:
    #     raise WinError()
    module_addr = windll.kernel32._handle
    function_addr = GetProcAddress(module_addr, function.encode("ascii"))
    if not function_addr:
        raise WinError()
    return function_addr

class LibraryInjector:

    def __init__(self, pid: int):
        self._pid = int(pid)

        self._handle = get_process_handle(self._pid, PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE)
        if not self._handle:
            raise WinError()
        logging.debug("Process handle: %s", self._handle)

        self._func_addr = get_address_from_module("kernel32.dll", "LoadLibraryA")
        logging.debug("LoadLibraryA addr: %s", self._func_addr)
    
    def load_library(self, dll_path: str):
        buffer = dll_path.encode("ascii")

        # load path into process memory
        args_addr = self._alloc_remote(buffer)
        logging.debug("DLL '%s' name addr: %s", dll_path, args_addr)

        # executo kernel32.LoadLibraryA from the remote process with a given argument
        dll_addr = self._create_remote_thread(self._func_addr, args_addr)
        logging.debug("DLL addr: %s", dll_addr)

        # cleanup path from the memory
        self._free_remote(args_addr, len(buffer))
        return dll_addr

    def close(self):
        if self._handle is not None:
            windll.kernel32.CloseHandle(self._handle)
            self._handle = None

    # xxx(okachaiev): I should do this as a context manager
    def _alloc_remote(self, buffer):
        local_buffer = ctypes.create_string_buffer(buffer)
        return allocate_and_write(self._handle, 0, len(buffer), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE, local_buffer)

    # xxx(okachaiev): I should do this as a context manager
    def _free_remote(self, addr, size):
        # xxx(okachaiev): somehow doesn't like types :(
        # if not VirtualFreeEx(self._handle, addr, c_int(size), MEM_RELEASE):
        #     raise WinError()
        pass

    def _create_remote_thread(self, function_addr, args_addr):
        thread_id = DWORD()
        hThread = create_thread(self._handle, function_addr, lpParameter=args_addr, lpThreadId=LPDWORD(thread_id))
        logging.debug("Remote thread: %s, handle: %s", thread_id, hThread)
        dll_addr = thread_id.value
        if windll.kernel32.WaitForSingleObject(hThread, 0xFFFFFFFF) == 0xFFFFFFFF:
            raise WinError()
        if not windll.kernel32.GetExitCodeThread(hThread, byref(thread_id)):
            raise WinError()
        return dll_addr

    def __enter__(self):
        return self
    
    def __exit__(self, _exception_type, _exception_value, _exception_traceback):
        self.close()
    
    def __del__(self):
        self.close()
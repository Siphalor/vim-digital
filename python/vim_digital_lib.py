import json
import os
import os.path
import socket
import sys
import vim

def _print_error(message: str):
    sys.stderr.write(message + '\n')

def _create_socket() -> socket.socket:
    sock = socket.create_connection(('localhost', 41114))
    sock.settimeout(5)
    return sock

def _close_socket(sock: socket.socket):
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def _get_raw_file_path():
    return vim.eval('expand("%")')

def _get_file_path():
    return os.path.abspath(_get_raw_file_path())

def _get_hex_file_path(base: str):
    if base[-4:] == '.hex':
        return base
    if base[-4:] == '.asm':
        return base[0:-4] + '.hex'
    return base + '.hex'

def _get_asm_file_path(base: str):
    if base[-4:] == '.asm':
        return base
    if base[-4:] == '.hex':
        if os.path.isfile(base[0:-4] + '.asm'):
            return base[0:-4] + '.asm'
        return base[0:-4]
    return base

def _get_map_file_path(base: str):
    if base[-4:] == '.asm' or base[-4:] == '.hex':
        return base[0:-4] + '.map'
    return base + '.map'

def _prepare_message(message: str):
    l = len(message)
    upper = l >> 8
    lower = l & 0xFF
    prefix = bytes((upper, lower))
    return prefix + message.encode('utf-8')

def _process_reply(sock: socket.socket, success_message: str):
    reply = sock.recv(4096)
    reply = reply[2:].decode('utf-8')
    if reply[0:2] == 'ok':
        print(success_message)
        if len(reply) > 2:
            return reply[3:]
        return True
    else:
        print('An error occured: ' + reply)
        return False

def _get_asm3_path():
    return vim.eval('g:digital_asm3_jar')

def _compile_hex(path: str):
    res = os.system('javaw -jar ' + _get_asm3_path() + ' ' + path)
    if res != 0:
        _print_error('Failed to compile hex file!')
    return res

def _update_current_debug_addr(file_path: str, addr: int):
    mapping = _get_debug_line_mapping(file_path, addr)
    if type(mapping) == int:
        _clear_current_debug_line(file_path)
        _set_current_debug_line(file_path, mapping)
        return True
    else:
        #_print_error('Unable to find line mapping for address ' + str(addr) + '!')
        return False

def _set_current_debug_line(file_path: str, line: int):
    try:
        vim.command('sign place 1001 line=' + str(line) + ' name=DigitalDebugCurrentLine file=' + file_path)
    except:
        pass

def _clear_current_debug_line(file_path: str):
    try:
        vim.command('sign unplace 1001 file=' + file_path)
    except:
        pass

def _get_debug_line_mapping(base_file: str, addr: int):
    path = _get_map_file_path(base_file)
    if not os.path.isfile(path):
        _print_error('Unable to load mappings file: ' + path)
        return False
    with open(path, 'rt') as f:
        for obj in json.load(f):
            if obj['addr'] == addr:
                return obj['line']
    return False

def _clear_tmp_files(base_file: str):
    if base_file[-4:] == '.asm' or base_file[-4:] == '.hex':
        base_file = base_file[0:-4]
    if os.path.isfile(base_file + '.map'):
        os.remove(base_file + '.map')
    if os.path.isfile(base_file + '.lst'):
        os.remove(base_file + '.lst')

def run_asm_program():
    sock = _create_socket()
    path = _get_hex_file_path(_get_file_path())
    if not os.path.isfile(path):
        _print_error('Unable to find hex file: ' + path)
        return
    sock.settimeout(30)
    sock.send(_prepare_message('start:' + path))
    res = _process_reply(sock, 'Run started')
    _close_socket(sock)
    return res

def debug_asm_program():
    sock = _create_socket()
    path = _get_hex_file_path(_get_file_path())
    if not os.path.isfile(path):
        _print_error('Unable to find hex file: ' + path)
        return
    sock.send(_prepare_message('debug:' + path))
    res = _process_reply(sock, 'Debugging started')
    if type(res) == str:
        path = _get_asm_file_path(_get_raw_file_path())
        _update_current_debug_addr(path, int(res, 16))
    _close_socket(sock)
    return res

def step_asm_program():
    sock = _create_socket()
    sock.send(_prepare_message('step'))
    res = _process_reply(sock, 'Step successful!')
    if type(res) == str:
        path = _get_asm_file_path(_get_raw_file_path())
        _update_current_debug_addr(path, int(res, 16))
    _close_socket(sock)
    return res

def continue_asm_program():
    sock = _create_socket()
    sock.settimeout(30)
    sock.send(_prepare_message('run'))
    res = _process_reply(sock, 'Continue successful!')
    if type(res) == str:
        path = _get_asm_file_path(_get_raw_file_path())
        _update_current_debug_addr(path, int(res, 16))
    _close_socket(sock)
    return res

def stop_asm_program():
    sock = _create_socket()
    sock.send(_prepare_message('stop'))
    res = _process_reply(sock, 'Run stopped')
    _close_socket(sock)
    path = _get_asm_file_path(_get_raw_file_path())
    _clear_current_debug_line(path)

    if vim.eval('g:digital_auto_clear_tmp_files').strip() != '0':
        _clear_tmp_files(_get_file_path())
    if vim.eval('g:digital_auto_clear_hex_file').strip() != '0':
        path = _get_hex_file_path(_get_file_path())
        if os.path.isfile(path):
            os.remove(path)
    return res

def run_auto_clear():
    if vim.eval('g:digital_auto_clear_tmp_files').strip() != '0':
        _clear_tmp_files(_get_file_path())
    if vim.eval('g:digital_auto_clear_hex_file').strip() != '0':
        path = _get_hex_file_path(_get_file_path())
        if os.path.isfile(path):
            os.remove(path)

def compile_asm_program():
    path = _get_asm_file_path(_get_file_path())
    if not os.path.isfile(path):
        _print_error('Unable to find asm file: ' + path)
        return False
    res = _compile_hex(path)
    if res == 0:
        print('File compiled successfully')
        return True
    return False

def compile_and_run_asm_program():
    if not compile_asm_program():
        _print_error('Compilation Failed!')
        return
    return run_asm_program()

def compile_and_debug_asm_program():
    if not compile_asm_program():
        _print_error('Compilation Failed!')
        return
    return debug_asm_program()


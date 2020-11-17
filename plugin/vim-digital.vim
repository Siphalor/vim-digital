" Vim Digital:	a plugin that interfaces with hneemann's Digital and Assembler
" Maintainer:	Siphalor <info@siphalor.de>
" Last Change:	2020/11/17
" Version:		1.0
" License:		MIT (c) 2020 Siphalor

if has('python3') == 0
	echoerr 'Vim Digital requires python3 support in Vim!'
	finish
endif

if exists('g:digital_plugin_loaded')
	finish
endif
let g:digital_plugin_loaded = 1

if !exists('g:digital_asm3_jar')
	echoerr 'The path to the Asm3 Jar is not defined (g:digital_asm3_jar)!'
	finish
endif

if !exists('g:digital_auto_clear_tmp_files')
	let g:digital_auto_clear_tmp_files = 1
endif

if !exists('g:digital_auto_clear_hex_file')
	let g:digital_auto_clear_hex_file = 0
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
python3 << EOF
import sys
from os.path import abspath, normpath, join
import vim

plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)

import vim_digital_lib
EOF

" Highlighting taken from https://github.com/vim-vdebug/vdebug/blob/master/plugin/vdebug.vim
" licensed as MIT by Jon Cairns
if hlexists('DbgCurrentLine') == 0
    hi default DbgCurrentLine term=reverse ctermfg=White ctermbg=Red guifg=#ffffff guibg=#ff0000
end
if hlexists('DbgCurrentSign') == 0
    hi default DbgCurrentSign term=reverse ctermfg=White ctermbg=Red guifg=#ffffff guibg=#ff0000
end

sign define DigitalDebugCurrentLine linehl=DbgCurrentLine text=➤ texthl=DbgCurrentSign

command! -nargs=0 DigitalProcessorStart call DigitalProcessorStart()
function! DigitalProcessorStart()
	python3 vim_digital_lib.run_asm_program()
endfunction

command! -nargs=0 DigitalProcessorDebug call DigitalProcessorDebug()
function! DigitalProcessorDebug()
	python3 vim_digital_lib.debug_asm_program()
endfunction

command! -nargs=0 DigitalProcessorStep call DigitalProcessorStep()
function! DigitalProcessorStep()
	python3 vim_digital_lib.step_asm_program()
endfunction

command! -nargs=0 DigitalProcessorContinue call DigitalProcessorContinue()
function! DigitalProcessorContinue()
	python3 vim_digital_lib.continue_asm_program()
endfunction

command! -nargs=0 DigitalProcessorStop call DigitalProcessorStop()
function! DigitalProcessorStop()
	python3 vim_digital_lib.stop_asm_program()
endfunction

command! -nargs=0 DigitalAsmCompile call DigitalAsmCompile()
function! DigitalAsmCompile()
	python3 vim_digital_lib.compile_asm_program()
endfunction

command! -nargs=0 DigitalAsmCompileAndRun call DigitalAsmCompileAndRun()
function! DigitalAsmCompileAndRun()
	python3 vim_digital_lib.compile_and_run_asm_program()
endfunction

command! -nargs=0 DigitalAsmCompileAndDebug call DigitalAsmCompileAndDebug()
function! DigitalAsmCompileAndDebug()
	python3 vim_digital_lib.compile_and_debug_asm_program()
endfunction

augroup DigitalQuit
	autocmd QuitPre *.asm python3 vim_digital_lib.run_auto_clear()
augroup END


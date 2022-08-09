added to PYTHONPATH under the hood. For each directory in vim’s runtimepath, vim adds the subdirectory python3 (and also pythonx) to the python module search path. 
As a result, we could omit the explicit path addition to the python.vim (aka convert_fstring.vim) file if we organized the plugin like

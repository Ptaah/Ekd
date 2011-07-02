#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    EkdProcess permet de gérer les processus dans l'ensemble du code d'Ekd
"""

import subprocess, os


def EkdProcess( command, output = subprocess.PIPE, outputerr = subprocess.PIPE,
                stdinput = None, universal_newlines = True, bufsize = 0 ):
    """
        Fonction permettant de lancer un processus via subprocess.Popen
    """
    try:
        process = subprocess.Popen( command, shell = True, stdin = stdinput,
                                    stdout = output, stderr = outputerr,
                                    universal_newlines = universal_newlines,
                                    bufsize = bufsize,
                                    preexec_fn = os.setsid)
    except AttributeError :
        process = subprocess.Popen( command, shell = True, stdin = stdinput,
                                    stdout = output, stderr = outputerr,
                                    universal_newlines = universal_newlines,
                                    bufsize = bufsize)
    return process
